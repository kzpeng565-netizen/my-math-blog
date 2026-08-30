from __future__ import annotations

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlparse
from zoneinfo import ZoneInfo


UNREAD_PREFIX_RE = re.compile(
    r"^\s*[\(\（][^\)\）]*(?:封私信|条消息|未读)[^\)\）]*[\)\）]\s*",
    re.IGNORECASE,
)
OTHER_TABS_RE = re.compile(r"\s+和另外\s*\d+\s*个页面.*$", re.IGNORECASE)
BROWSER_SUFFIXES = (
    re.compile(r"\s*-\s*个人\s*-\s*Microsoft.*Edge\s*$", re.IGNORECASE),
    re.compile(r"\s*-\s*Microsoft.*Edge\s*$", re.IGNORECASE),
    re.compile(r"\s*-\s*Google Chrome\s*$", re.IGNORECASE),
    re.compile(r"\s+-\s+[^-]{1,80}\s+-\s+Obsidian\s+[\d.]+\s*$", re.IGNORECASE),
)
EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
PHONE_RE = re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)")
LONG_SECRET_RE = re.compile(r"\b(?:sk-)?[A-Za-z0-9_-]{24,}\b")
SPACE_RE = re.compile(r"\s+")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_timestamp(value: str, timezone_name: str) -> datetime:
    text = value.strip().replace("Z", "+00:00")
    parsed = datetime.fromisoformat(text)
    timezone = ZoneInfo(timezone_name)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone)
    return parsed.astimezone(timezone)


def iso_timestamp(value: datetime) -> str:
    return value.isoformat(timespec="seconds")


def datetime_to_ns(value: datetime) -> int:
    return int(value.timestamp() * 1_000_000_000)


def ns_to_iso(value: int, timezone_name: str) -> str:
    timezone = ZoneInfo(timezone_name)
    return datetime.fromtimestamp(value / 1_000_000_000, timezone).isoformat(
        timespec="seconds"
    )


def clip_interval(start: int, end: int, lower: int, upper: int) -> tuple[int, int]:
    return max(start, lower), min(end, upper)


def overlap_ns(start: int, end: int, intervals: Iterable[tuple[int, int]]) -> int:
    return sum(
        max(0, min(end, other_end) - max(start, other_start))
        for other_start, other_end in intervals
        if other_start < end and other_end > start
    )


def merge_intervals(intervals: Iterable[tuple[int, int]]) -> list[tuple[int, int]]:
    merged: list[tuple[int, int]] = []
    for start, end in sorted((start, end) for start, end in intervals if end > start):
        if merged and start <= merged[-1][1]:
            merged[-1] = merged[-1][0], max(merged[-1][1], end)
        else:
            merged.append((start, end))
    return merged


def clean_title(value: str | None, max_characters: int = 180) -> str:
    if not value:
        return ""
    title = SPACE_RE.sub(" ", str(value)).strip()
    title = UNREAD_PREFIX_RE.sub("", title)
    title = OTHER_TABS_RE.sub("", title)
    for suffix in BROWSER_SUFFIXES:
        title = suffix.sub("", title)
    title = EMAIL_RE.sub("[邮箱已隐藏]", title)
    title = PHONE_RE.sub("[手机号已隐藏]", title)
    title = LONG_SECRET_RE.sub("[长标识符已隐藏]", title)
    return title[:max_characters].strip(" -")


def domain_from_url(value: str | None) -> str:
    if not value:
        return ""
    try:
        hostname = (urlparse(value).hostname or "").lower()
    except ValueError:
        return ""
    if hostname.startswith("www."):
        hostname = hostname[4:]
    return hostname


def merge_timeline(
    timeline: list[dict[str, Any]], identity_keys: tuple[str, ...]
) -> list[dict[str, Any]]:
    merged: list[dict[str, Any]] = []
    for item in timeline:
        if item.get("duration_seconds", 0) <= 0:
            continue
        identity = tuple(item.get(key) for key in identity_keys)
        if merged:
            previous_identity = tuple(merged[-1].get(key) for key in identity_keys)
            if identity == previous_identity and merged[-1]["end"] == item["start"]:
                merged[-1]["end"] = item["end"]
                if "_end_ns" in item:
                    merged[-1]["_end_ns"] = item["_end_ns"]
                merged[-1]["duration_seconds"] = round(
                    merged[-1]["duration_seconds"] + item["duration_seconds"], 3
                )
                continue
        merged.append(dict(item))
    return merged


def rounded_minutes(seconds: float) -> float:
    return round(seconds / 60, 2)


def atomic_write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    os.replace(temporary, path)


def atomic_write_text(path: Path, data: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(data, encoding="utf-8")
    os.replace(temporary, path)
