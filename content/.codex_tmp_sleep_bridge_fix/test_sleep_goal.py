import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from focus_garden.sleep_goal import build_sleep_goal_summary


class SleepGoalTests(unittest.TestCase):
    def make_summary(self, root: Path, day: str, last_use: str | None, status: str = "resolved") -> None:
        target = root / "statistics" / "daily_life" / f"{day}.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps({"phone_sleep_boundary": {
            "last_phone_use_at_night": last_use,
            "status": status,
            "quality": "high",
        }}), encoding="utf-8")

    def test_current_week_counts_strict_and_flexible_days(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for day, value in {
                "2026-09-01": "00:20", "2026-09-02": "00:30",
                "2026-09-03": "00:40", "2026-09-04": "00:55",
                "2026-09-05": "00:25", "2026-09-06": "00:29",
                "2026-09-07": "01:00",
            }.items():
                self.make_summary(root, day, value)
            result = build_sleep_goal_summary(
                {"sleep_goal": {"start_date": "2026-09-01", "end_date": "2027-01-17"}},
                root,
                datetime(2026, 9, 7, 10, tzinfo=ZoneInfo("Asia/Shanghai")),
            )
            self.assertEqual(result["week"]["strict_days"], 5)
            self.assertEqual(result["week"]["on_time_days"], 7)
            self.assertEqual(result["week"]["status"], "met")

    def test_late_boundary_is_not_on_time_and_missing_is_unknown(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            self.make_summary(root, "2026-09-01", "01:01")
            self.make_summary(root, "2026-09-02", None, status="possible_fault")
            result = build_sleep_goal_summary(
                {"sleep_goal": {"start_date": "2026-09-01", "end_date": "2027-01-17"}},
                root,
                datetime(2026, 9, 2, 12, tzinfo=ZoneInfo("Asia/Shanghai")),
            )
            statuses = {item["date"]: item["status"] for item in result["week"]["records"]}
            self.assertEqual(statuses["2026-09-01"], "late")
            self.assertEqual(statuses["2026-09-02"], "unknown")


if __name__ == "__main__":
    unittest.main()
