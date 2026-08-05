from __future__ import annotations

import gzip
import json
from collections import Counter
from datetime import timedelta
from pathlib import Path
from typing import Any

from common import iso_timestamp, merge_timeline, parse_timestamp, rounded_minutes


def _candidate_files(
    archive_root: Path, incoming_root: Path, period_start
) -> list[Path]:
    dates = {
        period_start.date().isoformat(),
        (period_start.date() - timedelta(days=1)).isoformat(),
    }
    files: list[Path] = []
    for date_text in dates:
        day = archive_root / date_text
        if day.exists():
            files.extend(path for path in day.iterdir() if path.is_file())
    if incoming_root.exists():
        files.extend(path for path in incoming_root.iterdir() if path.is_file())
    return sorted(set(files))


def _read_events(
    files: list[Path], timezone_name: str, device_filter: str | None = None
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    events: list[dict[str, Any]] = []
    file_counts: dict[str, int] = {}
    seen: set[tuple[Any, ...]] = set()
    for path in files:
        opener = gzip.open if path.suffix == ".gz" else open
        count = 0
        try:
            with opener(path, "rt", encoding="utf-8") as handle:
                for line in handle:
                    try:
                        raw = json.loads(line)
                        timestamp = parse_timestamp(raw["timestamp"], timezone_name)
                    except (KeyError, ValueError, TypeError, json.JSONDecodeError):
                        continue
                    if device_filter is not None and raw.get("device") != device_filter:
                        continue
                    identity = (
                        raw.get("device"),
                        raw.get("event"),
                        timestamp.isoformat(),
                        raw.get("package"),
                        raw.get("state"),
                    )
                    if identity in seen:
                        continue
                    seen.add(identity)
                    raw["_timestamp"] = timestamp
                    events.append(raw)
                    count += 1
        except OSError:
            continue
        file_counts[str(path)] = count
    events.sort(key=lambda event: event["_timestamp"])
    return events, file_counts


def _latest_before(
    events: list[dict[str, Any]], event_type: str, when
) -> dict[str, Any] | None:
    candidates = [
        event
        for event in events
        if event.get("event") == event_type and event["_timestamp"] <= when
    ]
    return candidates[-1] if candidates else None


def extract_phone_facts(
    settings: dict[str, Any], period_start, period_end, device_filter: str = "phone"
) -> dict[str, Any]:
    timezone_name = settings["timezone"]
    processing = settings["processing"]
    max_segments = int(processing["max_timeline_segments"])
    files = _candidate_files(
        Path(settings["phone_archive_root"]),
        Path(settings["phone_incoming_root"]),
        period_start,
    )
    events, file_counts = _read_events(files, timezone_name, device_filter)
    relevant = [event for event in events if event["_timestamp"] <= period_end]
    in_period = [
        event
        for event in relevant
        if period_start <= event["_timestamp"] < period_end
    ]

    boundaries = {period_start, period_end}
    for event in in_period:
        if event.get("event") in {"screen", "foreground"}:
            boundaries.add(event["_timestamp"])
    ordered = sorted(boundaries)

    screen_timeline: list[dict[str, Any]] = []
    app_timeline: list[dict[str, Any]] = []
    app_seconds: Counter[str] = Counter()
    package_seconds: Counter[str] = Counter()
    app_names = settings.get("phone_app_names", {})

    for left, right in zip(ordered, ordered[1:]):
        duration_seconds = (right - left).total_seconds()
        screen_event = _latest_before(relevant, "screen", left)
        state = str(screen_event.get("state", "unknown")) if screen_event else "unknown"
        screen_timeline.append(
            {
                "start": iso_timestamp(left),
                "end": iso_timestamp(right),
                "duration_seconds": round(duration_seconds, 3),
                "state": state,
            }
        )
        if state != "on":
            continue

        foreground_event = _latest_before(relevant, "foreground", left)
        last_screen_on = screen_event["_timestamp"] if screen_event else None
        package = ""
        if foreground_event and (
            last_screen_on is None
            or foreground_event["_timestamp"] >= last_screen_on
        ):
            package = str(foreground_event.get("package", ""))
        display = app_names.get(package, package or "亮屏但前台应用未知")
        app_seconds[display] += duration_seconds
        if package:
            package_seconds[package] += duration_seconds
        app_timeline.append(
            {
                "start": iso_timestamp(left),
                "end": iso_timestamp(right),
                "duration_seconds": round(duration_seconds, 3),
                "package": package,
                "app_display": display,
            }
        )

    screen_timeline = merge_timeline(screen_timeline, ("state",))
    app_timeline = merge_timeline(app_timeline, ("package", "app_display"))
    timeline_truncated = len(app_timeline) > max_segments
    app_timeline = app_timeline[:max_segments]

    screen_seconds: Counter[str] = Counter()
    for item in screen_timeline:
        screen_seconds[item["state"]] += item["duration_seconds"]

    unlock_count = sum(
        1
        for event in in_period
        if event.get("event") == "screen" and event.get("state") == "on"
    )
    foreground_switch_count = sum(
        1 for event in in_period if event.get("event") == "foreground"
    )
    fresh_limit = int(processing["heartbeat_fresh_seconds"])
    stale_limit = int(processing["heartbeat_stale_seconds"])
    nearby_heartbeats = [
        event
        for event in events
        if event.get("event") == "heartbeat"
        and abs((event["_timestamp"] - period_end).total_seconds()) <= stale_limit
    ]
    closest_heartbeat = (
        min(
            nearby_heartbeats,
            key=lambda event: abs((event["_timestamp"] - period_end).total_seconds()),
        )["_timestamp"]
        if nearby_heartbeats
        else None
    )
    heartbeat_offset = (
        (closest_heartbeat - period_end).total_seconds()
        if closest_heartbeat
        else None
    )
    heartbeat_distance = abs(heartbeat_offset) if heartbeat_offset is not None else None
    if heartbeat_distance is not None and heartbeat_distance <= fresh_limit:
        collector_quality = "high"
    elif heartbeat_distance is not None and heartbeat_distance <= stale_limit:
        collector_quality = "medium"
    else:
        collector_quality = "low"

    unknown_seconds = screen_seconds["unknown"]
    unknown_foreground_seconds = app_seconds["亮屏但前台应用未知"]
    if collector_quality == "high" and unknown_seconds <= 60:
        overall_quality = "high"
    elif collector_quality != "low" and unknown_seconds <= 300:
        overall_quality = "medium"
    else:
        overall_quality = "low"

    material_issues: list[str] = []
    if collector_quality == "low":
        material_issues.append("采集器长时间没有心跳，可能存在数据缺口。")
    if unknown_seconds > 60:
        material_issues.append(
            f"屏幕状态未知{rounded_minutes(unknown_seconds)}分钟。"
        )
    if unknown_foreground_seconds > 60:
        material_issues.append(
            f"亮屏期间前台应用未知{rounded_minutes(unknown_foreground_seconds)}分钟。"
        )
    if timeline_truncated:
        material_issues.append("手机时间线超过上限，已截断。")

    return {
        "schema_version": 1,
        "source": "mobile_usage_jsonl",
        "period": {
            "start": iso_timestamp(period_start),
            "end": iso_timestamp(period_end),
        },
        "input": {
            "files_read": [str(path) for path in files],
            "deduplicated_events_in_period": len(in_period),
            "deduplicated_events_by_type": dict(
                Counter(event.get("event", "unknown") for event in in_period)
            ),
            "accepted_events_by_file": file_counts,
        },
        "screen": {
            "on_minutes": rounded_minutes(screen_seconds["on"]),
            "off_minutes": rounded_minutes(screen_seconds["off"]),
            "unknown_minutes": rounded_minutes(screen_seconds["unknown"]),
            "unlock_count": unlock_count,
        },
        "foreground": {
            "switch_count": foreground_switch_count,
            "top_apps": [
                {"app": app, "minutes": rounded_minutes(seconds)}
                for app, seconds in app_seconds.most_common(20)
            ],
            "top_packages": [
                {"package": package, "minutes": rounded_minutes(seconds)}
                for package, seconds in package_seconds.most_common(20)
            ],
        },
        "screen_timeline": screen_timeline,
        "timeline": app_timeline,
        "quality": {
            "level": overall_quality,
            "collector_heartbeat": {
                "closest_seen": iso_timestamp(closest_heartbeat)
                if closest_heartbeat
                else None,
                "offset_seconds_from_period_end": round(heartbeat_offset, 1)
                if heartbeat_offset is not None
                else None,
                "level": collector_quality,
            },
            "timeline_truncated": timeline_truncated,
            "material_issues": material_issues,
            "limitations": [
                "亮屏表示屏幕开启，不保证用户持续注视或操作。",
                "前台应用只说明当时显示的应用，不直接表示使用目的。",
                "亮屏后尚未收到新的前台事件时，不沿用旧应用，保留为未知。",
            ],
        },
    }
