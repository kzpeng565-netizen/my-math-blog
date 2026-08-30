import copy
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path


SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

from bedtime_reminder import (
    BedtimeReminderEngine,
    ReminderState,
    StateStore,
    TriggerDecision,
    is_in_window,
)
from notifications import NotificationResult


BASE_POLICY = {
    "enabled": True,
    "active_window": {
        "start": "00:30",
        "end": "04:30",
        "timezone": "Asia/Shanghai",
    },
    "activity": {
        "lookback_seconds": 180,
        "minimum_active_seconds": 30,
        "maximum_data_age_seconds": 120,
    },
    "level_1": {
        "enabled": True,
        "priority": "default",
        "title": "level 1",
        "message": "level 1 body",
    },
    "level_2": {
        "enabled": True,
        "delay_after_level_1_minutes": 5,
        "maximum_notifications": 3,
        "interval_minutes": 1,
        "priority": "high",
        "title": "level 2",
        "message": "level 2 body",
    },
    "cooldown": {"minutes": 25, "on_expire": "recheck"},
    "daily_reset": {
        "time": "04:30",
        "cancel_pending_actions": True,
        "reset_counters": True,
    },
    "test_mode": {
        "level_2_delay_seconds": 20,
        "level_2_interval_seconds": 10,
        "cooldown_seconds": 30,
    },
}


def active_decision() -> TriggerDecision:
    return TriggerDecision(
        triggered=True,
        reason="active",
        evidence={},
        data_fresh=True,
        data_age={"computer": 0.0, "phone": 0.0},
        device_activity_summary={
            "computer_not_afk_seconds": 60,
            "phone_screen_on_seconds": 0,
        },
    )


def inactive_decision(reason: str = "inactive") -> TriggerDecision:
    return TriggerDecision(
        triggered=False,
        reason=reason,
        evidence={},
        data_fresh=reason != "activity_data_stale",
        data_age={"computer": 999.0 if reason == "activity_data_stale" else 0.0},
        device_activity_summary={
            "computer_not_afk_seconds": 0,
            "phone_screen_on_seconds": 0,
        },
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
        )


class SequenceDecisions:
    def __init__(self, *decisions):
        self.decisions = list(decisions)

    def __call__(self, now):
        del now
        if len(self.decisions) == 1:
            return self.decisions[0]
        return self.decisions.pop(0)


class BedtimeReminderTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.store = StateStore(
            self.root / "state.json",
            self.root / "events.jsonl",
        )
        self.notifier = FakeNotifier()
        self.settings = {
            "timezone": "Asia/Shanghai",
            "processing": {},
        }

    def tearDown(self):
        self.tmp.cleanup()

    def engine(self, decisions, test_mode=False):
        return BedtimeReminderEngine(
            settings=self.settings,
            policy=copy.deepcopy(BASE_POLICY),
            store=self.store,
            notifier=self.notifier,
            decision_provider=decisions,
            test_mode=test_mode,
        )

    def test_time_window_boundaries(self):
        self.assertFalse(
            is_in_window(
                datetime.fromisoformat("2026-07-29T00:29:59+08:00"),
                "00:30",
                "04:30",
            )
        )
        self.assertTrue(
            is_in_window(
                datetime.fromisoformat("2026-07-29T00:30:00+08:00"),
                "00:30",
                "04:30",
            )
        )
        self.assertFalse(
            is_in_window(
                datetime.fromisoformat("2026-07-29T04:30:00+08:00"),
                "00:30",
                "04:30",
            )
        )
        self.assertTrue(
            is_in_window(
                datetime.fromisoformat("2026-07-29T23:30:00+08:00"),
                "22:00",
                "02:00",
            )
        )

    def test_level_1_is_not_resent_before_delay(self):
        engine = self.engine(SequenceDecisions(active_decision()))
        engine.step(datetime.fromisoformat("2026-07-29T00:31:00+08:00"))
        engine.step(datetime.fromisoformat("2026-07-29T00:32:00+08:00"))
        self.assertEqual(len(self.notifier.sent), 1)
        self.assertEqual(
            self.store.load()["current_state"],
            ReminderState.LEVEL_1_SENT.value,
        )

    def test_inactive_after_level_1_prevents_level_2(self):
        engine = self.engine(
            SequenceDecisions(active_decision(), inactive_decision())
        )
        engine.step(datetime.fromisoformat("2026-07-29T00:31:00+08:00"))
        engine.step(datetime.fromisoformat("2026-07-29T00:36:00+08:00"))
        self.assertEqual(len(self.notifier.sent), 1)
        self.assertEqual(self.store.load()["current_state"], ReminderState.WAITING.value)

    def test_stale_data_after_level_1_cancels_escalation(self):
        engine = self.engine(
            SequenceDecisions(
                active_decision(),
                inactive_decision("activity_data_stale"),
            )
        )
        engine.step(datetime.fromisoformat("2026-07-29T00:31:00+08:00"))
        engine.step(datetime.fromisoformat("2026-07-29T00:36:00+08:00"))
        self.assertEqual(len(self.notifier.sent), 1)
        log = (self.root / "events.jsonl").read_text(encoding="utf-8")
        self.assertIn("activity_data_stale", log)

    def test_level_2_sends_three_times_then_cooldown(self):
        engine = self.engine(SequenceDecisions(active_decision()), test_mode=True)
        engine.step(datetime.fromisoformat("2026-07-29T00:31:00+08:00"))
        engine.step(datetime.fromisoformat("2026-07-29T00:31:20+08:00"))
        engine.step(datetime.fromisoformat("2026-07-29T00:31:30+08:00"))
        engine.step(datetime.fromisoformat("2026-07-29T00:31:40+08:00"))
        self.assertEqual(len(self.notifier.sent), 4)
        self.assertEqual(
            [item["priority"] for item in self.notifier.sent],
            ["default", "high", "high", "high"],
        )
        self.assertEqual(self.store.load()["current_state"], ReminderState.COOLDOWN.value)

    def test_0430_resets_state_without_sending(self):
        engine = self.engine(SequenceDecisions(active_decision()))
        engine.step(datetime.fromisoformat("2026-07-29T00:31:00+08:00"))
        engine.step(datetime.fromisoformat("2026-07-29T04:30:00+08:00"))
        self.assertEqual(len(self.notifier.sent), 1)
        state = self.store.load()
        self.assertEqual(state["current_state"], ReminderState.DISABLED.value)
        self.assertEqual(state["level_2_count"], 0)


if __name__ == "__main__":
    unittest.main()
