from __future__ import annotations

import argparse
import json
import os
from collections import Counter, defaultdict
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from common import atomic_write_json, atomic_write_text, load_json
from deepseek_client import _request_json_report
from obsidian_context import load_obsidian_context


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SETTINGS = PROJECT_ROOT / "config" / "settings.json"
DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / "data"
DEFAULT_PROMPT = PROJECT_ROOT / "prompts" / "daily-life-advisor.md"
DEFAULT_ENV = Path("/home/conrad/.config/activitywatch-advisor/env")
TIMEZONE = ZoneInfo("Asia/Shanghai")

WORK_CATEGORY_LABELS = {
    "数学学习": "数学学习",
    "家教": "家教",
    "系统维护": "项目维护/系统维护",
    "其他工作": "其他工作",
    "": "未分类工作",
}
AI_DOMAINS = {"chatgpt.com", "chat.deepseek.com", "gemini.google.com"}
AI_APPS = {"ChatGPT", "DeepSeek", "Gemini"}
SUMMARY_CATEGORIES = (
    "work",
    "entertainment",
    "shopping",
    "brief_communication",
    "rest",
    "other",
    "uncertain",
)


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else None
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return None


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _minutes(seconds: float) -> float:
    return round(seconds / 60, 2)


def _overlap_seconds(
    left_start: datetime,
    left_end: datetime,
    right_start: datetime,
    right_end: datetime,
) -> float:
    return max(0.0, (min(left_end, right_end) - max(left_start, right_start)).total_seconds())


def _day_report_paths(output_root: Path, day: date) -> list[Path]:
    return sorted((output_root / "ai_reports" / day.isoformat()).glob("*.json"))


def _day_semantic_paths(output_root: Path, day: date) -> list[Path]:
    return sorted((output_root / "semantic_timelines" / day.isoformat()).glob("*.json"))


def _load_reports(output_root: Path, day: date) -> list[dict[str, Any]]:
    reports = []
    for path in _day_report_paths(output_root, day):
        report = _read_json(path)
        if report:
            report["_path"] = str(path)
            reports.append(report)
    return reports


def _load_semantic_segments(output_root: Path, day: date) -> list[dict[str, Any]]:
    segments: list[dict[str, Any]] = []
    for path in _day_semantic_paths(output_root, day):
        timeline = _read_json(path)
        if not timeline:
            continue
        for segment in timeline.get("segments", []):
            if not isinstance(segment, dict):
                continue
            try:
                item = dict(segment)
                item["_start_dt"] = _parse_time(item["start"])
                item["_end_dt"] = _parse_time(item["end"])
                item["_path"] = str(path)
            except (KeyError, TypeError, ValueError):
                continue
            segments.append(item)
    return sorted(segments, key=lambda item: item["_start_dt"])


def _estimated_totals(reports: list[dict[str, Any]]) -> dict[str, float]:
    totals = {key: 0.0 for key in SUMMARY_CATEGORIES}
    for report in reports:
        allocation = report.get("estimated_time_allocation", {})
        if not isinstance(allocation, dict):
            continue
        for key in SUMMARY_CATEGORIES:
            try:
                totals[key] += float(allocation.get(key, {}).get("estimate_minutes", 0))
            except (TypeError, ValueError, AttributeError):
                continue
    return {key: round(value, 2) for key, value in totals.items()}


