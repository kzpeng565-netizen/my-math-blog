import sys
import unittest
from datetime import datetime
from pathlib import Path


SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

from notifications import NotificationResult
from run_half_hour import build_shadow_ntfy_message, send_shadow_candidate_via_ntfy


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


class HalfHourShadowNtfyTests(unittest.TestCase):
    def test_builds_compact_shadow_message(self):
        title, message = build_shadow_ntfy_message(
            BASE_CANDIDATE,
            datetime.fromisoformat("2026-07-29T09:00:00+08:00"),
            datetime.fromisoformat("2026-07-29T09:30:00+08:00"),
        )
        self.assertIn("09:00—09:30", title)
        self.assertIn("high_stimulation", message)
        self.assertIn("学习数学分析", message)
        self.assertIn("不执行干预", message)

    def test_sends_only_when_shadow_would_intervene(self):
        notifier = FakeNotifier()
        result = send_shadow_candidate_via_ntfy(
            BASE_CANDIDATE,
            datetime.fromisoformat("2026-07-29T09:00:00+08:00"),
            datetime.fromisoformat("2026-07-29T09:30:00+08:00"),
            notifier=notifier,
        )
        self.assertEqual(result["status"], "accepted")
        self.assertTrue(result["would_intervene"])
        self.assertEqual(len(notifier.sent), 1)
        self.assertEqual(notifier.sent[0]["priority"], "high")

    def test_skips_when_shadow_would_not_intervene(self):
        notifier = FakeNotifier()
        result = send_shadow_candidate_via_ntfy(
            {**BASE_CANDIDATE, "would_intervene": False},
            datetime.fromisoformat("2026-07-29T09:00:00+08:00"),
            datetime.fromisoformat("2026-07-29T09:30:00+08:00"),
            notifier=notifier,
        )
        self.assertEqual(result["status"], "skipped")
        self.assertEqual(len(notifier.sent), 0)

    def test_no_push_suppresses_ntfy_too(self):
        notifier = FakeNotifier()
        result = send_shadow_candidate_via_ntfy(
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
