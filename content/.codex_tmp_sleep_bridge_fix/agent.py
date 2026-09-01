from __future__ import annotations

import json
import math
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta
from http.cookiejar import CookieJar
from pathlib import Path
from typing import Any
from uuid import uuid4
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import HTTPCookieProcessor, Request, build_opener


ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "config.json"
STATE_PATH = ROOT / "state.json"
HEALTH_PATH = ROOT / "data" / "agent-health.json"
UI_SCRIPT_PATH = ROOT / "intervention_ui.pyw"

DEFAULT_CONFIG = {
    "api_base": "https://pi.taild4d3f7.ts.net:8450",
    "focus_garden_base_url": "https://pi.taild4d3f7.ts.net:8460",
    "computer_id": "windows-main",
    "poll_seconds": 30,
    "heartbeat_seconds": 300,
    "auth_required": True,
    "popup_timeout_seconds": 90,
    "cold_turkey_exe": "D:\\Cold Turkey\\Cold Turkey Blocker.exe",
    "steam_game_executable_path": "C:\\steam\\steamapps\\common\\Magical Girl Celesphonia\\Game.exe",
    "steam_gate_lock_minutes": 5,
    "allowed_blocks": {
        "常刷网站": {
            "cold_turkey_block": "常刷网站",
            "display_name": "常刷网站",
            "default_lock_minutes": 30,
        },
        "bilibili": {
            "cold_turkey_block": "bilibili",
            "display_name": "bilibili",
            "default_lock_minutes": 30,
        },
        "steam游戏": {
            "cold_turkey_block": "steam",
            "display_name": "Steam 游戏",
            "default_lock_minutes": 30,
        },
    },
    "scheduled_locks": [
        {
            "id": "steam-night",
            "name": "steam游戏",
            "start": "23:30",
            "end": "12:00",
            "pre_lock_countdown_seconds": 60,
            "latest_defer": "01:00",
        }
    ],
}


# Keep the desktop tools visually aligned with My Focus Garden.
FOCUS_GARDEN_COLORS = {
    "bg": "#dce9cd",
    "panel": "#fffdf3",
    "ink": "#20352d",
    "muted": "#708278",
    "line": "#d8dbc3",
    "accent": "#287a58",
    "accent_dark": "#15553f",
    "mint": "#77c889",
    "lime": "#b8df72",
    "soil": "#8c5a32",
    "sun": "#f4c858",
    "danger": "#a84c45",
    "danger_bg": "#f5c5ac",
    "soft": "#edf3d7",
    "ok": "#287a58",
    "ok_bg": "#d9edb4",
    "warn": "#8c5a32",
    "warn_bg": "#f3df83",
    "bad": "#a84c45",
    "bad_bg": "#f5c5ac",
}


def load_json(path: Path, fallback: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return fallback


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, path)


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def parse_iso(value: str) -> datetime | None:
    try:
        return datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def _clock_minutes(value: str) -> int:
    hour, minute = (int(part) for part in value.split(":", 1))
    if not 0 <= hour <= 23 or not 0 <= minute <= 59:
        raise ValueError("scheduled lock time must use HH:MM")
    return hour * 60 + minute


def scheduled_window(moment: datetime, start_text: str, end_text: str) -> tuple[datetime, datetime] | None:
    """Return the active local-time window, including overnight schedules."""
    start_value = _clock_minutes(start_text)
    end_value = _clock_minutes(end_text)
    current = moment.hour * 60 + moment.minute
    start_today = moment.replace(
        hour=start_value // 60, minute=start_value % 60, second=0, microsecond=0
    )
    end_today = moment.replace(
        hour=end_value // 60, minute=end_value % 60, second=0, microsecond=0
    )
    if start_value < end_value:
        return (start_today, end_today) if start_value <= current < end_value else None
    if current >= start_value:
        return start_today, end_today + timedelta(days=1)
    if current < end_value:
        return start_today - timedelta(days=1), end_today
    return None


def next_schedule_start(moment: datetime, start_text: str) -> datetime:
    start_value = _clock_minutes(start_text)
    candidate = moment.replace(
        hour=start_value // 60, minute=start_value % 60, second=0, microsecond=0
    )
    return candidate if candidate > moment else candidate + timedelta(days=1)


def looks_corrupt(text: str) -> bool:
    stripped = text.strip()
    return not stripped or all(ch in "?" for ch in stripped)


def configure_windows_dpi_awareness() -> None:
    if os.name != "nt":
        return
    try:
        import ctypes

        awareness_context = ctypes.c_void_p(-4)
        ctypes.windll.user32.SetProcessDpiAwarenessContext(awareness_context)
        return
    except Exception:
        pass
    try:
        import ctypes

        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            import ctypes

            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


class PiClient:
    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.base = str(config["api_base"]).rstrip("/")
        self.opener = build_opener(HTTPCookieProcessor(CookieJar()))
        self.logged_in = False

    def login(self) -> None:
        if not bool(self.config.get("auth_required", True)):
            self.logged_in = True
            return
        password = os.environ.get("NEXT_ACTION_WEB_PASSWORD") or str(
            self.config.get("password", "")
        )
        if not password:
            raise RuntimeError(
                "Set NEXT_ACTION_WEB_PASSWORD or add password to config.json."
            )
        self.post("/api/login", {"password": password}, require_login=False)
        self.logged_in = True

    def get_pending(self) -> dict[str, Any] | None:
        query = urlencode({"computer_id": self.config["computer_id"]})
        data = self.get(f"/api/computer-interventions/pending?{query}")
        request = data.get("request")
        return request if isinstance(request, dict) else None

    def ack(self, request_id: str) -> None:
        self.post(
            "/api/computer-interventions/ack",
            {
                "computer_id": self.config["computer_id"],
                "request_id": request_id,
                "status": "acknowledged",
                "acknowledged_at": now_iso(),
                "final": False,
            },
        )

    def send_response(self, payload: dict[str, Any]) -> None:
        self.post("/api/computer-interventions/response", payload)

    def heartbeat(self, payload: dict[str, Any]) -> None:
        self.post("/api/computer-interventions/heartbeat", payload)

    def submit_shared_decision(self, request_id: str, decision: str) -> dict[str, Any]:
        return self.post(
            "/api/interventions/decision",
            {
                "request_id": request_id,
                "decision": decision,
                "device_id": self.config["computer_id"],
            },
        )

    def get(self, path: str) -> dict[str, Any]:
        return self._request("GET", path)

    def post(
        self,
        path: str,
        body: dict[str, Any],
        *,
        require_login: bool = True,
    ) -> dict[str, Any]:
        return self._request("POST", path, body, require_login=require_login)

    def _request(
        self,
        method: str,
        path: str,
        body: dict[str, Any] | None = None,
        *,
        require_login: bool = True,
    ) -> dict[str, Any]:
        if require_login and not self.logged_in:
            self.login()
        data = None
        headers = {"User-Agent": "computer-intervention-agent/0.1"}
        if body is not None:
            data = json.dumps(body, ensure_ascii=False).encode("utf-8")
            headers["Content-Type"] = "application/json"
        request = Request(self.base + path, data=data, headers=headers, method=method)
        try:
            with self.opener.open(request, timeout=15) as response:
                raw = response.read().decode("utf-8")
        except HTTPError as error:
            if error.code == 401 and require_login:
                self.logged_in = False
                self.login()
                return self._request(method, path, body, require_login=False)
            raise
        return json.loads(raw) if raw else {}


