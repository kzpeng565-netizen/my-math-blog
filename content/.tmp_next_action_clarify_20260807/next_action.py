from __future__ import annotations

import argparse
import copy
import json
import os
import re
import uuid
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from common import atomic_write_json, load_json
from deepseek_client import _request_json_report
from obsidian_context import load_obsidian_context
from recent_context import RecentContextCorruptError, load_notes
from recent_context_selector import select_recent_context
from task_sync import compact_for_next_action, effective_state


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SETTINGS = PROJECT_ROOT / "config" / "settings.json"
DEFAULT_ENV = Path("/home/conrad/.config/activitywatch-advisor/env")
DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / "data"
PROMPT_VERSION = "next-action-v1.3"
POMODORO_MINUTES = 40
CLARIFICATION_MAX_ROUNDS = 2
ALLOWED_DECISIONS = {"task", "break", "exercise", "sleep", "clarify", "no_action"}
RESPONSE_RESULTS = {
    "accepted",
    "alternative_requested",
    "declined",
    "issue_reported",
}
OUTCOME_RESULTS = {"completed", "still_doing", "stopped", "not_started", "unknown"}
REJECTION_REASONS = {
    "environment_inconvenient",
    "wrong_priority",
    "too_tired",
    "too_difficult_or_large",
    "first_step_unclear",
    "task_already_done",
    "already_doing_something_else",
    "stale_data",
    "other",
}


def _now(timezone_name: str) -> datetime:
    return datetime.now(ZoneInfo(timezone_name))


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return {}


def _load_env_file(path: Path) -> None:
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            key, value = stripped.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))
    except OSError:
        return


def _latest_paths(root: Path, limit: int) -> list[Path]:
    return sorted((path for path in root.glob("*/*.json") if path.is_file()))[-limit:]


def _compact_report(report: dict[str, Any]) -> dict[str, Any]:
    mixing = report.get("mixing_assessment", {})
    allocation = report.get("estimated_time_allocation", {})
    return {
        "period": report.get("period"),
        "main_task": report.get("main_task") or report.get("primary_work_task"),
        "estimated_time_allocation": allocation,
        "final_state": report.get("final_state") or report.get("state_label"),
        "mixing_level": mixing.get("level"),
        "entertainment_deviation_minutes": mixing.get(
            "entertainment_deviation_minutes"
        ),
        "longest_continuous_work_minutes": mixing.get(
            "longest_continuous_work_minutes"
        ),
        "material_uncertainties": report.get("material_uncertainties", [])[:3],
    }


def _today_reports(output_root: Path, today: date) -> list[dict[str, Any]]:
    reports = []
    for path in sorted((output_root / "ai_reports" / today.isoformat()).glob("*.json")):
        item = _read_json(path)
        if item:
            reports.append(item)
    return reports


def _sum_allocation(reports: list[dict[str, Any]]) -> dict[str, float]:
    totals = {
        "work": 0.0,
        "entertainment": 0.0,
        "brief_communication": 0.0,
        "rest": 0.0,
        "uncertain": 0.0,
    }
    for report in reports:
        allocation = report.get("estimated_time_allocation", {})
        if not isinstance(allocation, dict):
            continue
        for key in totals:
            try:
                totals[key] += float(allocation.get(key, {}).get("estimate_minutes", 0))
            except (AttributeError, TypeError, ValueError):
                continue
    return {key: round(value, 2) for key, value in totals.items()}


def _task_titles(context: dict[str, Any] | None) -> list[str]:
    if not context:
        return []
    tasks = context.get("tasks", {})
    titles = []
    for bucket in ("overdue", "today", "near_term"):
        for task in tasks.get(bucket, []) if isinstance(tasks, dict) else []:
            title = str(task.get("title", "")).strip()
            if title and title not in titles:
                titles.append(title)
    return titles


def _recent_next_action_history(output_root: Path, limit: int = 6) -> list[dict[str, Any]]:
    items = []
    for path in _latest_paths(output_root / "next_action" / "responses", limit):
        item = _read_json(path)
        if item:
            items.append(
                {
                    "suggestion_id": item.get("suggestion_id"),
                    "result": item.get("result"),
                    "reason_code": item.get("reason_code"),
                    "detail": str(item.get("detail", ""))[:160],
                    "received_at": item.get("received_at"),
                }
            )
    return items


def _suggestion_records(
    output_root: Path, record_type: str, suggestion_id: str
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in sorted(
        (output_root / "next_action" / record_type).glob("*/*.json")
    ):
        item = _read_json(path)
        if item.get("suggestion_id") == suggestion_id:
            records.append(item)
    return records


def pending_active_suggestion(output_root: Path) -> dict[str, Any] | None:
    """Return the active suggestion when it still needs an explicit outcome."""
    active = _read_json(output_root / "next_action" / "active.json")
    suggestion_id = str(active.get("suggestion_id", "")).strip()
    if not suggestion_id:
        return None
    if _suggestion_records(output_root, "outcomes", suggestion_id):
        return None
    responses = _suggestion_records(output_root, "responses", suggestion_id)
    if responses and responses[-1].get("result") in {
        "alternative_requested",
        "declined",
    }:
        return None
    return active


def _parse_datetime(value: Any, timezone_name: str) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=ZoneInfo(timezone_name))
    return parsed.astimezone(ZoneInfo(timezone_name))


def _age_minutes(value: Any, current: datetime, timezone_name: str) -> float | None:
    parsed = _parse_datetime(value, timezone_name)
    if parsed is None:
        return None
    return round(max(0.0, (current - parsed).total_seconds() / 60), 2)


