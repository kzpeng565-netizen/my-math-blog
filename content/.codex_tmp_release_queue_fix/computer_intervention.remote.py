from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from uuid import uuid4
import threading

from common import atomic_write_json, iso_timestamp, load_json


DEFAULT_RULES = {
    "enabled": True,
    "request_ttl_seconds": 7200,
    "default_lock_minutes": 30,
    "decline_policy": {
        "max_declines_before_force": 2,
        "episode_reset_minutes": 90,
        "reset_when_meaningful_minutes_at_least": 20,
        "reset_when_confirmed_rest_minutes_at_least": 10,
    },
    "targets": [
        {
            "name": "常刷网站",
            "cold_turkey_block": "常刷网站",
            "lock_minutes": 30,
            "trigger": "always",
        },
        {
            "name": "bilibili",
            "cold_turkey_block": "bilibili",
            "lock_minutes": 30,
            "trigger": "bilibili_activity",
            "exempt_windows": [
                {"weekday": "saturday", "start": "00:00", "end": "24:00"},
                {"weekday": "sunday", "start": "00:00", "end": "24:00"},
                {"weekday": "monday", "start": "00:00", "end": "12:00"},
            ],
        },
    ],
}

WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}
BILIBILI_MARKERS = ("bilibili", "哔哩", "b站", "tv.danmaku.bili")
FINAL_DECISIONS = {
    "accepted",
    "declined",
    "forced",
    "ignored",
    "already_locked",
    "executed",
}

PHONE_DEVICE_ID = "android-main"
_DECISION_LOCK = threading.RLock()


def computer_intervention_rules(settings: dict[str, Any]) -> dict[str, Any]:
    configured = settings.get("computer_intervention")
    if not isinstance(configured, dict):
        return DEFAULT_RULES
    rules = {**DEFAULT_RULES, **configured}
    if "decline_policy" in configured:
        rules["decline_policy"] = {
            **DEFAULT_RULES["decline_policy"],
            **configured.get("decline_policy", {}),
        }
    if "targets" not in configured:
        rules["targets"] = DEFAULT_RULES["targets"]
    return rules


def _time_value(text: str) -> int:
    hour, minute = (int(part) for part in text.split(":", 1))
    if hour == 24 and minute == 0:
        return 24 * 60
    return hour * 60 + minute


def _window_matches(moment: datetime, window: dict[str, Any]) -> bool:
    weekday = WEEKDAYS.get(str(window.get("weekday", "")).lower())
    if weekday is None or moment.weekday() != weekday:
        return False
    current = moment.hour * 60 + moment.minute
    start = _time_value(str(window.get("start", "00:00")))
    end = _time_value(str(window.get("end", "24:00")))
    if start <= end:
        return start <= current < end
    return current >= start or current < end


def is_exempt_now(moment: datetime, target: dict[str, Any]) -> bool:
    return any(
        _window_matches(moment, window)
        for window in target.get("exempt_windows", [])
        if isinstance(window, dict)
    )


def _semantic_has_bilibili(semantic: dict[str, Any]) -> bool:
    text = str(semantic).lower()
    return any(marker in text for marker in BILIBILI_MARKERS)


def _target_is_triggered(target: dict[str, Any], semantic: dict[str, Any]) -> bool:
    trigger = str(target.get("trigger", "always"))
    if trigger == "always":
        return True
    if trigger == "bilibili_activity":
        return _semantic_has_bilibili(semantic)
    return False