def _work_breakdown(segments: list[dict[str, Any]]) -> dict[str, Any]:
    by_category: Counter[str] = Counter()
    by_task: Counter[str] = Counter()
    evidence_by_task: dict[str, str] = {}
    for segment in segments:
        if segment.get("activity") != "work":
            continue
        seconds = float(segment.get("duration_seconds", 0) or 0)
        category = WORK_CATEGORY_LABELS.get(
            str(segment.get("work_category", "")), str(segment.get("work_category", "未分类工作"))
        )
        by_category[category] += seconds
        task = str(segment.get("task", "")).strip() or category
        by_task[task] += seconds
        evidence = segment.get("evidence", [])
        if evidence and task not in evidence_by_task:
            evidence_by_task[task] = str(evidence[0])[:160]
    return {
        "by_category": [
            {"name": name, "minutes": _minutes(seconds)}
            for name, seconds in by_category.most_common()
        ],
        "top_tasks": [
            {
                "name": name,
                "minutes": _minutes(seconds),
                "evidence": evidence_by_task.get(name, ""),
            }
            for name, seconds in by_task.most_common(8)
        ],
    }


def _segment_task_name(segment: dict[str, Any], fallback: str) -> str:
    task = str(segment.get("task", "")).strip()
    if task:
        return task
    evidence = segment.get("evidence", [])
    if evidence:
        return str(evidence[0])[:80]
    return fallback


def _task_breakdown(
    segments: list[dict[str, Any]],
    *,
    activity: str,
    fallback: str,
    limit: int = 3,
) -> list[dict[str, Any]]:
    by_task: Counter[str] = Counter()
    evidence_by_task: dict[str, str] = {}
    for segment in segments:
        if segment.get("activity") != activity:
            continue
        seconds = float(segment.get("duration_seconds", 0) or 0)
        task = _segment_task_name(segment, fallback)
        by_task[task] += seconds
        evidence = segment.get("evidence", [])
        if evidence and task not in evidence_by_task:
            evidence_by_task[task] = str(evidence[0])[:160]
    return [
        {
            "name": name,
            "minutes": _minutes(seconds),
            "evidence": evidence_by_task.get(name, ""),
        }
        for name, seconds in by_task.most_common(limit)
    ]


def _merge_same_kind_segments(
    entries: list[dict[str, Any]],
    *,
    gap_seconds: float = 60,
) -> list[dict[str, Any]]:
    merged: list[dict[str, Any]] = []
    for entry in sorted(entries, key=lambda item: item["start"]):
        if (
            merged
            and merged[-1]["type"] == entry["type"]
            and merged[-1].get("label") == entry.get("label")
            and (entry["start"] - merged[-1]["end"]).total_seconds() <= gap_seconds
        ):
            merged[-1]["end"] = max(merged[-1]["end"], entry["end"])
            merged[-1]["seconds"] += entry["seconds"]
            merged[-1]["evidence"].extend(entry.get("evidence", [])[:1])
        else:
            merged.append({**entry, "evidence": list(entry.get("evidence", []))})
    return merged


def _long_blocks(
    segments: list[dict[str, Any]],
    ai_intervals: list[tuple[datetime, datetime]],
) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for segment in segments:
        activity = str(segment.get("activity", ""))
        if activity == "work":
            label = str(segment.get("task", "")).strip() or WORK_CATEGORY_LABELS.get(
                str(segment.get("work_category", "")), "工作"
            )
        elif activity == "entertainment":
            label = "娱乐"
        elif activity == "shopping":
            label = "购物"
        elif activity == "brief_communication":
            label = "通信"
        else:
            continue
        entries.append(
            {
                "type": activity,
                "label": label,
                "start": segment["_start_dt"],
                "end": segment["_end_dt"],
                "seconds": float(segment.get("duration_seconds", 0) or 0),
                "evidence": [str(item) for item in segment.get("evidence", [])[:2]],
            }
        )
    for start, end in ai_intervals:
        entries.append(
            {
                "type": "ai_use",
                "label": "AI使用",
                "start": start,
                "end": end,
                "seconds": (end - start).total_seconds(),
                "evidence": ["电脑前台为 ChatGPT/DeepSeek/Gemini 等 AI 工具"],
            }
        )
    thresholds = {
        "work": 90,
        "entertainment": 30,
        "shopping": 30,
        "brief_communication": 20,
        "ai_use": 90,
    }
    result = []
    for block in _merge_same_kind_segments(entries):
        minutes = _minutes(block["seconds"])
        threshold = thresholds.get(block["type"])
        if threshold is None or minutes < threshold:
            continue
        result.append(
            {
                "type": block["type"],
                "label": block["label"],
                "start": block["start"].strftime("%H:%M"),
                "end": block["end"].strftime("%H:%M"),
                "minutes": minutes,
                "reason": f"连续{block['label']}约{minutes}分钟，超过{threshold}分钟观察阈值。",
                "evidence": block["evidence"][:3],
            }
        )
    return sorted(result, key=lambda item: item["minutes"], reverse=True)[:8]