def _obsidian_sync_quality(
    context: dict[str, Any],
    context_path: Path,
    current: datetime,
    timezone_name: str,
) -> dict[str, Any]:
    heartbeat = _read_json(context_path.parent / "sync_heartbeat.json")
    generated_at = context.get("generated_at") if context.get("available") else None
    return {
        "obsidian_context_source": context.get("context_source"),
        "obsidian_snapshot_generated_at": generated_at,
        "obsidian_snapshot_content_age_minutes": _age_minutes(
            generated_at, current, timezone_name
        ),
        "obsidian_sync_last_checked_at": heartbeat.get("last_checked_at"),
        "obsidian_sync_checked_age_minutes": _age_minutes(
            heartbeat.get("last_checked_at"), current, timezone_name
        ),
        "obsidian_last_successful_export_at": heartbeat.get(
            "last_successful_export_at"
        ),
        "obsidian_last_successful_export_age_minutes": _age_minutes(
            heartbeat.get("last_successful_export_at"), current, timezone_name
        ),
        "obsidian_source_changed_at_last_check": heartbeat.get("source_changed"),
        "obsidian_sync_status": heartbeat.get("status"),
        "obsidian_context_age_note": (
            "snapshot_content_age may be high when the Obsidian source files "
            "have not changed; use sync_checked_age to judge exporter freshness"
        ),
    }


def build_decision_state(
    settings: dict[str, Any], output_root: Path, now: datetime | None = None
) -> dict[str, Any]:
    timezone_name = settings.get("timezone", "Asia/Shanghai")
    current = now or _now(timezone_name)
    context_path = Path(
        settings.get(
            "obsidian_context_path",
            "/home/conrad/workspace/behavior-context-sync/context_snapshot.json",
        )
    )
    context = load_obsidian_context(
        context_path,
        output_root / "context_cache" / "current.json",
        current,
    )
    ai_context = context.get("ai_context") if context.get("available") else None
    effective_tasks = compact_for_next_action(
        effective_state(
            context_path,
            output_root,
            timezone_name=timezone_name,
            now=current,
        )
    )
    ai_context = {**ai_context, **effective_tasks} if isinstance(ai_context, dict) else effective_tasks
    recent_reports = [
        _compact_report(_read_json(path))
        for path in _latest_paths(output_root / "ai_reports", 4)
    ]
    today_reports = _today_reports(output_root, current.date())
    daily_life = _read_json(
        output_root
        / "statistics"
        / "daily_life"
        / f"{(current.date() - timedelta(days=1)).isoformat()}.json"
    )
    state = {
        "schema_version": 1,
        "generated_at": current.isoformat(timespec="seconds"),
        "request_type": "next_action",
        "request_context": {
            "initiated_by_user": True,
            "interactive_web_request": True,
            "user_is_awake_for_decision_purposes": True,
            "evidence_note": (
                "The user deliberately clicked the web button to request a "
                "suggestion. Treat this as direct evidence that the user is "
                "awake and currently able to interact; never ask whether the "
                "user has gotten up or is awake."
            ),
        },
        "time_context": {
            "current_timestamp": current.isoformat(timespec="seconds"),
            "current_date": current.date().isoformat(),
            "current_time": current.strftime("%H:%M"),
            "current_weekday": current.strftime("%A"),
            "timezone": timezone_name,
            "utc_offset": current.strftime("%z"),
            "day_period": _day_period(current),
            "routine_context": _routine_context(current),
        },
        "data_quality": {
            **_obsidian_sync_quality(context, context_path, current, timezone_name),
            "task_sync_revision": effective_tasks["task_sync"]["revision"],
            "task_sync_pending_mutation_count": effective_tasks["task_sync"][
                "pending_mutation_count"
            ],
            "latest_report_count": len(recent_reports),
        },
        "recent_reports": recent_reports,
        "today_totals_from_half_hour_reports": _sum_allocation(today_reports),
        "sleep": daily_life.get("phone_sleep_boundary", {}),
        "obsidian_context": ai_context,
        "task_titles": _task_titles(ai_context),
        "recent_next_action_history": _recent_next_action_history(output_root),
        "hard_rules": {
            "one_action_only": True,
            "work_actions_must_match_task_titles": True,
            "user_request_implies_awake": (
                "The user actively clicked Generate suggestion, so the user "
                "is awake for this decision. Never use clarify to ask whether "
                "the user is awake or has gotten up."
            ),
            "pomodoro_minutes": POMODORO_MINUTES,
            "pomodoro_unit_rule": (
                "In this system, 1 tomato / 1 Pomodoro / 1 🍅 is exactly "
                "40 minutes, not 25. Do not call a 5/10/15/25/30-minute "
                "starter action one tomato."
            ),
            "allowed_durations_minutes": settings.get("next_action", {}).get(
                "allowed_durations_minutes", [5, 10, 15, 25, 40]
            ),
            "lunch_rest_rule": "12:00-13:00 is daily lunch and midday rest; do not recommend work/study tasks in this window unless the user explicitly overrides this rule",
            "pomodoro_role": "medium reliability positive evidence; 1 tomato equals 40 minutes; tomato counts are estimated task budgets/progress markers, not guarantees that the remaining work fits the remaining tomatoes; missing logs are not negative evidence",
            "obsidian_freshness_rule": "do not treat old snapshot_content_age as stale when sync_checked_age is fresh and source_changed_at_last_check is false",
            "persuasion_style": "warm, concrete, psychologically realistic, and moderately close; avoid moralizing, hype, flattery, guilt, or generic productivity slogans; persuade the user to start the smallest useful action, not to conquer the whole task",
        },
    }
    return state


