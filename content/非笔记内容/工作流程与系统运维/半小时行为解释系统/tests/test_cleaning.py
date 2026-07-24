import sys
import unittest
from pathlib import Path


SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

from common import clean_title, domain_from_url, merge_timeline


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


if __name__ == "__main__":
    unittest.main()
