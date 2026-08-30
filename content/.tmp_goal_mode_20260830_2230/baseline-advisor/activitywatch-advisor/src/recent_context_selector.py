"""Auditable two-stage recent-context recall for Next Action.

Code keeps a bounded broad candidate set.  V4 Flash then ranks only the
optional notes using current task metadata.  Active/imminent and critical
health/exam/deadline notes reserve a deterministic part of the final window.
The selector's order and reasons are preserved for the final decision model.
"""

from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from typing import Any

from deepseek_client import _request_json_report
from recent_context import coarse_candidates, recall_importance, _status_for


SELECT_REASONS = {"direct", "preparation", "conditional"}
SELECT_RELEVANCE = {"high", "medium"}
SELECT_IMPORTANCE = {"critical", "high", "normal"}
SELECTOR_PROMPT_VERSION = "recent-context-selector-v2"

SELECTOR_SYSTEM_PROMPT = (
    "你是‘近期动态相关性筛选器’，只输出 JSON，不做行动建议。\n"
    "输入给出 now、三天任务安排、近期动态候选、must_include 标记和 selection_limit。\n"
    "你的任务是为最终的下一步行动保留最少且最相关的可选动态。\n"
    "规则：\n"
    "1. 不要重新计算日期；使用给定的日期、day_offset、temporal_status 和 time。\n"
    "2. 不要改写动态原文或任务标题，不要虚构任务、事件或日期。\n"
    "3. must_include=true 的动态已由系统保留，不要再次放进 selected。\n"
    "4. selected 最多 selection_limit 条，必须按相关性从高到低排列；仅仅较新不是相关理由。\n"
    "5. health/exam/deadline 等 critical 动态必须优先考虑；direct 高于 preparation，"
    "preparation 高于 conditional。\n"
    "6. 每项只含 id、relevance、reason、importance、related_task_ids、summary。"
    "relevance 只能 high/medium；低相关或无关动态必须不选；reason 只能 direct/preparation/conditional；"
    "importance 只能 critical/high/normal；related_task_ids 只能使用输入任务 ID；"
    "summary 不超过60字，只说明其影响，不复述原文。\n"
    "7. 只引用输入 context 中真实且非 must_include 的 id。"
)


def _parse_day(value: Any) -> date | None:
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        return None


def _task_projection(tasks: dict[str, Any], now: datetime) -> list[dict[str, Any]]:
    """Return yesterday overdue plus today/tomorrow/the day after task plan."""
    grouped = tasks.get("tasks", {}) if isinstance(tasks, dict) else tasks
    if not isinstance(grouped, dict):
        return []
    start = now.date() - timedelta(days=1)
    end = now.date() + timedelta(days=2)
    items: list[dict[str, Any]] = []
    seen: set[str] = set()
    for bucket in ("overdue", "today", "near_term", "recurring", "later", "unassigned"):
        for task in grouped.get(bucket, []) or []:
            if not isinstance(task, dict):
                continue
            task_id = str(task.get("task_id") or "").strip()
            title = str(task.get("title") or "").strip()
            scheduled = _parse_day(task.get("scheduled_date"))
            if not task_id or not title or not scheduled or scheduled < start or scheduled > end:
                continue
            if task_id in seen:
                continue
            seen.add(task_id)
            item = {
                "id": task_id,
                "title": title,
                "scheduled_date": scheduled.isoformat(),
                "day_offset": (scheduled - now.date()).days,
                "priority": task.get("priority", "normal"),
                "bucket": bucket,
                "temporal_status": task.get("temporal_status", "all_day"),
                "time_windows": task.get("time_windows", []),
                "recurrence": task.get("recurrence"),
                "recurrence_projected": bool(task.get("recurrence_projected", False)),
                "tomatoes_completed": task.get("tomatoes_completed"),
                "tomatoes_total": task.get("tomatoes_total"),
            }
            items.append(item)
    priority_rank = {"highest": 0, "high": 1, "medium": 2, "normal": 3, "low": 4, "lowest": 5}
    return sorted(
        items,
        key=lambda item: (
            item["day_offset"],
            priority_rank.get(str(item.get("priority")), 3),
            str(item.get("title")),
        ),
    )


