import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from task_sync import (
    acknowledge_mutations,
    compact_for_next_action,
    effective_state,
    enqueue_mutation,
    set_primary_task,
)
from next_action import build_decision_state


class TaskSyncTests(unittest.TestCase):
    def _snapshot(self, root: Path) -> Path:
        path = root / "context_snapshot.json"
        path.write_text(
            json.dumps(
                {
                    "tasks": {
                        "overdue_tasks": [],
                        "today_tasks": [
                            {
                                "task_id": "^8m2kx7q4",
                                "title": "原任务",
                                "priority": "normal",
                                "scheduled_date": "2026-08-05",
                                "due_date": None,
                                "recurrence": None,
                                "tomatoes_completed": 0,
                                "tomatoes_total": 2,
                                "source_order": 1,
                            }
                        ],
                        "near_term_tasks": [],
                        "later_tasks": [],
                        "recurring_tasks": [],
                        "unassigned_tasks": [
                            {
                                "task_id": "^unassigned1",
                                "title": "待安排任务",
                                "priority": "high",
                                "scheduled_date": None,
                                "due_date": None,
                                "recurrence": None,
                                "tomatoes_completed": None,
                                "tomatoes_total": None,
                                "source_order": 2,
                                "task_source": "collection",
                            }
                        ],
                    }
                }
            ),
            encoding="utf-8",
        )
        return path

    def test_mutations_immediately_change_effective_view_then_ack(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = self._snapshot(root)
            updated = enqueue_mutation(
                context,
                root,
                {
                    "operation": "update",
                    "task_id": "^8m2kx7q4",
                    "scheduled_date": "2026-08-07",
                },
            )
            self.assertTrue(any(task["task_id"] == "^8m2kx7q4" for group in updated["effective"]["tasks"].values() for task in group))
            created = enqueue_mutation(
                context,
                root,
                {
                    "operation": "create",
                    "task_id": "^2z7q1w8e",
                    "title": "网页新增",
                    "scheduled_date": "2026-08-05",
                    "priority": "high",
                },
            )
            compact = compact_for_next_action(created["effective"])
            self.assertEqual(compact["task_sync"]["pending_mutation_count"], 2)
            self.assertTrue(any(task["title"] == "网页新增" for group in compact["tasks"].values() for task in group))
            snapshot = json.loads(context.read_text(encoding="utf-8"))
            snapshot["tasks"]["today_tasks"][0]["scheduled_date"] = "2026-08-07"
            snapshot["tasks"]["today_tasks"].append(
                {
                    "task_id": "^2z7q1w8e",
                    "title": "网页新增",
                    "priority": "high",
                    "scheduled_date": "2026-08-05",
                    "due_date": None,
                    "recurrence": None,
                    "tomatoes_completed": None,
                    "tomatoes_total": None,
                    "source_order": 3,
                }
            )
            context.write_text(json.dumps(snapshot), encoding="utf-8")
            exported = effective_state(context, root)
            ack = acknowledge_mutations(
                context,
                root,
                {
                    "snapshot_sha256": exported["snapshot_sha256"],
                    "mutation_ids": [
                        item["mutation_id"] for item in created["effective"]["mutations"]
                    ],
                },
            )
            self.assertEqual(ack["acknowledged"], 2)
            self.assertEqual(ack["effective"]["pending_mutation_count"], 0)

    def test_two_postponed_days_mark_task_and_survive_ack(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = self._snapshot(root)
            fixed_now = datetime(2026, 8, 5, 9, 0, tzinfo=ZoneInfo("Asia/Shanghai"))
            first = enqueue_mutation(
                context,
                root,
                {
                    "operation": "postpone",
                    "task_id": "^8m2kx7q4",
                    "scheduled_date": "2026-08-06",
                },
                now=fixed_now,
            )
            first_task = next(
                task for group in first["effective"]["tasks"].values() for task in group
                if task["task_id"] == "^8m2kx7q4"
            )
            self.assertEqual(first_task["postponed_days"], 1)
            self.assertFalse(first_task["procrastinated"])

            second = enqueue_mutation(
                context,
                root,
                {
                    "operation": "postpone",
                    "task_id": "^8m2kx7q4",
                    "scheduled_date": "2026-08-07",
                },
                now=fixed_now,
            )
            second_task = next(
                task for group in second["effective"]["tasks"].values() for task in group
                if task["task_id"] == "^8m2kx7q4"
            )
            self.assertEqual(second_task["postponed_days"], 2)
            self.assertEqual(second_task["postpone_count"], 2)
            self.assertTrue(second_task["procrastinated"])
            compact_task = next(
                task for group in compact_for_next_action(second["effective"])["tasks"].values()
                for task in group if task["task_id"] == "^8m2kx7q4"
            )
            self.assertTrue(compact_task["procrastinated"])

            snapshot = json.loads(context.read_text(encoding="utf-8"))
            snapshot["tasks"]["today_tasks"][0]["scheduled_date"] = "2026-08-07"
            context.write_text(json.dumps(snapshot), encoding="utf-8")
            exported = effective_state(context, root, now=fixed_now)
            ack = acknowledge_mutations(
                context,
                root,
                {
                    "snapshot_sha256": exported["snapshot_sha256"],
                    "mutation_ids": [item["mutation_id"] for item in second["effective"]["mutations"]],
                },
            )
            acked_task = next(
                task for group in ack["effective"]["tasks"].values() for task in group
                if task["task_id"] == "^8m2kx7q4"
            )
            self.assertEqual(acked_task["postponed_days"], 2)
            self.assertTrue(acked_task["procrastinated"])

    def test_normal_schedule_edit_does_not_count_as_postponement(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = self._snapshot(root)
            result = enqueue_mutation(
                context,
                root,
                {
                    "operation": "update",
                    "task_id": "^8m2kx7q4",
                    "scheduled_date": "2026-08-09",
                },
            )
            task = next(
                task for group in result["effective"]["tasks"].values() for task in group
                if task["task_id"] == "^8m2kx7q4"
            )
            self.assertNotIn("postponed_days", task)
            self.assertNotIn("procrastinated", task)

    def test_ack_rejects_matching_but_stale_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = self._snapshot(root)
            updated = enqueue_mutation(
                context,
                root,
                {
                    "operation": "update",
                    "task_id": "^8m2kx7q4",
                    "scheduled_date": "2026-08-07",
                },
            )
            with self.assertRaisesRegex(ValueError, "does not reflect"):
                acknowledge_mutations(
                    context,
                    root,
                    {
                        "snapshot_sha256": updated["effective"]["snapshot_sha256"],
                        "mutation_ids": [updated["mutation"]["mutation_id"]],
                    },
                )
            self.assertEqual(effective_state(context, root)["pending_mutation_count"], 1)

    def test_ack_accepts_final_value_after_multiple_updates_to_same_task(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = self._snapshot(root)
            enqueue_mutation(
                context,
                root,
                {"operation": "update", "task_id": "^8m2kx7q4", "scheduled_date": "2026-08-07"},
            )
            latest = enqueue_mutation(
                context,
                root,
                {"operation": "update", "task_id": "^8m2kx7q4", "scheduled_date": "2026-08-10"},
            )
            snapshot = json.loads(context.read_text(encoding="utf-8"))
            snapshot["tasks"]["today_tasks"][0]["scheduled_date"] = "2026-08-10"
            context.write_text(json.dumps(snapshot), encoding="utf-8")
            exported = effective_state(context, root)
            ack = acknowledge_mutations(
                context,
                root,
                {
                    "snapshot_sha256": exported["snapshot_sha256"],
                    "mutation_ids": [item["mutation_id"] for item in latest["effective"]["mutations"]],
                },
            )
            self.assertEqual(ack["acknowledged"], 2)
            self.assertEqual(ack["effective"]["pending_mutation_count"], 0)

    def test_rejects_non_block_ids_and_invalid_dates(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = self._snapshot(root)
            with self.assertRaises(ValueError):
                enqueue_mutation(context, root, {"operation": "complete", "task_id": "bad"})
            with self.assertRaises(ValueError):
                enqueue_mutation(
                    context,
                    root,
                    {"operation": "update", "task_id": "^8m2kx7q4", "scheduled_date": "tomorrow"},
                )

    def test_rejects_existing_id_and_completes_weekly_occurrence_with_existing_update_protocol(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = self._snapshot(root)
            with self.assertRaises(ValueError):
                enqueue_mutation(
                    context,
                    root,
                    {"operation": "create", "task_id": "^8m2kx7q4", "title": "duplicate"},
                )
            snapshot = json.loads(context.read_text(encoding="utf-8"))
            snapshot["tasks"]["today_tasks"][0]["recurrence"] = "every week on Wednesday"
            context.write_text(json.dumps(snapshot), encoding="utf-8")
            fixed_now = datetime(2026, 8, 5, 9, 0, tzinfo=ZoneInfo("Asia/Shanghai"))
            result = enqueue_mutation(context, root, {"operation": "complete", "task_id": "^8m2kx7q4"}, now=fixed_now)
            self.assertEqual(result["mutation"]["operation"], "update")
            self.assertEqual(result["mutation"]["payload"], {
                "scheduled_date": "2026-08-12", "tomatoes_completed": 0,
            })
            self.assertEqual(result["effective"]["completed_today"][0]["task_id"], "^8m2kx7q4")
            self.assertTrue(result["effective"]["completed_today"][0]["recurring"])
            self.assertFalse(any(
                task["task_id"] == "^8m2kx7q4"
                for group in result["effective"]["tasks"].values() for task in group
                if task.get("scheduled_date") == "2026-08-05"
            ))

            repeated = enqueue_mutation(context, root, {"operation": "complete", "task_id": "^8m2kx7q4"}, now=fixed_now)
            self.assertEqual(repeated["completion"]["completion_key"], "^8m2kx7q4@2026-08-05")
            self.assertEqual(repeated["effective"]["pending_mutation_count"], 1)

    def test_completed_task_stays_in_completed_today_after_writeback_ack(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = self._snapshot(root)
            result = enqueue_mutation(context, root, {"operation": "complete", "task_id": "^8m2kx7q4"})
            self.assertEqual(result["effective"]["completed_today"][0]["title"], "原任务")
            snapshot = json.loads(context.read_text(encoding="utf-8"))
            snapshot["tasks"]["today_tasks"] = []
            context.write_text(json.dumps(snapshot), encoding="utf-8")
            exported = effective_state(context, root)
            ack = acknowledge_mutations(context, root, {
                "snapshot_sha256": exported["snapshot_sha256"],
                "mutation_ids": [result["mutation"]["mutation_id"]],
            })
            self.assertEqual(ack["effective"]["pending_mutation_count"], 0)
            self.assertFalse(ack["effective"]["completed_today"][0]["sync_pending"])

    def test_daily_scorecard_is_monotonic_and_eligible_at_seven_completed_tomatoes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = self._snapshot(root)
            snapshot = json.loads(context.read_text(encoding="utf-8"))
            snapshot["tasks"]["today_tasks"][0].update({"tomatoes_completed": 7, "tomatoes_total": 7})
            context.write_text(json.dumps(snapshot), encoding="utf-8")
            fixed_now = datetime(2026, 8, 5, 9, 0, tzinfo=ZoneInfo("Asia/Shanghai"))
            effective = effective_state(context, root, now=fixed_now)
            card = effective["daily_scorecards"][0]
            self.assertEqual((card["planned_tomatoes"], card["completed_tomatoes"]), (7, 7))
            self.assertTrue(card["eligible"])
            snapshot["tasks"]["today_tasks"][0].update({"tomatoes_completed": 0, "tomatoes_total": 2})
            context.write_text(json.dumps(snapshot), encoding="utf-8")
            card = effective_state(context, root, now=fixed_now)["daily_scorecards"][0]
            self.assertEqual((card["planned_tomatoes"], card["completed_tomatoes"]), (7, 7))

    def test_primary_task_is_limited_to_today_or_tomorrow_and_toggles(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = self._snapshot(root)
            fixed_now = datetime(2026, 8, 5, 9, 0, tzinfo=ZoneInfo("Asia/Shanghai"))
            selected = set_primary_task(
                context, root, {"task_id": "^8m2kx7q4"}, now=fixed_now
            )
            task = selected["tasks"]["today"][0]
            self.assertTrue(task["is_primary"])
            self.assertEqual(selected["primary_tasks"]["2026-08-05"]["task_id"], "^8m2kx7q4")
            cleared = set_primary_task(
                context, root, {"task_id": "^8m2kx7q4"}, now=fixed_now
            )
            self.assertEqual(cleared["primary_tasks"], {})
            with self.assertRaisesRegex(ValueError, "today or tomorrow"):
                set_primary_task(
                    context, root, {"task_id": "^unassigned1"}, now=fixed_now
                )

    def test_steam_unlock_requires_six_tomatoes_and_completed_primary(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = self._snapshot(root)
            fixed_now = datetime(2026, 8, 5, 9, 0, tzinfo=ZoneInfo("Asia/Shanghai"))
            set_primary_task(context, root, {"task_id": "^8m2kx7q4"}, now=fixed_now)
            snapshot = json.loads(context.read_text(encoding="utf-8"))
            snapshot["tasks"]["today_tasks"][0].update(
                {"tomatoes_completed": 6, "tomatoes_total": 6}
            )
            context.write_text(json.dumps(snapshot), encoding="utf-8")
            before = effective_state(context, root, now=fixed_now)["steam_unlock_gate"]
            self.assertTrue(before["tomato_requirement_met"])
            self.assertFalse(before["primary_task_completed"])
            self.assertFalse(before["eligible"])
            completed = enqueue_mutation(
                context, root, {"operation": "complete", "task_id": "^8m2kx7q4"}, now=fixed_now
            )["effective"]["steam_unlock_gate"]
            self.assertTrue(completed["primary_task_completed"])
            self.assertTrue(completed["eligible"])

    def test_unassigned_task_can_be_scheduled_or_deleted(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = self._snapshot(root)
            initial = compact_for_next_action(enqueue_mutation(
                context, root, {"operation": "update", "task_id": "^unassigned1", "scheduled_date": "2026-08-08"}
            )["effective"])
            self.assertTrue(any(task["task_id"] == "^unassigned1" for group in initial["tasks"].values() for task in group))
            deleted = enqueue_mutation(context, root, {"operation": "delete", "task_id": "^unassigned1"})
            self.assertFalse(any(task["task_id"] == "^unassigned1" for group in deleted["effective"]["tasks"].values() for task in group))

    def test_weekly_recurrence_projects_to_current_or_next_occurrence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = self._snapshot(root)
            snapshot = json.loads(context.read_text(encoding="utf-8"))
            saturday = snapshot["tasks"]["today_tasks"][0]
            saturday.update({
                "task_id": "^saturday1",
                "scheduled_date": "2026-08-01",
                "recurrence": "every week on Saturday",
            })
            sunday = dict(saturday)
            sunday.update({
                "task_id": "^sunday01",
                "scheduled_date": "2026-08-02",
                "recurrence": "every week on Sunday",
                "source_order": 2,
            })
            monday = dict(saturday)
            monday.update({
                "task_id": "^monday01",
                "scheduled_date": "2026-08-03",
                "recurrence": "every week on Monday",
                "source_order": 3,
            })
            snapshot["tasks"]["today_tasks"] = [saturday, sunday, monday]
            context.write_text(json.dumps(snapshot), encoding="utf-8")
            effective = effective_state(
                context,
                root,
                now=datetime(2026, 8, 8, 9, 0, tzinfo=ZoneInfo("Asia/Shanghai")),
            )
            recurring = {task["task_id"]: task for task in effective["tasks"]["recurring"]}
            self.assertEqual(recurring["^saturday1"]["scheduled_date"], "2026-08-08")
            self.assertEqual(recurring["^sunday01"]["scheduled_date"], "2026-08-09")
            self.assertEqual(recurring["^monday01"]["scheduled_date"], "2026-08-10")
            self.assertEqual(recurring["^saturday1"]["source_scheduled_date"], "2026-08-01")
            self.assertTrue(recurring["^saturday1"]["recurrence_projected"])
            compact = compact_for_next_action(effective)
            projected = {task["task_id"]: task for task in compact["tasks"]["recurring"]}
            self.assertEqual(projected["^monday01"]["scheduled_date"], "2026-08-10")

    def test_next_action_receives_effective_tasks_and_explicit_current_time(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = self._snapshot(root)
            state = build_decision_state(
                {"timezone": "Asia/Shanghai", "obsidian_context_path": str(context)},
                root,
                now=datetime(2026, 8, 5, 13, 40, tzinfo=ZoneInfo("Asia/Shanghai")),
            )
            self.assertEqual(state["time_context"]["current_timestamp"], "2026-08-05T13:40:00+08:00")
            self.assertEqual(state["obsidian_context"]["tasks"]["today"][0]["task_id"], "^8m2kx7q4")

    def test_exported_direct_completion_is_attributed_by_stable_id(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = self._snapshot(root)
            snapshot = json.loads(context.read_text(encoding="utf-8"))
            snapshot["task_events"] = {
                "completed_recent": [
                    {
                        "event_id": "^goaltask@2026-08-05",
                        "task_id": "^goaltask",
                        "title": "目标模式任务",
                        "completed_at": "2026-08-05",
                        "completion_time_precision": "date",
                        "task_modified_at": "2026-08-05T19:20:00+08:00",
                    }
                ]
            }
            context.write_text(json.dumps(snapshot), encoding="utf-8")
            effective = effective_state(
                context,
                root,
                now=datetime(2026, 8, 5, 20, 0, tzinfo=ZoneInfo("Asia/Shanghai")),
            )
            self.assertEqual(effective["completed_recent"][0]["task_id"], "^goaltask")
            self.assertEqual(effective["completed_recent"][0]["source"], "obsidian_export")
            self.assertEqual(effective["completed_today"][0]["completion_time_precision"], "date")

    def test_client_request_id_replays_even_after_snapshot_ack(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = self._snapshot(root)
            payload = {
                "request_id": "goal-request-12345678",
                "operation": "create",
                "task_id": "^goalitem",
                "title": "目标任务",
                "scheduled_date": "2026-08-06",
            }
            first = enqueue_mutation(context, root, payload)
            mutation = first["mutation"]
            snapshot = json.loads(context.read_text(encoding="utf-8"))
            snapshot["tasks"]["near_term_tasks"].append(
                {
                    "task_id": "^goalitem",
                    "title": "目标任务",
                    "scheduled_date": "2026-08-06",
                    "priority": "normal",
                    "source_order": 99,
                    "task_source": "planned",
                }
            )
            context.write_text(json.dumps(snapshot), encoding="utf-8")
            digest = __import__("hashlib").sha256(context.read_bytes()).hexdigest()
            acknowledge_mutations(
                context,
                root,
                {"snapshot_sha256": digest, "mutation_ids": [mutation["mutation_id"]]},
            )
            replay = enqueue_mutation(context, root, payload)
            self.assertTrue(replay["idempotent_replay"])
            self.assertEqual(replay["mutation"]["mutation_id"], mutation["mutation_id"])
            self.assertEqual(replay["effective"]["pending_mutation_count"], 0)


if __name__ == "__main__":
    unittest.main()
