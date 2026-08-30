"""Pi-side task intent queue.

The Pi never writes the Obsidian vault.  It keeps a small durable queue of
web mutations and overlays it on the latest exported task snapshot so that
Next Action can react immediately.  The desktop Obsidian plugin is the only
Markdown writer and acknowledges a mutation only after the matching snapshot
has reached this Pi.
"""

from __future__ import annotations

import hashlib
import json
import re
import uuid
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from common import atomic_write_json


TASK_ID_RE = re.compile(r"^\^[A-Za-z0-9-]{4,32}$")
CLIENT_REQUEST_ID_RE = re.compile(r"^[A-Za-z0-9_-]{8,120}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
PRIORITIES = {"highest", "high", "medium", "normal", "low", "lowest"}
PROCRASTINATION_THRESHOLD_DAYS = 2
WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}
EDITABLE_FIELDS = {
    "title",
    "scheduled_date",
    "due_date",
    "priority",
    "tomatoes_completed",
    "tomatoes_total",
    "recurrence",
    "category",
}


def _now(timezone_name: str) -> datetime:
    return datetime.now(ZoneInfo(timezone_name))


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return {}


def _snapshot_hash(path: Path) -> str | None:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def _state_path(output_root: Path) -> Path:
    return output_root / "task_sync" / "state.json"


def _load_state(output_root: Path) -> dict[str, Any]:
    state = _read_json(_state_path(output_root))
    if state.get("schema_version") != 1 or not isinstance(state.get("mutations"), list):
        return {
            "schema_version": 1,
            "revision": 0,
            "mutations": [],
            "completions": [],
            "daily_plans": {},
            "postponements": {},
            "primary_tasks": {},
            "request_history": {},
        }
    state["revision"] = int(state.get("revision", 0) or 0)
    state.setdefault("completions", [])
    state.setdefault("daily_plans", {})
    state.setdefault("postponements", {})
    state.setdefault("primary_tasks", {})
    state.setdefault("request_history", {})
    if not isinstance(state["completions"], list):
        state["completions"] = []
    if not isinstance(state["daily_plans"], dict):
        state["daily_plans"] = {}
    if not isinstance(state["postponements"], dict):
        state["postponements"] = {}
    if not isinstance(state["primary_tasks"], dict):
        state["primary_tasks"] = {}
    if not isinstance(state["request_history"], dict):
        state["request_history"] = {}
    return state


def _save_state(output_root: Path, state: dict[str, Any]) -> None:
    atomic_write_json(_state_path(output_root), state)


def _bucket(task: dict[str, Any], today: date) -> str:
    if task.get("recurrence"):
        return "recurring"
    scheduled = task.get("scheduled_date")
    if not isinstance(scheduled, str) or not DATE_RE.fullmatch(scheduled):
        if task.get("task_source") == "collection":
            return "unassigned"
        return "later"
    scheduled_day = date.fromisoformat(scheduled)
    if scheduled_day < today:
        return "overdue"
    if scheduled_day == today:
        return "today"
    if scheduled_day <= date.fromordinal(today.toordinal() + 3):
        return "near_term"
    return "later"


def _snapshot_tasks(snapshot: dict[str, Any], today: date) -> dict[str, dict[str, Any]]:
    task_groups = snapshot.get("tasks", {})
    if not isinstance(task_groups, dict):
        return {}
    tasks: dict[str, dict[str, Any]] = {}
    for source_bucket in (
        "overdue_tasks",
        "today_tasks",
        "near_term_tasks",
        "later_tasks",
        "recurring_tasks",
        "unassigned_tasks",
    ):
        for raw in task_groups.get(source_bucket, []):
            if not isinstance(raw, dict):
                continue
            task_id = raw.get("task_id")
            if not isinstance(task_id, str) or not TASK_ID_RE.fullmatch(task_id):
                continue
            task = dict(raw)
            task["task_id"] = task_id
            task["task_source"] = str(task.get("task_source") or "planned")
            task["status"] = "open"
            task["bucket"] = _bucket(task, today)
            tasks[task_id] = task
    return tasks


