"""Independent long-horizon Goal Agent for the private Focus Garden.

The Goal Agent is deliberately separate from Next Action.  It owns a small
SQLite database, evaluates evidence against explicit acceptance criteria, and
may revise short-horizon plan items.  It never writes the Obsidian vault: a
confirmed recommended day is converted into the existing task-sync mutation
protocol and is considered synchronized only after a later exported snapshot
contains the stable task id.

The module uses only the Python standard library so it remains suitable for a
1 GB Raspberry Pi.  Local study materials are searched with SQLite FTS5 when
available; there is no vector service and no raw note text is sent to Tavily.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import os
import re
import sqlite3
import threading
import uuid
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

from deepseek_client import _request_json_report


SCHEMA_VERSION = 1
TIMEZONE = "Asia/Shanghai"
PORTFOLIO_ID = "math-2028-amss-he-weikun"
TRIAL_END = "2026-09-27"
REQUEST_ID_RE = re.compile(r"^[A-Za-z0-9_-]{8,100}$")
PLAN_ITEM_ID_RE = re.compile(r"^[A-Za-z0-9_-]{4,80}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TRACK_CODES = ("courses", "amss_exam", "ergodic", "abstract_algebra")
TRACK_WEIGHTS = {
    "courses": 0.40,
    "amss_exam": 0.20,
    "ergodic": 0.30,
    "abstract_algebra": 0.10,
}
COURSES = ("概率论", "泛函分析", "微分几何")
MAJOR_CHANGE_KEYS = {
    "portfolio_title",
    "target_date",
    "track_weights",
    "capacity_min_minutes",
    "capacity_max_minutes",
    "track_deadline",
    "cross_month_move",
}


class GoalAgentConflictError(RuntimeError):
    def __init__(self, current_version: int):
        super().__init__("plan version conflict")
        self.current_version = current_version


class GoalAgentNotFoundError(KeyError):
    pass


class _ClosingConnection(sqlite3.Connection):
    """sqlite3 context manager that also releases the file descriptor."""

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            return super().__exit__(exc_type, exc_value, traceback)
        finally:
            self.close()


@dataclass(frozen=True)
class GoalAgentPaths:
    database: Path
    material_root: Path
    tavily_env: Path


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def _loads(value: Any, default: Any) -> Any:
    if not isinstance(value, str) or not value:
        return default
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return default


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def _clean_text(value: Any, limit: int = 2000) -> str:
    return " ".join(str(value or "").split())[:limit]


def _parse_date(value: Any, *, required: bool = False) -> str | None:
    text = str(value or "").strip()
    if not text:
        if required:
            raise ValueError("date is required")
        return None
    if not DATE_RE.fullmatch(text):
        raise ValueError("date must use YYYY-MM-DD")
    date.fromisoformat(text)
    return text


def _week_start(day: date) -> date:
    return day - timedelta(days=day.weekday())


def _load_env_file(path: Path) -> None:
    """Load a private KEY=VALUE file without returning or logging its values."""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if re.fullmatch(r"[A-Z][A-Z0-9_]*", key.strip()):
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def course_grade_scenario(events: Iterable[dict[str, Any]], target: float = 90.0) -> dict[str, Any]:
    """Return a transparent course-grade scenario, never an invented point estimate."""
    known: list[tuple[float, float]] = []
    for event in events:
        payload = event.get("payload") if isinstance(event.get("payload"), dict) else {}
        weight = payload.get("weight")
        score = event.get("score")
        maximum = event.get("max_score")
        if not isinstance(weight, (int, float)) or not isinstance(score, (int, float)):
            continue
        maximum = maximum if isinstance(maximum, (int, float)) and maximum > 0 else 100.0
        normalized = 100.0 * float(score) / float(maximum)
        if 0 < float(weight) <= 1:
            known.append((float(weight), normalized))
    used = sum(weight for weight, _ in known)
    if not known or used <= 0 or used >= 1.000001:
        return {
            "state": "unknown",
            "known_weight": round(used, 4),
            "required_remaining_average": None,
            "reason": "考核比例或已取得成绩不足，不能计算总评预测。",
        }
    earned = sum(weight * score for weight, score in known)
    remaining = 1.0 - used
    required = (target - earned) / remaining
    return {
        "state": "possible" if required <= 100 else "at_risk",
        "known_weight": round(used, 4),
        "earned_points": round(earned, 2),
        "remaining_weight": round(remaining, 4),
        "required_remaining_average": round(required, 2),
        "target": target,
        "reason": (
            "按已确认考核比例计算。" if required <= 100
            else "即使剩余部分满分也无法达到目标；需核验比例或寻求额外得分路径。"
        ),
    }


def consecutive_exam_passes(events: Iterable[dict[str, Any]]) -> dict[str, Any]:
    attempts: list[dict[str, Any]] = []
    for event in events:
        score, maximum = event.get("score"), event.get("max_score")
        source_id = _clean_text(event.get("source_id"), 160)
        if not isinstance(score, (int, float)) or not isinstance(maximum, (int, float)) or maximum <= 0:
            continue
        normalized = 150.0 * float(score) / float(maximum)
        attempts.append({
            "occurred_at": str(event.get("occurred_at") or ""),
            "score_150": round(normalized, 1),
            "source_id": source_id or "unknown",
            "passed": normalized >= 120.0 and bool(source_id),
        })
    attempts.sort(key=lambda item: item["occurred_at"])
    streak: list[dict[str, Any]] = []
    used_sources: set[str] = set()
    for attempt in reversed(attempts):
        if not attempt["passed"] or attempt["source_id"] in used_sources:
            break
        streak.append(attempt)
        used_sources.add(attempt["source_id"])
    streak.reverse()
    return {
        "attempt_count": len(attempts),
        "consecutive_distinct_passes": len(streak),
        "criterion_met": len(streak) >= 3,
        "recent": attempts[-3:],
    }


class GoalAgent:
    def __init__(
        self,
        output_root: Path,
        settings: dict[str, Any],
        *,
        env_file: Path,
        now: Callable[[], datetime] | None = None,
        model_runner: Callable[[dict[str, Any], list[dict[str, str]]], tuple[dict[str, Any], dict[str, Any]]] | None = None,
    ) -> None:
        config = settings.get("goal_agent", {}) if isinstance(settings.get("goal_agent"), dict) else {}
        database = Path(config.get("database_path") or output_root / "goal_agent" / "goal-agent.sqlite3")
        material_root = Path(config.get("material_root") or "/home/conrad/workspace/behavior-context-sync/goal_agent")
        tavily_env = Path(config.get("tavily_env_file") or "/home/conrad/.config/activitywatch-advisor/tavily.env")
        self.paths = GoalAgentPaths(database=database, material_root=material_root, tavily_env=tavily_env)
        self.settings = settings
        self.config = config
        self.env_file = env_file
        self._now = now or (lambda: datetime.now(ZoneInfo(settings.get("timezone", TIMEZONE))))
        self._model_runner = model_runner or _request_json_report
        self._lock = threading.RLock()
        self.paths.database.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(
            self.paths.database,
            timeout=20,
            factory=_ClosingConnection,
        )
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute("PRAGMA busy_timeout=20000")
        return connection

    def _initialize(self) -> None:
        with self._lock, self._connect() as connection:
            connection.executescript(
                """
                PRAGMA journal_mode=WAL;
                CREATE TABLE IF NOT EXISTS meta (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS portfolio (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    target_cohort TEXT NOT NULL,
                    institution TEXT NOT NULL,
                    direction TEXT NOT NULL,
                    start_date TEXT NOT NULL,
                    target_date TEXT NOT NULL,
                    capacity_min_minutes INTEGER NOT NULL,
                    capacity_max_minutes INTEGER NOT NULL,
                    capacity_baseline_minutes INTEGER NOT NULL,
                    timezone TEXT NOT NULL,
                    feature_enabled INTEGER NOT NULL,
                    trial_ends_on TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS track (
                    id TEXT PRIMARY KEY,
                    portfolio_id TEXT NOT NULL REFERENCES portfolio(id),
                    code TEXT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    weight REAL NOT NULL,
                    outcome_definition TEXT NOT NULL,
                    deadline TEXT,
                    config_json TEXT NOT NULL DEFAULT '{}'
                );
                CREATE TABLE IF NOT EXISTS milestone (
                    id TEXT PRIMARY KEY,
                    track_id TEXT REFERENCES track(id),
                    period_start TEXT NOT NULL,
                    period_end TEXT NOT NULL,
                    title TEXT NOT NULL,
                    acceptance_json TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'planned',
                    sort_order INTEGER NOT NULL,
                    archived INTEGER NOT NULL DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS plan_item (
                    id TEXT PRIMARY KEY,
                    track_id TEXT NOT NULL REFERENCES track(id),
                    milestone_id TEXT REFERENCES milestone(id),
                    week_start TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL DEFAULT '',
                    deep_minutes INTEGER NOT NULL,
                    recommended_date TEXT,
                    accepted_date TEXT,
                    status TEXT NOT NULL DEFAULT 'planned',
                    value_score INTEGER NOT NULL DEFAULT 3,
                    material_required INTEGER NOT NULL DEFAULT 0,
                    material_status TEXT NOT NULL DEFAULT 'pending',
                    auto_adjustable INTEGER NOT NULL DEFAULT 1,
                    sort_order INTEGER NOT NULL DEFAULT 0,
                    archived INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS evidence_event (
                    id TEXT PRIMARY KEY,
                    track_id TEXT NOT NULL REFERENCES track(id),
                    plan_item_id TEXT REFERENCES plan_item(id),
                    evidence_type TEXT NOT NULL,
                    occurred_at TEXT NOT NULL,
                    deep_minutes INTEGER,
                    completed_units REAL,
                    total_units REAL,
                    score REAL,
                    max_score REAL,
                    source_id TEXT,
                    difficulty INTEGER,
                    confidence INTEGER,
                    blocked_reason TEXT,
                    change_note TEXT,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS progress_snapshot (
                    id TEXT PRIMARY KEY,
                    generated_at TEXT NOT NULL,
                    trigger TEXT NOT NULL,
                    plan_version INTEGER NOT NULL,
                    metrics_json TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS plan_version (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    trigger TEXT NOT NULL,
                    parent_version INTEGER,
                    snapshot_json TEXT NOT NULL,
                    diff_json TEXT NOT NULL,
                    actor TEXT NOT NULL,
                    rollback_of INTEGER
                );
                CREATE TABLE IF NOT EXISTS approval_request (
                    id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    status TEXT NOT NULL,
                    change_type TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    evidence_json TEXT NOT NULL,
                    patch_json TEXT NOT NULL,
                    base_plan_version INTEGER NOT NULL,
                    decided_at TEXT,
                    decision_note TEXT
                );
                CREATE TABLE IF NOT EXISTS source_record (
                    id TEXT PRIMARY KEY,
                    source_kind TEXT NOT NULL,
                    grade TEXT NOT NULL,
                    url TEXT,
                    title TEXT NOT NULL,
                    published_at TEXT,
                    fetched_at TEXT,
                    body_hash TEXT,
                    excerpt TEXT,
                    status TEXT NOT NULL,
                    reference_only INTEGER NOT NULL DEFAULT 0,
                    metadata_json TEXT NOT NULL DEFAULT '{}'
                );
                CREATE TABLE IF NOT EXISTS chat_message (
                    id TEXT PRIMARY KEY,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    metadata_json TEXT NOT NULL DEFAULT '{}'
                );
                CREATE TABLE IF NOT EXISTS request_log (
                    request_id TEXT PRIMARY KEY,
                    endpoint TEXT NOT NULL,
                    base_plan_version INTEGER NOT NULL,
                    response_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS plan_item_task (
                    plan_item_id TEXT PRIMARY KEY REFERENCES plan_item(id),
                    task_id TEXT UNIQUE NOT NULL,
                    mutation_id TEXT,
                    sync_status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    synced_at TEXT
                );
                CREATE TABLE IF NOT EXISTS material_record (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    source_path TEXT NOT NULL,
                    sha256 TEXT NOT NULL,
                    modified_at TEXT,
                    page_count INTEGER,
                    status TEXT NOT NULL,
                    indexed_at TEXT NOT NULL,
                    UNIQUE(source_path, sha256)
                );
                """
            )
            try:
                connection.execute(
                    "CREATE VIRTUAL TABLE IF NOT EXISTS material_fts USING fts5("
                    "record_id UNINDEXED, title, content, source_path UNINDEXED, "
                    "page_start UNINDEXED, page_end UNINDEXED, sha256 UNINDEXED)"
                )
                connection.execute("INSERT OR REPLACE INTO meta(key,value) VALUES('fts5','1')")
            except sqlite3.OperationalError:
                connection.execute("INSERT OR REPLACE INTO meta(key,value) VALUES('fts5','0')")
            self._seed(connection)
            connection.execute(
                "INSERT OR REPLACE INTO meta(key,value) VALUES('schema_version',?)",
                (str(SCHEMA_VERSION),),
            )

    def _seed(self, connection: sqlite3.Connection) -> None:
        if connection.execute("SELECT 1 FROM portfolio WHERE id=?", (PORTFOLIO_ID,)).fetchone():
            if not connection.execute("SELECT 1 FROM plan_version LIMIT 1").fetchone():
                self._create_version(connection, "恢复缺失的初始版本", "seed", [], "system")
            return
        now = self._now().isoformat(timespec="seconds")
        connection.execute(
            "INSERT INTO portfolio VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                PORTFOLIO_ID,
                "2028 级保研到数学所何伟鲲方向",
                "2028级",
                "中国科学院数学与系统科学研究院",
                "何伟鲲方向",
                "2026-08-31",
                "2027-09-30",
                1320,
                1860,
                1590,
                TIMEZONE,
                1,
                TRIAL_END,
                now,
                now,
            ),
        )
        tracks = (
            (
                "track-courses", "courses", "专业课三门均 ≥90", 0.40,
                "概率论、泛函分析、微分几何课程总评均不低于 90。",
                None,
                {"courses": list(COURSES), "target_score": 90, "assessment_known": False},
            ),
            (
                "track-amss-exam", "amss_exam", "数学所笔试", 0.20,
                "不同真实题源下连续 3 次限时成绩不低于 120/150。",
                "2027-08-31",
                {"target_score": 120, "max_score": 150, "required_streak": 3},
            ),
            (
                "track-ergodic", "ergodic", "遍历论与导师交流", 0.30,
                "完成双方确认章节与真实习题，并形成读书笔记、讲解和问题单。",
                "2027-01-31",
                {"note_pages": [3, 5], "talk_minutes": [20, 30], "question_sheet": True},
            ),
            (
                "track-algebra", "abstract_algebra", "抽象代数笔试与面试", 0.10,
                "不同真实题组连续 3 轮书面正确率 ≥80%，口头四项均 ≥4/5。",
                "2027-08-31",
                {"written_rate": 0.8, "written_streak": 3, "oral_min": 4},
            ),
        )
        for track_id, code, title, weight, outcome, deadline, config in tracks:
            connection.execute(
                "INSERT INTO track(id,portfolio_id,code,title,weight,outcome_definition,deadline,config_json) "
                "VALUES(?,?,?,?,?,?,?,?)",
                (track_id, PORTFOLIO_ID, code, title, weight, outcome, deadline, _json(config)),
            )
        milestones = (
            ("m-2026-09", "2026-08-31", "2026-09-27", "4 周灰度试运行", [
                "资料档案与真实题源基线", "4 次可回退周复盘", "校准 22–31 小时深度学习容量"
            ]),
            ("m-2026-10", "2026-09-28", "2026-10-31", "建立课程与训练证据", [
                "三门课考核档案经确认", "数学分析/高等代数/遍历论/抽代滚动训练"
            ]),
            ("m-2026-11", "2026-11-01", "2026-11-30", "形成稳定检索练习节奏", [
                "真实题源训练有可比记录", "按课程风险重新分配专业课资源"
            ]),
            ("m-2026-12-2027-01", "2026-12-01", "2027-01-31", "保护课程总评并完成遍历论交流包", [
                "按真实考试日期保护三门总评", "3–5 页笔记", "20–30 分钟讲解", "一页问题单"
            ]),
            ("m-2027-02-04", "2027-02-01", "2027-04-30", "春季选拔与导师交流准备", [
                "根据正式通知准备申请材料", "限时笔试", "只生成导师邮件草稿"
            ]),
            ("m-2027-05-07", "2027-05-01", "2027-07-31", "夏令营与考核", [
                "按当年正式通知调整报名与考核计划"
            ]),
            ("m-2027-08-09", "2027-08-01", "2027-09-30", "九月推免备用路线与最终核验", [
                "材料核验", "笔试和面试最终状态", "备用路线"
            ]),
        )
        for order, (milestone_id, start, end, title, acceptance) in enumerate(milestones, 1):
            connection.execute(
                "INSERT INTO milestone(id,track_id,period_start,period_end,title,acceptance_json,sort_order) "
                "VALUES(?,NULL,?,?,?,?,?)",
                (milestone_id, start, end, title, _json(acceptance), order),
            )
        self._seed_trial_week(connection, now)
        self._seed_sources(connection)
        self._create_version(connection, "初始化四轨道与 4 周试运行", "seed", [], "system")

    def _seed_trial_week(self, connection: sqlite3.Connection, now: str) -> None:
        # 1,590 minutes = 26.5 hours.  Each item is at most one weekday cap so
        # the recommendation engine can place it without inventing long
        # uninterrupted sessions.
        rows = (
            ("w1-c-p1", "track-courses", "概率论：课程基线检索练习（第一组）", 120, 5, 1),
            ("w1-c-p2", "track-courses", "概率论：整理错因并做第二组检索练习", 90, 5, 2),
            ("w1-c-f1", "track-courses", "泛函分析：课程基线检索练习（第一组）", 120, 5, 3),
            ("w1-c-f2", "track-courses", "泛函分析：整理错因并做第二组检索练习", 90, 5, 4),
            ("w1-c-d1", "track-courses", "微分几何：课程基线检索练习（第一组）", 120, 5, 5),
            ("w1-c-d2", "track-courses", "微分几何：整理错因并做第二组检索练习", 96, 5, 6),
            ("w1-e-1", "track-amss-exam", "数学所真实题源：限时基线（第一段）", 180, 5, 7),
            ("w1-e-2", "track-amss-exam", "数学所真实题源：订正与知识缺口归档", 138, 5, 8),
            ("w1-t-1", "track-ergodic", "遍历论：确认教材后完成首轮核心阅读", 180, 5, 9),
            ("w1-t-2", "track-ergodic", "遍历论：闭卷复述定义与关键证明策略", 180, 5, 10),
            ("w1-t-3", "track-ergodic", "遍历论：真实习题与待讨论问题记录", 117, 5, 11),
            ("w1-a-1", "track-algebra", "抽象代数：真实题组书面基线与口头复述", 159, 5, 12),
        )
        dates = self._recommend_dates([(row[0], row[3]) for row in rows], date(2026, 8, 31))
        for item_id, track_id, title, minutes, value, order in rows:
            connection.execute(
                "INSERT INTO plan_item(id,track_id,milestone_id,week_start,title,description,deep_minutes,"
                "recommended_date,status,value_score,material_required,material_status,sort_order,created_at,updated_at) "
                "VALUES(?,?,?, ?,?,?,?,?,'planned',?,1,'pending',?,?,?)",
                (
                    item_id,
                    track_id,
                    "m-2026-09",
                    "2026-08-31",
                    title,
                    "首周只做基线；具体章节或题组必须来自已授权资料，资料不足时显示待核验。",
                    minutes,
                    dates[item_id],
                    value,
                    order,
                    now,
                    now,
                ),
            )
        for week_number in range(2, 5):
            week = date(2026, 8, 31) + timedelta(days=7 * (week_number - 1))
            rolling = [
                (
                    item_id.replace("w1-", f"w{week_number}-"),
                    minutes,
                )
                for item_id, _, _, minutes, _, _ in rows
            ]
            dates = self._recommend_dates(rolling, week)
            for item_id, track_id, title, minutes, value, order in rows:
                next_id = item_id.replace("w1-", f"w{week_number}-")
                next_title = re.sub(
                    r"（第一组）|：订正与知识缺口归档|：确认教材后完成首轮核心阅读|：闭卷复述定义与关键证明策略|：真实习题与待讨论问题记录|：真实题组书面基线与口头复述",
                    "",
                    title,
                )
                next_title = f"第 {week_number} 周滚动 · {next_title}"
                connection.execute(
                    "INSERT INTO plan_item(id,track_id,milestone_id,week_start,title,description,deep_minutes,"
                    "recommended_date,status,value_score,material_required,material_status,sort_order,created_at,updated_at) "
                    "VALUES(?,?,?, ?,?,?,?,?,'planned',?,1,'pending',?,?,?)",
                    (
                        next_id,
                        track_id,
                        "m-2026-09",
                        week.isoformat(),
                        next_title,
                        "根据上一周证据滚动细化；Goal Agent 可在同月内调整推荐日、分钟数和拆分，资料不足时保持待核验。",
                        minutes,
                        dates[next_id],
                        value,
                        order,
                        now,
                        now,
                    ),
                )

    @staticmethod
    def _seed_sources(connection: sqlite3.Connection) -> None:
        sources = (
            ("src-amss-spring-2026", "official", "A", "https://amss.cas.cn/admission/sszs/tzgg/202503/t20250328_7792779.html", "2026级春季选拔通知", "往届参考"),
            ("src-amss-summer-2026", "official", "A", "https://amss.cas.cn/admission/sszs/tzgg/202605/t20260529_8211015.html", "2026年数学夏令营公告", "往届参考"),
            ("src-amss-sep-2025", "official", "A", "https://amss.cas.cn/admission/zsxm/9ytm/202509/t20250901_7950878.html", "九月推免通知", "往届参考"),
            ("src-he-weikun", "official", "A", "http://homepage.amss.ac.cn/research/homePage/17902e3d211d45d7b099d774bbd98463/myHomePage.html", "何伟鲲官方主页", "待刷新"),
            ("paper-harkin-2016", "research", "peer_reviewed", "https://doi.org/10.1037/bul0000025", "Harkin et al. progress monitoring meta-analysis", "已引用"),
            ("paper-gollwitzer-1999", "research", "peer_reviewed", "https://doi.org/10.1037/0003-066X.54.7.493", "Gollwitzer implementation intentions", "已引用"),
            ("paper-patall-2008", "research", "peer_reviewed", "https://doi.org/10.1037/0033-2909.134.2.270", "Patall et al. choice and motivation", "已引用"),
            ("paper-dunlosky-2013", "research", "peer_reviewed", "https://doi.org/10.1177/1529100612453266", "Dunlosky et al. effective learning techniques", "已引用"),
            ("paper-roediger-2006", "research", "peer_reviewed", "https://doi.org/10.1111/j.1467-9280.2006.01693.x", "Roediger & Karpicke test-enhanced learning", "已引用"),
            ("paper-cepeda-2006", "research", "peer_reviewed", "https://doi.org/10.1037/0033-2909.132.3.354", "Cepeda et al. distributed practice", "已引用"),
        )
        for source_id, kind, grade, url, title, status in sources:
            connection.execute(
                "INSERT OR IGNORE INTO source_record(id,source_kind,grade,url,title,status,reference_only) VALUES(?,?,?,?,?,?,?)",
                (source_id, kind, grade, url, title, status, 1 if "往届" in status else 0),
            )

    @staticmethod
    def _recommend_dates(items: list[tuple[str, int]], start: date) -> dict[str, str]:
        if start.weekday() != 0:
            raise ValueError("week start must be Monday")
        caps = [180, 180, 180, 180, 180, 480, 480]
        minimums = [120, 120, 120, 120, 120, 360, 360]
        total = sum(minutes for _, minutes in items)
        if total < 1320 or total > 1860:
            raise ValueError("normal weekly deep plan must be between 22 and 31 hours")
        for _, minutes in items:
            if minutes <= 0 or minutes > 480:
                raise ValueError("plan item minutes must be between 1 and 480")
        ordered = sorted(items, key=lambda item: (-item[1], item[0]))
        used = [0] * 7
        assignment: dict[str, int] = {}

        def place(index: int) -> bool:
            remaining = sum(minutes for _, minutes in ordered[index:])
            required = sum(max(0, minimums[i] - used[i]) for i in range(7))
            if remaining < required:
                return False
            if index == len(ordered):
                return all(minimums[i] <= used[i] <= caps[i] for i in range(7))
            item_id, minutes = ordered[index]
            candidates = [i for i in range(7) if used[i] + minutes <= caps[i]]
            candidates.sort(key=lambda i: (-(minimums[i] - used[i]), used[i] / caps[i], i))
            seen: set[tuple[int, int]] = set()
            for chosen in candidates:
                signature = (caps[chosen], used[chosen])
                if signature in seen:
                    continue
                seen.add(signature)
                used[chosen] += minutes
                assignment[item_id] = chosen
                if place(index + 1):
                    return True
                used[chosen] -= minutes
                assignment.pop(item_id, None)
            return False

        if not place(0):
            raise ValueError("weekly plan cannot be placed inside daily capacity")
        return {
            item_id: (start + timedelta(days=assignment[item_id])).isoformat()
            for item_id, _ in items
        }

    def _current_version(self, connection: sqlite3.Connection) -> int:
        row = connection.execute("SELECT COALESCE(MAX(id),0) AS value FROM plan_version").fetchone()
        return int(row["value"] if row else 0)

    def _plan_snapshot(self, connection: sqlite3.Connection) -> dict[str, Any]:
        portfolio = dict(connection.execute("SELECT * FROM portfolio WHERE id=?", (PORTFOLIO_ID,)).fetchone())
        tracks = [dict(row) for row in connection.execute("SELECT * FROM track ORDER BY rowid")]
        milestones = [dict(row) for row in connection.execute("SELECT * FROM milestone WHERE archived=0 ORDER BY sort_order")]
        items = [dict(row) for row in connection.execute("SELECT * FROM plan_item WHERE archived=0 ORDER BY week_start,sort_order")]
        return {"portfolio": portfolio, "tracks": tracks, "milestones": milestones, "plan_items": items}

    def _create_version(
        self,
        connection: sqlite3.Connection,
        reason: str,
        trigger: str,
        changes: list[dict[str, Any]],
        actor: str,
        *,
        rollback_of: int | None = None,
    ) -> int:
        parent = self._current_version(connection) or None
        cursor = connection.execute(
            "INSERT INTO plan_version(created_at,reason,trigger,parent_version,snapshot_json,diff_json,actor,rollback_of) "
            "VALUES(?,?,?,?,?,?,?,?)",
            (
                self._now().isoformat(timespec="seconds"),
                _clean_text(reason, 500),
                trigger,
                parent,
                _json(self._plan_snapshot(connection)),
                _json(changes),
                actor,
                rollback_of,
            ),
        )
        return int(cursor.lastrowid)

    def _request_fields(self, payload: dict[str, Any]) -> tuple[str, int]:
        request_id = str(payload.get("request_id") or "")
        if not REQUEST_ID_RE.fullmatch(request_id):
            raise ValueError("request_id must be 8-100 safe characters")
        try:
            base = int(payload["base_plan_version"])
        except (KeyError, TypeError, ValueError):
            raise ValueError("base_plan_version is required") from None
        return request_id, base

    def _run_write(
        self,
        endpoint: str,
        payload: dict[str, Any],
        operation: Callable[[sqlite3.Connection, int], dict[str, Any]],
    ) -> dict[str, Any]:
        request_id, base = self._request_fields(payload)
        with self._lock, self._connect() as connection:
            previous = connection.execute("SELECT * FROM request_log WHERE request_id=?", (request_id,)).fetchone()
            if previous:
                if previous["endpoint"] != endpoint:
                    raise ValueError("request_id was already used for another endpoint")
                return _loads(previous["response_json"], {})
            connection.execute("BEGIN IMMEDIATE")
            current = self._current_version(connection)
            if base != current:
                connection.rollback()
                raise GoalAgentConflictError(current)
            try:
                response = operation(connection, current)
                response["plan_version"] = self._current_version(connection)
                connection.execute(
                    "INSERT INTO request_log VALUES(?,?,?,?,?)",
                    (request_id, endpoint, base, _json(response), self._now().isoformat(timespec="seconds")),
                )
                connection.commit()
                return response
            except Exception:
                connection.rollback()
                raise

    def ingest_material_exports(self) -> dict[str, Any]:
        index_path = self.paths.material_root / "materials" / "index.json"
        try:
            index = json.loads(index_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            return {"status": "missing", "document_count": 0, "indexed_chunk_count": 0}
        documents = index.get("documents") if isinstance(index, dict) else None
        if not isinstance(documents, list):
            return {"status": "invalid", "document_count": 0, "indexed_chunk_count": 0}
        indexed = 0
        with self._lock, self._connect() as connection:
            fts = connection.execute("SELECT value FROM meta WHERE key='fts5'").fetchone()
            if not fts or fts["value"] != "1":
                return {"status": "fts_unavailable", "document_count": len(documents), "indexed_chunk_count": 0}
            known = {row["id"]: row["sha256"] for row in connection.execute("SELECT id,sha256 FROM material_record")}
            active_ids: set[str] = set()
            for document in documents:
                if not isinstance(document, dict):
                    continue
                record_id = _clean_text(document.get("id"), 80)
                sha256 = _clean_text(document.get("sha256"), 64)
                relative = _clean_text(document.get("export_file"), 300)
                source_path = _clean_text(document.get("source_path"), 1000)
                title = _clean_text(document.get("title"), 300)
                if not record_id or not re.fullmatch(r"[0-9a-f]{64}", sha256) or not relative:
                    continue
                active_ids.add(record_id)
                if known.get(record_id) == sha256:
                    connection.execute("UPDATE material_record SET status='indexed' WHERE id=?", (record_id,))
                    continue
                target = (self.paths.material_root / "materials" / relative).resolve()
                root = (self.paths.material_root / "materials").resolve()
                if root not in target.parents or target.suffix != ".gz":
                    continue
                try:
                    with gzip.open(target, "rt", encoding="utf-8") as handle:
                        exported = json.load(handle)
                except (OSError, UnicodeDecodeError, json.JSONDecodeError):
                    continue
                chunks = exported.get("chunks") if isinstance(exported, dict) else []
                connection.execute("DELETE FROM material_fts WHERE record_id=?", (record_id,))
                for chunk in chunks if isinstance(chunks, list) else []:
                    if not isinstance(chunk, dict):
                        continue
                    content = str(chunk.get("text") or "")[:30000]
                    if not content.strip():
                        continue
                    connection.execute(
                        "INSERT INTO material_fts VALUES(?,?,?,?,?,?,?)",
                        (
                            record_id,
                            title,
                            content,
                            source_path,
                            int(chunk.get("page_start") or 1),
                            int(chunk.get("page_end") or chunk.get("page_start") or 1),
                            sha256,
                        ),
                    )
                    indexed += 1
                connection.execute(
                    "INSERT OR REPLACE INTO material_record(id,title,source_path,sha256,modified_at,page_count,status,indexed_at) "
                    "VALUES(?,?,?,?,?,?,?,?)",
                    (
                        record_id,
                        title,
                        source_path,
                        sha256,
                        document.get("modified_at"),
                        document.get("page_count"),
                        "indexed",
                        self._now().isoformat(timespec="seconds"),
                    ),
                )
            for row in connection.execute("SELECT id FROM material_record"):
                if row["id"] not in active_ids:
                    connection.execute("UPDATE material_record SET status='withdrawn' WHERE id=?", (row["id"],))
                    connection.execute("DELETE FROM material_fts WHERE record_id=?", (row["id"],))
            active_titles = " ".join(
                row["title"] for row in connection.execute(
                    "SELECT title FROM material_record WHERE status='indexed'"
                )
            )
            readiness = {
                "track-courses": any(course in active_titles for course in COURSES),
                "track-amss-exam": any(word in active_titles for word in ("数学所", "数学分析", "高等代数")),
                "track-ergodic": "遍历" in active_titles,
                "track-algebra": any(word in active_titles for word in ("抽象代数", "抽代")),
            }
            for track_id, ready in readiness.items():
                connection.execute(
                    "UPDATE plan_item SET material_status=? WHERE track_id=? AND material_required=1",
                    ("ready" if ready else "pending", track_id),
                )
        return {"status": "ok", "document_count": len(documents), "indexed_chunk_count": indexed}

    def search_materials(self, query: str, limit: int = 6) -> list[dict[str, Any]]:
        terms = [term for term in re.findall(r"[\w\u4e00-\u9fff]{2,}", query)[:8]]
        if not terms:
            return []
        expression = " OR ".join(f'"{term.replace(chr(34), "")}"' for term in terms)
        with self._connect() as connection:
            fts = connection.execute("SELECT value FROM meta WHERE key='fts5'").fetchone()
            if not fts or fts["value"] != "1":
                return []
            try:
                rows = connection.execute(
                    "SELECT record_id,title,snippet(material_fts,2,'[',']','…',18) AS snippet,"
                    "source_path,page_start,page_end,sha256 FROM material_fts "
                    "WHERE material_fts MATCH ? ORDER BY rank LIMIT ?",
                    (expression, max(1, min(limit, 12))),
                ).fetchall()
            except sqlite3.OperationalError:
                return []
        return [dict(row) for row in rows]

    def _events(self, connection: sqlite3.Connection, track_id: str | None = None) -> list[dict[str, Any]]:
        query = "SELECT * FROM evidence_event"
        parameters: tuple[Any, ...] = ()
        if track_id:
            query += " WHERE track_id=?"
            parameters = (track_id,)
        query += " ORDER BY occurred_at,id"
        result = []
        for row in connection.execute(query, parameters):
            item = dict(row)
            item["payload"] = _loads(item.pop("payload_json", "{}"), {})
            result.append(item)
        return result

    def _track_metrics(self, connection: sqlite3.Connection, track: dict[str, Any], today: date) -> dict[str, Any]:
        events = self._events(connection, track["id"])
        items = [dict(row) for row in connection.execute(
            "SELECT * FROM plan_item WHERE track_id=? AND archived=0 ORDER BY week_start,sort_order",
            (track["id"],),
        )]
        planned = sum(max(0, int(item["deep_minutes"])) for item in items)
        completed_ids = {event["plan_item_id"] for event in events if event["plan_item_id"] and event["evidence_type"] in {"completed", "task_completed"}}
        completed_minutes = sum(int(item["deep_minutes"]) for item in items if item["id"] in completed_ids or item["status"] == "completed")
        actual_minutes = sum(int(event["deep_minutes"] or 0) for event in events)
        due = [item for item in items if item.get("recommended_date") and item["recommended_date"] <= today.isoformat()]
        due_completed = [item for item in due if item["status"] == "completed" or item["id"] in completed_ids]
        week_minutes: dict[str, int] = {}
        for event in events:
            if not event.get("deep_minutes"):
                continue
            try:
                event_day = date.fromisoformat(str(event["occurred_at"])[:10])
            except ValueError:
                continue
            key = _week_start(event_day).isoformat()
            week_minutes[key] = week_minutes.get(key, 0) + int(event["deep_minutes"])
        comparable_track_weeks = [value for _, value in sorted(week_minutes.items()) if value > 0]
        track_forecast = round(sum(comparable_track_weeks[-2:]) / min(2, len(comparable_track_weeks))) if comparable_track_weeks else None
        quantitative = sum(
            1 for event in events
            if event.get("score") is not None or event.get("completed_units") is not None or event.get("deep_minutes")
        )
        confidence = "high" if quantitative >= 6 and len(comparable_track_weeks) >= 3 else "medium" if quantitative >= 3 else "low" if quantitative else "unknown"
        common = {
            "content_coverage": {
                "completed_deep_minutes": completed_minutes,
                "planned_deep_minutes": planned,
                "ratio": round(completed_minutes / planned, 3) if planned else None,
            },
            "actual_deep_minutes": actual_minutes,
            "evidence_count": len(events),
            "weekly_execution": {
                "due_items": len(due),
                "completed_items": len(due_completed),
                "rate": round(len(due_completed) / len(due), 3) if due else None,
            },
            "throughput_forecast": {
                "status": "known" if len(comparable_track_weeks) >= 3 else "unknown",
                "comparable_weeks": len(comparable_track_weeks),
                "weekly_minutes": track_forecast if len(comparable_track_weeks) >= 3 else None,
            },
            "evidence_confidence": confidence,
        }
        code = track["code"]
        if code == "courses":
            course_results: dict[str, Any] = {}
            for course in COURSES:
                selected = [event for event in events if event["payload"].get("course") == course]
                course_results[course] = course_grade_scenario(selected)
                course_results[course]["profile_complete"] = any(
                    all(event["payload"].get(key) for key in ("teacher", "textbook", "assessment_weights", "exam_date"))
                    for event in selected
                )
            known = sum(1 for value in course_results.values() if value["state"] != "unknown")
            status = "unknown" if known < 3 else (
                "at_risk" if any(value["state"] == "at_risk" for value in course_results.values()) else "on_track"
            )
            return {**common, "status": status, "course_scenarios": course_results, "mastery": "待课程考核资料核验" if known < 3 else "按已确认成绩情景计算"}
        if code == "amss_exam":
            exam = consecutive_exam_passes(events)
            status = "achieved" if exam["criterion_met"] else ("unknown" if exam["attempt_count"] < 3 else "at_risk")
            return {**common, "status": status, "mastery": exam}
        if code == "ergodic":
            deliverables = {
                "reading_scope_confirmed": any(event["evidence_type"] == "ergodic_scope_confirmed" for event in events),
                "note_3_to_5_pages": any(event["evidence_type"] == "ergodic_note" and 3 <= float(event["completed_units"] or 0) <= 5 for event in events),
                "talk_20_to_30_minutes": any(event["evidence_type"] == "ergodic_talk" and 20 <= float(event["completed_units"] or 0) <= 30 for event in events),
                "question_sheet": any(event["evidence_type"] == "ergodic_questions" for event in events),
            }
            met = sum(bool(value) for value in deliverables.values())
            status = "achieved" if met == len(deliverables) and today <= date(2027, 1, 31) else ("unknown" if not events else "on_track")
            return {**common, "status": status, "mastery": {"deliverables": deliverables, "met": met, "total": 4}}
        written = [event for event in events if event["evidence_type"] == "algebra_written"]
        tail = 0
        seen: set[str] = set()
        for event in reversed(written):
            maximum = event["max_score"] or 100
            rate = float(event["score"] or 0) / float(maximum) if maximum else 0
            source_id = str(event["source_id"] or "")
            if rate < 0.8 or not source_id or source_id in seen:
                break
            tail += 1
            seen.add(source_id)
        oral = [event for event in events if event["evidence_type"] == "algebra_oral"]
        oral_met = False
        oral_scores: dict[str, Any] = {}
        if oral:
            oral_scores = oral[-1]["payload"].get("oral_scores", {})
            oral_met = all(isinstance(oral_scores.get(key), (int, float)) and oral_scores[key] >= 4 for key in ("definition", "example", "strategy", "follow_up"))
        achieved = tail >= 3 and oral_met
        return {
            **common,
            "status": "achieved" if achieved else ("unknown" if not events else "on_track"),
            "mastery": {"written_streak": tail, "oral_scores": oral_scores, "oral_met": oral_met, "criterion_met": achieved},
        }

    def _throughput(self, connection: sqlite3.Connection, today: date) -> dict[str, Any]:
        start = today - timedelta(days=20)
        rows = connection.execute(
            "SELECT occurred_at,deep_minutes FROM evidence_event WHERE deep_minutes IS NOT NULL AND occurred_at>=?",
            (start.isoformat(),),
        ).fetchall()
        by_week: dict[str, int] = {}
        active_days: set[str] = set()
        for row in rows:
            try:
                day = date.fromisoformat(str(row["occurred_at"])[:10])
            except ValueError:
                continue
            by_week.setdefault(_week_start(day).isoformat(), 0)
            by_week[_week_start(day).isoformat()] += max(0, int(row["deep_minutes"] or 0))
            active_days.add(day.isoformat())
        comparable = [value for key, value in sorted(by_week.items()) if value > 0]
        if len(comparable) < 3:
            return {
                "status": "unknown",
                "comparable_weeks": len(comparable),
                "forecast_weekly_minutes": None,
                "sustainable_capacity": None,
                "active_days": len(active_days),
                "reason": "少于三周可比深度学习数据。",
            }
        recent_two = comparable[-2:]
        forecast = round(sum(recent_two) / len(recent_two))
        sustainable = round(_clamp(forecast, 1320, 1860))
        return {
            "status": "known",
            "comparable_weeks": len(comparable),
            "forecast_weekly_minutes": forecast,
            "sustainable_capacity": sustainable,
            "active_days": len(active_days),
            "reason": "按最近两周真实吞吐量估算，并限制在用户确认的 22–31 小时范围。",
        }

    def _execution(self, connection: sqlite3.Connection, today: date) -> dict[str, Any]:
        start = (today - timedelta(days=20)).isoformat()
        items = [dict(row) for row in connection.execute(
            "SELECT * FROM plan_item WHERE archived=0 AND week_start>=?", (start,)
        )]
        due = [item for item in items if item.get("recommended_date") and item["recommended_date"] <= today.isoformat()]
        complete = [item for item in due if item["status"] == "completed"]
        return {
            "status": "unknown" if len({_week_start(date.fromisoformat(item["week_start"])).isoformat() for item in due}) < 3 else "known",
            "due_items": len(due),
            "completed_items": len(complete),
            "rate": round(len(complete) / len(due), 3) if due else None,
        }

    def _metrics(self, connection: sqlite3.Connection, trigger: str) -> dict[str, Any]:
        today = self._now().date()
        tracks = []
        for row in connection.execute("SELECT * FROM track ORDER BY rowid"):
            track = dict(row)
            tracks.append({
                "id": track["id"],
                "code": track["code"],
                "title": track["title"],
                "weight": track["weight"],
                "outcome_definition": track["outcome_definition"],
                "deadline": track["deadline"],
                **self._track_metrics(connection, track, today),
            })
        return {
            "generated_at": self._now().isoformat(timespec="seconds"),
            "trigger": trigger,
            "tracks": tracks,
            "throughput": self._throughput(connection, today),
            "execution": self._execution(connection, today),
        }

    def _save_progress(self, connection: sqlite3.Connection, trigger: str) -> dict[str, Any]:
        metrics = self._metrics(connection, trigger)
        connection.execute(
            "INSERT INTO progress_snapshot VALUES(?,?,?,?,?)",
            (
                uuid.uuid4().hex,
                metrics["generated_at"],
                trigger,
                self._current_version(connection),
                _json(metrics),
            ),
        )
        return metrics

    def _material_state(self, connection: sqlite3.Connection) -> dict[str, Any]:
        documents = [dict(row) for row in connection.execute(
            "SELECT id,title,source_path,sha256,modified_at,page_count,status,indexed_at FROM material_record ORDER BY title"
        )]
        gaps = [
            "概率论：教师、教材、大纲、考核比例、考试日期",
            "泛函分析：教师、教材、大纲、考核比例、考试日期",
            "微分几何：教师、教材、大纲、考核比例、考试日期",
            "数学所笔试：至少三份可区分的真实题源",
            "遍历论：双方确认的教材与章节范围",
            "抽象代数：真实书面题组与口头模拟题库",
            "2028 级正式选拔/夏令营/九月推免通知（发布后替换往届参考）",
        ]
        return {
            "manifest_path": "非笔记内容/任务计划/目标模式资料清单.md",
            "documents": documents,
            "gaps": gaps,
            "status": "ready" if documents else "awaiting_authorization",
        }

    def _reconcile_task_links(self, connection: sqlite3.Connection, task_state: dict[str, Any] | None) -> None:
        if not isinstance(task_state, dict):
            return
        tasks = task_state.get("tasks") if isinstance(task_state.get("tasks"), dict) else {}
        ids = {
            task.get("task_id")
            for group in tasks.values()
            for task in group if isinstance(group, list) and isinstance(task, dict)
        }
        completed = task_state.get("completed_recent") or task_state.get("completed_today") or []
        completed_ids = {item.get("task_id") for item in completed if isinstance(item, dict)}
        now = self._now().isoformat(timespec="seconds")
        for row in connection.execute("SELECT * FROM plan_item_task"):
            if row["task_id"] in completed_ids:
                connection.execute("UPDATE plan_item_task SET sync_status='completed',synced_at=COALESCE(synced_at,?) WHERE plan_item_id=?", (now, row["plan_item_id"]))
                connection.execute("UPDATE plan_item SET status='completed',updated_at=? WHERE id=?", (now, row["plan_item_id"]))
            elif row["task_id"] in ids and row["sync_status"] == "queued":
                connection.execute("UPDATE plan_item_task SET sync_status='synced',synced_at=? WHERE plan_item_id=?", (now, row["plan_item_id"]))

    def state(self, task_state: dict[str, Any] | None = None) -> dict[str, Any]:
        self.ingest_material_exports()
        with self._lock, self._connect() as connection:
            self._reconcile_task_links(connection, task_state)
            portfolio = dict(connection.execute("SELECT * FROM portfolio WHERE id=?", (PORTFOLIO_ID,)).fetchone())
            latest = connection.execute("SELECT * FROM progress_snapshot ORDER BY generated_at DESC LIMIT 1").fetchone()
            metrics = _loads(latest["metrics_json"], {}) if latest else self._metrics(connection, "state")
            current_week = _week_start(self._now().date()).isoformat()
            has_current = connection.execute(
                "SELECT 1 FROM plan_item WHERE archived=0 AND week_start=? LIMIT 1",
                (current_week,),
            ).fetchone()
            if not has_current:
                upcoming = connection.execute(
                    "SELECT MIN(week_start) AS week_start FROM plan_item WHERE archived=0 AND week_start>=?",
                    (current_week,),
                ).fetchone()
                if upcoming and upcoming["week_start"]:
                    current_week = upcoming["week_start"]
            items = [dict(row) for row in connection.execute(
                "SELECT p.*,t.code AS track_code,t.title AS track_title,pt.task_id,pt.sync_status,pt.mutation_id "
                "FROM plan_item p JOIN track t ON t.id=p.track_id "
                "LEFT JOIN plan_item_task pt ON pt.plan_item_id=p.id "
                "WHERE p.archived=0 AND p.week_start=? ORDER BY p.sort_order",
                (current_week,),
            )]
            approvals = [
                {**dict(row), "evidence": _loads(row["evidence_json"], []), "patch": _loads(row["patch_json"], {})}
                for row in connection.execute("SELECT * FROM approval_request WHERE status='pending' ORDER BY created_at DESC")
            ]
            sources = [dict(row) for row in connection.execute(
                "SELECT id,source_kind,grade,url,title,published_at,fetched_at,status,reference_only FROM source_record ORDER BY source_kind,grade,title"
            )]
            chats = [dict(row) for row in connection.execute(
                "SELECT id,role,content,created_at FROM chat_message ORDER BY created_at DESC LIMIT 30"
            )]
            chats.reverse()
            return {
                "schema_version": SCHEMA_VERSION,
                "plan_version": self._current_version(connection),
                "generated_at": self._now().isoformat(timespec="seconds"),
                "portfolio": portfolio,
                "tracks": metrics.get("tracks", []),
                "throughput": metrics.get("throughput", {}),
                "execution": metrics.get("execution", {}),
                "current_week": {"week_start": current_week, "items": items, "deep_minutes": sum(item["deep_minutes"] for item in items)},
                "materials": self._material_state(connection),
                "approvals": approvals,
                "sources": sources,
                "chat_messages": chats,
                "tavily": {
                    "configured": self._tavily_configured(),
                    "credential_policy": "复用 Codex Tavily MCP 的同一 API 密钥；Pi 只从私有环境文件读取，不保存到仓库。",
                },
                "boundaries": {
                    "next_action_is_separate": True,
                    "obsidian_writer": "desktop_plugin_only",
                    "automatic": ["同月周任务", "推荐日", "任务拆分", "低价值事项顺序"],
                    "approval_required": ["总目标", "截止日期", "资源权重", "每日容量范围", "重大跨月调整"],
                },
            }

    def plan(self) -> dict[str, Any]:
        with self._connect() as connection:
            milestones = []
            for row in connection.execute("SELECT * FROM milestone WHERE archived=0 ORDER BY sort_order"):
                item = dict(row)
                item["acceptance"] = _loads(item.pop("acceptance_json"), [])
                milestones.append(item)
            weeks = []
            for row in connection.execute(
                "SELECT week_start,SUM(deep_minutes) AS minutes,COUNT(*) AS item_count FROM plan_item "
                "WHERE archived=0 GROUP BY week_start ORDER BY week_start"
            ):
                weeks.append(dict(row))
            versions = []
            for row in connection.execute(
                "SELECT id,created_at,reason,trigger,parent_version,diff_json,actor,rollback_of "
                "FROM plan_version ORDER BY id DESC LIMIT 30"
            ):
                item = dict(row)
                item["changes"] = _loads(item.pop("diff_json"), [])
                versions.append(item)
            return {"plan_version": self._current_version(connection), "milestones": milestones, "weeks": weeks, "versions": versions}

    def _auto_adjust_short_term(self, connection: sqlite3.Connection) -> list[dict[str, Any]]:
        """Fit the active same-month week to observed sustainable throughput.

        This never changes the user-confirmed 22–31 hour range.  It also never
        rewrites an item whose day was already accepted into task-sync.
        """
        today = self._now().date()
        throughput = self._throughput(connection, today)
        target = throughput.get("sustainable_capacity")
        if throughput.get("status") != "known" or not isinstance(target, int):
            return []
        monday = _week_start(today)
        row = connection.execute(
            "SELECT MIN(week_start) AS value FROM plan_item WHERE archived=0 AND week_start>=?",
            (monday.isoformat(),),
        ).fetchone()
        if not row or not row["value"]:
            return []
        week_text = str(row["value"])
        if week_text[:7] != today.isoformat()[:7]:
            return []
        items = [dict(item) for item in connection.execute(
            "SELECT * FROM plan_item WHERE archived=0 AND week_start=? ORDER BY value_score,sort_order",
            (week_text,),
        )]
        current_total = sum(int(item["deep_minutes"]) for item in items)
        target = int(_clamp(target, 1320, 1860))
        if abs(current_total - target) < 40:
            return []
        changes: list[dict[str, Any]] = []
        remaining = target - current_total
        candidates = [item for item in items if not item["accepted_date"] and item["status"] != "completed" and int(item["auto_adjustable"])]
        if remaining < 0:
            for item in candidates:
                reducible = max(0, int(item["deep_minutes"]) - 40)
                amount = min(reducible, -remaining)
                if amount <= 0:
                    continue
                after = int(item["deep_minutes"]) - amount
                connection.execute("UPDATE plan_item SET deep_minutes=?,updated_at=? WHERE id=?", (after, self._now().isoformat(timespec="seconds"), item["id"]))
                changes.append({"plan_item_id": item["id"], "field": "deep_minutes", "before": item["deep_minutes"], "after": after, "reason": "按最近两周真实吞吐量收缩低价值承诺，不滚入全部欠账"})
                remaining += amount
                if remaining >= 0:
                    break
        else:
            for item in sorted(candidates, key=lambda value: (-int(value["value_score"]), int(value["sort_order"]))):
                day_text = item["recommended_date"]
                if not day_text:
                    continue
                day = date.fromisoformat(day_text)
                cap = 180 if day.weekday() < 5 else 480
                spare_day = cap - self._day_load(connection, day_text, exclude_id=item["id"]) - int(item["deep_minutes"])
                amount = min(max(0, spare_day), max(0, 480 - int(item["deep_minutes"])), remaining)
                if amount <= 0:
                    continue
                after = int(item["deep_minutes"]) + amount
                connection.execute("UPDATE plan_item SET deep_minutes=?,updated_at=? WHERE id=?", (after, self._now().isoformat(timespec="seconds"), item["id"]))
                changes.append({"plan_item_id": item["id"], "field": "deep_minutes", "before": item["deep_minutes"], "after": after, "reason": "按最近两周真实吞吐量增加高价值承诺"})
                remaining -= amount
                if remaining <= 0:
                    break
        final_total = connection.execute(
            "SELECT SUM(deep_minutes) AS total FROM plan_item WHERE archived=0 AND week_start=?",
            (week_text,),
        ).fetchone()["total"] or 0
        if not 1320 <= int(final_total) <= 1860:
            raise ValueError("automatic adjustment would leave the confirmed weekly range")
        return changes

    def feedback(self, payload: dict[str, Any]) -> dict[str, Any]:
        def operation(connection: sqlite3.Connection, current: int) -> dict[str, Any]:
            track_id = _clean_text(payload.get("track_id"), 80)
            if not connection.execute("SELECT 1 FROM track WHERE id=?", (track_id,)).fetchone():
                raise ValueError("unknown track_id")
            plan_item_id = _clean_text(payload.get("plan_item_id"), 80) or None
            if plan_item_id and not connection.execute("SELECT 1 FROM plan_item WHERE id=?", (plan_item_id,)).fetchone():
                raise ValueError("unknown plan_item_id")
            evidence_type = _clean_text(payload.get("evidence_type") or "progress_update", 80)
            occurred_at = str(payload.get("occurred_at") or self._now().isoformat(timespec="seconds"))
            try:
                datetime.fromisoformat(occurred_at.replace("Z", "+00:00"))
            except ValueError:
                raise ValueError("occurred_at must be ISO-8601") from None
            deep_minutes = payload.get("deep_minutes")
            if deep_minutes not in (None, ""):
                deep_minutes = int(deep_minutes)
                if deep_minutes < 0 or deep_minutes > 1440:
                    raise ValueError("deep_minutes must be between 0 and 1440")
            difficulty = payload.get("difficulty")
            confidence = payload.get("confidence")
            for label, value in (("difficulty", difficulty), ("confidence", confidence)):
                if value not in (None, "") and int(value) not in range(1, 6):
                    raise ValueError(f"{label} must be between 1 and 5")
            source_id = _clean_text(payload.get("source_id"), 160) or None
            event_id = "ev-" + uuid.uuid4().hex
            event_payload = payload.get("details") if isinstance(payload.get("details"), dict) else {}
            connection.execute(
                "INSERT INTO evidence_event VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    event_id,
                    track_id,
                    plan_item_id,
                    evidence_type,
                    occurred_at,
                    deep_minutes,
                    float(payload["completed_units"]) if payload.get("completed_units") not in (None, "") else None,
                    float(payload["total_units"]) if payload.get("total_units") not in (None, "") else None,
                    float(payload["score"]) if payload.get("score") not in (None, "") else None,
                    float(payload["max_score"]) if payload.get("max_score") not in (None, "") else None,
                    source_id,
                    int(difficulty) if difficulty not in (None, "") else None,
                    int(confidence) if confidence not in (None, "") else None,
                    _clean_text(payload.get("blocked_reason"), 1000) or None,
                    _clean_text(payload.get("change_note"), 2000) or None,
                    _json(event_payload),
                    self._now().isoformat(timespec="seconds"),
                ),
            )
            changes: list[dict[str, Any]] = []
            status = str(payload.get("status") or "").strip()
            if plan_item_id and status in {"planned", "in_progress", "blocked", "completed"}:
                before = connection.execute("SELECT status FROM plan_item WHERE id=?", (plan_item_id,)).fetchone()["status"]
                if before != status:
                    connection.execute("UPDATE plan_item SET status=?,updated_at=? WHERE id=?", (status, self._now().isoformat(timespec="seconds"), plan_item_id))
                    changes.append({"plan_item_id": plan_item_id, "field": "status", "before": before, "after": status, "reason": "用户进度反馈"})
            requested_change = payload.get("requested_change")
            approval_id = None
            if isinstance(requested_change, dict) and requested_change:
                major = sorted(set(requested_change) & MAJOR_CHANGE_KEYS)
                if major:
                    approval_id = "approval-" + uuid.uuid4().hex
                    connection.execute(
                        "INSERT INTO approval_request VALUES(?,?,?,?,?,?,?,?,?,?)",
                        (
                            approval_id,
                            self._now().isoformat(timespec="seconds"),
                            "pending",
                            ",".join(major),
                            _clean_text(payload.get("change_note") or "用户反馈触发重大计划变更", 500),
                            _json([{"event_id": event_id}]),
                            _json(requested_change),
                            current,
                            None,
                            None,
                        ),
                    )
            changes.extend(self._auto_adjust_short_term(connection))
            if changes:
                self._create_version(connection, "根据进度反馈更新周任务状态", "feedback", changes, "goal_agent")
            metrics = self._save_progress(connection, "feedback")
            return {"ok": True, "event_id": event_id, "approval_request_id": approval_id, "changes": changes, "progress": metrics}

        return self._run_write("feedback", payload, operation)

    def _day_load(self, connection: sqlite3.Connection, day_text: str, exclude_id: str | None = None) -> int:
        query = "SELECT COALESCE(SUM(deep_minutes),0) AS minutes FROM plan_item WHERE archived=0 AND COALESCE(accepted_date,recommended_date)=?"
        parameters: list[Any] = [day_text]
        if exclude_id:
            query += " AND id<>?"
            parameters.append(exclude_id)
        row = connection.execute(query, tuple(parameters)).fetchone()
        return int(row["minutes"] if row else 0)

    def accept_day(
        self,
        plan_item_id: str,
        payload: dict[str, Any],
        enqueue_task: Callable[[dict[str, Any]], dict[str, Any]],
    ) -> dict[str, Any]:
        if not PLAN_ITEM_ID_RE.fullmatch(plan_item_id):
            raise ValueError("invalid plan item id")

        def operation(connection: sqlite3.Connection, current: int) -> dict[str, Any]:
            item = connection.execute(
                "SELECT p.*,t.title AS track_title FROM plan_item p JOIN track t ON t.id=p.track_id WHERE p.id=? AND p.archived=0",
                (plan_item_id,),
            ).fetchone()
            if not item:
                raise GoalAgentNotFoundError(plan_item_id)
            accepted_date = _parse_date(payload.get("date") or item["recommended_date"], required=True)
            accepted_day = date.fromisoformat(accepted_date)
            week = date.fromisoformat(item["week_start"])
            if not week <= accepted_day <= week + timedelta(days=6):
                raise ValueError("accepted day must stay inside the plan item's week")
            cap = 180 if accepted_day.weekday() < 5 else 480
            load = self._day_load(connection, accepted_date, exclude_id=plan_item_id) + int(item["deep_minutes"])
            if load > cap:
                raise ValueError(f"accepted day would exceed its {cap}-minute deep-work cap")
            mapping = connection.execute("SELECT * FROM plan_item_task WHERE plan_item_id=?", (plan_item_id,)).fetchone()
            if mapping:
                return {"ok": True, "plan_item_id": plan_item_id, "task_id": mapping["task_id"], "sync_status": mapping["sync_status"], "accepted_date": item["accepted_date"]}
            task_id = "^g" + hashlib.sha256(plan_item_id.encode("utf-8")).hexdigest()[:10]
            tomatoes = max(1, math.ceil(int(item["deep_minutes"]) / 40))
            mutation_result = enqueue_task({
                "request_id": "goal-" + str(payload["request_id"]),
                "operation": "create",
                "task_id": task_id,
                "title": f"[目标模式] {item['title']}",
                "scheduled_date": accepted_date,
                "due_date": (week + timedelta(days=6)).isoformat(),
                "priority": "high" if int(item["value_score"]) >= 4 else "normal",
                "tomatoes_completed": 0,
                "tomatoes_total": tomatoes,
                "category": f"目标模式 · {item['track_title']}",
            })
            mutation = mutation_result.get("mutation") if isinstance(mutation_result, dict) else {}
            mutation_id = str((mutation or {}).get("mutation_id") or "")
            now = self._now().isoformat(timespec="seconds")
            connection.execute("UPDATE plan_item SET accepted_date=?,updated_at=? WHERE id=?", (accepted_date, now, plan_item_id))
            connection.execute(
                "INSERT INTO plan_item_task VALUES(?,?,?,?,?,NULL)",
                (plan_item_id, task_id, mutation_id, "queued", now),
            )
            changes = [{"plan_item_id": plan_item_id, "field": "accepted_date", "before": item["accepted_date"], "after": accepted_date, "reason": "用户确认推荐日"}]
            self._create_version(connection, "确认推荐日并排入任务同步队列", "accept_day", changes, "user")
            return {"ok": True, "plan_item_id": plan_item_id, "task_id": task_id, "mutation_id": mutation_id, "sync_status": "queued", "accepted_date": accepted_date, "changes": changes}

        return self._run_write(f"accept-day:{plan_item_id}", payload, operation)

    def _model(self, purpose: str, user_message: str, context: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
        _load_env_file(self.env_file)
        model = {
            **self.settings.get("model", {}),
            **self.settings.get("goal_agent_model", {}),
            **self.config.get("model", {}),
        }
        model.setdefault("name", "deepseek-v4-pro")
        model.setdefault("thinking", "enabled")
        model.setdefault("max_tokens", 4500)
        model.setdefault("timeout_seconds", 80)
        model.setdefault("retries", 1)
        default_system = (
            "你是独立的目标 Agent，不是 Next Action。你衡量长期目标距离、解释证据不足、"
            "调整月/周策略。禁止伪造课程考核、题源、成绩或招生规则。少于三周可比数据时必须说未知。"
            "你可以建议同月 plan item 的 recommended_date/deep_minutes/status，但总目标、截止日期、"
            "权重、每日容量或重大跨月移动只能放入 approval_request。"
            "只返回 JSON：{answer:string,plan_changes:list,approval_request:object|null,assessment:object}."
        )
        prompt_path = Path(
            self.config.get("prompt_path")
            or Path(__file__).resolve().parents[1] / "prompts" / "goal-agent.md"
        )
        try:
            system = prompt_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            system = default_system
        payload = _json({"purpose": purpose, "user_message": user_message, "context": context})
        return self._model_runner(model, [{"role": "system", "content": system}, {"role": "user", "content": payload}])

    def _apply_model_changes(self, connection: sqlite3.Connection, raw: Any) -> list[dict[str, Any]]:
        if not isinstance(raw, list):
            return []
        changes: list[dict[str, Any]] = []
        now_day = self._now().date()
        for patch in raw[:20]:
            if not isinstance(patch, dict):
                continue
            item_id = _clean_text(patch.get("plan_item_id"), 80)
            row = connection.execute("SELECT * FROM plan_item WHERE id=? AND archived=0", (item_id,)).fetchone()
            if not row or not int(row["auto_adjustable"]):
                continue
            updates: dict[str, Any] = {}
            recommended = patch.get("recommended_date")
            if recommended not in (None, ""):
                recommended = _parse_date(recommended, required=True)
                target = date.fromisoformat(recommended)
                week = date.fromisoformat(row["week_start"])
                if not week <= target <= week + timedelta(days=6):
                    continue
                if target.strftime("%Y-%m") != now_day.strftime("%Y-%m"):
                    continue
                cap = 180 if target.weekday() < 5 else 480
                if self._day_load(connection, recommended, exclude_id=item_id) + int(row["deep_minutes"]) > cap:
                    continue
                updates["recommended_date"] = recommended
            if patch.get("deep_minutes") not in (None, ""):
                minutes = int(patch["deep_minutes"])
                if not 40 <= minutes <= 480:
                    continue
                day_text = updates.get("recommended_date") or row["recommended_date"]
                if day_text:
                    target = date.fromisoformat(day_text)
                    cap = 180 if target.weekday() < 5 else 480
                    if self._day_load(connection, day_text, exclude_id=item_id) + minutes > cap:
                        continue
                updates["deep_minutes"] = minutes
            if patch.get("status") in {"planned", "in_progress", "blocked"}:
                updates["status"] = patch["status"]
            for field, after in updates.items():
                before = row[field]
                if before == after:
                    continue
                connection.execute(f"UPDATE plan_item SET {field}=?,updated_at=? WHERE id=?", (after, self._now().isoformat(timespec="seconds"), item_id))
                changes.append({"plan_item_id": item_id, "field": field, "before": before, "after": after, "reason": _clean_text(patch.get("reason"), 500) or "Goal Agent 策略调整"})
        # Reject the entire auto patch if it would change the user's normal
        # weekly range.  This is intentionally checked after field validation
        # and before a version is created.
        affected_weeks = {connection.execute("SELECT week_start FROM plan_item WHERE id=?", (change["plan_item_id"],)).fetchone()["week_start"] for change in changes}
        for week in affected_weeks:
            total = connection.execute("SELECT SUM(deep_minutes) AS total FROM plan_item WHERE archived=0 AND week_start=?", (week,)).fetchone()["total"] or 0
            if not 1320 <= int(total) <= 1860:
                raise ValueError("AI patch would move a normal week outside 22-31 hours")
        return changes

    def chat(self, payload: dict[str, Any]) -> dict[str, Any]:
        message = _clean_text(payload.get("message"), 4000)
        if not message:
            raise ValueError("message is required")
        context = self.state()
        context.pop("chat_messages", None)
        context["material_snippets"] = self.search_materials(message)
        model_error = None
        try:
            model_result, generation = self._model("chat", message, context)
        except Exception as error:
            model_result = {
                "answer": "我已记录这次沟通，但当前模型调用失败。确定性进度和计划版本仍可用；没有自动修改计划。",
                "plan_changes": [],
                "approval_request": None,
                "assessment": {"state": "unavailable"},
            }
            generation = {"status": "failed"}
            model_error = f"{type(error).__name__}: {error}"[:500]

        def operation(connection: sqlite3.Connection, current: int) -> dict[str, Any]:
            now = self._now().isoformat(timespec="seconds")
            user_id, assistant_id = "chat-" + uuid.uuid4().hex, "chat-" + uuid.uuid4().hex
            answer = _clean_text(model_result.get("answer"), 6000) or "没有生成可用回复。"
            connection.execute("INSERT INTO chat_message VALUES(?,?,?,?,?)", (user_id, "user", message, now, "{}"))
            changes = self._apply_model_changes(connection, model_result.get("plan_changes"))
            approval_id = None
            requested = model_result.get("approval_request")
            if isinstance(requested, dict) and requested:
                patch = requested.get("patch") if isinstance(requested.get("patch"), dict) else requested
                major = sorted(set(patch) & MAJOR_CHANGE_KEYS)
                if major:
                    approval_id = "approval-" + uuid.uuid4().hex
                    connection.execute(
                        "INSERT INTO approval_request VALUES(?,?,?,?,?,?,?,?,?,?)",
                        (approval_id, now, "pending", ",".join(major), _clean_text(requested.get("reason"), 500) or "Goal Agent 建议重大调整", _json(model_result.get("assessment") or {}), _json(patch), current, None, None),
                    )
            if changes:
                self._create_version(connection, "Goal Agent 根据沟通调整同月短期计划", "chat", changes, "goal_agent")
            metadata = {"generation": generation, "model_error": model_error, "changes": changes, "approval_request_id": approval_id}
            connection.execute("INSERT INTO chat_message VALUES(?,?,?,?,?)", (assistant_id, "assistant", answer, now, _json(metadata)))
            self._save_progress(connection, "chat")
            return {"ok": True, "message": {"id": assistant_id, "role": "assistant", "content": answer, "created_at": now}, "changes": changes, "approval_request_id": approval_id, "model_status": "failed" if model_error else "ok"}

        return self._run_write("chat", payload, operation)

    def review(self, payload: dict[str, Any], *, use_model: bool = True) -> dict[str, Any]:
        public_search = self.refresh_public_sources()
        context = self.state()
        context["public_search"] = {
            "status": public_search.get("status"),
            "result_count": len(public_search.get("results", [])),
        }
        model_result: dict[str, Any] = {"answer": "已完成确定性评估。", "plan_changes": [], "approval_request": None, "assessment": {}}
        generation: dict[str, Any] = {"status": "skipped"}
        model_error = None
        if use_model:
            try:
                model_result, generation = self._model("full_review", "评估当前距离、风险与本周/本月策略。", context)
            except Exception as error:
                model_error = f"{type(error).__name__}: {error}"[:500]

        def operation(connection: sqlite3.Connection, current: int) -> dict[str, Any]:
            changes = self._apply_model_changes(connection, model_result.get("plan_changes")) if use_model else []
            changes.extend(self._auto_adjust_short_term(connection))
            approval_id = None
            requested = model_result.get("approval_request")
            if isinstance(requested, dict) and requested:
                patch = requested.get("patch") if isinstance(requested.get("patch"), dict) else requested
                major = sorted(set(patch) & MAJOR_CHANGE_KEYS)
                if major:
                    approval_id = "approval-" + uuid.uuid4().hex
                    connection.execute(
                        "INSERT INTO approval_request VALUES(?,?,?,?,?,?,?,?,?,?)",
                        (approval_id, self._now().isoformat(timespec="seconds"), "pending", ",".join(major), _clean_text(requested.get("reason"), 500) or "周复盘建议重大调整", _json(model_result.get("assessment") or {}), _json(patch), current, None, None),
                    )
            if changes:
                self._create_version(connection, "完整复盘自动调整同月短期计划", "review", changes, "goal_agent")
            metrics = self._save_progress(connection, "review")
            return {"ok": True, "assessment": model_result.get("assessment") or {}, "summary": _clean_text(model_result.get("answer"), 5000), "changes": changes, "approval_request_id": approval_id, "progress": metrics, "generation": generation, "model_status": "failed" if model_error else ("ok" if use_model else "skipped"), "model_error": model_error, "public_search": public_search}

        return self._run_write("review", payload, operation)

    def approval_decision(self, approval_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        if not PLAN_ITEM_ID_RE.fullmatch(approval_id):
            raise ValueError("invalid approval id")

        def operation(connection: sqlite3.Connection, current: int) -> dict[str, Any]:
            row = connection.execute("SELECT * FROM approval_request WHERE id=?", (approval_id,)).fetchone()
            if not row:
                raise GoalAgentNotFoundError(approval_id)
            if row["status"] != "pending":
                return {"ok": True, "approval_id": approval_id, "status": row["status"], "changes": []}
            decision = str(payload.get("decision") or "")
            if decision not in {"approved", "rejected"}:
                raise ValueError("decision must be approved or rejected")
            changes: list[dict[str, Any]] = []
            if decision == "approved":
                patch = _loads(row["patch_json"], {})
                portfolio = connection.execute("SELECT * FROM portfolio WHERE id=?", (PORTFOLIO_ID,)).fetchone()
                mapping = {
                    "portfolio_title": ("title", str),
                    "target_date": ("target_date", str),
                    "capacity_min_minutes": ("capacity_min_minutes", int),
                    "capacity_max_minutes": ("capacity_max_minutes", int),
                }
                for key, (field, cast) in mapping.items():
                    if key not in patch:
                        continue
                    after = cast(patch[key])
                    if key == "target_date":
                        after = _parse_date(after, required=True)
                    if key.startswith("capacity_") and not 60 <= int(after) <= 4000:
                        raise ValueError("capacity change is outside safe bounds")
                    before = portfolio[field]
                    connection.execute(f"UPDATE portfolio SET {field}=?,updated_at=? WHERE id=?", (after, self._now().isoformat(timespec="seconds"), PORTFOLIO_ID))
                    changes.append({"field": key, "before": before, "after": after, "reason": row["reason"]})
                if isinstance(patch.get("track_weights"), dict):
                    weights = {code: float(patch["track_weights"].get(code, 0)) for code in TRACK_CODES}
                    if abs(sum(weights.values()) - 1.0) > 0.001 or any(value < 0 for value in weights.values()):
                        raise ValueError("track weights must be nonnegative and sum to 1")
                    for code, after in weights.items():
                        before = connection.execute("SELECT weight FROM track WHERE code=?", (code,)).fetchone()["weight"]
                        connection.execute("UPDATE track SET weight=? WHERE code=?", (after, code))
                        changes.append({"field": f"track_weights.{code}", "before": before, "after": after, "reason": row["reason"]})
                if isinstance(patch.get("track_deadline"), dict):
                    code = str(patch["track_deadline"].get("code") or "")
                    after = _parse_date(patch["track_deadline"].get("deadline"), required=True)
                    track = connection.execute("SELECT id,deadline FROM track WHERE code=?", (code,)).fetchone()
                    if not track:
                        raise ValueError("unknown track deadline code")
                    connection.execute("UPDATE track SET deadline=? WHERE id=?", (after, track["id"]))
                    changes.append({"field": f"track_deadline.{code}", "before": track["deadline"], "after": after, "reason": row["reason"]})
                if changes:
                    self._create_version(connection, "用户批准重大计划修改", "approval", changes, "user")
            connection.execute(
                "UPDATE approval_request SET status=?,decided_at=?,decision_note=? WHERE id=?",
                (decision, self._now().isoformat(timespec="seconds"), _clean_text(payload.get("note"), 500), approval_id),
            )
            self._save_progress(connection, "approval")
            return {"ok": True, "approval_id": approval_id, "status": decision, "changes": changes}

        return self._run_write(f"approval:{approval_id}", payload, operation)

    def rollback(self, version_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        def operation(connection: sqlite3.Connection, current: int) -> dict[str, Any]:
            row = connection.execute("SELECT snapshot_json FROM plan_version WHERE id=?", (version_id,)).fetchone()
            if not row:
                raise GoalAgentNotFoundError(str(version_id))
            snapshot = _loads(row["snapshot_json"], {})
            if not isinstance(snapshot, dict):
                raise ValueError("version snapshot is corrupt")
            before = self._plan_snapshot(connection)
            portfolio = snapshot.get("portfolio") if isinstance(snapshot.get("portfolio"), dict) else {}
            allowed_portfolio = ("title", "target_date", "capacity_min_minutes", "capacity_max_minutes", "capacity_baseline_minutes", "feature_enabled", "trial_ends_on")
            for field in allowed_portfolio:
                if field in portfolio:
                    connection.execute(f"UPDATE portfolio SET {field}=?,updated_at=? WHERE id=?", (portfolio[field], self._now().isoformat(timespec="seconds"), PORTFOLIO_ID))
            for track in snapshot.get("tracks", []):
                if isinstance(track, dict) and track.get("id"):
                    connection.execute("UPDATE track SET title=?,weight=?,outcome_definition=?,deadline=?,config_json=? WHERE id=?", (track["title"], track["weight"], track["outcome_definition"], track.get("deadline"), track.get("config_json", "{}"), track["id"]))
            milestone_ids = {item.get("id") for item in snapshot.get("milestones", []) if isinstance(item, dict)}
            if milestone_ids:
                placeholders = ",".join("?" for _ in milestone_ids)
                connection.execute(f"UPDATE milestone SET archived=1 WHERE id NOT IN ({placeholders})", tuple(milestone_ids))
            for item in snapshot.get("milestones", []):
                if not isinstance(item, dict):
                    continue
                connection.execute("UPDATE milestone SET track_id=?,period_start=?,period_end=?,title=?,acceptance_json=?,status=?,sort_order=?,archived=0 WHERE id=?", (item.get("track_id"), item["period_start"], item["period_end"], item["title"], item["acceptance_json"], item["status"], item["sort_order"], item["id"]))
            item_ids = {item.get("id") for item in snapshot.get("plan_items", []) if isinstance(item, dict)}
            if item_ids:
                placeholders = ",".join("?" for _ in item_ids)
                connection.execute(f"UPDATE plan_item SET archived=1 WHERE id NOT IN ({placeholders})", tuple(item_ids))
            for item in snapshot.get("plan_items", []):
                if not isinstance(item, dict):
                    continue
                connection.execute(
                    "UPDATE plan_item SET track_id=?,milestone_id=?,week_start=?,title=?,description=?,deep_minutes=?,recommended_date=?,accepted_date=?,status=?,value_score=?,material_required=?,material_status=?,auto_adjustable=?,sort_order=?,archived=0,updated_at=? WHERE id=?",
                    (item["track_id"], item.get("milestone_id"), item["week_start"], item["title"], item.get("description", ""), item["deep_minutes"], item.get("recommended_date"), item.get("accepted_date"), item["status"], item["value_score"], item["material_required"], item["material_status"], item["auto_adjustable"], item["sort_order"], self._now().isoformat(timespec="seconds"), item["id"]),
                )
            changes = [{"rollback_from": current, "rollback_to": version_id, "before_hash": hashlib.sha256(_json(before).encode()).hexdigest(), "after_hash": hashlib.sha256(_json(snapshot).encode()).hexdigest()}]
            new_version = self._create_version(connection, f"回退到计划版本 {version_id}", "rollback", changes, "user", rollback_of=version_id)
            self._save_progress(connection, "rollback")
            return {"ok": True, "rolled_back_to": version_id, "new_version": new_version, "changes": changes}

        return self._run_write(f"rollback:{version_id}", payload, operation)

    def _tavily_configured(self) -> bool:
        _load_env_file(self.paths.tavily_env)
        return bool(os.environ.get("TAVILY_API_KEY"))

    def tavily_search(self, query: str) -> dict[str, Any]:
        """Search only a fixed, non-personal research query through Tavily."""
        allowed = (
            query.startswith("site:amss.cas.cn ")
            or query.startswith("site:ucas.ac.cn ")
            or query.startswith("mathematics graduate admission ")
        )
        if not allowed or len(query) > 300:
            raise ValueError("Tavily query is outside the fixed public-information policy")
        _load_env_file(self.paths.tavily_env)
        key = os.environ.get("TAVILY_API_KEY")
        if not key:
            return {"status": "not_configured", "results": []}
        payload = json.dumps({"api_key": key, "query": query, "search_depth": "advanced", "max_results": 8, "include_raw_content": False}).encode("utf-8")
        request = Request("https://api.tavily.com/search", data=payload, method="POST", headers={"Content-Type": "application/json"})
        try:
            with urlopen(request, timeout=30) as response:
                data = json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, UnicodeDecodeError, json.JSONDecodeError) as error:
            return {"status": "failed", "error": f"{type(error).__name__}: {error}"[:300], "results": []}
        results = []
        for item in data.get("results", []) if isinstance(data, dict) else []:
            if not isinstance(item, dict):
                continue
            results.append({"title": _clean_text(item.get("title"), 300), "url": _clean_text(item.get("url"), 1000), "excerpt": _clean_text(item.get("content"), 1000)})
        return {"status": "ok", "results": results}

    def refresh_public_sources(self) -> dict[str, Any]:
        result = self.tavily_search(
            "site:amss.cas.cn 2028级 数学 推免 夏令营 春季选拔 招生通知"
        )
        if result.get("status") != "ok":
            return result
        fetched_at = self._now().isoformat(timespec="seconds")
        with self._lock, self._connect() as connection:
            for item in result.get("results", []):
                url = str(item.get("url") or "")
                title = _clean_text(item.get("title"), 300)
                excerpt = _clean_text(item.get("excerpt"), 1000)
                if not url or not title:
                    continue
                host = (urlparse(url).hostname or "").lower()
                official = host.endswith("cas.cn") or host.endswith("ucas.ac.cn")
                grade = "A" if official else "C"
                status = "官方搜索结果，待核验发布日期与适用年级" if official else "单一搜索结果，待两个独立来源互证"
                source_id = "web-" + hashlib.sha256(url.encode("utf-8")).hexdigest()[:24]
                connection.execute(
                    "INSERT INTO source_record(id,source_kind,grade,url,title,published_at,fetched_at,body_hash,excerpt,status,reference_only,metadata_json) "
                    "VALUES(?,?,?,?,?,NULL,?,?,?,?,?,?) "
                    "ON CONFLICT(id) DO UPDATE SET title=excluded.title,fetched_at=excluded.fetched_at,body_hash=excluded.body_hash,excerpt=excluded.excerpt,status=excluded.status,grade=excluded.grade",
                    (
                        source_id,
                        "official_search" if official else "experience_search",
                        grade,
                        url,
                        title,
                        fetched_at,
                        hashlib.sha256(excerpt.encode("utf-8")).hexdigest(),
                        excerpt,
                        status,
                        1,
                        _json({"provider": "Tavily", "query_policy": "fixed_public_only"}),
                    ),
                )
        return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a scheduled Goal Agent review")
    parser.add_argument("--settings", type=Path, default=Path("config/settings.json"))
    parser.add_argument("--env-file", type=Path, default=Path("/home/conrad/.config/activitywatch-advisor/env"))
    parser.add_argument("--review", action="store_true")
    parser.add_argument("--no-model", action="store_true")
    parser.add_argument("--notify", action="store_true")
    args = parser.parse_args()
    settings = json.loads(args.settings.read_text(encoding="utf-8"))
    agent = GoalAgent(Path(settings["output_root"]), settings, env_file=args.env_file)
    state = agent.state()
    if not args.review:
        print(json.dumps(state, ensure_ascii=False))
        return 0
    payload = {"request_id": "scheduled-" + uuid.uuid4().hex, "base_plan_version": state["plan_version"]}
    result = agent.review(payload, use_model=not args.no_model)
    if args.notify:
        _load_env_file(Path("/home/conrad/.config/activitywatch-advisor/ntfy.env"))
        try:
            from notifications.ntfy import send_notification

            progress = result.get("progress", {})
            risky = [track["title"] for track in progress.get("tracks", []) if track.get("status") in {"at_risk", "off_track"}]
            message = result.get("summary") or "周复盘已生成。"
            if risky:
                message += "\n需要关注：" + "、".join(risky)
            if result.get("approval_request_id"):
                message += "\n有一项重大调整等待确认。"
            send_notification(level=2 if risky else 1, policy_id="goal-agent-weekly-review", title="目标模式周复盘", message=message[:1800], priority="high" if risky else "default", tags=["dart"])
        except Exception:
            # A notification failure must never roll back the versioned review.
            pass
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
