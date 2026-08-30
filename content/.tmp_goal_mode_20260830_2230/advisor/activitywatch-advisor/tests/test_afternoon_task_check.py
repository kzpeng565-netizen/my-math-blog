from __future__ import annotations

import unittest
from datetime import date
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from afternoon_task_check import (
    parse_tasks,
    pomodoro_equivalent_for_day,
    progress_summary,
    tasks_for_day,
)


class AfternoonTaskCheckTests(unittest.TestCase):
    def test_counts_today_tasks_and_tomatoes(self) -> None:
        markdown = "\n".join(
            [
                "- [x] #task 完成A [🍅:: 2/2] ⏳ 2026-07-29",
                "- [ ] #task 完成B [🍅:: 1/4] ⏳ 2026-07-29",
                "- [ ] #task 明天任务 [🍅:: 0/3] ⏳ 2026-07-30",
            ]
        )
        tasks = tasks_for_day(parse_tasks(markdown), date(2026, 7, 29))
        summary = progress_summary(tasks=tasks, pomodoro_today=0)
        self.assertEqual(summary["task_count"], 2)
        self.assertEqual(summary["completed_tasks"], 1)
        self.assertEqual(summary["open_tasks"], 1)
        self.assertEqual(summary["tomatoes_completed"], 3)
        self.assertEqual(summary["tomatoes_total"], 6)
        self.assertFalse(summary["deterministic_should_send"])

    def test_uses_pomodoro_log_when_task_tomatoes_are_stale(self) -> None:
        markdown = "- [ ] #task 完成A [🍅:: 0/4] ⏳ 2026-07-29"
        pomodoro = "\n".join(
            [
                "- 🍅 (pomodoro::WORK) (duration:: 40m) (begin:: 2026-07-29 10:00) - (end:: 2026-07-29 10:40)",
                "- 🍅 (pomodoro::WORK) (duration:: 20m) (begin:: 2026-07-29 11:00) - (end:: 2026-07-29 11:20)",
            ]
        )
        tasks = tasks_for_day(parse_tasks(markdown), date(2026, 7, 29))
        summary = progress_summary(
            tasks=tasks,
            pomodoro_today=pomodoro_equivalent_for_day(pomodoro, date(2026, 7, 29)),
        )
        self.assertEqual(summary["pomodoro_log_today"], 1.5)
        self.assertEqual(summary["tomatoes_completed"], 1.5)
        self.assertTrue(summary["deterministic_should_send"])


if __name__ == "__main__":
    unittest.main()
