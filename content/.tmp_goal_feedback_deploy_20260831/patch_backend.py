from pathlib import Path
import re

path = Path(__file__).parent / "advisor" / "src" / "goal_agent.py"
text = path.read_text(encoding="utf-8")

normalizer = r'''
    @staticmethod
    def _normalize_quick_feedback(details: dict[str, Any]) -> tuple[dict[str, Any], str]:
        """Validate v2 quick feedback without inventing missing evidence."""
        if details.get("feedback_schema_version") != 2:
            return details, "旧版证据已保存；缺少作答条件时只作有限参考。"
        kind = _clean_text(details.get("feedback_kind"), 40)
        allowed_kinds = {"course", "exercise", "proof", "grade", "mock", "reading", "talk", "oral", "blocked"}
        if kind not in allowed_kinds:
            raise ValueError("unknown feedback_kind")
        raw_performance = details.get("performance")
        raw_conditions = details.get("conditions")
        if not isinstance(raw_performance, dict) or not isinstance(raw_conditions, dict):
            raise ValueError("v2 feedback requires performance and conditions objects")
        performance: dict[str, Any] = {}
        conditions: dict[str, Any] = {}
        text_fields = {"result", "error_type", "weak_step", "object", "impact", "quality_check", "questions"}
        numeric_fields = {"attempted", "correct", "independent_correct", "elapsed_minutes"}
        for key in text_fields:
            value = _clean_text(raw_performance.get(key), 200)
            if value:
                performance[key] = value
        for key in numeric_fields:
            value = raw_performance.get(key)
            if value in (None, ""):
                performance[key] = None
                continue
            number = int(value)
            if number < 0 or number > 10000:
                raise ValueError(f"{key} is outside the accepted range")
            performance[key] = number
        condition_options = {
            "assistance": {"none", "hint", "solution", "mixed", "unknown"},
            "verification": {"reference", "human", "self", "unchecked"},
            "mastery_basis": {"lecture", "recall", "practice", "unknown"},
            "attempt_timing": {"first", "immediate", "delayed", "unknown"},
            "origin": {"official", "self", "estimate"},
            "completion": {"timed", "interrupted", "untimed", "unknown"},
            "novelty": {"new", "repeat", "mixed", "unknown"},
            "rater": {"self", "peer", "ai", "unknown"},
            "requested_response": {"split", "explain", "defer"},
        }
        for key, options in condition_options.items():
            value = _clean_text(raw_conditions.get(key), 40)
            if value:
                if value not in options:
                    raise ValueError(f"invalid {key}")
                conditions[key] = value
        required = {
            "course": ("mastery_basis",),
            "exercise": ("assistance", "verification"),
            "proof": ("attempt_timing", "verification"),
            "grade": ("origin",),
            "mock": ("completion", "novelty", "verification", "assistance"),
            "talk": ("rater",),
            "oral": ("rater", "assistance"),
            "blocked": ("requested_response",),
        }
        missing = [key for key in required.get(kind, ()) if not conditions.get(key)]
        if missing:
            raise ValueError("missing required evidence conditions: " + ",".join(missing))
        attempted = performance.get("attempted")
        correct = performance.get("correct")
        independent = performance.get("independent_correct")
        if attempted is not None and correct is not None and correct > attempted:
            raise ValueError("correct must not exceed attempted")
        if independent is not None and (correct is None or independent > correct):
            raise ValueError("independent_correct must not exceed verified correct")
        oral_scores = details.get("oral_scores")
        normalized_oral: dict[str, Any] = {}
        if isinstance(oral_scores, dict):
            for key in ("definition", "example", "strategy", "follow_up"):
                value = oral_scores.get(key)
                if value in (None, ""):
                    normalized_oral[key] = None
                elif isinstance(value, (int, float)) and 0 <= float(value) <= 5:
                    normalized_oral[key] = float(value)
                else:
                    raise ValueError("oral scores must be null or between 0 and 5")
        normalized = {
            "feedback_schema_version": 2,
            "feedback_kind": kind,
            "performance": performance,
            "conditions": conditions,
            "note": _clean_text(details.get("note"), 1000) or None,
        }
        for key in ("course", "component"):
            value = _clean_text(details.get(key), 120)
            if value:
                normalized[key] = value
        if normalized_oral:
            normalized["oral_scores"] = normalized_oral
        if kind == "course":
            normalized["taught_units"] = details.get("taught_units")
        if kind == "exercise":
            if conditions.get("assistance") == "none" and correct is not None:
                normalized["performance"]["independent_correct"] = correct
            boundary = (
                "最终正确与独立正确已分开保存；单次表现不能证明长期保持或新题迁移。"
                if conditions.get("assistance") != "none"
                else "本次独立表现已保存；是否为新题、能否隔日保持仍需其他证据。"
            )
        elif kind == "course":
            boundary = (
                "授课范围与听课自评已保存；仅凭听课感受不能验证独立掌握。"
                if conditions.get("mastery_basis") == "lecture"
                else "掌握度及其依据已保存；仍需结合对应成果和后续复测。"
            )
        elif kind == "proof":
            boundary = (
                "即时重做已保存；它不能证明隔日仍能独立重建证明。"
                if conditions.get("attempt_timing") == "immediate"
                else "证明表现与核对方式已保存；未审查的步骤仍保持待核验。"
            )
        elif kind == "grade":
            boundary = "正式成绩已保存。" if conditions.get("origin") == "official" else "自评或估分已保存，但不会冒充正式成绩。"
        elif kind == "mock":
            complete = conditions.get("completion") == "timed" and conditions.get("novelty") == "new" and conditions.get("verification") in {"reference", "human"} and conditions.get("assistance") == "none"
            boundary = "本次具备独立、新题、限时和可靠评分条件。" if complete else "本次条件不完整；不会计入不同真实题源的连续达标记录。"
        elif kind in {"reading", "talk", "oral"}:
            boundary = "产出与检验条件已分开保存；数量或自评本身不等于掌握。"
        else:
            boundary = "阻塞范围已保存；单个卡点不会被扩展为整章不会。"
        normalized["evidence_boundary"] = boundary
        return normalized, boundary

'''
marker = "    def _normalize_course_progress(\n"
assert marker in text
text = text.replace(marker, normalizer + marker, 1)