def _computer_activity_files(output_root: Path, day: date) -> list[Path]:
    return sorted((output_root / "computer_facts" / day.isoformat()).glob("*.json"))


def _ai_intervals(output_root: Path, day: date) -> list[tuple[datetime, datetime]]:
    intervals: list[tuple[datetime, datetime]] = []
    for path in _computer_activity_files(output_root, day):
        facts = _read_json(path)
        if not facts:
            continue
        for item in facts.get("timeline", []):
            app = str(item.get("app_display", ""))
            domain = str(item.get("domain", ""))
            if app not in AI_APPS and domain not in AI_DOMAINS:
                continue
            try:
                intervals.append((_parse_time(item["start"]), _parse_time(item["end"])))
            except (KeyError, TypeError, ValueError):
                continue
    return _merge_intervals(intervals, max_gap_seconds=3)


def _merge_intervals(
    intervals: list[tuple[datetime, datetime]],
    *,
    max_gap_seconds: float = 0,
) -> list[tuple[datetime, datetime]]:
    merged: list[tuple[datetime, datetime]] = []
    for start, end in sorted(intervals):
        if end <= start:
            continue
        if merged and (start - merged[-1][1]).total_seconds() <= max_gap_seconds:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged


def _ai_usage(
    ai_intervals: list[tuple[datetime, datetime]],
    segments: list[dict[str, Any]],
) -> dict[str, Any]:
    total_seconds = sum((end - start).total_seconds() for start, end in ai_intervals)
    by_activity: Counter[str] = Counter()
    by_task: Counter[str] = Counter()
    task_activity: dict[str, str] = {}
    for ai_start, ai_end in ai_intervals:
        for segment in segments:
            seconds = _overlap_seconds(ai_start, ai_end, segment["_start_dt"], segment["_end_dt"])
            if seconds:
                activity = str(segment.get("activity", "uncertain"))
                task = _segment_task_name(segment, activity)
                by_activity[activity] += seconds
                by_task[task] += seconds
                task_activity.setdefault(task, activity)
    return {
        "total_minutes": _minutes(total_seconds),
        "by_activity": {
            "work": _minutes(by_activity["work"]),
            "entertainment": _minutes(by_activity["entertainment"]),
            "brief_communication": _minutes(by_activity["brief_communication"]),
            "other": _minutes(by_activity["other"]),
            "uncertain": _minutes(by_activity["uncertain"]),
        },
        "top_tasks": [
            {
                "name": name,
                "activity": task_activity.get(name, "uncertain"),
                "minutes": _minutes(seconds),
            }
            for name, seconds in by_task.most_common(3)
        ],
    }


def _phone_screen_intervals(output_root: Path, day: date) -> list[tuple[datetime, datetime]]:
    intervals: list[tuple[datetime, datetime]] = []
    for current_day in (day, day + timedelta(days=1)):
        for path in sorted((output_root / "phone_facts" / current_day.isoformat()).glob("*.json")):
            facts = _read_json(path)
            if not facts:
                continue
            for item in facts.get("screen_timeline", []):
                if item.get("state") != "on":
                    continue
                try:
                    intervals.append((_parse_time(item["start"]), _parse_time(item["end"])))
                except (KeyError, TypeError, ValueError):
                    continue
    return _merge_intervals(intervals, max_gap_seconds=60)