def _attach_recent_context(
    state: dict[str, Any],
    settings: dict[str, Any],
    output_root: Path,
) -> None:
    """Coarse-filter, then (if enabled) AI-select recent context and attach it.

    Any data-processing failure (corrupt store, missing API key, timeout,
    invalid JSON) must never break Next Action: it degrades to an empty
    recent_context and marks fallback_used.
    """
    empty_selection = {
        "candidate_ids": [],
        "forced_ids": [],
        "selected_ids": [],
        "fallback_used": False,
    }
    cfg = settings.get("recent_context", {})
    if not cfg.get("enabled", True):
        state["recent_context"] = []
        state["recent_context_selection"] = empty_selection
        return
    try:
        current = datetime.fromisoformat(str(state["generated_at"]))
    except ValueError:
        current = _now(settings.get("timezone", "Asia/Shanghai"))
    try:
        notes = load_notes(output_root)
    except RecentContextCorruptError:
        state["recent_context"] = []
        state["recent_context_selection"] = empty_selection
        state.setdefault("data_quality", {})["recent_context_state"] = "corrupt"
        return
    except Exception:
        state["recent_context"] = []
        state["recent_context_selection"] = empty_selection
        return
    try:
        result = select_recent_context(
            notes,
            state.get("obsidian_context", {}),
            current,
            settings,
        )
    except Exception:
        result = {"items": [], "selection": empty_selection}
    state["recent_context"] = result["items"]
    state["recent_context_selection"] = result["selection"]

def _day_period(current: datetime) -> str:
    hour = current.hour
    if hour < 5:
        return "late_night"
    if hour < 11:
        return "morning"
    if hour < 18:
        return "afternoon"
    if hour < 23:
        return "evening"
    return "late_night"


def _routine_context(current: datetime) -> str:
    if current.hour == 12:
        return "lunch_rest"
    return "normal"


def _system_prompt() -> str:
    return (
        "你是一个个人下一步行动决策器。只输出 JSON 对象。\n"
        "目标不是聊天，而是在用户主动询问时给出一个足够具体、足够有说服力的下一步。\n"
        "你必须只推荐一个行动。工作/学习类行动必须来自 task_titles 或 obsidian_context.tasks。\n"
        "新鲜度规则：obsidian_snapshot_content_age_minutes 很高并不一定表示同步过期；当 obsidian_sync_checked_age_minutes 很小且 source_changed_at_last_check=false 时，只能说明源文件近期未变化。\n"
        "允许的 decision_type: task, break, exercise, sleep, clarify, no_action。\n"
        "允许的 duration_minutes 只能从输入 allowed_durations_minutes 中选择。\n"
        "番茄钟单位硬规则：在这个系统里 1 个番茄钟 / 1 🍅 / 1 Pomodoro = 40 分钟，不是 25 分钟。"
        "如果建议时长是 5、10、15 或 25 分钟，只能称为启动片段、小块、缩小版，不能称为一个番茄钟。\n"
        "输出字段: decision_type, title, duration_minutes, first_step, task_title, reason_short, "
        "evidence_points, persuasive_explanation, anticipated_resistance, reduced_version, confidence, decision_trace。\n"
        "reason_short 不超过80字。persuasive_explanation 需要解释为什么现在做这件事值得，"
        "可以稍微丰富，但不要写成鸡汤或长篇规划。evidence_points 是2到4条基于数据的依据。\n"
        "anticipated_resistance 写用户可能不想开始的真实阻力；reduced_version 写阻力大时的更小版本。\n"
        "decision_trace 只写可审计摘要，不写隐藏思维链；允许字段为 evidence_used, rules_applied, excluded_options, data_quality_notes, recent_context_used。\n"
        "decision_trace.recent_context_used 只能引用输入 recent_context 中真实存在的 id 列表；不得自造 id，不得改写动态原文。\n"
        "字段内容不要使用 Markdown 语法，不要写 # 标题、Markdown 表格或 - 列表；可以少量使用 emoji，但总量控制在2到3个。\n"
        "不要把情绪推断当事实。缺关键数据且会改变建议时才用 clarify。"
        "本次请求由用户主动点击网页按钮触发，这本身就是用户已经醒来且能交互的直接证据；"
        "绝对不要询问用户是否起床、是否醒来或是否还在睡。"
    )


def _system_prompt_recent_context_addendum() -> str:
    return (
        "Recent context (近期动态) rules:\n"
        "1. recent_context 是用户近期主动记录的生活安排，已由系统按记录时间做过时间过滤；"
        "不要重新计算任何相对日期（今天/明天/本周），不要改写 content 或 impact。\n"
        "2. 判断每条动态如何影响此刻的行动选择：直接冲突、需要为近期事件准备、或取决于未确认条件。\n"
        "3. 对 status=conditional 的记录保持保守：事件是否已发生未确认，只能作为条件性提醒。\n"
        "4. 只使用 recent_context_selection.selected_ids/forced_ids 中列出的记录；"
        "不要在 evidence_points 里虚构没有传入的动态。\n"
        "5. 若使用了某条动态，必须在 decision_trace.recent_context_used 中列出其 id；"
        "页面会按 id 反查用户原文展示。\n"
        "6. 已结束、已归档或未被系统选中的动态不存在于输入中，不得提及。"
    )


