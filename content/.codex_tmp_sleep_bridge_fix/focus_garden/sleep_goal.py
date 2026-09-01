from __future__ import annotations

"""Deterministic semester sleep-goal projection for the Focus Garden homepage.

The source of truth is the Advisor daily-life summary generated from phone screen
facts.  This module only reads those summaries; it never writes the Advisor data
or claims that an inferred phone boundary equals physiological sleep.
"""

import json
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

SHANGHAI = ZoneInfo("Asia/Shanghai")
DEFAULT_START = date(2026, 9, 1)
DEFAULT_END = date(2027, 1, 17)
STRICT_CUTOFF_MINUTES = 30
FLEX_CUTOFF_MINUTES = 60


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _parse_date(value: Any, fallback: date) -> date:
    try:
        return date.fromisoformat(str(value))
    except (TypeError, ValueError):
        return fallback


def _time_minutes(value: Any) -> int | None:
    text = str(value or "").strip()
    try:
        hour, minute = (int(part) for part in text.split(":", 1))
    except (TypeError, ValueError):
        return None
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        return None
    return hour * 60 + minute


def _classify(summary: dict[str, Any]) -> tuple[str, str | None]:
    boundary = summary.get("phone_sleep_boundary")
    if not isinstance(boundary, dict):
        return "unknown", None
    last_use = str(boundary.get("last_phone_use_at_night") or "").strip() or None
    minutes = _time_minutes(last_use)
    if minutes is None or boundary.get("status") != "resolved":
        return "unknown", last_use
    if minutes <= STRICT_CUTOFF_MINUTES:
        return "strict", last_use
    if minutes <= FLEX_CUTOFF_MINUTES:
        return "flex", last_use
    return "late", last_use


def _day_record(data_root: Path, day: date, today: date) -> dict[str, Any]:
    if day > today:
        return {"date": day.isoformat(), "status": "future", "last_phone_use_at_night": None}
    path = data_root / "statistics" / "daily_life" / f"{day.isoformat()}.json"
    if not path.is_file():
        return {"date": day.isoformat(), "status": "unknown", "last_phone_use_at_night": None}
    summary = _read_json(path)
    status, last_use = _classify(summary)
    return {
        "date": day.isoformat(),
        "status": status,
        "last_phone_use_at_night": last_use,
        "source": str(path),
        "quality": (summary.get("phone_sleep_boundary") or {}).get("quality"),
        "boundary_status": (summary.get("phone_sleep_boundary") or {}).get("status"),
    }


def _week_status(records: list[dict[str, Any]], week_start: date, week_end: date, today: date) -> dict[str, Any]:
    evaluated = [r for r in records if r["status"] in {"strict", "flex", "late"}]
    strict = sum(r["status"] == "strict" for r in evaluated)
    on_time = sum(r["status"] in {"strict", "flex"} for r in evaluated)
    ended = week_end <= today
    if ended:
        status = "met" if strict >= 5 and on_time >= 7 else "missed"
    elif strict >= 5 and on_time >= 7:
        status = "met"
    elif strict + sum(r["status"] == "future" for r in records) < 5:
        status = "at_risk"
    else:
        status = "in_progress"
    return {
        "start": week_start.isoformat(),
        "end": week_end.isoformat(),
        "records": records,
        "evaluated_days": len(evaluated),
        "strict_days": strict,
        "flex_days": sum(r["status"] == "flex" for r in evaluated),
        "late_days": sum(r["status"] == "late" for r in evaluated),
        "on_time_days": on_time,
        "required_strict_days": 5,
        "required_on_time_days": 7,
        "status": status,
        "remaining_strict_days": max(0, 5 - strict),
        "remaining_on_time_days": max(0, 7 - on_time),
        "ended": ended,
        "days_elapsed": sum(day <= today for day in (week_start + timedelta(days=i) for i in range(7))),
    }


def build_sleep_goal_summary(settings: dict[str, Any], advisor_data_root: Path,
                             now: datetime | None = None) -> dict[str, Any]:
    config = settings.get("sleep_goal", {})
    current = (now or datetime.now(SHANGHAI)).astimezone(SHANGHAI)
    today = current.date()
    start = _parse_date(config.get("start_date"), DEFAULT_START)
    end = _parse_date(config.get("end_date"), DEFAULT_END)
    if end < start:
        end = start
    display_today = min(max(today, start), end)
    week_start = display_today - timedelta(days=display_today.weekday())
    week_start = max(start, week_start)
    week_end = min(end, week_start + timedelta(days=6))
    records = [_day_record(advisor_data_root, week_start + timedelta(days=i), today)
               for i in range((week_end - week_start).days + 1)]
    week = _week_status(records, week_start, week_end, today)

    semester_days = []
    for offset in range((display_today - start).days + 1):
        day = start + timedelta(days=offset)
        semester_days.append(_day_record(advisor_data_root, day, today))
    evaluated = [r for r in semester_days if r["status"] in {"strict", "flex", "late"}]
    strict = sum(r["status"] == "strict" for r in evaluated)
    on_time = sum(r["status"] in {"strict", "flex"} for r in evaluated)
    total_days = (end - start).days + 1
    return {
        "schema_version": 1,
        "enabled": bool(config.get("enabled", True)),
        "timezone": str(config.get("timezone", "Asia/Shanghai")),
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "today": today.isoformat(),
        "strict_cutoff": "00:30",
        "flex_cutoff": "01:00",
        "rule_text": "每7天至少5天在00:30前（含00:30）停止使用，另外2天不晚于01:00。",
        "week": week,
        "semester": {
            "evaluated_days": len(evaluated),
            "strict_days": strict,
            "on_time_days": on_time,
            "late_days": sum(r["status"] == "late" for r in evaluated),
            "unknown_days": sum(r["status"] == "unknown" for r in semester_days),
            "total_days": total_days,
            "remaining_days": max(0, (end - display_today).days),
        },
        "recent_days": semester_days[-14:],
        "source": "Advisor daily_life phone_sleep_boundary",
        "measurement_note": "这是根据手机夜间亮屏边界的估计，不等同于真实生理入睡时间；日报生成后才会定案。",
    }
