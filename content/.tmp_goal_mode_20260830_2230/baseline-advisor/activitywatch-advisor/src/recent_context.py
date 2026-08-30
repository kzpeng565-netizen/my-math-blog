"""Pi-side recent context notes (近期动态).

User-entered notes carry a natural-language impact period. The user text
(content + impact_text) is the single source of truth; any AI parse is
auxiliary and stored separately with a source hash so stale parses can never
overwrite a newer user edit.

Storage contract
----------------
- Single durable file: data/recent_context/state.json
- Shape: {"schema_version": 1, "revision": int, "updated_at": str, "notes": [...]}
- All writes are guarded by a module-level RLock (the web server is
  ThreadingHTTPServer), and every write API requires expected_revision;
  mismatch raises RecentContextConflictError -> HTTP 409.
- A corrupt file is never reset to empty: it is copied once (same content
  digest) to state.json.corrupt-<timestamp> and every read/write raises
  RecentContextCorruptError -> HTTP 503 until restored.
- AI network calls are never made while holding the RLock.
"""

from __future__ import annotations

import hashlib
import json
import re
import threading
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from common import atomic_write_json
from deepseek_client import _request_json_report


SCHEMA_VERSION = 1
PARSE_VERSION = 2
PARSE_PROMPT_VERSION = "recent-context-parse-v2"
PARSE_TYPES = {"day", "daypart", "range", "event", "open", "vague"}
EVENT_RELATIONS = {"until", "after", "at", "window", "unknown"}
PARTS = {"morning", "afternoon", "evening", "night", "noon"}
CONFIDENCE = {"high", "medium", "low"}
NOTE_ID_RE = re.compile(r"^rc_[A-Za-z0-9_-]{4,64}$")
TIMEZONE = ZoneInfo("Asia/Shanghai")

_LOCK = threading.RLock()


class RecentContextCorruptError(RuntimeError):
    """The state file exists but cannot be parsed; all APIs must return 503."""


class RecentContextConflictError(RuntimeError):
    def __init__(self, current_revision: int) -> None:
        super().__init__("revision conflict")
        self.current_revision = current_revision


class RecentContextNotFoundError(KeyError):
    pass


PARSE_SYSTEM_PROMPT = (
    "你是近期动态的\"影响时段\"解析器，只输出 JSON，不做任何行动建议。\n"
    "输入只有三个字段：recorded_at（记录时间）、content（动态内容）、impact_text（影响时段原文）。\n"
    "规则：\n"
    "1. 所有相对时间（今天/明天/本周/下周/下午/晚上等）必须以 recorded_at 为基准，"
    "绝不能以当前模型调用时间或系统当前日期为基准。\n"
    "2. 不得改写或复述 content 与 impact_text。\n"
    "3. 只输出影响时段的结构化理解，不输出行动建议，不输出长篇解释。\n"
    "4. 不确定时降低 confidence；无法可靠解析时返回 type=vague。\n"
    "5. 不得为\"下午\"\"晚上\"等伪造精确小时；只有原文明确到时分时，range 才填写"
    "带 +08:00 时区的 start/end（YYYY-MM-DDTHH:MM+08:00）。仅明确到日期时，"
    "range 必须保留 YYYY-MM-DD，绝不能补成 00:00。\n"
    "6. 事件型表达（直到/等…后/…之前/…之后/…当天/…后两周内）允许判断关系，"
    "但不得假设事件已经发生；只能使用 relation: until|after|at|window|unknown。\n"
    "7. 输出字段只能是：type(day|daypart|range|event|open|vague), "
    "date(YYYY-MM-DD), part(morning|afternoon|evening|night|noon), "
    "start/end（YYYY-MM-DD 或 YYYY-MM-DDTHH:MM+08:00）, relation(until|after|at|window|unknown), "
    "confidence(high|medium|low)。与 type 无关的字段不要输出。"
)


