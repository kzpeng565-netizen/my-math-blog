import json
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path


SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

from statistics_notifier import notify, resolve_period


class StatisticsNotifierTests(unittest.TestCase):
    def test_daily_targets_yesterday(self):
        days, period = resolve_period(
            "daily", datetime.fromisoformat("2026-07-28T00:18:00+08:00")
        )
        self.assertEqual(period, "2026-07-27")
        self.assertEqual([str(day) for day in days], ["2026-07-27"])

    def test_weekly_targets_previous_iso_week(self):
        days, period = resolve_period(
            "weekly", datetime.fromisoformat("2026-07-27T00:23:00+08:00")
        )
        self.assertEqual(period, "2026-W30")
        self.assertEqual(str(days[0]), "2026-07-20")
        self.assertEqual(str(days[-1]), "2026-07-26")

    def test_no_push_writes_statistics_and_receipt(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = notify(
                "daily",
                root,
                datetime.fromisoformat("2026-07-28T00:18:00+08:00"),
                no_push=True,
            )
            self.assertEqual(result["status"], "skipped")
            statistics = root / "statistics" / "daily" / "2026-07-27.json"
            receipt = (
                root
                / "statistics"
                / "pushplus_receipts"
                / "daily"
                / "2026-07-27.json"
            )
            self.assertTrue(statistics.exists())
            self.assertEqual(
                json.loads(receipt.read_text(encoding="utf-8"))["kind"],
                "daily",
            )


if __name__ == "__main__":
    unittest.main()
