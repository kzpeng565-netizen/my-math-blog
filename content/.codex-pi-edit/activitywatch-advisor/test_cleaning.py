import sys
import unittest
import json
from datetime import datetime
from pathlib import Path
from unittest.mock import patch


SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

from common import clean_title, domain_from_url, merge_timeline
from computer_facts import _compact_timeline
from cross_device import _confirmed_rest_intervals
from deepseek_client import _aggregate_usage, _validate_report
from fact_tagger import (
    build_tagged_fact_view,
    compact_fact_view_for_ai,
    load_tag_rules,
)
from phone_facts import _screen_state_at as _phone_screen_state_at
from pushplus_client import build_statistics_message, build_wechat_message
import semantic_analysis
from semantic_analysis import (
    extract_semantic_timeline_with_deepseek,
    _segments_from_ai_groups,
    calculate_work_entertainment_mixing,
)
from run_half_hour import _should_skip_push_for_inactive_devices
from tablet_facts import _screen_state_at


class CleaningTests(unittest.TestCase):
    @staticmethod
    def _tagged_fact_fixture():
        period = {
            "start": "2026-07-28T19:55:00+08:00",
            "end": "2026-07-28T20:35:00+08:00",
        }
        computer = {
            "period": period,
            "status_timeline": [
                {
                    "start": period["start"],
                    "end": period["end"],
                    "duration_seconds": 2400,
                    "status": "not-afk",
                }
            ],
            "timeline": [
                {
                    "start": period["start"],
                    "end": "2026-07-28T20:10:00+08:00",
                    "app": "ChatGPT.exe",
                    "app_display": "ChatGPT",
                    "title": "Pi Server",
                    "domain": "",
                },
                {
                    "start": "2026-07-28T20:10:00+08:00",
                    "end": "2026-07-28T20:11:05+08:00",
                    "app": "msedge.exe",
                    "app_display": "Microsoft Edge",
                    "title": "首页 - 知乎",
                    "domain": "zhihu.com",
                },
                {
                    "start": "2026-07-28T20:11:05+08:00",
                    "end": "2026-07-28T20:20:00+08:00",
                    "app": "ChatGPT.exe",
                    "app_display": "ChatGPT",
                    "title": "Pi Server",
                    "domain": "",
                },
                {
                    "start": "2026-07-28T20:20:00+08:00",
                    "end": "2026-07-28T20:21:00+08:00",
                    "app": "Weixin.exe",
                    "app_display": "微信",
                    "title": "微信",
                    "domain": "",
                },
                {
                    "start": "2026-07-28T20:21:00+08:00",
                    "end": period["end"],
                    "app": "ChatGPT.exe",
                    "app_display": "ChatGPT",
                    "title": "Pi Server",
                    "domain": "",
                },
            ],
            "quality": {"level": "high", "material_issues": []},
        }
        mobile = {
            "period": period,
            "screen_timeline": [
                {
                    "start": period["start"],
                    "end": period["end"],
                    "duration_seconds": 2400,
                    "state": "off",
                }
            ],
            "timeline": [],
            "quality": {"level": "high", "material_issues": []},
        }
        cross = {
            "rest_rule": {
                "confirmed_rest_intervals": [
                    {
                        "start": "2026-07-28T20:25:00+08:00",
                        "end": "2026-07-28T20:28:00+08:00",
                    }
                ]
            }
        }
        rules = Path(__file__).resolve().parents[1] / "config" / "tag_rules.json"
        return build_tagged_fact_view(
            {"timezone": "Asia/Shanghai"},
            rules,
            datetime.fromisoformat("2026-07-28T20:00:00+08:00"),
            datetime.fromisoformat("2026-07-28T20:30:00+08:00"),
            computer,
            mobile,
            mobile,
            cross,
        )

    @staticmethod
    def _single_computer_tagged_fact(title, domain, app="Microsoft Edge"):
        period = {
            "start": "2026-07-28T19:55:00+08:00",
            "end": "2026-07-28T20:35:00+08:00",
        }
        process = "msedge.exe" if app == "Microsoft Edge" else f"{app}.exe"
        computer = {
            "period": period,
            "status_timeline": [
                {
                    "start": period["start"],
                    "end": period["end"],
                    "duration_seconds": 2400,
                    "status": "not-afk",
                }
            ],
            "timeline": [
                {
                    "start": period["start"],
                    "end": period["end"],
                    "app": process,
                    "app_display": app,
                    "title": title,
                    "domain": domain,
                }
            ],
            "quality": {"level": "high", "material_issues": []},
        }
        mobile = {
            "period": period,
            "screen_timeline": [
                {
                    "start": period["start"],
                    "end": period["end"],
                    "duration_seconds": 2400,
                    "state": "off",
                }
            ],
            "timeline": [],
            "quality": {"level": "high", "material_issues": []},
        }
        rules = Path(__file__).resolve().parents[1] / "config" / "tag_rules.json"
        return build_tagged_fact_view(
            {"timezone": "Asia/Shanghai"},
            rules,
            datetime.fromisoformat("2026-07-28T20:00:00+08:00"),
            datetime.fromisoformat("2026-07-28T20:30:00+08:00"),
            computer,
            mobile,
            mobile,
            {"rest_rule": {"confirmed_rest_intervals": []}},
        )

    def test_tag_rules_configuration_is_valid(self):
        rules = Path(__file__).resolve().parents[1] / "config" / "tag_rules.json"
        loaded = load_tag_rules(rules)
        self.assertTrue(loaded["_rule_version"].startswith("sha256:"))

    def test_api_usage_aggregates_retries_and_cost(self):
        result = _aggregate_usage(
            [
                {
                    "usage": {
                        "prompt_tokens": 100,
                        "completion_tokens": 20,
                        "total_tokens": 120,
                        "prompt_cache_hit_tokens": 40,
                        "prompt_cache_miss_tokens": 60,
                    }
                },
                {
                    "usage": {
                        "prompt_tokens": 50,
                        "completion_tokens": 10,
                        "total_tokens": 60,
                        "prompt_cache_hit_tokens": 10,
                        "prompt_cache_miss_tokens": 40,
                    }
                },
            ],
            {
                "pricing_cny_per_million": {
                    "input_cache_hit": 0.02,
                    "input_cache_miss": 1,
                    "output": 2,
                }
            },
        )
        self.assertEqual(result["prompt_tokens"], 150)
        self.assertEqual(result["completion_tokens"], 30)
        self.assertEqual(result["prompt_cache_miss_tokens"], 100)
        self.assertGreater(result["estimated_cost_cny"], 0)

    def test_tagged_fact_view_contains_one_unified_forty_minute_window(self):
        tagged = self._tagged_fact_fixture()
        total = sum(float(block["duration_seconds"]) for block in tagged["blocks"])
        report_total = sum(
            float(block["duration_seconds"])
            for block in tagged["blocks"]
            if block["scope"] == "report"
        )
        self.assertEqual(total, 2400)
        self.assertEqual(report_total, 1800)
        zhihu = next(
            block
            for block in tagged["blocks"]
            if block.get("computer", {}).get("domain") == "zhihu.com"
        )
        self.assertTrue(zhihu["force_boundary"])
        self.assertIn(
            "content_feed", {tag["name"] for tag in zhihu["tags"]}
        )
        self.assertIn(
            "entertainment_app", {tag["name"] for tag in zhihu["tags"]}
        )
        self.assertEqual(zhihu["locked_activity"], "entertainment")
        wechat = next(
            block
            for block in tagged["blocks"]
            if block.get("computer", {}).get("app") == "微信"
        )
        self.assertEqual(wechat["locked_activity"], "brief_communication")
        rest = [
            block
            for block in tagged["blocks"]
            if block.get("locked_activity") == "rest"
        ]
        self.assertEqual(
            sum(float(block["duration_seconds"]) for block in rest), 180
        )

    def test_compact_ai_view_exposes_only_unlocked_report_ids(self):
        tagged = self._tagged_fact_fixture()
        compact = compact_fact_view_for_ai(tagged)
        candidate_ids = {
            block["id"] for block in compact["report_candidates"]
        }
        candidate_source_ids = {
            source_id
            for source_ids in compact["_candidate_map"].values()
            for source_id in source_ids
        }
        locked_ids = {
            block["id"]
            for block in tagged["blocks"]
            if block.get("scope") == "report"
            and block.get("locked_activity")
        }
        self.assertTrue(compact["locked_markers"])
        self.assertTrue(compact["context_blocks"])
        self.assertFalse(candidate_ids & locked_ids)
        self.assertFalse(candidate_source_ids & locked_ids)
        self.assertEqual(
            candidate_source_ids,
            {
                block["id"]
                for block in tagged["blocks"]
                if block.get("scope") == "report"
                and not block.get("locked_activity")
            },
        )
        self.assertTrue(
            all("id" not in marker for marker in compact["locked_markers"])
        )

    def test_ai_cannot_swallow_forced_boundary_or_locked_blocks(self):
        tagged = self._tagged_fact_fixture()
        report_blocks = [
            block for block in tagged["blocks"] if block["scope"] == "report"
        ]
        zhihu_index = next(
            index
            for index, block in enumerate(report_blocks)
            if block.get("computer", {}).get("domain") == "zhihu.com"
        )
        swallowed = [
            report_blocks[zhihu_index - 1]["id"],
            report_blocks[zhihu_index]["id"],
        ]
        result = {
            "groups": [
                {
                    "block_ids": swallowed,
                    "activity": "work",
                    "work_category": "系统维护",
                    "task": "维护服务器",
                    "relationship_to_work": "same_work_task",
                    "evidence_ids": swallowed[:1],
                    "confidence": "high",
                }
            ]
        }
        segments, issues = _segments_from_ai_groups(result, tagged)
        self.assertTrue(
            any("锁定" in issue or "必须单独判断" in issue for issue in issues)
        )
        self.assertEqual(
            sum(float(segment["duration_seconds"]) for segment in segments),
            1800,
        )
        self.assertTrue(
            any(
                segment["activity"] == "brief_communication"
                and segment["locked_by_program"]
                for segment in segments
            )
        )
        self.assertTrue(
            any(
                segment["activity"] == "rest"
                and segment["locked_by_program"]
                for segment in segments
            )
        )

    def test_entertainment_relationship_normalizes_activity_enum(self):
        tagged = self._tagged_fact_fixture()
        candidate = next(
            block
            for block in tagged["blocks"]
            if block.get("scope") == "report"
            and not block.get("locked_activity")
        )
        result = {
            "groups": [
                {
                    "block_ids": [candidate["id"]],
                    "activity": "other",
                    "work_category": "",
                    "task": "娱乐偏离",
                    "relationship_to_work": "entertainment_detour",
                    "evidence_ids": [candidate["id"]],
                    "confidence": "high",
                }
            ]
        }
        segments, _ = _segments_from_ai_groups(result, tagged)
        interpreted = next(
            segment
            for segment in segments
            if candidate["id"] in segment["fact_block_ids"]
        )
        self.assertEqual(interpreted["activity"], "entertainment")

    def test_valid_ai_groups_assemble_exact_timeline(self):
        tagged = self._tagged_fact_fixture()
        groups = []
        for block in tagged["blocks"]:
            if block["scope"] != "report" or block.get("locked_activity"):
                continue
            tag_names = {tag["name"] for tag in block.get("tags", [])}
            entertainment = "content_feed" in tag_names
            groups.append(
                {
                    "block_ids": [block["id"]],
                    "activity": "entertainment" if entertainment else "work",
                    "work_category": "" if entertainment else "系统维护",
                    "task": "浏览知乎首页" if entertainment else "维护服务器",
                    "relationship_to_work": (
                        "entertainment_detour"
                        if entertainment
                        else "same_work_task"
                    ),
                    "evidence_ids": [block["id"]],
                    "confidence": "high",
                }
            )
        segments, issues = _segments_from_ai_groups(
            {"groups": groups}, tagged
        )
        self.assertEqual(issues, [])
        self.assertEqual(
            sum(float(segment["duration_seconds"]) for segment in segments),
            1800,
        )
        self.assertTrue(
            any(
                segment["activity"] == "entertainment"
                and "zhihu.com" in " ".join(segment["evidence"])
                for segment in segments
            )
        )

    def test_zhihu_article_requires_task_context(self):
        tagged = self._single_computer_tagged_fact(
            "幼儿产检正常出生双脚畸形，医院坚持称系「医学盲区」 - 知乎",
            "zhihu.com",
        )
        report = next(block for block in tagged["blocks"] if block["scope"] == "report")
        tag_names = {tag["name"] for tag in report.get("tags", [])}
        self.assertIn("content_feed", tag_names)
        self.assertIn("context_required", tag_names)
        self.assertTrue(report["force_boundary"])
        self.assertNotIn("locked_activity", report)

    def test_personal_image_generation_requires_task_context(self):
        tagged = self._single_computer_tagged_fact(
            "生成自拍照片要求",
            "chatgpt.com",
        )
        report = next(block for block in tagged["blocks"] if block["scope"] == "report")
        tag_names = {tag["name"] for tag in report.get("tags", [])}
        self.assertIn("personal_image_generation", tag_names)
        self.assertIn("context_required", tag_names)
        self.assertTrue(report["force_boundary"])

    def test_deepseek_platform_is_system_maintenance_signal(self):
        tagged = self._single_computer_tagged_fact(
            "DeepSeek 开放平台",
            "platform.deepseek.com",
        )
        report = next(block for block in tagged["blocks"] if block["scope"] == "report")
        tag_names = {tag["name"] for tag in report.get("tags", [])}
        self.assertIn("system_maintenance_signal", tag_names)
        self.assertTrue(report["force_boundary"])

    def test_semantic_segmenter_receives_obsidian_context(self):
        tagged = self._tagged_fact_fixture()
        prompt = Path(__file__).resolve().parents[1] / "prompts" / "semantic-segmenter.md"

        def fake_request(_model, messages):
            payload = json.loads(messages[1]["content"].split("：\n", 1)[1])
            self.assertIn("read_only_obsidian_context", payload)
            context = payload["read_only_obsidian_context"]
            self.assertIn("profile_markdown", context)
            groups = [
                {
                    "block_ids": [item["id"]],
                    "activity": "work",
                    "work_category": "系统维护",
                    "task": "维护行为解释系统",
                    "relationship_to_work": "same_work_task",
                    "evidence_ids": [item["id"]],
                    "confidence": "high",
                }
                for item in payload["report_candidates"]
            ]
            return {
                "primary_work_task": "维护行为解释系统",
                "groups": groups,
                "material_uncertainties": [],
            }, {"provider": "test", "model": "fake"}

        with patch.object(
            semantic_analysis, "_request_json_report", side_effect=fake_request
        ):
            result = extract_semantic_timeline_with_deepseek(
                {"model": {}, "timezone": "Asia/Shanghai"},
                prompt,
                tagged,
                {
                    "profile_markdown": "当前重点是系统维护，不包含图像生成任务。",
                    "latest_plan_heading": "硬核通知方案",
                    "tasks": [{"title": "修正行为解释系统"}],
                    "pomodoro": [],
                },
            )
        self.assertEqual(result["primary_work_task"], "维护行为解释系统")

    def test_all_inactive_devices_suppress_push(self):
        self.assertTrue(
            _should_skip_push_for_inactive_devices(
                {"activity": {"not_afk_minutes": 0}},
                {"screen": {"on_minutes": 0}},
                {"screen": {"on_minutes": 0}},
                30,
            )
        )

    def test_any_active_device_allows_push(self):
        computer = {"activity": {"not_afk_minutes": 0}}
        phone = {"screen": {"on_minutes": 0}}
        tablet = {"screen": {"on_minutes": 0}}
        self.assertFalse(
            _should_skip_push_for_inactive_devices(
                {"activity": {"not_afk_minutes": 1}}, phone, tablet, 30
            )
        )
        self.assertFalse(
            _should_skip_push_for_inactive_devices(
                computer, {"screen": {"on_minutes": 1}}, tablet, 30
            )
        )
        self.assertFalse(
            _should_skip_push_for_inactive_devices(
                computer, phone, {"screen": {"on_minutes": 1}}, 30
            )
        )

    def test_stale_tablet_screen_on_is_unknown(self):
        screen_on = {
            "event": "screen",
            "state": "on",
            "_timestamp": datetime.fromisoformat("2026-07-27T00:41:44+08:00"),
        }
        state, event = _screen_state_at(
            [screen_on],
            datetime.fromisoformat("2026-07-28T02:00:00+08:00"),
            2700,
        )
        self.assertEqual(state, "unknown")
        self.assertIs(event, screen_on)

    def test_fresh_tablet_screen_on_remains_on(self):
        screen_on = {
            "event": "screen",
            "state": "on",
            "_timestamp": datetime.fromisoformat("2026-07-28T01:45:00+08:00"),
        }
        state, _ = _screen_state_at(
            [screen_on],
            datetime.fromisoformat("2026-07-28T02:00:00+08:00"),
            2700,
        )
        self.assertEqual(state, "on")

    def test_stale_phone_screen_on_is_unknown(self):
        screen_on = {
            "event": "screen",
            "state": "on",
            "_timestamp": datetime.fromisoformat("2026-07-27T00:41:44+08:00"),
        }
        state, _ = _phone_screen_state_at(
            [screen_on],
            datetime.fromisoformat("2026-07-28T02:00:00+08:00"),
            2700,
        )
        self.assertEqual(state, "unknown")

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

    def test_wechat_message_contains_shadow_review(self):
        report = {
            "concise_report": "以娱乐为主。",
            "verification_question": "判断是否正确？",
            "state_assessment": {"label": "entertainment"},
            "estimated_time_allocation": {},
            "mixing_assessment": {},
            "data_quality": {"level": "high", "material_issues": []},
        }
        candidate = {
            "would_intervene": True,
            "trigger_reasons": ["high_stimulation"],
            "observations": {
                "high_stimulation_minutes": 12,
                "meaningful_minutes": 0,
                "meaningful_minutes_60m": 4,
                "confirmed_rest_minutes": 0,
            },
            "recommended_task": {
                "title": "整理遍历论定义",
                "priority": "highest",
            },
            "context_source": "live",
            "context_age_minutes": 8,
        }
        _, content = build_wechat_message(
            report,
            datetime.fromisoformat("2026-07-28T00:00:00+08:00"),
            datetime.fromisoformat("2026-07-28T00:30:00+08:00"),
            candidate,
        )
        self.assertIn("## 影子判断", content)
        self.assertIn("会建议干预", content)
        self.assertIn("high_stimulation", content)
        self.assertIn("整理遍历论定义", content)
        self.assertIn("没有执行干预", content)

    def test_statistics_message_contains_review_counts(self):
        title, content = build_statistics_message(
            {
                "period": "2026-07-27",
                "report_count": 12,
                "estimated_minutes": {"work": 120, "entertainment": 20},
                "work_entertainment_mixing": {
                    "deviation_count": 2,
                    "deviation_minutes": 4,
                },
                "shadow_candidates": {
                    "candidate_count": 12,
                    "would_intervene_count": 3,
                    "push_count": 11,
                },
                "interpretation_warning": "番茄钟不覆盖客观时长。",
            },
            "daily",
        )
        self.assertIn("每日行为统计", title)
        self.assertIn("其中 3 个会建议干预", content)
        self.assertIn("PushPlus 已送达 11 个窗口", content)

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