# Expose recent evidence to the deterministic state and therefore to model review context.
state_marker = '''            chats.reverse()\n            return {'''
state_insert = '''            chats.reverse()\n            recent_evidence = []\n            for row in connection.execute(\n                "SELECT id,track_id,plan_item_id,evidence_type,occurred_at,deep_minutes,"\n                "completed_units,score,max_score,source_id,blocked_reason,payload_json "\n                "FROM evidence_event ORDER BY occurred_at DESC,id DESC LIMIT 24"\n            ):\n                item = dict(row)\n                item["payload"] = _loads(item.pop("payload_json", "{}"), {})\n                recent_evidence.append(item)\n            return {'''
assert state_marker in text
text = text.replace(state_marker, state_insert, 1)
text = text.replace('''                "chat_messages": chats,\n                "tavily": {''', '''                "chat_messages": chats,\n                "recent_evidence": recent_evidence,\n                "tavily": {''', 1)

# New course grades only count toward formal scenarios when reported as official.
text = text.replace('''        weight = payload.get("weight")\n        score = event.get("score")''', '''        weight = payload.get("weight")\n        if payload.get("feedback_schema_version") == 2 and payload.get("feedback_kind") == "grade" and payload.get("conditions", {}).get("origin") != "official":\n            continue\n        score = event.get("score")''', 1)

