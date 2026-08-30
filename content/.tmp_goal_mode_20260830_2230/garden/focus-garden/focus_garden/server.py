from __future__ import annotations

import json
import mimetypes
import os
import re
import subprocess
import threading
import time
from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlparse
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

from .bridge_monitor import evaluate_bridge_qualification
from .cold_turkey import ColdTurkeyController
from .control_metrics import ControlMetrics
from .database import GardenDatabase, utc_now
from .pi_sync import PiRewardSync

DEFAULT_FOCUS_MINUTES = (5, 20, 30, 40, 45, 60)
CONTINUOUS_FOCUS_MINUTES = {30, 40, 45, 60}
BRIDGE_STALE_SECONDS = 20 * 60
AGENT_STALE_SECONDS = 12 * 60
SHANGHAI = ZoneInfo("Asia/Shanghai")


def _bridge_heartbeat_metadata(body: dict[str, Any]) -> dict[str, Any]:
    """Keep the health endpoint narrow: never persist arbitrary phone payloads."""
    metadata: dict[str, Any] = {}
    string_limits = {
        "runtime_mode": 48,
        "app_version": 32,
        "service_instance_id": 80,
        "process_started_at": 48,
        "service_started_at": 48,
        "last_poll_at": 48,
        "last_poll_status": 80,
        "last_error": 240,
        "transport": 40,
        "lock_status": 48,
        "lock_request_id": 100,
        "lock_detail": 240,
        "lock_updated_at": 48,
        "last_execution_error": 240,
    }
    for key, limit in string_limits.items():
        value = body.get(key)
        if value is not None:
            metadata[key] = str(value)[:limit]
    for key in (
        "accessibility_enabled", "accessibility_connected", "fallback_active",
        "notification_access_enabled", "notification_listener_connected",
        "getaway_lock_active",
    ):
        if isinstance(body.get(key), bool):
            metadata[key] = body[key]
    for key in (
        "service_uptime_seconds", "restart_count", "connection_count",
        "lock_minutes", "lock_attempts",
    ):
        value = body.get(key)
        if isinstance(value, int) and not isinstance(value, bool):
            metadata[key] = max(0, min(value, 366 * 24 * 60 * 60))
    return metadata


class NextActionProxy:
    """A deliberately small same-Pi bridge to the existing Next Action UI.

    The garden never reads the Next Action password or its data directory.  It
    forwards the browser's existing signed cookie only to the loopback service.
    """

    _PATHS = {
        "active": "/api/next-action/active",
        "reports": "/api/half-hour/reports",
        "report": "/api/half-hour/report",
        "issues": "/api/issue-feedback/recent",
        "login": "/api/login",
        "generate": "/api/next-action",
        "issue_feedback": "/api/issue-feedback",
        "report_feedback": "/api/half-hour/feedback",
    }
    _INTERVENTION_PATHS = {
        "manual_focus": "/api/interventions/manual-focus",
        "manual_focus_release": "/api/interventions/manual-focus/release",
        "phone_pending": "/api/interventions/pending",
        "phone_decision": "/api/interventions/decision",
        "phone_event": "/api/interventions/event",
    }
    _TASK_SYNC_PATHS = {
        "state": "/api/task-sync/state",
        "mutations": "/api/task-sync/mutations",
        "primary": "/api/task-sync/primary",
    }
    _RECENT_CONTEXT_PATHS = {
        "list": "/api/recent-context",
        "relevant": "/api/recent-context/relevant",
        "create": "/api/recent-context",
        "update": "/api/recent-context/{id}/update",
        "archive": "/api/recent-context/{id}/archive",
        "unarchive": "/api/recent-context/{id}/unarchive",
        "pin": "/api/recent-context/{id}/pin",
        "unpin": "/api/recent-context/{id}/unpin",
        "confirm": "/api/recent-context/{id}/confirm",
    }
    _GOAL_AGENT_PATHS = {
        "state": "/api/goal-agent/state",
        "plan": "/api/goal-agent/plan",
        "feedback": "/api/goal-agent/feedback",
        "chat": "/api/goal-agent/chat",
        "review": "/api/goal-agent/review",
    }

    def __init__(self, settings: dict[str, Any]):
        config = settings.get("next_action", {})
        self.enabled = bool(config.get("enabled", True))
        self.base_url = str(config.get("base_url", "http://127.0.0.1:8767")).rstrip("/")
        self.timeout_seconds = int(config.get("timeout_seconds", 90))
        parsed = urlparse(self.base_url)
        if parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
            raise ValueError("Next Action must use a loopback HTTP endpoint")

    def request(self, target: str, method: str, *, body: dict[str, Any] | None = None,
                query: str = "", cookie: str = "", user_agent: str = "") -> tuple[int, Any, str]:
        if not self.enabled:
            raise ConnectionError("Next Action integration is disabled")
        if target not in self._PATHS:
            raise ValueError("unknown Next Action endpoint")
        return self._request_url(self.base_url + self._PATHS[target] + query, method, body, cookie, user_agent)

    def request_path(self, path: str, *, body: dict[str, Any], cookie: str = "",
                     user_agent: str = "") -> tuple[int, Any, str]:
        if not self.enabled:
            raise ConnectionError("Next Action integration is disabled")
        if not re.fullmatch(r"/api/next-action/[A-Za-z0-9_-]+/(response|outcome|clarify)", path):
            raise ValueError("invalid Next Action suggestion path")
        return self._request_url(self.base_url + path, "POST", body, cookie, user_agent)

    def intervention(self, target: str, method: str, *, body: dict[str, Any] | None = None,
                     query: str = "") -> tuple[int, Any, str]:
        """Call only fixed loopback intervention endpoints for the phone bridge."""
        if target not in self._INTERVENTION_PATHS:
            raise ValueError("unknown intervention endpoint")
        return self._request_url(
            self.base_url + self._INTERVENTION_PATHS[target] + query,
            method,
            body,
            "",
            "focus-garden-intervention-proxy/1",
            extra_headers={"X-Focus-Garden-Bridge": "1"},
        )

    def task_sync(self, target: str, method: str, *, body: dict[str, Any] | None = None,
                  timeout_seconds: int | None = None) -> tuple[int, Any, str]:
        if target not in self._TASK_SYNC_PATHS:
            raise ValueError("unknown task-sync endpoint")
        return self._request_url(
            self.base_url + self._TASK_SYNC_PATHS[target],
            method,
            body,
            "",
            "focus-garden-task-sync/1",
            extra_headers={"X-Focus-Garden-Bridge": "1"},
            timeout_seconds=timeout_seconds,
        )

    def recent_context(
        self,
        target: str,
        method: str,
        *,
        body: dict[str, Any] | None = None,
        note_id: str = "",
        query: str = "",
    ) -> tuple[int, Any, str]:
        """Forward only the fixed recent-context surface with the bridge header.

        The garden never holds recent-context data and never reads or writes
        state.json directly; it is a fixed whitelist proxy.
        """
        if target not in self._RECENT_CONTEXT_PATHS:
            raise ValueError("unknown recent-context endpoint")
        if note_id:
            if not re.fullmatch(r"[A-Za-z0-9_-]+", note_id):
                raise ValueError("invalid recent-context note id")
            path = self._RECENT_CONTEXT_PATHS[target].format(id=note_id)
        else:
            path = self._RECENT_CONTEXT_PATHS[target]
        if query:
            path = path + query
        return self._request_url(
            self.base_url + path,
            method,
            body,
            "",
            "focus-garden-recent-context/1",
            extra_headers={"X-Focus-Garden-Bridge": "1"},
        )

    def goal_agent(
        self,
        target: str,
        method: str,
        *,
        body: dict[str, Any] | None = None,
    ) -> tuple[int, Any, str]:
        """Forward only the Goal Agent's fixed, independently named API."""
        if target not in self._GOAL_AGENT_PATHS:
            raise ValueError("unknown Goal Agent endpoint")
        return self._request_url(
            self.base_url + self._GOAL_AGENT_PATHS[target],
            method,
            body,
            "",
            "focus-garden-goal-agent/1",
            extra_headers={"X-Focus-Garden-Bridge": "1"},
            timeout_seconds=90,
        )

    def goal_agent_scoped(
        self,
        path: str,
        *,
        body: dict[str, Any],
    ) -> tuple[int, Any, str]:
        allowed = (
            re.fullmatch(r"/api/goal-agent/plan-items/[A-Za-z0-9_-]{4,80}/accept-day", path)
            or re.fullmatch(r"/api/goal-agent/approvals/[A-Za-z0-9_-]{4,80}/decision", path)
            or re.fullmatch(r"/api/goal-agent/versions/\d+/rollback", path)
        )
        if not allowed:
            raise ValueError("invalid Goal Agent scoped path")
        return self._request_url(
            self.base_url + path,
            "POST",
            body,
            "",
            "focus-garden-goal-agent/1",
            extra_headers={"X-Focus-Garden-Bridge": "1"},
            timeout_seconds=90,
        )

    def _request_url(self, url: str, method: str, body: dict[str, Any] | None,
                     cookie: str, user_agent: str,
                     extra_headers: dict[str, str] | None = None,
                     timeout_seconds: int | None = None) -> tuple[int, Any, str]:
        raw_body = json.dumps(body or {}, ensure_ascii=False).encode("utf-8") if method == "POST" else None
        headers = {"Accept": "application/json"}
        if raw_body is not None:
            headers["Content-Type"] = "application/json; charset=utf-8"
        if cookie:
            headers["Cookie"] = cookie
        if user_agent:
            headers["User-Agent"] = user_agent
        if extra_headers:
            headers.update(extra_headers)
        request = Request(url, data=raw_body, headers=headers, method=method)
        try:
            with urlopen(request, timeout=timeout_seconds or self.timeout_seconds) as response:
                status, raw, set_cookie = response.status, response.read(), response.headers.get("Set-Cookie", "")
        except HTTPError as error:
            status, raw, set_cookie = error.code, error.read(), error.headers.get("Set-Cookie", "")
        except URLError as error:
            raise ConnectionError("Next Action 暂不可用，请检查 activitywatch-advisor-web.service") from error
        try:
            return status, json.loads(raw.decode("utf-8")), set_cookie
        except (UnicodeDecodeError, json.JSONDecodeError):
            return status, {"error": "Next Action returned an invalid response"}, set_cookie


