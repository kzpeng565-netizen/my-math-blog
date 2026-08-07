import sys
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo


SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

from computer_intervention import (
    build_computer_intervention_request,
    build_manual_focus_release_request,
    latest_pending_request,
    receive_computer_intervention_event,
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


if __name__ == "__main__":
    unittest.main()
