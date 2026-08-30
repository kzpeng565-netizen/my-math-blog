import copy
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path


SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

from notifications import NotificationResult
from sysadmin_time_guard import (
    GuardDecision,
    GuardState,
    StateStore,
    SysadminTimeGuardEngine,
    _intervals_from_facts,
    is_maintenance_item,
)


BASE_POLICY = {
    "enabled": True,
    "timezone": "Asia/Shanghai",
    "activity": {
        "lookback_minutes": 60,
        "level_1_window_minutes": 30,
        "level_2_window_minutes": 60,
        "cooldown_clear_minutes": 60,
        "minimum_active_seconds": 60,
        "level_1_maintenance_ratio": 0.75,
        "level_2_maintenance_ratio": 0.65,
        "level_2_minimum_edge_ratio": 0.4,
        "maximum_data_age_seconds": 600,
    },
    "classification": {
        "maintenance_apps": ["powershell.exe", "WindowsTerminal.exe", "Code.exe"],
        "maintenance_domains": ["pi.local", "pi.taild4d3f7.ts.net"],
        "maintenance_title_keywords": ["systemd", "ntfy", "树莓派", "系统维护"],
        "context_bridge_apps": ["ChatGPT.exe", "msedge.exe"],
        "context_bridge_keywords": ["ChatGPT"],
        "context_bridge_max_gap_seconds": 300,
        "non_maintenance_title_keywords": ["数学", "math"],
    },
    "level_1": {
        "title": "level 1",
        "message": "level 1 body",
        "priority": "default",
    },
    "level_2": {
        "title": "level 2",
        "message": "level 2 body",
        "priority": "high",
    },
}


