import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from focus_garden.database import GardenDatabase


class GardenDatabaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.db = GardenDatabase(Path(self.temp.name) / "test.sqlite3")

    def tearDown(self):
        self.temp.cleanup()

    def test_reward_import_is_idempotent_and_plants_once(self):
        event = {"id":"one", "type":"early_sleep", "occurred_at":"2026-08-01T23:59:00+08:00",
                 "reason":"早睡", "source":"test", "payload":{}}
        self.assertEqual(self.db.import_rewards([event]), 1)
        self.assertEqual(self.db.import_rewards([event]), 0)
        plant = self.db.plant_reward("one", "dandelion")
        repeated = self.db.plant_reward("one", "dandelion")
        self.assertEqual((plant["x"], plant["y"]), (repeated["x"], repeated["y"]))
        self.assertEqual(len(self.db.garden()["plants"]), 1)

    def test_explicit_steam_night_close_mints_one_idempotent_basic_reward(self):
        first = self.db.record_steam_night_closed(
            "steam-night:2026-08-14", "2026-08-14T23:30:20+08:00"
        )
        second = self.db.record_steam_night_closed(
            "steam-night:2026-08-14", "2026-08-14T23:30:20+08:00"
        )
        self.assertEqual(first["id"], second["id"])
        self.assertEqual(first["type"], "steam_night_closed")
        self.assertEqual(first["tier"], "basic")
        self.assertEqual(len(self.db.rewards("pending")), 1)

    def test_intervention_requires_three_acceptances_and_advanced_spends_three_basic_opportunities(self):
        events = [{"id": f"i{index}", "type": "intervention_accepted",
                   "occurred_at": f"2026-08-01T00:0{index}:00+00:00", "reason": "介入",
                   "source": "test", "payload": {}} for index in range(3)]
        self.db.import_rewards(events)
        pending = self.db.rewards("pending")
        self.assertEqual(len(pending), 1)
        self.assertEqual((pending[0]["type"], pending[0]["tier"]), ("intervention_basic", "basic"))
        with self.assertRaises(ValueError):
            self.db.plant_reward("i0", "dandelion")

        for index in range(2):
            reward = {"id": f"b{index}", "type": "early_sleep", "occurred_at": f"2026-08-02T00:0{index}:00+00:00",
                      "reason": "基础", "source": "test", "payload": {}}
            self.db.import_rewards([reward])

        stats = self.db.stats()
        self.assertEqual((stats["basic_available"], stats["advanced_available"]), (3, 1))
        with self.assertRaises(ValueError):
            self.db.plant_advanced_from_basic("dandelion", "basic")
        self.db.plant_advanced_from_basic("red_mushroom", "advanced")
        stats = self.db.stats()
        self.assertEqual((stats["basic_available"], stats["advanced_planted"], stats["advanced_available"]), (0, 1, 0))

    def test_garden_expands_after_25_plants(self):
        events = [{"id":f"r{i}", "type":"focus_completed", "occurred_at":"2026-08-01T00:00:00+00:00",
                   "reason":"专注", "source":"test", "payload":{}} for i in range(26)]
        self.db.import_rewards(events)
        for event in events:
            self.db.plant_reward(event["id"], "dandelion")
        self.assertEqual(self.db.garden()["size"], 7)

    def test_focus_minutes_carry_over(self):
        first = self.db.create_focus("study", 25, "2026-08-01T00:00:00+00:00", "2026-08-01T00:25:00+00:00")
        self.assertEqual(self.db.complete_focus(first["id"]), 0)
        second = self.db.create_focus("study", 25, "2026-08-01T01:00:00+00:00", "2026-08-01T01:25:00+00:00")
        self.assertEqual(self.db.complete_focus(second["id"]), 1)
        self.assertEqual(self.db.stats()["focus_credit_minutes"], 10)

    def test_completed_focus_summary_uses_completion_time_and_ignores_cancelled_sessions(self):
        completed = self.db.create_focus("study", 40, "2026-08-01T00:00:00+00:00", "2026-08-01T00:40:00+00:00")
        self.db.complete_focus(completed["id"])
        with self.db._connection() as conn:
            conn.execute("UPDATE focus_sessions SET completed_at=? WHERE id=?", ("2026-08-05T03:00:00+00:00", completed["id"]))
        cancelled = self.db.create_focus("study", 20, "2026-08-01T01:00:00+00:00", "2026-08-01T01:20:00+00:00")
        self.db.cancel_focus(cancelled["id"])
        summary = self.db.completed_focus_summary(
            datetime.fromisoformat("2026-08-05T00:00:00+00:00"),
            datetime.fromisoformat("2026-08-06T00:00:00+00:00"),
        )
        self.assertEqual(summary, {"focus_minutes": 40, "completed_count": 1})

    def test_cycle_plan_advances_after_each_completed_round(self):
        plan = self.db.create_focus_plan("cycle", "study", 30, 5, 2, ["phone"], "2026-08-01T00:00:00+00:00")
        self.assertEqual(self.db.next_due_focus_plan("2026-08-01T00:00:01+00:00")["id"], plan["id"])
        session = self.db.create_focus("study", 30, "2026-08-01T00:00:00+00:00", "2026-08-01T00:30:00+00:00")
        self.db.mark_focus_plan_started(plan["id"], session["id"])
        self.db.complete_focus(session["id"])
        self.db.advance_focus_plan_for_session(session["id"], "2026-08-01T00:30:00+00:00")
        advanced = self.db.focus_plans()[0]
        self.assertEqual((advanced["status"], advanced["current_round"]), ("break", 1))
        self.assertEqual(advanced["next_action_at"], "2026-08-01T00:35:00+00:00")

    def test_bridge_heartbeat_is_persisted(self):
        heartbeat = self.db.record_bridge_heartbeat("android-main", "accessibility_connected", "running")
        self.assertEqual(heartbeat["status"], "accessibility_connected")
        self.assertEqual(self.db.bridge_health("android-main")["detail"], "running")

    def test_daily_full_tomato_awards_one_direct_advanced_opportunity(self):
        cards = [{"date": "2026-08-08", "planned_tomatoes": 7,
                  "completed_tomatoes": 7, "task_count": 3, "eligible": True}]
        self.assertEqual(self.db.record_daily_scorecards(cards, "2026-08-09"), 1)
        self.assertEqual(self.db.record_daily_scorecards(cards, "2026-08-09"), 0)
        reward = next(item for item in self.db.rewards("pending") if item["id"] == "daily-full-tomato:2026-08-08")
        self.assertEqual(reward["tier"], "advanced")
        stats = self.db.stats()
        self.assertEqual((stats["advanced_direct_available"], stats["advanced_available"]), (1, 1))
        with self.assertRaises(ValueError):
            self.db.plant_reward(reward["id"], "dandelion", "basic")
        self.db.plant_reward(reward["id"], "red_mushroom", "advanced")
        self.assertEqual(self.db.stats()["advanced_direct_available"], 0)
        achievement = self.db.daily_achievements()[0]
        self.assertEqual((achievement["date"], achievement["eligible"]), ("2026-08-08", 1))

    def test_daily_challenge_does_not_award_current_or_incomplete_day(self):
        cards = [
            {"date": "2026-08-08", "planned_tomatoes": 7, "completed_tomatoes": 6, "task_count": 2},
            {"date": "2026-08-09", "planned_tomatoes": 8, "completed_tomatoes": 8, "task_count": 2},
        ]
        self.assertEqual(self.db.record_daily_scorecards(cards, "2026-08-09"), 0)
        self.assertEqual(len(self.db.rewards("pending")), 0)
        self.assertEqual(self.db.daily_achievements()[0]["eligible"], 0)


if __name__ == "__main__":
    unittest.main()
