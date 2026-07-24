import sys
import unittest
from datetime import datetime
from pathlib import Path


SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

from common import clean_title, domain_from_url, merge_timeline
from pushplus_client import build_wechat_message


class CleaningTests(unittest.TestCase):
    def test_edge_title_cleanup(self):
        raw = "(45 封私信 / 5 条消息) Haar 测度证明 和另外 7 个页面 - 个人 - Microsoft Edge"
        self.assertEqual(clean_title(raw), "Haar 测度证明")

    def test_sensitive_values_are_redacted(self):
        raw = "联系 13800138000 或 user@example.com"
        cleaned = clean_title(raw)
        self.assertNotIn("13800138000", cleaned)
        self.assertNotIn("user@example.com", cleaned)

    def test_domain_cleanup(self):
        self.assertEqual(
            domain_from_url("https://www.zhihu.com/question/1?utm_source=x"),
            "zhihu.com",
        )

    def test_adjacent_timeline_items_merge(self):
        items = [
            {
                "start": "2026-07-24T10:00:00+08:00",
                "end": "2026-07-24T10:01:00+08:00",
                "duration_seconds": 60,
                "state": "on",
            },
            {
                "start": "2026-07-24T10:01:00+08:00",
                "end": "2026-07-24T10:02:00+08:00",
                "duration_seconds": 60,
                "state": "on",
            },
        ]
        merged = merge_timeline(items, ("state",))
        self.assertEqual(len(merged), 1)
        self.assertEqual(merged[0]["duration_seconds"], 120)

    def test_wechat_message_contains_verification_fields(self):
        report = {
            "concise_report": "电脑主要用于阅读数学资料。",
            "verification_question": "这段理解是否正确？",
            "data_quality_assessment": {
                "level": "medium",
                "issues": ["浏览器标题覆盖不足。"],
            },
        }
        start = datetime.fromisoformat("2026-07-24T20:00:00+08:00")
        end = datetime.fromisoformat("2026-07-24T20:30:00+08:00")
        title, content = build_wechat_message(report, start, end)
        self.assertEqual(title, "行为核验 20:00—20:30")
        self.assertIn("电脑主要用于阅读数学资料", content)
        self.assertIn("这段理解是否正确", content)
        self.assertIn("不会触发屏蔽", content)
        self.assertIn("在 Codex 中反馈", content)


if __name__ == "__main__":
    unittest.main()
