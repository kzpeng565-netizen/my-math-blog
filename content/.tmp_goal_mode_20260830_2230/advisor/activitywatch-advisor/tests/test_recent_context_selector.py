import json
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from recent_context import create_note
from recent_context_selector import select_recent_context

TZ = ZoneInfo("Asia/Shanghai")
NOW = datetime(2026, 8, 6, 22, 0, 0, tzinfo=TZ)


def settings(selector_enabled=True):
    cfg = {
        "enabled": True,
        "direct_window_hours": 24,
        "preparation_window_days": 7,
        "review_after_days": 14,
        "parser_enabled": False,
        "selector_enabled": selector_enabled,
        "selector_model": "deepseek-v4-flash",
        "selector_thinking": True,
        "selector_reasoning_effort": "low",
        "selector_max_tokens": 800,
        "selector_candidate_limit": 30,
        "selector_output_limit": 6,
        "selector_timeout_seconds": 10,
        "card_limit": 3,
        "max_content_chars": 500,
        "max_impact_chars": 100,
    }
    return {
        "timezone": "Asia/Shanghai",
        "model": {"endpoint": "https://api.deepseek.com/chat/completions"},
        "recent_context": cfg,
    }


def make_note(note_id, content, impact, created, parse, archived=False, pinned=False):
    return {
        "id": note_id,
        "content": content,
        "impact_text": impact,
        "created_at": created,
        "updated_at": created,
        "confirmed_at": created,
        "archived": archived,
        "pinned": pinned,
        "parse": parse,
    }


