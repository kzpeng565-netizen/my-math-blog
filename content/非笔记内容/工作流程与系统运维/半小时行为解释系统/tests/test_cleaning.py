import sys
import unittest
from datetime import datetime
from pathlib import Path


SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

from common import clean_title, domain_from_url, merge_timeline
from computer_facts import _compact_timeline
from deepseek_client import _validate_report
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
            "concise_report": "集中工作，工作估计25分钟。",
            "verification_question": "这段理解是否正确？",
            "state_assessment": {"label": "focused_work"},
            "estimated_time_allocation": {
                "work": {"estimate_minutes": 25},
                "rest": {"estimate_minutes": 3},
                "uncertain": {"estimate_minutes": 2},
            },
            "fragmentation_assessment": {
                "level": "low",
                "context_switch_count": 3,
                "longest_context_minutes": 12,
            },
            "data_quality": {
                "level": "medium",
                "material_issues": [],
            },
        }
        start = datetime.fromisoformat("2026-07-24T20:00:00+08:00")
        end = datetime.fromisoformat("2026-07-24T20:30:00+08:00")
        title, content = build_wechat_message(report, start, end)
        self.assertEqual(title, "行为核验 20:00—20:30")
        self.assertIn("工作估计25分钟", content)
        self.assertIn("工作 25 分钟", content)
        self.assertIn("切换 3 次", content)
        self.assertIn("这段理解是否正确", content)
        self.assertIn("不会触发屏蔽", content)
        self.assertIn("在 Codex 中反馈", content)

    def test_semantically_identical_browser_segments_merge(self):
        items = [
            {
                "start": "2026-07-24T20:45:00+08:00",
                "end": "2026-07-24T20:46:00+08:00",
                "duration_seconds": 60,
                "app": "msedge.exe",
                "app_display": "Microsoft Edge",
                "title": "初高衔接数学",
                "domain": "bilibili.com",
                "context_source": "web",
            },
            {
                "start": "2026-07-24T20:46:00+08:00",
                "end": "2026-07-24T20:46:00+08:00",
                "duration_seconds": 0.001,
                "app": "msedge.exe",
                "app_display": "Microsoft Edge",
                "title": "初高衔接数学",
                "domain": "",
                "context_source": "window",
            },
            {
                "start": "2026-07-24T20:46:00+08:00",
                "end": "2026-07-24T20:49:00+08:00",
                "duration_seconds": 180,
                "app": "msedge.exe",
                "app_display": "Microsoft Edge",
                "title": "初高衔接数学",
                "domain": "",
                "context_source": "window",
            },
        ]
        compact = _compact_timeline(items, 3)
        self.assertEqual(len(compact), 1)
        self.assertEqual(compact[0]["duration_seconds"], 240)
        self.assertEqual(compact[0]["domain"], "bilibili.com")
        self.assertNotIn("0.001", str(compact))

    def test_report_validation_rejects_inconsistent_timeline(self):
        report = {
            "state_assessment": {"label": "focused_work"},
            "estimated_time_allocation": {
                "work": {
                    "estimate_minutes": 25,
                    "range_minutes": [20, 28],
                },
                "rest": {
                    "estimate_minutes": 3,
                    "range_minutes": [2, 5],
                },
                "other": {
                    "estimate_minutes": 2,
                    "range_minutes": [0, 3],
                },
                "uncertain": {
                    "estimate_minutes": 0,
                    "range_minutes": [0, 1],
                },
            },
            "timeline_summary": [
                {
                    "likely_state": "工作",
                    "minutes": 27,
                },
                {
                    "likely_state": "休息",
                    "minutes": 3,
                },
            ],
        }
        errors = _validate_report(report, 30)
        self.assertTrue(any("work" in error for error in errors))
        self.assertTrue(any("other" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
