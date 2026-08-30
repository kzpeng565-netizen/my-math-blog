from __future__ import annotations

import argparse
import copy
import fcntl
import hashlib
import json
import os
import sqlite3
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable
from zoneinfo import ZoneInfo

from common import datetime_to_ns, load_json, parse_timestamp
from computer_facts import _find_database, extract_computer_facts
from notifications import NtfyNotifier, NotificationResult, send_notification
from phone_facts import extract_phone_facts


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SETTINGS = PROJECT_ROOT / "config" / "settings.json"
DEFAULT_CONFIG = PROJECT_ROOT / "config" / "bedtime_reminder.json"
DEFAULT_STATE = PROJECT_ROOT / "data" / "state" / "bedtime-reminder-state.json"
DEFAULT_LOG = PROJECT_ROOT / "data" / "bedtime_reminder" / "events.jsonl"
POLICY_ID = "bedtime_stop"


class ReminderState(str, Enum):
    DISABLED = "DISABLED"
    WAITING = "WAITING"
    LEVEL_1_SENT = "LEVEL_1_SENT"
    LEVEL_2_ACTIVE = "LEVEL_2_ACTIVE"
    COOLDOWN = "COOLDOWN"


@dataclass(frozen=True)
class TriggerDecision:
    triggered: bool
    reason: str
    evidence: dict[str, Any]
    data_fresh: bool
    data_age: dict[str, float | None]
    device_activity_summary: dict[str, Any]


def _parse_time(value: str) -> time:
    hour, minute = (int(part) for part in value.split(":", 1))
    return time(hour, minute)


def is_in_window(now: datetime, start_text: str, end_text: str) -> bool:
    start = _parse_time(start_text)
    end = _parse_time(end_text)
    current = now.timetz().replace(tzinfo=None)
    if start <= end:
        return start <= current < end
    return current >= start or current < end


def event_date_for_window(now: datetime, start_text: str, end_text: str) -> date:
    start = _parse_time(start_text)
    end = _parse_time(end_text)
    current = now.timetz().replace(tzinfo=None)
    if start <= end:
        return now.date()
    if current < end:
        return now.date() - timedelta(days=1)
    return now.date()


def _iso(value: datetime | None) -> str | None:
    return value.isoformat(timespec="seconds") if value else None


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value)


def _seconds(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _minutes_or_test_seconds(
    policy: dict[str, Any],
    section: str,
    minutes_key: str,
    test_key: str,
    *,
    test_mode: bool,
) -> timedelta:
    if test_mode:
        seconds = policy.get("test_mode", {}).get(test_key)
        if seconds is not None:
            return timedelta(seconds=float(seconds))
    return timedelta(minutes=float(policy[section][minutes_key]))


def config_hash(config: dict[str, Any]) -> str:
    payload = json.dumps(config, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def atomic_write_json_fsynced(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)
    directory_fd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)


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
        "event_id": None,
        "current_state": ReminderState.DISABLED.value,
        "level_1_sent_at": None,
        "level_2_count": 0,
        "last_notification_at": None,
        "cooldown_until": None,
        "round_count": 0,
        "last_active_at": None,
        "policy_hash": policy_hash,
        "updated_at": _iso(now),
    }


def normalize_state(
    raw: dict[str, Any],
    *,
    now: datetime,
    event_id: str,
    policy_hash: str,
    active: bool,
) -> dict[str, Any]:
    state = dict(raw) if raw else initial_state(now, policy_hash)
    state.setdefault("policy_id", POLICY_ID)
    state.setdefault("current_state", ReminderState.DISABLED.value)
    state.setdefault("level_2_count", 0)
    state.setdefault("round_count", 0)
    state.setdefault("last_active_at", None)
    state.setdefault("policy_hash", policy_hash)
    if not active:
        return initial_state(now, policy_hash)
    if (
        state.get("event_id") != event_id
        or state.get("policy_hash") != policy_hash
        or state.get("current_state") == ReminderState.DISABLED.value
    ):
        state = initial_state(now, policy_hash)
        state["event_id"] = event_id
        state["current_state"] = ReminderState.WAITING.value
    state["updated_at"] = _iso(now)
    return state


