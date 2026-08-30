import json
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path


SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))
from behavior_statistics import update_statistics


class StatisticsTests(unittest.TestCase):
    def test_daily_and_weekly_statistics(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report_dir = root / "ai_reports" / "2026-07-27"
            candidate_dir = root / "intervention_candidates" / "2026-07-27"
            report_dir.mkdir(parents=True)
            candidate_dir.mkdir(parents=True)
            report = {
                "estimated_time_allocation": {
                    key: {"estimate_minutes": value}
                    for key, value in {
                        "work": 20,
                        "entertainment": 5,
                        "brief_communication": 1,
                        "rest": 4,
                        "other": 0,
                        "uncertain": 0,
                    }.items()
                },
                "mixing_assessment": {
                    "entertainment_deviation_count": 1,
                    "entertainment_deviation_minutes": 2,
                },
            }
            (report_dir / "10-00.json").write_text(
                json.dumps(report), encoding="utf-8"
            )
            (candidate_dir / "10-00.json").write_text(
                json.dumps({"would_intervene": True}), encoding="utf-8"
            )
            paths = update_statistics(root, date(2026, 7, 27))
            daily = json.loads(paths["daily"].read_text(encoding="utf-8"))
            weekly = json.loads(paths["weekly"].read_text(encoding="utf-8"))
            self.assertEqual(daily["estimated_minutes"]["work"], 20)
            self.assertEqual(daily["shadow_candidates"]["push_count"], 0)
            self.assertEqual(weekly["report_count"], 1)


if __name__ == "__main__":
    unittest.main()
