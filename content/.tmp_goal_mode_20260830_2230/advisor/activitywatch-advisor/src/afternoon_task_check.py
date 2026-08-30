from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from common import atomic_write_json, load_json
from deepseek_client import _request_json_report
from notifications import NtfyNotifier


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTEXT = Path("/home/conrad/workspace/behavior-context-sync/context_snapshot.json")
DEFAULT_RAW_TASKS = Path(
    "/home/conrad/workspace/behavior-context-sync/raw/ToDo-已经规划好的任务.md"
)
DEFAULT_RAW_POMODORO = Path(
    "/home/conrad/workspace/behavior-context-sync/raw/番茄钟log.md"
)
DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / "data"
DEFAULT_SETTINGS = PROJECT_ROOT / "config" / "settings.json"
DEFAULT_ENV = Path("/home/conrad/.config/activitywatch-advisor/env")
DEFAULT_NTFY_ENV = Path("/home/conrad/.config/activitywatch-advisor/ntfy.env")
TIMEZONE = ZoneInfo("Asia/Shanghai")

TASK_RE = re.compile(r"^\s*-\s+\[([ xX])\]\s+#task\s+(.*)$")
DATE_RE = re.compile(r"([⏳📅])\s*(\d{4}-\d{2}-\d{2})")
TOMATO_RE = re.compile(r"\[🍅::\s*(\d+(?:\.\d+)?)\s*/\s*(\d+(?:\.\d+)?)\]")
ANY_TOMATO_FIELD_RE = re.compile(r"\[🍅::[^\]]*\]")
POMODORO_RE = re.compile(
    r"^- 🍅 .*?\(duration::\s*(\d+)m\).*?\(begin::\s*(\d{4}-\d{2}-\d{2}) ",
    re.MULTILINE,
)


@dataclass(frozen=True)
class PlannedTask:
    title: str
    status: str
    scheduled_date: date | None
    due_date: date | None
    tomatoes_completed: float
    tomatoes_total: float
    raw_line: str

    @property
    def done(self) -> bool:
        return self.status.lower() == "x"


def _load_env_file(path: Path) -> None:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        if key and key not in os.environ:
            os.environ[key] = value.strip().strip('"').strip("'")


def _parse_date(value: str) -> date | None:
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def parse_tasks(markdown: str) -> list[PlannedTask]:
    tasks: list[PlannedTask] = []
    for line in markdown.splitlines():
        match = TASK_RE.match(line)
        if not match:
            continue
        status, rest = match.groups()
        scheduled_date = None
        due_date = None
        for marker, value in DATE_RE.findall(rest):
            parsed = _parse_date(value)
            if marker == "⏳":
                scheduled_date = parsed
            elif marker == "📅":
                due_date = parsed
        tomato_match = TOMATO_RE.search(rest)
        tomatoes_completed = 0.0
        tomatoes_total = 0.0
        if tomato_match:
            tomatoes_completed = float(tomato_match.group(1))
            tomatoes_total = float(tomato_match.group(2))
        title = ANY_TOMATO_FIELD_RE.sub("", rest)
        title = DATE_RE.sub("", title)
        title = re.sub(r"[⏫🔼🔽🔺🔁].*$", "", title).strip()
        tasks.append(
            PlannedTask(
                title=title,
                status=status,
                scheduled_date=scheduled_date,
                due_date=due_date,
                tomatoes_completed=tomatoes_completed,
                tomatoes_total=tomatoes_total,
                raw_line=line,
            )
        )
    return tasks


def tasks_for_day(tasks: list[PlannedTask], day: date) -> list[PlannedTask]:
    return [
        task
        for task in tasks
        if task.scheduled_date == day or task.due_date == day
    ]


def pomodoro_equivalent_for_day(markdown: str, day: date) -> float:
    total_minutes = 0
    day_text = day.isoformat()
    for minutes, begin_day in POMODORO_RE.findall(markdown):
        if begin_day == day_text:
            total_minutes += int(minutes)
    return round(total_minutes / 40, 2)