def _now(timezone_name: str) -> datetime:
    return datetime.now(ZoneInfo(timezone_name))


def _state_path(output_root: Path) -> Path:
    return output_root / "recent_context" / "state.json"


def _audit_path(output_root: Path) -> Path:
    return output_root / "recent_context" / "parse_audit.jsonl"


def _source_hash(content: str, impact_text: str) -> str:
    canonical = f"{content}\n{impact_text}".encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _empty_state() -> dict[str, Any]:
    return {"schema_version": SCHEMA_VERSION, "revision": 0, "updated_at": None, "notes": []}


def _preserve_corrupt_once(path: Path) -> None:
    """Copy the corrupt file once per content version; never overwrite it."""
    try:
        data = path.read_bytes()
    except OSError:
        return
    digest = hashlib.sha256(data).hexdigest()
    for existing in path.parent.glob(path.name + ".corrupt-*"):
        try:
            if hashlib.sha256(existing.read_bytes()).hexdigest() == digest:
                return
        except OSError:
            continue
    backup = path.parent / f"{path.name}.corrupt-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    try:
        backup.write_bytes(data)
    except OSError:
        pass


def _load_state_unlocked(output_root: Path) -> dict[str, Any]:
    path = _state_path(output_root)
    if not path.exists():
        return _empty_state()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        _preserve_corrupt_once(path)
        raise RecentContextCorruptError("recent_context_state_corrupt") from None
    if (
        not isinstance(raw, dict)
        or raw.get("schema_version") != SCHEMA_VERSION
        or not isinstance(raw.get("notes"), list)
    ):
        _preserve_corrupt_once(path)
        raise RecentContextCorruptError("recent_context_state_corrupt")
    notes: list[dict[str, Any]] = []
    for note in raw["notes"]:
        if isinstance(note, dict) and isinstance(note.get("id"), str):
            notes.append(note)
    return {
        "schema_version": SCHEMA_VERSION,
        "revision": int(raw.get("revision", 0) or 0),
        "updated_at": raw.get("updated_at"),
        "notes": notes,
    }


def _save_state_unlocked(output_root: Path, state: dict[str, Any], now: datetime) -> None:
    state["updated_at"] = now.isoformat(timespec="seconds")
    atomic_write_json(_state_path(output_root), state)


def _check_revision(state: dict[str, Any], expected_revision: Any) -> None:
    if expected_revision is None:
        raise ValueError("expected_revision is required")
    try:
        expected = int(expected_revision)
    except (TypeError, ValueError):
        raise ValueError("expected_revision must be an integer") from None
    if expected != int(state["revision"]):
        raise RecentContextConflictError(int(state["revision"]))


def _find_note(state: dict[str, Any], note_id: str) -> dict[str, Any] | None:
    for note in state["notes"]:
        if note.get("id") == note_id:
            return note
    return None


def _validate_text(value: str, field: str, limit: int) -> str:
    text = str(value or "").strip()
    if field == "content" and not text:
        raise ValueError("content is required")
    if len(text) > limit:
        raise ValueError(f"{field} exceeds {limit} characters")
    return text


