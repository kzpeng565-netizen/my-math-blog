import json
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path


SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

from daily_life_statistics import build_daily_life_summary, render_markdown


class DailyLifeStatisticsTests(unittest.TestCase):
    def test_daily_life_summary_builds_requested_metrics(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            day = date(2026, 7, 28)
            for name in (
                "ai_reports",
                "semantic_timelines",
                "computer_facts",
                "phone_facts",
            ):
                (root / name / "2026-07-28").mkdir(parents=True)
            (root / "phone_facts" / "2026-07-29").mkdir(parents=True)

            report = {
                "estimated_time_allocation": {
                    "work": {"estimate_minutes": 120},
                    "entertainment": {"estimate_minutes": 45},
                    "shopping": {"estimate_minutes": 12},
                    "brief_communication": {"estimate_minutes": 15},
                    "rest": {"estimate_minutes": 30},
                    "other": {"estimate_minutes": 0},
                    "uncertain": {"estimate_minutes": 5},
                },
                "mixing_assessment": {
                    "entertainment_deviation_count": 3,
                    "entertainment_deviation_minutes": 22,
                },
            }
            (root / "ai_reports" / "2026-07-28" / "10-00.json").write_text(
                json.dumps(report), encoding="utf-8"
            )

            semantic = {
                "segments": [
                    {
                        "start": "2026-07-28T10:00:00+08:00",
                        "end": "2026-07-28T12:00:00+08:00",
                        "duration_seconds": 7200,
                        "activity": "work",
                        "work_category": "数学学习",
                        "task": "学习GTM259",
                        "evidence": ["ChatGPT《GTM259》"],
                        "confidence": "high",
                    },
                    {
                        "start": "2026-07-28T12:00:00+08:00",
                        "end": "2026-07-28T12:45:00+08:00",
                        "duration_seconds": 2700,
                        "activity": "entertainment",
                        "task": "浏览知乎",
                        "evidence": ["Edge《首页 - 知乎》"],
                        "confidence": "high",
                    },
                    {
                        "start": "2026-07-28T13:00:00+08:00",
                        "end": "2026-07-28T13:20:00+08:00",
                        "duration_seconds": 1200,
                        "activity": "brief_communication",
                        "task": "微信通信",
                        "evidence": ["微信"],
                        "confidence": "high",
                    },
                ]
            }
            (root / "semantic_timelines" / "2026-07-28" / "10-00.json").write_text(
                json.dumps(semantic), encoding="utf-8"
            )

            computer = {
                "timeline": [
                    {
                        "start": "2026-07-28T10:00:00+08:00",
                        "end": "2026-07-28T11:40:00+08:00",
                        "app_display": "ChatGPT",
                        "domain": "chatgpt.com",
                    },
                    {
                        "start": "2026-07-28T12:00:00+08:00",
                        "end": "2026-07-28T12:20:00+08:00",
                        "app_display": "ChatGPT",
                        "domain": "chatgpt.com",
                    },
                    {
                        "start": "2026-07-28T13:00:00+08:00",
                        "end": "2026-07-28T13:10:00+08:00",
                        "app_display": "DeepSeek",
                        "domain": "chat.deepseek.com",
                    }
                ]
            }
            (root / "computer_facts" / "2026-07-28" / "10-00.json").write_text(
                json.dumps(computer), encoding="utf-8"
            )

            phone_evening = {
                "screen_timeline": [
                    {
                        "start": "2026-07-28T23:00:00+08:00",
                        "end": "2026-07-28T23:30:00+08:00",
                        "state": "on",
                    }
                ]
            }
            phone_morning = {
                "screen_timeline": [
                    {
                        "start": "2026-07-29T07:00:00+08:00",
                        "end": "2026-07-29T07:10:00+08:00",
                        "state": "on",
                    }
                ]
            }
            (root / "phone_facts" / "2026-07-28" / "23-00.json").write_text(
                json.dumps(phone_evening), encoding="utf-8"
            )
            (root / "phone_facts" / "2026-07-29" / "07-00.json").write_text(
                json.dumps(phone_morning), encoding="utf-8"
            )

            context = {
                "profile_markdown": "当前目标是数学学习。",
                "tasks": {
                    "today": [
                        {
                            "title": "完成GTM259 §2.1",
                            "priority": "high",
                            "scheduled_date": "2026-07-29",
                        }
                    ],
                    "near_term": [],
                    "overdue": [],
                },
                "pomodoro": {"reference_only": True},
            }
            summary = build_daily_life_summary(root, day, context)
            self.assertEqual(summary["daily_totals"]["work_minutes"], 120)
            self.assertEqual(summary["daily_totals"]["entertainment_minutes"], 45)
            self.assertEqual(summary["daily_totals"]["shopping_minutes"], 12)
            self.assertEqual(summary["entertainment_breakdown"]["top_tasks"][0]["name"], "浏览知乎")
            self.assertEqual(summary["ai_usage"]["total_minutes"], 130)
            self.assertEqual(summary["ai_usage"]["by_activity"]["entertainment"], 20)
            self.assertEqual(summary["ai_usage"]["by_activity"]["brief_communication"], 10)
            self.assertEqual(summary["ai_usage"]["top_tasks"][0]["name"], "学习GTM259")
            self.assertEqual(
                summary["phone_sleep_boundary"]["last_phone_use_at_night"], "23:30"
            )
            self.assertEqual(
                summary["phone_sleep_boundary"]["first_phone_use_in_morning"], "07:00"
            )
            self.assertEqual(
                summary["phone_sleep_boundary"]["sleep_estimate_minutes_minus_20"], 430
            )
            self.assertEqual(summary["phone_sleep_boundary"]["status"], "resolved")
            self.assertTrue(summary["long_blocks"])
            self.assertTrue(summary["efficiency_flags"])
            markdown = render_markdown(summary)
            self.assertIn("总工作", markdown)
            self.assertIn("手机睡眠边界", markdown)
            self.assertIn("娱乐项目 Top 3", markdown)
            self.assertIn("AI用途 Top 3", markdown)
            self.assertNotIn("\n# ", markdown)
            self.assertNotIn("\n## ", markdown)
            self.assertNotIn("\n- ", markdown)
            self.assertNotIn("\n> ", markdown)

    def test_sleep_boundary_does_not_invent_morning_pickup(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            day = date(2026, 7, 28)
            (root / "phone_facts" / "2026-07-28").mkdir(parents=True)
            phone_evening = {
                "screen_timeline": [
                    {
                        "start": "2026-07-28T23:00:00+08:00",
                        "end": "2026-07-28T23:30:00+08:00",
                        "state": "on",
                    }
                ]
            }
            (root / "phone_facts" / "2026-07-28" / "23-00.json").write_text(
                json.dumps(phone_evening), encoding="utf-8"
            )

            summary = build_daily_life_summary(root, day, None)
            sleep = summary["phone_sleep_boundary"]
            self.assertEqual(sleep["last_phone_use_at_night"], "23:30")
            self.assertIsNone(sleep["first_phone_use_in_morning"])
            self.assertIsNone(sleep["sleep_estimate_minutes_minus_20"])
            self.assertEqual(sleep["quality"], "low")
            self.assertEqual(sleep["status"], "pending")

    def test_sleep_boundary_marks_possible_fault_at_11(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            day = date(2026, 7, 28)
            (root / "phone_facts" / "2026-07-28").mkdir(parents=True)
            phone_evening = {
                "screen_timeline": [
                    {
                        "start": "2026-07-28T23:00:00+08:00",
                        "end": "2026-07-28T23:30:00+08:00",
                        "state": "on",
                    }
                ]
            }
            (root / "phone_facts" / "2026-07-28" / "23-00.json").write_text(
                json.dumps(phone_evening), encoding="utf-8"
            )

            summary = build_daily_life_summary(root, day, None, morning_cutoff_hour=11)
            sleep = summary["phone_sleep_boundary"]
            self.assertEqual(sleep["status"], "possible_fault")
            self.assertEqual(sleep["morning_cutoff_hour"], 11)


if __name__ == "__main__":
    unittest.main()
