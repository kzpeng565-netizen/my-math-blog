from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from common import atomic_write_json


CATEGORIES = (
    "work",
    "entertainment",
    "brief_communication",
    "rest",
    "other",
    "uncertain",
)


def _report_files(output_root: Path, days: list[date]) -> list[Path]:
    files: list[Path] = []
    for day in days:
        files.extend(
            sorted((output_root / "ai_reports" / day.isoformat()).glob("*.json"))
        )
    return files


def _candidate_files(output_root: Path, days: list[date]) -> list[Path]:
    files: list[Path] = []
    for day in days:
        files.extend(
            sorted(
                (output_root / "intervention_candidates" / day.isoformat()).glob(
                    "*.json"
                )
            )
        )
    return files


def _successful_push_count(output_root: Path, days: list[date]) -> int:
    count = 0
    for day in days:
        for path in (output_root / "pushplus_receipts" / day.isoformat()).glob(
            "*.json"
        ):
            try:
                receipt = json.loads(path.read_text(encoding="utf-8"))
                count += int(receipt.get("status") == "accepted")
            except (OSError, TypeError, ValueError, json.JSONDecodeError):
                continue
    return count


def aggregate(output_root: Path, days: list[date], period: str) -> dict[str, Any]:
    totals = {key: 0.0 for key in CATEGORIES}
    mixing = {"deviation_count": 0, "deviation_minutes": 0.0}
    reports = 0
    for path in _report_files(output_root, days):
        try:
            report = json.loads(path.read_text(encoding="utf-8"))
            allocation = report["estimated_time_allocation"]
            for key in CATEGORIES:
                totals[key] += float(allocation.get(key, {}).get("estimate_minutes", 0))
            metrics = report.get("mixing_assessment", {})
            mixing["deviation_count"] += int(
                metrics.get("entertainment_deviation_count", 0)
            )
            mixing["deviation_minutes"] += float(
                metrics.get("entertainment_deviation_minutes", 0)
            )
            reports += 1
        except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError):
            continue
    candidate_count = 0
    would_intervene_count = 0
    for path in _candidate_files(output_root, days):
        try:
            candidate = json.loads(path.read_text(encoding="utf-8"))
            candidate_count += 1
            would_intervene_count += int(bool(candidate.get("would_intervene")))
        except (OSError, TypeError, ValueError, json.JSONDecodeError):
            continue
    return {
        "schema_version": 1,
        "period": period,
        "days": [day.isoformat() for day in days],
        "report_count": reports,
        "estimated_minutes": {key: round(value, 2) for key, value in totals.items()},
        "work_entertainment_mixing": {
            "deviation_count": mixing["deviation_count"],
            "deviation_minutes": round(mixing["deviation_minutes"], 2),
        },
        "shadow_candidates": {
            "candidate_count": candidate_count,
            "would_intervene_count": would_intervene_count,
            "push_count": _successful_push_count(output_root, days),
        },
        "interpretation_warning": (
            "统计来自设备事实和经校验语义时间线；Obsidian 与番茄钟不覆盖客观时长。"
        ),
    }


def update_statistics(output_root: Path, current_day: date) -> dict[str, Path]:
    daily = aggregate(output_root, [current_day], current_day.isoformat())
    daily_path = output_root / "statistics" / "daily" / f"{current_day}.json"
    atomic_write_json(daily_path, daily)
    week_start = current_day - timedelta(days=current_day.weekday())
    week_days = [week_start + timedelta(days=offset) for offset in range(7)]
    iso_year, iso_week, _ = current_day.isocalendar()
    weekly = aggregate(output_root, week_days, f"{iso_year}-W{iso_week:02d}")
    weekly_path = (
        output_root / "statistics" / "weekly" / f"{iso_year}-W{iso_week:02d}.json"
    )
    atomic_write_json(weekly_path, weekly)
    return {"daily": daily_path, "weekly": weekly_path}
