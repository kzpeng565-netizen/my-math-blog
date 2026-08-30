import json
import sqlite3
import tempfile
import unittest
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from focus_garden.control_metrics import ControlMetrics


SHANGHAI = ZoneInfo("Asia/Shanghai")


class ControlMetricsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.advisor = self.root / "advisor"
        self.obsidian = self.root / "obsidian"
        self.database = self.root / "garden.sqlite3"
        self.snapshot = self.root / "control-review.json"
        (self.advisor / "statistics" / "daily_life").mkdir(parents=True)
        (self.advisor / "task_sync").mkdir(parents=True)
        self.obsidian.mkdir(parents=True)
        conn = sqlite3.connect(self.database)
        try:
            conn.execute("""CREATE TABLE focus_sessions(
                task_id TEXT, task_title TEXT, completed_at TEXT,
                duration_minutes INTEGER, credited_minutes INTEGER, status TEXT
            )""")
            conn.commit()
        finally:
            conn.close()
        (self.advisor / "task_sync" / "state.json").write_text(
            json.dumps({"completions": []}), encoding="utf-8"
        )
        self.metrics = ControlMetrics(self.database, self.advisor, self.obsidian, self.snapshot)

    def tearDown(self):
        self.temp.cleanup()

    def test_state_priority_marks_abandonment_before_other_failures(self):
        values = {
            "M": (2, 8), "D": (4, 0), "W": (200, 700), "L": (900, 400),
            "A": (0.2, 0.8), "F": (0.2, 0.8), "U": (2 / 7, 6 / 7), "R": (0.2, 0.8),
        }
        state = self.metrics._classify(values, {
            "report_days": 7, "report_stale_days": 1, "asked": 7,
            "accepted": 4, "recovery_offers": 5, "math_quality": "high",
        })
        self.assertEqual("S5", state["code"])
        self.assertTrue(state["redline_triggered"])

    def test_build_returns_eight_aggregate_metrics_without_task_text(self):
        end = date(2026, 8, 14)
        secret_title = "不要出现在接口里的任务正文"
        (self.obsidian / "context_snapshot.json").write_text(json.dumps({
            "tasks": {"today_tasks": [{
                "task_id": "^math01", "title": secret_title, "category": "数学学习"
            }]}
        }, ensure_ascii=False), encoding="utf-8")
        conn = sqlite3.connect(self.database)
        try:
            conn.execute(
                "INSERT INTO focus_sessions VALUES(?,?,?,?,?,?)",
                ("^math01", secret_title, "2026-08-14T04:00:00+00:00", 40, 40, "completed"),
            )
            conn.commit()
        finally:
            conn.close()
        for offset in range(8):
            day = end - timedelta(days=offset)
            report = {
                "period": day.isoformat(),
                "daily_totals": {"work_minutes": 120, "entertainment_minutes": 30},
                "ai_usage": {"by_activity": {"work": 10, "entertainment": 2, "other": 0, "uncertain": 1}},
                "obsidian_context": {"tasks": {"overdue": []}},
                "tomorrow_task_candidates": [],
            }
            (self.advisor / "statistics" / "daily_life" / f"{day}.json").write_text(
                json.dumps(report), encoding="utf-8"
            )
        report = self.metrics.build(datetime(2026, 8, 15, 12, tzinfo=SHANGHAI))
        self.assertEqual(list("MDWLAFUR"), [item["id"] for item in report["metrics"]])
        self.assertEqual(1.0, report["metrics"][0]["value"])
        self.assertFalse(report["policy"]["automatic_parameter_mutation"])
        self.assertNotIn(secret_title, json.dumps(report, ensure_ascii=False))

    def test_existing_review_remains_frozen(self):
        future = (datetime.now(SHANGHAI) + timedelta(days=2)).isoformat(timespec="seconds")
        self.snapshot.write_text(json.dumps({
            "schema_version": 1, "generated_at": "2026-08-15T12:00:00+08:00",
            "frozen_until": future, "state": {"code": "S0"},
        }), encoding="utf-8")
        result = self.metrics.write_snapshot()
        self.assertEqual("still_frozen", result["write_state"])
        self.assertEqual("S0", result["state"]["code"])

    def test_manual_sync_refreshes_metrics_but_preserves_frozen_decision(self):
        generated_at = "2026-08-15T12:00:00+08:00"
        future = (datetime.now(SHANGHAI) + timedelta(days=2)).isoformat(timespec="seconds")
        self.snapshot.write_text(json.dumps({
            "schema_version": 1,
            "generated_at": generated_at,
            "frozen_until": future,
            "state": {"code": "S0", "name": "正常运行"},
            "policy": {"automatic_parameter_mutation": False},
        }), encoding="utf-8")

        result = self.metrics.sync_status()

        self.assertEqual("synced_live", result["snapshot_state"])
        self.assertEqual("S0", result["state"]["code"])
        self.assertEqual(generated_at, result["decision_generated_at"])
        self.assertEqual(future, result["frozen_until"])
        self.assertTrue(self.metrics.live_snapshot_path.is_file())
        self.assertEqual("synced_live", self.metrics.load_snapshot()["snapshot_state"])
        self.assertNotIn("_tasks", json.dumps(result, ensure_ascii=False))

    def test_delay_debt_uses_open_postponements_priority_and_seven_day_cap(self):
        (self.obsidian / "context_snapshot.json").write_text(json.dumps({
            "generated_at": "2026-08-15T04:00:00+08:00",
            "tasks": {
                "today_tasks": [
                    {"task_id": "^high01", "priority": "high", "completed": False},
                    {"task_id": "^done01", "priority": "highest", "completed": True},
                ],
                "near_term_tasks": [
                    {"task_id": "^high01", "priority": "high", "completed": False},
                ],
            },
        }), encoding="utf-8")
        (self.advisor / "task_sync" / "state.json").write_text(json.dumps({
            "revision": 9,
            "postponements": {
                "^high01": {"postponed_days": 12, "postpone_count": 3},
                "^done01": {"postponed_days": 4, "postpone_count": 1},
            },
            "completions": [],
        }), encoding="utf-8")
        result = self.metrics.save_daily_snapshot(on_date=date(2026, 8, 15), force=True)
        self.assertEqual(14.0, result["delay_debt"])
        self.assertEqual(1, result["postponed_task_count"])
        self.assertEqual(12, result["max_postponed_days"])

    def test_recovery_uses_base_offer_and_successful_execute_pair_only(self):
        root = self.advisor / "computer_interventions" / "responses" / "2026-08-14"
        root.mkdir(parents=True)
        base = "2026-08-14-10-00_10-30"
        (root / "accepted-final.json").write_text(json.dumps({
            "event": {"request_id": base, "decision": "accepted", "decided_at": "2026-08-14T10:15:00+08:00"}
        }), encoding="utf-8")
        (root / "execute-final.json").write_text(json.dumps({
            "event": {"request_id": base + "-execute", "decision": "accepted",
                      "executions": [{"status": "success"}], "decided_at": "2026-08-14T10:16:00+08:00"}
        }), encoding="utf-8")
        (root / "manual-final.json").write_text(json.dumps({
            "event": {"request_id": "manual-focus-abc", "decision": "accepted",
                      "executions": [{"status": "success"}], "decided_at": "2026-08-14T11:00:00+08:00"}
        }), encoding="utf-8")
        values = self.metrics._interventions_by_day({date(2026, 8, 14)})
        self.assertEqual(1, values[date(2026, 8, 14)]["offers"])
        self.assertEqual(1, values[date(2026, 8, 14)]["accepted"])


if __name__ == "__main__":
    unittest.main()
