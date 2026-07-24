from __future__ import annotations

import json
import sqlite3
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

from common import (
    clean_title,
    clip_interval,
    datetime_to_ns,
    domain_from_url,
    iso_timestamp,
    merge_timeline,
    ns_to_iso,
    rounded_minutes,
)


def _find_database(sync_root: Path) -> Path:
    databases = sorted(
        sync_root.glob("*/*.db"),
        key=lambda path: (path.stat().st_mtime, path.stat().st_size),
        reverse=True,
    )
    if not databases:
        raise FileNotFoundError(f"ActivityWatch sync database not found under {sync_root}")
    return databases[0]


def _logical_events(
    connection: sqlite3.Connection,
    bucket_id: int,
    start_ns: int,
    end_ns: int,
) -> list[dict[str, Any]]:
    rows = connection.execute(
        """
        SELECT starttime, MAX(endtime) AS endtime, data, COUNT(*) AS versions
        FROM events
        WHERE bucketrow = ? AND endtime > ? AND starttime < ?
        GROUP BY starttime, data
        ORDER BY starttime
        """,
        (bucket_id, start_ns, end_ns),
    ).fetchall()
    events: list[dict[str, Any]] = []
    for row in rows:
        try:
            data = json.loads(row["data"])
        except (TypeError, json.JSONDecodeError):
            data = {}
        events.append(
            {
                "start": int(row["starttime"]),
                "end": int(row["endtime"]),
                "data": data,
                "versions": int(row["versions"]),
            }
        )
    return events


def _covering(
    events: list[dict[str, Any]], start: int, end: int
) -> dict[str, Any] | None:
    candidates = [
        event
        for event in events
        if event["start"] <= start and event["end"] >= end
    ]
    return max(candidates, key=lambda event: event["start"]) if candidates else None


def _status_timeline(
    events: list[dict[str, Any]],
    start_ns: int,
    end_ns: int,
    timezone_name: str,
) -> list[dict[str, Any]]:
    boundaries = {start_ns, end_ns}
    for event in events:
        clipped_start, clipped_end = clip_interval(
            event["start"], event["end"], start_ns, end_ns
        )
        if clipped_end > clipped_start:
            boundaries.update((clipped_start, clipped_end))
    ordered = sorted(boundaries)
    timeline: list[dict[str, Any]] = []
    for left, right in zip(ordered, ordered[1:]):
        event = _covering(events, left, right)
        status = event["data"].get("status", "unknown") if event else "unknown"
        timeline.append(
            {
                "start": ns_to_iso(left, timezone_name),
                "end": ns_to_iso(right, timezone_name),
                "duration_seconds": round((right - left) / 1_000_000_000, 3),
                "status": status,
                "_start_ns": left,
                "_end_ns": right,
            }
        )
    merged = merge_timeline(timeline, ("status",))
    return merged


def _display_app(app: str, app_names: dict[str, str]) -> str:
    return app_names.get(app, app or "未知应用")


def _compact_timeline(
    timeline: list[dict[str, Any]], noise_gap_seconds: float
) -> list[dict[str, Any]]:
    compact: list[dict[str, Any]] = []
    identity_keys = ("app", "app_display", "title")
    for item in timeline:
        if item.get("duration_seconds", 0) <= 0.01:
            continue
        if (
            item.get("context_source") == "missing"
            and item.get("duration_seconds", 0) <= noise_gap_seconds
        ):
            continue
        if compact:
            previous = compact[-1]
            same_identity = all(
                previous.get(key) == item.get(key) for key in identity_keys
            )
            previous_end = datetime_to_ns(datetime.fromisoformat(previous["end"]))
            item_start = datetime_to_ns(datetime.fromisoformat(item["start"]))
            gap_seconds = max(0.0, (item_start - previous_end) / 1_000_000_000)
            if same_identity and gap_seconds <= noise_gap_seconds:
                previous["end"] = item["end"]
                previous["duration_seconds"] = round(
                    previous["duration_seconds"] + item["duration_seconds"], 3
                )
                if not previous.get("domain") and item.get("domain"):
                    previous["domain"] = item["domain"]
                sources = set()
                for source_text in (
                    previous.get("context_source", ""),
                    item.get("context_source", ""),
                ):
                    sources.update(
                        source for source in source_text.split("+") if source
                    )
                previous["context_source"] = "+".join(sorted(sources))
                continue
        compact.append(dict(item))
    return compact