def _note_payload(note: dict[str, Any], now: datetime, cfg: dict[str, Any], forced_ids: set[str]) -> dict[str, Any]:
    item: dict[str, Any] = {
        "id": note["id"],
        "text": note["content"],
        "impact": note["impact_text"],
        "status": _status_for(note, now, cfg),
        "importance_floor": note.get("recall_importance") or recall_importance(note),
        "pinned": bool(note.get("pinned", False)),
        "must_include": note["id"] in forced_ids,
    }
    parse = note.get("parse")
    if isinstance(parse, dict) and not parse.get("error"):
        time_info = {key: parse[key] for key in ("date", "part", "start", "end") if parse.get(key)}
        if time_info:
            item["time"] = time_info
    ptype = parse.get("type") if isinstance(parse, dict) else None
    if ptype in ("event", "open", "vague") or (isinstance(parse, dict) and parse.get("error")):
        item["recorded_at"] = note.get("created_at")
    return item


def _selector_model(settings: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any]:
    base = settings.get("model", {})
    model = {
        "endpoint": base.get("endpoint", "https://api.deepseek.com/chat/completions"),
        "name": cfg.get("selector_model", "deepseek-v4-flash"),
        "thinking": "enabled" if cfg.get("selector_thinking", True) else "disabled",
        "max_tokens": int(cfg.get("selector_max_tokens", 800)),
        "timeout_seconds": int(cfg.get("selector_timeout_seconds", 10)),
        "retries": 0,
    }
    if model["thinking"] == "enabled":
        model["reasoning_effort"] = cfg.get("selector_reasoning_effort", "low")
    return model


