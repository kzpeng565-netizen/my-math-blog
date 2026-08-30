from __future__ import annotations

import tempfile
import unittest
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from goal_agent import (
    GoalAgent,
    GoalAgentConflictError,
    consecutive_exam_passes,
    course_grade_scenario,
)


class GoalAgentTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.current = datetime(2026, 8, 30, 22, 30, tzinfo=ZoneInfo("Asia/Shanghai"))
        self.settings = {
            "timezone": "Asia/Shanghai",
            "output_root": str(self.root / "data"),
            "model": {
                "endpoint": "https://example.invalid/chat",
                "name": "test-model",
                "thinking": "disabled",
                "max_tokens": 100,
                "timeout_seconds": 1,
                "retries": 0,
            },
            "goal_agent": {
                "database_path": str(self.root / "goal.sqlite3"),
                "material_root": str(self.root / "materials-root"),
                "tavily_env_file": str(self.root / "missing-tavily.env"),
            },
        }
        self.agent = GoalAgent(
            self.root / "data",
            self.settings,
            env_file=self.root / "missing.env",
            now=lambda: self.current,
            model_runner=self._model,
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    @staticmethod
    def _model(model, messages):
        del model, messages
        return (
            {
                "answer": "证据不足，先完成基线。",
                "assessment": {"distance": "unknown"},
                "plan_changes": [],
                "approval_request": None,
            },
            {"model": "test-model"},
        )

    def request(self, prefix: str, version: int | None = None) -> dict:
        return {
            "request_id": f"{prefix}-12345678",
            "base_plan_version": version if version is not None else self.agent.plan()["plan_version"],
        }

    def test_seed_has_exact_capacity_and_unknown_evidence(self) -> None:
        plan = self.agent.plan()
        self.assertEqual(plan["plan_version"], 1)
        self.assertEqual(len(plan["weeks"]), 4)
        self.assertEqual(plan["weeks"][0]["minutes"], 1590)
        self.assertTrue(all(week["minutes"] == 1590 for week in plan["weeks"]))
        state = self.agent.state()
        self.assertTrue(state["boundaries"]["next_action_is_separate"])
        self.assertEqual({track["status"] for track in state["tracks"]}, {"unknown"})
        self.assertFalse(state["tavily"]["configured"])

    def test_recommendations_respect_each_day_cap(self) -> None:
        with self.agent._connect() as connection:
            rows = connection.execute(
                "SELECT recommended_date,SUM(deep_minutes) AS minutes FROM plan_item GROUP BY recommended_date"
            ).fetchall()
        for row in rows:
            weekday = datetime.fromisoformat(row["recommended_date"]).weekday()
            self.assertLessEqual(row["minutes"], 180 if weekday < 5 else 480)
            self.assertGreaterEqual(row["minutes"], 120 if weekday < 5 else 360)

    def test_three_weeks_of_evidence_adjust_next_week_inside_confirmed_range(self) -> None:
        self.current = datetime(2026, 9, 21, 8, 0, tzinfo=ZoneInfo("Asia/Shanghai"))
        with self.agent._connect() as connection:
            for index, occurred_at in enumerate(("2026-09-01T20:00:00+08:00", "2026-09-08T20:00:00+08:00", "2026-09-15T20:00:00+08:00")):
                connection.execute(
                    "INSERT INTO evidence_event VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (
                        f"history-{index}", "track-courses", None, "weekly_total", occurred_at,
                        1320, None, None, None, None, None, 3, 3, None, None, "{}", occurred_at,
                    ),
                )
        result = self.agent.feedback({
            "request_id": "capacity-12345678",
            "base_plan_version": 1,
            "track_id": "track-courses",
            "evidence_type": "progress_update",
            "deep_minutes": 0,
        })
        self.assertTrue(result["changes"])
        with self.agent._connect() as connection:
            total = connection.execute(
                "SELECT SUM(deep_minutes) FROM plan_item WHERE week_start='2026-09-21'"
            ).fetchone()[0]
        self.assertEqual(total, 1320)

    def test_feedback_is_idempotent_and_conflict_is_409_material(self) -> None:
        payload = {
            **self.request("feedback"),
            "track_id": "track-courses",
            "evidence_type": "course_component",
            "score": 92,
            "max_score": 100,
            "deep_minutes": 120,
            "details": {"course": "概率论", "weight": 0.2},
        }
        first = self.agent.feedback(payload)
        second = self.agent.feedback(payload)
        self.assertEqual(first["event_id"], second["event_id"])
        with self.agent._connect() as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM evidence_event").fetchone()[0], 1)
        with self.assertRaises(GoalAgentConflictError):
            self.agent.feedback({**payload, "request_id": "different-12345678", "base_plan_version": 0})

    def test_accept_day_queues_existing_task_protocol_and_versions(self) -> None:
        state = self.agent.state()
        item = next(item for item in state["current_week"]["items"] if item["id"] == "w1-c-p1")
        captured = []

        def enqueue(body):
            captured.append(body)
            return {"mutation": {"mutation_id": "mutation-1"}}

        result = self.agent.accept_day(
            item["id"],
            {**self.request("acceptday"), "date": item["recommended_date"]},
            enqueue,
        )
        self.assertEqual(result["sync_status"], "queued")
        self.assertTrue(captured[0]["task_id"].startswith("^g"))
        self.assertEqual(captured[0]["operation"], "create")
        self.assertGreater(result["plan_version"], 1)

    def test_task_snapshot_marks_mapping_synced_then_completed(self) -> None:
        plan = self.agent.plan()
        with self.agent._connect() as connection:
            item = dict(connection.execute("SELECT * FROM plan_item WHERE id='w1-c-p1'").fetchone())
        created = self.agent.accept_day(
            item["id"],
            {"request_id": "sync-create-12345678", "base_plan_version": plan["plan_version"], "date": item["recommended_date"]},
            lambda body: {"mutation": {"mutation_id": "m1"}},
        )
        task_id = created["task_id"]
        synced = self.agent.state({"tasks": {"today": [{"task_id": task_id}]}, "completed_recent": []})
        mapped = next(item for item in synced["current_week"]["items"] if item["id"] == "w1-c-p1")
        self.assertEqual(mapped["sync_status"], "synced")
        completed = self.agent.state({"tasks": {}, "completed_recent": [{"task_id": task_id}]})
        mapped = next(item for item in completed["current_week"]["items"] if item["id"] == "w1-c-p1")
        self.assertEqual(mapped["status"], "completed")

    def test_major_change_waits_for_approval(self) -> None:
        payload = {
            **self.request("majorchange"),
            "track_id": "track-ergodic",
            "change_note": "需要调整资源",
            "requested_change": {"track_weights": {"courses": 0.5, "amss_exam": 0.2, "ergodic": 0.2, "abstract_algebra": 0.1}},
        }
        result = self.agent.feedback(payload)
        self.assertIsNotNone(result["approval_request_id"])
        state = self.agent.state()
        self.assertEqual(state["approvals"][0]["status"], "pending")
        self.assertEqual(next(track for track in state["tracks"] if track["code"] == "courses")["weight"], 0.4)

    def test_rollback_creates_new_auditable_version(self) -> None:
        with self.agent._connect() as connection:
            item = dict(connection.execute("SELECT * FROM plan_item WHERE id='w1-c-p1'").fetchone())
        accepted = self.agent.accept_day(
            item["id"],
            {**self.request("rollbackprep"), "date": item["recommended_date"]},
            lambda body: {"mutation": {"mutation_id": "m1"}},
        )
        result = self.agent.rollback(
            1,
            {"request_id": "rollback-12345678", "base_plan_version": accepted["plan_version"]},
        )
        self.assertEqual(result["rolled_back_to"], 1)
        self.assertGreater(result["new_version"], accepted["plan_version"])


