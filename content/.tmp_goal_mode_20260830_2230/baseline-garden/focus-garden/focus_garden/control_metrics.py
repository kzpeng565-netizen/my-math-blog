from __future__ import annotations

import json
import re
import sqlite3
import threading
from collections import defaultdict
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable
from zoneinfo import ZoneInfo


SHANGHAI = ZoneInfo("Asia/Shanghai")
PRIORITY_WEIGHTS = {
    "highest": 3.0,
    "high": 2.0,
    "medium": 1.5,
    "normal": 1.0,
    "low": 0.75,
    "lowest": 0.5,
}


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return {}


def _instant(value: Any) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(str(value))
    except (TypeError, ValueError):
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=SHANGHAI)
    return parsed.astimezone(SHANGHAI)


def _day(value: Any) -> date | None:
    instant = _instant(value)
    if instant:
        return instant.date()
    try:
        return date.fromisoformat(str(value)[:10])
    except (TypeError, ValueError):
        return None


def _ratio(current: float, baseline: float) -> float | None:
    return current / baseline if baseline > 0 else None


def _pct_delta(current: float, baseline: float | None) -> float | None:
    if baseline is None:
        return None
    ratio = _ratio(current, baseline)
    return round((ratio - 1) * 100, 1) if ratio is not None else None


def _sum(values: Iterable[float]) -> float:
    return float(sum(values))


