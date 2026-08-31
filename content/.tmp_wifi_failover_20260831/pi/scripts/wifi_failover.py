from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

try:
    import fcntl
except ImportError:  # Windows-only unit tests
    fcntl = None


@dataclass(frozen=True)
class CommandResult:
    returncode: int
    stdout: str = ""
    stderr: str = ""


class SubprocessRunner:
    def run(self, args: list[str], timeout: int) -> CommandResult:
        try:
            completed = subprocess.run(
                args,
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout,
            )
            return CommandResult(
                completed.returncode,
                completed.stdout,
                completed.stderr,
            )
        except (OSError, subprocess.TimeoutExpired) as error:
            return CommandResult(124, "", f"{type(error).__name__}: {error}")


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def load_json(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return dict(default)
    return value if isinstance(value, dict) else dict(default)


def atomic_write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=path.name + ".",
        suffix=".tmp",
        dir=path.parent,
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, 0o600)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


class WifiFailover:
    def __init__(
        self,
        config: dict[str, Any],
        *,
        runner: SubprocessRunner | Any | None = None,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self.config = config
        self.runner = runner or SubprocessRunner()
        self.clock = clock
        self.primary = str(config["primary_profile"])
        self.fallback = str(config["fallback_profile"])
        self.state_path = Path(config["state_path"])
        self.events_path = Path(config["events_path"])
        self.lock_path = Path(config["lock_path"])

    def _default_state(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "primary_failures": 0,
            "fallback_failures": 0,
            "cooldown_until": None,
            "last_probe_at": None,
            "last_active_profile": None,
            "last_internet_ok": None,
            "last_action": "initialized",
            "last_switch_at": None,
        }

    def _active_profile(self) -> str | None:
        result = self.runner.run(
            [
                "/usr/bin/nmcli",
                "-t",
                "-f",
                "NAME,DEVICE",
                "connection",
                "show",
                "--active",
            ],
            timeout=10,
        )
        if result.returncode != 0:
            return None
        for raw in result.stdout.splitlines():
            name, _, device = raw.rpartition(":")
            if device == "wlan0":
                return name.replace("\\:", ":")
        return None

    def _has_default_route(self) -> bool:
        result = self.runner.run(
            [
                "/usr/sbin/ip",
                "route",
                "show",
                "default",
            ],
            timeout=5,
        )
        return result.returncode == 0 and bool(result.stdout.strip())

    def _probe_url(self, *, ipv6: bool, url: str) -> bool:
        result = self.runner.run(
            [
                "/usr/bin/curl",
                "-6" if ipv6 else "-4",
                "-L",
                "-sS",
                "-o",
                "/dev/null",
                "-w",
                "%{http_code}",
                "--max-time",
                "7",
                url,
            ],
            timeout=10,
        )
        if result.returncode != 0:
            return False
        code = result.stdout.strip()
        if not code.isdigit():
            return False
        status = int(code)
        return status == 204 if not ipv6 else 200 <= status < 400

    def _internet_health(self) -> dict[str, bool]:
        default_route = self._has_default_route()
        ipv4 = self._probe_url(
            ipv6=False,
            url=str(
                self.config.get(
                    "ipv4_probe_url",
                    "https://www.gstatic.com/generate_204",
                )
            ),
        )
        ipv6 = self._probe_url(
            ipv6=True,
            url=str(
                self.config.get(
                    "ipv6_probe_url",
                    "https://www.cloudflare.com/",
                )
            ),
        )
        return {
            "default_route": default_route,
            "ipv4_ok": ipv4,
            "ipv6_ok": ipv6,
            "internet_ok": default_route and (ipv4 or ipv6),
        }

    def _activate(self, profile: str) -> bool:
        result = self.runner.run(
            ["/usr/bin/nmcli", "connection", "up", profile],
            timeout=50,
        )
        return result.returncode == 0 and self._active_profile() == profile

    def _append_event(self, event: dict[str, Any]) -> None:
        self.events_path.parent.mkdir(parents=True, exist_ok=True)
        encoded = json.dumps(event, ensure_ascii=False, separators=(",", ":"))
        with self.events_path.open("a", encoding="utf-8") as handle:
            handle.write(encoded + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(self.events_path, 0o600)
        print(encoded, flush=True)

    def _cooldown_active(self, state: dict[str, Any], now: datetime) -> bool:
        raw = state.get("cooldown_until")
        if not isinstance(raw, str) or not raw:
            return False
        try:
            return datetime.fromisoformat(raw) > now
        except ValueError:
            return False

    def run_once(self) -> dict[str, Any]:
        now = self.clock()
        state = load_json(self.state_path, self._default_state())
        active = self._active_profile()
        health = self._internet_health()
        reachable = health["internet_ok"]
        event: dict[str, Any] = {
            "at": now.isoformat(timespec="seconds"),
            "active_profile": active,
            **health,
            "action": "none",
        }
        state["last_probe_at"] = event["at"]
        state["last_active_profile"] = active
        state["last_internet_ok"] = reachable

        if not bool(self.config.get("enabled", True)):
            event["action"] = "disabled"
        elif active == self.primary:
            state["fallback_failures"] = 0
            if reachable:
                state["primary_failures"] = 0
                event["action"] = "primary_healthy"
            else:
                state["primary_failures"] = int(
                    state.get("primary_failures", 0)
                ) + 1
                event["primary_failures"] = state["primary_failures"]
                threshold = int(self.config.get("primary_failure_threshold", 4))
                if state["primary_failures"] < threshold:
                    event["action"] = "primary_failure_accumulating"
                elif self._cooldown_active(state, now):
                    event["action"] = "primary_failure_cooldown"
                elif self._activate(self.fallback):
                    state["primary_failures"] = 0
                    state["last_switch_at"] = event["at"]
                    state["last_action"] = "switched_to_fallback"
                    event["action"] = "switched_to_fallback"
                else:
                    restored = self._activate(self.primary)
                    cooldown = int(self.config.get("failed_switch_cooldown_seconds", 600))
                    state["cooldown_until"] = (
                        now + timedelta(seconds=cooldown)
                    ).isoformat(timespec="seconds")
                    state["primary_failures"] = 0
                    state["last_action"] = "fallback_failed_primary_restored"
                    event["action"] = "fallback_failed_primary_restored"
                    event["primary_restored"] = restored
        elif active == self.fallback:
            state["primary_failures"] = 0
            if reachable:
                state["fallback_failures"] = 0
                event["action"] = "fallback_healthy_hold"
            else:
                state["fallback_failures"] = int(
                    state.get("fallback_failures", 0)
                ) + 1
                event["fallback_failures"] = state["fallback_failures"]
                threshold = int(self.config.get("fallback_failure_threshold", 2))
                if state["fallback_failures"] < threshold:
                    event["action"] = "fallback_failure_accumulating"
                elif self._activate(self.primary):
                    state["fallback_failures"] = 0
                    state["last_switch_at"] = event["at"]
                    state["last_action"] = "fallback_failed_switched_primary"
                    event["action"] = "fallback_failed_switched_primary"
                else:
                    restored = self._activate(self.fallback)
                    state["fallback_failures"] = 0
                    state["last_action"] = "both_profiles_failed"
                    event["action"] = "both_profiles_failed"
                    event["fallback_restored"] = restored
        elif active is None:
            if self._activate(self.fallback):
                state["last_switch_at"] = event["at"]
                state["last_action"] = "no_wifi_switched_fallback"
                event["action"] = "no_wifi_switched_fallback"
            elif self._activate(self.primary):
                state["last_switch_at"] = event["at"]
                state["last_action"] = "no_wifi_switched_primary"
                event["action"] = "no_wifi_switched_primary"
            else:
                state["last_action"] = "no_wifi_profiles_failed"
                event["action"] = "no_wifi_profiles_failed"
        else:
            state["primary_failures"] = 0
            state["fallback_failures"] = 0
            event["action"] = "manual_other_profile_preserved"

        state["last_action"] = event["action"]
        atomic_write_json(self.state_path, state)
        self._append_event(event)
        return event

    def force_fallback(self) -> dict[str, Any]:
        now = self.clock()
        state = load_json(self.state_path, self._default_state())
        before = self._active_profile()
        event: dict[str, Any] = {
            "at": now.isoformat(timespec="seconds"),
            "active_profile": before,
            "action": "manual_fallback_requested",
        }
        if self._activate(self.fallback):
            state["primary_failures"] = 0
            state["fallback_failures"] = 0
            state["last_switch_at"] = event["at"]
            state["last_active_profile"] = self.fallback
            state["last_action"] = "manual_switched_to_fallback"
            event["action"] = "manual_switched_to_fallback"
            event["success"] = True
        else:
            restored = self._activate(self.primary)
            state["last_active_profile"] = (
                self.primary if restored else self._active_profile()
            )
            state["last_action"] = "manual_fallback_failed"
            event["action"] = "manual_fallback_failed"
            event["success"] = False
            event["primary_restored"] = restored
        atomic_write_json(self.state_path, state)
        self._append_event(event)
        return event

    def _locked(self, operation: Callable[[], dict[str, Any]]) -> dict[str, Any] | None:
        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
        with self.lock_path.open("a+", encoding="utf-8") as lock:
            if fcntl is not None:
                try:
                    fcntl.flock(
                        lock.fileno(),
                        fcntl.LOCK_EX | fcntl.LOCK_NB,
                    )
                except BlockingIOError:
                    return None
            return operation()

    def locked_run(self) -> dict[str, Any] | None:
        return self._locked(self.run_once)

    def locked_force_fallback(self) -> dict[str, Any] | None:
        return self._locked(self.force_fallback)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("/home/conrad/workspace/activitywatch-advisor/config/wifi_failover.json"),
    )
    parser.add_argument("--force-fallback", action="store_true")
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    controller = WifiFailover(config)
    event = (
        controller.locked_force_fallback()
        if args.force_fallback
        else controller.locked_run()
    )
    if args.force_fallback and event and not event.get("success"):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