class GardenService:
    def __init__(self, root: Path):
        self.root = root
        self.settings = json.loads((root / "config/settings.json").read_text(encoding="utf-8"))
        configured_minutes = self.settings.get("focus", {}).get("allowed_minutes", DEFAULT_FOCUS_MINUTES)
        self.allowed_focus_minutes = tuple(sorted({int(value) for value in configured_minutes}))
        if not self.allowed_focus_minutes or any(value < 1 or value > 180 for value in self.allowed_focus_minutes):
            raise ValueError("focus.allowed_minutes must contain values from 1 to 180")
        configured_always_blocks = self.settings.get("focus", {}).get(
            "always_windows_blocks", []
        )
        self.always_focus_blocks = tuple(
            dict.fromkeys(str(value).strip() for value in configured_always_blocks if str(value).strip())
        )
        self.catalog = json.loads((root / "config/plants.json").read_text(encoding="utf-8"))["plants"]
        self.profiles = json.loads((root / "config/focus_profiles.json").read_text(encoding="utf-8"))["profiles"]
        self.catalog_ids = {x["id"] for x in self.catalog}
        self.catalog_tiers = {x["id"]: x.get("tier", "basic") for x in self.catalog}
        self.profile_map = {x["id"]: x for x in self.profiles}
        database_override = os.environ.get("FOCUS_GARDEN_DB")
        self.db = GardenDatabase(Path(database_override) if database_override else root / self.settings["database"], self.catalog_tiers)
        self._last_daily_achievement_check = 0.0
        self.cold_turkey = ColdTurkeyController(self.settings)
        self.pi = PiRewardSync(self.settings)
        self.next_action = NextActionProxy(self.settings)
        operations = self.settings.get("operations", {})
        self.advisor_data_root = Path(operations.get(
            "advisor_data_root", "/home/conrad/workspace/activitywatch-advisor/data"
        ))
        self.obsidian_sync_root = Path(operations.get(
            "obsidian_sync_root", "/home/conrad/workspace/behavior-context-sync"
        ))
        self.archive_database_path = Path(operations.get(
            "archive_database_path", "/home/conrad/workspace/focus-garden-archive/focus-garden.sqlite3"
        ))
        self.control_metrics = ControlMetrics(
            self.db.path,
            self.advisor_data_root,
            self.obsidian_sync_root,
            root / "data" / "control-review.json",
        )

    def _task_by_id(self, effective: dict[str, Any], task_id: str) -> dict[str, Any] | None:
        for group in (effective.get("tasks") or {}).values():
            for task in group if isinstance(group, list) else []:
                if isinstance(task, dict) and task.get("task_id") == task_id:
                    return task
        return None

    def steam_gate_status(self, timeout_seconds: int | None = None) -> dict[str, Any]:
        status, effective, _ = self.next_action.task_sync(
            "state", "GET", timeout_seconds=timeout_seconds
        )
        if status != HTTPStatus.OK or not isinstance(effective, dict):
            raise ConnectionError("Steam unlock gate is unavailable")
        gate = effective.get("steam_unlock_gate")
        if not isinstance(gate, dict):
            raise ConnectionError("Steam unlock gate returned invalid data")
        day_key = datetime.now(SHANGHAI).date().isoformat()
        required = 5
        awarded = 0
        for task in effective.get("completed_today") or []:
            if not isinstance(task, dict) or task.get("occurrence_date") != day_key:
                continue
            try:
                awarded += max(0, int(task.get("tomatoes_total", 0) or 0))
            except (TypeError, ValueError):
                continue
        completed = min(awarded, required)
        primary_completed = bool(gate.get("primary_task_completed"))
        return {
            **gate,
            "date": day_key,
            "completed_tomatoes": completed,
            "required_completed_tomatoes": required,
            "tomato_requirement_met": awarded >= required,
            "primary_task_completed": primary_completed,
            "eligible": awarded >= required and primary_completed,
            "tomato_count_source": "completed_tasks_planned_tomatoes",
        }

    def steam_unlock_indicator(self) -> dict[str, Any]:
        """Return a task-text-free explanation for the read-only health panel."""
        try:
            gate = self.steam_gate_status(timeout_seconds=3)
            completed = max(0, int(gate.get("completed_tomatoes", 0) or 0))
            required = max(1, int(gate.get("required_completed_tomatoes", 5) or 5))
            tomato_met = bool(gate.get("tomato_requirement_met"))
            primary_set = bool(gate.get("primary_task_id"))
            primary_completed = bool(gate.get("primary_task_completed"))
            eligible = bool(gate.get("eligible"))
            reasons: list[str] = []
            if not tomato_met:
                reasons.append(f"还差 {max(0, required - completed)} 个完成番茄")
            if not primary_set:
                reasons.append("今天尚未设置主要任务")
            elif not primary_completed:
                reasons.append("今天的主要任务尚未完成")
            return {
                "available": True,
                "date": gate.get("date"),
                "completed_tomatoes": completed,
                "required_completed_tomatoes": required,
                "tomato_requirement_met": tomato_met,
                "primary_task_set": primary_set,
                "primary_task_completed": primary_completed,
                "eligible": eligible,
                "blocking_reasons": reasons,
            }
        except (ConnectionError, OSError, TypeError, ValueError):
            return {
                "available": False,
                "completed_tomatoes": None,
                "required_completed_tomatoes": 5,
                "tomato_requirement_met": False,
                "primary_task_set": None,
                "primary_task_completed": False,
                "eligible": False,
                "blocking_reasons": ["任务指标暂时不可用；为安全起见继续保持 Steam 锁定"],
            }

    def flush_task_focus_settlements(self) -> int:
        """Queue earned, task-linked tomatoes for the desktop Markdown writer.

        A settlement uses an absolute target count rather than a delta.  Thus
        retries after a network/process interruption are safe: the Obsidian
        plugin can set `max(current, target)` without double-counting.
        """
        pending = self.db.pending_task_focus_settlements()
        if not pending:
            return 0
        try:
            status, effective, _ = self.next_action.task_sync("state", "GET")
            if status != HTTPStatus.OK or not isinstance(effective, dict):
                return 0
        except (ConnectionError, ValueError):
            return 0
        queued = 0
        for settlement in pending:
            task = self._task_by_id(effective, str(settlement["task_id"]))
            if not task:
                self.db.mark_task_focus_settlement(
                    settlement["session_id"], "skipped", detail="task no longer exists in the effective Obsidian view"
                )
                continue
            total = task.get("tomatoes_total")
            if not isinstance(total, int) or total <= 0:
                self.db.mark_task_focus_settlement(
                    settlement["session_id"], "skipped", detail="task has no 🍅 estimate; focus remains in history only"
                )
                continue
            current = task.get("tomatoes_completed")
            current = current if isinstance(current, int) else 0
            target = min(total, current + int(settlement["tomatoes"]))
            if target <= current:
                self.db.mark_task_focus_settlement(
                    settlement["session_id"], "skipped", target_completed=current,
                    detail="task tomato estimate is already complete",
                )
                continue
            try:
                status, result, _ = self.next_action.task_sync("mutations", "POST", body={
                    "operation": "advance_tomatoes",
                    "task_id": settlement["task_id"],
                    "target_completed": target,
                    "settlement_id": settlement["session_id"],
                })
                if status != HTTPStatus.OK or not isinstance(result, dict):
                    break
                mutation = result.get("mutation", {})
                self.db.mark_task_focus_settlement(
                    settlement["session_id"], "queued", target_completed=target,
                    mutation_id=str(mutation.get("mutation_id", "")),
                )
                effective = result.get("effective", effective) if isinstance(result, dict) else effective
                queued += 1
            except (ConnectionError, ValueError):
                break
        return queued

    def reconcile_focus(self) -> int:
        session = self.db.focus()
        if not session:
            self.flush_task_focus_settlements()
            return 0
        if session.get("paused"):
            resume_at = session.get("resume_at")
            if resume_at and datetime.fromisoformat(resume_at) <= datetime.now(timezone.utc):
                # A confirmed pause ends even when neither the website nor
                # Obsidian is open.  The reconciler is the authoritative clock.
                self.resume_focus()
            return 0
        if datetime.fromisoformat(session["ends_at"]) <= datetime.now(timezone.utc):
            # Do not award or close a Windows focus session before a matching
            # release has been queued.  The release request is idempotent by
            # lease ID, so a transient Pi/agent failure is safe to retry.
            try:
                self.release_focus_lease(session)
            except Exception:
                # Keep the original execute receipt intact: it contains the
                # lease ID needed by the next retry.
                return 0
            rewards = self.db.complete_focus(session["id"])
            self.db.advance_focus_plan_for_session(session["id"], utc_now())
            self.flush_task_focus_settlements()
            return rewards
        return 0

    def reconcile_daily_achievements(self, *, force: bool = False) -> int:
        """Observe today's task plan and settle completed past days once."""
        now_tick = time.monotonic()
        if not force and now_tick - self._last_daily_achievement_check < 60:
            return 0
        self._last_daily_achievement_check = now_tick
        try:
            status, effective, _ = self.next_action.task_sync("state", "GET")
        except (ConnectionError, ValueError):
            return 0
        if status != HTTPStatus.OK or not isinstance(effective, dict):
            return 0
        scorecards = effective.get("daily_scorecards")
        if not isinstance(scorecards, list):
            return 0
        local_now = datetime.now(SHANGHAI)
        if (local_now.hour, local_now.minute) < (4, 10):
            return 0
        today = local_now.date().isoformat()
        return self.db.record_daily_scorecards(scorecards, today)

    def run_due_focus_plan(self) -> None:
        if self.db.focus():
            return
        plan = self.db.next_due_focus_plan(utc_now())
        if not plan:
            return
        try:
            session = self.start_focus(plan["profile_id"], int(plan["focus_minutes"]), plan["targets"])
            if session["status"] != "running":
                raise RuntimeError("unable to start the planned focus session")
            self.db.mark_focus_plan_started(plan["id"], session["id"])
        except Exception:
            # Do not silently retry a plan that could not be dispatched; the
            # retained plan state makes the problem observable in the UI.
            self.db.fail_focus_plan(plan["id"])

    def create_schedule(self, profile_id: str, duration: int, targets: list[str], starts_at: str) -> dict[str, Any]:
        start = datetime.fromisoformat(starts_at)
        if start.tzinfo is None:
            raise ValueError("scheduled time must include a timezone")
        if start <= datetime.now(start.tzinfo):
            raise ValueError("scheduled time must be in the future")
        self._validate_focus_request(profile_id, duration, targets)
        return self.db.create_focus_plan("scheduled", profile_id, duration, 0, 1, targets,
                                         start.astimezone(timezone.utc).isoformat(timespec="seconds"))

    def create_continuous_focus(self, profile_id: str, focus_minutes: int, rest_minutes: int,
                                rounds: int, targets: list[str]) -> dict[str, Any]:
        self._validate_focus_request(profile_id, focus_minutes, targets)
        if focus_minutes not in CONTINUOUS_FOCUS_MINUTES:
            raise ValueError("continuous focus must use 30, 40, 45, or 60 minutes")
        if not 1 <= rest_minutes <= 30 or not 2 <= rounds <= 8:
            raise ValueError("rest must be 1-30 minutes and rounds must be 2-8")
        return self.db.create_focus_plan("cycle", profile_id, focus_minutes, rest_minutes, rounds, targets, utc_now())

    def _validate_focus_request(self, profile_id: str, duration: int, targets: list[str]) -> None:
        if profile_id not in self.profile_map:
            raise ValueError("unknown focus profile")
        if duration not in self.allowed_focus_minutes:
            published = ", ".join(str(value) for value in self.allowed_focus_minutes)
            raise ValueError(f"focus duration must be one of: {published} minutes")
        if not set(targets) <= {"windows", "phone"}:
            raise ValueError("targets may only include computer and phone")

    def _focus_blocks(self, profile_id: str, requested_targets: set[str]) -> list[str]:
        blocks: list[str] = []
        if "windows" in requested_targets:
            blocks.extend(str(value) for value in self.profile_map[profile_id].get("blocks", []))
        blocks.extend(self.always_focus_blocks)
        return list(dict.fromkeys(block for block in blocks if block))

    def start_focus(self, profile_id: str, duration: int, targets: list[str] | None = None,
                    *, task_id: str | None = None, task_title: str | None = None,
                    source: str = "garden") -> dict[str, Any]:
        requested_targets = set(["windows", "phone"] if targets is None else targets)
        self._validate_focus_request(profile_id, duration, sorted(requested_targets))
        blocks = self._focus_blocks(profile_id, requested_targets)
        selected_targets = set(requested_targets)
        if blocks:
            selected_targets.add("windows")
        if task_id and not re.fullmatch(r"\^[A-Za-z0-9-]{4,32}", task_id):
            raise ValueError("task_id must be an Obsidian block ID")
        if source not in {"garden", "obsidian"}:
            raise ValueError("invalid focus source")
        existing = self.db.focus()
        if existing:
            return existing
        now = datetime.now(timezone.utc)
        session = self.db.create_focus(profile_id, duration, now.isoformat(timespec="seconds"),
                                       (now + timedelta(minutes=duration)).isoformat(timespec="seconds"),
                                       task_id=task_id, task_title=(task_title or "")[:500] or None, source=source,
                                       targets=sorted(selected_targets), blocks=blocks)
        try:
            if not selected_targets:
                self.db.set_focus_execution(session["id"], [{"status": "not_requested", "targets": []}], failed=False)
            elif os.environ.get("FOCUS_GARDEN_DISPATCH_INTERVENTIONS") == "1":
                status, payload, _ = self.next_action.intervention(
                    "manual_focus",
                    "POST",
                    body={"duration": duration, "targets": sorted(selected_targets),
                          "blocks": blocks,
                          "focus_deadline_at": session["ends_at"],
                          "allowed_phone_minutes": list(self.allowed_focus_minutes)},
                )
                if status != HTTPStatus.CREATED:
                    raise RuntimeError(str(payload.get("error", "intervention dispatcher rejected request")))
                self.db.set_focus_execution(
                    session["id"],
                    [{"status": "queued", "targets": sorted(selected_targets), "dispatcher": payload}],
                    failed=False,
                )
            else:
                # Local safe development remains deterministic and does not
                # require a reachable Pi Advisor service.
                executions = self.cold_turkey.start(blocks, duration)
                failed = any(x["status"] == "failed" for x in executions)
                self.db.set_focus_execution(session["id"], executions, failed=failed)
                if failed:
                    raise RuntimeError("Cold Turkey 未能启用全部封锁")
        except Exception:
            self.db.set_focus_execution(session["id"], [], failed=True)
            raise
        return self.db.focus(session["id"])  # type: ignore[return-value]

    def release_focus_lease(self, session: dict[str, Any]) -> None:
        """Queue independent, idempotent releases for each requested device."""
        selected_targets = set(session.get("targets", [])) & {"windows", "phone"}
        if not selected_targets:
            return
        blocks = [str(block) for block in session.get("blocks", [])]
        if "windows" in selected_targets and not blocks:
            return
        if os.environ.get("FOCUS_GARDEN_DISPATCH_INTERVENTIONS") == "1":
            lease_id = self._focus_lease_id(session)
            if not lease_id:
                # Pre-lease historical sessions cannot prove ownership of a
                # future Cold Turkey lock.  Let the Agent's expiry recovery
                # handle any old lock instead of emitting a generic stop.
                return
            releases = []
            for target in sorted(selected_targets):
                status, payload, _ = self.next_action.intervention(
                    "manual_focus_release", "POST",
                    body={"blocks": blocks if target == "windows" else [],
                          "lease_id": lease_id, "session_id": str(session.get("id", "")),
                          "targets": [target]},
                )
                if status != HTTPStatus.CREATED:
                    raise RuntimeError(str(payload.get("error", f"{target} intervention release rejected")))
                releases.append({"status": "release_queued", "targets": [target], "dispatcher": payload})
            self.db.set_focus_execution(session["id"], releases, failed=False)
        elif "windows" in selected_targets:
            self.cold_turkey.stop(blocks)

    @staticmethod
    def _focus_lease_id(session: dict[str, Any]) -> str:
        executions = session.get("cold_turkey", [])
        if not isinstance(executions, list):
            return ""
        for execution in reversed(executions):
            if not isinstance(execution, dict):
                continue
            dispatcher = execution.get("dispatcher", {})
            request = dispatcher.get("request", {}) if isinstance(dispatcher, dict) else {}
            if not isinstance(request, dict) or request.get("mode") != "execute":
                continue
            lease_id = str(request.get("lease_id") or request.get("request_id") or "").strip()
            if lease_id:
                return lease_id
        return ""

    def pause_focus(self, pause_minutes: int) -> dict[str, Any]:
        session = self.db.focus()
        if not session:
            raise ValueError("no running focus session")
        paused = self.db.pause_focus(session["id"], pause_minutes)
        try:
            self.release_focus_lease(paused)
        except Exception:
            # The pause remains true: completing it must not award credit while
            # the agent release is unconfirmed, and the status is visible.
            self.db.set_focus_execution(paused["id"], [{"status": "release_failed"}], failed=False)
        return self.db.focus(paused["id"])  # type: ignore[return-value]

    def resume_focus(self) -> dict[str, Any]:
        session = self.db.focus()
        if not session or not session.get("paused"):
            raise ValueError("focus session is not paused")
        resumed = self.db.resume_focus(session["id"])
        targets = [str(target) for target in session.get("targets", [])]
        if targets and os.environ.get("FOCUS_GARDEN_DISPATCH_INTERVENTIONS") == "1":
            status, payload, _ = self.next_action.intervention(
                "manual_focus", "POST", body={"duration": int(session["duration_minutes"]), "targets": targets,
                                                 "blocks": session.get("blocks", []),
                                                 "focus_deadline_at": resumed["ends_at"],
                                                 "allowed_phone_minutes": list(self.allowed_focus_minutes)}
            )
            if status != HTTPStatus.CREATED:
                raise RuntimeError(str(payload.get("error", "intervention dispatcher rejected resume")))
            self.db.set_focus_execution(session["id"], [{"status": "resume_queued", "targets": targets, "dispatcher": payload}], failed=False)
        elif targets:
            self.cold_turkey.start([str(block) for block in session.get("blocks", [])], int(session["duration_minutes"]))
        return resumed

    def sync_rewards(self) -> dict[str, Any]:
        events = self.pi.fetch()
        inserted = self.db.import_rewards(events)
        return {"seen": len(events), "inserted": inserted, "pending": len(self.db.rewards("pending"))}

    @staticmethod
    def _read_json(path: Path) -> dict[str, Any]:
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
            return value if isinstance(value, dict) else {}
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            return {}

    @staticmethod
    def _file_freshness(path: Path | None, now: datetime) -> dict[str, Any]:
        if path is None or not path.is_file():
            return {"state": "missing", "updated_at": None, "age_seconds": None}
        modified = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)
        return {
            "state": "ok",
            "updated_at": modified.isoformat(timespec="seconds"),
            "age_seconds": max(0, int((now - modified).total_seconds())),
        }

    @staticmethod
    def _service_state(name: str) -> dict[str, str]:
        try:
            result = subprocess.run(
                ["systemctl", "is-active", name],
                capture_output=True,
                text=True,
                timeout=3,
                check=False,
            )
            return {"name": name, "state": result.stdout.strip() or "unknown"}
        except (OSError, subprocess.SubprocessError):
            return {"name": name, "state": "unknown"}

    def _focus_bridge_status(self, now: datetime) -> dict[str, Any]:
        health = self.db.bridge_health("android-main")
        if not health:
            return {
                "state": "never", "last_seen_at": None, "age_seconds": None,
                "qualification": evaluate_bridge_qualification(None, [], now),
            }
        try:
            seen = datetime.fromisoformat(health["last_seen_at"])
            age = max(0, int((now - seen).total_seconds()))
        except (KeyError, TypeError, ValueError):
            age = None
        history = self.db.bridge_heartbeat_history("android-main")
        return {
            **health,
            "state": "online" if age is not None and age <= BRIDGE_STALE_SECONDS else "stale",
            "age_seconds": age,
            "qualification": evaluate_bridge_qualification(health, history, now),
        }

    def system_status(self) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        task_state = self._read_json(self.advisor_data_root / "task_sync" / "state.json")
        agent_state = self._read_json(
            self.advisor_data_root / "computer_interventions" / "state" / "windows-main.json"
        )
        agent_seen = agent_state.get("last_heartbeat_at") or agent_state.get("last_seen_at")
        try:
            agent_age = max(0, int((now - datetime.fromisoformat(str(agent_seen))).total_seconds()))
        except (TypeError, ValueError):
            agent_age = None
        latest_report = max(
            (path for path in (self.advisor_data_root / "ai_reports").glob("*/*.json") if path.is_file()),
            key=lambda path: path.stat().st_mtime,
            default=None,
        )
        raw_locks = agent_state.get("active_locks")
        if isinstance(raw_locks, dict):
            lease_blocks = sorted(str(key) for key in raw_locks)
        elif isinstance(raw_locks, list):
            lease_blocks = sorted(str(item) for item in raw_locks if isinstance(item, (str, int)))
        else:
            lease_blocks = []
        mutations = task_state.get("mutations")
        pending_mutation_count = len(mutations) if isinstance(mutations, list) else 0
        return {
            "generated_at": now.isoformat(timespec="seconds"),
            "services": [self._service_state(name) for name in (
                "focus-garden.service", "focus-garden-backup.timer", "activitywatch-advisor-web.service",
                "activitywatch-advisor.timer", "syncthing@conrad.service",
            )],
            "tasks": {
                "pending_mutation_count": pending_mutation_count,
                "revision": task_state.get("revision"),
                "queue": self._file_freshness(self.advisor_data_root / "task_sync" / "state.json", now),
                "snapshot": self._file_freshness(self.obsidian_sync_root / "context_snapshot.json", now),
                "sync_heartbeat": self._file_freshness(self.obsidian_sync_root / "sync_heartbeat.json", now),
            },
            "bridges": {
                "windows": {**agent_state, "state": "online" if agent_age is not None and agent_age <= AGENT_STALE_SECONDS else "stale" if agent_age is not None else "never", "age_seconds": agent_age,
                            "lease_state": "active" if lease_blocks else "idle",
                            "lease_blocks": lease_blocks},
                "android": self._focus_bridge_status(now),
            },
            "data": {
                "context_cache": self._file_freshness(self.advisor_data_root / "context_cache" / "current.json", now),
                "latest_report": self._file_freshness(latest_report, now),
                "archive_backup": self._file_freshness(self.archive_database_path, now),
            },
            "steam_unlock": self.steam_unlock_indicator(),
            "control": self.control_metrics.load_snapshot(),
            "privacy": {"access": "tailnet_only", "writer": "Pi SQLite only"},
        }

    @staticmethod
    def _time_in_range(value: Any, start: datetime, end: datetime) -> bool:
        try:
            instant = datetime.fromisoformat(str(value))
            if instant.tzinfo is None:
                instant = instant.replace(tzinfo=SHANGHAI)
            return start <= instant.astimezone(SHANGHAI) < end
        except (TypeError, ValueError):
            return False

    def _next_action_usage(self, start: datetime, end: datetime) -> dict[str, int]:
        root = self.advisor_data_root / "next_action"
        asked = 0
        accepted_ids: set[str] = set()
        accepted_in_period: set[str] = set()
        for path in (root / "suggestions").glob("*/*.json"):
            record = self._read_json(path)
            if self._time_in_range(record.get("created_at"), start, end):
                asked += 1
        for path in (root / "responses").glob("*/*.json"):
            record = self._read_json(path)
            suggestion_id = str(record.get("suggestion_id") or "").strip()
            if suggestion_id and record.get("result") == "accepted":
                accepted_ids.add(suggestion_id)
                if self._time_in_range(record.get("received_at"), start, end):
                    accepted_in_period.add(suggestion_id)
        completed_ids: set[str] = set()
        for path in (root / "outcomes").glob("*/*.json"):
            record = self._read_json(path)
            suggestion_id = str(record.get("suggestion_id") or "").strip()
            if (
                suggestion_id in accepted_ids
                and record.get("result") == "completed"
                and self._time_in_range(record.get("received_at"), start, end)
            ):
                completed_ids.add(suggestion_id)
        return {
            "asked_suggestions": asked,
            "accepted_suggestions": len(accepted_in_period),
            "completed_suggestions": len(completed_ids),
        }

    def _usage_frequency_period(self, start: datetime, end: datetime) -> dict[str, int]:
        focus = self.db.completed_focus_summary(start, end)
        return {"focus_minutes": focus["focus_minutes"], **self._next_action_usage(start, end)}

    def usage_frequency(self, now: datetime | None = None) -> dict[str, Any]:
        current = (now or datetime.now(SHANGHAI)).astimezone(SHANGHAI)
        today_start = current.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=today_start.weekday())
        days = []
        for offset in range(3):
            start = today_start - timedelta(days=offset)
            end = current if offset == 0 else start + timedelta(days=1)
            days.append({
                "label": start.strftime("%m/%d"),
                "current": self._usage_frequency_period(start, end),
                "last_week_same_period": self._usage_frequency_period(
                    start - timedelta(days=7), end - timedelta(days=7)
                ),
            })
        return {
            "days": days,
            "this_week": {
                "current": self._usage_frequency_period(week_start, current),
                "last_week_same_period": self._usage_frequency_period(
                    week_start - timedelta(days=7), current - timedelta(days=7)
                ),
            },
        }

    def bootstrap(self) -> dict[str, Any]:
        self.reconcile_focus()
        self.reconcile_daily_achievements()
        bridge = self._focus_bridge_status(datetime.now(timezone.utc))
        return {"catalog": self.catalog, "profiles": self.profiles, "garden": self.db.garden(),
                "pending_rewards": self.db.rewards("pending"), "reward_history": self.db.rewards(),
                "focus": self.db.focus(), "focus_history": self.db.focus_history(), "focus_plans": self.db.focus_plans(),
                "focus_bridge": bridge,
                "daily_achievements": self.db.daily_achievements(),
                "usage_frequency": self.usage_frequency(),
                "stats": self.db.stats(), "settings": {
                    "early_sleep_cutoff": self.settings["pi_sync"]["early_sleep_cutoff"],
                    "cold_turkey_mode": "dry_run" if os.environ.get("FOCUS_GARDEN_DRY_RUN") == "1"
                        else self.settings["cold_turkey"]["mode"],
                    "intervention_dispatch": os.environ.get("FOCUS_GARDEN_DISPATCH_INTERVENTIONS") == "1",
                    "allowed_focus_minutes": list(self.allowed_focus_minutes),
                }}