def _system_prompt_v11_addendum() -> str:
    return (
        "Next Action v1.1 rules:\n"
        "1. Use warm, concrete Chinese with moderate closeness. Sound like a familiar assistant who understands the user's rhythm, not a lecturer, slogan writer, or therapist.\n"
        "2. Persuasion should reduce resistance: acknowledge the likely friction, make the first step feel small, and explain the concrete near-term benefit. Avoid guilt, moral judgment, exaggerated encouragement, flattery, and generic phrases such as '掌控感' or '闭合感' unless grounded in a specific fact.\n"
        "3. The goal is to persuade the user to start the smallest useful action, not to finish a whole large task. If a task title is broad, make first_step and reduced_version narrow, physical, and startable within 5-10 minutes.\n"
        "4. 12:00-13:00 is the user's daily lunch and midday rest window. During this period, recommend eating, leaving screens, napping, or light recovery; do not recommend math/project work unless the user explicitly overrides this rule.\n"
        "5. Pomodoro unit rule: in this user's system, 1 tomato / 1 Pomodoro / 1 🍅 = exactly 40 minutes, not 25 minutes. If duration_minutes is 5, 10, 15, or 25, call it a starter slice or reduced version, never one Pomodoro.\n"
        "6. Pomodoro is medium-reliability positive evidence. Tomato counts are estimated budgets/progress markers; actual work can exceed the estimate. Never claim that remaining tomatoes guarantee completion. Prefer wording like '记录显示接近收尾' or '预估还剩约1个番茄（约40分钟预算）'.\n"
        "7. Do not present inferences as facts. If using schedule-like information from Obsidian notes, phrase it conservatively unless it is current and explicit.\n"
        "8. If decision_trace is included, keep it short and auditable. Do not reveal private chain-of-thought, scratchpad reasoning, or hidden deliberation. Summarize only the observable evidence, hard rules, and rejected option categories.\n"
        "9. Do not use Markdown formatting in user-facing fields. No Markdown headings, tables, bold markers, or hyphen lists. A small number of emoji is allowed, but keep it restrained.\n"
    )