class GardenClient:
    """Narrow client for the Steam gate and its one Garden reward event."""

    def __init__(self, config: dict[str, Any]):
        self.base = str(config.get("focus_garden_base_url", "")).rstrip("/")

    def get_steam_gate(self) -> dict[str, Any]:
        return self._request("GET", "/api/steam-gate/status")

    def award_steam_close(self, event_id: str, occurred_at: str) -> dict[str, Any]:
        return self._request(
            "POST",
            "/api/steam-night/closed",
            {"event_id": event_id, "occurred_at": occurred_at},
        )

    def _request(
        self, method: str, path: str, body: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        if not self.base:
            raise RuntimeError("focus_garden_base_url is not configured")
        data = json.dumps(body, ensure_ascii=False).encode("utf-8") if body is not None else None
        headers = {
            "Accept": "application/json",
            "User-Agent": "computer-intervention-agent/steam-gate-1",
            "X-Computer-Intervention-Agent": "1",
        }
        if data is not None:
            headers["Content-Type"] = "application/json"
        request = Request(self.base + path, data=data, headers=headers, method=method)
        with build_opener().open(request, timeout=15) as response:
            raw = response.read().decode("utf-8")
        return json.loads(raw) if raw else {}


class InterventionAgent:
    def __init__(self) -> None:
        config = load_json(CONFIG_PATH, {})
        self.config = {**DEFAULT_CONFIG, **config}
        if "allowed_blocks" in config:
            self.config["allowed_blocks"] = config["allowed_blocks"]
        self.state = load_json(
            STATE_PATH,
            {
                "decline_streak": 0,
                "processed_requests": {},
                "active_locks": {},
            },
        )
        self.client = PiClient(self.config)
        self.garden_client = GardenClient(self.config)
        self._last_heartbeat_monotonic = 0.0
        self.instance_id = uuid4().hex

    def write_health(self, status: str, *, busy_until: datetime | None = None) -> None:
        """Expose a local liveness contract for the independent watchdog.

        This file intentionally does not depend on the Pi connection: a hung UI
        or failed network must still be distinguishable from a live core.
        """
        payload = {
            "schema_version": 1,
            "pid": os.getpid(),
            "instance_id": self.instance_id,
            "updated_at": now_iso(),
            "status": status,
        }
        if busy_until is not None:
            payload["busy_until"] = busy_until.isoformat(timespec="seconds")
        save_json(HEALTH_PATH, payload)

    def run_forever(self) -> None:
        print("Computer intervention agent started.")
        self.write_health("starting")
        while True:
            try:
                self.write_health("running")
                self.reconcile_expired_leases()
                self.reconcile_scheduled_locks()
                self.reconcile_steam_day_gate()
                self.poll_once()
            except (HTTPError, URLError, TimeoutError, RuntimeError, OSError) as error:
                self._record_poll(f"error: {type(error).__name__}")
                print(f"[{now_iso()}] poll failed: {type(error).__name__}: {error}")
            finally:
                self.write_health("idle")
            time.sleep(int(self.config.get("poll_seconds", 30)))

    def poll_once(self) -> None:
        self.reconcile_expired_leases()
        self.maybe_heartbeat()
        request = self.client.get_pending()
        if not request:
            self._record_poll("no_pending")
            return
        request_id = str(request["request_id"])
        processed = self.state.get("processed_requests", {})
        if request_id in processed:
            self.client.send_response(processed[request_id])
            self._record_poll(f"replayed {request_id}")
            return
        self._record_poll(f"handling {request_id}")
        self.client.ack(request_id)
        response = self.handle_request(request)
        if bool(response.get("final", True)):
            processed[request_id] = response
            self.state["processed_requests"] = dict(list(processed.items())[-200:])
            self._record_poll(f"completed {request_id}")
        else:
            self._record_poll(f"retrying {request_id}")
        self.client.send_response(response)

    def reconcile_expired_leases(self) -> None:
        """Stop agent-owned Cold Turkey leases that expired while asleep/offline."""
        active_locks = self.state.setdefault("active_locks", {})
        now = datetime.now().astimezone()
        changed = False
        for name, lease in list(active_locks.items()):
            if not isinstance(lease, dict) or lease.get("mode") != "agent_lease":
                continue
            until = parse_iso(str(lease.get("lock_until_estimated", "")))
            if until is None or until > now:
                continue
            result = self.stop_cold_turkey(
                str(name),
                str(lease.get("block", name)),
                expected_lease_id=str(lease.get("lease_id", "")),
            )
            lease["last_release_attempt_at"] = now_iso()
            lease["last_release_status"] = result.get("status", "unknown")
            if result.get("status") in {"released", "already_released", "lease_superseded"}:
                changed = True
            else:
                lease["release_error"] = result.get("error") or result.get("output_excerpt", "")
                changed = True
        if changed:
            save_json(STATE_PATH, self.state)

    def reconcile_scheduled_locks(self, now: datetime | None = None) -> None:
        """Prompt once at night, then apply a non-reversible lock until noon."""
        schedules = self.config.get("scheduled_locks", [])
        if not isinstance(schedules, list):
            return
        now = now or datetime.now().astimezone()
        runs = self.state.setdefault("scheduled_lock_runs", {})
        for schedule in schedules:
            if not isinstance(schedule, dict):
                continue
            schedule_id = str(schedule.get("id", "")).strip()
            name = str(schedule.get("name", "")).strip()
            if not schedule_id or name not in self.config.get("allowed_blocks", {}):
                continue
            window = scheduled_window(now, str(schedule.get("start", "23:30")), str(schedule.get("end", "12:00")))
            if window is None:
                continue
            window_start, window_end = window
            run_id = window_start.isoformat(timespec="seconds")
            run = runs.get(schedule_id)
            if not isinstance(run, dict) or run.get("window_start") != run_id:
                run = {
                    "window_start": run_id,
                    "window_end": window_end.isoformat(timespec="seconds"),
                    "event_id": f"{schedule_id}:{window_start.date().isoformat()}",
                    "created_at": now_iso(),
                }
                runs[schedule_id] = run
                save_json(STATE_PATH, self.state)
            elif run.get("lease_id") and not run.get("prompt_finished"):
                # One-time migration from the previous reversible schedule.
                # That run already displayed its save countdown and started
                # Steam blocking; never surprise the user with another night
                # prompt after an agent upgrade/restart the next morning.
                run["hard_lock_started"] = True
                run["migrated_from_legacy_lease"] = True
                run["updated_at"] = now_iso()
                save_json(STATE_PATH, self.state)
                continue
            if run.get("hard_lock_started"):
                continue
            defer_at = parse_iso(str(run.get("defer_until", "")))
            if defer_at and now < defer_at:
                continue
            countdown = max(1, int(schedule.get("pre_lock_countdown_seconds", 60) or 60))
            explicit_close = False
            if not run.get("prompt_finished"):
                response = ask_steam_night_user(
                    schedule,
                    window_start,
                    countdown,
                    self.write_health,
                )
                decision = str(response.get("decision", "timeout"))
                run["prompt_finished"] = True
                run["decision"] = decision
                run["decided_at"] = now_iso()
                if decision == "defer":
                    chosen = self._defer_datetime(
                        window_start,
                        str(response.get("defer_until", "")),
                        str(schedule.get("latest_defer", "01:00")),
                    )
                    if chosen > datetime.now().astimezone():
                        run["defer_until"] = chosen.isoformat(timespec="seconds")
                        save_json(STATE_PATH, self.state)
                        continue
                    decision = "timeout"
                    run["decision"] = decision
                explicit_close = decision == "close"
                save_json(STATE_PATH, self.state)
            else:
                show_pre_lock_countdown(
                    [{"display_name": self.config["allowed_blocks"][name].get("display_name", name)}],
                    countdown,
                    self.config,
                    self.write_health,
                    title="Steam 延时结束，即将关闭并锁定",
                )
            close_result = self.close_configured_steam_game()
            run["game_close"] = close_result
            run["game_closed_at"] = now_iso()
            if explicit_close:
                try:
                    run["reward"] = self.garden_client.award_steam_close(
                        str(run["event_id"]), now_iso()
                    )
                except Exception as error:
                    run["reward_error"] = f"{type(error).__name__}: {error}"
            remaining_minutes = max(1, math.ceil((window_end - now).total_seconds() / 60))
            allowed = self.config["allowed_blocks"][name]
            result = self.start_hard_cold_turkey(
                name,
                str(allowed.get("cold_turkey_block", name)),
                remaining_minutes,
                source="scheduled_night_hard_lock",
            )
            run["hard_lock_started"] = result.get("status") == "success"
            run["hard_lock_minutes"] = remaining_minutes
            run["hard_lock_result"] = result
            run["updated_at"] = now_iso()
            save_json(STATE_PATH, self.state)

    @staticmethod
    def _defer_datetime(
        window_start: datetime, selected: str, latest: str
    ) -> datetime:
        selected_minutes = _clock_minutes(selected)
        latest_minutes = _clock_minutes(latest)
        if latest_minutes >= _clock_minutes(window_start.strftime("%H:%M")):
            latest_dt = window_start.replace(
                hour=latest_minutes // 60, minute=latest_minutes % 60
            )
        else:
            latest_dt = (window_start + timedelta(days=1)).replace(
                hour=latest_minutes // 60, minute=latest_minutes % 60
            )
        selected_dt = window_start.replace(
            hour=selected_minutes // 60, minute=selected_minutes % 60
        )
        if selected_dt < window_start:
            selected_dt += timedelta(days=1)
        if selected_dt <= window_start or selected_dt > latest_dt:
            raise ValueError("Steam defer time must be after 23:30 and no later than 01:00")
        return selected_dt

    def reconcile_steam_day_gate(self, now: datetime | None = None) -> None:
        """After noon, renew a short hard lock until today's gate is eligible."""
        now = now or datetime.now().astimezone()
        current_minutes = now.hour * 60 + now.minute
        if current_minutes < 12 * 60 or current_minutes >= 23 * 60 + 30:
            return
        gate_state = self.state.setdefault("steam_day_gate", {})
        today = now.date().isoformat()
        last_check = parse_iso(str(gate_state.get("checked_at", "")))
        if gate_state.get("date") == today and last_check and (now - last_check).total_seconds() < 60:
            return
        eligible = False
        try:
            gate = self.garden_client.get_steam_gate()
            eligible = bool(gate.get("eligible")) and gate.get("date") == today
            gate_state.update({"date": today, "checked_at": now_iso(), "gate": gate})
            gate_state.pop("error", None)
        except Exception as error:
            gate_state.update({
                "date": today,
                "checked_at": now_iso(),
                "error": f"{type(error).__name__}: {error}",
            })
        if eligible:
            gate_state["status"] = "eligible_waiting_for_hard_lock_expiry"
            save_json(STATE_PATH, self.state)
            return
        name = "steam游戏"
        allowed = self.config.get("allowed_blocks", {}).get(name)
        if not isinstance(allowed, dict):
            gate_state["status"] = "missing_allowed_block"
            save_json(STATE_PATH, self.state)
            return
        minutes = max(2, int(self.config.get("steam_gate_lock_minutes", 5) or 5))
        result = self.start_hard_cold_turkey(
            name,
            str(allowed.get("cold_turkey_block", name)),
            minutes,
            source="steam_day_unlock_gate",
        )
        gate_state["status"] = "locked"
        gate_state["renewal"] = result
        gate_state["renewed_at"] = now_iso()
        save_json(STATE_PATH, self.state)

    def maybe_heartbeat(self) -> None:
        interval = max(60, int(self.config.get("heartbeat_seconds", 300)))
        now = time.monotonic()
        if now - self._last_heartbeat_monotonic < interval:
            return
        # State written by the former hard-lock implementation is only an
        # estimate and must not be presented as a live reversible lease.
        active_locks = self.state.setdefault("active_locks", {})
        for name, lease in list(active_locks.items()):
            if not isinstance(lease, dict) or lease.get("mode") != "agent_lease":
                active_locks.pop(name, None)
        try:
            self.client.heartbeat(
                {
                    "computer_id": self.config["computer_id"],
                    "status": "online",
                    "agent_version": "0.3",
                    "last_poll_status": self.state.get("last_poll_status", "starting"),
                    "active_lock_count": len(self.state.get("active_locks", {})),
                    "active_locks": sorted(str(name) for name in self.state.get("active_locks", {}).keys()),
                }
            )
            self._last_heartbeat_monotonic = now
            self.state["last_heartbeat_at"] = now_iso()
            self.state.pop("last_heartbeat_error", None)
            save_json(STATE_PATH, self.state)
        except (HTTPError, URLError, TimeoutError, RuntimeError, OSError) as error:
            self.state["last_heartbeat_error"] = type(error).__name__
            save_json(STATE_PATH, self.state)

    def _record_poll(self, status: str) -> None:
        self.state["last_poll_at"] = now_iso()
        self.state["last_poll_status"] = status
        save_json(STATE_PATH, self.state)

    def handle_request(self, request: dict[str, Any]) -> dict[str, Any]:
        self.reset_episode_if_recovered(request)
        request_id = str(request["request_id"])
        mode = str(request.get("mode", "ask_or_force"))

        # New shadow requests are one logical offer mirrored to the phone.
        # Only Pi decides which response wins and whether it fans out a
        # follow-up dual-device execution request.
        if mode == "offer":
            decision = ask_user(request, self.config, self.write_health)
            if decision == "ignored":
                return self.final_response(request_id, "ignored", [], "offer_timeout")
            resolved = self.client.submit_shared_decision(request_id, decision)
            result = resolved.get("decision", {}) if isinstance(resolved, dict) else {}
            effective = str(result.get("decision", decision))
            return self.final_response(
                request_id,
                effective,
                [],
                "shared_pi_decision",
                decline_streak_before=result.get("decline_streak_before"),
                decline_streak_after=result.get("decline_streak_after"),
            )

        # Focus Garden uses the existing intervention channel for a reversible
        # Cold Turkey lease.  This is intentionally handled before the normal
        # lock/deduplication path: a pause must always be allowed to release.
        if mode == "release":
            raw_lease_id = request.get("lease_id")
            executions = self.release_targets(
                request.get("targets", []),
                default_lease_id=str(raw_lease_id).strip() if raw_lease_id else "",
            )
            terminal = all(
                item.get("status") in {
                    "released",
                    "already_released",
                    "lease_superseded",
                    "unknown_block",
                    "lease_id_required",
                }
                for item in executions
            )
            legacy_only = bool(executions) and all(
                item.get("status") == "lease_id_required" for item in executions
            )
            response = self.final_response(
                request_id,
                "legacy_release_ignored" if legacy_only else ("released" if terminal else "release_pending"),
                executions,
                "lease_id_required" if legacy_only else ("shared_release" if terminal else "release_retry"),
                final=terminal,
            )
            return response

        enabled_targets = self.enabled_targets(request)
        if not enabled_targets:
            return self.final_response(request_id, "skipped", [], "no_enabled_targets")
        already_locked = self.already_locked_results(enabled_targets)
        if already_locked and len(already_locked) == len(enabled_targets):
            self.reset_declines("already_locked")
            return self.final_response(request_id, "already_locked", already_locked)

        # A settled manual/accepted/forced command must never show another
        # local prompt: that would let the two devices diverge or double count.
        if mode == "execute":
            source = str(request.get("source", ""))
            countdown = max(
                (int(item.get("pre_lock_countdown_seconds", 0) or 0) for item in enabled_targets),
                default=0,
            )
            if source == "forced_intervention" and countdown:
                show_pre_lock_countdown(
                    enabled_targets, countdown, self.config, self.write_health
                )
            executions = self.execute_targets(
                enabled_targets, request_id=request_id, source=source
            )
            show_execution_notice(enabled_targets, self.config)
            decision = "forced" if source == "forced_intervention" else "accepted"
            if any(item["status"] in {"success", "already_locked"} for item in executions):
                self.reset_declines("lock_satisfied")
            return self.final_response(request_id, decision, executions, "shared_execution")

        decline_before = int(self.state.get("decline_streak", 0) or 0)
        policy = request.get("decline_policy", {})
        max_declines = int(policy.get("max_declines_before_force", 2))
        force = decline_before >= max_declines
        decision = "forced" if force else ask_user(request, self.config, self.write_health)
        if decision == "declined":
            self.state["decline_streak"] = decline_before + 1
            self.state["last_decline_at"] = now_iso()
            return self.final_response(
                request_id,
                "declined",
                [],
                decline_streak_before=decline_before,
                decline_streak_after=self.state["decline_streak"],
            )
        if decision == "ignored":
            return self.final_response(
                request_id,
                "ignored",
                [],
                decline_streak_before=decline_before,
                decline_streak_after=decline_before,
            )
        executions = self.execute_targets(enabled_targets, request_id=request_id, source=str(request.get("source", "")))
        if any(item["status"] in {"success", "already_locked"} for item in executions):
            self.reset_declines("lock_satisfied")
        return self.final_response(
            request_id,
            decision,
            executions,
            decline_streak_before=decline_before,
            decline_streak_after=int(self.state.get("decline_streak", 0) or 0),
        )

    def enabled_targets(self, request: dict[str, Any]) -> list[dict[str, Any]]:
        result = []
        for target in request.get("targets", []):
            normalized = self.normalize_target(target)
            name = normalized["name"]
            if name not in self.config["allowed_blocks"]:
                result.append(
                    {
                        "name": name,
                        "enabled": False,
                        "reject_reason": "unknown_block",
                    }
                )
                continue
            if not normalized.get("enabled", True) or normalized.get("exempt"):
                continue
            result.append(normalized)
        return [item for item in result if item.get("enabled", True)]

    def normalize_target(self, target: dict[str, Any]) -> dict[str, Any]:
        raw_name = str(target.get("name", ""))
        cold_turkey_block = str(target.get("cold_turkey_block", ""))
        allowed_blocks = self.config["allowed_blocks"]
        name = raw_name
        if name not in allowed_blocks and cold_turkey_block in allowed_blocks:
            name = cold_turkey_block
        if name not in allowed_blocks and looks_corrupt(name):
            for allowed_name in allowed_blocks:
                if allowed_name != "bilibili":
                    name = allowed_name
                    break
        normalized = dict(target)
        normalized["name"] = name
        allowed = allowed_blocks.get(name, {})
        normalized["display_name"] = str(allowed.get("display_name", name))
        return normalized

    def already_locked_results(self, targets: list[dict[str, Any]]) -> list[dict[str, Any]]:
        results = []
        active_locks = self.state.get("active_locks", {})
        current = datetime.now().astimezone()
        for target in targets:
            name = str(target.get("name"))
            until = parse_iso(str(active_locks.get(name, {}).get("lock_until_estimated", "")))
            if until and until > current:
                results.append(
                    {
                        "block": name,
                        "action": "already_locked_by_agent",
                        "status": "already_locked",
                        "lock_until_estimated": until.isoformat(timespec="seconds"),
                    }
                )
        return results

    def execute_targets(self, targets: list[dict[str, Any]], *, request_id: str = "", source: str = "") -> list[dict[str, Any]]:
        results = []
        for target in targets:
            name = str(target.get("name"))
            allowed = self.config["allowed_blocks"].get(name)
            if not allowed:
                results.append({"block": name, "action": "rejected", "status": "unknown_block"})
                continue
            block = str(allowed.get("cold_turkey_block", name))
            minutes = int(target.get("lock_minutes", allowed.get("default_lock_minutes", 30)))
            result = self.start_cold_turkey(
                name,
                block,
                minutes,
                lease_id=str(target.get("lease_id") or request_id),
                source=source,
            )
            results.append(result)
        save_json(STATE_PATH, self.state)
        return results

    def release_targets(self, targets: list[dict[str, Any]], *, default_lease_id: str = "") -> list[dict[str, Any]]:
        results = []
        for target in targets:
            normalized = self.normalize_target(target)
            name = str(normalized.get("name", ""))
            allowed = self.config["allowed_blocks"].get(name)
            if not allowed:
                results.append({"block": name, "action": "rejected", "status": "unknown_block"})
                continue
            block = str(allowed.get("cold_turkey_block", name))
            expected_lease_id = str(normalized.get("lease_id") or default_lease_id).strip()
            # Releases created before lease ownership existed are not safe to
            # replay.  They cannot prove which later focus session they belong
            # to, so treating them as a generic `-stop` could unlock a new one.
            if not expected_lease_id:
                results.append(
                    {
                        "block": name,
                        "cold_turkey_block": block,
                        "action": "cold_turkey_stop_lease",
                        "status": "lease_id_required",
                    }
                )
                continue
            results.append(
                self.stop_cold_turkey(
                    name,
                    block,
                    expected_lease_id=expected_lease_id,
                )
            )
        save_json(STATE_PATH, self.state)
        return results

    def start_cold_turkey(self, name: str, block: str, minutes: int, *, lease_id: str = "", source: str = "") -> dict[str, Any]:
        exe = str(self.config["cold_turkey_exe"])
        # Do not use ``-lock`` here.  Focus Garden owns this short-lived
        # session through the agent and must be able to stop it on a pause.
        command = [exe, "-start", block]
        started_at = datetime.now().astimezone()
        owned_lease_id = lease_id or f"{name}:{started_at.timestamp()}"
        until = started_at + timedelta(minutes=minutes)
        # Persist ownership before spawning Cold Turkey.  A process crash after
        # `-start` but before its result is known is therefore recovered as an
        # uncertain, lease-bound session instead of being silently forgotten.
        active_locks = self.state.setdefault("active_locks", {})
        active_locks[name] = {
            "block": block,
            "mode": "agent_lease",
            "lease_id": owned_lease_id,
            "source": source,
            "last_command_at": started_at.isoformat(timespec="seconds"),
            "lock_until_estimated": until.isoformat(timespec="seconds"),
            "lease_state": "starting",
        }
        save_json(STATE_PATH, self.state)
        last_result: dict[str, Any] = {}
        # Cold Turkey normally works while Windows is locked, but an unavailable
        # blocker process used to make the agent permanently acknowledge failure.
        # Retry the exact same allow-listed command once after 30 seconds.
        for attempt in (1, 2):
            try:
                completed = subprocess.run(
                    command,
                    text=True,
                    capture_output=True,
                    timeout=30,
                    check=False,
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                )
                combined = (completed.stdout + "\n" + completed.stderr).strip()
                success = completed.returncode == 0 or any(
                    marker in combined.lower() for marker in ("already", "locked", "running")
                )
                last_result = {
                    "block": name,
                    "cold_turkey_block": block,
                    "action": "cold_turkey_start_lease",
                    "lock_minutes": minutes,
                    "exit_code": completed.returncode,
                    "status": "success" if success else "unknown_command_result",
                    "attempts": attempt,
                    "output_excerpt": combined[:500],
                }
                if success:
                    lease = self.state.setdefault("active_locks", {}).get(name, {})
                    if isinstance(lease, dict) and lease.get("lease_id") == owned_lease_id:
                        lease["lease_state"] = "active"
                        lease["started_confirmed_at"] = now_iso()
                        lease["start_attempts"] = attempt
                        save_json(STATE_PATH, self.state)
                    return last_result
            except Exception as error:
                last_result = {
                    "block": name,
                    "cold_turkey_block": block,
                    "action": "cold_turkey_start_lease",
                    "lock_minutes": minutes,
                    "status": "error",
                    "attempts": attempt,
                    "error": f"{type(error).__name__}: {error}",
                }
            if attempt == 1:
                time.sleep(30)
        lease = self.state.setdefault("active_locks", {}).get(name, {})
        if isinstance(lease, dict) and lease.get("lease_id") == owned_lease_id:
            # Even an apparently failed command can have reached the blocker.
            # Keep the exact lease through its deadline; recovery may stop only
            # this owned record, never an unleased Cold Turkey session.
            lease["lease_state"] = "start_uncertain"
            lease["last_start_result"] = last_result.get("status", "unknown")
            save_json(STATE_PATH, self.state)
        return last_result

    def start_hard_cold_turkey(
        self, name: str, block: str, minutes: int, *, source: str = ""
    ) -> dict[str, Any]:
        """Start a Cold Turkey lock that the agent cannot cancel early."""
        minutes = max(1, int(minutes))
        command = [str(self.config["cold_turkey_exe"]), "-start", block, "-lock", str(minutes)]
        try:
            completed = subprocess.run(
                command,
                text=True,
                capture_output=True,
                timeout=30,
                check=False,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            combined = (completed.stdout + "\n" + completed.stderr).strip()
            output_lower = combined.lower()
            # Cold Turkey can print "Error: Invalid block name" while still
            # returning exit code 0.  Exit status alone is therefore not proof
            # that Steam was locked; reject explicit failure text first.
            failure_markers = (
                "error:", "invalid block", "not found", "failed", "unknown block",
            )
            success = not any(marker in output_lower for marker in failure_markers) and (
                completed.returncode == 0 or any(
                    marker in output_lower for marker in ("already", "locked", "running")
                )
            )
            return {
                "block": name,
                "cold_turkey_block": block,
                "action": "cold_turkey_start_hard_lock",
                "lock_minutes": minutes,
                "source": source,
                "exit_code": completed.returncode,
                "status": "success" if success else "command_rejected",
                "output_excerpt": combined[:500],
            }
        except Exception as error:
            return {
                "block": name,
                "cold_turkey_block": block,
                "action": "cold_turkey_start_hard_lock",
                "lock_minutes": minutes,
                "source": source,
                "status": "error",
                "error": f"{type(error).__name__}: {error}",
            }

    def close_configured_steam_game(self) -> dict[str, Any]:
        """Close only the configured executable, never every process named Game.exe."""
        configured = str(self.config.get("steam_game_executable_path", "")).strip()
        if not configured:
            return {"status": "not_configured", "matched_pids": []}
        try:
            import psutil
        except ImportError as error:
            return {"status": "error", "matched_pids": [], "error": str(error)}
        expected = os.path.normcase(os.path.abspath(configured))
        processes = []
        for process in psutil.process_iter(["pid", "exe"]):
            try:
                executable = process.info.get("exe") or process.exe()
                if executable and os.path.normcase(os.path.abspath(executable)) == expected:
                    processes.append(process)
            except (psutil.AccessDenied, psutil.NoSuchProcess, OSError):
                continue
        pids = [process.pid for process in processes]
        if not processes:
            return {"status": "not_running", "matched_pids": []}
        if os.name == "nt":
            try:
                import ctypes

                user32 = ctypes.windll.user32
                callback_type = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

                def close_window(hwnd: int, _lparam: int) -> bool:
                    pid = ctypes.c_ulong()
                    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                    if pid.value in pids and user32.IsWindowVisible(hwnd):
                        user32.PostMessageW(hwnd, 0x0010, 0, 0)  # WM_CLOSE
                    return True

                user32.EnumWindows(callback_type(close_window), 0)
            except Exception:
                pass
        gone, alive = psutil.wait_procs(processes, timeout=15)
        for process in alive:
            try:
                process.terminate()
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                pass
        _, alive = psutil.wait_procs(alive, timeout=5)
        for process in alive:
            try:
                process.kill()
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                pass
        final_alive = [process.pid for process in alive if process.is_running()]
        return {
            "status": "closed" if not final_alive else "close_incomplete",
            "matched_pids": pids,
            "remaining_pids": final_alive,
            "executable_path": configured,
        }

    def stop_cold_turkey(self, name: str, block: str, *, expected_lease_id: str = "") -> dict[str, Any]:
        current_lease = self.state.setdefault("active_locks", {}).get(name)
        current_lease_id = str(current_lease.get("lease_id", "")) if isinstance(current_lease, dict) else ""
        if expected_lease_id and not current_lease_id:
            return {
                "block": name,
                "cold_turkey_block": block,
                "action": "cold_turkey_stop_lease",
                "status": "lease_not_owned",
                "expected_lease_id": expected_lease_id,
            }
        if expected_lease_id and current_lease_id and expected_lease_id != current_lease_id:
            return {
                "block": name,
                "cold_turkey_block": block,
                "action": "cold_turkey_stop_lease",
                "status": "lease_superseded",
                "expected_lease_id": expected_lease_id,
                "current_lease_id": current_lease_id,
            }
        exe = str(self.config["cold_turkey_exe"])
        command = [exe, "-stop", block]
        try:
            completed = subprocess.run(
                command,
                text=True,
                capture_output=True,
                timeout=30,
                check=False,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            combined = (completed.stdout + "\n" + completed.stderr).strip()
            success = completed.returncode == 0 or any(marker in combined.lower() for marker in ("not running", "stopped", "already"))
            if success:
                latest = self.state.setdefault("active_locks", {}).get(name)
                latest_id = str(latest.get("lease_id", "")) if isinstance(latest, dict) else ""
                if not expected_lease_id or not latest_id or expected_lease_id == latest_id:
                    self.state.setdefault("active_locks", {}).pop(name, None)
            return {
                "block": name, "cold_turkey_block": block, "action": "cold_turkey_stop_lease",
                "exit_code": completed.returncode, "status": "released" if success else "unknown_command_result",
                "output_excerpt": combined[:500],
            }
        except Exception as error:
            return {"block": name, "cold_turkey_block": block, "action": "cold_turkey_stop_lease",
                    "status": "error", "error": f"{type(error).__name__}: {error}"}

    def reset_episode_if_recovered(self, request: dict[str, Any]) -> None:
        observations = request.get("observations", {})
        policy = request.get("decline_policy", {})
        meaningful = float(observations.get("meaningful_minutes", 0) or 0)
        rest = float(observations.get("confirmed_rest_minutes", 0) or 0)
        if meaningful >= float(policy.get("reset_when_meaningful_minutes_at_least", 20)):
            self.reset_declines("meaningful_activity_recovered")
        if rest >= float(policy.get("reset_when_confirmed_rest_minutes_at_least", 10)):
            self.reset_declines("confirmed_rest_recovered")
        last = parse_iso(str(self.state.get("last_decline_at", "")))
        if last:
            minutes = (datetime.now().astimezone() - last).total_seconds() / 60
            if minutes >= float(policy.get("episode_reset_minutes", 90)):
                self.reset_declines("episode_timeout")

    def reset_declines(self, reason: str) -> None:
        self.state["decline_streak"] = 0
        self.state["last_reset_at"] = now_iso()
        self.state["last_reset_reason"] = reason

    def final_response(
        self,
        request_id: str,
        decision: str,
        executions: list[dict[str, Any]],
        reason: str = "",
        *,
        decline_streak_before: int | None = None,
        decline_streak_after: int | None = None,
        final: bool = True,
    ) -> dict[str, Any]:
        return {
            "computer_id": self.config["computer_id"],
            "request_id": request_id,
            "agent_version": "0.1",
            "status": "final" if final else "retrying",
            "final": final,
            "decision": decision,
            "reason": reason,
            "decided_at": now_iso(),
            "decline_streak_before": decline_streak_before
            if decline_streak_before is not None
            else int(self.state.get("decline_streak", 0) or 0),
            "decline_streak_after": decline_streak_after
            if decline_streak_after is not None
            else int(self.state.get("decline_streak", 0) or 0),
            "executions": executions,
        }


def ask_steam_night_user(
    schedule: dict[str, Any],
    window_start: datetime,
    seconds: int,
    on_wait: Any = None,
) -> dict[str, Any]:
    """Offer explicit close/reward or a bounded 15-minute defer choice."""
    latest_text = str(schedule.get("latest_defer", "01:00"))
    latest_minutes = _clock_minutes(latest_text)
    latest = window_start.replace(hour=latest_minutes // 60, minute=latest_minutes % 60)
    if latest <= window_start:
        latest += timedelta(days=1)
    cursor = window_start + timedelta(minutes=15)
    options: list[str] = []
    while cursor <= latest:
        options.append(cursor.strftime("%H:%M"))
        cursor += timedelta(minutes=15)
    response = _launch_intervention_ui(
        {
            "kind": "steam_night_prompt",
            "title": "23:30 · Steam 夜间收尾",
            "message": (
                "现在关闭游戏可获得 1 次普通植物种植机会。\n"
                "也可以延时，但最晚只能到 01:00；60 秒无操作将自动关闭并锁定。"
            ),
            "timeout_seconds": max(1, int(seconds)),
            "defer_options": options,
        },
        wait=True,
        on_wait=on_wait,
    )
    decision = str(response.get("decision", "timeout"))
    if decision == "close":
        return {"decision": "close"}
    if decision == "defer" and str(response.get("defer_until", "")) in options:
        return {"decision": "defer", "defer_until": str(response["defer_until"])}
    return {"decision": "timeout"}


def show_execution_notice(targets: list[dict[str, Any]], config: dict[str, Any]) -> None:
    """Launch the Tk notice in another process; it can never crash the core."""
    labels = [str(target.get("display_name", target.get("name", "锁机"))) for target in targets]
    minutes = max((int(target.get("lock_minutes", 0) or 0) for target in targets), default=0)
    _launch_intervention_ui(
        {
            "kind": "notice",
            "title": "专注锁机已开始",
            "message": f"已开始 {minutes} 分钟专注锁机\n" + "、".join(labels),
            "timeout_seconds": 7,
        },
        wait=False,
    )


def show_pre_lock_countdown(
    targets: list[dict[str, Any]],
    seconds: int,
    config: dict[str, Any],
    on_wait: Any = None,
    *,
    title: str = "Steam 强制锁定即将开始",
) -> None:
    """Show a non-cancellable save warning and wait before starting Cold Turkey."""
    seconds = max(0, int(seconds))
    if seconds <= 0:
        return
    labels = [str(item.get("display_name", item.get("name", "Steam 游戏"))) for item in targets]
    _launch_intervention_ui(
        {
            "kind": "countdown",
            "title": title,
            "message": "请立即保存游戏进度。倒计时结束后将启动 Cold Turkey。",
            "targets": labels,
            "timeout_seconds": seconds,
        },
        wait=False,
    )
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if callable(on_wait):
            on_wait(
                "pre_lock_countdown",
                busy_until=datetime.now().astimezone() + timedelta(
                    seconds=max(1, int(deadline - time.monotonic()))
                ),
            )
        time.sleep(min(1, max(0, deadline - time.monotonic())))


def legacy_ask_user(request: dict[str, Any], config: dict[str, Any]) -> str:
    configure_windows_dpi_awareness()
    try:
        import tkinter as tk
        from tkinter import font as tkfont
    except Exception:
        return "ignored"
    result = {"decision": "ignored"}
    root = tk.Tk()
    root.title("\u7535\u8111\u4ecb\u5165\u63d0\u9192")
    root.attributes("-topmost", True)
    root.resizable(False, False)

    colors = dict(FOCUS_GARDEN_COLORS)
    root.configure(bg=colors["bg"])

    try:
        dpi = root.winfo_fpixels("1i")
        root.tk.call("tk", "scaling", max(1.0, min(1.75, dpi / 72.0)))
    except Exception:
        pass

    base_font = tkfont.Font(family="Microsoft YaHei", size=12)
    title_font = tkfont.Font(family="Microsoft YaHei", size=22, weight="bold")
    subtitle_font = tkfont.Font(family="Microsoft YaHei", size=13)
    section_font = tkfont.Font(family="Microsoft YaHei", size=14, weight="bold")
    metric_font = tkfont.Font(family="Consolas", size=22, weight="bold")
    button_font = tkfont.Font(family="Microsoft YaHei", size=12, weight="bold")

    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    width = min(900, max(780, screen_w - 120))
    height = min(820, max(720, screen_h - 120))
    x = max(0, int((screen_w - width) / 2))
    y = max(0, int((screen_h - height) / 3))
    root.geometry(f"{width}x{height}+{x}+{y}")

    outer = tk.Frame(root, bg=colors["bg"])
    outer.pack(fill="both", expand=True)
    canvas = tk.Canvas(outer, bg=colors["bg"], highlightthickness=0)
    scrollbar = tk.Scrollbar(outer, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    shell = tk.Frame(canvas, bg=colors["bg"], padx=18, pady=16)
    window_id = canvas.create_window((0, 0), window=shell, anchor="nw")

    def refresh_scroll(_event=None) -> None:
        canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.itemconfigure(window_id, width=canvas.winfo_width())

    shell.bind("<Configure>", refresh_scroll)
    canvas.bind("<Configure>", refresh_scroll)
    canvas.bind_all(
        "<MouseWheel>",
        lambda event: canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"),
    )

    hero = tk.Frame(
        shell,
        bg=colors["panel"],
        highlightthickness=3,
        highlightbackground=colors["accent_dark"],
    )
    hero.pack(fill="x")
    tk.Frame(hero, bg=colors["sun"], width=9).pack(side="left", fill="y")
    hero_body = tk.Frame(hero, bg=colors["panel"], padx=16, pady=14)
    hero_body.pack(side="left", fill="both", expand=True)
    tk.Label(
        hero_body,
        text="\u73b0\u5728\u53ef\u80fd\u9700\u8981\u4e00\u70b9\u4ecb\u5165",
        bg=colors["panel"],
        fg=colors["ink"],
        font=title_font,
        anchor="w",
    ).pack(fill="x")
    tk.Label(
        hero_body,
        text="\u534a\u5c0f\u65f6\u7cfb\u7edf\u68c0\u6d4b\u5230\u9ad8\u523a\u6fc0\u6216\u4f4e\u610f\u4e49\u6d3b\u52a8\uff0c\u5efa\u8bae\u542f\u52a8 Cold Turkey 30 \u5206\u949f\u3002",
        bg=colors["panel"],
        fg=colors["muted"],
        font=subtitle_font,
        justify="left",
        wraplength=width - 90,
        anchor="w",
    ).pack(fill="x", pady=(6, 0))

    observations = request.get("observations", {})
    reasons = request.get("trigger_reasons", [])
    targets = display_targets(request.get("targets", []), config)

    stats = tk.Frame(shell, bg=colors["bg"])
    stats.pack(fill="x", pady=(14, 0))
    for index in range(3):
        stats.columnconfigure(index, weight=1, uniform="stat")

    def stat_card(parent, column: int, title: str, value: str, tone: str = "accent") -> None:
        fg = colors["danger"] if tone == "danger" else colors["accent"]
        bg = colors["danger_bg"] if tone == "danger" else colors["soft"]
        card = tk.Frame(
            parent,
            bg=bg,
            padx=12,
            pady=10,
            highlightthickness=2,
            highlightbackground=colors["accent_dark"],
        )
        card.grid(row=0, column=column, sticky="nsew", padx=(0 if column == 0 else 8, 0))
        tk.Label(
            card,
            text=title,
            bg=bg,
            fg=colors["muted"],
            font=base_font,
            anchor="w",
        ).pack(fill="x")
        tk.Label(
            card,
            text=value,
            bg=bg,
            fg=fg,
            font=metric_font,
            anchor="w",
        ).pack(fill="x", pady=(2, 0))

    stat_card(
        stats,
        0,
        "\u9ad8\u523a\u6fc0",
        f"{observations.get('high_stimulation_minutes', 0)} \u5206\u949f",
        "danger",
    )
    stat_card(
        stats,
        1,
        "60\u5206\u949f\u6709\u610f\u4e49\u6d3b\u52a8",
        f"{observations.get('meaningful_minutes_60m', 0)} \u5206\u949f",
    )
    stat_card(
        stats,
        2,
        "\u786e\u8ba4\u4f11\u606f",
        f"{observations.get('confirmed_rest_minutes', 0)} \u5206\u949f",
    )

    detail = tk.Frame(
        shell,
        bg=colors["panel"],
        padx=14,
        pady=12,
        highlightthickness=3,
        highlightbackground=colors["accent_dark"],
    )
    detail.pack(fill="both", expand=True, pady=(14, 0))
    tk.Label(
        detail,
        text="\u89e6\u53d1\u539f\u56e0",
        bg=colors["panel"],
        fg=colors["ink"],
        font=section_font,
        anchor="w",
    ).pack(fill="x")
    reason_text = ", ".join(str(item) for item in reasons) if reasons else "\u672a\u63d0\u4f9b"
    tk.Label(
        detail,
        text=reason_text,
        bg=colors["panel"],
        fg=colors["muted"],
        font=base_font,
        justify="left",
        wraplength=width - 80,
        anchor="w",
    ).pack(fill="x", pady=(5, 12))

    tk.Label(
        detail,
        text="\u5c06\u5904\u7406\u7684\u6a21\u5757",
        bg=colors["panel"],
        fg=colors["ink"],
        font=section_font,
        anchor="w",
    ).pack(fill="x")

    target_box = tk.Frame(detail, bg=colors["panel"])
    target_box.pack(fill="x", pady=(6, 0))
    shown_targets = [item for item in targets if item.get("enabled", True)]
    skipped_targets = [item for item in targets if not item.get("enabled", True)]
    if not shown_targets and not skipped_targets:
        tk.Label(
            target_box,
            text="\u6ca1\u6709\u53ef\u6267\u884c\u76ee\u6807",
            bg=colors["panel"],
            fg=colors["muted"],
            font=base_font,
            anchor="w",
        ).pack(fill="x")
    for item in shown_targets:
        row = tk.Frame(
            target_box,
            bg=colors["soft"],
            padx=10,
            pady=7,
            highlightthickness=2,
            highlightbackground=colors["accent_dark"],
        )
        row.pack(fill="x", pady=(0, 6))
        tk.Label(
            row,
            text=str(item.get("display_name") or item.get("name", "\u672a\u77e5\u6a21\u5757")),
            bg=colors["soft"],
            fg=colors["ink"],
            font=section_font,
        ).pack(side="left")
        tk.Label(
            row,
            text=f"{item.get('lock_minutes', 30)} \u5206\u949f",
            bg=colors["soft"],
            fg=colors["accent"],
            font=section_font,
        ).pack(side="right")
    for item in skipped_targets:
        row = tk.Frame(
            target_box,
            bg=colors["panel"],
            padx=10,
            pady=7,
            highlightthickness=2,
            highlightbackground=colors["line"],
        )
        row.pack(fill="x", pady=(0, 6))
        tk.Label(
            row,
            text=f"{item.get('display_name') or item.get('name', '\u672a\u77e5\u6a21\u5757')} \u5df2\u8df3\u8fc7",
            bg=colors["panel"],
            fg=colors["muted"],
            font=base_font,
        ).pack(side="left")
        tk.Label(
            row,
            text=str(item.get("reason", "exempt")),
            bg=colors["panel"],
            fg=colors["ok"],
            font=base_font,
        ).pack(side="right")

    footer = tk.Frame(root, bg=colors["bg"], padx=18, pady=12)
    footer.pack(fill="x", side="bottom")
    countdown_var = tk.StringVar()
    timeout = int(config.get("popup_timeout_seconds", 90))
    deadline = time.monotonic() + timeout
    tk.Label(
        footer,
        textvariable=countdown_var,
        bg=colors["bg"],
        fg=colors["muted"],
        font=base_font,
        anchor="w",
    ).pack(side="left")

    buttons = tk.Frame(footer, bg=colors["bg"])
    buttons.pack(side="right")

    def styled_button(parent, text: str, command, bg: str, fg: str = "#ffffff"):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg=fg,
            activebackground=bg,
            activeforeground=fg,
            relief="flat",
            borderwidth=0,
            highlightthickness=3,
            highlightbackground=colors["accent_dark"],
            padx=18,
            pady=10,
            font=button_font,
            cursor="hand2",
        )

    def choose(value: str) -> None:
        result["decision"] = value
        root.destroy()

    styled_button(
        buttons,
        "\u6682\u4e0d\u4ecb\u5165",
        lambda: choose("declined"),
        colors["sun"],
        colors["ink"],
    ).pack(side="left", padx=(0, 10))
    styled_button(
        buttons,
        "\u4ecb\u5165 30 \u5206\u949f",
        lambda: choose("accepted"),
        colors["mint"],
        colors["accent_dark"],
    ).pack(side="left")

    def tick() -> None:
        remaining = max(0, int(deadline - time.monotonic()))
        countdown_var.set(
            f"{remaining} \u79d2\u540e\u672a\u54cd\u5e94\u5c06\u6309\u6682\u4e0d\u4ecb\u5165\u5904\u7406\uff0c\u4f46\u4e0d\u7d2f\u8ba1\u62d2\u7edd"
        )
        if remaining <= 0:
            choose("ignored")
            return
        if root.winfo_exists():
            root.after(1000, tick)

    root.bind("<Escape>", lambda _event: choose("declined"))
    root.bind("<Return>", lambda _event: choose("accepted"))
    root.after(100, tick)
    root.lift()
    root.focus_force()
    root.mainloop()
    return result["decision"]


def _launch_intervention_ui(
    payload: dict[str, Any],
    *,
    wait: bool,
    on_wait: Any = None,
) -> dict[str, Any]:
    """Use an out-of-process Tk front end with a file-only reply channel."""
    if not UI_SCRIPT_PATH.exists():
        return {}
    token = uuid4().hex
    ui_root = ROOT / "data" / "ui"
    request_path = ui_root / f"{token}.request.json"
    response_path = ui_root / f"{token}.response.json"
    save_json(request_path, payload)
    command = [
        sys.executable,
        str(UI_SCRIPT_PATH),
        "--request",
        str(request_path),
        "--response",
        str(response_path),
    ]
    kind = str(payload.get("kind", "offer"))
    print(f"[{now_iso()}] UI launch: {kind} timeout={payload.get('timeout_seconds', '')}", flush=True)
    try:
        process = subprocess.Popen(
            command,
            cwd=str(ROOT),
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    except OSError as error:
        print(f"[{now_iso()}] UI launch failed: {kind} {type(error).__name__}", flush=True)
        request_path.unlink(missing_ok=True)
        return {}
    if not wait:
        # The child deletes its request after presenting a notice.  No core
        # thread or Tk object remains alive after this function returns.
        return {}

    timeout_seconds = max(1, int(payload.get("timeout_seconds", 90))) + 15
    deadline = time.monotonic() + timeout_seconds
    while process.poll() is None and time.monotonic() < deadline:
        if callable(on_wait):
            on_wait(
                "waiting_for_ui",
                busy_until=datetime.now().astimezone() + timedelta(seconds=timeout_seconds),
            )
        time.sleep(1)
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
    result = load_json(response_path, {})
    print(f"[{now_iso()}] UI finished: {kind} decision={result.get('decision', '') if isinstance(result, dict) else ''} exit={process.returncode}", flush=True)
    request_path.unlink(missing_ok=True)
    response_path.unlink(missing_ok=True)
    return result if isinstance(result, dict) else {}


def ask_user(
    request: dict[str, Any],
    config: dict[str, Any],
    on_wait: Any = None,
) -> str:
    """Ask in a disposable UI process; a Tcl crash becomes an ignored offer."""
    response = _launch_intervention_ui(
        {
            "kind": "offer",
            "title": "电脑介入提醒",
            "request": request,
            "allowed_blocks": config.get("allowed_blocks", {}),
            "timeout_seconds": int(config.get("popup_timeout_seconds", 90)),
        },
        wait=True,
        on_wait=on_wait,
    )
    decision = str(response.get("decision", "ignored"))
    return decision if decision in {"accepted", "declined", "ignored"} else "ignored"


def display_targets(targets: Any, config: dict[str, Any]) -> list[dict[str, Any]]:
    allowed_blocks = config.get("allowed_blocks", {})
    result: list[dict[str, Any]] = []
    for raw in targets if isinstance(targets, list) else []:
        if not isinstance(raw, dict):
            continue
        item = dict(raw)
        name = str(item.get("name", ""))
        cold_turkey_block = str(item.get("cold_turkey_block", ""))
        if name not in allowed_blocks and cold_turkey_block in allowed_blocks:
            name = cold_turkey_block
        if name not in allowed_blocks and looks_corrupt(name):
            for allowed_name in allowed_blocks:
                if allowed_name != "bilibili":
                    name = allowed_name
                    break
        item["name"] = name
        allowed = allowed_blocks.get(name, {})
        item["display_name"] = str(allowed.get("display_name", name))
        result.append(item)
    return result


_INSTANCE_MUTEX: Any = None


def acquire_single_instance() -> bool:
    """Prevent a watchdog recovery and a manual launch from owning one block twice."""
    global _INSTANCE_MUTEX
    if os.name != "nt":
        return True
    try:
        import ctypes

        ctypes.set_last_error(0)
        handle = ctypes.windll.kernel32.CreateMutexW(None, False, "Local\\ComputerInterventionAgent")
        if not handle:
            return False
        if ctypes.get_last_error() == 183:  # ERROR_ALREADY_EXISTS
            ctypes.windll.kernel32.CloseHandle(handle)
            return False
        _INSTANCE_MUTEX = handle
        return True
    except Exception:
        # The Scheduled Task still has IgnoreNew as a second duplicate guard.
        return True


def main() -> int:
    if not CONFIG_PATH.exists():
        save_json(CONFIG_PATH, DEFAULT_CONFIG)
        print(f"Created {CONFIG_PATH}. Add password or set NEXT_ACTION_WEB_PASSWORD.")
        return 2
    config = load_json(CONFIG_PATH, {})
    if bool(config.get("auth_required", True)) and not (os.environ.get("NEXT_ACTION_WEB_PASSWORD") or str(config.get("password", ""))):
        print("Set NEXT_ACTION_WEB_PASSWORD or add password to config.json.")
        return 2
    if not acquire_single_instance():
        print("Computer intervention agent already running.")
        return 0
    InterventionAgent().run_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