def decision(
    *,
    level_1=False,
    level_2=False,
    maintenance_seconds_60m=0,
    reason="test",
):
    return GuardDecision(
        level_1=level_1,
        level_2=level_2,
        reason=reason,
        data_fresh=True,
        summary={
            "maintenance_seconds_60m": maintenance_seconds_60m,
            "maintenance_ratio_30m": 1.0 if level_1 else 0.0,
            "maintenance_ratio_60m": 1.0 if level_2 else 0.0,
        },
        evidence={},
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


class SysadminTimeGuardTests(unittest.TestCase):
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

    def engine(self, decisions):
        return SysadminTimeGuardEngine(
            settings=self.settings,
            policy=copy.deepcopy(BASE_POLICY),
            store=self.store,
            notifier=self.notifier,
            decision_provider=decisions,
        )

    def test_classifies_maintenance_by_app_domain_and_title(self):
        policy = BASE_POLICY["classification"]
        self.assertTrue(
            is_maintenance_item({"app": "powershell.exe", "title": "ssh pi"}, policy)
        )
        self.assertTrue(
            is_maintenance_item(
                {"app": "msedge.exe", "domain": "pi.taild4d3f7.ts.net"},
                policy,
            )
        )
        self.assertTrue(
            is_maintenance_item({"title": "systemd timer 调试"}, policy)
        )
        self.assertFalse(
            is_maintenance_item({"title": "数学 proof in Obsidian"}, policy)
        )

    def test_adjacent_chatgpt_inherits_system_maintenance_context(self):
        policy = BASE_POLICY["classification"]
        facts = {
            "timeline": [
                {
                    "start": "2026-07-29T10:00:00+08:00",
                    "end": "2026-07-29T10:05:00+08:00",
                    "app": "msedge.exe",
                    "app_display": "Microsoft Edge",
                    "domain": "pi.taild4d3f7.ts.net",
                    "title": "activitywatch-advisor - Pi Server Files",
                },
                {
                    "start": "2026-07-29T10:05:30+08:00",
                    "end": "2026-07-29T10:15:30+08:00",
                    "app": "ChatGPT.exe",
                    "app_display": "ChatGPT",
                    "domain": "",
                    "title": "ChatGPT",
                },
                {
                    "start": "2026-07-29T10:16:00+08:00",
                    "end": "2026-07-29T10:20:00+08:00",
                    "app": "msedge.exe",
                    "app_display": "Microsoft Edge",
                    "domain": "pi.taild4d3f7.ts.net",
                    "title": "systemd timer",
                },
            ]
        }
        intervals = _intervals_from_facts(facts, policy, "Asia/Shanghai")
        self.assertTrue(all(item[2] for item in intervals))
        self.assertEqual(
            intervals[1][3]["maintenance_classification_source"],
            "context_bridge",
        )

    def test_math_chatgpt_does_not_inherit_maintenance_context(self):
        policy = BASE_POLICY["classification"]
        facts = {
            "timeline": [
                {
                    "start": "2026-07-29T10:00:00+08:00",
                    "end": "2026-07-29T10:05:00+08:00",
                    "app": "msedge.exe",
                    "app_display": "Microsoft Edge",
                    "domain": "pi.taild4d3f7.ts.net",
                    "title": "activitywatch-advisor - Pi Server Files",
                },
                {
                    "start": "2026-07-29T10:05:30+08:00",
                    "end": "2026-07-29T10:15:30+08:00",
                    "app": "ChatGPT.exe",
                    "app_display": "ChatGPT",
                    "domain": "",
                    "title": "ChatGPT 数学证明",
                },
            ]
        }
        intervals = _intervals_from_facts(facts, policy, "Asia/Shanghai")
        self.assertTrue(intervals[0][2])
        self.assertFalse(intervals[1][2])

    def test_level_1_sends_once(self):
        engine = self.engine(
            SequenceDecisions(
                decision(level_1=True, maintenance_seconds_60m=1800),
                decision(level_1=True, maintenance_seconds_60m=2100),
            )
        )
        engine.step(datetime.fromisoformat("2026-07-29T10:30:00+08:00"))
        engine.step(datetime.fromisoformat("2026-07-29T10:35:00+08:00"))
        self.assertEqual(len(self.notifier.sent), 1)
        self.assertEqual(self.notifier.sent[0]["title"], "level 1")
        self.assertEqual(
            self.store.load()["current_state"],
            GuardState.LEVEL_1_SENT.value,
        )

    def test_level_1_escalates_to_level_2(self):
        engine = self.engine(
            SequenceDecisions(
                decision(level_1=True, maintenance_seconds_60m=1800),
                decision(level_1=True, level_2=True, maintenance_seconds_60m=3600),
            )
        )
        engine.step(datetime.fromisoformat("2026-07-29T10:30:00+08:00"))
        engine.step(datetime.fromisoformat("2026-07-29T11:00:00+08:00"))
        self.assertEqual([item["title"] for item in self.notifier.sent], ["level 1", "level 2"])
        self.assertEqual(
            self.store.load()["current_state"],
            GuardState.COOLDOWN.value,
        )

    def test_level_2_can_fire_directly_if_first_seen_late(self):
        engine = self.engine(
            SequenceDecisions(
                decision(level_1=True, level_2=True, maintenance_seconds_60m=3600)
            )
        )
        engine.step(datetime.fromisoformat("2026-07-29T11:00:00+08:00"))
        self.assertEqual(len(self.notifier.sent), 1)
        self.assertEqual(self.notifier.sent[0]["title"], "level 2")
        self.assertEqual(
            self.store.load()["current_state"],
            GuardState.COOLDOWN.value,
        )

    def test_cooldown_resets_only_after_one_hour_without_maintenance(self):
        engine = self.engine(
            SequenceDecisions(
                decision(level_1=True, level_2=True, maintenance_seconds_60m=3600),
                decision(maintenance_seconds_60m=1),
                decision(maintenance_seconds_60m=0),
                decision(maintenance_seconds_60m=0),
            )
        )
        engine.step(datetime.fromisoformat("2026-07-29T11:00:00+08:00"))
        engine.step(datetime.fromisoformat("2026-07-29T11:30:00+08:00"))
        engine.step(datetime.fromisoformat("2026-07-29T12:20:00+08:00"))
        self.assertEqual(self.store.load()["current_state"], GuardState.COOLDOWN.value)
        engine.step(datetime.fromisoformat("2026-07-29T12:31:00+08:00"))
        self.assertEqual(self.store.load()["current_state"], GuardState.IDLE.value)
        self.assertEqual(len(self.notifier.sent), 1)


if __name__ == "__main__":
    unittest.main()
