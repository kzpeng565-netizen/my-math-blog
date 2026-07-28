from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from common import parse_timestamp, rounded_minutes
from deepseek_client import _request_json_report
from fact_tagger import compact_fact_view_for_ai


ACTIVITIES = {
    "work",
    "entertainment",
    "brief_communication",
    "rest",
    "other",
    "uncertain",
}
WORK_CATEGORIES = {"数学学习", "家教", "系统维护", "其他工作", ""}
RELATIONSHIPS = {
    "same_work_task",
    "supporting_work",
    "brief_communication",
    "entertainment_detour",
    "task_transition",
    "standalone_activity",
    "confirmed_rest",
    "uncertain",
}
CONFIDENCE_LEVELS = {"high", "medium", "low"}


def _parse_segment_time(value: Any, timezone_name: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError("时间必须是ISO 8601字符串")
    return parse_timestamp(value, timezone_name)


def _validate_semantic_timeline(
    result: dict[str, Any],
    period_start: datetime,
    period_end: datetime,
    timezone_name: str,
    confirmed_rest_minutes: float,
    confirmed_rest_intervals: list[dict[str, Any]],
) -> list[str]:
    errors: list[str] = []
    segments = result.get("segments")
    if not isinstance(segments, list) or not segments:
        return ["segments必须是非空数组"]

    parsed: list[tuple[datetime, datetime, dict[str, Any]]] = []
    for index, segment in enumerate(segments):
        if not isinstance(segment, dict):
            errors.append(f"segments[{index}]不是对象")
            continue
        try:
            start = _parse_segment_time(segment.get("start"), timezone_name)
            end = _parse_segment_time(segment.get("end"), timezone_name)
        except ValueError as error:
            errors.append(f"segments[{index}]时间错误：{error}")
            continue
        if end <= start:
            errors.append(f"segments[{index}]结束时间不晚于开始时间")
        if start < period_start or end > period_end:
            errors.append(f"segments[{index}]超出报告时段")
        if segment.get("activity") not in ACTIVITIES:
            errors.append(f"segments[{index}].activity不在允许列表中")
        work_category = segment.get("work_category", "")
        if work_category not in WORK_CATEGORIES:
            errors.append(f"segments[{index}].work_category不在允许列表中")
        if segment.get("activity") == "work" and not work_category:
            errors.append(f"segments[{index}]为工作但没有work_category")
        if segment.get("activity") != "work" and work_category:
            errors.append(f"segments[{index}]非工作却设置了work_category")
        if segment.get("relationship_to_work") not in RELATIONSHIPS:
            errors.append(
                f"segments[{index}].relationship_to_work不在允许列表中"
            )
        if segment.get("confidence") not in CONFIDENCE_LEVELS:
            errors.append(f"segments[{index}].confidence不在允许列表中")
        if not isinstance(segment.get("evidence", []), list):
            errors.append(f"segments[{index}].evidence必须是数组")
        parsed.append((start, end, segment))

    if not parsed:
        return errors or ["没有可解析的时间段"]
    parsed.sort(key=lambda item: item[0])
    tolerance_seconds = 1.0
    if abs((parsed[0][0] - period_start).total_seconds()) > tolerance_seconds:
        errors.append("时间线没有从报告时段起点开始")
    if abs((parsed[-1][1] - period_end).total_seconds()) > tolerance_seconds:
        errors.append("时间线没有覆盖到报告时段终点")
    for previous, current in zip(parsed, parsed[1:]):
        difference = (current[0] - previous[1]).total_seconds()
        if difference > tolerance_seconds:
            errors.append(f"时间线存在{round(difference, 1)}秒空白")
        elif difference < -tolerance_seconds:
            errors.append(f"时间线存在{round(-difference, 1)}秒重叠")

    rest_seconds = sum(
        (end - start).total_seconds()
        for start, end, segment in parsed
        if segment.get("activity") == "rest"
    )
    if abs(rounded_minutes(rest_seconds) - confirmed_rest_minutes) > 0.2:
        errors.append("AI时间线中的休息分钟数不等于确定性休息规则结果")
    actual_rest = [
        (start, end)
        for start, end, segment in parsed
        if segment.get("activity") == "rest"
    ]
    expected_rest = [
        (
            parse_timestamp(item["start"], timezone_name),
            parse_timestamp(item["end"], timezone_name),
        )
        for item in confirmed_rest_intervals
    ]
    if len(actual_rest) != len(expected_rest):
        errors.append("AI时间线中的休息区间数量与确定性休息区间不一致")
    else:
        for actual, expected in zip(actual_rest, expected_rest):
            if (
                abs((actual[0] - expected[0]).total_seconds()) > 1
                or abs((actual[1] - expected[1]).total_seconds()) > 1
            ):
                errors.append("AI时间线中的休息区间位置与确定性休息区间不一致")
                break
    return errors


def _normalize_semantic_timeline(
    result: dict[str, Any],
    period_start: datetime,
    period_end: datetime,
    timezone_name: str,
) -> dict[str, Any]:
    normalized: list[dict[str, Any]] = []
    segments = sorted(
        result["segments"],
        key=lambda item: _parse_segment_time(item["start"], timezone_name),
    )
    previous_end = period_start
    for index, segment in enumerate(segments):
        start = _parse_segment_time(segment["start"], timezone_name)
        end = _parse_segment_time(segment["end"], timezone_name)
        if index == 0 and abs((start - period_start).total_seconds()) <= 1:
            start = period_start
        if abs((start - previous_end).total_seconds()) <= 1:
            start = previous_end
        if index == len(segments) - 1 and abs(
            (end - period_end).total_seconds()
        ) <= 1:
            end = period_end
        item = {
            "start": start.isoformat(timespec="seconds"),
            "end": end.isoformat(timespec="seconds"),
            "duration_seconds": round((end - start).total_seconds(), 3),
            "activity": segment["activity"],
            "work_category": segment.get("work_category", ""),
            "task": str(segment.get("task", "")).strip(),
            "relationship_to_work": segment["relationship_to_work"],
            "devices": [
                device
                for device in segment.get("devices", [])
                if device in {"computer", "phone", "tablet"}
            ],
            "evidence": [str(item) for item in segment.get("evidence", [])[:4]],
            "confidence": segment["confidence"],
        }
        previous_end = end
        if (
            normalized
            and normalized[-1]["end"] == item["start"]
            and all(
                normalized[-1].get(key) == item.get(key)
                for key in (
                    "activity",
                    "work_category",
                    "task",
                    "relationship_to_work",
                    "confidence",
                )
            )
        ):
            normalized[-1]["end"] = item["end"]
            normalized[-1]["duration_seconds"] = round(
                normalized[-1]["duration_seconds"] + item["duration_seconds"], 3
            )
            normalized[-1]["devices"] = sorted(
                set(normalized[-1]["devices"] + item["devices"])
            )
            normalized[-1]["evidence"] = list(
                dict.fromkeys(normalized[-1]["evidence"] + item["evidence"])
            )[:4]
        else:
            normalized.append(item)

    return {
        "schema_version": 1,
        "source": "deepseek_semantic_timeline",
        "period": {
            "start": period_start.isoformat(timespec="seconds"),
            "end": period_end.isoformat(timespec="seconds"),
        },
        "primary_work_task": str(result.get("primary_work_task", "")).strip(),
        "segments": normalized,
        "material_uncertainties": [
            str(item) for item in result.get("material_uncertainties", [])[:2]
        ],
    }


def _block_devices(blocks: list[dict[str, Any]]) -> list[str]:
    devices: set[str] = set()
    for block in blocks:
        computer = block.get("computer", {})
        phone = block.get("phone", {})
        tablet = block.get("tablet", {})
        if computer.get("app") or computer.get("status") == "not-afk":
            devices.add("computer")
        if phone.get("app") or phone.get("screen") == "on":
            devices.add("phone")
        if tablet.get("app") or tablet.get("screen") == "on":
            devices.add("tablet")
    return sorted(devices)


def _block_evidence(block: dict[str, Any]) -> str:
    parts: list[str] = []
    computer = block.get("computer", {})
    if computer.get("app"):
        detail = computer["app"]
        if computer.get("title"):
            detail += f"《{computer['title']}》"
        if computer.get("domain"):
            detail += f"({computer['domain']})"
        parts.append("电脑：" + detail)
    elif computer.get("status"):
        parts.append("电脑：" + computer["status"])
    for label, key in (("手机", "phone"), ("平板", "tablet")):
        mobile = block.get(key, {})
        apps = mobile.get("apps", [])
        if apps:
            summary = ",".join(
                f"{item['app']} {round(float(item['seconds']))}秒"
                for item in apps[:3]
            )
            parts.append(f"{label}：{summary}")
        elif mobile.get("app"):
            parts.append(f"{label}：{mobile['app']}")
        elif mobile.get("screen"):
            parts.append(f"{label}：{mobile['screen']}")
    tags = ",".join(tag["name"] for tag in block.get("tags", []))
    if tags:
        parts.append("tag：" + tags)
    start = str(block["start"])[11:19]
    end = str(block["end"])[11:19]
    return f"{start}-{end} " + "；".join(parts)


def _locked_segment(block: dict[str, Any]) -> dict[str, Any]:
    activity = block["locked_activity"]
    task_by_activity = {
        "rest": "确认休息",
        "brief_communication": "通信",
        "entertainment": "娱乐",
        "other": "其他活动",
        "uncertain": "无法判断",
    }
    relationship_by_activity = {
        "rest": "confirmed_rest",
        "brief_communication": "brief_communication",
        "entertainment": "standalone_activity",
        "other": "standalone_activity",
        "uncertain": "uncertain",
    }
    return {
        "start": block["start"],
        "end": block["end"],
        "duration_seconds": float(block["duration_seconds"]),
        "activity": activity,
        "work_category": "",
        "task": task_by_activity.get(activity, activity),
        "relationship_to_work": relationship_by_activity.get(
            activity, "uncertain"
        ),
        "devices": _block_devices([block]),
        "evidence": [_block_evidence(block)],
        "confidence": "high",
        "fact_block_ids": [block["id"]],
        "locked_by_program": True,
    }


def _uncertain_segment(blocks: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "start": blocks[0]["start"],
        "end": blocks[-1]["end"],
        "duration_seconds": round(
            sum(float(block["duration_seconds"]) for block in blocks), 3
        ),
        "activity": "uncertain",
        "work_category": "",
        "task": "AI未可靠标注的事实块",
        "relationship_to_work": "uncertain",
        "devices": _block_devices(blocks),
        "evidence": [_block_evidence(block) for block in blocks[:4]],
        "confidence": "low",
        "fact_block_ids": [block["id"] for block in blocks],
        "locked_by_program": False,
    }


def _merge_semantic_segments(
    segments: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    merged: list[dict[str, Any]] = []
    for segment in segments:
        if (
            merged
            and merged[-1]["end"] == segment["start"]
            and all(
                merged[-1].get(key) == segment.get(key)
                for key in (
                    "activity",
                    "work_category",
                    "task",
                    "relationship_to_work",
                    "confidence",
                    "locked_by_program",
                )
            )
        ):
            previous = merged[-1]
            previous["end"] = segment["end"]
            previous["duration_seconds"] = round(
                float(previous["duration_seconds"])
                + float(segment["duration_seconds"]),
                3,
            )
            previous["devices"] = sorted(
                set(previous["devices"] + segment["devices"])
            )
            previous["evidence"] = list(
                dict.fromkeys(previous["evidence"] + segment["evidence"])
            )[:4]
            previous["fact_block_ids"].extend(segment["fact_block_ids"])
        else:
            merged.append(dict(segment))
    return merged


def _segments_from_ai_groups(
    result: dict[str, Any],
    tagged_fact_view: dict[str, Any],
    candidate_map: dict[str, list[str]] | None = None,
) -> tuple[list[dict[str, Any]], list[str]]:
    candidate_map = candidate_map or {}
    all_blocks = tagged_fact_view.get("blocks", [])
    report_blocks = [
        block for block in all_blocks if block.get("scope") == "report"
    ]
    block_by_id = {block["id"]: block for block in all_blocks}
    report_index = {
        block["id"]: index for index, block in enumerate(report_blocks)
    }
    assigned: dict[str, dict[str, Any]] = {}
    issues: list[str] = []
    groups = result.get("groups", [])
    if not isinstance(groups, list):
        groups = []
        issues.append("groups不是数组")

    for group_index, group in enumerate(groups):
        prefix = f"groups[{group_index}]"
        if not isinstance(group, dict):
            issues.append(f"{prefix}不是对象")
            continue
        candidate_ids = group.get("block_ids")
        if (
            not isinstance(candidate_ids, list)
            or not candidate_ids
            or not all(isinstance(item, str) for item in candidate_ids)
        ):
            issues.append(f"{prefix}.block_ids无效")
            continue
        if len(set(candidate_ids)) != len(candidate_ids):
            issues.append(f"{prefix}.block_ids存在重复")
            continue
        block_ids = [
            source_id
            for candidate_id in candidate_ids
            for source_id in candidate_map.get(
                candidate_id, [candidate_id]
            )
        ]
        blocks = [block_by_id.get(block_id) for block_id in block_ids]
        if any(block is None for block in blocks):
            issues.append(f"{prefix}引用未知事实块")
            continue
        typed_blocks = [block for block in blocks if block is not None]
        if any(block.get("scope") != "report" for block in typed_blocks):
            issues.append(f"{prefix}引用了边界上下文块")
            continue
        if any(block.get("locked_activity") for block in typed_blocks):
            issues.append(f"{prefix}试图覆盖程序锁定事实块")
            continue
        indexes = [report_index[block_id] for block_id in block_ids]
        if indexes != sorted(indexes):
            issues.append(f"{prefix}.block_ids不是有序的事实块")
            continue
        forced_ids: set[str] = set()
        if len(typed_blocks) > 1:
            forced_ids = {
                block["id"]
                for block in typed_blocks
                if block.get("force_boundary")
            }
        if forced_ids:
            issues.append(f"{prefix}跨越了必须单独判断的事实块")
        if indexes != list(range(indexes[0], indexes[0] + len(indexes))):
            issues.append(f"{prefix}跨越程序锁定边界，程序已拆分")
        if any(block_id in assigned for block_id in block_ids):
            issues.append(f"{prefix}重复覆盖事实块")
            continue

        activity = group.get("activity")
        work_category = group.get("work_category", "")
        relationship = group.get("relationship_to_work")
        confidence = group.get("confidence")
        if relationship == "entertainment_detour":
            activity = "entertainment"
            work_category = ""
        elif relationship == "brief_communication":
            activity = "brief_communication"
            work_category = ""
        if activity not in ACTIVITIES - {"rest"}:
            issues.append(f"{prefix}.activity无效")
            continue
        if work_category not in WORK_CATEGORIES:
            issues.append(f"{prefix}.work_category无效")
            continue
        if activity == "work" and not work_category:
            issues.append(f"{prefix}为工作但没有work_category")
            continue
        if activity != "work" and work_category:
            issues.append(f"{prefix}非工作却设置work_category")
            continue
        if relationship not in RELATIONSHIPS - {"confirmed_rest"}:
            issues.append(f"{prefix}.relationship_to_work无效")
            continue
        if confidence not in CONFIDENCE_LEVELS:
            issues.append(f"{prefix}.confidence无效")
            continue

        evidence_candidate_ids = group.get("evidence_ids", [])
        if not isinstance(evidence_candidate_ids, list):
            evidence_candidate_ids = []
        evidence_ids = [
            source_id
            for candidate_id in evidence_candidate_ids
            if isinstance(candidate_id, str)
            for source_id in candidate_map.get(
                candidate_id, [candidate_id]
            )
        ]
        evidence_blocks = [
            block_by_id[item]
            for item in evidence_ids[:4]
            if isinstance(item, str) and item in block_by_id
        ]
        if not evidence_blocks:
            evidence_blocks = typed_blocks[:4]
        valid_blocks = [
            block
            for block in typed_blocks
            if block["id"] not in forced_ids
        ]
        runs: list[list[dict[str, Any]]] = []
        for block in valid_blocks:
            if (
                runs
                and report_index[block["id"]]
                == report_index[runs[-1][-1]["id"]] + 1
            ):
                runs[-1].append(block)
            else:
                runs.append([block])
        for run in runs:
            run_ids = [block["id"] for block in run]
            segment = {
                "start": run[0]["start"],
                "end": run[-1]["end"],
                "duration_seconds": round(
                    sum(float(block["duration_seconds"]) for block in run),
                    3,
                ),
                "activity": activity,
                "work_category": work_category,
                "task": str(group.get("task", "")).strip(),
                "relationship_to_work": relationship,
                "devices": _block_devices(run),
                "evidence": [
                    _block_evidence(block) for block in evidence_blocks
                ],
                "confidence": confidence,
                "fact_block_ids": run_ids,
                "locked_by_program": False,
            }
            for block_id in run_ids:
                assigned[block_id] = segment

    segments: list[dict[str, Any]] = []
    index = 0
    while index < len(report_blocks):
        block = report_blocks[index]
        if block.get("locked_activity"):
            segments.append(_locked_segment(block))
            index += 1
            continue
        assigned_segment = assigned.get(block["id"])
        if assigned_segment is not None:
            if (
                not segments
                or segments[-1] is not assigned_segment
            ):
                segments.append(assigned_segment)
            index += len(assigned_segment["fact_block_ids"])
            continue
        missing: list[dict[str, Any]] = [block]
        cursor = index + 1
        while cursor < len(report_blocks):
            following = report_blocks[cursor]
            if following.get("locked_activity") or following["id"] in assigned:
                break
            missing.append(following)
            cursor += 1
        segments.append(_uncertain_segment(missing))
        index = cursor

    missing_seconds = sum(
        float(segment["duration_seconds"])
        for segment in segments
        if segment["activity"] == "uncertain"
        and segment["task"] == "AI未可靠标注的事实块"
    )
    if missing_seconds:
        issues.append(
            f"AI漏答或无效标注共{rounded_minutes(missing_seconds)}分钟，"
            "程序已标为无法判断"
        )
    return _merge_semantic_segments(segments), list(dict.fromkeys(issues))


def _compact_obsidian_context(
    obsidian_context: dict[str, Any] | None,
) -> dict[str, Any] | None:
    if not obsidian_context:
        return None
    compact = {
        key: obsidian_context.get(key)
        for key in (
            "generated_at",
            "profile_markdown",
            "latest_plan_heading",
            "tasks",
            "pomodoro",
        )
        if obsidian_context.get(key) not in (None, "", [], {})
    }
    profile = compact.get("profile_markdown")
    if isinstance(profile, str):
        compact["profile_markdown"] = profile[:1200]
    tasks = compact.get("tasks")
    if isinstance(tasks, list):
        compact["tasks"] = tasks[:8]
    pomodoro = compact.get("pomodoro")
    if isinstance(pomodoro, list):
        compact["pomodoro"] = pomodoro[:8]
    return compact or None


def extract_semantic_timeline_with_deepseek(
    settings: dict[str, Any],
    prompt_path: Path,
    tagged_fact_view: dict[str, Any],
    obsidian_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    evidence = compact_fact_view_for_ai(tagged_fact_view)
    candidate_map = evidence.pop("_candidate_map", {})
    compact_context = _compact_obsidian_context(obsidian_context)
    if compact_context:
        evidence["read_only_obsidian_context"] = compact_context
    messages = [
        {
            "role": "system",
            "content": prompt_path.read_text(encoding="utf-8"),
        },
        {
            "role": "user",
            "content": (
                "请只组合report_candidates中的事实块；"
                "locked_markers已由程序分类且没有可输出ID，"
                "context_blocks只用于理解前后文。"
                "返回语义分组JSON：\n"
                + json.dumps(evidence, ensure_ascii=False, separators=(",", ":"))
            ),
        },
    ]
    segment_model = {
        **settings["model"],
        **settings.get("semantic_model", {}),
    }
    result, generation = _request_json_report(segment_model, messages)
    segments, issues = _segments_from_ai_groups(
        result, tagged_fact_view, candidate_map
    )
    uncertainties = [
        str(item) for item in result.get("material_uncertainties", [])[:2]
    ]
    if issues and not uncertainties:
        uncertainties = [issues[-1]]
    return {
        "schema_version": 2,
        "source": "deepseek_tagged_fact_groups",
        "period": tagged_fact_view["report_period"],
        "primary_work_task": str(
            result.get("primary_work_task", "")
        ).strip(),
        "segments": segments,
        "material_uncertainties": uncertainties[:2],
        "tag_rule_version": tagged_fact_view["tag_rule_version"],
        "_validation": {
            "passed": True,
            "errors": [],
            "ai_output_issues": issues,
            "correction_attempts": 0,
        },
        "_generation": generation,
    }


def _nearest_activity(
    segments: list[dict[str, Any]], index: int, direction: int
) -> str | None:
    cursor = index + direction
    while 0 <= cursor < len(segments):
        activity = segments[cursor]["activity"]
        if activity in {"work", "entertainment"}:
            return activity
        cursor += direction
    return None


def _return_latency_seconds(
    segments: list[dict[str, Any]], index: int, timezone_name: str
) -> float | None:
    entertainment_end = parse_timestamp(segments[index]["end"], timezone_name)
    for following in segments[index + 1 :]:
        if following["activity"] == "work":
            return max(
                0.0,
                (
                    parse_timestamp(following["start"], timezone_name)
                    - entertainment_end
                ).total_seconds(),
            )
        if following["activity"] == "entertainment":
            continue
    return None


def _longest_work_continuity_seconds(
    segments: list[dict[str, Any]],
) -> float:
    longest = 0.0
    index = 0
    while index < len(segments):
        if segments[index].get("activity") != "work":
            index += 1
            continue
        start_index = index
        end_index = index
        task = str(segments[index].get("task", "")).strip()
        cursor = index + 1
        while cursor + 1 < len(segments):
            bridge = segments[cursor]
            next_work = segments[cursor + 1]
            if (
                bridge.get("activity") == "brief_communication"
                and next_work.get("activity") == "work"
                and (
                    not task
                    or not str(next_work.get("task", "")).strip()
                    or str(next_work.get("task", "")).strip() == task
                )
            ):
                end_index = cursor + 1
                cursor += 2
                continue
            break
        duration = sum(
            float(item.get("duration_seconds", 0))
            for item in segments[start_index : end_index + 1]
        )
        longest = max(longest, duration)
        index = end_index + 1
    return longest


def calculate_work_entertainment_mixing(
    semantic_timeline: dict[str, Any],
    cross_device_facts: dict[str, Any],
    settings: dict[str, Any],
) -> dict[str, Any]:
    threshold_seconds = float(
        settings.get("state_rules", {}).get(
            "entertainment_deviation_minimum_seconds", 30
        )
    )
    timezone_name = settings["timezone"]
    segments = semantic_timeline.get("segments", [])
    deviations: list[dict[str, Any]] = []
    for index, segment in enumerate(segments):
        if segment.get("activity") != "entertainment":
            continue
        duration = float(segment.get("duration_seconds", 0))
        if duration <= threshold_seconds:
            continue
        before = _nearest_activity(segments, index, -1)
        after = _nearest_activity(segments, index, 1)
        is_detour = (
            segment.get("relationship_to_work") == "entertainment_detour"
            or (before == "work" and after == "work")
        )
        if not is_detour:
            continue
        latency = _return_latency_seconds(segments, index, timezone_name)
        deviations.append(
            {
                "start": segment["start"],
                "end": segment["end"],
                "minutes": rounded_minutes(duration),
                "duration_seconds": duration,
                "task": segment.get("task", ""),
                "evidence": segment.get("evidence", []),
                "returned_to_work": latency is not None,
                "return_latency_minutes": rounded_minutes(latency)
                if latency is not None
                else None,
                "confidence": segment.get("confidence", "low"),
            }
        )

    all_entertainment_seconds = sum(
        float(segment.get("duration_seconds", 0))
        for segment in segments
        if segment.get("activity") == "entertainment"
    )
    detour_seconds = sum(item["duration_seconds"] for item in deviations)
    count = len(deviations)
    if count == 0:
        level = "none"
    elif detour_seconds > 300 or count >= 4:
        level = "high"
    elif detour_seconds > 120 or count >= 2:
        level = "medium"
    else:
        level = "low"

    compact_work_entertainment = [
        segment["activity"]
        for segment in segments
        if segment["activity"] in {"work", "entertainment"}
    ]
    transitions = sum(
        left != right
        for left, right in zip(
            compact_work_entertainment, compact_work_entertainment[1:]
        )
    )
    work_segments = [
        segment for segment in segments if segment.get("activity") == "work"
    ]
    brief_communication_seconds = sum(
        float(segment.get("duration_seconds", 0))
        for segment in segments
        if segment.get("activity") == "brief_communication"
    )
    longest_work_seconds = _longest_work_continuity_seconds(segments)

    raw_context_blocks = cross_device_facts.get(
        "computer_fragmentation_metrics", {}
    ).get("context_blocks", [])
    same_task_tool_switches = 0
    for work_segment in work_segments:
        work_start = parse_timestamp(work_segment["start"], timezone_name)
        work_end = parse_timestamp(work_segment["end"], timezone_name)
        contained = 0
        for block in raw_context_blocks:
            block_start = parse_timestamp(block["start"], timezone_name)
            block_end = parse_timestamp(block["end"], timezone_name)
            if block_start < work_end and block_end > work_start:
                contained += 1
        same_task_tool_switches += max(0, contained - 1)

    return {
        "schema_version": 1,
        "source": "deterministic_from_ai_semantic_timeline",
        "rule": {
            "entertainment_deviation_minimum_seconds": threshold_seconds,
            "comparison": "strictly_greater_than",
            "brief_communication_is_not_scored": True,
            "same_work_task_tool_switches_are_not_scored": True,
        },
        "level": level,
        "entertainment_deviation_count": count,
        "entertainment_deviation_minutes": rounded_minutes(detour_seconds),
        "all_entertainment_minutes": rounded_minutes(all_entertainment_seconds),
        "longest_entertainment_deviation_minutes": max(
            (item["minutes"] for item in deviations), default=0.0
        ),
        "work_entertainment_transition_count": transitions,
        "brief_communication_minutes": rounded_minutes(
            brief_communication_seconds
        ),
        "longest_continuous_work_minutes": rounded_minutes(longest_work_seconds),
        "same_task_tool_switches_not_scored": same_task_tool_switches,
        "raw_foreground_context_switches_not_scored": cross_device_facts.get(
            "computer_fragmentation_metrics", {}
        ).get("context_switch_count", 0),
        "deviations": deviations,
        "interpretation_note": (
            "等级只反映工作过程中超过30秒的娱乐偏离；"
            "纯娱乐、短暂通信和同任务工具切换不计为混杂。"
        ),
    }
