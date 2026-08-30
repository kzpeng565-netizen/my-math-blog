from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from common import atomic_write_json


SUPPORTED_SCHEMA_VERSION = 1
PRIORITY_ORDER = {
    "highest": 0,
    "high": 1,
    "medium": 2,
    "normal": 3,
    "low": 4,
    "lowest": 5,
}
POMODORO_RELIABILITY = "medium"
POMODORO_MINUTES = 40


class ContextValidationError(ValueError):
    pass


def _validate_task(task: Any) -> None:
    if not isinstance(task, dict):
        raise ContextValidationError("task must be an object")
    required = ("title", "priority", "source_order")
    if any(key not in task for key in required):
        raise ContextValidationError("task is missing required fields")
    if not isinstance(task["title"], str) or not isinstance(task["source_order"], int):
        raise ContextValidationError("task field type is invalid")


def validate_snapshot(snapshot: Any) -> dict[str, Any]:
    if not isinstance(snapshot, dict):
        raise ContextValidationError("snapshot must be an object")
    if snapshot.get("schema_version") != SUPPORTED_SCHEMA_VERSION:
        raise ContextValidationError("unsupported schema_version")
    generated_at = snapshot.get("generated_at")
    if not isinstance(generated_at, str):
        raise ContextValidationError("generated_at must be a string")
    try:
        generated = datetime.fromisoformat(generated_at.replace("Z", "+00:00"))
    except ValueError as error:
        raise ContextValidationError("generated_at is invalid") from error
    if generated.tzinfo is None:
        raise ContextValidationError("generated_at must include timezone")
    if not isinstance(snapshot.get("sources"), dict):
        raise ContextValidationError("sources must be an object")
    if not isinstance(snapshot.get("profile"), dict) or not isinstance(
        snapshot["profile"].get("raw_markdown"), str
    ):
        raise ContextValidationError("profile.raw_markdown must be a string")
    tasks = snapshot.get("tasks")
    if not isinstance(tasks, dict):
        raise ContextValidationError("tasks must be an object")
    for key in (
        "overdue_tasks",
        "today_tasks",
        "near_term_tasks",
        "later_tasks",
        "recurring_tasks",
    ):
        values = tasks.get(key)
        if not isinstance(values, list):
            raise ContextValidationError(f"tasks.{key} must be a list")
        for task in values:
            _validate_task(task)
    if not isinstance(snapshot.get("pomodoro"), dict):
        raise ContextValidationError("pomodoro must be an object")
    if snapshot["pomodoro"].get("reference_only") is not True:
        raise ContextValidationError("pomodoro.reference_only must be true")
    return snapshot


def _read_valid(path: Path) -> dict[str, Any]:
    return validate_snapshot(json.loads(path.read_text(encoding="utf-8")))


def _task_view(task: dict[str, Any]) -> dict[str, Any]:
    return {
        key: task.get(key)
        for key in (
            "title",
            "category",
            "priority",
            "scheduled_date",
            "due_date",
            "tomatoes_completed",
            "tomatoes_total",
            "source_order",
        )
    }


def _rank(tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        tasks,
        key=lambda task: (
            PRIORITY_ORDER.get(task.get("priority", "normal"), 3),
            task.get("source_order", 10**9),
        ),
    )


def _pomodoro_data_quality(pomodoro: dict[str, Any]) -> dict[str, Any]:
    quality = {
        key: pomodoro.get("data_quality", {}).get(key)
        for key in (
            "extended_wall_clock_interval_count",
            "manual_missing_log_notes",
            "malformed_session_count",
            "reliability",
            "wall_clock_interpretation",
        )
        if key in pomodoro.get("data_quality", {})
    }
    quality["reliability"] = POMODORO_RELIABILITY
    quality["pomodoro_minutes"] = POMODORO_MINUTES
    quality["unit_rule"] = "1 tomato / 1 Pomodoro / 1 🍅 = 40 minutes"
    quality["decision_role"] = (
        "medium_reliability_positive_evidence_only; "
        "1 tomato equals 40 minutes; tomato counts are estimated task budgets/progress markers, "
        "not completion guarantees; missing logs must not be interpreted as no work"
    )
    return quality


def compact_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    tasks = snapshot["tasks"]
    pomodoro = snapshot["pomodoro"]
    return {
        "generated_at": snapshot["generated_at"],
        "profile_markdown": snapshot["profile"]["raw_markdown"],
        "latest_plan_heading": tasks.get("latest_plan_heading"),
        "latest_plan_notes_markdown": tasks.get("latest_plan_notes_markdown", ""),
        "tasks": {
            "overdue": [
                _task_view(task) for task in _rank(tasks["overdue_tasks"])[:5]
            ],
            "today": [_task_view(task) for task in _rank(tasks["today_tasks"])[:8]],
            "near_term": [
                _task_view(task) for task in _rank(tasks["near_term_tasks"])[:5]
            ],
        },
        "pomodoro": {
            "reference_only": True,
            "last_recorded_session_end": pomodoro.get("last_recorded_session_end"),
            "last_24h": pomodoro.get("last_24h", {}),
            "last_3d": pomodoro.get("last_3d", {}),
            "last_7d": pomodoro.get("last_7d", {}),
            "data_quality": _pomodoro_data_quality(pomodoro),
            "interpretation_warning": pomodoro.get("interpretation_warning", ""),
        },
    }


def load_obsidian_context(
    live_path: Path, cache_path: Path, now: datetime | None = None
) -> dict[str, Any]:
    current = now or datetime.now(timezone.utc)
    source = "unavailable"
    snapshot: dict[str, Any] | None = None
    reason: str | None = None
    try:
        snapshot = _read_valid(live_path)
        atomic_write_json(cache_path, snapshot)
        source = "live"
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ContextValidationError) as error:
        reason = f"{type(error).__name__}: {error}"
        try:
            snapshot = _read_valid(cache_path)
            source = "last_known_good"
        except (
            OSError,
            UnicodeDecodeError,
            json.JSONDecodeError,
            ContextValidationError,
        ):
            return {
                "available": False,
                "reason": "context_unavailable",
                "context_source": "unavailable",
                "context_age_minutes": None,
                "load_error": reason,
                "ai_context": None,
            }
    generated = datetime.fromisoformat(
        snapshot["generated_at"].replace("Z", "+00:00")
    )
    age = max(0.0, (current.astimezone(timezone.utc) - generated.astimezone(timezone.utc)).total_seconds() / 60)
    return {
        "available": True,
        "reason": None,
        "context_source": source,
        "context_age_minutes": round(age, 2),
        "load_error": reason,
        "ai_context": compact_snapshot(snapshot),
    }
