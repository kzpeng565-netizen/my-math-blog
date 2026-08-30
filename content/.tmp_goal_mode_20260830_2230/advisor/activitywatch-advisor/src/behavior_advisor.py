from __future__ import annotations

from datetime import datetime
from typing import Any


ENTERTAINMENT_MARKERS = (
    "zhihu",
    "知乎",
    "bilibili",
    "哔哩哔哩",
    "xiaohongshu",
    "小红书",
    "douyin",
    "抖音",
)


def _entertainment_minutes(semantic: dict[str, Any]) -> float:
    return round(
        sum(
            float(segment.get("duration_seconds", 0)) / 60
            for segment in semantic.get("segments", [])
            if segment.get("activity") == "entertainment"
            and any(
                marker in str(segment).lower() for marker in ENTERTAINMENT_MARKERS
            )
        ),
        2,
    )


def _recommended_task(context: dict[str, Any]) -> dict[str, Any] | None:
    if not context.get("available"):
        return None
    ai_context = context.get("ai_context") or {}
    tasks = ai_context.get("tasks", {})
    for bucket in ("overdue", "today", "near_term"):
        values = tasks.get(bucket, [])
        if values:
            return values[0]
    return None


def build_shadow_candidate(
    settings: dict[str, Any],
    period_end: datetime,
    semantic: dict[str, Any],
    mixing: dict[str, Any],
    cross: dict[str, Any],
    context: dict[str, Any],
    recent_candidates: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    advisor = settings.get("behavior_advisor", {})
    stimulation = _entertainment_minutes(semantic)
    active = float(
        cross.get("time_accounting_observed", {}).get(
            "computer_not_afk_minutes", 0
        )
    ) + float(
        cross.get("time_accounting_observed", {}).get("phone_screen_on_minutes", 0)
    )
    meaningful = sum(
        float(segment.get("duration_seconds", 0)) / 60
        for segment in semantic.get("segments", [])
        if segment.get("activity") == "work"
    )
    confirmed_rest = float(
        cross.get("time_accounting_observed", {}).get(
            "confirmed_rest_minutes", 0
        )
    )
    confirmed_rest_exemption_minutes = float(
        advisor.get("confirmed_rest_exemption_minutes", 12)
    )
    has_explicit_rest = confirmed_rest > confirmed_rest_exemption_minutes
    reasons: list[str] = []
    high_stimulation_threshold = float(
        advisor.get("high_stimulation_minutes_threshold", 10)
    )
    transition_count = int(mixing.get("work_entertainment_transition_count", 0))
    qualified_transition_count = int(mixing.get("qualified_work_entertainment_transition_count", 0))
    entertainment_deviation_count = int(
        mixing.get("entertainment_deviation_count", 0)
    )
    has_work_entertainment_alternation = bool(
        qualified_transition_count
        >= int(
            advisor.get("work_entertainment_transition_threshold", 2)
        )
        and entertainment_deviation_count > 0
    )
    if stimulation > high_stimulation_threshold:
        reasons.append("high_stimulation")
    late_cutoff = str(advisor.get("late_night_cutoff", "00:30"))
    cutoff_hour, cutoff_minute = (int(part) for part in late_cutoff.split(":"))
    is_late = (period_end.hour, period_end.minute) >= (cutoff_hour, cutoff_minute) and period_end.hour < 6
    if is_late and stimulation > 0:
        reasons.append("late_night_entertainment")
    if has_work_entertainment_alternation:
        reasons.append("work_entertainment_alternation")
    task = _recommended_task(context)
    stale_context = context.get("context_source") == "last_known_good"
    should_intervene = bool(
        advisor.get("enabled", True)
        and reasons
        and not has_explicit_rest
    )
    if stale_context:
        task = None
    return {
        "schema_version": 1,
        "shadow_mode": bool(advisor.get("shadow_mode", True)),
        "would_intervene": should_intervene,
        "push_sent": False,
        "trigger_reasons": reasons,
        "observations": {
            "high_stimulation_minutes": stimulation,
            "active_device_minutes": round(active, 2),
            "meaningful_minutes": round(meaningful, 2),
            "confirmed_rest_minutes": confirmed_rest,
            "confirmed_rest_exemption_minutes": confirmed_rest_exemption_minutes,
            "has_explicit_rest": has_explicit_rest,
            "work_entertainment_transition_count": transition_count,
            "qualified_work_entertainment_transition_count": qualified_transition_count,
            "entertainment_deviation_count": entertainment_deviation_count,
            "has_work_entertainment_alternation": has_work_entertainment_alternation,
            "pomodoro_used_as_trigger": False,
        },
        "recommended_task": task,
        "context_source": context.get("context_source", "unavailable"),
        "context_age_minutes": context.get("context_age_minutes"),
        "note": (
            "影子模式只记录候选，不发送干预；番茄钟缺失永不单独触发。"
        ),
    }
