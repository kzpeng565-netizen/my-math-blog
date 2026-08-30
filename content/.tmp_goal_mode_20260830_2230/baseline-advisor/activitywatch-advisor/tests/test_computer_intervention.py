import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo


SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

from computer_intervention import (
    archive_legacy_unleased_release_requests,
    build_computer_intervention_request,
    build_manual_focus_request,
    build_manual_focus_release_request,
    latest_pending_request,
    latest_pending_device_request,
    receive_computer_intervention_event,
    resolve_intervention_decision,
    save_computer_intervention_request,
)


BASE_INTERVENTION = {
    "would_intervene": True,
    "trigger_reasons": ["high_stimulation"],
    "observations": {
        "high_stimulation_minutes": 12,
        "meaningful_minutes_60m": 3,
    },
}


class ComputerInterventionTests(unittest.TestCase):
    def test_shared_decline_streak_resets_after_episode_timeout(self):
        timezone = ZoneInfo("Asia/Shanghai")
        with tempfile.TemporaryDirectory() as directory:
            output_root = Path(directory)
            now = datetime.now(timezone)
            offer = build_computer_intervention_request(
                {}, now - timedelta(minutes=30), now, BASE_INTERVENTION,
                {"segments": [{"activity": "entertainment", "evidence": ["x.com"]}]},
            )
            save_computer_intervention_request(output_root, offer)
            state_path = output_root / "computer_interventions" / "state" / "shared-episode.json"
            state_path.parent.mkdir(parents=True)
            state_path.write_text(json.dumps({
                "decline_streak": 1,
                "last_decline_at": (now - timedelta(minutes=91)).isoformat(),
            }), encoding="utf-8")

            result = resolve_intervention_decision(
                output_root, offer["request_id"], "declined", "windows-main"
            )["decision"]

            self.assertEqual(result["decision"], "declined")
            self.assertEqual(result["decline_streak_before"], 0)
            self.assertEqual(result["decline_streak_after"], 1)
            state = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual(state["last_reset_reason"], "episode_timeout")

    def test_adjacent_decline_is_still_forced(self):
        timezone = ZoneInfo("Asia/Shanghai")
        with tempfile.TemporaryDirectory() as directory:
            output_root = Path(directory)
            now = datetime.now(timezone)
            offer = build_computer_intervention_request(
                {}, now - timedelta(minutes=30), now, BASE_INTERVENTION,
                {"segments": [{"activity": "entertainment", "evidence": ["x.com"]}]},
            )
            save_computer_intervention_request(output_root, offer)
            state_path = output_root / "computer_interventions" / "state" / "shared-episode.json"
            state_path.parent.mkdir(parents=True)
            state_path.write_text(json.dumps({
                "decline_streak": 1,
                "last_decline_at": (now - timedelta(minutes=30)).isoformat(),
            }), encoding="utf-8")

            result = resolve_intervention_decision(
                output_root, offer["request_id"], "declined", "windows-main"
            )["decision"]

            self.assertEqual(result["decision"], "forced")
            self.assertEqual(result["decline_streak_before"], 1)
            self.assertEqual(result["decline_streak_after"], 0)

    def test_manual_focus_carries_absolute_deadline_and_configurable_phone_ladder(self):
        timezone = ZoneInfo("Asia/Shanghai")
        now = datetime(2026, 8, 10, 10, 0, tzinfo=timezone)
        request = build_manual_focus_request(
            {}, 60, ["phone"], now=now,
            focus_deadline_at="2026-08-10T11:00:00+08:00",
            allowed_phone_minutes=[5, 20, 30, 40, 45, 60],
        )
        self.assertEqual(request["focus_deadline_at"], "2026-08-10T11:00:00+08:00")
        self.assertEqual(request["expires_after_seconds"], 3660)
        self.assertEqual(request["phone"]["allowed_minutes"], [5, 20, 30, 40, 45, 60])
        self.assertEqual(request["phone"]["duration_strategy"], "nearest_remaining_midpoint_tie_longer")

    def test_phone_release_completes_itself_and_superseded_lock_request(self):
        timezone = ZoneInfo("Asia/Shanghai")
        with tempfile.TemporaryDirectory() as directory:
            output_root = Path(directory)
            release = build_manual_focus_release_request(
                {}, [], lease_id="manual-focus-original", requested_targets=["phone"],
                now=datetime(2026, 8, 10, 11, 0, tzinfo=timezone),
            )
            save_computer_intervention_request(output_root, release)
            response = receive_computer_intervention_event(output_root, {
                "computer_id": "android-main", "request_id": release["request_id"],
                "decision": "released", "status": "success", "final": True,
            })
            completed = response["state"]["completed_request_ids"]
            self.assertIn(release["request_id"], completed)
            self.assertIn("manual-focus-original", completed)

    def test_accepted_phone_execution_remains_pollable_for_fifteen_minutes(self):
        timezone = ZoneInfo("Asia/Shanghai")
        with tempfile.TemporaryDirectory() as directory:
            output_root = Path(directory)
            now = datetime.now(timezone)
            offer = build_computer_intervention_request(
                {}, now - timedelta(minutes=30), now, BASE_INTERVENTION,
                {"segments": [{"activity": "entertainment", "evidence": ["x.com"]}]},
            )
            save_computer_intervention_request(output_root, offer)
            result = resolve_intervention_decision(
                output_root, offer["request_id"], "accepted", "android-main"
            )
            request = latest_pending_device_request(
                output_root, "android-main", "phone", now + timedelta(minutes=10)
            )
            self.assertEqual(request["request_id"], result["decision"]["execution_request_id"])
            self.assertEqual(request["expires_after_seconds"], 960)

    def test_builds_general_request(self):
        start = datetime.fromisoformat("2026-07-31T11:00:00+08:00")
        end = datetime.fromisoformat("2026-07-31T11:30:00+08:00")
        request = build_computer_intervention_request(
            {},
            start,
            end,
            BASE_INTERVENTION,
            {"segments": [{"activity": "entertainment", "evidence": ["x.com"]}]},
        )
        self.assertIsNotNone(request)
        self.assertEqual(request["targets"][0]["cold_turkey_block"], "常刷网站")
        self.assertEqual(len(request["targets"]), 1)

    def test_steam_target_requires_strictly_more_than_five_minutes(self):
        start = datetime.fromisoformat("2026-08-14T14:00:00+08:00")
        end = start + timedelta(minutes=30)
        settings = {
            "computer_intervention": {
                "targets": [
                    {
                        "name": "steam游戏",
                        "cold_turkey_block": "steam游戏",
                        "lock_minutes": 30,
                        "trigger": "steam_activity",
                        "minimum_activity_minutes": 5,
                        "pre_lock_countdown_seconds": 60,
                    }
                ]
            }
        }
        at_threshold = {
            **BASE_INTERVENTION,
            "observations": {**BASE_INTERVENTION["observations"], "steam_activity_minutes": 5},
        }
        above_threshold = {
            **BASE_INTERVENTION,
            "observations": {**BASE_INTERVENTION["observations"], "steam_activity_minutes": 5.01},
        }
        self.assertIsNone(build_computer_intervention_request(
            settings, start, end, at_threshold, {"segments": []}
        ))
        request = build_computer_intervention_request(
            settings, start, end, above_threshold, {"segments": []}
        )
        self.assertEqual(request["targets"][0]["name"], "steam游戏")
        self.assertEqual(request["targets"][0]["pre_lock_countdown_seconds"], 60)

    def test_bilibili_is_exempt_on_sunday(self):
        start = datetime.fromisoformat("2026-08-02T10:00:00+08:00")
        end = datetime.fromisoformat("2026-08-02T10:30:00+08:00")
        request = build_computer_intervention_request(
            {},
            start,
            end,
            BASE_INTERVENTION,
            {"segments": [{"activity": "entertainment", "evidence": ["bilibili"]}]},
        )
        bilibili = [item for item in request["targets"] if item["name"] == "bilibili"][0]
        self.assertTrue(bilibili["exempt"])
        self.assertFalse(bilibili["enabled"])

    def test_completed_request_is_not_pending(self):
        timezone = ZoneInfo("Asia/Shanghai")
        with tempfile.TemporaryDirectory() as directory:
            output_root = Path(directory)
            start = datetime(2026, 7, 31, 11, 0, tzinfo=timezone)
            end = start + timedelta(minutes=30)
            request = build_computer_intervention_request(
                {},
                start,
                end,
                BASE_INTERVENTION,
                {"segments": [{"activity": "entertainment", "evidence": ["x.com"]}]},
            )
            save_computer_intervention_request(output_root, request)
            pending = latest_pending_request(output_root, "windows-main", end)
            self.assertEqual(pending["request_id"], request["request_id"])
            receive_computer_intervention_event(
                output_root,
                {
                    "computer_id": "windows-main",
                    "request_id": request["request_id"],
                    "decision": "forced",
                    "final": True,
                    "decline_streak_after": 0,
                },
            )
            self.assertIsNone(latest_pending_request(output_root, "windows-main", end))

    def test_duplicate_final_event_is_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            output_root = Path(directory)
            event = {
                "computer_id": "android-main",
                "request_id": "phone-lock-1",
                "decision": "accepted",
                "status": "success",
                "final": True,
            }
            first = receive_computer_intervention_event(output_root, event)
            second = receive_computer_intervention_event(output_root, event)

            self.assertFalse(first.get("already_completed", False))
            self.assertTrue(second["already_completed"])
            self.assertIsNone(second["path"])
            responses = list(
                (output_root / "computer_interventions" / "responses").glob("*/*.json")
            )
            self.assertEqual(len(responses), 1)

    def test_newer_non_intervention_candidate_suppresses_stale_request(self):
        timezone = ZoneInfo("Asia/Shanghai")
        with tempfile.TemporaryDirectory() as directory:
            output_root = Path(directory)
            start = datetime(2026, 8, 1, 21, 30, tzinfo=timezone)
            end = start + timedelta(minutes=30)
            request = build_computer_intervention_request(
                {},
                start,
                end,
                BASE_INTERVENTION,
                {"segments": [{"activity": "entertainment", "evidence": ["x.com"]}]},
            )
            save_computer_intervention_request(output_root, request)
            candidate_path = (
                output_root
                / "intervention_candidates"
                / "2026-08-01"
                / "22-00.json"
            )
            candidate_path.parent.mkdir(parents=True)
            candidate_path.write_text('{"would_intervene": false}', encoding="utf-8")

            self.assertIsNone(
                latest_pending_request(
                    output_root,
                    "windows-main",
                    datetime(2026, 8, 1, 23, 18, tzinfo=timezone),
                )
            )

    def test_release_request_is_durable_and_stable_for_same_lease(self):
        timezone = ZoneInfo("Asia/Shanghai")
        first = build_manual_focus_release_request(
            {}, ["常刷网站"], lease_id="manual-focus-lease-1",
            now=datetime(2026, 8, 7, 13, 0, tzinfo=timezone),
        )
        second = build_manual_focus_release_request(
            {}, ["常刷网站"], lease_id="manual-focus-lease-1",
            now=datetime(2026, 8, 7, 13, 10, tzinfo=timezone),
        )
        self.assertTrue(first["durable"])
        self.assertNotIn("expires_after_seconds", first)
        self.assertEqual(first["request_id"], second["request_id"])
        self.assertEqual(first["lease_id"], "manual-focus-lease-1")
        self.assertEqual(first["targets"][0]["lease_id"], "manual-focus-lease-1")

    def test_durable_release_stays_pending_after_normal_ttl_window(self):
        timezone = ZoneInfo("Asia/Shanghai")
        with tempfile.TemporaryDirectory() as directory:
            output_root = Path(directory)
            request = build_manual_focus_release_request(
                {}, ["常刷网站"], lease_id="manual-focus-lease-2",
                now=datetime(2026, 8, 7, 13, 0, tzinfo=timezone),
            )
            save_computer_intervention_request(output_root, request)
            pending = latest_pending_request(
                output_root, "windows-main", datetime(2026, 8, 7, 14, 0, tzinfo=timezone)
            )
            self.assertEqual(pending["request_id"], request["request_id"])

    def test_release_requires_lease_id(self):
        with self.assertRaisesRegex(ValueError, "lease_id"):
            build_manual_focus_release_request({}, ["常刷网站"])

    def test_legacy_unleased_release_is_archived_after_grace_window(self):
        timezone = ZoneInfo("Asia/Shanghai")
        with tempfile.TemporaryDirectory() as directory:
            output_root = Path(directory)
            request = {
                "request_id": "legacy-release-1",
                "created_at": "2026-08-07T12:00:00+08:00",
                "period": {
                    "start": "2026-08-07T12:00:00+08:00",
                    "end": "2026-08-07T12:00:00+08:00",
                },
                "mode": "release",
                "source": "manual_focus_pause",
                "targets": [{"name": "常刷网站"}],
            }
            request_path = save_computer_intervention_request(output_root, request)
            archived = archive_legacy_unleased_release_requests(
                output_root, now=datetime(2026, 8, 7, 12, 11, tzinfo=timezone)
            )
            self.assertEqual(len(archived), 1)
            self.assertFalse(request_path.exists())
            self.assertTrue(archived[0].exists())
            self.assertIsNone(
                latest_pending_request(
                    output_root, "windows-main", datetime(2026, 8, 7, 13, 0, tzinfo=timezone)
                )
            )

    def test_completed_release_is_archived_after_final_agent_event(self):
        timezone = ZoneInfo("Asia/Shanghai")
        with tempfile.TemporaryDirectory() as directory:
            output_root = Path(directory)
            request = build_manual_focus_release_request(
                {}, ["常刷网站"], lease_id="manual-focus-lease-archive",
                now=datetime(2026, 8, 7, 13, 0, tzinfo=timezone),
            )
            request_path = save_computer_intervention_request(output_root, request)
            receive_computer_intervention_event(
                output_root,
                {
                    "computer_id": "windows-main",
                    "request_id": request["request_id"],
                    "decision": "released",
                    "final": True,
                },
            )
            archived = list((output_root / "computer_interventions" / "archive" / "release" / "completed").glob("*/*.json"))
            self.assertFalse(request_path.exists())
            self.assertEqual(len(archived), 1)
            self.assertEqual(archived[0].name, request_path.name)


if __name__ == "__main__":
    unittest.main()