class ControlMetrics:
    """Build a privacy-preserving weekly control snapshot from existing Pi facts.

    The report contains aggregates only. Task titles, raw activity, and AI report
    prose never leave the Raspberry Pi through this interface.
    """

    def __init__(self, database_path: Path, advisor_data_root: Path,
                 obsidian_sync_root: Path, snapshot_path: Path):
        self.database_path = Path(database_path)
        self.advisor_data_root = Path(advisor_data_root)
        self.obsidian_sync_root = Path(obsidian_sync_root)
        self.snapshot_path = Path(snapshot_path)
        self.live_snapshot_path = self.snapshot_path.with_name("control-live.json")
        self.daily_snapshot_root = self.snapshot_path.parent / "control-metrics"
        self._sync_lock = threading.Lock()

    def load_snapshot(self) -> dict[str, Any]:
        snapshot = _read_json(self.snapshot_path)
        if snapshot.get("schema_version") == 1:
            live = _read_json(self.live_snapshot_path)
            frozen_until = _instant(snapshot.get("frozen_until"))
            frozen_active = bool(frozen_until and frozen_until > datetime.now(SHANGHAI))
            live_matches_decision = (
                live.get("schema_version") == 1
                and live.get("decision_generated_at") == snapshot.get("generated_at")
            )
            live_is_current_preview = (
                live.get("schema_version") == 1
                and live.get("snapshot_state") == "synced_preview"
                and not frozen_active
            )
            if live_matches_decision or live_is_current_preview:
                return live
            snapshot["snapshot_state"] = "frozen"
            return snapshot
        report = self.build()
        report["snapshot_state"] = "provisional"
        return report

    def write_snapshot(self, *, force: bool = False) -> dict[str, Any]:
        existing = _read_json(self.snapshot_path)
        frozen_until = _instant(existing.get("frozen_until"))
        now = datetime.now(SHANGHAI)
        if existing.get("schema_version") == 1 and frozen_until and frozen_until > now and not force:
            existing["write_state"] = "still_frozen"
            return existing
        report = self.build(now=now)
        self.snapshot_path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.snapshot_path.with_suffix(self.snapshot_path.suffix + ".tmp")
        temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        temporary.replace(self.snapshot_path)
        self.live_snapshot_path.unlink(missing_ok=True)
        report["write_state"] = "updated"
        return report

    def sync_status(self) -> dict[str, Any]:
        """Refresh live aggregates without replacing the frozen weekly decision."""
        with self._sync_lock:
            now = datetime.now(SHANGHAI)
            daily = self.save_daily_snapshot(on_date=now.date(), force=True)
            report = self.build(now=now)
            frozen = _read_json(self.snapshot_path)
            frozen_until = _instant(frozen.get("frozen_until"))
            frozen_active = bool(
                frozen.get("schema_version") == 1
                and frozen_until
                and frozen_until > now
            )
            if frozen_active:
                report["state"] = frozen.get("state") or report["state"]
                report["frozen_until"] = frozen.get("frozen_until")
                report["policy"] = frozen.get("policy") or report["policy"]
                report["decision_generated_at"] = frozen.get("generated_at")
                report["snapshot_state"] = "synced_live"
            else:
                report["decision_generated_at"] = None
                report["snapshot_state"] = "synced_preview"
            report["synced_at"] = now.isoformat(timespec="seconds")
            report["daily_sync"] = {
                "date": daily.get("date"),
                "delay_debt": daily.get("delay_debt"),
                "postponed_task_count": daily.get("postponed_task_count"),
                "write_state": daily.get("write_state"),
            }
            self.live_snapshot_path.parent.mkdir(parents=True, exist_ok=True)
            temporary = self.live_snapshot_path.with_suffix(self.live_snapshot_path.suffix + ".tmp")
            temporary.write_text(
                json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            temporary.replace(self.live_snapshot_path)
            return report

    def save_daily_snapshot(self, *, on_date: date | None = None, force: bool = False) -> dict[str, Any]:
        snapshot_date = on_date or datetime.now(SHANGHAI).date()
        target = self.daily_snapshot_root / f"{snapshot_date.isoformat()}.json"
        if target.is_file() and not force:
            existing = _read_json(target)
            if existing.get("schema_version") == 1:
                existing["write_state"] = "already_recorded"
                return existing

        task_snapshot = _read_json(self.obsidian_sync_root / "context_snapshot.json")
        groups = task_snapshot.get("tasks") if isinstance(task_snapshot.get("tasks"), dict) else {}
        open_tasks: dict[str, dict[str, Any]] = {}
        for group in groups.values():
            if not isinstance(group, list):
                continue
            for task in group:
                if not isinstance(task, dict) or task.get("completed"):
                    continue
                task_id = str(task.get("task_id") or "").strip()
                if task_id:
                    open_tasks[task_id] = task

        task_state = _read_json(self.advisor_data_root / "task_sync" / "state.json")
        postponements = task_state.get("postponements") if isinstance(task_state.get("postponements"), dict) else {}
        task_values: dict[str, dict[str, float]] = {}
        for task_id, task in open_tasks.items():
            record = postponements.get(task_id)
            if not isinstance(record, dict):
                continue
            days = max(0, int(record.get("postponed_days") or 0))
            if not days:
                continue
            priority = str(task.get("priority") or "normal").lower()
            weight = PRIORITY_WEIGHTS.get(priority, 1.0)
            task_values[task_id] = {
                "capped_days": float(min(days, 7)),
                "weight": float(weight),
                "raw_days": float(days),
            }

        previous = self._latest_daily_snapshot(before=snapshot_date)
        previous_tasks = previous.get("_tasks") if isinstance(previous.get("_tasks"), dict) else {}
        weighted_new_days = 0.0
        for task_id, item in task_values.items():
            current_value = item["capped_days"] * item["weight"]
            old = previous_tasks.get(task_id) if isinstance(previous_tasks.get(task_id), dict) else {}
            previous_value = float(old.get("capped_days") or 0) * float(old.get("weight") or item["weight"])
            weighted_new_days += max(0.0, current_value - previous_value)

        result = {
            "schema_version": 1,
            "date": snapshot_date.isoformat(),
            "generated_at": datetime.now(SHANGHAI).isoformat(timespec="seconds"),
            "delay_debt": round(sum(item["capped_days"] * item["weight"] for item in task_values.values()), 2),
            "postponed_task_count": len(task_values),
            "max_postponed_days": int(max((item["raw_days"] for item in task_values.values()), default=0)),
            "weighted_new_days": round(weighted_new_days, 2),
            "source_revision": task_state.get("revision"),
            "task_snapshot_generated_at": task_snapshot.get("generated_at"),
            "_tasks": task_values,
        }
        self.daily_snapshot_root.mkdir(parents=True, exist_ok=True)
        temporary = target.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        temporary.replace(target)
        result["write_state"] = "updated"
        return result

    def build(self, now: datetime | None = None) -> dict[str, Any]:
        current_time = (now or datetime.now(SHANGHAI)).astimezone(SHANGHAI)
        reports = self._daily_reports()
        latest_day = max(reports, default=current_time.date() - timedelta(days=1))
        current_days = [latest_day - timedelta(days=offset) for offset in range(6, -1, -1)]
        baseline_days = [latest_day - timedelta(days=offset) for offset in range(27, 6, -1)]
        current_set, baseline_set = set(current_days), set(baseline_days)

        categories = self._task_categories(reports)
        focus = self._focus_by_day(categories, current_set | baseline_set)
        next_action = self._next_action_by_day(current_set | baseline_set)
        interventions = self._interventions_by_day(current_set | baseline_set)
        task_completions = self._task_completions_by_day(current_set | baseline_set)

        current_report_days = [day for day in current_days if day in reports]
        baseline_report_days = [day for day in baseline_days if day in reports]
        daily = self._daily_values(reports)
        delay = self.save_daily_snapshot(on_date=current_time.date())
        delay_baseline_snapshot = self._latest_daily_snapshot(before=current_time.date() - timedelta(days=6))

        def period_sum(source: dict[date, dict[str, float]], days: list[date], key: str) -> float:
            return _sum(source.get(day, {}).get(key, 0.0) for day in days)

        def scaled_baseline(source: dict[date, dict[str, float]], days: list[date], key: str) -> float:
            valid = [day for day in days if day in source]
            return round(period_sum(source, valid, key) / len(valid) * 7, 2) if valid else 0.0

        math_current = round(period_sum(focus, current_days, "math_minutes") / 40, 2)
        math_baseline = round(scaled_baseline(focus, baseline_days, "math_minutes") / 40, 2)
        work_current = round(period_sum(daily, current_report_days, "work_minutes"), 1)
        work_baseline = round(scaled_baseline(daily, baseline_report_days, "work_minutes"), 1)
        leisure_current = round(period_sum(daily, current_report_days, "leisure_minutes"), 1)
        leisure_baseline = round(scaled_baseline(daily, baseline_report_days, "leisure_minutes"), 1)
        debt_current = float(delay.get("delay_debt") or 0)
        debt_baseline = float(delay_baseline_snapshot["delay_debt"]) if "delay_debt" in delay_baseline_snapshot else None

        asked_current = int(period_sum(next_action, current_days, "asked"))
        accepted_current = int(period_sum(next_action, current_days, "accepted"))
        completed_current = int(period_sum(next_action, current_days, "completed"))
        asked_baseline = int(period_sum(next_action, baseline_days, "asked"))
        accepted_baseline = int(period_sum(next_action, baseline_days, "accepted"))
        completed_baseline = int(period_sum(next_action, baseline_days, "completed"))
        accept_rate = accepted_current / asked_current if asked_current else 0.0
        accept_base = accepted_baseline / asked_baseline if asked_baseline else 0.0
        finish_rate = completed_current / accepted_current if accepted_current else 0.0
        finish_base = completed_baseline / accepted_baseline if accepted_baseline else 0.0

        active_current = self._active_days(current_days, focus, next_action, interventions, task_completions)
        active_baseline_days = self._active_days(baseline_days, focus, next_action, interventions, task_completions)
        active_rate = active_current / 7
        active_base = active_baseline_days / len(baseline_days) if baseline_days else 0.0

        recovery_offers = int(period_sum(interventions, current_days, "offers"))
        recovery_accepts = int(period_sum(interventions, current_days, "accepted"))
        recovery_base_offers = int(period_sum(interventions, baseline_days, "offers"))
        recovery_base_accepts = int(period_sum(interventions, baseline_days, "accepted"))
        recovery_rate = recovery_accepts / recovery_offers if recovery_offers else 0.0
        recovery_base = recovery_base_accepts / recovery_base_offers if recovery_base_offers else 0.0

        ai_task = round(period_sum(daily, current_report_days, "ai_task_minutes"), 1)
        ai_free = round(period_sum(daily, current_report_days, "ai_free_minutes"), 1)
        ai_unknown = round(period_sum(daily, current_report_days, "ai_unknown_minutes"), 1)

        total_focus = period_sum(focus, current_days, "task_minutes")
        classified_focus = period_sum(focus, current_days, "classified_minutes")
        math_quality = "high" if total_focus and classified_focus / total_focus >= 0.8 else "medium" if total_focus and classified_focus / total_focus >= 0.5 else "low"
        values: dict[str, tuple[float, float | None]] = {
            "M": (math_current, math_baseline),
            "D": (debt_current, debt_baseline),
            "W": (work_current, work_baseline),
            "L": (leisure_current, leisure_baseline),
            "A": (accept_rate, accept_base),
            "F": (finish_rate, finish_base),
            "U": (active_rate, active_base),
            "R": (recovery_rate, recovery_base),
        }
        state = self._classify(values, {
            "report_days": len(current_report_days),
            "report_stale_days": max(0, (current_time.date() - latest_day).days),
            "asked": asked_current,
            "accepted": accepted_current,
            "recovery_offers": recovery_offers,
            "math_quality": math_quality,
            "core_ready": bool(
                (math_quality != "low" and (math_current > 0 or math_baseline > 0))
                or debt_baseline is not None
            ),
            "delay_baseline_ready": debt_baseline is not None,
        })
        metrics = [
            self._metric("M", "数学番茄", math_current, "P", math_baseline, "核心结果", math_quality,
                         f"数学任务匹配 {int(classified_focus)}/{int(total_focus)} 分钟" if total_focus else "本窗口没有绑定任务的有效专注"),
            self._metric("D", "任务推迟债务", debt_current, "点", debt_baseline, "核心结果",
                         "high" if debt_baseline is not None else "collecting",
                         f"{int(delay.get('postponed_task_count') or 0)} 个未完成推迟任务 · 最多推迟 {int(delay.get('max_postponed_days') or 0)} 天"),
            self._metric("W", "可观测工作", work_current, "分钟", work_baseline, "诊断", "high" if len(current_report_days) >= 5 else "low",
                         f"覆盖 {len(current_report_days)}/7 个已完成日报日"),
            self._metric("L", "娱乐", leisure_current, "分钟", leisure_baseline, "诊断", "high" if len(current_report_days) >= 5 else "low",
                         f"覆盖 {len(current_report_days)}/7 个已完成日报日"),
            self._metric("A", "建议接受率", round(accept_rate * 100, 1), "%", round(accept_base * 100, 1), "诊断", "high" if asked_current >= 5 else "low",
                         f"{accepted_current}/{asked_current} 个建议"),
            self._metric("F", "接受后完成率", round(finish_rate * 100, 1), "%", round(finish_base * 100, 1), "近端结果", "high" if accepted_current >= 3 else "low",
                         f"{completed_current}/{accepted_current} 个已接受建议"),
            self._metric("U", "有效使用率", round(active_rate * 100, 1), "%", round(active_base * 100, 1), "系统健康", "high",
                         f"{active_current}/7 天出现专注、接受建议、接受介入或完成任务"),
            self._metric("R", "首次介入主动恢复率", round(recovery_rate * 100, 1), "%", round(recovery_base * 100, 1), "自控能力", "medium" if recovery_offers >= 3 else "low",
                         f"{recovery_accepts}/{recovery_offers} 次首轮可选介入被接受且执行成功"),
        ]
        generated_at = current_time.isoformat(timespec="seconds")
        frozen_until = (current_time + timedelta(days=7)).isoformat(timespec="seconds")
        return {
            "schema_version": 1,
            "generated_at": generated_at,
            "frozen_until": frozen_until,
            "window": {
                "current": {"start": current_days[0].isoformat(), "end": current_days[-1].isoformat(), "report_days": len(current_report_days)},
                "baseline": {"start": baseline_days[0].isoformat(), "end": baseline_days[-1].isoformat(), "report_days": len(baseline_report_days)},
            },
            "state": state,
            "metrics": metrics,
            "ai": {"task_minutes": ai_task, "free_minutes": ai_free, "unknown_minutes": ai_unknown, "role": "辅助诊断"},
            "policy": {
                "automatic_parameter_mutation": False,
                "weekly_change_limit": 1,
                "hard_rules_stable": ["Steam 既有锁定", "Focus 既有锁定", "第二次强制介入"],
                "note": "当前只冻结识别结果与唯一建议；指标可靠性足够前不自动加严。",
            },
        }

    @staticmethod
    def _metric(metric_id: str, label: str, value: float, unit: str, baseline: float | None,
                role: str, quality: str, coverage: str) -> dict[str, Any]:
        return {"id": metric_id, "label": label, "value": value, "unit": unit,
                "baseline": baseline, "delta_percent": _pct_delta(value, baseline),
                "role": role, "quality": quality, "coverage": coverage}

    def _daily_reports(self) -> dict[date, dict[str, Any]]:
        reports: dict[date, dict[str, Any]] = {}
        root = self.advisor_data_root / "statistics" / "daily_life"
        for path in root.glob("*.json"):
            report = _read_json(path)
            report_day = _day(report.get("period") or path.stem)
            if report_day:
                reports[report_day] = report
        return reports

    def _latest_daily_snapshot(self, *, before: date) -> dict[str, Any]:
        candidates: list[tuple[date, Path]] = []
        for path in self.daily_snapshot_root.glob("*.json"):
            snapshot_day = _day(path.stem)
            if snapshot_day and snapshot_day < before:
                candidates.append((snapshot_day, path))
        if not candidates:
            return {}
        return _read_json(max(candidates, key=lambda item: item[0])[1])

    def _daily_values(self, reports: dict[date, dict[str, Any]]) -> dict[date, dict[str, float]]:
        values: dict[date, dict[str, float]] = {}
        for report_day, report in reports.items():
            totals = report.get("daily_totals") if isinstance(report.get("daily_totals"), dict) else {}
            ai = report.get("ai_usage") if isinstance(report.get("ai_usage"), dict) else {}
            ai_by = ai.get("by_activity") if isinstance(ai.get("by_activity"), dict) else {}
            values[report_day] = {
                "work_minutes": float(totals.get("work_minutes") or 0),
                "leisure_minutes": float(totals.get("entertainment_minutes") or 0),
                "ai_task_minutes": float(ai_by.get("work") or 0),
                "ai_free_minutes": float(ai_by.get("entertainment") or 0) + float(ai_by.get("other") or 0),
                "ai_unknown_minutes": float(ai_by.get("uncertain") or 0),
            }
        return values

    def _task_categories(self, reports: dict[date, dict[str, Any]]) -> tuple[dict[str, str], dict[str, str]]:
        by_id: dict[str, str] = {}
        by_title: dict[str, str] = {}
        snapshot = _read_json(self.obsidian_sync_root / "context_snapshot.json")
        groups = (snapshot.get("tasks") or {}) if isinstance(snapshot.get("tasks"), dict) else {}
        candidates: list[dict[str, Any]] = []
        for group in groups.values():
            if isinstance(group, list):
                candidates.extend(item for item in group if isinstance(item, dict))
        task_state = _read_json(self.advisor_data_root / "task_sync" / "state.json")
        for completion in task_state.get("completions") or []:
            task = completion.get("task") if isinstance(completion, dict) else None
            if isinstance(task, dict):
                candidates.append(task)
        for report in reports.values():
            for task in report.get("tomorrow_task_candidates") or []:
                if isinstance(task, dict):
                    candidates.append(task)
        for task in candidates:
            category = str(task.get("category") or "").strip()
            task_id = str(task.get("task_id") or "").strip()
            title = str(task.get("title") or "").strip()
            if category and task_id:
                by_id[task_id] = category
            if category and title:
                by_title[title] = category
        return by_id, by_title

    def _focus_by_day(self, categories: tuple[dict[str, str], dict[str, str]], wanted: set[date]) -> dict[date, dict[str, float]]:
        result: dict[date, dict[str, float]] = defaultdict(lambda: defaultdict(float))
        if not self.database_path.is_file():
            return result
        by_id, by_title = categories
        conn = sqlite3.connect(self.database_path)
        try:
            conn.row_factory = sqlite3.Row
            columns = {row[1] for row in conn.execute("PRAGMA table_info(focus_sessions)")}
            credit = "credited_minutes" if "credited_minutes" in columns else "duration_minutes"
            rows = conn.execute(f"SELECT task_id,task_title,completed_at,duration_minutes,{credit} AS credit FROM focus_sessions WHERE status='completed' AND completed_at IS NOT NULL").fetchall()
        finally:
            conn.close()
        for row in rows:
            completed_day = _day(row["completed_at"])
            if completed_day not in wanted:
                continue
            minutes = float(row["credit"] or row["duration_minutes"] or 0)
            result[completed_day]["active"] += 1
            task_id, title = str(row["task_id"] or ""), str(row["task_title"] or "")
            if task_id or title:
                result[completed_day]["task_minutes"] += minutes
            category = by_id.get(task_id) or by_title.get(title)
            if category:
                result[completed_day]["classified_minutes"] += minutes
                if "数学" in category:
                    result[completed_day]["math_minutes"] += minutes
        return result

    def _next_action_by_day(self, wanted: set[date]) -> dict[date, dict[str, float]]:
        root = self.advisor_data_root / "next_action"
        result: dict[date, dict[str, float]] = defaultdict(lambda: defaultdict(float))
        accepted: dict[str, date] = {}
        completed_ids: set[str] = set()
        for path in (root / "outcomes").glob("*/*.json"):
            record = _read_json(path)
            if record.get("result") == "completed":
                completed_ids.add(str(record.get("suggestion_id") or ""))
        for path in (root / "suggestions").glob("*/*.json"):
            record = _read_json(path)
            event_day = _day(record.get("created_at"))
            if event_day in wanted:
                result[event_day]["asked"] += 1
        for path in (root / "responses").glob("*/*.json"):
            record = _read_json(path)
            event_day = _day(record.get("received_at"))
            suggestion_id = str(record.get("suggestion_id") or "")
            if event_day in wanted and suggestion_id and record.get("result") == "accepted":
                accepted[suggestion_id] = event_day
                result[event_day]["accepted"] += 1
        for suggestion_id, accepted_day in accepted.items():
            if suggestion_id in completed_ids:
                result[accepted_day]["completed"] += 1
        return result

    def _interventions_by_day(self, wanted: set[date]) -> dict[date, dict[str, float]]:
        root = self.advisor_data_root / "computer_interventions" / "responses"
        result: dict[date, dict[str, float]] = defaultdict(lambda: defaultdict(float))
        records: dict[str, dict[str, Any]] = {}
        for path in root.glob("**/*final.json"):
            record = _read_json(path)
            event = record.get("event") if isinstance(record.get("event"), dict) else {}
            request_id = str(event.get("request_id") or record.get("request_id") or "")
            if request_id:
                records[request_id] = record
        offer_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}-\d{2}-\d{2}_\d{2}-\d{2}$")
        for request_id, record in records.items():
            if not offer_pattern.fullmatch(request_id):
                continue
            event = record.get("event") if isinstance(record.get("event"), dict) else {}
            event_day = _day(event.get("decided_at") or record.get("received_at"))
            decision = str(event.get("decision") or "")
            if event_day not in wanted:
                continue
            if decision in {"accepted", "ignored", "declined"}:
                result[event_day]["offers"] += 1
            if decision == "accepted":
                execute_record = records.get(request_id + "-execute") or record
                execute_event = execute_record.get("event") if isinstance(execute_record.get("event"), dict) else {}
                executions = execute_event.get("executions") if isinstance(execute_event.get("executions"), list) else []
                if any(isinstance(item, dict) and item.get("status") == "success" for item in executions):
                    result[event_day]["accepted"] += 1
        return result

    def _task_completions_by_day(self, wanted: set[date]) -> dict[date, dict[str, float]]:
        result: dict[date, dict[str, float]] = defaultdict(lambda: defaultdict(float))
        state = _read_json(self.advisor_data_root / "task_sync" / "state.json")
        for completion in state.get("completions") or []:
            if not isinstance(completion, dict):
                continue
            completed_day = _day(completion.get("completed_at"))
            if completed_day in wanted:
                result[completed_day]["completed"] += 1
        return result

    @staticmethod
    def _active_days(days: list[date], focus: dict[date, dict[str, float]],
                     next_action: dict[date, dict[str, float]], interventions: dict[date, dict[str, float]],
                     completions: dict[date, dict[str, float]]) -> int:
        return sum(1 for day in days if (
            focus.get(day, {}).get("active", 0)
            or next_action.get(day, {}).get("accepted", 0)
            or interventions.get(day, {}).get("accepted", 0)
            or completions.get(day, {}).get("completed", 0)
        ))

    @staticmethod
    def _classify(values: dict[str, tuple[float, float | None]], context: dict[str, Any]) -> dict[str, Any]:
        m, mb = values["M"]
        d, db = values["D"]
        w, wb = values["W"]
        leisure, leisure_base = values["L"]
        accept, accept_base = values["A"]
        finish, finish_base = values["F"]
        usage, usage_base = values["U"]
        recovery, recovery_base = values["R"]
        m_low = mb > 0 and m < 0.75 * mb
        d_worse = db is not None and d > max(db + 0.5, db * 1.25)
        w_low = wb > 0 and w < 0.75 * wb
        leisure_high = leisure_base > 0 and leisure > 1.25 * leisure_base
        accept_low = context["asked"] >= 5 and accept_base > 0 and accept < 0.75 * accept_base
        finish_low = context["accepted"] >= 3 and finish_base > 0 and finish < 0.75 * finish_base
        usage_low = usage_base >= 0.5 and usage < usage_base - 0.25
        recovery_low = context["recovery_offers"] >= 3 and recovery_base > 0 and recovery < 0.75 * recovery_base
        outcomes_bad = m_low or d_worse
        evidence: list[str] = []

        def add(text: str, condition: bool) -> None:
            if condition and len(evidence) < 3:
                evidence.append(text)

        if m_low and mb and (delta := _pct_delta(m, mb)) is not None:
            add(f"数学番茄较基线 {delta:+.0f}%", True)
        if d_worse and db is not None:
            add(f"任务推迟债务 {db:g} → {d:g}", True)
        if w_low and wb and (delta := _pct_delta(w, wb)) is not None:
            add(f"可观测工作较基线 {delta:+.0f}%", True)
        if leisure_high and leisure_base and (delta := _pct_delta(leisure, leisure_base)) is not None:
            add(f"娱乐较基线 {delta:+.0f}%", True)
        add(f"有效使用率 {usage_base * 100:.0f}% → {usage * 100:.0f}%", usage_low)
        add(f"建议接受率 {accept_base * 100:.0f}% → {accept * 100:.0f}%", accept_low)
        add(f"接受后完成率 {finish_base * 100:.0f}% → {finish * 100:.0f}%", finish_low)
        add(f"首次介入主动恢复率 {recovery_base * 100:.0f}% → {recovery * 100:.0f}%", recovery_low)

        if context["report_days"] < 4 or context["report_stale_days"] > 2 or not context.get("core_ready", True):
            code = "S7"
        elif usage_low and outcomes_bad:
            code = "S5"
        elif usage_low and not outcomes_bad:
            code = "S6"
        elif not outcomes_bad:
            code = "S0"
        elif not w_low and not leisure_high:
            code = "S1"
        elif accept_low and not finish_low:
            code = "S2"
        elif leisure_high and (w_low or finish_low or recovery_low):
            code = "S4"
        elif w_low and not leisure_high:
            code = "S7"
        else:
            code = "S3"

        definitions = {
            "S0": ("正常运行", "stable", "结果与系统使用没有出现需要调整的组合。", "本周期不调整核心参数。"),
            "S1": ("任务规划失配", "plan", "投入没有明显下降，但结果变量恶化，优先检查任务排序与负荷。", "只调整 Next Action 的任务排序或拆分，不增加娱乐限制。"),
            "S2": ("推荐失配", "plan", "接受率下降而接受后仍能完成，问题更可能在推荐。", "只复核 Next Action 候选与拒绝原因。"),
            "S3": ("执行困难", "attention", "愿意执行但完成困难，或结果下降尚不能归因于娱乐。", "把下一项行动缩小到一个 20—40 分钟单元。"),
            "S4": ("娱乐性偏离", "risk", "产出、工作、娱乐与恢复信号共同指向娱乐抢占。", "保持硬规则，只把接受 Next Action 后的 Focus 设为默认建议。"),
            "S5": ("系统弃用风险", "risk", "系统有效使用与真实结果同时下降。", "停止加严；本周只排查一个造成弃用的摩擦点。"),
            "S6": ("自主稳定", "stable", "系统使用下降，但结果没有随之恶化。", "减少非必要提示，Steam 与 Focus 硬规则保持。"),
            "S7": ("不可判定 / 数据异常", "unknown", "数据覆盖不足，或低产出不能由已观测工作和娱乐解释。", "不调整参数；只补充一次低摩擦现实情况标注。"),
        }
        name, tone, summary, adjustment = definitions[code]
        if code == "S7" and not context.get("core_ready"):
            evidence = []
            if context.get("math_quality") == "low":
                evidence.append("M 的数学任务匹配覆盖不足，不能可靠比较产出")
            if not context.get("delay_baseline_ready"):
                evidence.append("D 的每日推迟债务基线正在积累")
        elif code == "S0":
            evidence = ["M 与 D 均未触发显著恶化阈值", f"系统有效使用率为 {usage * 100:.0f}%"]
        if not evidence:
            evidence = ["当前窗口没有触发显著变化阈值"]
        return {"code": code, "name": name, "tone": tone, "summary": summary,
                "evidence": evidence[:3], "single_adjustment": adjustment,
                "redline_triggered": code == "S5"}