def _latest_activitywatch_event_age_seconds(
    settings: dict[str, Any], now: datetime
) -> float | None:
    try:
        database = _find_database(Path(settings["activitywatch_sync_root"]))
    except FileNotFoundError:
        return None
    now_ns = datetime_to_ns(now)
    connection = sqlite3.connect(f"file:{database}?mode=ro", uri=True, timeout=10)
    connection.row_factory = sqlite3.Row
    try:
        row = connection.execute(
            """
            SELECT MAX(events.endtime) AS latest_end
            FROM events
            JOIN buckets ON buckets.id = events.bucketrow
            WHERE buckets.type IN ('afkstatus', 'currentwindow')
              AND events.starttime <= ?
            """,
            (now_ns,),
        ).fetchone()
    finally:
        connection.close()
    latest_end = row["latest_end"] if row else None
    if latest_end is None:
        return None
    return max(0.0, (now_ns - int(latest_end)) / 1_000_000_000)


def _phone_heartbeat_age_seconds(phone: dict[str, Any]) -> float | None:
    heartbeat = phone.get("quality", {}).get("collector_heartbeat", {})
    offset = heartbeat.get("offset_seconds_from_period_end")
    if offset is None:
        return None
    return abs(float(offset))


def _copy_settings_for_policy(
    settings: dict[str, Any], maximum_data_age_seconds: int
) -> dict[str, Any]:
    copied = copy.deepcopy(settings)
    processing = copied.setdefault("processing", {})
    processing["heartbeat_fresh_seconds"] = min(
        int(processing.get("heartbeat_fresh_seconds", maximum_data_age_seconds)),
        maximum_data_age_seconds,
    )
    processing["heartbeat_stale_seconds"] = maximum_data_age_seconds
    return copied


def should_trigger_bedtime_stop(
    settings: dict[str, Any],
    policy: dict[str, Any],
    now: datetime,
) -> TriggerDecision:
    activity = policy["activity"]
    maximum_age = int(activity.get("maximum_data_age_seconds", 120))
    lookback = int(activity.get("lookback_seconds", max(180, maximum_age)))
    minimum_active_seconds = float(activity.get("minimum_active_seconds", 30))
    policy_settings = _copy_settings_for_policy(settings, maximum_age)
    start = now - timedelta(seconds=lookback)

    try:
        computer = extract_computer_facts(policy_settings, start, now)
        computer_age = _latest_activitywatch_event_age_seconds(policy_settings, now)
    except Exception as error:
        computer = {"error": f"{type(error).__name__}: {error}"}
        computer_age = None

    try:
        phone = extract_phone_facts(policy_settings, start, now)
        phone_age = _phone_heartbeat_age_seconds(phone)
    except Exception as error:
        phone = {"error": f"{type(error).__name__}: {error}"}
        phone_age = None

    computer_seconds = _seconds(computer.get("activity", {}).get("not_afk_minutes")) * 60
    phone_seconds = _seconds(phone.get("screen", {}).get("on_minutes")) * 60
    computer_fresh = computer_age is not None and computer_age <= maximum_age
    phone_fresh = phone_age is not None and phone_age <= maximum_age
    computer_active = computer_fresh and computer_seconds >= minimum_active_seconds
    phone_active = phone_fresh and phone_seconds >= minimum_active_seconds
    triggered = computer_active or phone_active
    any_fresh = computer_fresh or phone_fresh

    if triggered:
        reason = "primary_device_active_after_bedtime"
    elif not any_fresh:
        reason = "activity_data_stale"
    else:
        reason = "primary_devices_inactive"

    summary = {
        "computer_not_afk_seconds": round(computer_seconds, 1),
        "phone_screen_on_seconds": round(phone_seconds, 1),
        "computer_fresh": computer_fresh,
        "phone_fresh": phone_fresh,
        "category_filter": "not_available_in_current_fact_layer",
    }
    evidence = {
        "computer_top_apps": computer.get("top_apps", [])[:5],
        "computer_top_websites": computer.get("top_websites", [])[:5],
        "phone_top_apps": phone.get("foreground", {}).get("top_apps", [])[:5],
        "computer_quality": computer.get("quality", {}),
        "phone_quality": phone.get("quality", {}),
        "computer_error": computer.get("error"),
        "phone_error": phone.get("error"),
    }
    return TriggerDecision(
        triggered=triggered,
        reason=reason,
        evidence=evidence,
        data_fresh=any_fresh,
        data_age={"computer": computer_age, "phone": phone_age},
        device_activity_summary=summary,
    )