def build_computer_intervention_request(
    settings: dict[str, Any],
    start: datetime,
    end: datetime,
    intervention: dict[str, Any],
    semantic: dict[str, Any],
) -> dict[str, Any] | None:
    rules = computer_intervention_rules(settings)
    if not rules.get("enabled", True) or not intervention.get("would_intervene"):
        return None

    targets: list[dict[str, Any]] = []
    for target in rules.get("targets", []):
        if not isinstance(target, dict) or not _target_is_triggered(target, semantic):
            continue
        exempt = is_exempt_now(end, target)
        targets.append(
            {
                "name": str(target.get("name") or target.get("cold_turkey_block")),
                "cold_turkey_block": str(target.get("cold_turkey_block", "")),
                "lock_minutes": int(
                    target.get("lock_minutes", rules.get("default_lock_minutes", 30))
                ),
                "enabled": not exempt,
                "exempt": exempt,
                "reason": "lesson_prep_exempt_window" if exempt else "triggered",
            }
        )
    if not targets:
        return None
    request_id = f"{start:%Y-%m-%d-%H-%M}_{end:%H-%M}"
    observations = intervention.get("observations", {})
    reasons = intervention.get("trigger_reasons", [])
    return {
        "schema_version": 2,
        "request_id": request_id,
        "created_at": iso_timestamp(end),
        "period": {
            "start": iso_timestamp(start),
            "end": iso_timestamp(end),
        },
        # An offer is resolved once, centrally.  Both the desktop and phone
        # clients may display it, but only the first response can fan out an
        # execution request.
        "mode": "offer",
        "source": "half_hour_candidate",
        "would_intervene": True,
        "expires_after_seconds": int(rules.get("request_ttl_seconds", 7200)),
        "decline_policy": rules.get("decline_policy", {}),
        "targets": targets,
        "phone": {
            "enabled": True,
            "minutes": int(rules.get("phone_quick_pomodoro_minutes", rules.get("default_lock_minutes", 30))),
        },
        "trigger_reasons": reasons,
        "observations": observations,
        "recommended_task": intervention.get("recommended_task"),
        "message": _request_message(reasons, observations),
    }


