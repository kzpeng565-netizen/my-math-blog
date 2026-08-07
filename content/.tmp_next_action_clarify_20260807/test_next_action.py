import json
import sys
import tempfile
import unittest
from unittest.mock import patch
from datetime import datetime
from pathlib import Path


SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

from next_action import (
    build_decision_state,
    clarify_next_action,
    fallback_suggestion,
    pending_active_suggestion,
    save_outcome,
    save_response,
    _validate_suggestion,
)


def context_snapshot() -> dict:
    return {
        "schema_version": 1,
        "generated_at": "2026-07-29T10:00:00+08:00",
        "timezone": "Asia/Shanghai",
        "sources": {},
        "profile": {"raw_markdown": "优先推进数学学习。"},
        "tasks": {
            "open_task_count": 1,
            "overdue_tasks": [],
            "today_tasks": [
                {
                    "title": "学习动力系统",
                    "category": "数学学习",
                    "priority": "high",
                    "scheduled_date": "2026-07-29",
                    "due_date": None,
                    "tomatoes_completed": 0,
                    "tomatoes_total": 3,
                    "source_order": 1,
                }
            ],
            "near_term_tasks": [],
            "later_tasks": [],
            "recurring_tasks": [],
        },
        "pomodoro": {
            "reference_only": True,
            "last_recorded_session_end": None,
            "last_24h": {},
            "last_3d": {},
            "last_7d": {},
            "data_quality": {"reliability": "low"},
        },
    }