def progress_summary(
    *,
    tasks: list[PlannedTask],
    pomodoro_today: float,
) -> dict[str, Any]:
    task_count = len(tasks)
    completed_tasks = sum(1 for task in tasks if task.done)
    open_tasks = task_count - completed_tasks
    tomatoes_total = sum(task.tomatoes_total for task in tasks)
    tomatoes_from_tasks = sum(task.tomatoes_completed for task in tasks)
    tomatoes_completed = max(tomatoes_from_tasks, pomodoro_today)

    task_ratio = completed_tasks / task_count if task_count else None
    tomato_ratio = (
        min(tomatoes_completed / tomatoes_total, 1.0)
        if tomatoes_total
        else None
    )
    available = [value for value in (task_ratio, tomato_ratio) if value is not None]
    progress_ratio = sum(available) / len(available) if available else 1.0

    return {
        "task_count": task_count,
        "completed_tasks": completed_tasks,
        "open_tasks": open_tasks,
        "task_ratio": round(task_ratio, 3) if task_ratio is not None else None,
        "tomatoes_completed": round(tomatoes_completed, 2),
        "tomatoes_from_tasks": round(tomatoes_from_tasks, 2),
        "pomodoro_log_today": round(pomodoro_today, 2),
        "tomatoes_total": round(tomatoes_total, 2),
        "tomato_ratio": round(tomato_ratio, 3) if tomato_ratio is not None else None,
        "progress_ratio": round(progress_ratio, 3),
        "deterministic_should_send": bool(task_count and progress_ratio < 0.5),
        "tasks": [
            {
                "title": task.title,
                "done": task.done,
                "scheduled_date": task.scheduled_date.isoformat()
                if task.scheduled_date
                else None,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "tomatoes_completed": task.tomatoes_completed,
                "tomatoes_total": task.tomatoes_total,
            }
            for task in tasks
        ],
    }


def ai_decision(summary: dict[str, Any], settings: dict[str, Any]) -> dict[str, Any]:
    model = dict(settings.get("model", {}))
    if not model:
        raise RuntimeError("settings.model is not configured")
    model["thinking"] = "disabled"
    model["max_tokens"] = min(int(model.get("max_tokens", 1200)), 1200)
    messages = [
        {
            "role": "system",
            "content": (
                "你是一个克制的学习进度提醒裁决器。只输出 JSON 对象。"
                "下午三点时，如果当天计划任务完成度明显不到一半，"
                "应该发送手机提醒；如果任务很少、已完成一半、或证据不足，则不发送。"
                "不要责备用户。JSON 字段：should_send(boolean), reason(string), "
                "confidence(number), suggested_next_action(string)。"
            ),
        },
        {
            "role": "user",
            "content": json.dumps(summary, ensure_ascii=False, indent=2),
        },
    ]
    report, generation = _request_json_report(model, messages)
    return {
        "report": report,
        "generation": generation,
    }


def build_message(day: date, summary: dict[str, Any], reason: str, next_action: str) -> str:
    percent = round(float(summary["progress_ratio"]) * 100)
    return "\n".join(
        [
            f"现在是 {day.isoformat()} 15:00 左右，全天任务进度约 {percent}%。",
            f"任务：已完成 {summary['completed_tasks']}/{summary['task_count']} 个，未完成 {summary['open_tasks']} 个。",
            (
                "番茄钟："
                f"{summary['tomatoes_completed']}/{summary['tomatoes_total']} 🍅 "
                f"（任务字段 {summary['tomatoes_from_tasks']}，今日日志 {summary['pomodoro_log_today']}）。"
            ),
            f"判断：{reason}",
            f"下一步：{next_action}",
        ]
    )


def receipt_path(output_root: Path, day: date) -> Path:
    return (
        output_root
        / "statistics"
        / "ntfy_receipts"
        / "afternoon_task_check"
        / f"{day.isoformat()}.json"
    )