def _call_selector(
    candidates: list[dict[str, Any]],
    forced_ids: set[str],
    tasks: dict[str, Any],
    now: datetime,
    settings: dict[str, Any],
    cfg: dict[str, Any],
    limit: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    payload = {
        "now": now.isoformat(timespec="seconds"),
        "task_window": {"from": (now.date() - timedelta(days=1)).isoformat(), "to": (now.date() + timedelta(days=2)).isoformat()},
        "tasks": _task_projection(tasks, now),
        "selection_limit": limit,
        "context": [_note_payload(note, now, cfg, forced_ids) for note in candidates],
    }
    model = _selector_model(settings, cfg)
    messages = [
        {"role": "system", "content": SELECTOR_SYSTEM_PROMPT},
        {"role": "user", "content": json.dumps(payload, ensure_ascii=False, separators=(",", ":"))},
    ]
    report, generation = _request_json_report(model, messages)
    selected = report.get("selected", [])
    if not isinstance(selected, list):
        raise ValueError("selector output selected is not a list")
    candidate_ids = {note["id"] for note in candidates} - forced_ids
    task_ids = {item["id"] for item in payload["tasks"]}
    chosen: list[dict[str, Any]] = []
    seen: set[str] = set()
    for raw in selected:
        if not isinstance(raw, dict) or len(chosen) >= limit:
            continue
        note_id = str(raw.get("id", "")).strip()
        reason = str(raw.get("reason", "")).strip()
        relevance = str(raw.get("relevance", "")).strip()
        importance = str(raw.get("importance", "")).strip()
        if note_id not in candidate_ids or note_id in seen or reason not in SELECT_REASONS or relevance not in SELECT_RELEVANCE or importance not in SELECT_IMPORTANCE:
            continue
        related = raw.get("related_task_ids", [])
        if not isinstance(related, list):
            related = []
        chosen.append({
            "id": note_id,
            "reason": reason,
            "relevance": relevance,
            "importance": importance,
            "related_task_ids": [str(item) for item in related if str(item) in task_ids][:4],
            "summary": " ".join(str(raw.get("summary", "")).split())[:60],
            "source": "selector",
        })
        seen.add(note_id)
    return chosen, generation


def _forced_rank(note: dict[str, Any], now: datetime, cfg: dict[str, Any]) -> tuple[int, int, float, int, float]:
    importance_rank = {"critical": 0, "high": 1, "normal": 2}
    status_rank = {"active": 0, "upcoming": 1, "conditional": 2}
    hours = note.get("recall_hours_ahead")
    urgency = float(hours) if isinstance(hours, (int, float)) else float("inf")
    return (
        importance_rank.get(str(note.get("recall_importance") or recall_importance(note)), 2),
        status_rank.get(_status_for(note, now, cfg), 3),
        urgency,
        0 if note.get("pinned", False) else 1,
        -datetime.fromisoformat(str(note.get("created_at", ""))).timestamp(),
    )


def _local_selection(notes: list[dict[str, Any]], now: datetime, cfg: dict[str, Any], limit: int) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    for note in sorted(notes, key=lambda item: _forced_rank(item, now, cfg))[:limit]:
        status = _status_for(note, now, cfg)
        selected.append({
            "id": note["id"],
            "reason": "direct" if status in ("active", "upcoming") else "conditional",
            "relevance": "high" if status == "active" else "medium",
            "importance": note.get("recall_importance") or recall_importance(note),
            "related_task_ids": [],
            "summary": "deterministic fallback selection",
            "source": "fallback",
        })
    return selected


def select_recent_context(
    notes: list[dict[str, Any]],
    effective_tasks: dict[str, Any],
    now: datetime,
    settings: dict[str, Any],
) -> dict[str, Any]:
    cfg = settings.get("recent_context", {})
    output_limit = int(cfg.get("selector_output_limit", 6))
    coarse = coarse_candidates(notes, now, settings)
    candidates = coarse["candidates"]
    candidate_by_id = {note["id"]: note for note in candidates}
    forced_ids = [note_id for note_id in coarse["forced_ids"] if note_id in candidate_by_id]
    forced = sorted((candidate_by_id[note_id] for note_id in forced_ids), key=lambda item: _forced_rank(item, now, cfg))
    kept_forced = forced[:output_limit]
    omitted_forced_ids = [note["id"] for note in forced[output_limit:]]
    kept_forced_ids = {note["id"] for note in kept_forced}
    remaining = max(0, output_limit - len(kept_forced))
    optional = [note for note in candidates if note["id"] not in set(forced_ids)]

    fallback_used = False
    selector_generation: dict[str, Any] = {}
    ranked_optional: list[dict[str, Any]] = []
    if remaining and optional and cfg.get("selector_enabled", True):
        try:
            ranked_optional, selector_generation = _call_selector(
                candidates, set(forced_ids), effective_tasks, now, settings, cfg, remaining
            )
        except Exception:
            fallback_used = True
    elif remaining and optional:
        fallback_used = True
    if fallback_used:
        ranked_optional = _local_selection(optional, now, cfg, remaining)

    final_ranked = [
        {
            "id": note["id"], "reason": "direct", "relevance": "high",
            "importance": note.get("recall_importance") or recall_importance(note),
            "related_task_ids": [], "summary": "system must_include", "source": "forced",
        }
        for note in kept_forced
    ] + ranked_optional[:remaining]
    final_ids = [item["id"] for item in final_ranked]
    items: list[dict[str, Any]] = []
    for rank, entry in enumerate(final_ranked, 1):
        note = candidate_by_id[entry["id"]]
        item: dict[str, Any] = {
            "id": note["id"], "content": note["content"], "impact": note["impact_text"],
            "status": _status_for(note, now, cfg), "rank": rank,
            "selection_reason": entry["reason"], "relevance": entry["relevance"],
            "importance": entry["importance"], "related_task_ids": entry["related_task_ids"],
            "selection_summary": entry["summary"], "selection_source": entry["source"],
        }
        if item["status"] in ("conditional", "needs_review"):
            item["condition"] = "事件状态尚未确认"
        items.append(item)
    model_trace = {
        key: selector_generation.get(key)
        for key in ("provider", "model", "finish_reason", "usage", "request_count")
        if key in selector_generation
    }
    return {
        "items": items,
        "selection": {
            "prompt_version": SELECTOR_PROMPT_VERSION,
            "candidate_ids": [note["id"] for note in candidates],
            "forced_ids": [note["id"] for note in kept_forced],
            "forced_omitted_ids": omitted_forced_ids,
            "selector_ranked": ranked_optional,
            "final_ranked": final_ranked,
            "selected_ids": final_ids,
            "fallback_used": fallback_used,
            "selector_model": {
                "name": cfg.get("selector_model", "deepseek-v4-flash"),
                "thinking": bool(cfg.get("selector_thinking", True)),
                "reasoning_effort_requested": cfg.get("selector_reasoning_effort", "low"),
                "max_tokens": int(cfg.get("selector_max_tokens", 800)),
                "deepseek_effort_note": "DeepSeek maps low/medium reasoning effort to high.",
            },
            "selector_generation": model_trace,
        },
    }