def make_note_id(now: datetime) -> str:
    return "rc_" + now.strftime("%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:8]


def _normalize_parse(report: Any, source_hash: str) -> dict[str, Any]:
    if not isinstance(report, dict):
        raise ValueError("parse output is not a JSON object")
    ptype = str(report.get("type", "")).strip()
    if ptype not in PARSE_TYPES:
        raise ValueError(f"invalid parse type: {ptype}")
    confidence = str(report.get("confidence", "low")).strip()
    if confidence not in CONFIDENCE:
        confidence = "low"
    parse: dict[str, Any] = {"v": PARSE_VERSION, "hash": source_hash}
    if ptype == "day":
        date = str(report.get("date", "")).strip()
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
            raise ValueError("day parse requires valid date")
        parse["type"] = "day"
        parse["date"] = date
        parse["confidence"] = confidence
    elif ptype == "daypart":
        date = str(report.get("date", "")).strip()
        part = str(report.get("part", "")).strip()
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date) or part not in PARTS:
            raise ValueError("daypart parse requires valid date and part")
        parse["type"] = "daypart"
        parse["date"] = date
        parse["part"] = part
        parse["confidence"] = confidence
    elif ptype == "range":
        start = str(report.get("start", "")).strip()
        end = str(report.get("end", "")).strip()
        start_at = _parse_impact_bound(start, end_of_day=False)
        end_at = _parse_impact_bound(end, end_of_day=True)
        if start_at is None or end_at is None or start_at > end_at:
            raise ValueError("range parse requires ordered date or minute-precise bounds")
        parse["type"] = "range"
        parse["start"] = start
        parse["end"] = end
        parse["confidence"] = confidence
    elif ptype == "event":
        relation = str(report.get("relation", "unknown")).strip()
        if relation not in EVENT_RELATIONS:
            relation = "unknown"
        parse["type"] = "event"
        parse["relation"] = relation
        parse["confidence"] = confidence
    else:
        parse["type"] = ptype
        parse["confidence"] = confidence
    return parse


def _parse_impact_bound(value: Any, *, end_of_day: bool) -> datetime | None:
    """Turn a date or minute-precise ISO value into a Shanghai-aware bound."""
    text = str(value or "").strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        parsed = datetime.fromisoformat(text).replace(tzinfo=TIMEZONE)
        return parsed.replace(hour=23, minute=59, second=59) if end_of_day else parsed
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?:Z|[+-]\d{2}:\d{2})", text):
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(TIMEZONE)