class BedtimeReminderEngine:
    def __init__(
        self,
        *,
        settings: dict[str, Any],
        policy: dict[str, Any],
        store: StateStore,
        notifier: NtfyNotifier | None = None,
        decision_provider: Callable[[datetime], TriggerDecision] | None = None,
        test_mode: bool = False,
    ) -> None:
        self.settings = settings
        self.policy = policy
        self.store = store
        self.notifier = notifier or NtfyNotifier()
        self.decision_provider = decision_provider
        self.test_mode = test_mode
        self.policy_hash = config_hash(policy)

    def _decision(self, now: datetime) -> TriggerDecision:
        if self.decision_provider is not None:
            return self.decision_provider(now)
        return should_trigger_bedtime_stop(self.settings, self.policy, now)

    def _event_id(self, now: datetime) -> str:
        window = self.policy["active_window"]
        event_date = event_date_for_window(now, window["start"], window["end"])
        return f"bedtime-stop-{event_date.isoformat()}"

    def _log(
        self,
        *,
        now: datetime,
        previous_state: str,
        new_state: str,
        reason: str,
        state: dict[str, Any],
        decision: TriggerDecision | None = None,
        notification_level: int | None = None,
        notification_attempt: int | None = None,
        delivery: NotificationResult | None = None,
        error: str | None = None,
    ) -> None:
        self.store.append_log(
            {
                "timestamp": _iso(now),
                "policy_id": POLICY_ID,
                "event_id": state.get("event_id"),
                "previous_state": previous_state,
                "new_state": new_state,
                "reason": reason,
                "device_activity_summary": (
                    decision.device_activity_summary if decision else None
                ),
                "data_age": decision.data_age if decision else None,
                "notification_level": notification_level,
                "notification_attempt": notification_attempt,
                "send_success": delivery.accepted if delivery else None,
                "delivery": delivery.as_dict() if delivery else None,
                "error": error or (delivery.error if delivery else None),
            }
        )

    def _transition(
        self,
        state: dict[str, Any],
        *,
        now: datetime,
        new_state: ReminderState,
        reason: str,
        decision: TriggerDecision | None = None,
        delivery: NotificationResult | None = None,
        notification_level: int | None = None,
        notification_attempt: int | None = None,
    ) -> dict[str, Any]:
        previous = str(state.get("current_state", ReminderState.DISABLED.value))
        state["current_state"] = new_state.value
        state["updated_at"] = _iso(now)
        if decision and decision.triggered:
            state["last_active_at"] = _iso(now)
        self.store.save(state)
        self._log(
            now=now,
            previous_state=previous,
            new_state=new_state.value,
            reason=reason,
            state=state,
            decision=decision,
            notification_level=notification_level,
            notification_attempt=notification_attempt,
            delivery=delivery,
        )
        return state

    def _send_level(
        self, level: int, now: datetime
    ) -> tuple[NotificationResult, str, str]:
        section = self.policy[f"level_{level}"]
        result = send_notification(
            level=level,
            policy_id=POLICY_ID,
            title=section["title"],
            message=section["message"],
            priority=section.get("priority"),
            notifier=self.notifier,
        )
        return result, section["title"], _iso(now) or ""

    def step(self, now: datetime) -> dict[str, Any]:
        window = self.policy["active_window"]
        active = bool(self.policy.get("enabled", True)) and is_in_window(
            now, window["start"], window["end"]
        )
        event_id = self._event_id(now)
        raw = self.store.load()
        state = normalize_state(
            raw,
            now=now,
            event_id=event_id,
            policy_hash=self.policy_hash,
            active=active,
        )

        if not active:
            if raw and raw.get("current_state") != ReminderState.DISABLED.value:
                self._transition(
                    state,
                    now=now,
                    new_state=ReminderState.DISABLED,
                    reason="outside_active_window_reset",
                )
            elif raw and raw.get("policy_hash") == self.policy_hash:
                state = raw
            else:
                self.store.save(state)
            return {"status": "disabled", "state": state}

        current = ReminderState(state["current_state"])

        if current == ReminderState.WAITING:
            decision = self._decision(now)
            if not decision.triggered:
                self._log(
                    now=now,
                    previous_state=current.value,
                    new_state=current.value,
                    reason=decision.reason,
                    state=state,
                    decision=decision,
                )
                self.store.save(state)
                return {"status": "waiting", "decision": decision, "state": state}
            delivery, _, sent_at = self._send_level(1, now)
            state["level_1_sent_at"] = sent_at
            state["last_notification_at"] = sent_at
            state["level_2_count"] = 0
            state["cooldown_until"] = None
            state["round_count"] = int(state.get("round_count", 0)) + 1
            self._transition(
                state,
                now=now,
                new_state=ReminderState.LEVEL_1_SENT,
                reason=decision.reason,
                decision=decision,
                delivery=delivery,
                notification_level=1,
                notification_attempt=1,
            )
            return {"status": delivery.status, "decision": decision, "state": state}

        if current == ReminderState.LEVEL_1_SENT:
            sent_at = _parse_iso(state.get("level_1_sent_at"))
            delay = _minutes_or_test_seconds(
                self.policy,
                "level_2",
                "delay_after_level_1_minutes",
                "level_2_delay_seconds",
                test_mode=self.test_mode,
            )
            if sent_at and now < sent_at + delay:
                return {"status": "level_1_waiting", "state": state}
            decision = self._decision(now)
            if not decision.triggered:
                state["level_1_sent_at"] = None
                state["last_notification_at"] = None
                self._transition(
                    state,
                    now=now,
                    new_state=ReminderState.WAITING,
                    reason=decision.reason,
                    decision=decision,
                )
                return {"status": "back_to_waiting", "decision": decision, "state": state}
            delivery, _, sent_at_text = self._send_level(2, now)
            state["level_2_count"] = 1
            state["last_notification_at"] = sent_at_text
            self._transition(
                state,
                now=now,
                new_state=ReminderState.LEVEL_2_ACTIVE,
                reason=decision.reason,
                decision=decision,
                delivery=delivery,
                notification_level=2,
                notification_attempt=1,
            )
            return {"status": delivery.status, "decision": decision, "state": state}

        if current == ReminderState.LEVEL_2_ACTIVE:
            count = int(state.get("level_2_count", 0))
            maximum = int(self.policy["level_2"].get("maximum_notifications", 3))
            if count >= maximum:
                return self._enter_cooldown(state, now, "level_2_complete")
            last = _parse_iso(state.get("last_notification_at"))
            interval = _minutes_or_test_seconds(
                self.policy,
                "level_2",
                "interval_minutes",
                "level_2_interval_seconds",
                test_mode=self.test_mode,
            )
            if last and now < last + interval:
                return {"status": "level_2_waiting", "state": state}
            decision = self._decision(now)
            if not decision.triggered:
                state["level_1_sent_at"] = None
                state["last_notification_at"] = None
                self._transition(
                    state,
                    now=now,
                    new_state=ReminderState.WAITING,
                    reason=decision.reason,
                    decision=decision,
                )
                return {"status": "back_to_waiting", "decision": decision, "state": state}
            delivery, _, sent_at_text = self._send_level(2, now)
            count += 1
            state["level_2_count"] = count
            state["last_notification_at"] = sent_at_text
            if count >= maximum:
                self._log(
                    now=now,
                    previous_state=current.value,
                    new_state=current.value,
                    reason=decision.reason,
                    state=state,
                    decision=decision,
                    delivery=delivery,
                    notification_level=2,
                    notification_attempt=count,
                )
                self.store.save(state)
                return self._enter_cooldown(state, now, "level_2_complete")
            self._transition(
                state,
                now=now,
                new_state=ReminderState.LEVEL_2_ACTIVE,
                reason=decision.reason,
                decision=decision,
                delivery=delivery,
                notification_level=2,
                notification_attempt=count,
            )
            return {"status": delivery.status, "decision": decision, "state": state}

        if current == ReminderState.COOLDOWN:
            cooldown_until = _parse_iso(state.get("cooldown_until"))
            if cooldown_until and now < cooldown_until:
                return {"status": "cooldown", "state": state}
            decision = self._decision(now)
            if not decision.triggered:
                state["level_1_sent_at"] = None
                state["last_notification_at"] = None
                state["cooldown_until"] = None
                state["level_2_count"] = 0
                self._transition(
                    state,
                    now=now,
                    new_state=ReminderState.WAITING,
                    reason=decision.reason,
                    decision=decision,
                )
                return {"status": "back_to_waiting", "decision": decision, "state": state}
            delivery, _, sent_at = self._send_level(1, now)
            state["level_1_sent_at"] = sent_at
            state["last_notification_at"] = sent_at
            state["cooldown_until"] = None
            state["level_2_count"] = 0
            state["round_count"] = int(state.get("round_count", 0)) + 1
            self._transition(
                state,
                now=now,
                new_state=ReminderState.LEVEL_1_SENT,
                reason="cooldown_expired_recheck_triggered",
                decision=decision,
                delivery=delivery,
                notification_level=1,
                notification_attempt=1,
            )
            return {"status": delivery.status, "decision": decision, "state": state}

        self._transition(
            state,
            now=now,
            new_state=ReminderState.WAITING,
            reason="unknown_state_recovered",
        )
        return {"status": "recovered", "state": state}

    def _enter_cooldown(
        self, state: dict[str, Any], now: datetime, reason: str
    ) -> dict[str, Any]:
        cooldown = _minutes_or_test_seconds(
            self.policy,
            "cooldown",
            "minutes",
            "cooldown_seconds",
            test_mode=self.test_mode,
        )
        state["cooldown_until"] = _iso(now + cooldown)
        self._transition(
            state,
            now=now,
            new_state=ReminderState.COOLDOWN,
            reason=reason,
        )
        return {"status": "cooldown_started", "state": state}