def _sleep_boundary(
    output_root: Path, day: date, morning_cutoff_hour: int = 9
) -> dict[str, Any]:
    evening = datetime.combine(day, time(20, 0), tzinfo=TIMEZONE)
    morning_hour = min(11, max(9, int(morning_cutoff_hour)))
    morning = datetime.combine(
        day + timedelta(days=1), time(morning_hour, 0), tzinfo=TIMEZONE
    )
    deep_night_start = datetime.combine(day, time(23, 0), tzinfo=TIMEZONE)
    deep_night_end = datetime.combine(day + timedelta(days=1), time(7, 0), tzinfo=TIMEZONE)
    intervals = []
    ignored_short = 0
    for start, end in _phone_screen_intervals(output_root, day):
        clipped_start = max(start, evening)
        clipped_end = min(end, morning)
        if clipped_end <= clipped_start:
            continue
        seconds = (clipped_end - clipped_start).total_seconds()
        if (
            clipped_start >= deep_night_start
            and clipped_end <= deep_night_end
            and seconds < 300
        ):
            ignored_short += 1
            continue
        if seconds >= 30:
            intervals.append((clipped_start, clipped_end))
    intervals = _merge_intervals(intervals, max_gap_seconds=120)
    if not intervals:
        return {
            "last_phone_use_at_night": None,
            "first_phone_use_in_morning": None,
            "sleep_estimate_minutes_minus_20": None,
            "quality": "low",
            "status": "possible_fault" if morning_hour >= 11 else "pending",
            "morning_cutoff_hour": morning_hour,
            "notes": [f"20:00-{morning_hour:02d}:00内没有足够手机亮屏证据。"],
        }
    candidates: list[tuple[float, datetime, datetime, str]] = []
    previous_end = evening
    for start, end in intervals:
        candidates.append(((start - previous_end).total_seconds(), previous_end, start, "closed"))
        previous_end = max(previous_end, end)
    candidates.append(((morning - previous_end).total_seconds(), previous_end, morning, "open_end"))
    gap_seconds, gap_start, gap_end, gap_kind = max(candidates, key=lambda item: item[0])
    notes = []
    if ignored_short:
        notes.append(f"夜间{ignored_short}次短亮屏已忽略，不打断睡眠边界。")
    if gap_seconds < 3 * 3600:
        notes.append("最长无手机使用间隔不足3小时，睡眠边界置信度较低。")
    if gap_kind == "open_end":
        notes.append(
            f"{morning_hour:02d}:00前没有下一次手机亮屏记录，无法确定早上拿起手机时间。"
        )
        if morning_hour >= 11:
            notes.append("已到11:00仍未观察到早晨边界，可能是手机采集或同步故障。")
        return {
            "last_phone_use_at_night": gap_start.strftime("%H:%M"),
            "first_phone_use_in_morning": None,
            "sleep_estimate_minutes_minus_20": None,
            "quality": "low",
            "status": "possible_fault" if morning_hour >= 11 else "pending",
            "morning_cutoff_hour": morning_hour,
            "notes": notes,
        }
    sleep_minutes = max(0, _minutes(gap_seconds - 20 * 60))
    return {
        "last_phone_use_at_night": gap_start.strftime("%H:%M"),
        "first_phone_use_in_morning": gap_end.strftime("%H:%M"),
        "sleep_estimate_minutes_minus_20": sleep_minutes,
        "quality": "high" if gap_seconds >= 5 * 3600 else "medium",
        "status": "resolved",
        "morning_cutoff_hour": morning_hour,
        "notes": notes,
    }


def _mixing_totals(reports: list[dict[str, Any]]) -> dict[str, float | int]:
    count = 0
    minutes = 0.0
    for report in reports:
        metrics = report.get("mixing_assessment", {})
        try:
            count += int(metrics.get("entertainment_deviation_count", 0))
            minutes += float(metrics.get("entertainment_deviation_minutes", 0))
        except (TypeError, ValueError):
            continue
    return {"deviation_count": count, "deviation_minutes": round(minutes, 2)}