def _request_parse(
    note: dict[str, Any],
    settings: dict[str, Any],
    cfg: dict[str, Any],
    source_hash: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    base_model = settings.get("model", {})
    model = {
        "endpoint": base_model.get("endpoint", "https://api.deepseek.com/chat/completions"),
        "name": cfg.get("parser_model", "deepseek-v4-flash"),
        "thinking": "disabled",
        "max_tokens": 240,
        "timeout_seconds": int(cfg.get("parser_timeout_seconds", 10)),
        "retries": 0,
    }
    payload = {
        "recorded_at": note.get("created_at"),
        "content": note.get("content", ""),
        "impact_text": note.get("impact_text", ""),
    }
    messages = [
        {"role": "system", "content": PARSE_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
        },
    ]
    report, generation = _request_json_report(model, messages)
    return _normalize_parse(report, source_hash), generation


def _append_audit(output_root: Path, record: dict[str, Any]) -> None:
    path = _audit_path(output_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def _run_parse_and_persist(
    output_root: Path,
    note: dict[str, Any],
    settings: dict[str, Any],
    timezone_name: str,
    now: datetime,
) -> dict[str, Any] | None:
    """Parse outside the lock, then persist only if the source hash still matches."""
    cfg = settings.get("recent_context", {})
    if not cfg.get("parser_enabled", True):
        return None
    source_hash = _source_hash(note["content"], note["impact_text"])
    audit: dict[str, Any] = {
        "note_id": note["id"],
        "at": now.isoformat(timespec="seconds"),
        "model": cfg.get("parser_model", "deepseek-v4-flash"),
        "thinking": False,
        "prompt": PARSE_PROMPT_VERSION,
        "success": True,
        "usage": {},
    }
    parse: dict[str, Any]
    try:
        raw_parse, generation = _request_parse(note, settings, cfg, source_hash)
        parse = raw_parse
        usage_total = generation.get("usage", {})
        audit["usage"] = {
            "input_tokens": int(usage_total.get("prompt_tokens", 0) or 0),
            "output_tokens": int(usage_total.get("completion_tokens", 0) or 0),
        }
    except Exception as error:
        audit["success"] = False
        audit["error"] = f"{type(error).__name__}: {str(error)[:300]}"
        parse = {"v": PARSE_VERSION, "hash": source_hash, "error": "parse_failed"}
    _append_audit(output_root, audit)
    with _LOCK:
        state = _load_state_unlocked(output_root)
        current = _find_note(state, note["id"])
        if current is None:
            return parse
        if _source_hash(current.get("content", ""), current.get("impact_text", "")) != source_hash:
            # The user edited the note while parsing; discard the stale parse.
            return parse
        current["parse"] = parse
        _save_state_unlocked(output_root, state, now)
    return parse


def _status_for(note: dict[str, Any], now: datetime, cfg: dict[str, Any]) -> str:
    parse = note.get("parse")
    ptype = parse.get("type") if isinstance(parse, dict) else None
    today = now.date()
    status = "conditional"
    if ptype in ("day", "daypart"):
        try:
            date = datetime.fromisoformat(parse["date"]).date()
        except (KeyError, ValueError):
            date = None
        if date:
            status = "ended" if date < today else ("active" if date == today else "upcoming")
    elif ptype == "range":
        start = _parse_impact_bound(parse.get("start"), end_of_day=False)
        end = _parse_impact_bound(parse.get("end"), end_of_day=True)
        if start and end:
            if end < now:
                status = "ended"
            elif start > now:
                status = "upcoming"
            else:
                status = "active"
    if status == "conditional":
        review_days = int(cfg.get("review_after_days", 14))
        anchor = note.get("confirmed_at") or note.get("created_at")
        try:
            anchor_date = datetime.fromisoformat(str(anchor)).date()
        except ValueError:
            anchor_date = datetime.fromisoformat(str(note.get("created_at", ""))).date()
        if (today - anchor_date).days > review_days:
            status = "needs_review"
    return status


def recall_importance(note: dict[str, Any]) -> str:
    """Conservative importance floor for Next Action recall.

    This is not a claim about the user's overall priorities.  It only prevents
    health, exam and hard-deadline notes from being silently squeezed out of a
    small decision-context window before the selector model can inspect them.
    """
    text = f"{note.get('content', '')} {note.get('impact_text', '')}".lower()
    if re.search(
        r"生病|发烧|不舒服|就医|医院|急诊|吃药|复诊|考试|测验|期中|期末|答辩|"
        r"硬截止|截止日期|截止|ddl|due\s*date",
        text,
        re.I,
    ):
        return "critical"
    if re.search(r"预约|面试|家教|上课|出行|火车|高铁|航班|会议", text, re.I):
        return "high"
    return "normal"


def _parse_text(parse: dict[str, Any] | None) -> str:
    if not isinstance(parse, dict):
        return "等待解析"
    if parse.get("error"):
        return "时间解析失败"
    ptype = parse.get("type")
    date = parse.get("date") or parse.get("start")
    if ptype in ("day", "daypart"):
        label = _format_date(date)
        if ptype == "daypart":
            part_labels = {
                "morning": "上午", "afternoon": "下午", "evening": "晚上",
                "night": "夜间", "noon": "中午",
            }
            return f"{label}{part_labels.get(parse.get('part'), '')}"
        return label
    if ptype == "range":
        return _format_range(parse.get("start"), parse.get("end"))
    if ptype == "event":
        return "取决于事件是否发生"
    if ptype == "open":
        return "没有明确结束时间"
    if ptype == "vague":
        return "时段暂时无法确定"
    return "时段暂时无法确定"


def _format_date(value: Any) -> str:
    try:
        parsed = datetime.fromisoformat(str(value)).date()
        return f"{parsed.month}月{parsed.day}日"
    except ValueError:
        return str(value or "")


def _format_range(start: Any, end: Any) -> str:
    start_text = str(start or "")
    end_text = str(end or "")
    start_at = _parse_impact_bound(start_text, end_of_day=False)
    end_at = _parse_impact_bound(end_text, end_of_day=True)
    if not start_at or not end_at:
        return "时段暂时无法确定"
    start_label = _format_date(start_text)
    end_label = _format_date(end_text)
    start_precise = "T" in start_text
    end_precise = "T" in end_text
    if start_precise:
        start_label += " " + start_at.strftime("%H:%M")
    if end_precise:
        end_label += " " + end_at.strftime("%H:%M")
    if start_at.date() == end_at.date() and start_precise and end_precise:
        return f"{start_label}至{end_at.strftime('%H:%M')}"
    return f"{start_label}至{end_label}"


def _public_note(note: dict[str, Any], now: datetime, cfg: dict[str, Any]) -> dict[str, Any]:
    parse = note.get("parse")
    public = {
        "id": note["id"],
        "content": note["content"],
        "impact_text": note["impact_text"],
        "created_at": note["created_at"],
        "updated_at": note["updated_at"],
        "confirmed_at": note.get("confirmed_at"),
        "archived": bool(note.get("archived", False)),
        "pinned": bool(note.get("pinned", False)),
        "status": _status_for(note, now, cfg),
        "parse_text": _parse_text(parse),
    }
    if isinstance(parse, dict) and not parse.get("error"):
        public["parse"] = {key: value for key, value in parse.items() if value is not None}
    return public


def load_notes(output_root: Path) -> list[dict[str, Any]]:
    with _LOCK:
        return _load_state_unlocked(output_root)["notes"]


def create_note(
    output_root: Path,
    content: str,
    impact_text: str,
    expected_revision: Any,
    settings: dict[str, Any],
    timezone_name: str = "Asia/Shanghai",
    now: datetime | None = None,
) -> dict[str, Any]:
    current = now or _now(timezone_name)
    cfg = settings.get("recent_context", {})
    cleaned_content = _validate_text(content, "content", int(cfg.get("max_content_chars", 500)))
    cleaned_impact = _validate_text(impact_text, "impact_text", int(cfg.get("max_impact_chars", 100)))
    note = {
        "id": make_note_id(current),
        "content": cleaned_content,
        "impact_text": cleaned_impact,
        "created_at": current.isoformat(timespec="seconds"),
        "updated_at": current.isoformat(timespec="seconds"),
        "confirmed_at": current.isoformat(timespec="seconds"),
        "archived": False,
        "pinned": False,
    }
    with _LOCK:
        state = _load_state_unlocked(output_root)
        _check_revision(state, expected_revision)
        state["notes"].append(note)
        state["revision"] += 1
        _save_state_unlocked(output_root, state, current)
        revision = int(state["revision"])
    _run_parse_and_persist(output_root, note, settings, timezone_name, current)
    with _LOCK:
        state = _load_state_unlocked(output_root)
        saved = _find_note(state, note["id"]) or note
        revision = int(state["revision"])
    return {"note": _public_note(saved, current, cfg), "revision": revision}


def update_note(
    output_root: Path,
    note_id: str,
    expected_revision: Any,
    settings: dict[str, Any],
    *,
    content: str | None = None,
    impact_text: str | None = None,
    pinned: bool | None = None,
    timezone_name: str = "Asia/Shanghai",
    now: datetime | None = None,
) -> dict[str, Any]:
    current = now or _now(timezone_name)
    cfg = settings.get("recent_context", {})
    if not NOTE_ID_RE.fullmatch(note_id):
        raise ValueError("invalid note id")
    with _LOCK:
        state = _load_state_unlocked(output_root)
        _check_revision(state, expected_revision)
        note = _find_note(state, note_id)
        if note is None:
            raise RecentContextNotFoundError(note_id)
        reparse = False
        if content is not None:
            note["content"] = _validate_text(content, "content", int(cfg.get("max_content_chars", 500)))
            reparse = True
        if impact_text is not None:
            note["impact_text"] = _validate_text(impact_text, "impact_text", int(cfg.get("max_impact_chars", 100)))
            reparse = True
        if pinned is not None:
            note["pinned"] = bool(pinned)
        if reparse:
            note["updated_at"] = current.isoformat(timespec="seconds")
            note["confirmed_at"] = current.isoformat(timespec="seconds")
            note.pop("parse", None)
        state["revision"] += 1
        _save_state_unlocked(output_root, state, current)
        revision = int(state["revision"])
    if reparse:
        _run_parse_and_persist(output_root, note, settings, timezone_name, current)
        with _LOCK:
            state = _load_state_unlocked(output_root)
            saved = _find_note(state, note_id) or note
            revision = int(state["revision"])
    else:
        saved = note
    return {"note": _public_note(saved, current, cfg), "revision": revision}


def _simple_mutation(
    output_root: Path,
    note_id: str,
    expected_revision: Any,
    *,
    archived: bool | None = None,
    pinned: bool | None = None,
    confirm: bool = False,
    timezone_name: str = "Asia/Shanghai",
    now: datetime | None = None,
) -> dict[str, Any]:
    current = now or _now(timezone_name)
    cfg: dict[str, Any] = {}
    if not NOTE_ID_RE.fullmatch(note_id):
        raise ValueError("invalid note id")
    with _LOCK:
        state = _load_state_unlocked(output_root)
        _check_revision(state, expected_revision)
        note = _find_note(state, note_id)
        if note is None:
            raise RecentContextNotFoundError(note_id)
        if archived is not None:
            note["archived"] = bool(archived)
        if pinned is not None:
            note["pinned"] = bool(pinned)
        if confirm:
            note["confirmed_at"] = current.isoformat(timespec="seconds")
        state["revision"] += 1
        _save_state_unlocked(output_root, state, current)
        revision = int(state["revision"])
        saved = _find_note(state, note_id) or note
    return {"note": _public_note(saved, current, cfg), "revision": revision}


def set_archived(output_root: Path, note_id: str, expected_revision: Any, archived: bool, **kwargs: Any) -> dict[str, Any]:
    return _simple_mutation(output_root, note_id, expected_revision, archived=archived, **kwargs)


def set_pinned(output_root: Path, note_id: str, expected_revision: Any, pinned: bool, **kwargs: Any) -> dict[str, Any]:
    return _simple_mutation(output_root, note_id, expected_revision, pinned=pinned, **kwargs)


def confirm_note(output_root: Path, note_id: str, expected_revision: Any, **kwargs: Any) -> dict[str, Any]:
    return _simple_mutation(output_root, note_id, expected_revision, confirm=True, **kwargs)


def list_notes(
    output_root: Path,
    *,
    include_archived: bool = False,
    settings: dict[str, Any] | None = None,
    timezone_name: str = "Asia/Shanghai",
    now: datetime | None = None,
) -> dict[str, Any]:
    current = now or _now(timezone_name)
    with _LOCK:
        state = _load_state_unlocked(output_root)
        notes = list(state["notes"])
        revision = int(state["revision"])
    cfg: dict[str, Any] = (settings or {}).get("recent_context", {})
    visible = [note for note in notes if include_archived or not note.get("archived", False)]
    visible.sort(
        key=lambda note: (
            0 if note.get("pinned", False) else 1,
            -datetime.fromisoformat(str(note.get("created_at", ""))).timestamp(),
        )
    )
    return {
        "revision": revision,
        "notes": [_public_note(note, current, cfg) for note in visible],
    }


def _date_bounds(parse: dict[str, Any] | None) -> tuple[datetime, datetime] | None:
    if not isinstance(parse, dict) or parse.get("error"):
        return None
    ptype = parse.get("type")
    if ptype in ("day", "daypart") and parse.get("date"):
        start = _parse_impact_bound(parse["date"], end_of_day=False)
        end = _parse_impact_bound(parse["date"], end_of_day=True)
        return (start, end) if start and end else None
    if ptype == "range" and parse.get("start") and parse.get("end"):
        start = _parse_impact_bound(parse["start"], end_of_day=False)
        end = _parse_impact_bound(parse["end"], end_of_day=True)
        return (start, end) if start and end else None
    return None


def coarse_candidates(
    notes: list[dict[str, Any]],
    now: datetime,
    settings: dict[str, Any],
) -> dict[str, Any]:
    """Code-only coarse filter. Returns forced_ids and an ordered candidate list."""
    cfg = settings.get("recent_context", {})
    direct_hours = int(cfg.get("direct_window_hours", 24))
    prep_days = int(cfg.get("preparation_window_days", 7))
    review_days = int(cfg.get("review_after_days", 14))
    candidate_limit = int(cfg.get("selector_candidate_limit", 30))
    today = now.date()
    forced: list[dict[str, Any]] = []
    candidates: list[dict[str, Any]] = []
    for note in notes:
        if note.get("archived", False):
            continue
        status = _status_for(note, now, cfg)
        importance = recall_importance(note)
        if status == "ended" or status == "needs_review":
            continue
        bounds = _date_bounds(note.get("parse"))
        hours_ahead: float | None = None
        if bounds and bounds[0]:
            hours_ahead = (bounds[0] - now).total_seconds() / 3600
        candidate = dict(note)
        candidate["recall_importance"] = importance
        candidate["recall_hours_ahead"] = hours_ahead
        if status == "active":
            forced.append(candidate)
            continue
        if status == "upcoming":
            if hours_ahead is None:
                continue
            if hours_ahead <= direct_hours:
                forced.append(candidate)
            elif hours_ahead <= prep_days * 24:
                (forced if importance == "critical" else candidates).append(candidate)
            else:
                continue
        else:  # conditional (event/open/vague/error/parsing)
            anchor = note.get("confirmed_at") or note.get("created_at")
            try:
                anchor_date = datetime.fromisoformat(str(anchor)).date()
            except ValueError:
                anchor_date = today
            if (today - anchor_date).days <= review_days:
                (forced if importance == "critical" else candidates).append(candidate)
            else:
                continue
    importance_rank = {"critical": 0, "high": 1, "normal": 2}
    def order_key(note: dict[str, Any]) -> tuple[int, int, float, int, float]:
        status = _status_for(note, now, cfg)
        status_rank = {"active": 0, "upcoming": 1, "conditional": 2}.get(status, 3)
        hours = note.get("recall_hours_ahead")
        urgency = float(hours) if isinstance(hours, (int, float)) else float("inf")
        return (
            importance_rank.get(str(note.get("recall_importance")), 2),
            status_rank,
            urgency,
            0 if note.get("pinned", False) else 1,
            -datetime.fromisoformat(str(note.get("created_at", ""))).timestamp(),
        )
    forced.sort(key=order_key)
    candidates.sort(key=order_key)
    ordered = forced + candidates
    ordered = ordered[:candidate_limit]
    forced_ids = [note["id"] for note in ordered if note["id"] in {item["id"] for item in forced}]
    return {"forced_ids": forced_ids, "candidates": ordered}


def relevant_notes(
    output_root: Path,
    *,
    settings: dict[str, Any] | None = None,
    timezone_name: str = "Asia/Shanghai",
    now: datetime | None = None,
) -> dict[str, Any]:
    """Code coarse filter only (no selector AI) for the UI card."""
    current = now or _now(timezone_name)
    notes = load_notes(output_root)
    cfg: dict[str, Any] = (settings or {}).get("recent_context", {})
    result = coarse_candidates(notes, current, {"recent_context": cfg})
    items = []
    for note in result["candidates"]:
        public = _public_note(note, current, cfg)
        items.append(
            {
                "id": public["id"],
                "content": public["content"],
                "impact_text": public["impact_text"],
                "status": public["status"],
                "created_at": public["created_at"],
                "parse_text": public["parse_text"],
            }
        )
    return {
        "as_of": current.isoformat(timespec="seconds"),
        "items": items,
        "omitted_count": max(0, len(notes) - len(items)),
    }
