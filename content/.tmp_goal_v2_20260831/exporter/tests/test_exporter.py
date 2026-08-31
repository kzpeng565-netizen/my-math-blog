import sys
import tempfile
import unittest
import json
import logging
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from behavior_context_exporter import (
    export,
    export_goal_materials,
    parse_completed_tasks,
    parse_goal_material_manifest,
    parse_pomodoro,
    parse_tasks,
    sanitize_material_text,
)


TZ = ZoneInfo("Asia/Shanghai")


class TaskParserTests(unittest.TestCase):
    def test_tasks_priorities_dates_recurrence_and_notes(self):
        markdown = """# 2026-07-27 假期任务重排

> [!note]
> 先完成 A，再做 B；未完成顺延。

## 数学学习
- [ ] #task 完成GTM259 §2.1 [🍅:: 2/6] 🔺 ⏳ 2026-07-28
- [x] #task 已经完成 ⏫ ⏳ 2026-07-27
- [ ] #task 普通任务 📅 2026-08-01
- [ ] #task 每日复习 [🍅:: ] 🔁 every day ⏬
"""
        result = parse_tasks(markdown, datetime(2026, 7, 27).date())
        self.assertEqual(result["open_task_count"], 3)
        self.assertEqual(result["near_term_tasks"][0]["priority"], "highest")
        self.assertEqual(result["near_term_tasks"][0]["tomatoes_completed"], 2)
        self.assertEqual(result["near_term_tasks"][0]["tomatoes_total"], 6)
        self.assertEqual(result["later_tasks"][0]["due_date"], "2026-08-01")
        self.assertEqual(result["later_tasks"][0]["priority"], "normal")
        self.assertEqual(result["recurring_tasks"][0]["recurrence"], "every day")
        self.assertIsNone(result["recurring_tasks"][0]["tomatoes_total"])
        self.assertEqual(result["latest_plan_heading"], "2026-07-27 假期任务重排")
        self.assertIn("先完成 A", result["latest_plan_notes_markdown"])

    def test_chinese_path(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "中文目录" / "ToDo-已经规划好的任务.md"
            path.parent.mkdir()
            path.write_text("- [ ] #task 中文任务", encoding="utf-8")
            parsed = parse_tasks(path.read_text(encoding="utf-8"), datetime.now().date())
            self.assertEqual(parsed["later_tasks"][0]["title"], "中文任务")

    def test_extracts_obsidian_block_id_without_leaking_into_title(self):
        parsed = parse_tasks(
            "- [ ] #task 测试任务 ⏳ 2026-08-05 [🍅:: 1/2] ^8m2kx7q4",
            datetime(2026, 8, 5).date(),
        )
        task = parsed["today_tasks"][0]
        self.assertEqual(task["task_id"], "^8m2kx7q4")
        self.assertEqual(task["title"], "测试任务")
        self.assertEqual(parsed["missing_task_id_count"], 0)

    def test_completed_task_stats_are_archive_only(self):
        stats = parse_completed_tasks(
            "- [x] #task 已完成任务 ✅ 2026-08-05 ^8m2kx7q4\n"
            "- [ ] #task 不应统计 ^4abc"
        )
        self.assertEqual(stats["completed_task_count"], 1)
        self.assertEqual(stats["missing_task_id_count"], 0)

    def test_completed_events_are_stable_deduplicated_and_date_precision(self):
        stats = parse_completed_tasks(
            "- [x] #task 目标任务 ✅ 2026-08-19 ^goal1234\n"
            "- [x] #task 目标任务 ✅ 2026-08-19 ^goal1234\n"
            "- [x] #task 没有 ID ✅ 2026-08-20",
            source_modified_at="2026-08-20T09:30:00+08:00",
            today=datetime(2026, 8, 30).date(),
        )
        self.assertEqual(len(stats["recent_events"]), 1)
        event = stats["recent_events"][0]
        self.assertEqual(event["event_id"], "^goal1234@2026-08-19")
        self.assertEqual(event["completion_time_precision"], "date")
        self.assertEqual(event["task_modified_at"], "2026-08-20T09:30:00+08:00")


class GoalMaterialTests(unittest.TestCase):
    def test_only_checked_vault_files_are_authorized(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            allowed = root / "课程" / "大纲.md"
            allowed.parent.mkdir()
            allowed.write_text("第一章", encoding="utf-8")
            manifest = (
                "- [x] 概率论大纲｜[[课程/大纲.md]]\n"
                "- [ ] 未授权｜[[课程/大纲.md]]\n"
                "- [x] Vault 外｜路径：C:/Windows/win.ini"
            )
            result = parse_goal_material_manifest(manifest, root)
            self.assertEqual(sum(item["status"] == "authorized" for item in result), 1)
            self.assertEqual(sum(item["status"] == "not_allowed" for item in result), 1)

    def test_mathink_payload_is_removed(self):
        cleaned = sanitize_material_text(
            "正文\n```inkedmark\nBASE64-STROKES\n```\n结论\n"
            "%%inkedmark\nMORE-STROKES\n%%"
        )
        self.assertIn("正文", cleaned)
        self.assertIn("手写笔记", cleaned)
        self.assertNotIn("STROKES", cleaned)

    def test_markdown_is_exported_as_gzip_chunks_with_hash(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "遍历论.md"
            source.write_text("定义与习题\n" * 100, encoding="utf-8")
            output = root / "output"
            result = export_goal_materials(
                {"vault_root": str(root)},
                "- [x] 遍历论主教材｜[[遍历论.md]]",
                output,
                datetime(2026, 8, 30, 22, tzinfo=TZ),
            )
            self.assertEqual(result["status"], "ok")
            index = json.loads((output / "goal_agent" / "materials" / "index.json").read_text(encoding="utf-8"))
            self.assertEqual(index["document_count"], 1)
            document = index["documents"][0]
            self.assertEqual(len(document["sha256"]), 64)
            self.assertTrue((output / "goal_agent" / "materials" / document["export_file"]).is_file())


class PomodoroParserTests(unittest.TestCase):
    def test_declared_duration_wins_and_pause_inclusive_span_is_flagged(self):
        text = """
- 🍅 (pomodoro::WORK) (duration:: 40m)
  (begin:: 2026-07-27 08:00)
  (end:: 2026-07-27 08:40)
- 🍅 (pomodoro::WORK) (duration:: 20m)
  (begin:: 2026-07-27 09:00)
  (end:: 2026-07-27 09:20)
- 🍅 (pomodoro::WORK) (duration:: 40m)
  (begin:: 2026-07-27 10:00)
  (end:: 2026-07-27 14:00)
"""
        result = parse_pomodoro(text, datetime(2026, 7, 27, 15, tzinfo=TZ))
        self.assertEqual(result["last_24h"]["declared_minutes"], 100)
        self.assertEqual(
            result["data_quality"]["extended_wall_clock_interval_count"], 1
        )
        self.assertIn(
            "暂停后继续", result["data_quality"]["wall_clock_interpretation"]
        )

    def test_midnight_missing_note_old_data_and_malformed_line(self):
        text = """
- 🍅 (pomodoro::WORK) (duration:: 40m)
  (begin:: 2026-07-19 23:40)
  (end:: 2026-07-20 00:20)
- 忘记记录一次
- 🍅 (pomodoro::WORK) (duration:: broken)
"""
        result = parse_pomodoro(text, datetime(2026, 7, 27, 12, tzinfo=TZ))
        self.assertEqual(result["last_7d"]["session_count"], 0)
        self.assertEqual(result["data_quality"]["manual_missing_log_notes"], 1)
        self.assertEqual(result["data_quality"]["malformed_session_count"], 1)
        self.assertTrue(result["reference_only"])
        self.assertIn("无记录不能解释为无学习", result["interpretation_warning"])


class ExportSafetyTests(unittest.TestCase):
    def test_missing_source_does_not_overwrite_last_good_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            vault = root / "vault"
            output = root / "output"
            vault.mkdir()
            paths = {
                "profile_path": vault / "Profile.md",
                "task_collection_path": vault / "ToDo-任务集合.md",
                "planned_tasks_path": vault / "ToDo-已经规划好的任务.md",
                "completed_tasks_path": vault / "已完成任务.md",
                "pomodoro_log_path": vault / "番茄钟log.md",
                "goal_materials_path": vault / "目标模式资料清单.md",
            }
            paths["profile_path"].write_text("profile", encoding="utf-8")
            paths["task_collection_path"].write_text("collection", encoding="utf-8")
            paths["planned_tasks_path"].write_text(
                "- [ ] #task 安全测试", encoding="utf-8"
            )
            paths["pomodoro_log_path"].write_text("", encoding="utf-8")
            paths["completed_tasks_path"].write_text("", encoding="utf-8")
            paths["goal_materials_path"].write_text("# 未授权", encoding="utf-8")
            config_path = root / "config.json"
            config_path.write_text(
                json.dumps(
                    {
                        "vault_root": str(vault),
                        **{key: str(value) for key, value in paths.items()},
                        "export_dir": str(output),
                    }
                ),
                encoding="utf-8",
            )
            export(config_path)
            snapshot = (output / "context_snapshot.json").read_bytes()
            paths["planned_tasks_path"].unlink()
            with self.assertRaises(ValueError):
                export(config_path)
            self.assertEqual(
                (output / "context_snapshot.json").read_bytes(), snapshot
            )
            logging.shutdown()


if __name__ == "__main__":
    unittest.main()