def _snapshot_completed_recent(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    task_events = snapshot.get("task_events")
    if not isinstance(task_events, dict):
        return []
    events = task_events.get("completed_recent")
    if not isinstance(events, list):
        return []
    deduplicated: dict[str, dict[str, Any]] = {}
    for raw in events[-1000:]:
        if not isinstance(raw, dict):
            continue
        task_id = raw.get("task_id")
        completed_at = str(raw.get("completed_at") or "")
        day_text = completed_at[:10]
        if not isinstance(task_id, str) or not TASK_ID_RE.fullmatch(task_id) or not DATE_RE.fullmatch(day_text):
            continue
        try:
            date.fromisoformat(day_text)
        except ValueError:
            continue
        event_id = str(raw.get("event_id") or _completion_key(task_id, day_text))
        if event_id != _completion_key(task_id, day_text):
            continue
        deduplicated[event_id] = {
            "event_id": event_id,
            "task_id": task_id,
            "title": str(raw.get("title") or "")[:500],
            "completed_at": completed_at,
            "occurrence_date": day_text,
            "completion_time_precision": str(raw.get("completion_time_precision") or "date"),
            "task_modified_at": raw.get("task_modified_at"),
            "scheduled_date": raw.get("scheduled_date"),
            "due_date": raw.get("due_date"),
            "tomatoes_completed": raw.get("tomatoes_completed"),
            "tomatoes_total": raw.get("tomatoes_total"),
            "source": "obsidian_export",
            "status": "completed",
            "recurring": False,
            "sync_pending": False,
        }
    return sorted(
        deduplicated.values(), key=lambda item: (item["occurrence_date"], item["task_id"])
    )[-500:]


def _project_weekly_recurrence(task: dict[str, Any], today: date) -> None:
    recurrence = task.get("recurrence")
    scheduled = task.get("scheduled_date")
    if not isinstance(recurrence, str) or not isinstance(scheduled, str) or not DATE_RE.fullmatch(scheduled):
        return
    match = re.fullmatch(r"every\s+week\s+on\s+([A-Za-z]+)", recurrence.strip(), re.IGNORECASE)
    if not match:
        return
    weekday = WEEKDAYS.get(match.group(1).lower())
    if weekday is None:
        return
    scheduled_day = date.fromisoformat(scheduled)
    if scheduled_day >= today:
        return
    next_occurrence = today + timedelta(days=(weekday - today.weekday()) % 7)
    task["source_scheduled_date"] = scheduled
    task["scheduled_date"] = next_occurrence.isoformat()
    task["recurrence_projected"] = True


def _next_weekly_occurrence(recurrence: Any, occurrence_day: date) -> date:
    match = re.fullmatch(r"every\s+week\s+on\s+([A-Za-z]+)", str(recurrence or "").strip(), re.IGNORECASE)
    if not match or WEEKDAYS.get(match.group(1).lower()) != occurrence_day.weekday():
        raise ValueError("only weekly recurrence on the occurrence weekday can be completed from the web")
    return occurrence_day + timedelta(days=7)


def _completion_key(task_id: str, occurrence_date: str) -> str:
    return f"{task_id}@{occurrence_date}"


def _observe_daily_plan(state: dict[str, Any], tasks: dict[str, dict[str, Any]], today: date,
                        generated_at: str) -> bool:
    """Keep a monotonic daily tomato plan so later edits cannot erase evidence."""
    day_key = today.isoformat()
    plans = state["daily_plans"]
    plan = plans.setdefault(day_key, {"date": day_key, "tasks": {}, "first_seen_at": generated_at})
    plan_tasks = plan.setdefault("tasks", {})
    changed = False
    candidates = [task for task in tasks.values() if task.get("scheduled_date") == day_key]
    completions = [item for item in state["completions"] if item.get("occurrence_date") == day_key]
    for completion in completions:
        snapshot = completion.get("task")
        if isinstance(snapshot, dict):
            candidates.append(snapshot)
    for task in candidates:
        task_id = task.get("task_id")
        total = task.get("tomatoes_total")
        if not isinstance(task_id, str) or not isinstance(total, int) or total <= 0:
            continue
        key = _completion_key(task_id, day_key)
        completed = task.get("tomatoes_completed")
        completed = completed if isinstance(completed, int) else 0
        existing = plan_tasks.get(key)
        if not isinstance(existing, dict):
            plan_tasks[key] = {
                "occurrence_id": key, "task_id": task_id, "title": task.get("title"),
                "tomatoes_planned": total, "tomatoes_completed": min(total, completed),
            }
            changed = True
            continue
        next_planned = max(int(existing.get("tomatoes_planned", 0) or 0), total)
        next_completed = max(int(existing.get("tomatoes_completed", 0) or 0), min(next_planned, completed))
        if next_planned != existing.get("tomatoes_planned") or next_completed != existing.get("tomatoes_completed"):
            existing["tomatoes_planned"] = next_planned
            existing["tomatoes_completed"] = next_completed
            changed = True
    if changed:
        plan["updated_at"] = generated_at
    return changed


def _daily_scorecards(state: dict[str, Any]) -> list[dict[str, Any]]:
    scorecards = []
    for day_key, plan in sorted(state["daily_plans"].items()):
        if not isinstance(plan, dict) or not DATE_RE.fullmatch(str(day_key)):
            continue
        rows = [row for row in (plan.get("tasks") or {}).values() if isinstance(row, dict)]
        planned = sum(int(row.get("tomatoes_planned", 0) or 0) for row in rows)
        completed = sum(min(int(row.get("tomatoes_planned", 0) or 0),
                            int(row.get("tomatoes_completed", 0) or 0)) for row in rows)
        all_completed = bool(rows) and completed == planned
        scorecards.append({
            "date": day_key, "planned_tomatoes": planned, "completed_tomatoes": completed,
            "task_count": len(rows), "all_completed": all_completed,
            "eligible": planned >= 7 and all_completed,
        })
    return scorecards[-62:]


def _clean_text(value: Any, *, limit: int = 500) -> str:
    return " ".join(str(value or "").split())[:limit]


def _clean_date(value: Any) -> str | None:
    if value in (None, ""):
        return None
    result = str(value)
    if not DATE_RE.fullmatch(result):
        raise ValueError("date must use YYYY-MM-DD")
    date.fromisoformat(result)
    return result


def _clean_tomato(value: Any) -> int | None:
    if value in (None, ""):
        return None
    result = int(value)
    if result < 0 or result > 999:
        raise ValueError("tomato count must be between 0 and 999")
    return result


def _clean_changes(payload: dict[str, Any], *, creating: bool) -> dict[str, Any]:
    changes: dict[str, Any] = {}
    for key in EDITABLE_FIELDS:
        if key not in payload and not (creating and key == "priority"):
            continue
        value = payload.get(key)
        if key == "title":
            value = _clean_text(value)
            if creating and not value:
                raise ValueError("title is required")
        elif key in {"scheduled_date", "due_date"}:
            value = _clean_date(value)
        elif key in {"tomatoes_completed", "tomatoes_total"}:
            value = _clean_tomato(value)
        elif key == "priority":
            value = str(value or "normal")
            if value not in PRIORITIES:
                raise ValueError("invalid priority")
        elif key in {"recurrence", "category"}:
            value = _clean_text(value, limit=120) or None
        changes[key] = value
    if creating:
        total = changes.get("tomatoes_total")
        completed = changes.get("tomatoes_completed")
        if total is not None and completed is not None and completed > total:
            raise ValueError("completed tomatoes cannot exceed total tomatoes")
    return changes


def _apply_mutation(tasks: dict[str, dict[str, Any]], mutation: dict[str, Any], today: date) -> None:
    operation = mutation.get("operation")
    task_id = mutation.get("task_id")
    payload = mutation.get("payload", {})
    if not isinstance(task_id, str) or not isinstance(payload, dict):
        return
    if operation == "create":
        if task_id in tasks:
            return
        task = {
            "task_id": task_id,
            "title": "",
            "category": None,
            "planning_batch": None,
            "priority": "normal",
            "scheduled_date": None,
            "due_date": None,
            "recurrence": None,
            "tomatoes_completed": None,
            "tomatoes_total": None,
            "source_order": 10**9,
            "raw_line": None,
            "status": "open",
            "created_on_pi": True,
            "task_source": "collection",
        }
        task.update(payload)
        task["task_source"] = "planned" if task.get("scheduled_date") else "collection"
        task["bucket"] = _bucket(task, today)
        tasks[task_id] = task
    elif operation == "update" and task_id in tasks:
        tasks[task_id].update(payload)
        tasks[task_id]["task_source"] = "planned" if tasks[task_id].get("scheduled_date") else "collection"
        tasks[task_id]["bucket"] = _bucket(tasks[task_id], today)
    elif operation == "complete" and task_id in tasks:
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["completed_on_pi"] = mutation.get("created_at")
    elif operation == "advance_tomatoes" and task_id in tasks:
        # This is an absolute, monotonic target rather than an increment.  A
        # desktop retry can therefore safely reapply the same mutation after
        # a write/export interruption without creating an extra tomato.
        target = payload.get("target_completed")
        if isinstance(target, int):
            current = tasks[task_id].get("tomatoes_completed")
            current = current if isinstance(current, int) else 0
            total = tasks[task_id].get("tomatoes_total")
            if isinstance(total, int):
                target = min(target, total)
            tasks[task_id]["tomatoes_completed"] = max(current, target)
    elif operation == "delete":
        tasks.pop(task_id, None)


def _attach_postponement_metadata(
    tasks: dict[str, dict[str, Any]], state: dict[str, Any]
) -> None:
    postponements = state.get("postponements", {})
    if not isinstance(postponements, dict):
        return
    for task_id, task in tasks.items():
        record = postponements.get(task_id)
        if not isinstance(record, dict):
            continue
        try:
            postponed_days = max(0, int(record.get("postponed_days", 0) or 0))
            postpone_count = max(0, int(record.get("postpone_count", 0) or 0))
        except (TypeError, ValueError):
            continue
        if postponed_days <= 0:
            continue
        task["postponed_days"] = postponed_days
        task["postpone_count"] = postpone_count
        task["procrastinated"] = postponed_days >= PROCRASTINATION_THRESHOLD_DAYS
        task["last_postponed_at"] = record.get("last_postponed_at")


def _primary_task_view(
    state: dict[str, Any], tasks: dict[str, dict[str, Any]], today: date
) -> dict[str, dict[str, Any]]:
    """Return only still-valid today/tomorrow primary selections."""
    allowed_dates = {today.isoformat(), (today + timedelta(days=1)).isoformat()}
    result: dict[str, dict[str, Any]] = {}
    for day_key, raw in state.get("primary_tasks", {}).items():
        if day_key not in allowed_dates or not isinstance(raw, dict):
            continue
        task_id = str(raw.get("task_id", ""))
        task = tasks.get(task_id)
        if task is None:
            # A completed task leaves the open view, but its durable selection
            # remains valid for today's unlock gate.
            completion = next(
                (
                    item for item in state.get("completions", [])
                    if item.get("task_id") == task_id and item.get("occurrence_date") == day_key
                ),
                None,
            )
            task = completion.get("task") if isinstance(completion, dict) else None
        if not isinstance(task, dict) or task.get("scheduled_date") != day_key:
            continue
        result[day_key] = {
            "date": day_key,
            "task_id": task_id,
            "title": str(task.get("title") or raw.get("title") or ""),
            "set_at": raw.get("set_at"),
        }
    return result


def _steam_unlock_gate(
    state: dict[str, Any], primary_tasks: dict[str, dict[str, Any]], today: date
) -> dict[str, Any]:
    day_key = today.isoformat()
    scorecard = next(
        (card for card in _daily_scorecards(state) if card.get("date") == day_key),
        {},
    )
    completed_tomatoes = max(0, int(scorecard.get("completed_tomatoes", 0) or 0))
    primary = primary_tasks.get(day_key)
    primary_task_id = str(primary.get("task_id", "")) if primary else ""
    primary_completed = bool(
        primary_task_id
        and any(
            item.get("task_id") == primary_task_id and item.get("occurrence_date") == day_key
            for item in state.get("completions", [])
        )
    )
    return {
        "date": day_key,
        "completed_tomatoes": completed_tomatoes,
        "required_completed_tomatoes": 6,
        "tomato_requirement_met": completed_tomatoes > 5,
        "primary_task_id": primary_task_id or None,
        "primary_task_title": primary.get("title") if primary else None,
        "primary_task_completed": primary_completed,
        "eligible": completed_tomatoes > 5 and primary_completed,
    }


def effective_state(
    context_path: Path, output_root: Path, *, timezone_name: str = "Asia/Shanghai", now: datetime | None = None
) -> dict[str, Any]:
    current = now or _now(timezone_name)
    snapshot = _read_json(context_path)
    if not snapshot:
        snapshot = _read_json(output_root / "context_cache" / "current.json")
    tasks = _snapshot_tasks(snapshot, current.date())
    exported_completed = _snapshot_completed_recent(snapshot)
    state = _load_state(output_root)
    for mutation in state["mutations"]:
        if isinstance(mutation, dict):
            _apply_mutation(tasks, mutation, current.date())
    for task in tasks.values():
        _project_weekly_recurrence(task, current.date())
    _attach_postponement_metadata(tasks, state)
    primary_tasks = _primary_task_view(state, tasks, current.date())
    for task in tasks.values():
        scheduled = task.get("scheduled_date")
        primary = primary_tasks.get(str(scheduled))
        task["is_primary"] = bool(primary and primary.get("task_id") == task.get("task_id"))
        task["primary_date"] = scheduled if task["is_primary"] else None
    generated_at = current.isoformat(timespec="seconds")
    if _observe_daily_plan(state, tasks, current.date(), generated_at):
        _save_state(output_root, state)
    open_tasks = [task for task in tasks.values() if task.get("status") == "open"]
    open_tasks.sort(key=lambda task: (task.get("source_order", 10**9), task["task_id"]))
    grouped = {key: [] for key in ("unassigned", "overdue", "today", "near_term", "later", "recurring")}
    for task in open_tasks:
        grouped[_bucket(task, current.date())].append(task)
    pi_completed = [
        {**item.get("task", {}), "event_id": _completion_key(str(item.get("task_id", "")), str(item.get("occurrence_date", ""))),
         "status": "completed", "completed_at": item.get("completed_at"),
         "occurrence_date": item.get("occurrence_date"), "completion_time_precision": "second",
         "source": "pi_task_sync", "recurring": bool(item.get("recurring")),
         "is_primary": bool(primary_tasks.get(current.date().isoformat(), {}).get("task_id") == item.get("task_id")),
         "primary_date": current.date().isoformat() if primary_tasks.get(current.date().isoformat(), {}).get("task_id") == item.get("task_id") else None,
         "sync_pending": bool(item.get("mutation_id") in {m.get("mutation_id") for m in state["mutations"]})}
        for item in state["completions"]
        if item.get("task_id") and item.get("occurrence_date")
    ]
    completed_by_id = {item["event_id"]: item for item in exported_completed}
    completed_by_id.update({item["event_id"]: item for item in pi_completed})
    completed_recent = sorted(
        completed_by_id.values(), key=lambda item: (str(item.get("occurrence_date", "")), str(item.get("task_id", "")))
    )[-500:]
    return {
        "schema_version": 1,
        "generated_at": generated_at,
        "revision": state["revision"],
        "pending_mutation_count": len(state["mutations"]),
        "snapshot_sha256": _snapshot_hash(context_path),
        "tasks": grouped,
        "mutations": state["mutations"],
        "completed_today": [item for item in completed_recent if item.get("occurrence_date") == current.date().isoformat()],
        "completed_recent": completed_recent,
        "daily_scorecards": _daily_scorecards(state),
        "primary_tasks": primary_tasks,
        "steam_unlock_gate": _steam_unlock_gate(state, primary_tasks, current.date()),
    }


def compact_for_next_action(effective: dict[str, Any]) -> dict[str, Any]:
    fields = (
        "task_id", "title", "category", "priority", "scheduled_date", "due_date", "task_source",
        "tomatoes_completed", "tomatoes_total", "source_order", "recurrence",
        "source_scheduled_date", "recurrence_projected",
        "postponed_days", "postpone_count", "procrastinated", "last_postponed_at",
        "is_primary", "primary_date",
    )
    return {
        "tasks": {
            key: [{field: task.get(field) for field in fields} for task in effective["tasks"][key]]
            for key in ("unassigned", "overdue", "today", "near_term", "later", "recurring")
        },
        "task_sync": {
            "revision": effective["revision"],
            "pending_mutation_count": effective["pending_mutation_count"],
            "effective_generated_at": effective["generated_at"],
            "snapshot_sha256": effective["snapshot_sha256"],
        },
        "primary_tasks": effective.get("primary_tasks", {}),
        "steam_unlock_gate": effective.get("steam_unlock_gate", {}),
    }


def set_primary_task(
    context_path: Path,
    output_root: Path,
    payload: dict[str, Any],
    *,
    timezone_name: str = "Asia/Shanghai",
    now: datetime | None = None,
) -> dict[str, Any]:
    """Set, replace, or clear the one primary task for today or tomorrow."""
    current = now or _now(timezone_name)
    task_id = str(payload.get("task_id", ""))
    if not TASK_ID_RE.fullmatch(task_id):
        raise ValueError("task_id must be an Obsidian block ID")
    effective = effective_state(
        context_path, output_root, timezone_name=timezone_name, now=current
    )
    tasks = {
        task["task_id"]: task
        for group in effective["tasks"].values()
        for task in group
    }
    task = tasks.get(task_id)
    if not task:
        raise ValueError("task_id does not exist in the effective task view")
    scheduled_date = str(task.get("scheduled_date") or "")
    allowed_dates = {
        current.date().isoformat(),
        (current.date() + timedelta(days=1)).isoformat(),
    }
    if scheduled_date not in allowed_dates:
        raise ValueError("primary task must be scheduled for today or tomorrow")
    state = _load_state(output_root)
    selected = state["primary_tasks"].get(scheduled_date)
    clear = bool(payload.get("clear")) or (
        isinstance(selected, dict) and selected.get("task_id") == task_id
    )
    if clear:
        state["primary_tasks"].pop(scheduled_date, None)
    else:
        state["primary_tasks"][scheduled_date] = {
            "task_id": task_id,
            "title": str(task.get("title") or ""),
            "set_at": current.isoformat(timespec="seconds"),
        }
    state["revision"] += 1
    state["updated_at"] = current.isoformat(timespec="seconds")
    _save_state(output_root, state)
    return effective_state(
        context_path, output_root, timezone_name=timezone_name, now=current
    )


def enqueue_mutation(
    context_path: Path,
    output_root: Path,
    payload: dict[str, Any],
    *,
    timezone_name: str = "Asia/Shanghai",
    now: datetime | None = None,
) -> dict[str, Any]:
    current = now or _now(timezone_name)
    operation = str(payload.get("operation", ""))
    if operation not in {"create", "update", "postpone", "complete", "complete_occurrence", "delete", "advance_tomatoes"}:
        raise ValueError("unsupported task operation")
    task_id = str(payload.get("task_id", ""))
    if not TASK_ID_RE.fullmatch(task_id):
        raise ValueError("task_id must be an Obsidian block ID")
    client_request_id = str(payload.get("request_id") or "")
    if client_request_id and not CLIENT_REQUEST_ID_RE.fullmatch(client_request_id):
        raise ValueError("request_id must be 8-120 safe characters")
    state = _load_state(output_root)
    if client_request_id:
        previous = state["request_history"].get(client_request_id)
        if isinstance(previous, dict) and isinstance(previous.get("mutation"), dict):
            return {
                "mutation": previous["mutation"],
                "effective": effective_state(
                    context_path, output_root, timezone_name=timezone_name, now=current
                ),
                "idempotent_replay": True,
            }
    changes = _clean_changes(payload, creating=operation == "create") if operation not in {"complete", "complete_occurrence", "delete", "advance_tomatoes"} else {}
    current_effective = effective_state(context_path, output_root, timezone_name=timezone_name, now=current)
    current_tasks = {
        task["task_id"]: task
        for group in current_effective["tasks"].values()
        for task in group
    }
    if operation == "create" and task_id in current_tasks:
        raise ValueError("task_id already exists")
    occurrence_date = current.date().isoformat()
    existing_completion = next((item for item in state["completions"]
                                if item.get("completion_key") == _completion_key(task_id, occurrence_date)), None)
    if operation in {"complete", "complete_occurrence"} and existing_completion:
        return {"completion": existing_completion,
                "effective": effective_state(context_path, output_root, timezone_name=timezone_name, now=current)}
    if operation in {"update", "postpone", "complete", "complete_occurrence", "delete"} and task_id not in current_tasks:
        raise ValueError("task_id does not exist in the effective task view")
    task = current_tasks.get(task_id)
    postponed_days = 0
    if operation == "postpone":
        if set(changes) != {"scheduled_date"} or not changes.get("scheduled_date"):
            raise ValueError("postpone requires only scheduled_date")
        previous_text = str(task.get("scheduled_date") or current.date().isoformat()) if task else ""
        previous_day = date.fromisoformat(previous_text)
        next_day = date.fromisoformat(changes["scheduled_date"])
        postponed_days = (next_day - previous_day).days
        if postponed_days <= 0:
            raise ValueError("postpone must move the task to a later date")
    if operation == "complete" and task and task.get("recurrence"):
        operation = "complete_occurrence"
    if operation == "complete_occurrence":
        if not task or not task.get("recurrence") or task.get("scheduled_date") != occurrence_date:
            raise ValueError("only today's recurring occurrence can be completed")
        next_date = _next_weekly_occurrence(task.get("recurrence"), current.date()).isoformat()
        changes = {"scheduled_date": next_date, "tomatoes_completed": 0}
    if operation in {"complete", "complete_occurrence"} and task:
        completion = {
            "completion_key": _completion_key(task_id, occurrence_date), "task_id": task_id,
            "occurrence_date": occurrence_date, "completed_at": current.isoformat(timespec="seconds"),
            "recurring": operation == "complete_occurrence", "task": dict(task),
        }
        state["completions"].append(completion)
        state["postponements"].pop(task_id, None)
    elif operation == "delete":
        state["postponements"].pop(task_id, None)
    elif operation == "postpone":
        record = state["postponements"].get(task_id)
        if not isinstance(record, dict):
            record = {"postponed_days": 0, "postpone_count": 0}
        record["postponed_days"] = max(0, int(record.get("postponed_days", 0) or 0)) + postponed_days
        record["postpone_count"] = max(0, int(record.get("postpone_count", 0) or 0)) + 1
        record["last_postponed_at"] = current.isoformat(timespec="seconds")
        record["current_scheduled_date"] = changes["scheduled_date"]
        state["postponements"][task_id] = record
    if operation == "advance_tomatoes":
        target = _clean_tomato(payload.get("target_completed"))
        settlement_id = str(payload.get("settlement_id", ""))
        if target is None:
            raise ValueError("target_completed is required")
        if not re.fullmatch(r"[A-Za-z0-9-]{8,80}", settlement_id):
            raise ValueError("settlement_id must be a stable focus session ID")
        task = current_tasks.get(task_id)
        if not task:
            raise ValueError("task_id does not exist in the effective task view")
        total = task.get("tomatoes_total")
        if not isinstance(total, int) or total <= 0:
            raise ValueError("task must have a positive tomato estimate")
        target = min(target, total)
        for existing in state["mutations"]:
            if (existing.get("operation") == "advance_tomatoes"
                    and existing.get("payload", {}).get("settlement_id") == settlement_id):
                return {"mutation": existing, "effective": effective_state(context_path, output_root, timezone_name=timezone_name, now=current)}
        changes = {"target_completed": target, "settlement_id": settlement_id}
    queued_operation = "update" if operation in {"complete_occurrence", "postpone"} else operation
    mutation = {
        "mutation_id": uuid.uuid4().hex,
        "operation": queued_operation,
        "task_id": task_id,
        "payload": changes,
        "created_at": current.isoformat(timespec="seconds"),
        "base_snapshot_sha256": _snapshot_hash(context_path),
    }
    if client_request_id:
        mutation["client_request_id"] = client_request_id
    if operation in {"complete", "complete_occurrence"}:
        completion["mutation_id"] = mutation["mutation_id"]
    state["mutations"].append(mutation)
    if client_request_id:
        state["request_history"][client_request_id] = {
            "mutation": mutation,
            "status": "queued",
            "created_at": mutation["created_at"],
        }
        if len(state["request_history"]) > 500:
            oldest = sorted(
                state["request_history"],
                key=lambda key: str(state["request_history"][key].get("created_at", "")),
            )[: len(state["request_history"]) - 500]
            for key in oldest:
                state["request_history"].pop(key, None)
    state["revision"] += 1
    state["updated_at"] = mutation["created_at"]
    _save_state(output_root, state)
    result = {"mutation": mutation, "effective": effective_state(context_path, output_root, timezone_name=timezone_name, now=current)}
    if operation in {"complete", "complete_occurrence"}:
        result["completion"] = completion
    return result


def acknowledge_mutations(
    context_path: Path,
    output_root: Path,
    payload: dict[str, Any],
    *,
    timezone_name: str = "Asia/Shanghai",
) -> dict[str, Any]:
    expected_hash = str(payload.get("snapshot_sha256", ""))
    actual_hash = _snapshot_hash(context_path)
    if not expected_hash or expected_hash != actual_hash:
        raise ValueError("Pi has not received the expected exported snapshot")
    mutation_ids = payload.get("mutation_ids")
    if not isinstance(mutation_ids, list) or not all(isinstance(item, str) for item in mutation_ids):
        raise ValueError("mutation_ids must be a list of strings")
    selected = set(mutation_ids)
    state = _load_state(output_root)
    snapshot = _read_json(context_path)
    snapshot_tasks = _snapshot_tasks(snapshot, _now(timezone_name).date())
    selected_mutations = [
        item for item in state["mutations"] if item.get("mutation_id") in selected
    ]
    requirements: dict[str, dict[str, Any]] = {}
    for mutation in selected_mutations:
        operation = mutation.get("operation")
        task_id = mutation.get("task_id")
        mutation_payload = mutation.get("payload", {})
        if not isinstance(task_id, str) or not isinstance(mutation_payload, dict):
            raise ValueError("exported snapshot does not reflect selected task mutations")
        if operation == "create":
            requirements[task_id] = {
                "exists": True, "fields": dict(mutation_payload), "tomatoes_completed": None,
            }
        elif operation == "update":
            requirement = requirements.setdefault(
                task_id, {"exists": True, "fields": {}, "tomatoes_completed": None}
            )
            requirement["exists"] = True
            requirement["fields"].update(mutation_payload)
        elif operation in {"complete", "delete"}:
            requirements[task_id] = {
                "exists": False, "fields": {}, "tomatoes_completed": None,
            }
        elif operation == "advance_tomatoes":
            target = mutation_payload.get("target_completed")
            requirement = requirements.setdefault(
                task_id, {"exists": True, "fields": {}, "tomatoes_completed": None}
            )
            previous = requirement.get("tomatoes_completed")
            requirement["exists"] = True
            requirement["tomatoes_completed"] = max(previous or 0, target) if isinstance(target, int) else None
        else:
            raise ValueError("exported snapshot does not reflect selected task mutations")
    for task_id, requirement in requirements.items():
        task = snapshot_tasks.get(task_id)
        if not requirement["exists"]:
            reflected = task is None
        else:
            reflected = task is not None and all(
                task.get(key) == value for key, value in requirement["fields"].items()
            )
            target = requirement.get("tomatoes_completed")
            if target is not None:
                completed = task.get("tomatoes_completed") if task else None
                reflected = reflected and isinstance(completed, int) and completed >= target
        if not reflected:
            raise ValueError("exported snapshot does not reflect selected task mutations")
    before = len(state["mutations"])
    state["mutations"] = [item for item in state["mutations"] if item.get("mutation_id") not in selected]
    acknowledged = before - len(state["mutations"])
    if acknowledged:
        for record in state.get("request_history", {}).values():
            if not isinstance(record, dict):
                continue
            mutation = record.get("mutation")
            if isinstance(mutation, dict) and mutation.get("mutation_id") in selected:
                record["status"] = "acknowledged"
                record["acknowledged_at"] = _now(timezone_name).isoformat(timespec="seconds")
        state["revision"] += 1
        state["updated_at"] = _now(timezone_name).isoformat(timespec="seconds")
        _save_state(output_root, state)
    return {"acknowledged": acknowledged, "effective": effective_state(context_path, output_root, timezone_name=timezone_name)}
