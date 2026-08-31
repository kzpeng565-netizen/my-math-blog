from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import logging
import os
import re
import shutil
import subprocess
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


TIMEZONE = ZoneInfo("Asia/Shanghai")
EXPORTER_VERSION = 6
GOAL_MATERIAL_SCHEMA_VERSION = 2
ALLOWED_MATERIAL_EXTENSIONS = {".pdf", ".md", ".txt"}
SOURCE_NAMES = {
    "profile": "Profile.md",
    "task_collection": "ToDo-任务集合.md",
    "planned_tasks": "ToDo-已经规划好的任务.md",
    "completed_tasks": "已完成任务.md",
    "pomodoro_log": "番茄钟log.md",
    "goal_materials": "目标模式资料清单.md",
}
DEFAULT_CONFIG = Path(__file__).with_name("behavior_context_exporter.json")
POMODORO_WARNING = (
    "番茄钟日志在假期中记录不完整，只能作为主动工作信号。"
    "无记录不能解释为无学习，且不能用于判断具体任务进度。"
)
TASK_RE = re.compile(r"^\s*-\s*\[([ xX])\]\s+#task(?:\s+|$)(.*)$")
TASK_ID_RE = re.compile(r"\s+(\^[A-Za-z0-9-]{4,32})\s*$")
DATE_RE = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")
POMODORO_RE = re.compile(
    r"🍅\s*\(pomodoro::\s*WORK\)\s*"
    r"\(duration::\s*(\d+)\s*m\).*?"
    r"\(begin::\s*(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})\).*?"
    r"\(end::\s*(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})\)",
    re.DOTALL,
)
PRIORITIES = (("🔺", "highest"), ("⏫", "high"), ("🔼", "medium"),
              ("🔽", "low"), ("⏬", "lowest"))


def now_local() -> datetime:
    return datetime.now(TIMEZONE)


def iso(value: datetime) -> str:
    return value.isoformat(timespec="seconds")


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def atomic_write_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("wb") as handle:
        handle.write(content)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def atomic_write_json(path: Path, value: Any) -> None:
    encoded = json.dumps(value, ensure_ascii=False, indent=2).encode("utf-8") + b"\n"
    json.loads(encoded.decode("utf-8"))
    atomic_write_bytes(path, encoded)


