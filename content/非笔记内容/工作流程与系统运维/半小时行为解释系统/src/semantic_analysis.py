from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from common import parse_timestamp, rounded_minutes
from deepseek_client import _request_json_report


ACTIVITIES = {
    "work",
    "entertainment",
    "brief_communication",
    "rest",
    "other",
    "uncertain",
}
WORK_CATEGORIES = {"数学学习", "家教", "系统维护", "其他工作", ""}
RELATIONSHIPS = {
    "same_work_task",
    "supporting_work",
    "brief_communication",
    "entertainment_detour",
    "task_transition",
    "standalone_activity",
    "confirmed_rest",
    "uncertain",
}
CONFIDENCE_LEVELS = {"high", "medium", "low"}


def _parse_segment_time(value: Any, timezone_name: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError("时间必须是ISO 8601字符串")
    return parse_timestamp(value, timezone_name)


def _validate_semantic_timeline(
    result: dict[str, Any],
    period_start: datetime,
    period_end: datetime,
    timezone_name: str,
    confirmed_rest_minutes: float,
    confirmed_rest_intervals: list[dict[str, Any]],
) -> list[str]:
    errors: list[str] = []
    segments = result.get("segments")
    if not isinstance(segments, list) or not segments:
        return ["segments必须是非空数组"]

    parsed: list[tuple[datetime, datetime, dict[str, Any]]] = []
    for index, segment in enumerate(segments):
        if not isinstance(segment, dict):
            errors.append(f"segments[{index}]不是对象")
            continue
        try:
            start = _parse_segment_time(segment.get("start"), timezone_name)
            end = _parse_segment_time(segment.get("end"), timezone_name)
        except ValueError as error:
            errors.append(f"segments[{index}]时间错误：{error}")
            continue
        if end <= start:
            errors.append(f"segments[{index}]结束时间不晚于开始时间")
        if start < period_start or end > period_end:
            errors.append(f"segments[{index}]超出报告时段")
        if segment.get("activity") not in ACTIVITIES:
            errors.append(f"segments[{index}].activity不在允许列表中")
        work_category = segment.get("work_category", "")
        if work_category not in WORK_CATEGORIES:
            errors.append(f"segments[{index}].work_category不在允许列表中")
        if segment.get("activity") == "work" and not work_category:
            errors.append(f"segments[{index}]为工作但没有work_category")
        if segment.get("activity") != "work" and work_category:
            errors.append(f"segments[{index}]非工作却设置了work_category")
        if segment.get("relationship_to_work") not in RELATIONSHIPS:
            errors.append(
                f"segments[{index}].relationship_to_work不在允许列表中"
            )
        if segment.get("confidence") not in CONFIDENCE_LEVELS:
            errors.append(f"segments[{index}].confidence不在允许列表中")
        if not isinstance(segment.get("evidence", []), list):
            errors.append(f"segments[{index}].evidence必须是数组")
        parsed.append((start, end, segment))

    if not parsed:
        return errors or ["没有可解析的时间段"]
    parsed.sort(key=lambda item: item[0])
    tolerance_seconds = 1.0
    if abs((parsed[0][0] - period_start).total_seconds()) > tolerance_seconds:
        errors.append("时间线没有从报告时段起点开始")
    if abs((parsed[-1][1] - period_end).total_seconds()) > tolerance_seconds:
        errors.append("时间线没有覆盖到报告时段终点")
    for previous, current in zip(parsed, parsed[1:]):
        difference = (current[0] - previous[1]).total_seconds()
        if difference > tolerance_seconds:
            errors.append(f"时间线存在{round(difference, 1)}秒空白")
        elif difference < -tolerance_seconds:
            errors.append(f"时间线存在{round(-difference, 1)}秒重叠")

    rest_seconds = sum(
        (end - start).total_seconds()
        for start, end, segment in parsed
        if segment.get("activity") == "rest"
    )
    if abs(rounded_minutes(rest_seconds) - confirmed_rest_minutes) > 0.2:
        errors.append("AI时间线中的休息分钟数不等于确定性休息规则结果")
    actual_rest = [
        (start, end)
        for start, end, segment in parsed
        if segment.get("activity") == "rest"
    ]
    expected_rest = [
        (
            parse_timestamp(item["start"], timezone_name),
            parse_timestamp(item["end"], timezone_name),
        )
        for item in confirmed_rest_intervals
    ]
    if len(actual_rest) != len(expected_rest):
        errors.append("AI时间线中的休息区间数量与确定性休息区间不一致")
    else:
        for actual, expected in zip(actual_rest, expected_rest):
            if (
                abs((actual[0] - expected[0]).total_seconds()) > 1
                or abs((actual[1] - expected[1]).total_seconds()) > 1
            ):
                errors.append("AI时间线中的休息区间位置与确定性休息区间不一致")
                break
    return errors


def _normalize_semantic_timeline(
    result: dict[str, Any],
    period_start: datetime,
    period_end: datetime,
    timezone_name: str,
) -> dict[str, Any]:
    normalized: list[dict[str, Any]] = []
    segments = sorted(
        result["segments"],
        key=lambda item: _parse_segment_time(item["start"], timezone_name),
    )
    previous_end = period_start
    for index, segment in enumerate(segments):
        start = _parse_segment_time(segment["start"], timezone_name)
        end = _parse_segment_time(segment["end"], timezone_name)
        if index == 0 and abs((start - period_start).total_seconds()) <= 1:
            start = period_start
        if abs((start - previous_end).total_seconds()) <= 1:
            start = previous_end
        if index == len(segments) - 1 and abs(
            (end - period_end).total_seconds()
        ) <= 1:
            end = period_end
        item = {
            "start": start.isoformat(timespec="seconds"),
            "end": end.isoformat(timespec="seconds"),
            "duration_seconds": round((end - start).total_seconds(), 3),
            "activity": segment["activity"],
            "work_category": segment.get("work_category", ""),
            "task": str(segment.get("task", "")).strip(),
            "relationship_to_work": segment["relationship_to_work"],
            "devices": [
                device
                for device in segment.get("devices", [])
                if device in {"computer", "phone", "tablet"}
            ],
            "evidence": [str(item) for item in segment.get("evidence", [])[:4]],
            "confidence": segment["confidence"],
        }
        previous_end = end
        if (
            normalized
            and normalized[-1]["end"] == item["start"]
            and all(
                normalized[-1].get(key) == item.get(key)
                for key in (
                    "activity",
                    "work_category",
                    "task",
                    "relationship_to_work",
                    "confidence",
                )
            )
        ):
            normalized[-1]["end"] = item["end"]
            normalized[-1]["duration_seconds"] = round(
                normalized[-1]["duration_seconds"] + item["duration_seconds"], 3
            )
            normalized[-1]["devices"] = sorted(
                set(normalized[-1]["devices"] + item["devices"])
            )
            normalized[-1]["evidence"] = list(
                dict.fromkeys(normalized[-1]["evidence"] + item["evidence"])
            )[:4]
        else:
            normalized.append(item)

    return {
        "schema_version": 1,
        "source": "deepseek_semantic_timeline",
        "period": {
            "start": period_start.isoformat(timespec="seconds"),
            "end": period_end.isoformat(timespec="seconds"),
        },
        "primary_work_task": str(result.get("primary_work_task", "")).strip(),
        "segments": normalized,
        "material_uncertainties": [
            str(item) for item in result.get("material_uncertainties", [])[:2]
        ],
    }


def extract_semantic_timeline_with_deepseek(
    settings: dict[str, Any],
    prompt_path: Path,
    computer_facts: dict[str, Any],
    phone_facts: dict[str, Any],
    cross_device_facts: dict[str, Any],
    context_computer_facts: dict[str, Any],
    context_phone_facts: dict[str, Any],
) -> dict[str, Any]:
    timezone_name = settings["timezone"]
    period_start = parse_timestamp(computer_facts["period"]["start"], timezone_name)
    period_end = parse_timestamp(computer_facts["period"]["end"], timezone_name)
    confirmed_rest_minutes = float(
        cross_device_facts["time_accounting_observed"]["confirmed_rest_minutes"]
    )
    confirmed_rest_intervals = cross_device_facts.get("rest_rule", {}).get(
        "confirmed_intervals", []
    )
    evidence = {
        "report_period": computer_facts["period"],
        "report_period_computer_facts": computer_facts,
        "report_period_phone_facts": phone_facts,
        "report_period_cross_device_facts": cross_device_facts,
        "auxiliary_context_only": {
            "note": "前后上下文只辅助判断时段边界，不计入本次30分钟。",
            "computer_facts": context_computer_facts,
            "phone_facts": context_phone_facts,
        },
    }
    messages = [
        {
            "role": "system",
            "content": prompt_path.read_text(encoding="utf-8"),
        },
        {
            "role": "user",
            "content": "请把报告时段解释成无重叠、无空白的语义时间段JSON：\n"
            + json.dumps(evidence, ensure_ascii=False, separators=(",", ":")),
        },
    ]

    generation: dict[str, Any] = {}
    errors: list[str] = []
    result: dict[str, Any] = {}
    correction_attempts = 0
    segment_model = {
        **settings["model"],
        **settings.get("semantic_model", {}),
    }
    for correction_attempts in range(3):
        result, generation = _request_json_report(segment_model, messages)
        errors = _validate_semantic_timeline(
            result,
            period_start,
            period_end,
            timezone_name,
            confirmed_rest_minutes,
            confirmed_rest_intervals,
        )
        if not errors:
            break
        messages.extend(
            [
                {
                    "role": "assistant",
                    "content": json.dumps(result, ensure_ascii=False),
                },
                {
                    "role": "user",
                    "content": (
                        "上一个JSON没有通过时间线校验。请保持行为判断尽量不变，"
                        "修正以下问题并返回完整JSON：\n- "
                        + "\n- ".join(errors)
                    ),
                },
            ]
        )

    if errors:
        return {
            "schema_version": 1,
            "source": "deepseek_semantic_timeline",
            "period": computer_facts["period"],
            "primary_work_task": "",
            "segments": [],
            "material_uncertainties": ["AI未能生成通过一致性检查的时间线。"],
            "_validation": {
                "passed": False,
                "errors": errors,
                "correction_attempts": correction_attempts,
            },
            "_generation": generation,
        }

    normalized = _normalize_semantic_timeline(
        result, period_start, period_end, timezone_name
    )
    normalized["_validation"] = {
        "passed": True,
        "errors": [],
        "correction_attempts": correction_attempts,
    }
    normalized["_generation"] = generation
    return normalized


def _nearest_activity(
    segments: list[dict[str, Any]], index: int, direction: int
) -> str | None:
    cursor = index + direction
    while 0 <= cursor < len(segments):
        activity = segments[cursor]["activity"]
        if activity in {"work", "entertainment"}:
            return activity
        cursor += direction
    return None


def _return_latency_seconds(
    segments: list[dict[str, Any]], index: int, timezone_name: str
) -> float | None:
    entertainment_end = parse_timestamp(segments[index]["end"], timezone_name)
    for following in segments[index + 1 :]:
        if following["activity"] == "work":
            return max(
                0.0,
                (
                    parse_timestamp(following["start"], timezone_name)
                    - entertainment_end
                ).total_seconds(),
            )
        if following["activity"] == "entertainment":
            continue
    return None


def _longest_work_continuity_seconds(
    segments: list[dict[str, Any]],
) -> float:
    longest = 0.0
    index = 0
    while index < len(segments):
        if segments[index].get("activity") != "work":
            index += 1
            continue
        start_index = index
        end_index = index
        task = str(segments[index].get("task", "")).strip()
        cursor = index + 1
        while cursor + 1 < len(segments):
            bridge = segments[cursor]
            next_work = segments[cursor + 1]
            if (
                bridge.get("activity") == "brief_communication"
                and next_work.get("activity") == "work"
                and (
                    not task
                    or not str(next_work.get("task", "")).strip()
                    or str(next_work.get("task", "")).strip() == task
                )
            ):
                end_index = cursor + 1
                cursor += 2
                continue
            break
        duration = sum(
            float(item.get("duration_seconds", 0))
            for item in segments[start_index : end_index + 1]
        )
        longest = max(longest, duration)
        index = end_index + 1
    return longest


def calculate_work_entertainment_mixing(
    semantic_timeline: dict[str, Any],
    cross_device_facts: dict[str, Any],
    settings: dict[str, Any],
) -> dict[str, Any]:
    threshold_seconds = float(
        settings.get("state_rules", {}).get(
            "entertainment_deviation_minimum_seconds", 30
        )
    )
    timezone_name = settings["timezone"]
    segments = semantic_timeline.get("segments", [])
    deviations: list[dict[str, Any]] = []
    for index, segment in enumerate(segments):
        if segment.get("activity") != "entertainment":
            continue
        duration = float(segment.get("duration_seconds", 0))
        if duration <= threshold_seconds:
            continue
        before = _nearest_activity(segments, index, -1)
        after = _nearest_activity(segments, index, 1)
        is_detour = (
            segment.get("relationship_to_work") == "entertainment_detour"
            or (before == "work" and after == "work")
        )
        if not is_detour:
            continue
        latency = _return_latency_seconds(segments, index, timezone_name)
        deviations.append(
            {
                "start": segment["start"],
                "end": segment["end"],
                "minutes": rounded_minutes(duration),
                "duration_seconds": duration,
                "task": segment.get("task", ""),
                "evidence": segment.get("evidence", []),
                "returned_to_work": latency is not None,
                "return_latency_minutes": rounded_minutes(latency)
                if latency is not None
                else None,
                "confidence": segment.get("confidence", "low"),
            }
        )

    all_entertainment_seconds = sum(
        float(segment.get("duration_seconds", 0))
        for segment in segments
        if segment.get("activity") == "entertainment"
    )
    detour_seconds = sum(item["duration_seconds"] for item in deviations)
    count = len(deviations)
    if count == 0:
        level = "none"
    elif detour_seconds > 300 or count >= 4:
        level = "high"
    elif detour_seconds > 120 or count >= 2:
        level = "medium"
    else:
        level = "low"

    compact_work_entertainment = [
        segment["activity"]
        for segment in segments
        if segment["activity"] in {"work", "entertainment"}
    ]
    transitions = sum(
        left != right
        for left, right in zip(
            compact_work_entertainment, compact_work_entertainment[1:]
        )
    )
    work_segments = [
        segment for segment in segments if segment.get("activity") == "work"
    ]
    brief_communication_seconds = sum(
        float(segment.get("duration_seconds", 0))
        for segment in segments
        if segment.get("activity") == "brief_communication"
    )
    longest_work_seconds = _longest_work_continuity_seconds(segments)

    raw_context_blocks = cross_device_facts.get(
        "computer_fragmentation_metrics", {}
    ).get("context_blocks", [])
    same_task_tool_switches = 0
    for work_segment in work_segments:
        work_start = parse_timestamp(work_segment["start"], timezone_name)
        work_end = parse_timestamp(work_segment["end"], timezone_name)
        contained = 0
        for block in raw_context_blocks:
            block_start = parse_timestamp(block["start"], timezone_name)
            block_end = parse_timestamp(block["end"], timezone_name)
            if block_start < work_end and block_end > work_start:
                contained += 1
        same_task_tool_switches += max(0, contained - 1)

    return {
        "schema_version": 1,
        "source": "deterministic_from_ai_semantic_timeline",
        "rule": {
            "entertainment_deviation_minimum_seconds": threshold_seconds,
            "comparison": "strictly_greater_than",
            "brief_communication_is_not_scored": True,
            "same_work_task_tool_switches_are_not_scored": True,
        },
        "level": level,
        "entertainment_deviation_count": count,
        "entertainment_deviation_minutes": rounded_minutes(detour_seconds),
        "all_entertainment_minutes": rounded_minutes(all_entertainment_seconds),
        "longest_entertainment_deviation_minutes": max(
            (item["minutes"] for item in deviations), default=0.0
        ),
        "work_entertainment_transition_count": transitions,
        "brief_communication_minutes": rounded_minutes(
            brief_communication_seconds
        ),
        "longest_continuous_work_minutes": rounded_minutes(longest_work_seconds),
        "same_task_tool_switches_not_scored": same_task_tool_switches,
        "raw_foreground_context_switches_not_scored": cross_device_facts.get(
            "computer_fragmentation_metrics", {}
        ).get("context_switch_count", 0),
        "deviations": deviations,
        "interpretation_note": (
            "等级只反映工作过程中超过30秒的娱乐偏离；"
            "纯娱乐、短暂通信和同任务工具切换不计为混杂。"
        ),
    }
