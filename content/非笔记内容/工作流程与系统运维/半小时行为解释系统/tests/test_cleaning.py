import sys
import unittest
from datetime import datetime
from pathlib import Path


SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

from common import clean_title, domain_from_url, merge_timeline
from computer_facts import _compact_timeline
from cross_device import _confirmed_rest_intervals
from deepseek_client import _validate_report
from pushplus_client import build_wechat_message
from semantic_analysis import calculate_work_entertainment_mixing


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
                "entertainment": {"estimate_minutes": 1},
                "brief_communication": {"estimate_minutes": 0.2},
                "rest": {"estimate_minutes": 3},
                "other": {"estimate_minutes": 0.8},
                "uncertain": {"estimate_minutes": 0},
            },
            "mixing_assessment": {
                "level": "low",
                "entertainment_deviation_count": 1,
                "entertainment_deviation_minutes": 1,
                "longest_entertainment_deviation_minutes": 1,
                "brief_communication_minutes": 0.2,
                "same_task_tool_switches_not_scored": 3,
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
        self.assertIn("娱乐 1 分钟", content)
        self.assertIn("娱乐偏离 1 次", content)
        self.assertIn("同任务工具切换 3 次", content)
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
                "entertainment": {
                    "estimate_minutes": 0,
                    "range_minutes": [0, 0],
                },
                "brief_communication": {
                    "estimate_minutes": 0,
                    "range_minutes": [0, 0],
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

    def test_rest_requires_three_minutes_of_cross_device_inactivity(self):
        computer_afk = [(0, 120), (300, 600)]
        phone_off = [(0, 600)]
        confirmed = _confirmed_rest_intervals(computer_afk, phone_off, 180)
        self.assertEqual(confirmed, [(300, 600)])

    def test_rest_validation_uses_confirmed_rest_minutes(self):
        report = {
            "state_assessment": {"label": "focused_work"},
            "estimated_time_allocation": {
                "work": {
                    "estimate_minutes": 26.72,
                    "range_minutes": [26, 27],
                },
                "entertainment": {
                    "estimate_minutes": 0,
                    "range_minutes": [0, 0],
                },
                "brief_communication": {
                    "estimate_minutes": 0,
                    "range_minutes": [0, 0],
                },
                "rest": {
                    "estimate_minutes": 3.28,
                    "range_minutes": [3, 4],
                },
                "other": {
                    "estimate_minutes": 0,
                    "range_minutes": [0, 0],
                },
                "uncertain": {
                    "estimate_minutes": 0,
                    "range_minutes": [0, 0],
                },
            },
            "timeline_summary": [
                {"likely_state": "工作", "minutes": 26.72},
                {"likely_state": "休息", "minutes": 3.28},
            ],
        }
        errors = _validate_report(report, 30, confirmed_rest_minutes=0)
        self.assertTrue(any("confirmed_rest_minutes" in error for error in errors))

    def test_entertainment_over_thirty_seconds_inside_work_is_deviation(self):
        semantic = {
            "segments": [
                {
                    "start": "2026-07-24T20:00:00+08:00",
                    "end": "2026-07-24T20:10:00+08:00",
                    "duration_seconds": 600,
                    "activity": "work",
                },
                {
                    "start": "2026-07-24T20:10:00+08:00",
                    "end": "2026-07-24T20:10:31+08:00",
                    "duration_seconds": 31,
                    "activity": "entertainment",
                    "relationship_to_work": "entertainment_detour",
                    "task": "浏览知乎",
                    "evidence": ["zhihu.com"],
                    "confidence": "high",
                },
                {
                    "start": "2026-07-24T20:10:31+08:00",
                    "end": "2026-07-24T20:30:00+08:00",
                    "duration_seconds": 1169,
                    "activity": "work",
                },
            ]
        }
        cross = {
            "computer_fragmentation_metrics": {
                "context_switch_count": 8,
                "context_blocks": [],
            }
        }
        settings = {
            "timezone": "Asia/Shanghai",
            "state_rules": {
                "entertainment_deviation_minimum_seconds": 30
            },
        }
        result = calculate_work_entertainment_mixing(
            semantic, cross, settings
        )
        self.assertEqual(result["entertainment_deviation_count"], 1)
        self.assertEqual(result["level"], "low")

    def test_exactly_thirty_seconds_is_not_deviation(self):
        semantic = {
            "segments": [
                {
                    "start": "2026-07-24T20:00:00+08:00",
                    "end": "2026-07-24T20:10:00+08:00",
                    "duration_seconds": 600,
                    "activity": "work",
                },
                {
                    "start": "2026-07-24T20:10:00+08:00",
                    "end": "2026-07-24T20:10:30+08:00",
                    "duration_seconds": 30,
                    "activity": "entertainment",
                    "relationship_to_work": "entertainment_detour",
                },
                {
                    "start": "2026-07-24T20:10:30+08:00",
                    "end": "2026-07-24T20:30:00+08:00",
                    "duration_seconds": 1170,
                    "activity": "work",
                },
            ]
        }
        result = calculate_work_entertainment_mixing(
            semantic,
            {
                "computer_fragmentation_metrics": {
                    "context_switch_count": 2,
                    "context_blocks": [],
                }
            },
            {
                "timezone": "Asia/Shanghai",
                "state_rules": {
                    "entertainment_deviation_minimum_seconds": 30
                },
            },
        )
        self.assertEqual(result["entertainment_deviation_count"], 0)
        self.assertEqual(result["level"], "none")

    def test_brief_message_does_not_break_work_or_count_as_deviation(self):
        semantic = {
            "segments": [
                {
                    "start": "2026-07-24T20:00:00+08:00",
                    "end": "2026-07-24T20:10:00+08:00",
                    "duration_seconds": 600,
                    "activity": "work",
                },
                {
                    "start": "2026-07-24T20:10:00+08:00",
                    "end": "2026-07-24T20:10:10+08:00",
                    "duration_seconds": 10,
                    "activity": "brief_communication",
                },
                {
                    "start": "2026-07-24T20:10:10+08:00",
                    "end": "2026-07-24T20:30:00+08:00",
                    "duration_seconds": 1190,
                    "activity": "work",
                },
            ]
        }
        result = calculate_work_entertainment_mixing(
            semantic,
            {
                "computer_fragmentation_metrics": {
                    "context_switch_count": 5,
                    "context_blocks": [],
                }
            },
            {
                "timezone": "Asia/Shanghai",
                "state_rules": {
                    "entertainment_deviation_minimum_seconds": 30
                },
            },
        )
        self.assertEqual(result["entertainment_deviation_count"], 0)
        self.assertEqual(result["brief_communication_minutes"], 0.17)
        self.assertEqual(result["longest_continuous_work_minutes"], 30.0)
        self.assertEqual(result["level"], "none")


if __name__ == "__main__":
    unittest.main()