def load_config(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def discover_sources(config: dict[str, Any], config_path: Path) -> dict[str, Path]:
    vault_root = Path(config["vault_root"]).resolve()
    keys = {
        "profile": "profile_path",
        "task_collection": "task_collection_path",
        "planned_tasks": "planned_tasks_path",
        "completed_tasks": "completed_tasks_path",
        "pomodoro_log": "pomodoro_log_path",
        "goal_materials": "goal_materials_path",
    }
    resolved: dict[str, Path] = {}
    changed = False
    for source_key, config_key in keys.items():
        configured = config.get(config_key)
        configured_path = Path(configured).resolve() if configured else None
        if configured_path and configured_path.is_file():
            resolved[source_key] = configured_path
            continue
        matches = list(vault_root.rglob(SOURCE_NAMES[source_key]))
        if len(matches) != 1:
            raise ValueError(
                f"{SOURCE_NAMES[source_key]} expected exactly one match, found {len(matches)}"
            )
        resolved[source_key] = matches[0].resolve()
        config[config_key] = str(matches[0].resolve())
        changed = True
    if changed:
        atomic_write_json(config_path, config)
    return resolved


def source_info(path: Path, content: bytes) -> dict[str, Any]:
    modified = datetime.fromtimestamp(path.stat().st_mtime, TIMEZONE)
    return {
        "path": str(path),
        "modified_at": iso(modified),
        "sha256": sha256_bytes(content),
    }


def _metadata_value(pattern: str, text: str) -> str | None:
    match = re.search(pattern, text)
    return match.group(1).strip() if match else None


def parse_task_line(
    raw_line: str,
    category: str | None,
    planning_batch: str | None,
    order: int,
    *,
    include_completed: bool = False,
) -> dict[str, Any] | None:
    match = TASK_RE.match(raw_line)
    if not match or (match.group(1).lower() == "x" and not include_completed):
        return None
    body = match.group(2).strip()
    task_id_match = TASK_ID_RE.search(body)
    task_id = task_id_match.group(1) if task_id_match else None
    if task_id_match:
        body = body[: task_id_match.start()].rstrip()
    scheduled = _metadata_value(r"⏳\s*(\d{4}-\d{2}-\d{2})", body)
    due = _metadata_value(r"📅\s*(\d{4}-\d{2}-\d{2})", body)
    tomato = re.search(r"\[🍅::\s*(?:(\d+)\s*/\s*(\d+))?\s*\]", body)
    recurrence = _metadata_value(
        r"🔁\s*(.*?)(?=\s+(?:⏳|📅|🔺|⏫|🔼|🔽|⏬|\[🍅::)|$)", body
    )
    completed_on = _metadata_value(r"✅\s*(\d{4}-\d{2}-\d{2})", body)
    priority = "normal"
    for symbol, value in PRIORITIES:
        if symbol in body:
            priority = value
            break
    title = re.sub(r"\[🍅::.*?\]", "", body)
    title = re.sub(r"⏳\s*\d{4}-\d{2}-\d{2}", "", title)
    title = re.sub(r"📅\s*\d{4}-\d{2}-\d{2}", "", title)
    title = re.sub(r"✅\s*\d{4}-\d{2}-\d{2}", "", title)
    title = re.sub(r"🔁\s*.*?(?=\s+(?:⏳|📅|🔺|⏫|🔼|🔽|⏬)|$)", "", title)
    title = re.sub(r"[🔺🔼🔽]", "", title).replace("⏫", "").replace("⏬", "")
    title = re.sub(r"\s+", " ", title).strip()
    return {
        "task_id": task_id,
        "title": title,
        "category": category,
        "planning_batch": planning_batch,
        "priority": priority,
        "scheduled_date": scheduled,
        "due_date": due,
        "recurrence": recurrence,
        "tomatoes_completed": int(tomato.group(1)) if tomato and tomato.group(1) else None,
        "tomatoes_total": int(tomato.group(2)) if tomato and tomato.group(2) else None,
        "source_order": order,
        "completed": match.group(1).lower() == "x",
        "completed_on": completed_on,
        "raw_line": raw_line,
    }


def parse_tasks(markdown: str, today: date, collection_markdown: str = "") -> dict[str, Any]:
    current_h1: str | None = None
    current_h2: str | None = None
    tasks: list[dict[str, Any]] = []
    h1_positions: list[tuple[int, str]] = []
    warnings: list[str] = []
    lines = markdown.splitlines()
    for index, line in enumerate(lines):
        if line.startswith("# "):
            current_h1 = line[2:].strip()
            current_h2 = None
            if DATE_RE.search(current_h1):
                h1_positions.append((index, current_h1))
        elif line.startswith("## "):
            current_h2 = line[3:].strip()
        if TASK_RE.match(line):
            try:
                parsed = parse_task_line(
                    line, current_h2, current_h1, len(tasks) + 1
                )
                if parsed:
                    parsed["task_source"] = "planned"
                    tasks.append(parsed)
            except (TypeError, ValueError) as error:
                warnings.append(f"line {index + 1}: {error}")
    latest_heading = h1_positions[-1][1] if h1_positions else None
    notes = ""
    if h1_positions:
        start = h1_positions[-1][0] + 1
        end = next(
            (i for i in range(start, len(lines)) if lines[i].startswith("# ")),
            len(lines),
        )
        note_lines = [line for line in lines[start:end] if not TASK_RE.match(line)]
        notes = "\n".join(note_lines).strip()
    buckets: dict[str, list[dict[str, Any]]] = {
        "unassigned_tasks": [],
        "overdue_tasks": [],
        "today_tasks": [],
        "near_term_tasks": [],
        "later_tasks": [],
        "recurring_tasks": [],
    }
    for index, line in enumerate(collection_markdown.splitlines(), start=1):
        try:
            parsed = parse_task_line(line, "待正式安排", "树莓派新增", len(tasks) + 1)
            if parsed:
                parsed["task_source"] = "collection"
                tasks.append(parsed)
        except (TypeError, ValueError) as error:
            warnings.append(f"collection line {index}: {error}")
    for task in tasks:
        if task.get("task_source") == "collection" and not task["scheduled_date"]:
            buckets["unassigned_tasks"].append(task)
            continue
        if task["recurrence"]:
            buckets["recurring_tasks"].append(task)
            continue
        scheduled = task["scheduled_date"]
        if not scheduled:
            buckets["later_tasks"].append(task)
            continue
        try:
            scheduled_day = date.fromisoformat(scheduled)
        except ValueError:
            warnings.append(f"invalid scheduled date in task {task['source_order']}")
            buckets["later_tasks"].append(task)
            continue
        if scheduled_day < today:
            buckets["overdue_tasks"].append(task)
        elif scheduled_day == today:
            buckets["today_tasks"].append(task)
        elif scheduled_day <= today + timedelta(days=3):
            buckets["near_term_tasks"].append(task)
        else:
            buckets["later_tasks"].append(task)
    return {
        "open_task_count": len(tasks),
        "missing_task_id_count": sum(1 for task in tasks if not task["task_id"]),
        **buckets,
        "latest_plan_heading": latest_heading,
        "latest_plan_notes_markdown": notes,
        "parser_warnings": warnings,
    }


def parse_completed_tasks(
    markdown: str,
    *,
    source_modified_at: str | None = None,
    today: date | None = None,
    recent_days: int = 120,
) -> dict[str, Any]:
    completed: list[dict[str, Any]] = []
    for order, line in enumerate(markdown.splitlines(), start=1):
        parsed = parse_task_line(
            line,
            category=None,
            planning_batch=None,
            order=order,
            include_completed=True,
        )
        if parsed and parsed["completed"]:
            completed.append(parsed)
    # The archive may contain repeated blocks.  Stable task id + completion
    # date is the reliable event identity; direct Obsidian completion only has
    # day precision, so the export says so instead of inventing a clock time.
    deduplicated: dict[str, dict[str, Any]] = {}
    cutoff = (today or now_local().date()) - timedelta(days=recent_days)
    for task in completed:
        task_id = task.get("task_id")
        completed_on = task.get("completed_on")
        if not task_id or not completed_on:
            continue
        try:
            completed_day = date.fromisoformat(completed_on)
        except ValueError:
            continue
        if completed_day < cutoff:
            continue
        event_id = f"{task_id}@{completed_on}"
        deduplicated[event_id] = {
            "event_id": event_id,
            "task_id": task_id,
            "title": task.get("title"),
            "completed_at": completed_on,
            "completion_time_precision": "date",
            "task_modified_at": source_modified_at,
            "scheduled_date": task.get("scheduled_date"),
            "due_date": task.get("due_date"),
            "tomatoes_completed": task.get("tomatoes_completed"),
            "tomatoes_total": task.get("tomatoes_total"),
        }
    return {
        "completed_task_count": len(completed),
        "missing_task_id_count": sum(1 for task in completed if not task["task_id"]),
        "recent_events": sorted(
            deduplicated.values(), key=lambda item: (item["completed_at"], item["task_id"])
        )[-500:],
        "event_identity": "task_id@completed_date",
    }


HANDWRITING_PLACEHOLDER = "[手写笔记：笔画采样已省略，请以周围文字或识别转写为准。]"
_HIDDEN_INK_RE = re.compile(
    r"(?ms)^[ \t]*%%inkedmark[ \t]*\r?\n.*?^[ \t]*%%[ \t]*(?:\r?\n|$)"
)
_FENCED_INK_RE = re.compile(
    r"(?ms)^[ \t]*(?P<fence>`{3,}|~{3,})[ \t]*inkedmark\b[^\r\n]*\r?\n"
    r"(?P<body>.*?)^[ \t]*(?P=fence)[ \t]*(?:\r?\n|$)"
)
_CAPTION_RE = re.compile(r"(?mi)^[ \t]*caption:[ \t]*(?P<caption>[^\r\n]*)$")
_MANAGED_TEXT_RE = re.compile(
    r"(?s)<!--inkedmark-text-->(.*?)<!--/inkedmark-text-->"
)
_MANAGED_PAGE_RE = re.compile(r"<!--inkedmark-page:(\d+)-->")
_MARKDOWN_IMAGE_RE = re.compile(
    r"!\[([^\r\n\]]*)\]\((?:<([^>\r\n]+)>|([^\s)\r\n]+))\)"
)


def sanitize_material_text(text: str) -> str:
    """Remove MathInk samples/base64 while retaining AI-readable Markdown."""

    def replace_fenced(match: re.Match[str]) -> str:
        caption_match = _CAPTION_RE.search(match.group("body"))
        caption = caption_match.group("caption").strip() if caption_match else ""
        if caption:
            return f"[手写笔记：笔画采样已省略。识别转写：{caption}]\n"
        return HANDWRITING_PLACEHOLDER + "\n"

    text = _FENCED_INK_RE.sub(replace_fenced, text)
    text = _HIDDEN_INK_RE.sub(HANDWRITING_PLACEHOLDER + "\n", text)
    text = re.sub(
        r"data:image/[^;\s]+;base64,[A-Za-z0-9+/=\r\n]+",
        "[图片数据已省略]",
        text,
        flags=re.IGNORECASE,
    )
    # Preserve the managed transcription itself but remove implementation-only
    # markers. MathInk page headings remain ordinary Markdown.
    text = text.replace("<!--inkedmark-text-->", "")
    text = text.replace("<!--/inkedmark-text-->", "")
    text = re.sub(r"<!--/?inkedmark-page:\d+-->", "", text)
    # Standard Markdown image projection remains visible. World-space layout
    # metadata is irrelevant to the Goal Agent and may be large/noisy.
    text = re.sub(r"<!--\s*mathink:image\s+\{[^\r\n]*\}\s*-->", "", text)
    return text


def material_text_metadata(raw_text: str) -> dict[str, Any]:
    managed = _MANAGED_TEXT_RE.search(raw_text)
    images = [
        {
            "alt": match.group(1).strip(),
            "path": (match.group(2) or match.group(3) or "").strip(),
        }
        for match in _MARKDOWN_IMAGE_RE.finditer(raw_text)
    ][:100]
    return {
        "note_format": (
            "mathink_markdown"
            if _HIDDEN_INK_RE.search(raw_text)
            or _FENCED_INK_RE.search(raw_text)
            or managed
            or "mathink:image" in raw_text
            else "markdown"
        ),
        "has_handwriting_payload": bool(
            _HIDDEN_INK_RE.search(raw_text) or _FENCED_INK_RE.search(raw_text)
        ),
        "has_managed_recognition": bool(managed and managed.group(1).strip()),
        "recognized_pages": sorted(
            {int(value) for value in _MANAGED_PAGE_RE.findall(raw_text)}
        ),
        "markdown_images": images,
        "image_binary_exported": False,
    }


def _within_vault(path: Path, root: Path) -> bool:
    return path == root or root in path.parents


def _excluded_material_path(path: Path, authorization_root: Path) -> bool:
    try:
        relative_parts = path.relative_to(authorization_root).parts
    except ValueError:
        return True
    if any(part.startswith(".") for part in relative_parts[:-1]):
        return True
    name = path.name.lower()
    return (
        name.startswith(".")
        or name.startswith("~")
        or name.startswith("~syncthing~")
        or ".sync-conflict-" in name
        or name.endswith(".ink.md")
        or ".ink.sync-conflict-" in name
        or name.endswith(".tmp")
        or name.endswith(".temp")
        or name.endswith(".bak")
    )


def _manifest_extensions(line: str) -> set[str]:
    match = re.search(
        r"(?:extensions?|扩展名)\s*=\s*([A-Za-z0-9.,\s]+)",
        line,
        re.IGNORECASE,
    )
    if not match:
        return set(ALLOWED_MATERIAL_EXTENSIONS)
    values = {
        "." + value.strip().lower().lstrip(".")
        for value in match.group(1).split(",")
        if value.strip()
    }
    if not values or not values.issubset(ALLOWED_MATERIAL_EXTENSIONS):
        return set()
    return values


def parse_goal_material_manifest(markdown: str, vault_root: Path) -> list[dict[str, Any]]:
    root = vault_root.resolve()
    result: list[dict[str, Any]] = []
    seen: set[Path] = set()
    for line_number, line in enumerate(markdown.splitlines(), start=1):
        if not re.match(r"^\s*-\s*\[[xX]\]\s+", line):
            continue
        wiki = re.search(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]", line)
        markdown_link = re.search(r"\[[^\]]*\]\(([^)]+)\)", line)
        explicit = re.search(
            r"(?:路径|path)\s*[:：]\s*`?([^`|]+?)`?(?:\s*[|｜].*)?$",
            line,
            re.IGNORECASE,
        )
        raw_target = (wiki.group(1) if wiki else markdown_link.group(1) if markdown_link else explicit.group(1) if explicit else "").strip()
        if not raw_target:
            result.append({"line": line_number, "status": "missing_path", "label": line.strip()[:240]})
            continue
        extensions = _manifest_extensions(line)
        if not extensions:
            result.append(
                {
                    "line": line_number,
                    "status": "invalid_extensions",
                    "label": line.strip()[:240],
                }
            )
            continue
        candidate = Path(raw_target)
        if not candidate.is_absolute():
            candidate = root / candidate
        if not candidate.exists() and not candidate.suffix:
            markdown_candidate = candidate.with_suffix(".md")
            if markdown_candidate.is_file():
                candidate = markdown_candidate
        try:
            resolved = candidate.resolve()
        except OSError:
            result.append({"line": line_number, "status": "invalid_path", "label": line.strip()[:240]})
            continue
        if not _within_vault(resolved, root) or resolved == root:
            result.append({"line": line_number, "status": "not_allowed", "label": line.strip()[:240]})
            continue
        label = re.sub(r"^\s*-\s*\[[xX]\]\s+", "", line)
        label = re.sub(r"\[\[[^\]]+\]\]|\[[^\]]*\]\([^)]+\)", "", label)
        label = re.sub(r"(?:路径|path)\s*[:：].*$", "", label, flags=re.IGNORECASE)
        label = re.sub(
            r"(?:extensions?|扩展名)\s*=.*$",
            "",
            label,
            flags=re.IGNORECASE,
        ).strip(" |｜-")
        if resolved.is_dir():
            files = [
                path.resolve()
                for path in resolved.rglob("*")
                if path.is_file()
                and path.suffix.lower() in extensions
                and not _excluded_material_path(path, resolved)
            ]
            files.sort(key=lambda path: path.relative_to(root).as_posix().casefold())
            if len(files) > 5000:
                result.append(
                    {
                        "line": line_number,
                        "status": "too_many_files",
                        "source_path": resolved.relative_to(root).as_posix(),
                        "label": label or resolved.name,
                    }
                )
                continue
            new_count = 0
            for file_path in files:
                if file_path in seen:
                    continue
                seen.add(file_path)
                new_count += 1
                relative = file_path.relative_to(root).as_posix()
                result.append(
                    {
                        "line": line_number,
                        "status": "authorized",
                        "authorization_kind": "directory",
                        "authorization_root": resolved.relative_to(root).as_posix(),
                        "source_path": str(file_path),
                        "vault_relative_path": relative,
                        "title": f"{label or resolved.name} · {relative}",
                        "extensions": sorted(value.lstrip(".") for value in extensions),
                    }
                )
            if new_count == 0:
                result.append(
                    {
                        "line": line_number,
                        "status": "authorized_empty_directory",
                        "authorization_kind": "directory",
                        "authorization_root": resolved.relative_to(root).as_posix(),
                        "source_path": str(resolved),
                        "vault_relative_path": resolved.relative_to(root).as_posix(),
                        "title": label or resolved.name,
                        "extensions": sorted(value.lstrip(".") for value in extensions),
                    }
                )
            continue
        if not resolved.is_file():
            result.append({"line": line_number, "status": "missing_file", "source_path": str(resolved), "label": line.strip()[:240]})
            continue
        if (
            resolved.suffix.lower() not in extensions
            or resolved.suffix.lower() not in ALLOWED_MATERIAL_EXTENSIONS
            or _excluded_material_path(resolved, resolved.parent)
        ):
            result.append({"line": line_number, "status": "not_allowed", "label": line.strip()[:240]})
            continue
        if resolved in seen:
            continue
        seen.add(resolved)
        result.append(
            {
                "line": line_number,
                "status": "authorized",
                "authorization_kind": "file",
                "source_path": str(resolved),
                "vault_relative_path": resolved.relative_to(root).as_posix(),
                "title": label or resolved.stem,
                "extensions": sorted(value.lstrip(".") for value in extensions),
            }
        )
    return result


def _chunks_from_text(text: str, *, pages: bool) -> list[dict[str, Any]]:
    chunks: list[dict[str, Any]] = []
    page_texts = text.split("\f") if pages else [text]
    for page_number, page in enumerate(page_texts, start=1):
        clean = sanitize_material_text(page).strip()
        if not clean:
            continue
        offset = 0
        while offset < len(clean):
            end = min(len(clean), offset + 6000)
            if end < len(clean):
                boundary = clean.rfind("\n", offset + 3500, end)
                if boundary > offset:
                    end = boundary
            segment = clean[offset:end].strip()
            if segment:
                before = clean[:offset]
                chunks.append({
                    "page_start": page_number,
                    "page_end": page_number,
                    "line_start": before.count("\n") + 1,
                    "line_end": before.count("\n") + segment.count("\n") + 1,
                    "text": segment,
                })
            offset = max(end, offset + 1)
    return chunks


def _extract_material(
    path: Path,
    config: dict[str, Any],
) -> tuple[list[dict[str, Any]], int, dict[str, Any]]:
    if path.suffix.lower() in {".md", ".txt"}:
        text = path.read_text(encoding="utf-8")
        metadata = (
            material_text_metadata(text)
            if path.suffix.lower() == ".md"
            else {
                "note_format": "text",
                "has_handwriting_payload": False,
                "has_managed_recognition": False,
                "recognized_pages": [],
                "markdown_images": [],
                "image_binary_exported": False,
            }
        )
        return _chunks_from_text(text, pages=False), 1, metadata
    executable = str(config.get("pdftotext_path") or shutil.which("pdftotext") or "")
    if not executable:
        raise RuntimeError("pdftotext is not available")
    completed = subprocess.run(
        [executable, "-layout", "-enc", "UTF-8", str(path), "-"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=180,
    )
    text = completed.stdout.decode("utf-8", errors="replace")
    pages = text.split("\f")
    return (
        _chunks_from_text(text, pages=True),
        max(1, len([page for page in pages if page.strip()])),
        {
            "note_format": "pdf_text",
            "has_handwriting_payload": False,
            "has_managed_recognition": False,
            "recognized_pages": [],
            "markdown_images": [],
            "image_binary_exported": False,
        },
    )


def export_goal_materials(
    config: dict[str, Any],
    manifest_markdown: str,
    export_dir: Path,
    generated_at: datetime,
) -> dict[str, Any]:
    materials_root = export_dir / "goal_agent" / "materials"
    vault_root = Path(config["vault_root"]).resolve()
    entries = parse_goal_material_manifest(manifest_markdown, vault_root)
    documents: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    empty_directories: list[dict[str, Any]] = []
    for entry in entries:
        if entry.get("status") == "authorized_empty_directory":
            empty_directories.append(
                {
                    key: entry.get(key)
                    for key in (
                        "line",
                        "title",
                        "vault_relative_path",
                        "authorization_root",
                        "extensions",
                    )
                }
            )
            continue
        if entry.get("status") != "authorized":
            errors.append(entry)
            continue
        path = Path(entry["source_path"])
        content = path.read_bytes()
        digest = sha256_bytes(content)
        relative_path = str(entry["vault_relative_path"])
        record_id = "material-" + hashlib.sha256(relative_path.casefold().encode("utf-8")).hexdigest()[:24]
        export_file = f"{record_id}-{digest[:16]}.json.gz"
        modified_at = iso(datetime.fromtimestamp(path.stat().st_mtime, TIMEZONE))
        try:
            chunks, page_count, metadata = _extract_material(path, config)
            payload = {
                "schema_version": GOAL_MATERIAL_SCHEMA_VERSION,
                "id": record_id,
                "title": entry["title"],
                "source_path": relative_path,
                "sha256": digest,
                "modified_at": modified_at,
                "generated_at": iso(generated_at),
                "page_count": page_count,
                "metadata": metadata,
                "chunks": chunks,
            }
            encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
            atomic_write_bytes(materials_root / export_file, gzip.compress(encoded, compresslevel=9))
            documents.append({
                "id": record_id,
                "title": entry["title"],
                "source_path": relative_path,
                "sha256": digest,
                "modified_at": modified_at,
                "page_count": page_count,
                "chunk_count": len(chunks),
                "export_file": export_file,
                "status": "ready",
                "metadata": metadata,
            })
        except (OSError, RuntimeError, subprocess.SubprocessError, UnicodeDecodeError) as error:
            errors.append({
                "line": entry.get("line"),
                "status": "extract_failed",
                "source_path": str(path),
                "error": f"{type(error).__name__}: {error}"[:300],
            })
    index = {
        "schema_version": GOAL_MATERIAL_SCHEMA_VERSION,
        "generated_at": iso(generated_at),
        "manifest_sha256": sha256_bytes(manifest_markdown.encode("utf-8")),
        "document_count": len(documents),
        "documents": documents,
        "empty_directories": empty_directories,
        "errors": errors,
    }
    index_path = materials_root / "index.json"
    previous_value: dict[str, Any] = {}
    if index_path.exists():
        try:
            previous_value = json.loads(index_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            previous_value = {}
    changed = any(
        previous_value.get(key) != index.get(key)
        for key in (
            "schema_version",
            "manifest_sha256",
            "documents",
            "empty_directories",
            "errors",
        )
    )
    atomic_write_json(index_path, index)
    return {
        "status": "ok" if not errors else "partial",
        "document_count": len(documents),
        "error_count": len(errors),
        "changed": changed,
    }


def parse_pomodoro(markdown: str, now: datetime) -> dict[str, Any]:
    sessions: list[dict[str, Any]] = []
    for match in POMODORO_RE.finditer(markdown):
        declared = int(match.group(1))
        begin = datetime.strptime(match.group(2), "%Y-%m-%d %H:%M").replace(
            tzinfo=TIMEZONE
        )
        end = datetime.strptime(match.group(3), "%Y-%m-%d %H:%M").replace(
            tzinfo=TIMEZONE
        )
        wall_minutes = (end - begin).total_seconds() / 60
        sessions.append(
            {
                "begin": begin,
                "end": end,
                "declared_minutes": declared,
                "wall_clock_minutes": round(wall_minutes, 2),
                "wall_clock_exceeds_declared_threshold": wall_minutes
                > max(declared * 2, declared + 30),
                "wall_clock_interpretation": (
                    "墙钟跨度可能包含暂停后继续计时，不代表实际工作时长或坏数据。"
                ),
            }
        )

    def window(delta: timedelta, with_days: bool = False) -> dict[str, Any]:
        selected = [s for s in sessions if now - delta <= s["end"] <= now]
        result = {
            "session_count": len(selected),
            "declared_minutes": sum(s["declared_minutes"] for s in selected),
        }
        if with_days:
            result["days_with_records"] = len({s["end"].date() for s in selected})
        return result

    work_markers = len(re.findall(r"pomodoro::\s*WORK", markdown))
    return {
        "reference_only": True,
        "last_recorded_session_end": iso(max(s["end"] for s in sessions))
        if sessions
        else None,
        "last_24h": window(timedelta(hours=24)),
        "last_3d": window(timedelta(days=3), True),
        "last_7d": window(timedelta(days=7), True),
        "data_quality": {
            "extended_wall_clock_interval_count": sum(
                1
                for s in sessions
                if s["wall_clock_exceeds_declared_threshold"]
            ),
            "manual_missing_log_notes": len(re.findall(r"忘记记录", markdown)),
            "malformed_session_count": max(0, work_markers - len(sessions)),
            "reliability": "low",
            "wall_clock_interpretation": (
                "end-begin 可能包含中途暂停后继续番茄钟的时间。"
                "工作量始终按 duration 声明值统计，较长墙钟跨度不视为负面信号。"
            ),
        },
        "interpretation_warning": POMODORO_WARNING,
    }


def build_snapshot(
    paths: dict[str, Path],
    contents: dict[str, bytes],
    generated_at: datetime,
    *,
    vault_root: Path | None = None,
) -> dict[str, Any]:
    decoded = {key: value.decode("utf-8") for key, value in contents.items()}
    completed_source = source_info(paths["completed_tasks"], contents["completed_tasks"])
    completed_stats = parse_completed_tasks(
        decoded["completed_tasks"],
        source_modified_at=completed_source["modified_at"],
        today=generated_at.date(),
    )
    authorized_materials = parse_goal_material_manifest(
        decoded["goal_materials"],
        (vault_root or paths["goal_materials"].parent).resolve(),
    )
    return {
        "schema_version": 1,
        "exporter_version": EXPORTER_VERSION,
        "generated_at": iso(generated_at),
        "timezone": "Asia/Shanghai",
        "sources": {
            key: source_info(paths[key], contents[key]) for key in SOURCE_NAMES
        },
        "profile": {
            "raw_markdown": decoded["profile"],
            "source_modified_at": source_info(paths["profile"], contents["profile"])[
                "modified_at"
            ],
            "content_hash": sha256_bytes(contents["profile"]),
        },
        "tasks": parse_tasks(decoded["planned_tasks"], generated_at.date(), decoded["task_collection"]),
        "task_sources": {
            "collection_markdown": decoded["task_collection"],
            "planned_markdown": decoded["planned_tasks"],
            "completed_stats": {
                key: value for key, value in completed_stats.items() if key != "recent_events"
            },
        },
        "task_events": {
            "completed_recent": completed_stats["recent_events"],
            "source_modified_at": completed_source["modified_at"],
            "event_identity": completed_stats["event_identity"],
        },
        "goal_materials": {
            "authorized_count": sum(
                1
                for item in authorized_materials
                if item.get("status")
                in {"authorized", "authorized_empty_directory"}
            ),
            "problem_count": sum(
                1
                for item in authorized_materials
                if item.get("status")
                not in {"authorized", "authorized_empty_directory"}
            ),
            "manifest_modified_at": source_info(paths["goal_materials"], contents["goal_materials"])["modified_at"],
        },
        "pomodoro": parse_pomodoro(decoded["pomodoro_log"], generated_at),
    }


def export(config_path: Path) -> dict[str, Any]:
    config = load_config(config_path)
    export_dir = Path(config["export_dir"]).resolve()
    log_dir = export_dir / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=log_dir / "exporter.log",
        encoding="utf-8",
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    checked_at = now_local()
    paths = discover_sources(config, config_path)
    contents = {key: path.read_bytes() for key, path in paths.items()}
    for content in contents.values():
        content.decode("utf-8")
    materials = export_goal_materials(
        config,
        contents["goal_materials"].decode("utf-8"),
        export_dir,
        checked_at,
    )
    snapshot_path = export_dir / "context_snapshot.json"
    old_hashes: dict[str, str] = {}
    old_exporter_version: int | None = None
    if snapshot_path.exists():
        try:
            old = json.loads(snapshot_path.read_text(encoding="utf-8"))
            old_exporter_version = old.get("exporter_version")
            old_hashes = {
                key: old["sources"][key]["sha256"] for key in SOURCE_NAMES
            }
        except (KeyError, TypeError, json.JSONDecodeError, UnicodeDecodeError):
            old_hashes = {}
    hashes = {key: sha256_bytes(value) for key, value in contents.items()}
    changed = (
        hashes != old_hashes
        or old_exporter_version != EXPORTER_VERSION
        or materials["changed"]
    )
    if changed:
        snapshot = build_snapshot(
            paths,
            contents,
            checked_at,
            vault_root=Path(config["vault_root"]),
        )
        atomic_write_json(snapshot_path, snapshot)
        for key, filename in SOURCE_NAMES.items():
            atomic_write_bytes(export_dir / "raw" / filename, contents[key])
        successful_at = iso(checked_at)
    else:
        old_heartbeat = export_dir / "sync_heartbeat.json"
        successful_at = iso(checked_at)
        if old_heartbeat.exists():
            try:
                successful_at = json.loads(
                    old_heartbeat.read_text(encoding="utf-8")
                ).get("last_successful_export_at", successful_at)
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass
    heartbeat = {
        "last_checked_at": iso(checked_at),
        "last_successful_export_at": successful_at,
        "status": "ok",
        "source_changed": changed,
        "goal_materials": materials,
        "error": None,
    }
    atomic_write_json(export_dir / "sync_heartbeat.json", heartbeat)
    logging.info("export completed source_changed=%s", changed)
    return heartbeat


def main() -> int:
    parser = argparse.ArgumentParser(description="Export read-only Obsidian context")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    arguments = parser.parse_args()
    config_path = arguments.config.resolve()
    config = load_config(config_path)
    export_dir = Path(config["export_dir"]).resolve()
    export_dir.mkdir(parents=True, exist_ok=True)
    lock_path = export_dir / "exporter.lock"
    try:
        descriptor = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        return 0
    try:
        with os.fdopen(descriptor, "w", encoding="ascii") as lock:
            lock.write(str(os.getpid()))
        result = export(config_path)
        if sys.stdout is not None:
            print(json.dumps(result, ensure_ascii=False))
        return 0
    except Exception as error:
        checked_at = now_local()
        heartbeat = {
            "last_checked_at": iso(checked_at),
            "last_successful_export_at": None,
            "status": "error",
            "source_changed": False,
            "error": f"{type(error).__name__}: {error}",
        }
        heartbeat_path = export_dir / "sync_heartbeat.json"
        if heartbeat_path.exists():
            try:
                old = json.loads(heartbeat_path.read_text(encoding="utf-8"))
                heartbeat["last_successful_export_at"] = old.get(
                    "last_successful_export_at"
                )
            except Exception:
                pass
        atomic_write_json(heartbeat_path, heartbeat)
        logging.exception("export failed")
        if sys.stderr is not None:
            print(json.dumps(heartbeat, ensure_ascii=False), file=sys.stderr)
        return 1
    finally:
        lock_path.unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main())