def run_check(
    *,
    day: date,
    context_path: Path,
    raw_tasks_path: Path,
    raw_pomodoro_path: Path,
    settings_path: Path,
    output_root: Path,
    env_file: Path,
    ntfy_env_file: Path,
    force: bool = False,
    no_ai: bool = False,
    no_push: bool = False,
    now: datetime | None = None,
) -> dict[str, Any]:
    now = now or datetime.now(TIMEZONE)
    receipt = receipt_path(output_root, day)
    if receipt.exists() and not force:
        existing = load_json(receipt)
        if existing.get("status") in {"accepted", "not_needed"}:
            return {
                "status": "already_checked",
                "period": day.isoformat(),
                "receipt": str(receipt),
            }

    context = load_json(context_path) if context_path.exists() else {}
    task_markdown = raw_tasks_path.read_text(encoding="utf-8")
    pomodoro_markdown = (
        raw_pomodoro_path.read_text(encoding="utf-8")
        if raw_pomodoro_path.exists()
        else ""
    )
    tasks = tasks_for_day(parse_tasks(task_markdown), day)
    summary = progress_summary(
        tasks=tasks,
        pomodoro_today=pomodoro_equivalent_for_day(pomodoro_markdown, day),
    )
    summary["context_generated_at"] = context.get("generated_at")

    ai: dict[str, Any] | None = None
    ai_error: str | None = None
    should_send = bool(summary["deterministic_should_send"])
    reason = "确定性进度低于全天一半。"
    next_action = "先收束一个最小可完成任务，再继续下一项。"

    if not no_ai and summary["task_count"]:
        _load_env_file(env_file)
        try:
            ai = ai_decision(summary, load_json(settings_path))
            report = ai.get("report", {})
            should_send = bool(report.get("should_send", should_send))
            reason = str(report.get("reason") or reason).strip()
            next_action = str(
                report.get("suggested_next_action") or next_action
            ).strip()
        except Exception as error:  # keep the reminder path available.
            ai_error = f"{type(error).__name__}: {error}"

    if not summary["task_count"]:
        status = "skipped"
        delivery: dict[str, Any] = {
            "status": status,
            "provider": "ntfy",
            "reason": "No tasks scheduled or due for this day.",
        }
    elif not should_send:
        status = "not_needed"
        delivery = {
            "status": status,
            "provider": "ntfy",
            "reason": reason,
        }
    elif no_push:
        status = "skipped"
        delivery = {
            "status": status,
            "provider": "ntfy",
            "reason": "--no-push was supplied",
        }
    else:
        _load_env_file(ntfy_env_file)
        result = NtfyNotifier().send(
            title=f"下午任务进度提醒 {day.isoformat()}",
            message=build_message(day, summary, reason, next_action),
            priority="high",
            tags=["calendar", "alarm_clock"],
        )
        delivery = result.as_dict()
        status = str(delivery.get("status"))

    output = {
        **delivery,
        "period": day.isoformat(),
        "checked_at": now.isoformat(timespec="seconds"),
        "summary": summary,
        "ai": ai,
        "ai_error": ai_error,
    }
    if no_push:
        output["dry_run"] = True
    atomic_write_json(receipt, output)
    return output


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Send a 15:00 ntfy reminder when daily task progress is below half."
    )
    parser.add_argument("--date", type=date.fromisoformat)
    parser.add_argument("--context", type=Path, default=DEFAULT_CONTEXT)
    parser.add_argument("--raw-tasks", type=Path, default=DEFAULT_RAW_TASKS)
    parser.add_argument("--raw-pomodoro", type=Path, default=DEFAULT_RAW_POMODORO)
    parser.add_argument("--settings", type=Path, default=DEFAULT_SETTINGS)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--env-file", type=Path, default=DEFAULT_ENV)
    parser.add_argument("--ntfy-env-file", type=Path, default=DEFAULT_NTFY_ENV)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--no-ai", action="store_true")
    parser.add_argument("--no-push", action="store_true")
    args = parser.parse_args()
    day = args.date or datetime.now(TIMEZONE).date()
    result = run_check(
        day=day,
        context_path=args.context,
        raw_tasks_path=args.raw_tasks,
        raw_pomodoro_path=args.raw_pomodoro,
        settings_path=args.settings,
        output_root=args.output_root,
        env_file=args.env_file,
        ntfy_env_file=args.ntfy_env_file,
        force=args.force,
        no_ai=args.no_ai,
        no_push=args.no_push,
    )
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result.get("status") in {"accepted", "already_checked", "not_needed", "skipped"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
