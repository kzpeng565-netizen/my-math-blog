from __future__ import annotations

import json
import os
import secrets
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


TIMEZONE = ZoneInfo("Asia/Shanghai")
PROJECT_ROOT = Path("/home/conrad/workspace/activitywatch-advisor")
ANNOTATION_ROOT = PROJECT_ROOT / "data" / "user_annotations"
MAX_MESSAGE_CHARACTERS = 500

CATEGORIES = {
    0: ("wrong_behavior_judgment", "AI行为判断错误"),
    1: ("data_or_device_error", "数据缺失或设备状态错误"),
    2: ("invalid_ai_output", "AI输出数据不符合要求"),
    3: ("bad_recommendation", "推荐任务或建议不合适"),
    4: ("other", "其他问题"),
}

RELATED_PATHS = {
    "ai_report_markdown": ("ai_reports", ".md"),
    "ai_report_json": ("ai_reports", ".json"),
    "context_snapshot": ("context_snapshots", ".json"),
    "computer_facts": ("computer_facts", ".json"),
    "phone_facts": ("phone_facts", ".json"),
    "tablet_facts": ("tablet_facts", ".json"),
    "combined_facts": ("combined_facts", ".json"),
    "semantic_timeline": ("semantic_timelines", ".json"),
    "mixing_metrics": ("mixing_metrics", ".json"),
}


class AnnotationError(ValueError):
    def __init__(self, error: str):
        super().__init__(error)
        self.error = error


def now_shanghai() -> datetime:
    return datetime.now(TIMEZONE)


def _iso(value: datetime) -> str:
    return value.astimezone(TIMEZONE).isoformat(timespec="seconds")


def _display_time(value: str) -> str:
    return datetime.fromisoformat(value).astimezone(TIMEZONE).strftime(
        "%Y-%m-%d %H:%M:%S"
    )


def _display_clock(value: str) -> str:
    return datetime.fromisoformat(value).astimezone(TIMEZONE).strftime("%H:%M")


def _relative(path: Path) -> str:
    return path.relative_to(PROJECT_ROOT).as_posix()