def build_manual_focus_request(
    settings: dict[str, Any],
    duration: int,
    requested_targets: list[str],
    *,
    requested_blocks: list[str] | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Create one idempotent, allowlisted dual-device focus command.

    This deliberately contains neither shell input nor Android Intent payloads.
    The Windows agent still applies its own Cold Turkey allowlist and the phone
    bridge only accepts its compiled quick-pomodoro minute presets.
    """
    if not 1 <= duration <= 180:
        raise ValueError("focus duration must be between 5 and 180 minutes")
    targets = set(requested_targets)
    if not targets or not targets <= {"windows", "phone"}:
        raise ValueError("targets must contain windows and/or phone")
    rules = computer_intervention_rules(settings)
    allowed_targets = [target for target in rules.get("targets", []) if isinstance(target, dict)]
    allowed_names = {str(target.get("name") or target.get("cold_turkey_block")) for target in allowed_targets}
    selected_blocks = set(requested_blocks or allowed_names)
    if not selected_blocks <= allowed_names:
        raise ValueError("requested blocks must be in the configured allowlist")
    moment = now or datetime.now().astimezone()
    windows_targets: list[dict[str, Any]] = []
    if "windows" in targets:
        for target in allowed_targets:
            name = str(target.get("name") or target.get("cold_turkey_block"))
            if name not in selected_blocks:
                continue
            windows_targets.append(
                {
                    "name": name,
                    "cold_turkey_block": str(target.get("cold_turkey_block", "")),
                    "lock_minutes": duration,
                    "enabled": True,
                    "exempt": False,
                    "reason": "manual_focus",
                }
            )
    request_id = f"manual-focus-{moment:%Y%m%dT%H%M%S}-{uuid4().hex[:10]}"
    return {
        "schema_version": 2,
        "request_id": request_id,
        "created_at": moment.isoformat(timespec="seconds"),
        "period": {
            "start": moment.isoformat(timespec="seconds"),
            "end": (moment + timedelta(minutes=duration)).isoformat(timespec="seconds"),
        },
        "mode": "execute",
        "source": "manual_focus",
        "lease_id": request_id,
        "expires_after_seconds": 180,
        "targets": [{**target, "lease_id": request_id} for target in windows_targets],
        "phone": {"enabled": "phone" in targets, "minutes": duration},
        "message": "Focus Garden manual focus start",
    }


def build_manual_focus_release_request(
    settings: dict[str, Any], requested_blocks: list[str], *, lease_id: str | None = None,
    session_id: str | None = None, now: datetime | None = None
) -> dict[str, Any]:
    """Ask the existing Windows intervention agent to stop only allowlisted blocks.

    Cold Turkey's unlocked ``-start`` sessions are deliberately owned by this
    agent, so the exact same path can release them during a Pomodoro pause.
    """
    rules = computer_intervention_rules(settings)
    allowed_targets = [target for target in rules.get("targets", []) if isinstance(target, dict)]
    allowed_by_name = {str(target.get("name") or target.get("cold_turkey_block")): target for target in allowed_targets}
    blocks = [str(block) for block in requested_blocks]
    if not blocks or any(block not in allowed_by_name for block in blocks):
        raise ValueError("release blocks must be in the configured allowlist")
    moment = now or datetime.now().astimezone()
    owner = str(lease_id or "").strip()
    session = str(session_id or "").strip()
    stable_owner = owner or session
    if stable_owner:
        safe_owner = "".join(ch for ch in stable_owner if ch.isalnum() or ch in "-_")[:100]
        request_id = f"manual-focus-release-{safe_owner}"
    else:
        request_id = f"manual-focus-release-{moment:%Y%m%dT%H%M%S}-{uuid4().hex[:10]}"
    return {
        "schema_version": 2,
        "request_id": request_id,
        "created_at": moment.isoformat(timespec="seconds"),
        "period": {"start": moment.isoformat(timespec="seconds"), "end": moment.isoformat(timespec="seconds")},
        "mode": "release",
        "source": "manual_focus_pause",
        # A release is a durable command.  It remains pending until the
        # Windows agent confirms that the matching lease was stopped.
        "durable": True,
        "lease_id": owner or None,
        "session_id": session or None,
        "targets": [
            {"name": name, "cold_turkey_block": str(allowed_by_name[name].get("cold_turkey_block", name)),
             "enabled": True, "exempt": False, "reason": "manual_focus_pause",
             "lease_id": owner or None}
            for name in blocks
        ],
        "phone": {"enabled": False, "minutes": 0},
        "message": "Focus Garden manual focus pause/release",
    }


def _request_message(reasons: list[str], observations: dict[str, Any]) -> str:
    return (
        "半小时系统判断可能需要介入。"
        f"触发原因：{'、'.join(reasons) if reasons else '无'}；"
        f"高刺激 {observations.get('high_stimulation_minutes', 0)} 分钟；"
        f"60分钟有意义活动 {observations.get('meaningful_minutes_60m', 0)} 分钟。"
    )


def save_computer_intervention_request(
    output_root: Path,
    request: dict[str, Any],
) -> Path:
    period_end = str(request["period"]["end"])
    day = period_end[:10]
    request_id = request["request_id"]
    path = output_root / "computer_interventions" / "requests" / day / f"{request_id}.json"
    atomic_write_json(path, request)
    return path


def _request_files(output_root: Path) -> list[Path]:
    # Request IDs mix time-stamped `manual-focus-*` and `manual-focus-release-*`
    # prefixes.  Lexicographic ordering places every release after every start,
    # so a release-heavy history could hide a newer start from the Windows agent.
    paths = sorted(
        (output_root / "computer_interventions" / "requests").glob("*/*.json"),
        key=lambda path: path.stat().st_mtime,
    )
    recent = paths[-80:]
    # Durable release commands must never fall out of the scan window while
    # the computer is asleep or the agent is offline.
    durable = []
    for path in paths:
        try:
            request = load_json(path)
        except (OSError, ValueError):
            continue
        if isinstance(request, dict) and request.get("mode") == "release":
            durable.append(path)
    return sorted(set(recent + durable), key=lambda path: path.stat().st_mtime)


def _decision_path(output_root: Path, request_id: str) -> Path:
    safe = "".join(ch for ch in request_id if ch.isalnum() or ch in "-_")[:160]
    return output_root / "computer_interventions" / "decisions" / f"{safe}.json"


def _read_decision(output_root: Path, request_id: str) -> dict[str, Any] | None:
    path = _decision_path(output_root, request_id)
    try:
        result = load_json(path)
    except (OSError, ValueError):
        return None
    return result if isinstance(result, dict) else None


def _episode_path(output_root: Path) -> Path:
    return output_root / "computer_interventions" / "state" / "shared-episode.json"


def _episode(output_root: Path) -> dict[str, Any]:
    try:
        state = load_json(_episode_path(output_root))
    except (OSError, ValueError):
        state = {}
    if not isinstance(state, dict):
        state = {}
    return {"decline_streak": 0, **state}


def _is_expired(request: dict[str, Any], now: datetime) -> bool:
    if request.get("mode") == "release" or request.get("durable") is True:
        return False
    try:
        created = datetime.fromisoformat(str(request["created_at"])).astimezone(now.tzinfo)
    except (KeyError, ValueError):
        return True
    return (now - created).total_seconds() > int(request.get("expires_after_seconds", 7200))


def _latest_shadow_candidate(
    output_root: Path,
    timezone: Any,
) -> tuple[datetime, dict[str, Any]] | None:
    root = output_root / "intervention_candidates"
    for path in reversed(sorted(root.glob("*/*.json"))):
        try:
            candidate = load_json(path)
            start = datetime.strptime(
                f"{path.parent.name}T{path.stem}",
                "%Y-%m-%dT%H-%M",
            ).replace(tzinfo=timezone)
        except (OSError, ValueError):
            continue
        if isinstance(candidate, dict):
            return start + timedelta(minutes=30), candidate
    return None


def latest_pending_request(
    output_root: Path,
    computer_id: str,
    now: datetime,
) -> dict[str, Any] | None:
    return latest_pending_device_request(output_root, computer_id, "windows", now)


def latest_pending_phone_request(
    output_root: Path,
    phone_id: str,
    now: datetime,
) -> dict[str, Any] | None:
    return latest_pending_device_request(output_root, phone_id, "phone", now)


def latest_pending_device_request(
    output_root: Path,
    device_id: str,
    device_kind: str,
    now: datetime,
) -> dict[str, Any] | None:
    state = _agent_state(output_root, device_id)
    completed = set(state.get("completed_request_ids", []))
    latest_candidate = _latest_shadow_candidate(output_root, now.tzinfo)
    for path in reversed(_request_files(output_root)):
        try:
            request = load_json(path)
        except (OSError, ValueError):
            continue
        request_id = str(request.get("request_id", ""))
        if not request_id or request_id in completed:
            continue
        if _is_expired(request, now):
            continue
        if device_kind == "phone" and not bool(request.get("phone", {}).get("enabled")):
            continue
        if device_kind == "windows" and not request.get("targets"):
            continue
        decision = _read_decision(output_root, request_id)
        if request.get("mode") == "offer" and decision is not None:
            continue
        request_end = datetime.fromisoformat(str(request["period"]["end"])).astimezone(now.tzinfo)
        if (
            request.get("source") == "half_hour_candidate"
            and latest_candidate is not None
            and latest_candidate[0] > request_end
            and not latest_candidate[1].get("would_intervene")
        ):
            continue
        request["server_path"] = str(path.relative_to(output_root))
        return request
    return None


def resolve_intervention_decision(
    output_root: Path,
    request_id: str,
    decision: str,
    device_id: str,
) -> dict[str, Any]:
    """Atomically settle one mirrored shadow offer and fan out both devices."""
    if decision not in {"accepted", "declined", "ignored"}:
        raise ValueError("decision must be accepted, declined, or ignored")
    with _DECISION_LOCK:
        existing = _read_decision(output_root, request_id)
        if existing is not None:
            return {"ok": True, "already_resolved": True, "decision": existing}
        offer = next(
            (item for path in _request_files(output_root)
             if isinstance((item := _safe_load(path)), dict) and item.get("request_id") == request_id),
            None,
        )
        if not offer or offer.get("mode") != "offer" or _is_expired(offer, datetime.now().astimezone()):
            raise ValueError("active intervention offer not found")
        episode = _episode(output_root)
        before = int(episode.get("decline_streak", 0) or 0)
        effective = decision
        execution_request_id = ""
        if decision == "accepted":
            episode["decline_streak"] = 0
        elif decision == "declined":
            after = before + 1
            if after >= 2:
                effective = "forced"
                episode["decline_streak"] = 0
            else:
                episode["decline_streak"] = after
                episode["last_decline_at"] = datetime.now().astimezone().isoformat(timespec="seconds")
        if effective in {"accepted", "forced"}:
            execution_request_id = f"{request_id}-execute"
            execution = {
                **offer,
                "request_id": execution_request_id,
                "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
                "mode": "execute",
                "source": "forced_intervention" if effective == "forced" else "shadow_intervention",
                "expires_after_seconds": 180,
            }
            execution["lease_id"] = execution_request_id
            execution["targets"] = [
                {**target, "lease_id": execution_request_id}
                for target in execution.get("targets", [])
            ]
            save_computer_intervention_request(output_root, execution)
        episode["last_updated_at"] = datetime.now().astimezone().isoformat(timespec="seconds")
        atomic_write_json(_episode_path(output_root), episode)
        result = {
            "schema_version": 1,
            "request_id": request_id,
            "decision": effective,
            "submitted_decision": decision,
            "device_id": device_id[:80],
            "decline_streak_before": before,
            "decline_streak_after": int(episode.get("decline_streak", 0) or 0),
            "execution_request_id": execution_request_id or None,
            "resolved_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        }
        atomic_write_json(_decision_path(output_root, request_id), result)
        return {"ok": True, "already_resolved": False, "decision": result}


def _safe_load(path: Path) -> dict[str, Any] | None:
    try:
        result = load_json(path)
    except (OSError, ValueError):
        return None
    return result if isinstance(result, dict) else None


def receive_computer_intervention_event(
    output_root: Path,
    event: dict[str, Any],
    *,
    user_agent: str = "",
) -> dict[str, Any]:
    computer_id = str(event.get("computer_id", "windows-main"))[:80]
    request_id = str(event.get("request_id", ""))[:120]
    status = str(event.get("status", event.get("decision", "event")))[:80]
    if not request_id:
        raise ValueError("request_id is required")
    created_at = datetime.now().astimezone().isoformat(timespec="seconds")
    payload = {
        "schema_version": 1,
        "received_at": created_at,
        "computer_id": computer_id,
        "request_id": request_id,
        "status": status,
        "event": event,
        "user_agent": user_agent[:300],
    }
    day = created_at[:10]
    stamp = created_at.replace(":", "").replace("+", "p").replace("-", "")
    safe_status = "".join(ch for ch in status if ch.isalnum() or ch in "-_")[:40]
    path = (
        output_root
        / "computer_interventions"
        / "responses"
        / day
        / f"{stamp}-{request_id}-{safe_status}.json"
    )
    atomic_write_json(path, payload)
    state = _agent_state(output_root, computer_id)
    state["computer_id"] = computer_id
    state["last_seen_at"] = created_at
    state["last_request_id"] = request_id
    state["last_status"] = status
    decision = str(event.get("decision", ""))
    if decision in FINAL_DECISIONS or bool(event.get("final")):
        completed = list(dict.fromkeys(state.get("completed_request_ids", []) + [request_id]))
        state["completed_request_ids"] = completed[-200:]
        if "decline_streak_after" in event:
            state["decline_streak"] = event.get("decline_streak_after")
        if decision:
            state["last_decision"] = decision
    atomic_write_json(_agent_state_path(output_root, computer_id), state)
    return {"ok": True, "path": str(path), "state": state}


def receive_computer_intervention_heartbeat(
    output_root: Path,
    heartbeat: dict[str, Any],
    *,
    user_agent: str = "",
) -> dict[str, Any]:
    """Record lightweight Windows-agent liveness without creating a request event."""
    computer_id = str(heartbeat.get("computer_id", "windows-main"))[:80]
    status = str(heartbeat.get("status", "online"))[:80]
    if status not in {"online", "degraded"}:
        raise ValueError("invalid heartbeat status")
    received_at = datetime.now().astimezone().isoformat(timespec="seconds")
    state = _agent_state(output_root, computer_id)
    state.update(
        {
            "computer_id": computer_id,
            "last_seen_at": received_at,
            "last_heartbeat_at": received_at,
            "agent_status": status,
            "agent_version": str(heartbeat.get("agent_version", ""))[:80],
            "last_poll_status": str(heartbeat.get("last_poll_status", ""))[:160],
            "active_lock_count": max(0, int(heartbeat.get("active_lock_count", 0) or 0)),
            "active_locks": [str(name)[:120] for name in heartbeat.get("active_locks", [])
                             if isinstance(name, str)][:20],
            "heartbeat_user_agent": user_agent[:300],
        }
    )
    atomic_write_json(_agent_state_path(output_root, computer_id), state)
    return {"ok": True, "state": state}


def _agent_state_path(output_root: Path, computer_id: str) -> Path:
    safe = "".join(ch for ch in computer_id if ch.isalnum() or ch in "-_") or "unknown"
    return output_root / "computer_interventions" / "state" / f"{safe}.json"


def _agent_state(output_root: Path, computer_id: str) -> dict[str, Any]:
    path = _agent_state_path(output_root, computer_id)
    if path.exists():
        try:
            return load_json(path)
        except (OSError, ValueError):
            pass
    return {"computer_id": computer_id, "completed_request_ids": []}