def fake_generation():
    return {"provider": "DeepSeek", "model": "deepseek-v4-flash", "finish_reason": "stop", "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}}


def selected(note_id, reason="preparation", relevance="medium", importance="normal", related=None):
    return {
        "id": note_id,
        "reason": reason,
        "relevance": relevance,
        "importance": importance,
        "related_task_ids": related or [],
        "summary": "影响当前安排",
    }


class RecentContextSelectorTests(unittest.TestCase):
    def _tasks(self):
        return {
            "tasks": {
                "overdue": [],
                "today": [{"task_id": "^task1", "title": "完成实验汇报", "scheduled_date": "2026-08-06", "priority": "high", "temporal_status": "all_day"}],
                "near_term": [],
                "later": [],
                "recurring": [],
            },
            "task_sync": {"revision": 3, "pending_mutation_count": 0},
        }

    def test_selector_receives_minimal_projection(self):
        notes = [
            make_note("rc_001", "明天下午临时要去实验室", "明天下午", "2026-08-06T21:30:00+08:00",
                      {"v": 1, "hash": "h", "type": "daypart", "date": "2026-08-07", "part": "afternoon", "confidence": "high"}),
            make_note("rc_002", "等老师回复", "直到老师回复", "2026-08-06T21:30:00+08:00",
                      {"v": 1, "hash": "h", "type": "event", "relation": "until", "confidence": "medium"}),
        ]
        captured = {}

        def fake(model, messages):
            captured["payload"] = json.loads(messages[-1]["content"])
            captured["model"] = model
            return {"selected": [selected("rc_002", related=["^task1"])]}, fake_generation()

        with patch("recent_context_selector._request_json_report", side_effect=fake):
            result = select_recent_context(notes, self._tasks(), NOW, settings())
        payload = captured["payload"]
        self.assertEqual(payload["now"], NOW.isoformat(timespec="seconds"))
        self.assertEqual(payload["tasks"][0]["title"], "完成实验汇报")
        self.assertEqual(payload["tasks"][0]["day_offset"], 0)
        self.assertEqual(payload["selection_limit"], 5)
        self.assertEqual(captured["model"]["thinking"], "enabled")
        self.assertEqual(captured["model"]["reasoning_effort"], "low")
        self.assertEqual(captured["model"]["max_tokens"], 800)
        item = payload["context"][0]
        self.assertIn("time", item)
        self.assertEqual(item["time"]["part"], "afternoon")
        # event/open/vague carry recorded_at; the daypart one does not.
        self.assertNotIn("recorded_at", payload["context"][0])
        self.assertEqual(payload["context"][1]["recorded_at"], "2026-08-06T21:30:00+08:00")
        self.assertNotIn("updated_at", payload["context"][0])
        self.assertNotIn("archived", payload["context"][0])
        self.assertFalse(payload["context"][0]["pinned"])
        self.assertTrue(payload["context"][0]["must_include"])
        self.assertNotIn("hash", payload["context"][0])
        self.assertEqual(result["selection"]["selected_ids"], ["rc_001", "rc_002"])
        self.assertEqual(result["selection"]["selector_ranked"][0]["id"], "rc_002")
        self.assertFalse(result["selection"]["fallback_used"])

    def test_forced_kept_even_when_ai_returns_empty(self):
        notes = [
            make_note("rc_force", "今天要去医院", "今天", "2026-08-06T08:00:00+08:00",
                      {"v": 1, "hash": "h", "type": "day", "date": "2026-08-06", "confidence": "high"}),
            make_note("rc_opt", "下周出差", "下周", "2026-08-06T08:00:00+08:00",
                      {"v": 1, "hash": "h", "type": "day", "date": "2026-08-10", "confidence": "high"}),
        ]

        def fake(model, messages):
            return {"selected": []}, fake_generation()

        with patch("recent_context_selector._request_json_report", side_effect=fake):
            result = select_recent_context(notes, self._tasks(), NOW, settings())
        ids = [item["id"] for item in result["items"]]
        self.assertIn("rc_force", ids)
        self.assertIn("rc_force", result["selection"]["forced_ids"])
        self.assertIn("rc_force", result["selection"]["selected_ids"])

    def test_unknown_id_and_bad_reason_dropped(self):
        notes = [
            make_note("rc_ok", "明天考试", "明天", "2026-08-06T08:00:00+08:00",
                      {"v": 1, "hash": "h", "type": "day", "date": "2026-08-07", "confidence": "high"}),
        ]

        def fake(model, messages):
            return {"selected": [selected("rc_fake"), {"id": "rc_ok", "reason": "fabricated"}]}, fake_generation()

        with patch("recent_context_selector._request_json_report", side_effect=fake):
            result = select_recent_context(notes, self._tasks(), NOW, settings())
        self.assertEqual([item["id"] for item in result["items"]], ["rc_ok"])
        self.assertFalse(result["selection"]["fallback_used"])

    def test_ai_failure_falls_back_locally(self):
        notes = [
            make_note("rc_a", "今天有事", "今天", "2026-08-06T08:00:00+08:00",
                      {"v": 1, "hash": "h", "type": "day", "date": "2026-08-06", "confidence": "high"}),
            make_note("rc_b", "明天有事", "明天", "2026-08-06T08:00:00+08:00",
                      {"v": 1, "hash": "h", "type": "day", "date": "2026-08-07", "confidence": "high"}),
            make_note("rc_c", "下月", "下个月", "2026-08-06T08:00:00+08:00",
                      {"v": 1, "hash": "h", "type": "day", "date": "2026-09-01", "confidence": "high"}),
        ]

        notes.append(make_note("rc_d", "等老师回复", "直到老师回复", "2026-08-06T08:00:00+08:00",
                               {"v": 1, "hash": "h", "type": "event", "relation": "until", "confidence": "medium"}))

        def fake(model, messages):
            raise RuntimeError("timeout")

        with patch("recent_context_selector._request_json_report", side_effect=fake):
            result = select_recent_context(notes, self._tasks(), NOW, settings())
        ids = [item["id"] for item in result["items"]]
        self.assertIn("rc_a", ids)
        self.assertIn("rc_b", ids)
        self.assertNotIn("rc_c", ids)
        self.assertTrue(result["selection"]["fallback_used"])

    def test_selector_disabled_falls_back(self):
        notes = [
            make_note("rc_a", "今天有事", "今天", "2026-08-06T08:00:00+08:00",
                      {"v": 1, "hash": "h", "type": "day", "date": "2026-08-06", "confidence": "high"}),
            make_note("rc_b", "等回复", "直到老师回复", "2026-08-06T08:00:00+08:00",
                      {"v": 1, "hash": "h", "type": "event", "relation": "until", "confidence": "medium"}),
        ]
        result = select_recent_context(notes, self._tasks(), NOW, settings(selector_enabled=False))
        self.assertEqual([item["id"] for item in result["items"]], ["rc_a", "rc_b"])
        self.assertTrue(result["selection"]["fallback_used"])

    def test_output_capped_at_limit(self):
        notes = [
            make_note(f"rc_{i:03d}", f"动态{i}", "未来几天", "2026-08-06T08:00:00+08:00",
                      {"v": 1, "hash": "h", "type": "vague", "confidence": "low"})
            for i in range(12)
        ]

        def fake(model, messages):
            return {"selected": [{"id": note["id"], "reason": "conditional"} for note in messages[1:2] and []] + []}, fake_generation()

        with patch("recent_context_selector._request_json_report", side_effect=fake):
            result = select_recent_context(notes, self._tasks(), NOW, settings())
        self.assertLessEqual(len(result["items"]), 6)
        self.assertLessEqual(len(result["selection"]["candidate_ids"]), 30)

    def test_selector_order_and_reasons_are_exposed(self):
        notes = [
            make_note("rc_first", "等一个普通回复", "未确认", "2026-08-06T20:00:00+08:00", {"v": 1, "hash": "h", "type": "event", "relation": "until", "confidence": "medium"}),
            make_note("rc_second", "等待实验室确认", "未确认", "2026-08-06T21:00:00+08:00", {"v": 1, "hash": "h", "type": "event", "relation": "until", "confidence": "medium"}),
        ]
        def fake(model, messages):
            return {"selected": [selected("rc_second", "direct", "high", "high", ["^task1"]), selected("rc_first", "conditional", "medium")]}, fake_generation()
        with patch("recent_context_selector._request_json_report", side_effect=fake):
            result = select_recent_context(notes, self._tasks(), NOW, settings())
        self.assertEqual(result["selection"]["selected_ids"], ["rc_second", "rc_first"])
        self.assertEqual(result["items"][0]["selection_reason"], "direct")
        self.assertEqual(result["items"][0]["related_task_ids"], ["^task1"])
        self.assertTrue(result["selection"]["selector_model"]["thinking"])

    def test_critical_health_note_beats_noncritical_imminent_note(self):
        notes = [
            make_note("rc_health", "我生病发烧，需要安排就医", "身体恢复", "2026-08-06T20:00:00+08:00", {"v": 1, "hash": "h", "type": "event", "relation": "until", "confidence": "medium"}),
            make_note("rc_normal", "明天普通活动", "明天", "2026-08-06T20:00:00+08:00", {"v": 1, "hash": "h", "type": "day", "date": "2026-08-07", "confidence": "high"}),
        ]
        result = select_recent_context(notes, self._tasks(), NOW, settings(selector_enabled=False))
        self.assertEqual(result["items"][0]["id"], "rc_health")
        self.assertEqual(result["items"][0]["importance"], "critical")

    def test_force_cap_keeps_critical_items_and_audits_omitted_items(self):
        """Six forced slots cannot hide health/exam items behind ordinary reminders."""
        critical = [
            make_note(
                f"rc_critical_{index}", f"生病就医跟进 {index}", "身体健康紧急",
                "2026-08-06T20:00:00+08:00",
                {"v": 1, "hash": "h", "type": "event", "relation": "until", "confidence": "medium"},
            )
            for index in range(3)
        ]
        ordinary = [
            make_note(
                f"rc_ordinary_{index}", f"ordinary reminder {index}", "tomorrow",
                "2026-08-06T20:00:00+08:00",
                {"v": 1, "hash": "h", "type": "day", "date": "2026-08-07", "confidence": "high"},
            )
            for index in range(5)
        ]
        result = select_recent_context(critical + ordinary, self._tasks(), NOW, settings(selector_enabled=False))
        selected_ids = result["selection"]["selected_ids"]
        omitted_ids = result["selection"]["forced_omitted_ids"]
        self.assertEqual(len(selected_ids), 6)
        self.assertTrue({note["id"] for note in critical}.issubset(selected_ids))
        self.assertEqual(len(omitted_ids), 2)
        self.assertTrue(all(note_id.startswith("rc_ordinary_") for note_id in omitted_ids))

    def test_selector_gets_four_day_task_window_and_preserves_its_order(self):
        """Flash sees overdue-one-day through day-after, and its ranking remains visible."""
        tasks = {
            "tasks": {
                "overdue": [{"task_id": "^yesterday", "title": "yesterday high", "scheduled_date": "2026-08-05", "priority": "high"}],
                "today": [{"task_id": "^today", "title": "today normal", "scheduled_date": "2026-08-06", "priority": "normal"}],
                "near_term": [
                    {"task_id": "^tomorrow", "title": "tomorrow highest", "scheduled_date": "2026-08-07", "priority": "highest"},
                    {"task_id": "^day_after", "title": "day after", "scheduled_date": "2026-08-08", "priority": "medium"},
                    {"task_id": "^too_far", "title": "not in window", "scheduled_date": "2026-08-09", "priority": "highest"},
                ],
                "later": [],
                "recurring": [{"task_id": "^recurring", "title": "projected recurring", "scheduled_date": "2026-08-08", "priority": "highest", "recurrence_projected": True, "recurrence": "every week on Saturday"}],
                "unassigned": [],
            }
        }
        notes = [
            make_note("rc_a", "wait for a reply", "unconfirmed", "2026-08-06T20:00:00+08:00", {"v": 1, "hash": "h", "type": "event", "relation": "until", "confidence": "medium"}),
            make_note("rc_b", "prepare document", "unconfirmed", "2026-08-06T20:01:00+08:00", {"v": 1, "hash": "h", "type": "event", "relation": "until", "confidence": "medium"}),
        ]
        captured = {}

        def fake(model, messages):
            captured["payload"] = json.loads(messages[-1]["content"])
            return {"selected": [selected("rc_b", "direct", "high", "high", ["^tomorrow"]), selected("rc_a", "conditional", "medium")]}, fake_generation()

        with patch("recent_context_selector._request_json_report", side_effect=fake):
            result = select_recent_context(notes, tasks, NOW, settings())
        payload = captured["payload"]
        self.assertEqual(payload["task_window"], {"from": "2026-08-05", "to": "2026-08-08"})
        self.assertEqual([task["id"] for task in payload["tasks"]], ["^yesterday", "^today", "^tomorrow", "^recurring", "^day_after"])
        self.assertTrue(payload["tasks"][3]["recurrence_projected"])
        self.assertEqual(result["selection"]["selector_ranked"][0]["id"], "rc_b")
        self.assertEqual(result["selection"]["selected_ids"], ["rc_b", "rc_a"])

    def test_conditional_item_has_condition_note(self):
        notes = [
            make_note("rc_x", "等老师回复", "直到老师回复", "2026-08-06T08:00:00+08:00",
                      {"v": 1, "hash": "h", "type": "event", "relation": "until", "confidence": "medium"}),
        ]
        result = select_recent_context(notes, self._tasks(), NOW, settings(selector_enabled=False))
        self.assertEqual(result["items"][0]["status"], "conditional")
        self.assertEqual(result["items"][0]["condition"], "事件状态尚未确认")


if __name__ == "__main__":
    import json
    unittest.main()
