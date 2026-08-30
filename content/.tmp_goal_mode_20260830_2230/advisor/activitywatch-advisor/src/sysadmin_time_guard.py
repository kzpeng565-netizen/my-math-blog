from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable
from zoneinfo import ZoneInfo

from bedtime_reminder import atomic_write_json_fsynced
from common import load_json, parse_timestamp
from computer_facts import extract_computer_facts
from notifications import NtfyNotifier, NotificationResult


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SETTINGS = PROJECT_ROOT / "config" / "settings.json"
DEFAULT_CONFIG = PROJECT_ROOT / "config" / "sysadmin_time_guard.json"
DEFAULT_STATE = PROJECT_ROOT / "data" / "state" / "sysadmin-time-guard-state.json"
DEFAULT_LOG = PROJECT_ROOT / "data" / "sysadmin_time_guard" / "events.jsonl"
POLICY_ID = "sysadmin_time_guard"


class GuardState(str, Enum):
    IDLE = "IDLE"
    LEVEL_1_SENT = "LEVEL_1_SENT"
    COOLDOWN = "COOLDOWN"


@dataclass(frozen=True)
class GuardDecision:
    level_1: bool
    level_2: bool
    reason: str
    data_fresh: bool
    summary: dict[str, Any]
    evidence: dict[str, Any]

    @property
    def maintenance_detected(self) -> bool:
        return bool(self.summary.get("maintenance_seconds_60m", 0) > 0)

    @property
    def active_maintenance_detected(self) -> bool:
        return bool(
            self.data_fresh and self.summary.get("maintenance_seconds_recent", 0) > 0
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "level_1": self.level_1,
            "level_2": self.level_2,
            "reason": self.reason,
            "data_fresh": self.data_fresh,
            "summary": self.summary,
            "evidence": self.evidence,
        }


def _iso(value: datetime | None) -> str | None:
    return value.isoformat(timespec="seconds") if value else None


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value)


def _load_env_file(path: Path) -> None:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        if key and key not in os.environ:
            os.environ[key] = value.strip().strip('"').strip("'")