class GoalAgentCalculationsTest(unittest.TestCase):
    def test_course_grade_scenario(self) -> None:
        result = course_grade_scenario([
            {"score": 88, "max_score": 100, "payload": {"weight": 0.4}}
        ])
        self.assertEqual(result["state"], "possible")
        self.assertAlmostEqual(result["required_remaining_average"], 91.33, places=2)
        self.assertEqual(course_grade_scenario([])["state"], "unknown")

    def test_three_distinct_120_of_150_attempts(self) -> None:
        result = consecutive_exam_passes([
            {"occurred_at": "2027-01-01", "score": 121, "max_score": 150, "source_id": "paper-a"},
            {"occurred_at": "2027-01-08", "score": 125, "max_score": 150, "source_id": "paper-b"},
            {"occurred_at": "2027-01-15", "score": 120, "max_score": 150, "source_id": "paper-c"},
        ])
        self.assertTrue(result["criterion_met"])
        repeated = consecutive_exam_passes([
            {"occurred_at": "2027-01-01", "score": 121, "max_score": 150, "source_id": "paper-a"},
            {"occurred_at": "2027-01-08", "score": 125, "max_score": 150, "source_id": "paper-a"},
            {"occurred_at": "2027-01-15", "score": 130, "max_score": 150, "source_id": "paper-c"},
        ])
        self.assertFalse(repeated["criterion_met"])


if __name__ == "__main__":
    unittest.main()