class NextActionTests(unittest.TestCase):
    def test_build_state_uses_context_and_recent_reports(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = root / "context_snapshot.json"
            context.write_text(json.dumps(context_snapshot()), encoding="utf-8")
            (root / "sync_heartbeat.json").write_text(
                json.dumps(
                    {
                        "last_checked_at": "2026-07-29T10:39:00+08:00",
                        "last_successful_export_at": "2026-07-29T10:00:00+08:00",
                        "status": "ok",
                        "source_changed": False,
                        "error": None,
                    }
                ),
                encoding="utf-8",
            )
            report_dir = root / "ai_reports" / "2026-07-29"
            report_dir.mkdir(parents=True)
            (report_dir / "10-00.json").write_text(
                json.dumps(
                    {
                        "period": "2026-07-29 10:00-10:30",
                        "estimated_time_allocation": {
                            "work": {"estimate_minutes": 0},
                            "entertainment": {"estimate_minutes": 25},
                        },
                        "mixing_assessment": {
                            "level": "high",
                            "entertainment_deviation_minutes": 25,
                        },
                    }
                ),
                encoding="utf-8",
            )
            settings = {
                "timezone": "Asia/Shanghai",
                "output_root": str(root),
                "obsidian_context_path": str(context),
                "next_action": {"allowed_durations_minutes": [5, 10, 15, 25, 40]},
            }

            state = build_decision_state(
                settings,
                root,
                now=datetime.fromisoformat("2026-07-29T10:40:00+08:00"),
            )

            self.assertIn("学习动力系统", state["task_titles"])
            self.assertEqual(
                state["obsidian_context"]["pomodoro"]["data_quality"]["reliability"],
                "medium",
            )
            quality = state["data_quality"]
            self.assertEqual(quality["obsidian_snapshot_content_age_minutes"], 40.0)
            self.assertEqual(quality["obsidian_sync_checked_age_minutes"], 1.0)
            self.assertFalse(quality["obsidian_source_changed_at_last_check"])
            self.assertEqual(state["today_totals_from_half_hour_reports"]["entertainment"], 25)
            self.assertEqual(state["hard_rules"]["pomodoro_minutes"], 40)
            self.assertIn("40 minutes", state["hard_rules"]["pomodoro_unit_rule"])
            self.assertIn("estimated task budgets", state["hard_rules"]["pomodoro_role"])
            self.assertTrue(
                state["request_context"]["user_is_awake_for_decision_purposes"]
            )
            self.assertIn(
                "Never use clarify",
                state["hard_rules"]["user_request_implies_awake"],
            )
            self.assertEqual(state["time_context"]["routine_context"], "normal")

    def test_lunch_rest_window_blocks_work_fallback(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = root / "context_snapshot.json"
            context.write_text(json.dumps(context_snapshot()), encoding="utf-8")
            settings = {
                "timezone": "Asia/Shanghai",
                "output_root": str(root),
                "obsidian_context_path": str(context),
                "next_action": {"allowed_durations_minutes": [5, 10, 15, 25, 40]},
            }

            state = build_decision_state(
                settings,
                root,
                now=datetime.fromisoformat("2026-07-29T12:10:00+08:00"),
            )
            suggestion = fallback_suggestion(state)

            self.assertEqual(state["time_context"]["routine_context"], "lunch_rest")
            self.assertEqual(suggestion["decision_type"], "break")
            self.assertEqual(suggestion["duration_minutes"], 40)
            self.assertIn("12:00-13:00", suggestion["reason_short"])

    def test_fallback_suggestion_contains_rich_persuasive_fields(self):
        state = {
            "generated_at": "2026-07-29T10:40:00+08:00",
            "time_context": {"day_period": "morning"},
            "task_titles": ["学习动力系统"],
        }
        suggestion = fallback_suggestion(state)
        self.assertEqual(suggestion["decision_type"], "task")
        self.assertIn("persuasive_explanation", suggestion)
        self.assertIn("anticipated_resistance", suggestion)
        self.assertIn("reduced_version", suggestion)
        self.assertEqual(
            suggestion["decision_trace"]["trace_type"],
            "auditable_summary_not_chain_of_thought",
        )
        self.assertFalse(suggestion["decision_trace"]["model"]["full_reasoning_saved"])
        self.assertIn("为什么是这个", suggestion["display_text"])

    def test_validated_model_suggestion_records_auditable_trace(self):
        state = {
            "generated_at": "2026-07-29T10:40:00+08:00",
            "time_context": {"day_period": "morning", "routine_context": "normal"},
            "task_titles": ["瀛︿範鍔ㄥ姏绯荤粺"],
            "data_quality": {},
            "obsidian_context": {},
        }
        settings = {
            "model": {"name": "deepseek-v4-flash", "thinking": "enabled"},
            "decision_model": {"name": "deepseek-v4-pro", "thinking": "enabled"},
            "next_action": {"allowed_durations_minutes": [5, 10, 15, 25, 40]},
        }
        suggestion = _validate_suggestion(
            {
                "decision_type": "task",
                "title": "鍏堟帹杩涘姩鍔涚郴缁?",
                "duration_minutes": 10,
                "first_step": "鎵撳紑绗旇骞跺厛璇讳竴娈?",
                "task_title": "瀛︿範鍔ㄥ姏绯荤粺",
                "reason_short": "褰撳ぉ浠诲姟鍖归厤锛岄€傚悎灏忓潡鍚姩銆?",
                "evidence_points": ["浠诲姟鍦ㄤ粖鏃ュ垪琛ㄤ腑銆?"],
                "persuasive_explanation": "鍏堝仛涓€灏忔锛岄樆鍔涙渶灏忋€?",
                "anticipated_resistance": "浠诲姟棰樼洰姣旇緝澶с€?",
                "reduced_version": "鍙墦寮€绗旇銆?",
                "confidence": 0.7,
            },
            state,
            settings,
        )

        trace = suggestion["decision_trace"]
        self.assertEqual(trace["model"]["model"], "deepseek-v4-pro")
        self.assertEqual(trace["model"]["thinking"], "enabled")
        self.assertFalse(trace["model"]["full_reasoning_saved"])
        self.assertIn("work_actions_must_match_task_titles", trace["rules_applied"])

    def test_rejects_model_that_treats_25_minutes_as_one_pomodoro(self):
        state = {
            "generated_at": "2026-07-29T10:40:00+08:00",
            "time_context": {"day_period": "morning", "routine_context": "normal"},
            "task_titles": ["学习动力系统"],
            "data_quality": {},
            "obsidian_context": {},
        }
        settings = {
            "model": {"name": "deepseek-v4-flash", "thinking": "enabled"},
            "decision_model": {"name": "deepseek-v4-pro", "thinking": "enabled"},
            "next_action": {"allowed_durations_minutes": [5, 10, 15, 25, 40]},
        }
        with self.assertRaisesRegex(ValueError, "pomodoro unit"):
            _validate_suggestion(
                {
                    "decision_type": "task",
                    "title": "完成一小段学习",
                    "duration_minutes": 25,
                    "first_step": "打开笔记。",
                    "task_title": "学习动力系统",
                    "reason_short": "刚好一个番茄的长度。",
                    "evidence_points": ["仅剩最后1个番茄。"],
                    "persuasive_explanation": "用25分钟完成这个番茄。",
                    "anticipated_resistance": "可能觉得任务大。",
                    "reduced_version": "只做5分钟。",
                    "confidence": 0.7,
                },
                state,
                settings,
            )

    def test_rejects_question_about_whether_user_is_awake(self):
        state = {
            "generated_at": "2026-07-30T09:20:00+08:00",
            "time_context": {"day_period": "morning", "routine_context": "normal"},
            "request_context": {"user_is_awake_for_decision_purposes": True},
            "task_titles": [],
            "data_quality": {},
            "obsidian_context": {},
        }
        settings = {
            "next_action": {"allowed_durations_minutes": [5, 10, 15, 25, 40]},
        }
        with self.assertRaisesRegex(ValueError, "awake clarification"):
            _validate_suggestion(
                {
                    "decision_type": "clarify",
                    "title": "确认你是否已经起床",
                    "duration_minutes": 5,
                    "first_step": "告诉我你现在是否已经醒来。",
                    "task_title": "",
                    "reason_short": "不确定你是否还在睡。",
                    "evidence_points": [],
                    "persuasive_explanation": "先确认状态。",
                    "anticipated_resistance": "",
                    "reduced_version": "回复是否起床。",
                    "confidence": 0.5,
                },
                state,
                settings,
            )

    def test_pending_active_suggestion_requires_outcome_before_new_generation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            active_path = root / "next_action" / "active.json"
            active_path.parent.mkdir(parents=True)
            active_path.write_text(
                json.dumps({"suggestion_id": "s1", "title": "旧建议"}),
                encoding="utf-8",
            )

            self.assertEqual(
                pending_active_suggestion(root)["suggestion_id"],
                "s1",
            )

            save_response(
                root,
                "s1",
                "accepted",
                expected_action_revision=0,
                now=datetime.fromisoformat("2026-07-30T09:10:00+08:00"),
            )
            self.assertIsNotNone(pending_active_suggestion(root))

            save_outcome(
                root,
                "s1",
                "not_started",
                now=datetime.fromisoformat("2026-07-30T09:20:00+08:00"),
            )
            self.assertIsNone(pending_active_suggestion(root))

    def test_declined_or_alternative_response_closes_old_suggestion(self):
        for result in ("declined", "alternative_requested"):
            with self.subTest(result=result), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                active_path = root / "next_action" / "active.json"
                active_path.parent.mkdir(parents=True)
                active_path.write_text(
                    json.dumps({"suggestion_id": "s1", "title": "旧建议"}),
                    encoding="utf-8",
                )
                save_response(
                    root,
                    "s1",
                    result,
                    now=datetime.fromisoformat("2026-07-30T09:10:00+08:00"),
                )
                self.assertIsNone(pending_active_suggestion(root))

    def test_response_and_outcome_are_archived(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            now = datetime.fromisoformat("2026-07-29T10:40:00+08:00")
            response = save_response(
                root,
                "s1",
                "declined",
                reason_code="too_tired",
                detail="刚醒，不适合高强度任务",
                now=now,
            )
            outcome = save_outcome(root, "s1", "not_started", now=now)
            self.assertEqual(response["reason_code"], "too_tired")
            self.assertEqual(outcome["result"], "not_started")
            self.assertTrue((root / "next_action" / "responses" / "2026-07-29").exists())

    def test_two_clarifications_version_the_final_accepted_action(self):
        state = {
            "generated_at": "2026-07-30T10:00:00+08:00",
            "time_context": {"day_period": "morning", "routine_context": "normal"},
            "task_titles": [],
            "data_quality": {},
            "obsidian_context": {"task_sync": {"revision": 4}},
        }
        settings = {
            "model": {"name": "deepseek-v4-flash", "thinking": "enabled", "max_tokens": 800},
            "decision_model": {"name": "deepseek-v4-pro", "thinking": "enabled", "max_tokens": 3500},
            "next_action": {"allowed_durations_minutes": [5, 10, 15, 25, 40]},
        }
        raw = {
            "assistant_message": "先把动作缩到能立刻开始。",
            "action": {
                "decision_type": "break", "title": "离屏喝水", "duration_minutes": 5,
                "first_step": "站起来，给自己倒一杯水。", "task_title": "",
                "reason_short": "先降低启动阻力。", "evidence_points": [],
                "persuasive_explanation": "只要离开屏幕一分钟。", "anticipated_resistance": "不想中断。",
                "reduced_version": "先站起来。", "confidence": 0.7,
            },
        }
        requests = []
        def model_call(_settings, payload):
            requests.append(payload)
            return raw, {"model": "pro"}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            active = {
                "suggestion_id": "s1", "action_id": "s1", "action_revision": 0,
                "decision_type": "break", "title": "旧建议", "duration_minutes": 10,
                "first_step": "停一下。", "task_title": "", "clarification": {"max_rounds": 2, "rounds": []},
            }
            active_path = root / "next_action" / "active.json"
            active_path.parent.mkdir(parents=True)
            active_path.write_text(json.dumps(active), encoding="utf-8")
            with patch("next_action.build_decision_state", return_value=state), patch("next_action._attach_recent_context"), patch("next_action._load_env_file"), patch("next_action._call_clarification_model", side_effect=model_call):
                first = clarify_next_action(settings, root, "s1", "第一步太大", 0)
                self.assertEqual(first["action_revision"], 1)
                self.assertEqual(len(first["clarification"]["rounds"]), 1)
                self.assertEqual(first["decision_trace"]["model"]["model"], "deepseek-v4-pro")
                self.assertEqual(first["decision_trace"]["model"]["thinking"], "enabled")
                accepted = save_response(root, "s1", "accepted", expected_action_revision=1, now=datetime.fromisoformat("2026-07-30T10:01:00+08:00"))
                self.assertEqual(accepted["accepted_action_revision"], 1)
                with self.assertRaisesRegex(ValueError, "already accepted"):
                    clarify_next_action(settings, root, "s1", "还是很累", 1)
                active_path.write_text(json.dumps(first), encoding="utf-8")
                (root / "next_action" / "responses" / "2026-07-30" / "s1-accepted.json").unlink()
                second = clarify_next_action(settings, root, "s1", "还是很累", 1)
                self.assertEqual(second["action_revision"], 2)
                self.assertEqual(requests[1]["dialogue_history"][0]["user_message"], "第一步太大")
                self.assertEqual(requests[1]["dialogue_history"][0]["assistant_message"], "先把动作缩到能立刻开始。")
                self.assertEqual(requests[1]["dialogue_history"][0]["resulting_action"]["action_revision"], 1)
                with self.assertRaisesRegex(ValueError, "round limit"):
                    clarify_next_action(settings, root, "s1", "再来一次", 2)


if __name__ == "__main__":
    unittest.main()

class RecentContextIntegrationTests(unittest.TestCase):
    def _settings(self, root):
        return {
            "timezone": "Asia/Shanghai",
            "output_root": str(root),
            "next_action": {"allowed_durations_minutes": [5, 10, 15, 25, 40]},
            "recent_context": {
                "enabled": True,
                "direct_window_hours": 24,
                "preparation_window_days": 7,
                "review_after_days": 14,
                "parser_enabled": False,
                "selector_enabled": False,
                "selector_candidate_limit": 20,
                "selector_output_limit": 6,
                "max_content_chars": 500,
                "max_impact_chars": 100,
            },
        }

    def test_prompt_version_and_recent_context_addendum(self):
        from next_action import PROMPT_VERSION, _system_prompt_recent_context_addendum
        self.assertEqual(PROMPT_VERSION, "next-action-v1.3")
        addendum = _system_prompt_recent_context_addendum()
        self.assertIn("recent_context_used", addendum)
        self.assertIn("不要重新计算任何相对日期", addendum)

    def test_attach_recent_context_populates_state(self):
        from recent_context import create_note
        from next_action import _attach_recent_context
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            settings = self._settings(root)
            create_note(
                root, "明天下午临时要去实验室", "明天下午", 0, settings,
                now=datetime.fromisoformat("2026-08-06T21:30:00+08:00"),
            )
            state = {
                "generated_at": "2026-08-06T22:00:00+08:00",
                "obsidian_context": {"tasks": {"today": []}},
                "task_titles": [],
            }
            _attach_recent_context(state, settings, root)
            self.assertEqual(len(state["recent_context"]), 1)
            self.assertEqual(state["recent_context"][0]["content"], "明天下午临时要去实验室")
            self.assertEqual(state["recent_context_selection"]["fallback_used"], True)
            self.assertIn(
                state["recent_context"][0]["id"],
                state["recent_context_selection"]["selected_ids"],
            )

    def test_attach_recent_context_degrades_on_corrupt_store(self):
        from next_action import _attach_recent_context
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state_path = root / "recent_context" / "state.json"
            state_path.parent.mkdir(parents=True)
            state_path.write_text("{broken", encoding="utf-8")
            settings = self._settings(root)
            state = {"generated_at": "2026-08-06T22:00:00+08:00", "obsidian_context": {}}
            _attach_recent_context(state, settings, root)
            self.assertEqual(state["recent_context"], [])
            self.assertEqual(state["data_quality"]["recent_context_state"], "corrupt")

    def test_validate_suggestion_sanitizes_recent_context_used(self):
        from next_action import _validate_suggestion
        settings = {
            "timezone": "Asia/Shanghai",
            "next_action": {"allowed_durations_minutes": [5, 10, 15, 25, 40], "rationale_max_characters": 900},
        }
        state = {
            "generated_at": "2026-08-06T22:00:00+08:00",
            "time_context": {"routine_context": "normal", "day_period": "evening"},
            "request_context": {"user_is_awake_for_decision_purposes": True},
            "task_titles": [],
            "obsidian_context": {},
            "exclude_suggestion_id": None,
            "recent_context_selection": {
                "candidate_ids": ["rc_ok", "rc_other"],
                "forced_ids": ["rc_ok"],
                "selected_ids": ["rc_ok", "rc_other"],
                "fallback_used": False,
            },
        }
        raw = {
            "decision_type": "break",
            "title": "起身活动一下",
            "duration_minutes": 5,
            "first_step": "离开座位走动五分钟",
            "task_title": "",
            "reason_short": "久坐后恢复",
            "evidence_points": ["近期动态显示明天有安排。"],
            "persuasive_explanation": "短暂活动有助于继续学习。",
            "anticipated_resistance": "想继续坐",
            "reduced_version": "只站起来",
            "confidence": 0.7,
            "decision_trace": {"recent_context_used": ["rc_ok", "rc_fake", "rc_ok"]},
        }
        normalized = _validate_suggestion(raw, state, settings)
        self.assertEqual(normalized["decision_trace"]["recent_context_used"], ["rc_ok"])
        self.assertEqual(normalized["prompt_version"], "next-action-v1.3")