def _relative_to(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def atomic_write_bytes(target: Path, body: bytes) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    os.chmod(target.parent, 0o700)
    descriptor, temporary_name = tempfile.mkstemp(
        dir=target.parent,
        prefix=f".{target.name}.",
        suffix=".tmp",
    )
    try:
        with os.fdopen(descriptor, "wb") as temporary:
            temporary.write(body)
            temporary.flush()
            os.fsync(temporary.fileno())
        os.chmod(temporary_name, 0o600)
        os.replace(temporary_name, target)
    except Exception:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def atomic_write_text(target: Path, text: str) -> None:
    atomic_write_bytes(target, text.encode("utf-8"))


def half_hour_window(when: datetime) -> dict[str, str]:
    local = when.astimezone(TIMEZONE)
    minute = 30 if local.minute >= 30 else 0
    start = local.replace(minute=minute, second=0, microsecond=0)
    end = start + timedelta(minutes=30)
    return {"start": _iso(start), "end": _iso(end)}


def candidate_windows(when: datetime) -> list[dict[str, str]]:
    current = half_hour_window(when)
    previous_start = datetime.fromisoformat(current["start"]) - timedelta(minutes=30)
    previous_end = datetime.fromisoformat(current["start"])
    return [
        {"start": _iso(previous_start), "end": _iso(previous_end)},
        current,
    ]


def validate_annotation_fields(category_value: Any, message_value: Any) -> tuple[int, str]:
    try:
        category_index = int(str(category_value))
    except (TypeError, ValueError):
        raise AnnotationError("invalid_category")
    if category_index not in CATEGORIES:
        raise AnnotationError("invalid_category")

    message = "" if message_value is None else str(message_value)
    message = message.strip()
    if len(message) > MAX_MESSAGE_CHARACTERS:
        raise AnnotationError("message_too_long")
    if category_index == 4 and not message:
        raise AnnotationError("message_required")
    return category_index, message


def make_annotation_id(received_at: datetime) -> str:
    stamp = received_at.astimezone(TIMEZONE).strftime("%Y%m%d-%H%M%S")
    return f"{stamp}-{secrets.token_hex(3)}"


def _report_time(path: Path) -> datetime | None:
    try:
        if path.suffix == ".json":
            report = json.loads(path.read_text(encoding="utf-8"))
            period = report.get("period")
            if isinstance(period, str) and "/" in period:
                return datetime.fromisoformat(period.split("/", 1)[0]).astimezone(TIMEZONE)
    except (OSError, json.JSONDecodeError, ValueError):
        pass
    try:
        day = path.parent.name
        hour, minute = path.stem.split("-", 1)
        return datetime.fromisoformat(f"{day}T{hour}:{minute}:00+08:00")
    except ValueError:
        return None


def find_primary_related_report(
    received_at: datetime,
    project_root: Path = PROJECT_ROOT,
) -> str | None:
    reports_root = project_root / "data" / "ai_reports"
    if not reports_root.exists():
        return None
    received = received_at.astimezone(TIMEZONE)
    candidates: list[tuple[float, Path]] = []
    lower = received - timedelta(minutes=90)
    for path in reports_root.glob("*/*.md"):
        report_time = _report_time(path)
        try:
            mtime = datetime.fromtimestamp(path.stat().st_mtime, TIMEZONE)
        except OSError:
            continue
        effective_time = max(time for time in (report_time, mtime) if time is not None)
        if lower <= effective_time <= received:
            candidates.append((effective_time.timestamp(), path))
    if not candidates:
        return None
    return _relative_to(max(candidates, key=lambda item: item[0])[1], project_root)


def related_paths_for_report(
    primary_related_report: str | None,
    project_root: Path = PROJECT_ROOT,
) -> dict[str, str | None]:
    if not primary_related_report:
        return {key: None for key in RELATED_PATHS}
    report_path = project_root / primary_related_report
    day = report_path.parent.name
    window = report_path.stem
    result: dict[str, str | None] = {}
    for key, (directory, suffix) in RELATED_PATHS.items():
        candidate = project_root / "data" / directory / day / f"{window}{suffix}"
        result[key] = _relative_to(candidate, project_root) if candidate.exists() else None
    return result


def build_annotation(
    category_value: Any,
    message_value: Any,
    received_at: datetime | None = None,
    project_root: Path = PROJECT_ROOT,
) -> dict[str, Any]:
    category_index, message = validate_annotation_fields(category_value, message_value)
    category, label = CATEGORIES[category_index]
    received = received_at or now_shanghai()
    annotation_id = make_annotation_id(received)
    primary_report = find_primary_related_report(received, project_root)
    return {
        "schema_version": 1,
        "annotation_id": annotation_id,
        "received_at": _iso(received),
        "source": "phone_automate",
        "device": "phone",
        "category_index": category_index,
        "category": category,
        "category_label": label,
        "message": message,
        "status": "unreviewed",
        "current_half_hour_window": half_hour_window(received),
        "candidate_half_hour_windows": candidate_windows(received),
        "primary_related_report": primary_report,
        "related_paths": related_paths_for_report(primary_report, project_root),
        "correlation_notes": [],
    }


def annotation_json_path(
    annotation: dict[str, Any],
    annotation_root: Path = ANNOTATION_ROOT,
) -> Path:
    received = datetime.fromisoformat(annotation["received_at"]).astimezone(TIMEZONE)
    return annotation_root / "raw" / received.date().isoformat() / (
        f"{annotation['annotation_id']}.json"
    )


def save_raw_annotation(
    annotation: dict[str, Any],
    annotation_root: Path = ANNOTATION_ROOT,
) -> Path:
    target = annotation_json_path(annotation, annotation_root)
    for directory in (annotation_root, annotation_root / "raw", target.parent):
        directory.mkdir(parents=True, exist_ok=True)
        os.chmod(directory, 0o700)
    if target.exists():
        raise FileExistsError(target)
    body = json.dumps(annotation, ensure_ascii=False, indent=2).encode("utf-8") + b"\n"
    atomic_write_bytes(target, body)
    return target


def load_raw_annotations(annotation_root: Path = ANNOTATION_ROOT) -> list[dict[str, Any]]:
    annotations = []
    for path in sorted((annotation_root / "raw").glob("*/*.json")):
        try:
            item = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(item, dict):
            annotations.append(item)
    return annotations


def _line_value(value: str | None) -> str:
    return value if value else "无"


def _annotation_markdown(annotation: dict[str, Any]) -> str:
    message = annotation.get("message") or "未填写"
    current = annotation["current_half_hour_window"]
    related = annotation.get("related_paths", {})
    candidates = annotation.get("candidate_half_hour_windows", [])
    candidate_text = "；".join(
        f"{_display_clock(item['start'])}-{_display_clock(item['end'])}"
        for item in candidates
    )
    lines = [
        f"## {_display_clock(annotation['received_at'])} {annotation['category_label']}",
        "",
        "- 状态：未处理",
        f"- 接收时间：{_display_time(annotation['received_at'])}",
        f"- 编号：{annotation['annotation_id']}",
        f"- 用户说明：{message}",
        f"- 主要关联报告：{_line_value(annotation.get('primary_related_report'))}",
        (
            "- 当前时间窗口："
            f"{_display_clock(current['start'])}-{_display_clock(current['end'])}"
        ),
        f"- 候选时间窗口：{candidate_text}",
        "",
        "相关文件：",
        "",
        f"- AI报告：{_line_value(related.get('ai_report_markdown'))}",
        f"- 电脑事实：{_line_value(related.get('computer_facts'))}",
        f"- 手机事实：{_line_value(related.get('phone_facts'))}",
        f"- 平板事实：{_line_value(related.get('tablet_facts'))}",
        f"- 综合事实：{_line_value(related.get('combined_facts'))}",
        f"- 语义时间线：{_line_value(related.get('semantic_timeline'))}",
        f"- 混杂指标：{_line_value(related.get('mixing_metrics'))}",
        f"- 任务上下文：{_line_value(related.get('context_snapshot'))}",
        "",
    ]
    return "\n".join(lines)


def render_daily_markdown(day: str, annotations: list[dict[str, Any]]) -> str:
    selected = [
        item
        for item in annotations
        if datetime.fromisoformat(item["received_at"]).astimezone(TIMEZONE)
        .date()
        .isoformat()
        == day
    ]
    selected.sort(key=lambda item: item["received_at"])
    parts = [f"# {day} 系统异常记录", ""]
    parts.extend(_annotation_markdown(item) for item in selected)
    return "\n".join(parts).rstrip() + "\n"


def render_unreviewed_markdown(annotations: list[dict[str, Any]]) -> str:
    selected = [
        item for item in annotations if item.get("status", "unreviewed") == "unreviewed"
    ]
    selected.sort(key=lambda item: item["received_at"], reverse=True)
    parts = ["# 未处理系统异常记录", ""]
    parts.extend(_annotation_markdown(item) for item in selected)
    return "\n".join(parts).rstrip() + "\n"


def rebuild_markdown_summaries(
    annotation_root: Path = ANNOTATION_ROOT,
) -> dict[str, Path]:
    annotations = load_raw_annotations(annotation_root)
    days = sorted(
        {
            datetime.fromisoformat(item["received_at"])
            .astimezone(TIMEZONE)
            .date()
            .isoformat()
            for item in annotations
            if "received_at" in item
        }
    )
    written: dict[str, Path] = {}
    for day in days:
        target = annotation_root / "daily" / f"{day}.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        os.chmod(target.parent, 0o700)
        atomic_write_text(target, render_daily_markdown(day, annotations))
        written[f"daily/{day}"] = target
    target = annotation_root / "UNREVIEWED.md"
    annotation_root.mkdir(parents=True, exist_ok=True)
    os.chmod(annotation_root, 0o700)
    atomic_write_text(target, render_unreviewed_markdown(annotations))
    written["unreviewed"] = target
    return written


def receive_annotation(
    category_value: Any,
    message_value: Any,
    received_at: datetime | None = None,
    annotation_root: Path = ANNOTATION_ROOT,
    project_root: Path = PROJECT_ROOT,
) -> dict[str, Any]:
    annotation = build_annotation(category_value, message_value, received_at, project_root)
    save_raw_annotation(annotation, annotation_root)
    try:
        rebuild_markdown_summaries(annotation_root)
    except Exception as exc:
        annotation["markdown_rebuild_error"] = exc.__class__.__name__
    return annotation
