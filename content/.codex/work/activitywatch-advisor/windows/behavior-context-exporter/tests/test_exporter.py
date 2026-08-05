import sys
import tempfile
import unittest
import json
import logging
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from behavior_context_exporter import export, parse_pomodoro, parse_tasks


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
                "planned_tasks_path": vault / "ToDo-已经规划好的任务.md",
                "pomodoro_log_path": vault / "番茄钟log.md",
            }
            paths["profile_path"].write_text("profile", encoding="utf-8")
            paths["planned_tasks_path"].write_text(
                "- [ ] #task 安全测试", encoding="utf-8"
            )
            paths["pomodoro_log_path"].write_text("", encoding="utf-8")
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