def _config_hash(config: dict[str, Any]) -> str:
    payload = json.dumps(config, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


class StateStore:
    def __init__(self, state_path: Path, log_path: Path) -> None:
        self.state_path = state_path
        self.log_path = log_path
        self.lock_path = state_path.with_suffix(".lock")
        self._lock_handle = None

    def acquire(self) -> bool:
        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock_handle = self.lock_path.open("a+")
        try:
            fcntl.flock(self._lock_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except BlockingIOError:
            return False

    def release(self) -> None:
        if self._lock_handle is None:
            return
        fcntl.flock(self._lock_handle.fileno(), fcntl.LOCK_UN)
        self._lock_handle.close()
        self._lock_handle = None

    def load(self) -> dict[str, Any]:
        if not self.state_path.exists():
            return {}
        try:
            return json.loads(self.state_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}

    def save(self, state: dict[str, Any]) -> None:
        atomic_write_json_fsynced(self.state_path, state)

    def append_log(self, record: dict[str, Any]) -> None:
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
            handle.flush()
            os.fsync(handle.fileno())


def initial_state(now: datetime, policy_hash: str) -> dict[str, Any]:
    return {
        "policy_id": POLICY_ID,
        "current_state": GuardState.IDLE.value,
        "level_1_sent_at": None,
        "level_2_sent_at": None,
        "last_notification_at": None,
        "last_maintenance_at": None,
        "maintenance_stopped_at": None,
        "policy_hash": policy_hash,
        "updated_at": _iso(now),
    }


def normalize_state(raw: dict[str, Any], now: datetime, policy_hash: str) -> dict[str, Any]:
    state = dict(raw) if raw else initial_state(now, policy_hash)
    if state.get("policy_hash") != policy_hash or state.get("policy_id") != POLICY_ID:
        return initial_state(now, policy_hash)
    state.setdefault("current_state", GuardState.IDLE.value)
    state.setdefault("level_1_sent_at", None)
    state.setdefault("level_2_sent_at", None)
    state.setdefault("last_notification_at", None)
    state.setdefault("last_maintenance_at", None)
    state.setdefault("maintenance_stopped_at", None)
    state["updated_at"] = _iso(now)
    return state


def _text_hit(value: str, needles: list[str]) -> bool:
    text = value.casefold()
    return any(needle.casefold() in text for needle in needles if needle)


def _item_text(item: dict[str, Any]) -> tuple[str, str, str, str, str]:
    app = str(item.get("app") or "")
    app_display = str(item.get("app_display") or "")
    domain = str(item.get("domain") or "")
    title = str(item.get("title") or "")
    return app, app_display, domain, title, " ".join([app, app_display, domain, title])


def is_maintenance_item(item: dict[str, Any], classification: dict[str, Any]) -> bool:
    return is_direct_maintenance_item(item, classification)


def is_direct_maintenance_item(item: dict[str, Any], classification: dict[str, Any]) -> bool:
    app, _, domain, _, full_text = _item_text(item)
    if _text_hit(full_text, list(classification.get("non_maintenance_title_keywords", []))):
        return False
    if app in set(classification.get("maintenance_apps", [])):
        return True
    if domain in set(classification.get("maintenance_domains", [])):
        return True
    return _text_hit(full_text, list(classification.get("maintenance_title_keywords", [])))


def is_context_bridge_item(item: dict[str, Any], classification: dict[str, Any]) -> bool:
    app, _, _, _, full_text = _item_text(item)
    if _text_hit(full_text, list(classification.get("non_maintenance_title_keywords", []))):
        return False
    if app in set(classification.get("context_bridge_apps", [])):
        return True
    return _text_hit(full_text, list(classification.get("context_bridge_keywords", [])))


def _overlap_seconds(
    left: datetime,
    right: datetime,
    start: datetime,
    end: datetime,
) -> float:
    return max(0.0, (min(right, end) - max(left, start)).total_seconds())


def _window_summary(
    intervals: list[tuple[datetime, datetime, bool, dict[str, Any]]],
    start: datetime,
    end: datetime,
) -> dict[str, float]:
    active = 0.0
    maintenance = 0.0
    for left, right, is_maintenance, _ in intervals:
        seconds = _overlap_seconds(left, right, start, end)
        active += seconds
        if is_maintenance:
            maintenance += seconds
    ratio = maintenance / active if active else 0.0
    return {
        "active_seconds": round(active, 3),
        "maintenance_seconds": round(maintenance, 3),
        "maintenance_ratio": round(ratio, 3),
    }


def _intervals_from_facts(
    facts: dict[str, Any],
    classification: dict[str, Any],
    timezone_name: str,
) -> list[tuple[datetime, datetime, bool, dict[str, Any]]]:
    raw_intervals: list[tuple[datetime, datetime, bool, bool, dict[str, Any]]] = []
    for item in facts.get("timeline", []):
        try:
            left = parse_timestamp(item["start"], timezone_name)
            right = parse_timestamp(item["end"], timezone_name)
        except (KeyError, TypeError, ValueError):
            continue
        if right <= left:
            continue
        raw_intervals.append(
            (
                left,
                right,
                is_direct_maintenance_item(item, classification),
                is_context_bridge_item(item, classification),
                item,
            )
        )

    max_gap_seconds = float(classification.get("context_bridge_max_gap_seconds", 300))
    intervals: list[tuple[datetime, datetime, bool, dict[str, Any]]] = []
    for left, right, direct, bridge, item in raw_intervals:
        source = "direct" if direct else None
        if bridge and not direct:
            for other_left, other_right, other_direct, _, _ in raw_intervals:
                if not other_direct:
                    continue
                gap_seconds = 0.0
                if right < other_left:
                    gap_seconds = (other_left - right).total_seconds()
                elif other_right < left:
                    gap_seconds = (left - other_right).total_seconds()
                if gap_seconds <= max_gap_seconds:
                    source = "context_bridge"
                    break
        tagged_item = dict(item)
        if source:
            tagged_item["maintenance_classification_source"] = source
        intervals.append((left, right, bool(source), tagged_item))
    return intervals


def _maintenance_source_counts(
    intervals: list[tuple[datetime, datetime, bool, dict[str, Any]]]
) -> dict[str, float]:
    totals: dict[str, float] = {}
    for left, right, is_maintenance, item in intervals:
        if not is_maintenance:
            continue
        source = str(item.get("maintenance_classification_source") or "direct")
        totals[source] = totals.get(source, 0.0) + (right - left).total_seconds()
    return {key: round(value, 3) for key, value in sorted(totals.items())}


def _context_bridge_items(
    intervals: list[tuple[datetime, datetime, bool, dict[str, Any]]]
) -> list[dict[str, Any]]:
    items = []
    for left, right, is_maintenance, item in intervals:
        if (
            is_maintenance
            and item.get("maintenance_classification_source") == "context_bridge"
        ):
            items.append(
                {
                    "start": left.isoformat(timespec="seconds"),
                    "end": right.isoformat(timespec="seconds"),
                    "duration_seconds": round((right - left).total_seconds(), 3),
                    "app": item.get("app_display") or item.get("app"),
                    "domain": item.get("domain"),
                    "title": item.get("title"),
                }
            )
    return sorted(
        items,
        key=lambda value: value["duration_seconds"],
        reverse=True,
    )[:8]


def _latest_timeline_end(
    intervals: list[tuple[datetime, datetime, bool, dict[str, Any]]]
) -> datetime | None:
    if not intervals:
        return None
    return max(right for _, right, _, _ in intervals)


def build_decision(
    *,
    settings: dict[str, Any],
    policy: dict[str, Any],
    now: datetime,
) -> GuardDecision:
    activity = policy["activity"]
    timezone_name = policy.get("timezone") or settings.get("timezone", "Asia/Shanghai")
    lookback = timedelta(minutes=float(activity.get("lookback_minutes", 60)))
    start = now - lookback

    try:
        facts = extract_computer_facts(settings, start, now)
        intervals = _intervals_from_facts(
            facts,
            policy.get("classification", {}),
            timezone_name,
        )
        latest_end = _latest_timeline_end(intervals)
        data_age = (now - latest_end).total_seconds() if latest_end else None
        data_fresh = data_age is not None and data_age <= float(
            activity.get("maximum_data_age_seconds", 600)
        )
        error = None
    except Exception as exc:
        facts = {}
        intervals = []
        data_age = None
        data_fresh = False
        error = f"{type(exc).__name__}: {exc}"

    level_1_start = now - timedelta(minutes=float(activity["level_1_window_minutes"]))
    level_2_start = now - timedelta(minutes=float(activity["level_2_window_minutes"]))
    recent_start = now - timedelta(
        minutes=float(activity.get("follow_up_recent_minutes", 6))
    )
    edge = timedelta(minutes=10)
    summary_30 = _window_summary(intervals, level_1_start, now)
    summary_60 = _window_summary(intervals, level_2_start, now)
    summary_recent = _window_summary(intervals, recent_start, now)
    first_edge = _window_summary(intervals, level_2_start, min(now, level_2_start + edge))
    last_edge = _window_summary(intervals, max(level_2_start, now - edge), now)

    minimum_active = float(activity.get("minimum_active_seconds", 60))
    level_1 = (
        data_fresh
        and summary_30["active_seconds"] >= minimum_active
        and summary_30["maintenance_ratio"] >= float(activity["level_1_maintenance_ratio"])
    )
    level_2 = (
        data_fresh
        and summary_60["active_seconds"] >= minimum_active
        and summary_60["maintenance_ratio"] >= float(activity["level_2_maintenance_ratio"])
        and first_edge["maintenance_ratio"]
        >= float(activity.get("level_2_minimum_edge_ratio", 0.4))
        and last_edge["maintenance_ratio"]
        >= float(activity.get("level_2_minimum_edge_ratio", 0.4))
    )

    if not data_fresh:
        reason = "activity_data_stale"
    elif level_2:
        reason = "maintenance_present_across_60m_window"
    elif level_1:
        reason = "maintenance_dominates_30m_window"
    elif summary_60["maintenance_seconds"] > 0:
        reason = "maintenance_below_threshold"
    else:
        reason = "no_recent_maintenance"

    maintenance_items = [
        {
            "start": left.isoformat(timespec="seconds"),
            "end": right.isoformat(timespec="seconds"),
            "duration_seconds": round((right - left).total_seconds(), 3),
            "app": item.get("app_display") or item.get("app"),
            "domain": item.get("domain"),
            "title": item.get("title"),
            "source": item.get("maintenance_classification_source", "direct"),
        }
        for left, right, is_maintenance, item in intervals
        if is_maintenance
    ]
    evidence = {
        "top_maintenance_items": sorted(
            maintenance_items,
            key=lambda value: value["duration_seconds"],
            reverse=True,
        )[:8],
        "top_apps": facts.get("top_apps", [])[:8],
        "top_websites": facts.get("top_websites", [])[:8],
        "maintenance_source_seconds": _maintenance_source_counts(intervals),
        "context_bridge_items": _context_bridge_items(intervals),
        "quality": facts.get("quality"),
        "error": error,
    }
    return GuardDecision(
        level_1=level_1,
        level_2=level_2,
        reason=reason,
        data_fresh=data_fresh,
        summary={
            "window_start": start.isoformat(timespec="seconds"),
            "window_end": now.isoformat(timespec="seconds"),
            "data_age_seconds": round(data_age, 3) if data_age is not None else None,
            "active_seconds_30m": summary_30["active_seconds"],
            "maintenance_seconds_30m": summary_30["maintenance_seconds"],
            "maintenance_ratio_30m": summary_30["maintenance_ratio"],
            "active_seconds_60m": summary_60["active_seconds"],
            "maintenance_seconds_60m": summary_60["maintenance_seconds"],
            "maintenance_ratio_60m": summary_60["maintenance_ratio"],
            "active_seconds_recent": summary_recent["active_seconds"],
            "maintenance_seconds_recent": summary_recent["maintenance_seconds"],
            "maintenance_ratio_recent": summary_recent["maintenance_ratio"],
            "first_10m_maintenance_ratio": first_edge["maintenance_ratio"],
            "last_10m_maintenance_ratio": last_edge["maintenance_ratio"],
        },
        evidence=evidence,
    )


class SysadminTimeGuardEngine:
    def __init__(
        self,
        *,
        settings: dict[str, Any],
        policy: dict[str, Any],
        store: StateStore,
        notifier: NtfyNotifier | None = None,
        decision_provider: Callable[[datetime], GuardDecision] | None = None,
        no_push: bool = False,
    ) -> None:
        self.settings = settings
        self.policy = policy
        self.store = store
        self.notifier = notifier or NtfyNotifier()
        self.decision_provider = decision_provider
        self.no_push = no_push
        self.policy_hash = _config_hash(policy)

    def _decision(self, now: datetime) -> GuardDecision:
        if self.decision_provider is not None:
            return self.decision_provider(now)
        return build_decision(settings=self.settings, policy=self.policy, now=now)

    def _send(self, level: int, now: datetime) -> NotificationResult:
        section = self.policy[f"level_{level}"]
        if self.no_push:
            return NotificationResult(
                status="skipped",
                provider="dry_run",
                title=section["title"],
                priority=section.get("priority", "default"),
            )
        return self.notifier.send(
            title=section["title"],
            message=section["message"],
            priority=section.get("priority", "default"),
            tags=["tools"] if level == 1 else ["warning"],
        )

    def _log(
        self,
        *,
        now: datetime,
        previous_state: str,
        new_state: str,
        reason: str,
        decision: GuardDecision,
        delivery: NotificationResult | None = None,
        notification_level: int | None = None,
    ) -> None:
        self.store.append_log(
            {
                "timestamp": _iso(now),
                "policy_id": POLICY_ID,
                "previous_state": previous_state,
                "new_state": new_state,
                "reason": reason,
                "data_fresh": decision.data_fresh,
                "summary": decision.summary,
                "evidence": decision.evidence,
                "notification_level": notification_level,
                "delivery": delivery.as_dict() if delivery else None,
                "send_success": delivery.accepted if delivery else None,
            }
        )

    def _save_transition(
        self,
        state: dict[str, Any],
        *,
        now: datetime,
        new_state: GuardState,
        reason: str,
        decision: GuardDecision,
        delivery: NotificationResult | None = None,
        notification_level: int | None = None,
    ) -> dict[str, Any]:
        previous = str(state.get("current_state", GuardState.IDLE.value))
        state["current_state"] = new_state.value
        state["updated_at"] = _iso(now)
        if decision.maintenance_detected:
            state["last_maintenance_at"] = _iso(now)
        self.store.save(state)
        self._log(
            now=now,
            previous_state=previous,
            new_state=new_state.value,
            reason=reason,
            decision=decision,
            delivery=delivery,
            notification_level=notification_level,
        )
        return state

    def step(self, now: datetime) -> dict[str, Any]:
        if not bool(self.policy.get("enabled", True)):
            return {"status": "disabled"}

        raw = self.store.load()
        state = normalize_state(raw, now, self.policy_hash)
        current = GuardState(state["current_state"])
        decision = self._decision(now)

        if decision.maintenance_detected:
            state["last_maintenance_at"] = _iso(now)

        if current != GuardState.IDLE:
            if decision.active_maintenance_detected:
                state["maintenance_stopped_at"] = None
            elif state.get("maintenance_stopped_at") is None:
                state["maintenance_stopped_at"] = _iso(now)

        maintenance_stopped_at = _parse_iso(state.get("maintenance_stopped_at"))
        clear_after = timedelta(
            minutes=float(self.policy["activity"]["cooldown_clear_minutes"])
        )
        if (
            current != GuardState.IDLE
            and not decision.active_maintenance_detected
            and maintenance_stopped_at is not None
            and now >= maintenance_stopped_at + clear_after
        ):
            state["level_1_sent_at"] = None
            state["level_2_sent_at"] = None
            state["last_notification_at"] = None
            state["last_maintenance_at"] = None
            state["maintenance_stopped_at"] = None
            self._save_transition(
                state,
                now=now,
                new_state=GuardState.IDLE,
                reason="stopped_maintenance_cooldown_complete",
                decision=decision,
            )
            return {"status": "reset", "decision": decision, "state": state}

        if current == GuardState.IDLE:
            if decision.level_2:
                delivery = self._send(2, now)
                sent_at = _iso(now)
                state["level_2_sent_at"] = sent_at
                state["last_notification_at"] = sent_at
                state["maintenance_stopped_at"] = None
                self._save_transition(
                    state,
                    now=now,
                    new_state=GuardState.COOLDOWN,
                    reason=decision.reason,
                    decision=decision,
                    delivery=delivery,
                    notification_level=2,
                )
                return {"status": delivery.status, "decision": decision, "state": state}
            if decision.level_1:
                delivery = self._send(1, now)
                sent_at = _iso(now)
                state["level_1_sent_at"] = sent_at
                state["last_notification_at"] = sent_at
                state["maintenance_stopped_at"] = None
                self._save_transition(
                    state,
                    now=now,
                    new_state=GuardState.LEVEL_1_SENT,
                    reason=decision.reason,
                    decision=decision,
                    delivery=delivery,
                    notification_level=1,
                )
                return {"status": delivery.status, "decision": decision, "state": state}

        if current == GuardState.LEVEL_1_SENT and decision.level_2:
            delivery = self._send(2, now)
            sent_at = _iso(now)
            state["level_2_sent_at"] = sent_at
            state["last_notification_at"] = sent_at
            state["maintenance_stopped_at"] = None
            self._save_transition(
                state,
                now=now,
                new_state=GuardState.COOLDOWN,
                reason=decision.reason,
                decision=decision,
                delivery=delivery,
                notification_level=2,
            )
            return {"status": delivery.status, "decision": decision, "state": state}

        if current != GuardState.IDLE and decision.active_maintenance_detected:
            last_notification_at = _parse_iso(state.get("last_notification_at"))
            repeat_after = timedelta(
                minutes=float(self.policy["activity"].get("follow_up_interval_minutes", 3))
            )
            if last_notification_at is None or now >= last_notification_at + repeat_after:
                notification_level = (
                    2
                    if current == GuardState.COOLDOWN
                    or state.get("level_2_sent_at")
                    or decision.level_2
                    else 1
                )
                delivery = self._send(notification_level, now)
                sent_at = _iso(now)
                state["last_notification_at"] = sent_at
                state["maintenance_stopped_at"] = None
                if notification_level == 2:
                    state["level_2_sent_at"] = state.get("level_2_sent_at") or sent_at
                    new_state = GuardState.COOLDOWN
                else:
                    new_state = GuardState.LEVEL_1_SENT
                self._save_transition(
                    state,
                    now=now,
                    new_state=new_state,
                    reason="maintenance_follow_up",
                    decision=decision,
                    delivery=delivery,
                    notification_level=notification_level,
                )
                return {"status": delivery.status, "decision": decision, "state": state}

        self.store.save(state)
        self._log(
            now=now,
            previous_state=current.value,
            new_state=current.value,
            reason=decision.reason,
            decision=decision,
        )
        return {"status": "no_action", "decision": decision, "state": state}


def run_guard(
    *,
    settings_path: Path,
    config_path: Path,
    state_path: Path,
    log_path: Path,
    ntfy_env_file: Path,
    no_push: bool = False,
    now: datetime | None = None,
) -> dict[str, Any]:
    settings = load_json(settings_path)
    policy = load_json(config_path)
    timezone = ZoneInfo(policy.get("timezone") or settings.get("timezone", "Asia/Shanghai"))
    now = now or datetime.now(timezone)
    _load_env_file(ntfy_env_file)
    store = StateStore(state_path, log_path)
    if not store.acquire():
        return {"status": "locked"}
    try:
        engine = SysadminTimeGuardEngine(
            settings=settings,
            policy=policy,
            store=store,
            no_push=no_push,
        )
        return engine.step(now)
    finally:
        store.release()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--settings", type=Path, default=DEFAULT_SETTINGS)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE)
    parser.add_argument("--log", type=Path, default=DEFAULT_LOG)
    parser.add_argument(
        "--ntfy-env",
        type=Path,
        default=Path("/home/conrad/.config/activitywatch-advisor/ntfy.env"),
    )
    parser.add_argument("--now")
    parser.add_argument("--no-push", action="store_true")
    args = parser.parse_args()

    if args.no_push and args.state == DEFAULT_STATE:
        args.state = DEFAULT_STATE.with_name("sysadmin-time-guard-dry-run-state.json")
    if args.no_push and args.log == DEFAULT_LOG:
        args.log = DEFAULT_LOG.with_name("dry-run-events.jsonl")

    now = datetime.fromisoformat(args.now) if args.now else None
    result = run_guard(
        settings_path=args.settings,
        config_path=args.config,
        state_path=args.state,
        log_path=args.log,
        ntfy_env_file=args.ntfy_env,
        no_push=args.no_push,
        now=now,
    )
    printable = dict(result)
    if isinstance(printable.get("decision"), GuardDecision):
        printable["decision"] = printable["decision"].as_dict()
    print(json.dumps(printable, ensure_ascii=False, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