class GardenHandler(BaseHTTPRequestHandler):
    server_version = "MyFocusGarden/0.1"

    @property
    def service(self) -> GardenService:
        return self.server.service  # type: ignore[attr-defined]

    def log_message(self, fmt: str, *args: Any) -> None:
        print(f"[{self.log_date_time_string()}] {fmt % args}")

    def _json(self, data: Any, status: int = 200, set_cookie: str = "") -> None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        if set_cookie:
            self.send_header("Set-Cookie", set_cookie)
        self.end_headers()
        self.wfile.write(body)

    def _body(self) -> dict[str, Any]:
        length = min(int(self.headers.get("Content-Length", "0")), 65536)
        return json.loads(self.rfile.read(length) or b"{}")

    def _error(self, exc: Exception) -> None:
        status = (
            HTTPStatus.SERVICE_UNAVAILABLE if isinstance(exc, ConnectionError)
            else HTTPStatus.NOT_FOUND if isinstance(exc, KeyError)
            else HTTPStatus.BAD_REQUEST
        )
        self._json({"error": str(exc).strip("'")}, status)

    def _next_action(self, target: str, method: str, body: dict[str, Any] | None = None,
                     query: str = "") -> None:
        try:
            status, data, set_cookie = self.service.next_action.request(
                target, method, body=body, query=query,
                cookie=self.headers.get("Cookie", ""), user_agent=self.headers.get("User-Agent", ""),
            )
            self._json(data, status, set_cookie)
        except Exception as exc:
            self._error(exc)

    def _intervention(self, target: str, method: str, body: dict[str, Any] | None = None,
                      query: str = "") -> None:
        try:
            status, data, _ = self.service.next_action.intervention(
                target, method, body=body, query=query
            )
            self._json(data, status)
        except Exception as exc:
            self._error(exc)

    def _task_sync(self, target: str, method: str, body: dict[str, Any] | None = None) -> None:
        try:
            status, data, _ = self.service.next_action.task_sync(target, method, body=body)
            self._json(data, status)
        except Exception as exc:
            self._error(exc)

    def _recent_context(
        self,
        target: str,
        method: str,
        body: dict[str, Any] | None = None,
        note_id: str = "",
        query: str = "",
    ) -> None:
        try:
            status, data, _ = self.service.next_action.recent_context(
                target, method, body=body, note_id=note_id, query=query
            )
            self._json(data, status)
        except Exception as exc:
            self._error(exc)

    def _goal_agent(self, target: str, method: str, body: dict[str, Any] | None = None) -> None:
        try:
            status, data, _ = self.service.next_action.goal_agent(
                target, method, body=body
            )
            self._json(data, status)
        except Exception as exc:
            self._error(exc)

    def _goal_agent_scoped(self, path: str, body: dict[str, Any]) -> None:
        try:
            status, data, _ = self.service.next_action.goal_agent_scoped(
                path, body=body
            )
            self._json(data, status)
        except Exception as exc:
            self._error(exc)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/health":
            return self._json({"status": "ok"})
        if parsed.path == "/api/system-status":
            return self._json(self.service.system_status())
        if parsed.path == "/api/bootstrap":
            return self._json(self.service.bootstrap())
        if parsed.path == "/api/garden":
            return self._json(self.service.db.garden())
        if parsed.path == "/api/focus-bridge/pending":
            # The Android bridge is intentionally restricted to its one fixed
            # device identity; this is not a generic remote command channel.
            query = "?device_id=android-main"
            return self._intervention("phone_pending", "GET", query=query)
        if parsed.path == "/api/tasks":
            return self._task_sync("state", "GET")
        if parsed.path == "/api/goal-agent/state":
            return self._goal_agent("state", "GET")
        if parsed.path == "/api/goal-agent/plan":
            return self._goal_agent("plan", "GET")
        if parsed.path == "/api/steam-gate/status":
            if self.headers.get("X-Computer-Intervention-Agent") != "1":
                return self._json({"error": "computer agent required"}, HTTPStatus.UNAUTHORIZED)
            try:
                return self._json(self.service.steam_gate_status())
            except Exception as exc:
                return self._error(exc)
        if parsed.path == "/api/recent-context":
            query = ("?" + parsed.query) if parsed.query else ""
            return self._recent_context("list", "GET", query=query)
        if parsed.path == "/api/recent-context/relevant":
            return self._recent_context("relevant", "GET")
        next_action_get = {
            "/api/next-action/active": "active",
            "/api/next-action/reports": "reports",
            "/api/next-action/report": "report",
            "/api/next-action/issues": "issues",
        }
        if parsed.path in next_action_get:
            query = ("?" + parsed.query) if parsed.path == "/api/next-action/report" and parsed.query else ""
            return self._next_action(next_action_get[parsed.path], "GET", query=query)
        if parsed.path.startswith("/api/"):
            return self._json({"error": "not found"}, 404)
        self._static(parsed.path)

    def do_POST(self) -> None:
        if self.headers.get("Content-Type", "").split(";")[0] != "application/json":
            return self._json({"error": "application/json required"}, 415)
        try:
            body = self._body()
            if self.path == "/api/next-action/login":
                return self._next_action("login", "POST", body)
            if self.path == "/api/tasks/mutations":
                return self._task_sync("mutations", "POST", body)
            if self.path == "/api/tasks/primary":
                return self._task_sync("primary", "POST", body)
            if self.path == "/api/goal-agent/feedback":
                return self._goal_agent("feedback", "POST", body)
            if self.path == "/api/goal-agent/chat":
                return self._goal_agent("chat", "POST", body)
            if self.path == "/api/goal-agent/review":
                return self._goal_agent("review", "POST", body)
            if (
                re.fullmatch(r"/api/goal-agent/plan-items/[A-Za-z0-9_-]{4,80}/accept-day", self.path)
                or re.fullmatch(r"/api/goal-agent/approvals/[A-Za-z0-9_-]{4,80}/decision", self.path)
                or re.fullmatch(r"/api/goal-agent/versions/\d+/rollback", self.path)
            ):
                return self._goal_agent_scoped(self.path, body)
            if self.path == "/api/steam-night/closed":
                if self.headers.get("X-Computer-Intervention-Agent") != "1":
                    return self._json({"error": "computer agent required"}, HTTPStatus.UNAUTHORIZED)
                return self._json(
                    self.service.db.record_steam_night_closed(
                        str(body.get("event_id", "")),
                        str(body.get("occurred_at", "")),
                    ),
                    HTTPStatus.CREATED,
                )
            if self.path == "/api/recent-context":
                return self._recent_context("create", "POST", body)
            recent_match = re.fullmatch(
                r"/api/recent-context/([A-Za-z0-9_-]+)/(update|archive|unarchive|pin|unpin|confirm)",
                self.path,
            )
            if recent_match:
                note_id, action = recent_match.group(1), recent_match.group(2)
                return self._recent_context(action, "POST", body, note_id=note_id)
            if self.path == "/api/next-action/generate":
                return self._next_action("generate", "POST", body)
            if self.path == "/api/next-action/issue-feedback":
                return self._next_action("issue_feedback", "POST", body)
            if self.path == "/api/next-action/report-feedback":
                return self._next_action("report_feedback", "POST", body)
            clarify_match = re.fullmatch(r"/api/next-action/suggestion/([^/]+)/clarify", self.path)
            if clarify_match:
                return self._next_action_path(f"/api/next-action/{clarify_match.group(1)}/clarify", body)
            response_match = re.fullmatch(r"/api/next-action/suggestion/([^/]+)/response", self.path)
            if response_match:
                return self._next_action_path(f"/api/next-action/{response_match.group(1)}/response", body)
            outcome_match = re.fullmatch(r"/api/next-action/suggestion/([^/]+)/outcome", self.path)
            if outcome_match:
                return self._next_action_path(f"/api/next-action/{outcome_match.group(1)}/outcome", body)
            if self.path == "/api/rewards/sync":
                return self._json(self.service.sync_rewards())
            if self.path == "/api/control/sync":
                return self._json(self.service.control_metrics.sync_status())
            if self.path == "/api/focus-bridge/decision":
                return self._intervention(
                    "phone_decision",
                    "POST",
                    {**body, "device_id": "android-main"},
                )
            if self.path == "/api/focus-bridge/event":
                return self._intervention(
                    "phone_event",
                    "POST",
                    {**body, "computer_id": "android-main"},
                )
            if self.path == "/api/focus-bridge/heartbeat":
                status = str(body.get("status", ""))
                if status not in {
                    "accessibility_connected", "accessibility_disconnected",
                    "foreground_running", "running",
                }:
                    raise ValueError("invalid bridge heartbeat status")
                return self._json(self.service.db.record_bridge_heartbeat(
                    "android-main", status, str(body.get("detail", "")),
                    _bridge_heartbeat_metadata(body),
                ))
            if self.path == "/api/focus/start":
                targets = body.get("targets", ["windows", "phone"])
                if not isinstance(targets, list):
                    raise ValueError("targets must be a list")
                return self._json(
                    self.service.start_focus(
                        str(body.get("profile_id", "study")),
                        int(body["duration"]),
                        [str(target) for target in targets],
                        task_id=(str(body.get("task_id", "")).strip() or None),
                        task_title=(str(body.get("task_title", "")).strip() or None),
                        source=str(body.get("source", "garden")),
                    ),
                    201,
                )
            if self.path == "/api/focus/schedule":
                targets = body.get("targets", ["windows", "phone"])
                if not isinstance(targets, list):
                    raise ValueError("targets must be a list")
                return self._json(self.service.create_schedule(
                    str(body.get("profile_id", "study")), int(body["duration"]),
                    [str(target) for target in targets], str(body["starts_at"]),
                ), 201)
            if self.path == "/api/focus/continuous":
                targets = body.get("targets", ["windows", "phone"])
                if not isinstance(targets, list):
                    raise ValueError("targets must be a list")
                return self._json(self.service.create_continuous_focus(
                    str(body.get("profile_id", "study")), int(body["focus_minutes"]),
                    int(body["rest_minutes"]), int(body["rounds"]), [str(target) for target in targets],
                ), 201)
            if self.path == "/api/focus/cancel":
                focus = self.service.db.focus()
                if focus:
                    self.service.release_focus_lease(focus)
                    self.service.db.cancel_focus(focus["id"])
                    self.service.db.cancel_focus_plan_for_session(focus["id"])
                return self._json({"ok": True})
            if self.path == "/api/focus/pause":
                return self._json(self.service.pause_focus(int(body["pause_minutes"])))
            if self.path == "/api/focus/resume":
                return self._json(self.service.resume_focus())
            if self.path == "/api/rewards/advanced-plant":
                species_id = str(body["species_id"])
                if species_id not in self.service.catalog_ids:
                    raise ValueError("未知植物种类")
                return self._json(
                    self.service.db.plant_advanced_from_basic(species_id, self.service.catalog_tiers[species_id]), 201
                )
            match = re.fullmatch(r"/api/rewards/([^/]+)/plant", self.path)
            if match:
                species_id = str(body["species_id"])
                if species_id not in self.service.catalog_ids:
                    raise ValueError("未知植物种类")
                reward_id = unquote(match.group(1))
                return self._json(self.service.db.plant_reward(reward_id, species_id, self.service.catalog_tiers[species_id]), 201)
            return self._json({"error": "not found"}, 404)
        except Exception as exc:
            self._error(exc)

    def _next_action_path(self, upstream_path: str, body: dict[str, Any]) -> None:
        """Forward the two ID-scoped endpoints after validating their exact shape."""
        try:
            status, data, set_cookie = self.service.next_action.request_path(
                upstream_path, body=body, cookie=self.headers.get("Cookie", ""),
                user_agent=self.headers.get("User-Agent", ""),
            )
            self._json(data, status, set_cookie)
        except Exception as exc:
            self._error(exc)

    def _static(self, path: str) -> None:
        relative = "index.html" if path in ("", "/") else path.lstrip("/")
        static_root = (self.service.root / "static").resolve()
        target = (static_root / relative).resolve()
        if static_root not in target.parents and target != static_root:
            self.send_error(404)
            return
        if not target.is_file():
            target = static_root / "index.html"
        body = target.read_bytes()
        content_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        self.send_response(200)
        self.send_header("Content-Type", content_type + ("; charset=utf-8" if content_type.startswith("text/") else ""))
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(body)


class GardenHTTPServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address: tuple[str, int], service: GardenService):
        super().__init__(address, GardenHandler)
        self.service = service


def start_reconciler(service: GardenService) -> threading.Thread:
    def loop() -> None:
        while True:
            try:
                service.reconcile_focus()
                service.run_due_focus_plan()
                service.reconcile_daily_achievements()
            except Exception as exc:
                print("focus reconcile error:", exc)
            time.sleep(2)
    thread = threading.Thread(target=loop, name="focus-reconciler", daemon=True)
    thread.start()
    return thread
