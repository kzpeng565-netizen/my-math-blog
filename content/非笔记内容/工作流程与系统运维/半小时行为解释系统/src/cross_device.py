from __future__ import annotations

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

    return {
        "schema_version": 1,
        "source": "deterministic_cross_device_overlap",
        "period": computer["period"],
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
            "任一设备数据质量较低时，跨设备重叠也应降低置信度。",
        ],
    }
