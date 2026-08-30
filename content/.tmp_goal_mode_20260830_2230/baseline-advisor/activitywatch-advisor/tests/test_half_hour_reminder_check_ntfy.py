import sys
import unittest
from datetime import datetime
from pathlib import Path


SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

from notifications import NotificationResult
from run_half_hour import (
    apply_steam_activity_trigger,
    build_half_hour_reminder_check_message,
    send_half_hour_reminder_check_via_ntfy,
    tagged_activity_minutes,
)


class FakeNotifier:
    def __init__(self):
        self.sent = []

    def send(self, *, title, message, priority="default", tags=None):
        self.sent.append(
            {
                "title": title,
                "message": message,
                "priority": priority,
                "tags": list(tags or []),
            }
        )
        return NotificationResult(
            status="accepted",
            provider="fake",
            title=title,
            priority=priority,
            attempt_count=1,
            message_id="test-message",
        )


BASE_CANDIDATE = {
    "would_intervene": True,
    "trigger_reasons": ["high_stimulation", "sustained_low_efficiency_60m"],
    "observations": {
        "high_stimulation_minutes": 12.5,
        "meaningful_minutes": 3.0,
        "meaningful_minutes_60m": 8.0,
        "confirmed_rest_minutes": 0.0,
    },
    "recommended_task": {"title": "学习数学分析"},
    "context_source": "fresh",
    "context_age_minutes": 4,
}


class HalfHourReminderCheckNtfyTests(unittest.TestCase):
    def test_tagged_activity_minutes_counts_only_report_scope(self):
        tagged = {
            "blocks": [
                {"scope": "report", "duration_seconds": 181,
                 "tags": [{"name": "steam_entertainment"}]},
                {"scope": "report", "duration_seconds": 121,
                 "tags": [{"name": "steam_entertainment"}]},
                {"scope": "context_before", "duration_seconds": 600,
                 "tags": [{"name": "steam_entertainment"}]},
            ]
        }
        self.assertEqual(tagged_activity_minutes(tagged, "steam_entertainment"), 5.03)

    def test_steam_over_five_minutes_is_an_independent_half_hour_trigger(self):
        settings = {
            "computer_intervention": {
                "targets": [
                    {
                        "name": "steam游戏",
                        "trigger": "steam_activity",
                        "minimum_activity_minutes": 5,
                    }
                ]
            }
        }
        candidate = {
            "would_intervene": False,
            "trigger_reasons": [],
            "observations": {"steam_activity_minutes": 16.93},
        }

        result = apply_steam_activity_trigger(settings, candidate)

        self.assertTrue(result["would_intervene"])
        self.assertEqual(result["trigger_reasons"], ["steam_activity"])
        self.assertTrue(result["observations"]["steam_activity_triggered"])

    def test_exactly_five_steam_minutes_does_not_trigger(self):
        settings = {
            "computer_intervention": {
                "targets": [
                    {
                        "name": "steam游戏",
                        "trigger": "steam_activity",
                        "minimum_activity_minutes": 5,
                    }
                ]
            }
        }
        candidate = {
            "would_intervene": False,
            "trigger_reasons": [],
            "observations": {"steam_activity_minutes": 5},
        }

        result = apply_steam_activity_trigger(settings, candidate)

        self.assertFalse(result["would_intervene"])
        self.assertEqual(result["trigger_reasons"], [])
        self.assertFalse(result["observations"]["steam_activity_triggered"])

    def test_builds_compact_reminder_check_message(self):
        title, message = build_half_hour_reminder_check_message(
            BASE_CANDIDATE,
            datetime.fromisoformat("2026-07-29T09:00:00+08:00"),
            datetime.fromisoformat("2026-07-29T09:30:00+08:00"),
        )
        self.assertIn("半小时提醒检测系统", title)
        self.assertIn("09:00—09:30", title)
        self.assertIn("high_stimulation", message)
        self.assertIn("学习数学分析", message)
        self.assertIn("不执行干预", message)

    def test_sends_only_when_candidate_would_intervene(self):
        notifier = FakeNotifier()
        result = send_half_hour_reminder_check_via_ntfy(
            BASE_CANDIDATE,
            datetime.fromisoformat("2026-07-29T09:00:00+08:00"),
            datetime.fromisoformat("2026-07-29T09:30:00+08:00"),
            notifier=notifier,
        )
        self.assertEqual(result["status"], "accepted")
        self.assertTrue(result["would_intervene"])
        self.assertEqual(len(notifier.sent), 1)
        self.assertEqual(notifier.sent[0]["priority"], "high")

    def test_skips_when_candidate_would_not_intervene(self):
        notifier = FakeNotifier()
        result = send_half_hour_reminder_check_via_ntfy(
            {**BASE_CANDIDATE, "would_intervene": False},
            datetime.fromisoformat("2026-07-29T09:00:00+08:00"),
            datetime.fromisoformat("2026-07-29T09:30:00+08:00"),
            notifier=notifier,
        )
        self.assertEqual(result["status"], "skipped")
        self.assertEqual(len(notifier.sent), 0)

    def test_no_push_suppresses_ntfy_too(self):
        notifier = FakeNotifier()
        result = send_half_hour_reminder_check_via_ntfy(
            BASE_CANDIDATE,
            datetime.fromisoformat("2026-07-29T09:00:00+08:00"),
            datetime.fromisoformat("2026-07-29T09:30:00+08:00"),
            notifier=notifier,
            no_push=True,
        )
        self.assertEqual(result["status"], "skipped")
        self.assertEqual(result["reason"], "--no-push was supplied")
        self.assertEqual(len(notifier.sent), 0)


if __name__ == "__main__":
    unittest.main()
