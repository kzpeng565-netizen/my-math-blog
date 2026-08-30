import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path


SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

from issue_feedback import receive_issue_feedback, recent_issues


class IssueFeedbackTests(unittest.TestCase):
    def test_receive_issue_feedback_writes_raw_daily_and_unreviewed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = receive_issue_feedback(
                {
                    "category": "ai_suggestion_quality",
                    "severity": "high",
                    "message": "它把一个番茄钟理解成25分钟。",
                    "page": "next_action",
                    "suggestion_id": "s1",
                },
                output_root=root,
                user_agent="UnitTest",
                now=datetime.fromisoformat("2026-07-30T10:30:00+08:00"),
            )
            self.assertEqual(result["status"], "open")
            self.assertTrue(Path(result["raw_path"]).exists())
            daily = root / "issue_feedback" / "daily" / "2026-07-30.md"
            unreviewed = root / "issue_feedback" / "UNREVIEWED.md"
            self.assertIn("AI建议质量", daily.read_text(encoding="utf-8"))
            self.assertIn("s1", unreviewed.read_text(encoding="utf-8"))
            self.assertEqual(len(recent_issues(root)), 1)

    def test_requires_message_and_normalizes_unknown_values(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaisesRegex(ValueError, "message is required"):
                receive_issue_feedback({}, output_root=root)
            result = receive_issue_feedback(
                {"category": "bad", "severity": "bad", "message": "x"},
                output_root=root,
                now=datetime.fromisoformat("2026-07-30T10:30:00+08:00"),
            )
            self.assertEqual(result["category"], "other")
            self.assertEqual(result["severity"], "medium")


if __name__ == "__main__":
    unittest.main()