def load_runtime(
    settings_path: Path,
    config_path: Path,
) -> tuple[dict[str, Any], dict[str, Any], ZoneInfo]:
    settings = load_json(settings_path)
    config = load_json(config_path)
    policy = config["policies"][POLICY_ID]
    timezone = ZoneInfo(policy["active_window"].get("timezone") or settings["timezone"])
    return settings, policy, timezone


def simulated_decision(kind: str) -> Callable[[datetime], TriggerDecision] | None:
    if kind == "real":
        return None

    def provider(now: datetime) -> TriggerDecision:
        del now
        if kind == "active":
            return TriggerDecision(
                triggered=True,
                reason="simulated_active",
                evidence={"source": "cli"},
                data_fresh=True,
                data_age={"computer": 0.0, "phone": 0.0},
                device_activity_summary={
                    "computer_not_afk_seconds": 60,
                    "phone_screen_on_seconds": 0,
                    "computer_fresh": True,
                    "phone_fresh": True,
                },
            )
        if kind == "stale":
            return TriggerDecision(
                triggered=False,
                reason="activity_data_stale",
                evidence={"source": "cli"},
                data_fresh=False,
                data_age={"computer": 999.0, "phone": 999.0},
                device_activity_summary={
                    "computer_not_afk_seconds": 0,
                    "phone_screen_on_seconds": 0,
                    "computer_fresh": False,
                    "phone_fresh": False,
                },
            )
        return TriggerDecision(
            triggered=False,
            reason="simulated_inactive",
            evidence={"source": "cli"},
            data_fresh=True,
            data_age={"computer": 0.0, "phone": 0.0},
            device_activity_summary={
                "computer_not_afk_seconds": 0,
                "phone_screen_on_seconds": 0,
                "computer_fresh": True,
                "phone_fresh": True,
            },
        )

    return provider


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--settings", type=Path, default=DEFAULT_SETTINGS)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE)
    parser.add_argument("--log", type=Path, default=DEFAULT_LOG)
    parser.add_argument("--now", help="ISO timestamp for tests")
    parser.add_argument(
        "--simulate-trigger",
        choices=("real", "active", "inactive", "stale"),
        default="real",
    )
    arguments = parser.parse_args()

    settings, policy, timezone = load_runtime(arguments.settings, arguments.config)
    now = (
        parse_timestamp(arguments.now, str(timezone.key))
        if arguments.now
        else datetime.now(timezone)
    )
    test_mode = os.environ.get("BEDTIME_REMINDER_TEST_MODE", "").lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    store = StateStore(arguments.state, arguments.log)
    if not store.acquire():
        print(json.dumps({"status": "locked"}, ensure_ascii=False))
        return 0
    try:
        engine = BedtimeReminderEngine(
            settings=settings,
            policy=policy,
            store=store,
            notifier=NtfyNotifier(),
            decision_provider=simulated_decision(arguments.simulate_trigger),
            test_mode=test_mode,
        )
        result = engine.step(now)
    finally:
        store.release()
    printable = {
        key: value
        for key, value in result.items()
        if key not in {"decision"}
    }
    if "decision" in result:
        decision = result["decision"]
        printable["decision"] = {
            "triggered": decision.triggered,
            "reason": decision.reason,
            "data_fresh": decision.data_fresh,
            "data_age": decision.data_age,
            "device_activity_summary": decision.device_activity_summary,
        }
    print(json.dumps(printable, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
