import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path


SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

from behavior_advisor import build_shadow_candidate
from obsidian_context import load_obsidian_context


def snapshot():
    task = {
        "title": "遍历论当前章节",
        "category": "数学学习",
        "priority": "highest",
        "scheduled_date": "2026-07-27",
        "due_date": None,
        "tomatoes_completed": 0,
        "tomatoes_total": 3,
        "source_order": 1,
    }
    return {
        "schema_version": 1,
        "generated_at": "2026-07-27T12:00:00+08:00",
        "timezone": "Asia/Shanghai",
        "sources": {},
        "profile": {"raw_markdown": "正常休息不应被否定。"},
        "tasks": {
            "open_task_count": 1,
            "overdue_tasks": [],
            "today_tasks": [task],
            "near_term_tasks": [],
            "later_tasks": [],
            "recurring_tasks": [],
            "latest_plan_heading": "2026-07-27 假期任务重排",
            "latest_plan_notes_markdown": "先完成遍历论。",
            "parser_warnings": [],
        },
        "pomodoro": {
            "reference_only": True,
            "last_recorded_session_end": None,
            "last_24h": {},
            "last_3d": {},
            "last_7d": {},
            "data_quality": {"reliability": "low"},
            "interpretation_warning": "无记录不能解释为无学习。",
        },
    }


class ContextTests(unittest.TestCase):
    def test_valid_json_and_conflict_file_is_ignored(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            live, cache = root / "context_snapshot.json", root / "cache.json"
            live.write_text(json.dumps(snapshot()), encoding="utf-8")
            (root / "context_snapshot.sync-conflict.json").write_text(
                "{broken", encoding="utf-8"
            )
            result = load_obsidian_context(
                live, cache, datetime(2026, 7, 27, 5, tzinfo=timezone.utc)
            )
            self.assertEqual(result["context_source"], "live")
            self.assertTrue(cache.exists())

    def test_partial_json_and_unsupported_schema_fall_back(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            live, cache = root / "context_snapshot.json", root / "cache.json"
            cache.write_text(json.dumps(snapshot()), encoding="utf-8")
            live.write_text('{"schema_version":', encoding="utf-8")
            self.assertEqual(
                load_obsidian_context(live, cache)["context_source"],
                "last_known_good",
            )
            broken_schema = snapshot()
            broken_schema["schema_version"] = 99
            live.write_text(json.dumps(broken_schema), encoding="utf-8")
            self.assertEqual(
                load_obsidian_context(live, cache)["context_source"],
                "last_known_good",
            )

    def test_missing_without_cache_is_unavailable(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = load_obsidian_context(root / "missing", root / "also-missing")
            self.assertFalse(result["available"])
            self.assertEqual(result["reason"], "context_unavailable")

    def test_shadow_zhihu_candidate_and_no_pomodoro_trigger(self):
        context = {
            "available": True,
            "context_source": "live",
            "context_age_minutes": 5,
            "ai_context": {
                "tasks": {
                    "overdue": [],
                    "today": snapshot()["tasks"]["today_tasks"],
                    "near_term": [],
                }
            },
        }
        semantic = {
            "segments": [
                {
                    "activity": "entertainment",
                    "duration_seconds": 720,
                    "task": "浏览知乎",
                }
            ]
        }
        cross = {
            "time_accounting_observed": {
                "computer_not_afk_minutes": 25,
                "phone_screen_on_minutes": 0,
                "confirmed_rest_minutes": 0,
            }
        }
        settings = {"behavior_advisor": {"enabled": True, "shadow_mode": True}}
        result = build_shadow_candidate(
            settings,
            datetime.fromisoformat("2026-07-27T20:30:00+08:00"),
            semantic,
            {},
            cross,
            context,
        )
        self.assertTrue(result["would_intervene"])
        self.assertFalse(result["push_sent"])
        self.assertEqual(result["recommended_task"]["title"], "遍历论当前章节")
        self.assertFalse(result["observations"]["pomodoro_used_as_trigger"])

    def test_two_windows_form_sixty_minute_low_efficiency_candidate(self):
        settings = {
            "behavior_advisor": {
                "enabled": True,
                "shadow_mode": True,
                "active_device_minutes_threshold": 40,
                "low_efficiency_meaningful_minutes_threshold": 15,
            }
        }
        context = {"available": False, "context_source": "unavailable"}
        semantic = {"segments": [{"activity": "other", "duration_seconds": 1200}]}
        cross = {
            "time_accounting_observed": {
                "computer_not_afk_minutes": 21,
                "phone_screen_on_minutes": 0,
                "confirmed_rest_minutes": 0,
            }
        }
        previous = {
            "observations": {
                "active_device_minutes": 21,
                "meaningful_minutes": 0,
                "mainline_present": False,
            }
        }
        result = build_shadow_candidate(
            settings,
            datetime.fromisoformat("2026-07-27T20:30:00+08:00"),
            semantic,
            {},
            cross,
            context,
            [previous],
        )
        self.assertIn("sustained_low_efficiency_60m", result["trigger_reasons"])
        self.assertIn("two_windows_without_mainline", result["trigger_reasons"])

    def test_math_study_and_confirmed_rest_do_not_intervene(self):
        settings = {"behavior_advisor": {"enabled": True, "shadow_mode": True}}
        context = {"available": False, "context_source": "unavailable"}
        math = {"segments": [{"activity": "work", "duration_seconds": 1500}]}
        cross = {
            "time_accounting_observed": {
                "computer_not_afk_minutes": 25,
                "phone_screen_on_minutes": 0,
                "confirmed_rest_minutes": 0,
            }
        }
        result = build_shadow_candidate(
            settings, datetime.now().astimezone(), math, {}, cross, context
        )
        self.assertFalse(result["would_intervene"])
        rest_cross = {
            "time_accounting_observed": {
                "computer_not_afk_minutes": 0,
                "phone_screen_on_minutes": 0,
                "confirmed_rest_minutes": 30,
            }
        }
        result = build_shadow_candidate(
            settings, datetime.now().astimezone(), {"segments": []}, {}, rest_cross, context
        )
        self.assertFalse(result["would_intervene"])


if __name__ == "__main__":
    unittest.main()
