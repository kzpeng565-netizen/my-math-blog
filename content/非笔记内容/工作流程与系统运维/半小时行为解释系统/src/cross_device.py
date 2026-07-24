from __future__ import annotations

from statistics import median
from typing import Any

from common import parse_timestamp, rounded_minutes


def _intervals(
    timeline: list[dict[str, Any]],
    key: str,
    expected: str,
    timezone_name: str,
) -> list[tuple[float, float]]:
    result: list[tuple[float, float]] = []
    for item in timeline:
        if item.get(key) != expected:
            continue
        start = parse_timestamp(item["start"], timezone_name).timestamp()
        end = parse_timestamp(item["end"], timezone_name).timestamp()
        if end > start:
            result.append((start, end))
    return result


def _overlap_seconds(
    left: list[tuple[float, float]], right: list[tuple[float, float]]
) -> float:
    return sum(
        max(0.0, min(left_end, right_end) - max(left_start, right_start))
        for left_start, left_end in left
        for right_start, right_end in right
        if left_start < right_end and left_end > right_start
    )


def _union_seconds(intervals: list[tuple[float, float]]) -> float:
    merged: list[list[float]] = []
    for start, end in sorted(intervals):
        if end <= start:
            continue
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return sum(end - start for start, end in merged)


def _computer_context_metrics(
    timeline: list[dict[str, Any]], timezone_name: str
) -> dict[str, Any]:
    meaningful = [
        item for item in timeline if float(item.get("duration_seconds", 0)) >= 5
    ]
    durations = [float(item["duration_seconds"]) for item in meaningful]
    switch_count = max(0, len(meaningful) - 1)
    active_seconds = sum(durations)
    context_blocks = [
        {
            "start": item["start"],
            "end": item["end"],
            "minutes": rounded_minutes(float(item["duration_seconds"])),
            "app": item.get("app_display", ""),
            "title": item.get("title", ""),
            "domain": item.get("domain", ""),
        }
        for item in meaningful
    ]
    return {
        "minimum_context_seconds": 5,
        "meaningful_context_blocks": len(meaningful),
        "context_switch_count": switch_count,
        "switches_per_active_hour": round(
            switch_count / active_seconds * 3600, 2
        )
        if active_seconds
        else 0.0,
        "short_context_blocks_under_60_seconds": sum(
            duration < 60 for duration in durations
        ),
        "sustained_context_blocks_at_least_5_minutes": sum(
            duration >= 300 for duration in durations
        ),
        "longest_context_minutes": rounded_minutes(max(durations, default=0.0)),
        "median_context_minutes": rounded_minutes(median(durations))
        if durations
        else 0.0,
        "context_blocks": context_blocks,
        "interpretation_note": (
            "这些是前台电脑上下文的客观切换指标；切换次数不直接等于分心。"
        ),
    }


def compare_devices(
    computer: dict[str, Any], phone: dict[str, Any], timezone_name: str
) -> dict[str, Any]:
    computer_active = _intervals(
        computer.get("status_timeline", []), "status", "not-afk", timezone_name
    )
    computer_afk = _intervals(
        computer.get("status_timeline", []), "status", "afk", timezone_name
    )
    phone_on = _intervals(
        phone.get("screen_timeline", []), "state", "on", timezone_name
    )
    phone_off = _intervals(
        phone.get("screen_timeline", []), "state", "off", timezone_name
    )
    period_start = parse_timestamp(computer["period"]["start"], timezone_name)
    period_end = parse_timestamp(computer["period"]["end"], timezone_name)
    period_seconds = (period_end - period_start).total_seconds()
    any_device_interaction_seconds = _union_seconds(computer_active + phone_on)

    return {
        "schema_version": 2,
        "source": "deterministic_cross_device_overlap",
        "period": computer["period"],
        "time_accounting_observed": {
            "period_minutes": rounded_minutes(period_seconds),
            "computer_not_afk_minutes": computer.get("activity", {}).get(
                "not_afk_minutes", 0
            ),
            "computer_afk_minutes": computer.get("activity", {}).get(
                "afk_minutes", 0
            ),
            "phone_screen_on_minutes": phone.get("screen", {}).get(
                "on_minutes", 0
            ),
            "any_device_interaction_minutes": rounded_minutes(
                any_device_interaction_seconds
            ),
            "no_detected_device_interaction_minutes": rounded_minutes(
                max(0.0, period_seconds - any_device_interaction_seconds)
            ),
            "note": (
                "无设备交互不等于休息；它也可能是看视频、阅读、思考或离开。"
            ),
        },
        "computer_fragmentation_metrics": _computer_context_metrics(
            computer.get("timeline", []), timezone_name
        ),
        "overlap_minutes": {
            "computer_not_afk_and_phone_on": rounded_minutes(
                _overlap_seconds(computer_active, phone_on)
            ),
            "computer_afk_and_phone_on": rounded_minutes(
                _overlap_seconds(computer_afk, phone_on)
            ),
            "computer_not_afk_and_phone_off": rounded_minutes(
                _overlap_seconds(computer_active, phone_off)
            ),
            "computer_afk_and_phone_off": rounded_minutes(
                _overlap_seconds(computer_afk, phone_off)
            ),
        },
        "limitations": [
            "这里只计算时间重叠，不推断分心、休息或行为动机。",
            "工作和休息时长由AI结合标题、应用顺序和这些客观指标估计。",
        ],
    }
