import json
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch


SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

from daily_life_notifier import notify_daily_life, target_date
from notifications import NotificationResult


class FakeNotifier:
    def send(self, *, title, message, priority="default", tags=None):
        self.title = title
        self.message = message
        self.priority = priority
        self.tags = list(tags or [])
        return NotificationResult(
            status="accepted",
            provider="ntfy",
            title=title,
            priority=priority,
            attempt_count=1,
            message_id="abc",
        )


class DailyLifeNotifierTests(unittest.TestCase):
    def test_target_date_is_yesterday(self):
        self.assertEqual(
            str(target_date(datetime.fromisoformat("2026-07-29T09:00:00+08:00"))),
            "2026-07-28",
        )

    def test_notify_generates_sends_and_writes_receipt(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            markdown = root / "statistics" / "daily_life" / "2026-07-28.md"
            report_json = root / "statistics" / "daily_life" / "2026-07-28.json"
            markdown.parent.mkdir(parents=True)
            markdown.write_text("# 每日行为复盘：2026-07-28\n\n正文", encoding="utf-8")
            report_json.write_text(
                json.dumps({"ai_advice": {"status": "轻微提醒"}}, ensure_ascii=False),
                encoding="utf-8",
            )
            fake = FakeNotifier()

            with patch(
                "daily_life_notifier.run",
                return_value={
                    "status": "completed",
                    "date": "2026-07-28",
                    "json": str(report_json),
                    "markdown": str(markdown),
                    "ai_advice": True,
                    "ai_error": None,
                },
            ):
                receipt = notify_daily_life(
                    day=datetime.fromisoformat("2026-07-28T00:00:00+08:00").date(),
                    output_root=root,
                    settings=Path("settings.json"),
                    prompt=Path("prompt.md"),
                    env_file=Path("env"),
                    notifier=fake,
                    now=datetime.fromisoformat("2026-07-29T09:00:00+08:00"),
                )

            self.assertEqual(receipt["status"], "accepted")
            self.assertIn("轻微提醒", fake.title)
            self.assertIn("每日行为复盘", fake.message)
            receipt_path = root / "statistics" / "ntfy_receipts" / "daily_life" / "2026-07-28.json"
            self.assertTrue(receipt_path.exists())


if __name__ == "__main__":
    unittest.main()