def extract_computer_facts(
    settings: dict[str, Any], period_start, period_end
) -> dict[str, Any]:
    timezone_name = settings["timezone"]
    processing = settings["processing"]
    max_title = int(processing["title_max_characters"])
    max_segments = int(processing["max_timeline_segments"])
    noise_gap_seconds = float(processing.get("timeline_noise_gap_seconds", 3))
    database_path = _find_database(Path(settings["activitywatch_sync_root"]))
    start_ns = datetime_to_ns(period_start)
    end_ns = datetime_to_ns(period_end)

    connection = sqlite3.connect(
        f"file:{database_path}?mode=ro", uri=True, timeout=10
    )
    connection.row_factory = sqlite3.Row
    try:
        buckets = [
            dict(row)
            for row in connection.execute(
                "SELECT id, name, type, client, hostname FROM buckets ORDER BY id"
            )
        ]
        bucket_events: dict[int, list[dict[str, Any]]] = {}
        raw_counts: dict[str, int] = {}
        for bucket in buckets:
            bucket_events[bucket["id"]] = _logical_events(
                connection, bucket["id"], start_ns, end_ns
            )
            raw_counts[bucket["name"]] = connection.execute(
                """
                SELECT COUNT(*) FROM events
                WHERE bucketrow = ? AND endtime > ? AND starttime < ?
                """,
                (bucket["id"], start_ns, end_ns),
            ).fetchone()[0]
    finally:
        connection.close()

    afk_buckets = [bucket for bucket in buckets if bucket["type"] == "afkstatus"]
    window_buckets = [bucket for bucket in buckets if bucket["type"] == "currentwindow"]
    web_buckets = [bucket for bucket in buckets if bucket["type"] == "web.tab.current"]

    afk_events = [
        event
        for bucket in afk_buckets
        for event in bucket_events.get(bucket["id"], [])
    ]
    status_timeline = _status_timeline(
        afk_events, start_ns, end_ns, timezone_name
    )
    status_internal = [
        {
            "start": item["_start_ns"],
            "end": item["_end_ns"],
            "status": item["status"],
        }
        for item in status_timeline
    ]

    window_events = [
        event
        for bucket in window_buckets
        for event in bucket_events.get(bucket["id"], [])
    ]
    web_events_by_app: dict[str, list[dict[str, Any]]] = {
        "msedge.exe": [],
        "chrome.exe": [],
    }
    for bucket in web_buckets:
        name = bucket["name"].lower()
        target = "msedge.exe" if "edge" in name else "chrome.exe" if "chrome" in name else ""
        if target:
            web_events_by_app[target].extend(bucket_events.get(bucket["id"], []))

    title_domain_votes: dict[str, Counter[str]] = {}
    page_observations: dict[tuple[str, str], dict[str, Any]] = {}
    for events in web_events_by_app.values():
        for event in events:
            title = clean_title(event["data"].get("title"), max_title)
            domain = domain_from_url(event["data"].get("url"))
            if not title:
                continue
            if domain:
                title_domain_votes.setdefault(title, Counter())[domain] += 1
            key = (domain, title)
            observation = page_observations.setdefault(
                key,
                {
                    "domain": domain,
                    "title": title,
                    "first_seen_ns": event["start"],
                    "last_seen_ns": event["end"],
                    "raw_event_count": 0,
                },
            )
            observation["first_seen_ns"] = min(
                observation["first_seen_ns"], event["start"]
            )
            observation["last_seen_ns"] = max(
                observation["last_seen_ns"], event["end"]
            )
            observation["raw_event_count"] += 1

    boundaries = {start_ns, end_ns}
    for event in window_events:
        left, right = clip_interval(event["start"], event["end"], start_ns, end_ns)
        if right > left:
            boundaries.update((left, right))
    for events in web_events_by_app.values():
        for event in events:
            left, right = clip_interval(event["start"], event["end"], start_ns, end_ns)
            if right > left:
                boundaries.update((left, right))
    for item in status_internal:
        boundaries.update((item["start"], item["end"]))

    ordered = sorted(boundaries)
    timeline: list[dict[str, Any]] = []
    app_seconds: Counter[str] = Counter()
    domain_seconds: Counter[str] = Counter()
    title_seconds: Counter[tuple[str, str, str]] = Counter()
    browser_seconds = 0.0
    browser_exact_web_overlap_seconds = 0.0
    browser_resolved_domain_seconds = 0.0
    browser_title_seconds = 0.0
    observed_active_seconds = 0.0

    for left, right in zip(ordered, ordered[1:]):
        status_item = next(
            (
                item
                for item in status_internal
                if item["start"] <= left and item["end"] >= right
            ),
            None,
        )
        if not status_item or status_item["status"] != "not-afk":
            continue

        duration_seconds = (right - left) / 1_000_000_000
        window_event = _covering(window_events, left, right)
        if not window_event:
            timeline.append(
                {
                    "start": ns_to_iso(left, timezone_name),
                    "end": ns_to_iso(right, timezone_name),
                    "duration_seconds": round(duration_seconds, 3),
                    "app": "",
                    "app_display": "活跃但无窗口记录",
                    "title": "",
                    "domain": "",
                    "context_source": "missing",
                }
            )
            continue

        app = str(window_event["data"].get("app", ""))
        window_title = clean_title(window_event["data"].get("title"), max_title)
        title = window_title
        domain = ""
        context_source = "window"
        if app in web_events_by_app:
            browser_seconds += duration_seconds
            if window_title:
                browser_title_seconds += duration_seconds
            web_event = _covering(web_events_by_app[app], left, right)
            if web_event:
                web_title = clean_title(web_event["data"].get("title"), max_title)
                domain = domain_from_url(web_event["data"].get("url"))
                title = web_title or window_title
                context_source = "web"
                browser_exact_web_overlap_seconds += duration_seconds
            elif window_title in title_domain_votes:
                domain = title_domain_votes[window_title].most_common(1)[0][0]
                context_source = "title_match"
            if domain:
                browser_resolved_domain_seconds += duration_seconds

        observed_active_seconds += duration_seconds
        display_app = _display_app(app, settings.get("computer_app_names", {}))
        app_seconds[display_app] += duration_seconds
        if domain:
            domain_seconds[domain] += duration_seconds
        if title:
            title_seconds[(display_app, domain, title)] += duration_seconds
        timeline.append(
            {
                "start": ns_to_iso(left, timezone_name),
                "end": ns_to_iso(right, timezone_name),
                "duration_seconds": round(duration_seconds, 3),
                "app": app,
                "app_display": display_app,
                "title": title,
                "domain": domain,
                "context_source": context_source,
            }
        )

    timeline = merge_timeline(
        timeline, ("app", "app_display", "title", "domain", "context_source")
    )
    timeline = _compact_timeline(timeline, noise_gap_seconds)
    timeline_truncated = len(timeline) > max_segments
    timeline = timeline[:max_segments]

    status_seconds: Counter[str] = Counter()
    public_status_timeline: list[dict[str, Any]] = []
    for item in status_timeline:
        if item["status"] == "unknown" and item["duration_seconds"] <= 1:
            continue
        status_seconds[item["status"]] += item["duration_seconds"]
        public_status_timeline.append(
            {key: value for key, value in item.items() if not key.startswith("_")}
        )

    active_seconds = status_seconds["not-afk"]
    coverage = observed_active_seconds / active_seconds if active_seconds else 0.0
    browser_exact_overlap = (
        browser_exact_web_overlap_seconds / browser_seconds
        if browser_seconds
        else 1.0
    )
    browser_domain_coverage = (
        browser_resolved_domain_seconds / browser_seconds
        if browser_seconds
        else 1.0
    )
    browser_title_coverage = (
        browser_title_seconds / browser_seconds if browser_seconds else 1.0
    )
    unknown_status_seconds = status_seconds["unknown"]
    if coverage >= 0.9 and unknown_status_seconds <= 60:
        quality = "high"
    elif coverage >= 0.7 and unknown_status_seconds <= 300:
        quality = "medium"
    else:
        quality = "low"
    browser_share = browser_seconds / active_seconds if active_seconds else 0.0
    if browser_share >= 0.3 and browser_domain_coverage < 0.5 and quality == "high":
        quality = "medium"

    material_issues: list[str] = []
    if coverage < 0.9:
        material_issues.append(
            f"电脑活跃窗口只覆盖{round(coverage * 100, 1)}%。"
        )
    if browser_share >= 0.3 and browser_domain_coverage < 0.5:
        material_issues.append(
            f"浏览器前台时间中只有{round(browser_domain_coverage * 100, 1)}%能关联到域名。"
        )
    if unknown_status_seconds > 60:
        material_issues.append(
            f"电脑活动状态未知{rounded_minutes(unknown_status_seconds)}分钟。"
        )
    if timeline_truncated:
        material_issues.append("电脑时间线超过上限，已截断。")

    observed_pages = [
        {
            "domain": item["domain"],
            "title": item["title"],
            "first_seen": ns_to_iso(item["first_seen_ns"], timezone_name),
            "last_seen": ns_to_iso(item["last_seen_ns"], timezone_name),
            "raw_event_count": item["raw_event_count"],
        }
        for item in sorted(
            page_observations.values(),
            key=lambda value: (value["first_seen_ns"], value["title"]),
        )[:50]
    ]

    return {
        "schema_version": 1,
        "source": "computer_activitywatch",
        "period": {
            "start": iso_timestamp(period_start),
            "end": iso_timestamp(period_end),
        },
        "database": {
            "file_name": database_path.name,
            "buckets_seen": [bucket["name"] for bucket in buckets],
            "raw_event_counts_in_period": raw_counts,
        },
        "activity": {
            "not_afk_minutes": rounded_minutes(status_seconds["not-afk"]),
            "afk_minutes": rounded_minutes(status_seconds["afk"]),
            "unknown_status_minutes": rounded_minutes(status_seconds["unknown"]),
            "window_observed_minutes": rounded_minutes(observed_active_seconds),
        },
        "top_apps": [
            {"app": app, "minutes": rounded_minutes(seconds)}
            for app, seconds in app_seconds.most_common(20)
        ],
        "top_websites": [
            {"domain": domain, "minutes": rounded_minutes(seconds)}
            for domain, seconds in domain_seconds.most_common(20)
        ],
        "top_titles": [
            {
                "app": key[0],
                "domain": key[1],
                "title": key[2],
                "minutes": rounded_minutes(seconds),
            }
            for key, seconds in title_seconds.most_common(30)
        ],
        "observed_pages": observed_pages,
        "status_timeline": public_status_timeline,
        "timeline": timeline,
        "quality": {
            "level": quality,
            "active_window_coverage": round(coverage, 3),
            "browser_title_coverage": round(browser_title_coverage, 3),
            "browser_domain_context_coverage": round(browser_domain_coverage, 3),
            "web_watcher_exact_time_overlap": round(browser_exact_overlap, 3),
            "browser_share_of_active_time": round(browser_share, 3),
            "timeline_truncated": timeline_truncated,
            "material_issues": material_issues,
            "limitations": [
                "AFK只表示电脑无键鼠操作，不等于休息。",
                "web_watcher_exact_time_overlap只衡量两个采集器的事件时长重合，不衡量标签页是否被识别。",
                "网页用途优先参考前台窗口标题及本时段观察到的标签页；网页事件时长不直接当作浏览时长。",
            ],
        },
    }