def _call_model(settings: dict[str, Any], state: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    model = {**settings["model"], **settings.get("decision_model", {})}
    messages = [
        {"role": "system", "content": _system_prompt()},
        {"role": "system", "content": _system_prompt_v11_addendum()},
        {"role": "system", "content": _system_prompt_recent_context_addendum()},
        {
            "role": "user",
            "content": json.dumps(state, ensure_ascii=False, separators=(",", ":")),
        },
    ]
    return _request_json_report(model, messages)


def _clarification_prompt() -> str:
    return (
        "You refine one existing Next Action after the user describes a real obstacle. "
        "Return JSON only: {assistant_message:string, action:object}. action must contain "
        "the normal Next Action fields: decision_type, title, duration_minutes, first_step, "
        "task_title, reason_short, evidence_points, persuasive_explanation, "
        "anticipated_resistance, reduced_version, confidence.\n"
        "Rules: speak concise, warm Chinese; make only one directly startable action; do not "
        "create or edit tasks, schedules, Pomodoros, or garden records; task actions must use "
        "only a listed task title; obey the supplied hard rules. This is a clarification, not "
        "an acceptance. Do not claim the user has started. Do not ask a new question."
    )


def _clarification_model(settings: dict[str, Any]) -> dict[str, Any]:
    """Use the same deliberative model as the initial Next Action decision."""
    return {**settings["model"], **settings.get("decision_model", {})}


def _call_clarification_model(
    settings: dict[str, Any], payload: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    messages = [
        {"role": "system", "content": _clarification_prompt()},
        {"role": "user", "content": json.dumps(payload, ensure_ascii=False, separators=(",", ":"))},
    ]
    return _request_json_report(_clarification_model(settings), messages)


def _clean_text(value: Any, limit: int) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()[:limit]


def _clean_list(value: Any, limit: int = 4, text_limit: int = 180) -> list[str]:
    if not isinstance(value, list):
        return []
    return [_clean_text(item, text_limit) for item in value[:limit] if _clean_text(item, text_limit)]


def _model_for_trace(settings: dict[str, Any]) -> dict[str, Any]:
    model = {**settings.get("model", {}), **settings.get("decision_model", {})}
    return {
        "provider": "DeepSeek",
        "model": model.get("name", "unknown"),
        "thinking": model.get("thinking", "disabled"),
        "full_reasoning_saved": False,
    }


def _data_quality_notes(state: dict[str, Any]) -> list[str]:
    notes: list[str] = []
    quality = state.get("data_quality", {})
    sync_age = quality.get("obsidian_sync_checked_age_minutes")
    content_age = quality.get("obsidian_snapshot_content_age_minutes")
    source_changed = quality.get("obsidian_source_changed_at_last_check")
    if (
        isinstance(sync_age, (int, float))
        and sync_age <= 30
        and isinstance(content_age, (int, float))
        and content_age > 120
        and source_changed is False
    ):
        notes.append(
            "Obsidian sync was checked recently; old snapshot content age likely means source files did not change."
        )
    if state.get("obsidian_context", {}).get("pomodoro"):
        notes.append(
            "Pomodoro counts are medium-reliability positive evidence and estimated progress markers, not completion guarantees; 1 tomato equals 40 minutes, not 25."
        )
    return notes[:4]


def _rules_applied(suggestion: dict[str, Any], state: dict[str, Any]) -> list[str]:
    rules = ["one_action_only"]
    if suggestion.get("decision_type") == "task":
        rules.append("work_actions_must_match_task_titles")
    if state.get("time_context", {}).get("routine_context") == "lunch_rest":
        rules.append("12:00-13:00_lunch_rest_no_work_task")
    if state.get("data_quality"):
        rules.append("do_not_treat_freshly_checked_unchanged_obsidian_snapshot_as_stale")
    return rules[:6]


def _excluded_options(suggestion: dict[str, Any], state: dict[str, Any]) -> list[str]:
    excluded: list[str] = []
    if state.get("time_context", {}).get("routine_context") == "lunch_rest":
        excluded.append("study_or_project_task_during_lunch_rest_window")
    if suggestion.get("decision_type") == "task":
        excluded.append("new_work_tasks_not_present_in_today_task_titles")
    if state.get("exclude_suggestion_id"):
        excluded.append("previous_suggestion_requested_as_alternative")
    return excluded[:4]


def _build_decision_trace(
    suggestion: dict[str, Any],
    state: dict[str, Any],
    settings: dict[str, Any] | None = None,
    *,
    source: str,
) -> dict[str, Any]:
    settings = settings or {}
    model_trace = _model_for_trace(settings) if settings else {"full_reasoning_saved": False}
    model_trace["source"] = source
    return {
        "trace_type": "auditable_summary_not_chain_of_thought",
        "evidence_used": _clean_list(suggestion.get("evidence_points"), 4, 180),
        "rules_applied": _rules_applied(suggestion, state),
        "excluded_options": _excluded_options(suggestion, state),
        "data_quality_notes": _data_quality_notes(state),
        "recent_context_used": _clean_recent_context_used(suggestion, state),
        "model": model_trace,
    }


def _clean_recent_context_used(
    suggestion: dict[str, Any], state: dict[str, Any]
) -> list[str]:
    """Return only IDs the model could legitimately reference.

    Allowed IDs are the forced/selected IDs passed to the model; fabricated
    IDs are silently dropped (audit field, never a decision field).
    """
    selection = state.get("recent_context_selection", {})
    allowed = set(selection.get("forced_ids", [])) | set(selection.get("selected_ids", []))
    trace = suggestion.get("decision_trace")
    raw = trace.get("recent_context_used") if isinstance(trace, dict) else None
    if not isinstance(raw, list):
        return []
    used: list[str] = []
    seen: set[str] = set()
    for item in raw:
        note_id = str(item or "").strip()
        if note_id in allowed and note_id not in seen:
            seen.add(note_id)
            used.append(note_id)
    return used


def _validate_suggestion(
    suggestion: dict[str, Any], state: dict[str, Any], settings: dict[str, Any], *, source: str = "model"
) -> dict[str, Any]:
    decision_type = str(suggestion.get("decision_type", "")).strip()
    if decision_type not in ALLOWED_DECISIONS:
        raise ValueError("invalid decision_type")
    allowed = settings.get("next_action", {}).get(
        "allowed_durations_minutes", [5, 10, 15, 25, 40]
    )
    try:
        duration = int(suggestion.get("duration_minutes", allowed[0]))
    except (TypeError, ValueError):
        duration = allowed[0]
    if duration not in allowed:
        raise ValueError("invalid duration_minutes")
    task_title = _clean_text(suggestion.get("task_title"), 160)
    routine_context = state.get("time_context", {}).get("routine_context")
    if routine_context == "lunch_rest" and decision_type == "task":
        raise ValueError("task action is not allowed during lunch_rest")
    if decision_type == "task" and task_title not in state.get("task_titles", []):
        raise ValueError("task action must match a known task")
    evidence = suggestion.get("evidence_points", [])
    if not isinstance(evidence, list):
        evidence = []
    normalized = {
        "suggestion_id": make_suggestion_id(),
        "prompt_version": PROMPT_VERSION,
        "created_at": state["generated_at"],
        "decision_type": decision_type,
        "title": _clean_text(suggestion.get("title"), 80),
        "duration_minutes": duration,
        "first_step": _clean_text(suggestion.get("first_step"), 140),
        "task_title": task_title,
        "reason_short": _clean_text(suggestion.get("reason_short"), 120),
        "evidence_points": [_clean_text(item, 160) for item in evidence[:4]],
        "persuasive_explanation": _clean_text(
            suggestion.get("persuasive_explanation"),
            settings.get("next_action", {}).get("rationale_max_characters", 900),
        ),
        "anticipated_resistance": _clean_text(
            suggestion.get("anticipated_resistance"), 220
        ),
        "reduced_version": _clean_text(suggestion.get("reduced_version"), 220),
        "confidence": float(suggestion.get("confidence", 0.5) or 0.5),
    }
    if not normalized["title"] or not normalized["first_step"]:
        raise ValueError("title and first_step are required")
    _reject_awake_clarification(normalized, state)
    _reject_pomodoro_unit_confusion(normalized)
    normalized["decision_trace"] = _build_decision_trace(
        normalized, state, settings, source=source
    )
    # Keep only IDs the model could legitimately reference from the raw output.
    raw_trace = suggestion.get("decision_trace")
    raw_used = raw_trace.get("recent_context_used") if isinstance(raw_trace, dict) else None
    normalized["decision_trace"]["recent_context_used"] = _clean_recent_context_used(
        {"decision_trace": {"recent_context_used": raw_used}}, state
    )
    normalized["display_text"] = display_text(normalized)
    return normalized


def _reject_awake_clarification(
    suggestion: dict[str, Any], state: dict[str, Any]
) -> None:
    if not state.get("request_context", {}).get(
        "user_is_awake_for_decision_purposes"
    ):
        return
    if suggestion.get("decision_type") != "clarify":
        return
    user_text = " ".join(
        str(suggestion.get(key, ""))
        for key in (
            "title",
            "first_step",
            "reason_short",
            "persuasive_explanation",
            "anticipated_resistance",
            "reduced_version",
        )
    )
    if re.search(r"起床|醒来|醒着|睡醒|还在睡|是否醒|有没有醒|awake", user_text, re.I):
        raise ValueError(
            "awake clarification is invalid for a user-initiated web request"
        )


def _reject_pomodoro_unit_confusion(suggestion: dict[str, Any]) -> None:
    user_text = " ".join(
        str(suggestion.get(key, ""))
        for key in (
            "title",
            "first_step",
            "reason_short",
            "persuasive_explanation",
            "anticipated_resistance",
            "reduced_version",
        )
    )
    user_text += " " + " ".join(
        str(item) for item in suggestion.get("evidence_points", [])
    )
    mentions_single_tomato = re.search(
        r"(?:1\s*个|1\s*颗|一\s*个|一\s*颗|最后\s*1\s*个|最后\s*一\s*个|1\s*🍅).*?(?:番茄|🍅)"
        r"|(?:番茄|🍅).*?(?:1\s*个|1\s*颗|一\s*个|一\s*颗|最后\s*1\s*个|最后\s*一\s*个)",
        user_text,
    )
    mentions_wrong_duration = re.search(
        r"(?:15|25|30)\s*分钟|半小时|半个小时",
        user_text,
    )
    explicitly_correct = re.search(r"40\s*分钟|约\s*40|四十\s*分钟", user_text)
    if mentions_single_tomato and mentions_wrong_duration and not explicitly_correct:
        raise ValueError("pomodoro unit confusion: 1 tomato must be treated as 40 minutes")
    if (
        mentions_single_tomato
        and suggestion.get("duration_minutes") != POMODORO_MINUTES
        and not explicitly_correct
    ):
        raise ValueError("pomodoro unit missing: single tomato references must state about 40 minutes")


def make_suggestion_id() -> str:
    return datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:8]


def fallback_suggestion(
    state: dict[str, Any], settings: dict[str, Any] | None = None
) -> dict[str, Any]:
    day_period = state.get("time_context", {}).get("day_period")
    routine_context = state.get("time_context", {}).get("routine_context")
    titles = state.get("task_titles", [])
    if routine_context == "lunch_rest":
        result = {
            "suggestion_id": make_suggestion_id(),
            "prompt_version": PROMPT_VERSION,
            "created_at": state["generated_at"],
            "decision_type": "break",
            "title": "吃饭并离屏休息",
            "duration_minutes": 40,
            "first_step": "先离开电脑，把吃饭这件事安排好，不在屏幕前继续比较任务。",
            "task_title": "",
            "reason_short": "现在是12:00-13:00固定吃饭和午休窗口，不适合启动数学或项目工作。",
            "evidence_points": [
                "当前处于 lunch_rest 例行时段。",
                "午间恢复优先级高于继续压榨一个工作块。",
            ],
            "persuasive_explanation": "这不是放弃上午的主线，而是在保护下午的可用精力。现在强行开一个任务，很容易变成一边饿着一边拖延；先吃饭、离屏、让脑子降下来，下午再回来会更稳。",
            "anticipated_resistance": "可能会觉得还有一点时间，想趁热再补一小块。",
            "reduced_version": "只做第一步：站起来离开屏幕，先去吃饭。",
            "confidence": 0.7,
        }
    elif day_period == "late_night":
        result = {
            "suggestion_id": make_suggestion_id(),
            "prompt_version": PROMPT_VERSION,
            "created_at": state["generated_at"],
            "decision_type": "sleep",
            "title": "停止继续展开任务，准备睡觉",
            "duration_minutes": 10,
            "first_step": "先把当前娱乐或网页关掉，去洗漱。",
            "task_title": "",
            "reason_short": "现在处于深夜时段，继续启动学习任务的收益较低。",
            "evidence_points": ["当前时间属于 late_night。"],
            "persuasive_explanation": "这一步的价值不在于今天多完成一点，而是避免把明天的清醒度继续透支。现在把收尾动作做完，比再比较几个选择更容易保护明天的主线。",
            "anticipated_resistance": "你可能会觉得还没有真正开始做事，所以不甘心直接结束。",
            "reduced_version": "只做第一步：关掉当前页面并站起来。",
            "confidence": 0.55,
        }
    else:
        task = titles[0] if titles else ""
        result = {
            "suggestion_id": make_suggestion_id(),
            "prompt_version": PROMPT_VERSION,
            "created_at": state["generated_at"],
            "decision_type": "task" if task else "break",
            "title": f"先推进：{task}" if task else "离开屏幕整理状态",
            "duration_minutes": 10,
            "first_step": "打开对应任务材料，只处理最小的下一步。" if task else "离开屏幕走动并喝水。",
            "task_title": task,
            "reason_short": "模型暂时不可用，使用任务列表和当前时段给出保守建议。",
            "evidence_points": ["用户主动请求下一步建议。", "当天任务列表可作为主要候选。"],
            "persuasive_explanation": "现在最重要的是终止犹豫，而不是得到完美建议。先用10分钟碰一下主线任务，成本小，但能迅速让系统和你自己都获得新的行动证据。",
            "anticipated_resistance": "你可能担心这个任务太大，打开以后会被拖进去。",
            "reduced_version": "只打开材料并读第一小段，5分钟也算完成启动。",
            "confidence": 0.45,
        }
    result["decision_trace"] = _build_decision_trace(
        result, state, settings, source="fallback"
    )
    result["display_text"] = display_text(result)
    return result


def display_text(suggestion: dict[str, Any]) -> str:
    evidence = "\n".join(f"• {item}" for item in suggestion.get("evidence_points", []))
    return (
        f"🎯 现在做：{suggestion['title']}\n\n"
        f"⏱ 时长：{suggestion['duration_minutes']}分钟\n"
        f"第一步：{suggestion['first_step']}\n\n"
        f"为什么是这个：{suggestion.get('reason_short', '')}\n"
        f"{suggestion.get('persuasive_explanation', '')}\n\n"
        f"依据：\n{evidence}\n\n"
        f"如果不想做：{suggestion.get('reduced_version', '')}"
    ).strip()


def _source_task_id(suggestion: dict[str, Any], state: dict[str, Any]) -> str | None:
    target = str(suggestion.get("task_title", "")).strip()
    context = state.get("obsidian_context", {})
    tasks = context.get("tasks", {}) if isinstance(context, dict) else {}
    if not target or not isinstance(tasks, dict):
        return None
    for bucket in ("overdue", "today", "near_term", "later", "recurring"):
        for task in tasks.get(bucket, []):
            if isinstance(task, dict) and task.get("title") == target:
                task_id = task.get("task_id")
                return task_id if isinstance(task_id, str) else None
    return None


def generate_next_action(
    settings: dict[str, Any],
    output_root: Path,
    *,
    env_file: Path = DEFAULT_ENV,
    exclude_suggestion_id: str | None = None,
) -> dict[str, Any]:
    state = build_decision_state(settings, output_root)
    if exclude_suggestion_id:
        state["exclude_suggestion_id"] = exclude_suggestion_id
    _attach_recent_context(state, settings, output_root)
    state_id = state["generated_at"].replace(":", "").replace("+", "_") + "-" + uuid.uuid4().hex[:6]
    state_path = output_root / "next_action" / "state_snapshots" / f"{state_id}.json"
    atomic_write_json(state_path, state)
    _load_env_file(env_file)
    generation: dict[str, Any] = {}
    try:
        raw, generation = _call_model(settings, state)
        suggestion = _validate_suggestion(raw, state, settings)
    except Exception as error:
        suggestion = fallback_suggestion(state, settings)
        suggestion["model_error"] = f"{type(error).__name__}: {error}"
    suggestion["state_snapshot"] = str(state_path)
    task_sync = state.get("obsidian_context", {}).get("task_sync", {})
    suggestion["task_revision"] = task_sync.get("revision") if isinstance(task_sync, dict) else None
    suggestion["source_task_id"] = _source_task_id(suggestion, state)
    suggestion["action_id"] = suggestion["suggestion_id"]
    suggestion["action_revision"] = 0
    suggestion["clarification"] = {"max_rounds": CLARIFICATION_MAX_ROUNDS, "rounds": []}
    if generation:
        suggestion["_generation"] = generation
    day = datetime.fromisoformat(state["generated_at"]).date().isoformat()
    suggestion_path = (
        output_root
        / "next_action"
        / "suggestions"
        / day
        / f"{suggestion['suggestion_id']}.json"
    )
    atomic_write_json(suggestion_path, suggestion)
    atomic_write_json(output_root / "next_action" / "active.json", suggestion)
    return suggestion


def _active_suggestion(output_root: Path, suggestion_id: str) -> dict[str, Any]:
    active = _read_json(output_root / "next_action" / "active.json")
    if not active or active.get("suggestion_id") != suggestion_id:
        raise KeyError("active suggestion not found")
    return active


def _action_view(suggestion: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "action_id", "action_revision", "decision_type", "title", "duration_minutes",
        "first_step", "task_title", "reason_short", "evidence_points",
        "persuasive_explanation", "anticipated_resistance", "reduced_version", "confidence",
    )
    return {key: copy.deepcopy(suggestion.get(key)) for key in keys}


def clarify_next_action(
    settings: dict[str, Any],
    output_root: Path,
    suggestion_id: str,
    message: str,
    expected_action_revision: int | str | None,
    *,
    env_file: Path = DEFAULT_ENV,
) -> dict[str, Any]:
    """Create at most two revised actions; acceptance always targets the newest revision."""
    active = _active_suggestion(output_root, suggestion_id)
    if any(
        item.get("result") == "accepted"
        for item in _suggestion_records(output_root, "responses", suggestion_id)
    ):
        raise ValueError("action already accepted; record an outcome before requesting another suggestion")
    clarification = active.get("clarification")
    if not isinstance(clarification, dict):
        clarification = {"max_rounds": CLARIFICATION_MAX_ROUNDS, "rounds": []}
    rounds = clarification.get("rounds")
    if not isinstance(rounds, list):
        rounds = []
    max_rounds = min(CLARIFICATION_MAX_ROUNDS, max(0, int(clarification.get("max_rounds", CLARIFICATION_MAX_ROUNDS))))
    if len(rounds) >= max_rounds:
        raise ValueError("clarification round limit reached")
    try:
        expected = int(expected_action_revision)
    except (TypeError, ValueError):
        raise ValueError("expected_action_revision is required")
    current_revision = int(active.get("action_revision", 0) or 0)
    if expected != current_revision:
        raise ValueError("action revision conflict; reload the latest action")
    user_message = _clean_text(message, 600)
    if not user_message:
        raise ValueError("clarification message is required")

    state = build_decision_state(settings, output_root)
    _attach_recent_context(state, settings, output_root)
    payload = {
        "request_type": "next_action_clarification",
        "round": len(rounds) + 1,
        "round_limit": max_rounds,
        "user_message": user_message,
        "current_action": _action_view(active),
        "original_action": _action_view(rounds[0].get("original_action", active)) if rounds else _action_view(active),
        "decision_state": state,
    }
    _load_env_file(env_file)
    raw, generation = _call_clarification_model(settings, payload)
    raw_action = raw.get("action") if isinstance(raw.get("action"), dict) else raw
    revised = _validate_suggestion(raw_action, state, settings, source="clarification_decision_model")
    clarification_model = _clarification_model(settings)
    revised["decision_trace"]["model"] = {
        "provider": "DeepSeek",
        "model": clarification_model.get("name", "unknown"),
        "thinking": clarification_model.get("thinking", "enabled"),
        "full_reasoning_saved": False,
        "source": "clarification_decision_model",
    }
    assistant_message = _clean_text(raw.get("assistant_message"), 280)
    if not assistant_message:
        assistant_message = "我把这一步按你刚才的阻力缩小了；上面这一版就是现在可以接受并开始的最后行动。"

    updated = dict(active)
    for key, value in revised.items():
        if key not in {"suggestion_id", "created_at", "prompt_version"}:
            updated[key] = value
    updated["action_id"] = revised["suggestion_id"]
    updated["action_revision"] = current_revision + 1
    updated["updated_at"] = state["generated_at"]
    updated["source_task_id"] = _source_task_id(updated, state)
    updated["task_revision"] = state.get("obsidian_context", {}).get("task_sync", {}).get("revision")
    updated["clarification"] = {
        "max_rounds": max_rounds,
        "rounds": rounds + [{
            "round": len(rounds) + 1,
            "at": state["generated_at"],
            "user_message": user_message,
            "assistant_message": assistant_message,
            "action_id": revised["suggestion_id"],
            "action_revision": current_revision + 1,
            "original_action": _action_view(active) if not rounds else rounds[0].get("original_action", _action_view(active)),
            "generation": generation,
        }],
    }
    updated["display_text"] = display_text(updated)
    day = datetime.fromisoformat(state["generated_at"]).date().isoformat()
    record_path = output_root / "next_action" / "clarifications" / day / f"{suggestion_id}-r{updated['action_revision']}.json"
    atomic_write_json(record_path, updated)
    atomic_write_json(output_root / "next_action" / "active.json", updated)
    return updated


def save_response(
    output_root: Path,
    suggestion_id: str,
    result: str,
    *,
    reason_code: str = "other",
    detail: str = "",
    expected_action_revision: int | str | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    if result not in RESPONSE_RESULTS:
        raise ValueError("invalid response result")
    if reason_code not in REJECTION_REASONS:
        reason_code = "other"
    current = now or datetime.now(ZoneInfo("Asia/Shanghai"))
    record = {
        "suggestion_id": suggestion_id,
        "result": result,
        "reason_code": reason_code,
        "detail": _clean_text(detail, 500),
        "received_at": current.isoformat(timespec="seconds"),
    }
    if result == "accepted":
        active = _active_suggestion(output_root, suggestion_id)
        try:
            expected = int(expected_action_revision)
        except (TypeError, ValueError):
            raise ValueError("expected_action_revision is required when accepting")
        current_revision = int(active.get("action_revision", 0) or 0)
        if expected != current_revision:
            raise ValueError("action revision conflict; reload the latest action")
        record["accepted_action_id"] = str(active.get("action_id") or suggestion_id)
        record["accepted_action_revision"] = current_revision
        record["clarification_rounds"] = len(active.get("clarification", {}).get("rounds", []))
        active["accepted_action_id"] = record["accepted_action_id"]
        active["accepted_action_revision"] = current_revision
        active["accepted_at"] = record["received_at"]
        atomic_write_json(output_root / "next_action" / "active.json", active)
    target = output_root / "next_action" / "responses" / current.date().isoformat() / f"{suggestion_id}-{result}.json"
    atomic_write_json(target, record)
    return record


def save_outcome(
    output_root: Path,
    suggestion_id: str,
    result: str,
    *,
    detail: str = "",
    now: datetime | None = None,
) -> dict[str, Any]:
    if result not in OUTCOME_RESULTS:
        raise ValueError("invalid outcome result")
    current = now or datetime.now(ZoneInfo("Asia/Shanghai"))
    record = {
        "suggestion_id": suggestion_id,
        "result": result,
        "detail": _clean_text(detail, 500),
        "received_at": current.isoformat(timespec="seconds"),
    }
    target = output_root / "next_action" / "outcomes" / current.date().isoformat() / f"{suggestion_id}-{result}.json"
    atomic_write_json(target, record)
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate an on-demand next-action suggestion.")
    parser.add_argument("--settings", type=Path, default=DEFAULT_SETTINGS)
    parser.add_argument("--output-root", type=Path)
    parser.add_argument("--env-file", type=Path, default=DEFAULT_ENV)
    args = parser.parse_args()
    settings = load_json(args.settings)
    output_root = args.output_root or Path(settings.get("output_root", DEFAULT_OUTPUT_ROOT))
    result = generate_next_action(settings, output_root, env_file=args.env_file)
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
