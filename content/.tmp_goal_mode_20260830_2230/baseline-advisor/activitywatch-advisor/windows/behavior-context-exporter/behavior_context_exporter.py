from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


TIMEZONE = ZoneInfo("Asia/Shanghai")
EXPORTER_VERSION = 2
SOURCE_NAMES = {
    "profile": "Profile.md",
    "planned_tasks": "ToDo-已经规划好的任务.md",
    "pomodoro_log": "番茄钟log.md",
}
DEFAULT_CONFIG = Path(__file__).with_name("behavior_context_exporter.json")
POMODORO_WARNING = (
    "番茄钟日志在假期中记录不完整，只能作为主动工作信号。"
    "无记录不能解释为无学习，且不能用于判断具体任务进度。"
)
TASK_RE = re.compile(r"^\s*-\s*\[([ xX])\]\s+#task(?:\s+|$)(.*)$")
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
        "planned_tasks": "planned_tasks_path",
        "pomodoro_log": "pomodoro_log_path",
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
    raw_line: str, category: str | None, planning_batch: str | None, order: int
) -> dict[str, Any] | None:
    match = TASK_RE.match(raw_line)
    if not match or match.group(1).lower() == "x":
        return None
    body = match.group(2).strip()
    scheduled = _metadata_value(r"⏳\s*(\d{4}-\d{2}-\d{2})", body)
    due = _metadata_value(r"📅\s*(\d{4}-\d{2}-\d{2})", body)
    tomato = re.search(r"\[🍅::\s*(?:(\d+)\s*/\s*(\d+))?\s*\]", body)
    recurrence = _metadata_value(
        r"🔁\s*(.*?)(?=\s+(?:⏳|📅|🔺|⏫|🔼|🔽|⏬|\[🍅::)|$)", body
    )
    priority = "normal"
    for symbol, value in PRIORITIES:
        if symbol in body:
            priority = value
            break
    title = re.sub(r"\[🍅::.*?\]", "", body)
    title = re.sub(r"⏳\s*\d{4}-\d{2}-\d{2}", "", title)
    title = re.sub(r"📅\s*\d{4}-\d{2}-\d{2}", "", title)
    title = re.sub(r"🔁\s*.*?(?=\s+(?:⏳|📅|🔺|⏫|🔼|🔽|⏬)|$)", "", title)
    title = re.sub(r"[🔺🔼🔽]", "", title).replace("⏫", "").replace("⏬", "")
    title = re.sub(r"\s+", " ", title).strip()
    return {
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
        "raw_line": raw_line,
    }


def parse_tasks(markdown: str, today: date) -> dict[str, Any]:
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
        "overdue_tasks": [],
        "today_tasks": [],
        "near_term_tasks": [],
        "later_tasks": [],
        "recurring_tasks": [],
    }
    for task in tasks:
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
        **buckets,
        "latest_plan_heading": latest_heading,
        "latest_plan_notes_markdown": notes,
        "parser_warnings": warnings,
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
    paths: dict[str, Path], contents: dict[str, bytes], generated_at: datetime
) -> dict[str, Any]:
    decoded = {key: value.decode("utf-8") for key, value in contents.items()}
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
        "tasks": parse_tasks(decoded["planned_tasks"], generated_at.date()),
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
    changed = hashes != old_hashes or old_exporter_version != EXPORTER_VERSION
    if changed:
        snapshot = build_snapshot(paths, contents, checked_at)
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