# New mock records require independent, new, timed and verified conditions to pass.
text = text.replace('''        normalized = 150.0 * float(score) / float(maximum)\n        attempts.append({''', '''        normalized = 150.0 * float(score) / float(maximum)\n        payload = event.get("payload") if isinstance(event.get("payload"), dict) else {}\n        conditions = payload.get("conditions") if isinstance(payload.get("conditions"), dict) else {}\n        v2 = payload.get("feedback_schema_version") == 2\n        condition_complete = (\n            not v2 or (\n                conditions.get("completion") == "timed"\n                and conditions.get("novelty") == "new"\n                and conditions.get("verification") in {"reference", "human"}\n                and conditions.get("assistance") == "none"\n            )\n        )\n        attempts.append({''', 1)
text = text.replace('''            "passed": normalized >= 120.0 and bool(source_id),\n        })''', '''            "condition_complete": condition_complete,\n            "passed": normalized >= 120.0 and bool(source_id) and condition_complete,\n        })''', 1)

# Normalize the structured v2 payload before course-specific normalization and persistence.
text = text.replace('''            event_payload = payload.get("details") if isinstance(payload.get("details"), dict) else {}\n            course_progress = None''', '''            event_payload = payload.get("details") if isinstance(payload.get("details"), dict) else {}\n            event_payload, evidence_boundary = self._normalize_quick_feedback(event_payload)\n            course_progress = None''', 1)

# Course-specific normalization must retain the v2 condition metadata.
text = text.replace('''                event_payload = {\n                    **event_payload,\n                    **course_progress,\n                }''', '''                event_payload = {\n                    **event_payload,\n                    **course_progress,\n                    "conditions": event_payload.get("conditions", {}),\n                    "feedback_schema_version": event_payload.get("feedback_schema_version"),\n                    "feedback_kind": event_payload.get("feedback_kind"),\n                    "evidence_boundary": event_payload.get("evidence_boundary"),\n                }''', 1)

# Validate score bounds for every feedback type.
score_anchor = '''            source_id = _clean_text(payload.get("source_id"), 160) or None\n            event_id = "ev-" + uuid.uuid4().hex'''
score_replacement = '''            score_value = payload.get("score")\n            maximum_value = payload.get("max_score")\n            if score_value not in (None, ""):\n                score_value = float(score_value)\n                if score_value < 0:\n                    raise ValueError("score must be non-negative")\n            if maximum_value not in (None, ""):\n                maximum_value = float(maximum_value)\n                if maximum_value <= 0:\n                    raise ValueError("max_score must be positive")\n            if score_value is not None and maximum_value is not None and score_value > maximum_value:\n                raise ValueError("score must not exceed max_score")\n            source_id = _clean_text(payload.get("source_id"), 160) or None\n            event_id = "ev-" + uuid.uuid4().hex'''
assert score_anchor in text
text = text.replace(score_anchor, score_replacement, 1)
text = text.replace('''                    float(payload["score"]) if payload.get("score") not in (None, "") else None,\n                    float(payload["max_score"]) if payload.get("max_score") not in (None, "") else None,''', '''                    score_value,\n                    maximum_value,''', 1)

# Return the boundary so the UI can immediately explain the limited conclusion.
text = text.replace('''            return {"ok": True, "event_id": event_id, "approval_request_id": approval_id, "changes": changes, "progress": metrics}''', '''            return {"ok": True, "event_id": event_id, "approval_request_id": approval_id, "changes": changes, "progress": metrics, "evidence_boundary": evidence_boundary}''', 1)

# Algebra v2 streaks require independent, verified attempts.
algebra_anchor = '''            source_id = str(event["source_id"] or "")\n            if rate < 0.8 or not source_id or source_id in seen:\n                break'''
algebra_replace = '''            source_id = str(event["source_id"] or "")\n            payload = event.get("payload") if isinstance(event.get("payload"), dict) else {}\n            conditions = payload.get("conditions") if isinstance(payload.get("conditions"), dict) else {}\n            v2_valid = (\n                payload.get("feedback_schema_version") != 2\n                or (conditions.get("assistance") == "none" and conditions.get("verification") in {"reference", "human"})\n            )\n            if rate < 0.8 or not source_id or source_id in seen or not v2_valid:\n                break'''
assert algebra_anchor in text
text = text.replace(algebra_anchor, algebra_replace, 1)

path.write_text(text, encoding="utf-8")