def _efficiency_flags(
    totals: dict[str, float],
    mixing: dict[str, float | int],
    long_blocks: list[dict[str, Any]],
    task_candidates: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    flags = []
    if int(mixing.get("deviation_count", 0)) >= 3:
        flags.append(
            {
                "type": "frequent_entertainment_deviation",
                "label": "工作中娱乐偏离偏多",
                "evidence": f"工作中娱乐偏离{mixing['deviation_count']}次，共{mixing['deviation_minutes']}分钟。",
            }
        )
    if float(mixing.get("deviation_minutes", 0)) >= 20:
        flags.append(
            {
                "type": "long_entertainment_deviation",
                "label": "娱乐偏离总时长偏长",
                "evidence": f"娱乐偏离总时长{mixing['deviation_minutes']}分钟，超过20分钟观察阈值。",
            }
        )
    if totals.get("uncertain", 0) >= 60:
        flags.append(
            {
                "type": "large_uncertain_time",
                "label": "无法判断时间偏多",
                "evidence": f"无法判断{totals['uncertain']}分钟，效率判断需要降低置信度。",
            }
        )
    for block in long_blocks:
        if block["type"] == "work":
            flags.append(
                {
                    "type": "long_work_block",
                    "label": "单个工作块较长",
                    "evidence": f"{block['start']}-{block['end']} {block['label']}持续{block['minutes']}分钟，可能需要核验是否有效推进。",
                }
            )
            break
    if task_candidates:
        flags.append(
            {
                "type": "priority_task_review",
                "label": "高优先级任务需要对照投入",
                "evidence": "存在高优先级/近期任务，AI建议层需结合今日实际工作检查是否被挤压。",
            }
        )
    return flags[:8]


def _uncertain_patterns(segments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counter: Counter[str] = Counter()
    examples: dict[str, str] = {}
    for segment in segments:
        if segment.get("activity") != "uncertain" and segment.get("confidence") != "low":
            continue
        evidence = " ".join(str(item) for item in segment.get("evidence", [])[:2])
        label = "无窗口记录" if "无窗口" in evidence else "语义不确定"
        if "知乎" in evidence:
            label = "知乎边界需核验"
        elif "新建标签页" in evidence:
            label = "新建标签页用途不明"
        elif "前台未知" in evidence:
            label = "手机前台未知"
        counter[label] += 1
        examples.setdefault(label, evidence[:160])
    return [
        {
            "type": "uncertain_pattern",
            "label": label,
            "evidence": f"出现{count}次；例：{examples.get(label, '')}",
        }
        for label, count in counter.most_common()
        if count >= 3
    ][:5]


def _annotation_flags(output_root: Path, day: date) -> list[dict[str, Any]]:
    flags = []
    raw_dir = output_root / "user_annotations" / "raw" / day.isoformat()
    for path in sorted(raw_dir.glob("*.json")):
        annotation = _read_json(path)
        if not annotation or annotation.get("status") != "unreviewed":
            continue
        message = str(annotation.get("message") or "").strip()
        if (
            not message
            or message.startswith("测试")
            or "??" in message
        ):
            continue
        flags.append(
            {
                "type": "user_annotation",
                "label": str(annotation.get("category_label", "用户反馈未处理")),
                "evidence": message[:160],
            }
        )
    return flags[:5]


def _task_candidates(context: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not context:
        return []
    tasks = context.get("tasks", {})
    candidates: list[dict[str, Any]] = []
    for bucket in ("overdue", "today", "near_term"):
        for task in tasks.get(bucket, []) if isinstance(tasks, dict) else []:
            if not isinstance(task, dict):
                continue
            priority = str(task.get("priority", "normal"))
            if bucket == "near_term" and priority not in {"highest", "high"}:
                continue
            candidates.append(
                {
                    "title": task.get("title", ""),
                    "category": task.get("category"),
                    "priority": priority,
                    "scheduled_date": task.get("scheduled_date"),
                    "due_date": task.get("due_date"),
                    "tomatoes_completed": task.get("tomatoes_completed"),
                    "tomatoes_total": task.get("tomatoes_total"),
                    "source": f"obsidian_{bucket}",
                }
            )
    return candidates[:8]


def _data_quality(
    reports: list[dict[str, Any]],
    totals: dict[str, float],
    sleep: dict[str, Any],
) -> dict[str, Any]:
    issues = []
    if len(reports) < 40:
        issues.append(f"有效半小时报告只有{len(reports)}份，少于全天48份。")
    if totals.get("uncertain", 0) >= 60:
        issues.append(f"无法判断时间{totals['uncertain']}分钟，建议降低效率判断置信度。")
    if sleep.get("quality") != "high":
        issues.extend(sleep.get("notes", []))
    return {
        "level": "high" if not issues else ("medium" if len(issues) <= 2 else "low"),
        "issues": issues[:5],
    }


def _compact_context(context: dict[str, Any] | None) -> dict[str, Any] | None:
    if not context:
        return None
    compact = {
        "generated_at": context.get("generated_at"),
        "latest_plan_heading": context.get("latest_plan_heading"),
        "profile_markdown": str(context.get("profile_markdown", ""))[:1200],
        "tasks": context.get("tasks"),
        "pomodoro": context.get("pomodoro"),
    }
    return {key: value for key, value in compact.items() if value not in (None, "", [], {})}


def build_daily_life_summary(
    output_root: Path,
    day: date,
    obsidian_context: dict[str, Any] | None = None,
    morning_cutoff_hour: int = 9,
) -> dict[str, Any]:
    reports = _load_reports(output_root, day)
    segments = _load_semantic_segments(output_root, day)
    totals = _estimated_totals(reports)
    mixing = _mixing_totals(reports)
    ai_intervals = _ai_intervals(output_root, day)
    ai_usage = _ai_usage(ai_intervals, segments)
    work = _work_breakdown(segments)
    entertainment = _task_breakdown(
        segments,
        activity="entertainment",
        fallback="未细分娱乐",
        limit=3,
    )
    sleep = _sleep_boundary(output_root, day, morning_cutoff_hour)
    tasks = _task_candidates(obsidian_context)
    long_blocks = _long_blocks(segments, ai_intervals)
    system_flags = [*_uncertain_patterns(segments), *_annotation_flags(output_root, day)]
    efficiency_flags = _efficiency_flags(totals, mixing, long_blocks, tasks)
    summary = {
        "schema_version": 1,
        "period": day.isoformat(),
        "generated_at": datetime.now(TIMEZONE).isoformat(timespec="seconds"),
        "report_count": len(reports),
        "daily_totals": {
            "work_minutes": totals["work"],
            "entertainment_minutes": totals["entertainment"],
            "shopping_minutes": totals["shopping"],
            "communication_minutes": totals["brief_communication"],
            "rest_minutes": totals["rest"],
            "other_minutes": totals["other"],
            "uncertain_minutes": totals["uncertain"],
        },
        "work_breakdown": work,
        "entertainment_breakdown": {"top_tasks": entertainment},
        "phone_sleep_boundary": sleep,
        "ai_usage": ai_usage,
        "work_entertainment_mixing": mixing,
        "long_blocks": long_blocks,
        "efficiency_flags": efficiency_flags,
        "system_review_flags": system_flags,
        "tomorrow_task_candidates": tasks,
        "obsidian_context": _compact_context(obsidian_context),
    }
    summary["data_quality"] = _data_quality(reports, totals, sleep)
    return summary


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


def generate_ai_advice(
    settings: dict[str, Any],
    prompt_path: Path,
    summary: dict[str, Any],
) -> dict[str, Any]:
    model = {**settings["model"], **settings.get("report_model", {})}
    payload = {
        key: summary.get(key)
        for key in (
            "period",
            "daily_totals",
            "work_breakdown",
            "entertainment_breakdown",
            "phone_sleep_boundary",
            "ai_usage",
            "work_entertainment_mixing",
            "long_blocks",
            "efficiency_flags",
            "system_review_flags",
            "tomorrow_task_candidates",
            "obsidian_context",
            "data_quality",
        )
    }
    messages = [
        {"role": "system", "content": prompt_path.read_text(encoding="utf-8")},
        {
            "role": "user",
            "content": "请根据以下确定性日报候选输出建议JSON：\n"
            + json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
        },
    ]
    advice, generation = _request_json_report(model, messages)
    return {"advice": advice, "_generation": generation}


def _format_minutes(value: Any) -> str:
    if value is None:
        return "未知"
    minutes = int(round(float(value)))
    hours, mins = divmod(minutes, 60)
    return f"{hours}小时{mins}分" if hours else f"{mins}分"


def _rank_label(index: int) -> str:
    labels = ("①", "②", "③", "④", "⑤")
    return labels[index - 1] if 0 < index <= len(labels) else str(index)


def render_markdown(summary: dict[str, Any]) -> str:
    totals = summary["daily_totals"]
    sleep = summary["phone_sleep_boundary"]
    ai = summary["ai_usage"]
    lines = [
        f"📊 每日行为复盘：{summary['period']}",
        "",
        "🧮 总览",
        f"有效半小时报告：{summary.get('report_count', 0)} 份",
        f"总工作：{_format_minutes(totals['work_minutes'])}",
        f"总娱乐：{_format_minutes(totals['entertainment_minutes'])}",
        f"总购物：{_format_minutes(totals['shopping_minutes'])}",
        f"总通信：{_format_minutes(totals['communication_minutes'])}",
        f"AI使用：{_format_minutes(ai['total_minutes'])}",
        "",
        "🧠 工作分解",
    ]
    for item in summary["work_breakdown"]["by_category"]:
        lines.append(f"{item['name']}：{_format_minutes(item['minutes'])}")
    lines.extend(["", "📌 工作项目 Top"])
    for item in summary["work_breakdown"]["top_tasks"][:5]:
        lines.append(f"{item['name']}：{_format_minutes(item['minutes'])}")
    lines.extend(["", "🎮 娱乐项目 Top 3"])
    entertainment_tasks = summary.get("entertainment_breakdown", {}).get("top_tasks", [])
    if entertainment_tasks:
        for index, item in enumerate(entertainment_tasks[:3], start=1):
            lines.append(f"{_rank_label(index)} {item['name']}：{_format_minutes(item['minutes'])}")
    else:
        lines.append("没有明显娱乐项目")
    lines.extend(
        [
            "",
            "📱 手机睡眠边界",
            f"晚上停止玩手机：{sleep.get('last_phone_use_at_night') or '未知'}",
            f"早上拿起手机：{sleep.get('first_phone_use_in_morning') or '未知'}",
            f"扣除20分钟入睡后估计睡眠：{_format_minutes(sleep.get('sleep_estimate_minutes_minus_20'))}",
            "",
            "🤖 AI使用",
            f"总计：{_format_minutes(ai['total_minutes'])}",
            f"用于工作：{_format_minutes(ai['by_activity'].get('work', 0))}",
            f"用于娱乐：{_format_minutes(ai['by_activity'].get('entertainment', 0))}",
            f"用于通信：{_format_minutes(ai['by_activity'].get('brief_communication', 0))}",
            f"无法判断：{_format_minutes(ai['by_activity'].get('uncertain', 0))}",
            "",
            "🤖 AI用途 Top 3",
        ]
    )
    if ai.get("top_tasks"):
        for index, item in enumerate(ai["top_tasks"][:3], start=1):
            lines.append(f"{_rank_label(index)} {item['name']}：{_format_minutes(item['minutes'])}")
    else:
        lines.append("没有明显AI用途")
    lines.extend(["", "🧩 候选检查"])
    if summary.get("long_blocks"):
        lines.append("过长时间块：" + "；".join(
            f"{item['start']}-{item['end']} {item['label']} {item['minutes']}分钟"
            for item in summary["long_blocks"][:3]
        ))
    else:
        lines.append("过长时间块：没有明显候选")
    if summary.get("efficiency_flags"):
        lines.append("可能低效：" + "；".join(item["label"] for item in summary["efficiency_flags"][:3]))
    else:
        lines.append("可能低效：没有明显候选")
    if summary.get("system_review_flags"):
        lines.append("系统调整候选：" + "；".join(item["label"] for item in summary["system_review_flags"][:3]))
    else:
        lines.append("系统调整候选：没有明显候选")
    advice = summary.get("ai_advice")
    if advice:
        lines.extend(["", "💡 AI复盘建议", advice.get("concise_advice", "")])
        priorities = advice.get("tomorrow_priorities", [])
        if priorities:
            lines.append("")
            lines.append("明天优先：")
            for item in priorities[:3]:
                lines.append(
                    f"{item.get('title', '')}：{item.get('starter_action', '')}"
                )
    if summary["data_quality"].get("issues"):
        lines.extend(["", "⚠️ 数据质量"])
        lines.extend(str(item) for item in summary["data_quality"]["issues"])
    lines.append("")
    lines.append("说明：统计数字由脚本生成；AI只解释候选并给建议，不修改分钟数。")
    return "\n".join(lines)


def run(arguments: argparse.Namespace) -> dict[str, Any]:
    settings = load_json(Path(arguments.settings))
    output_root = Path(arguments.output_root)
    context = load_obsidian_context(
        Path(settings.get("obsidian_context_path", "/home/conrad/workspace/behavior-context-sync/context_snapshot.json")),
        output_root / "context_cache" / "current.json",
    )
    summary = build_daily_life_summary(
        output_root,
        arguments.date,
        context.get("ai_context") if context.get("available") else None,
        getattr(arguments, "morning_cutoff_hour", 9),
    )
    summary["context_source"] = context.get("context_source")
    summary["context_age_minutes"] = context.get("context_age_minutes")
    if not arguments.no_ai:
        _load_env_file(Path(arguments.env_file))
        try:
            ai_result = generate_ai_advice(settings, Path(arguments.prompt), summary)
            summary["ai_advice"] = ai_result["advice"]
            summary["_ai_generation"] = ai_result["_generation"]
        except Exception as error:
            summary["ai_advice_error"] = f"{type(error).__name__}: {error}"
    target_dir = output_root / "statistics" / "daily_life"
    json_path = target_dir / f"{arguments.date.isoformat()}.json"
    md_path = target_dir / f"{arguments.date.isoformat()}.md"
    atomic_write_json(json_path, summary)
    atomic_write_text(md_path, render_markdown(summary))
    return {
        "status": "completed",
        "date": arguments.date.isoformat(),
        "json": str(json_path),
        "markdown": str(md_path),
        "ai_advice": "ai_advice" in summary,
        "ai_error": summary.get("ai_advice_error"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate deterministic daily life statistics and optional AI advice.")
    parser.add_argument("--settings", default=str(DEFAULT_SETTINGS))
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--prompt", default=str(DEFAULT_PROMPT))
    parser.add_argument("--env-file", default=str(DEFAULT_ENV))
    parser.add_argument("--date", type=date.fromisoformat)
    parser.add_argument("--morning-cutoff-hour", type=int, default=9)
    parser.add_argument("--no-ai", action="store_true")
    args = parser.parse_args()
    if args.date is None:
        args.date = datetime.now(TIMEZONE).date() - timedelta(days=1)
    result = run(args)
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["status"] == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
