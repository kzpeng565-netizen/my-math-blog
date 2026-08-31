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

from goal_model_client import request_goal_json
from course_schedule import schedule_view


SCHEMA_VERSION = 2
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
COURSE_IDS = {
    "概率论": "probability",
    "泛函分析": "functional-analysis",
    "微分几何": "differential-geometry",
}
COURSE_PROFILES: tuple[dict[str, Any], ...] = (
    {
        "id": "probability",
        "name": "概率论",
        "course_code": "B0111005H",
        "teacher": "施展",
        "credits": 4.0,
        "textbooks": [
            "Sheldon M. Ross《概率论基础教程》（原书第9版）",
            "A.H.施利亚耶夫《概率（第一卷）》",
            "A.H.施利亚耶夫《概率论习题集》",
        ],
        "assessment_weights": {
            "midterm": 0.30,
            "homework": 0.15,
            "thinking_problems": 0.15,
            "final": 0.40,
        },
        "nominal_hours": 64,
        "hours_detail": {"lecture": 80, "exercise": 40, "total": 120},
        "hours_warning": "课程页面标注 64 学时，但详细表为讲课 80 + 习题 40，共 120 学时；只作相对学习量参考。",
    },
    {
        "id": "functional-analysis",
        "name": "泛函分析",
        "course_code": "B0111011H",
        "teacher": "韩丕功",
        "credits": 4.0,
        "textbooks": [
            "H. Brezis《泛函分析：理论和应用》",
            "H. Brezis, Functional Analysis, Sobolev Spaces and Partial Differential Equations",
        ],
        "assessment_weights": {
            "midterm": 0.30,
            "final": 0.50,
            "coursework": 0.20,
        },
        "nominal_hours": 64,
        "hours_detail": {"lecture": 60, "exercise": 16, "total": 76},
        "hours_warning": "课程页面标注 64 学时，但六章详细分配合计讲课 60 + 习题 16，共 76 学时；只作相对学习量参考。",
    },
    {
        "id": "differential-geometry",
        "name": "微分几何",
        "course_code": "B0111006H",
        "teacher": "王晋民",
        "credits": 4.0,
        "textbooks": [
            "Kristopher Tapp, Differential Geometry of Curves and Surfaces",
            "彭家贵、陈卿《微分几何》第2版",
        ],
        "assessment_weights": {
            "midterm": 0.30,
            "final": 0.40,
            "coursework": 0.30,
        },
        "nominal_hours": 64,
        "hours_detail": {"lecture": 74, "exercise": 0, "total": 74},
        "hours_warning": "课程页面标注 64 学时，但六部分逐项合计为 74 学时；只作相对学习量参考。",
    },
)


def _units(
    course_id: str,
    chapters: tuple[tuple[str, tuple[str, ...]], ...],
) -> tuple[dict[str, Any], ...]:
    result: list[dict[str, Any]] = []
    order = 0
    for chapter_index, (chapter_title, sections) in enumerate(chapters, 1):
        for section_index, title in enumerate(sections, 1):
            order += 1
            result.append(
                {
                    "id": f"{course_id}-{chapter_index:02d}-{section_index:02d}",
                    "course_id": course_id,
                    "chapter_no": chapter_index,
                    "chapter_title": chapter_title,
                    "section_no": section_index,
                    "title": title,
                    "sort_order": order,
                }
            )
    return tuple(result)


COURSE_UNITS = (
    *_units(
        "probability",
        (
            ("组合分析", ("组合分析与计数基本法则", "排列与组合", "方程的整数解个数")),
            ("概率论公理", ("不确定性现象与概率论发展简史", "样本空间与事件", "柯尔莫果洛夫概率论公理及基本命题", "等可能样本空间及其理论刻画", "概率作为连续集函数", "可信性命题推理与概率论的贝叶斯公理")),
            ("条件概率和独立性", ("条件概率与贝叶斯公式", "柯尔莫果洛夫公理与贝叶斯公理的等价性", "事件独立性的两种定义及性质", "条件概率的概率性质与条件独立性")),
            ("可测空间及概率测度", ("无限种结局的概率模型", "代数、σ-代数与可测空间", "卡拉泰奥多里测度扩展定理")),
            ("常用可测空间上概率测度的构造", ("实直线 R 上 Borel 概率测度的构造", "R^n 上 Borel 概率测度的构造", "R^∞ 上 Borel 概率测度的构造", "R^T 上 Borel 概率测度的构造")),
            ("一般随机变量及其相关性质", ("随机变量与随机元", "勒贝格积分与数学期望", "数学期望的极限定理与常用不等式")),
            ("离散型和连续型随机变量", ("随机变量的数字特征", "典型离散型随机变量", "典型连续型随机变量")),
            ("随机变量的联合分布", ("联合分布函数", "独立随机变量及其和", "条件分布", "次序统计量与可交换随机变量")),
            ("数学期望的性质及其应用", ("估计复杂函数的界", "随机变量和的数字特征及其应用", "条件期望的性质及其应用", "预测与条件期望", "矩母函数与多元正态分布")),
            ("概率极限定理", ("切比雪夫不等式与弱大数定律", "中心极限定理", "强大数定律与其他概率不等式", "二项分布与泊松分布的概率误差界")),
            ("泊松过程、马尔可夫过程、熵与编码定理", ("泊松过程", "马尔可夫过程与搜索算法", "惊奇、不确定性及熵", "编码定理与熵")),
            ("随机模拟", ("模拟连续型随机变量", "模拟离散型随机变量", "方差缩减技术")),
        ),
    ),
    *_units(
        "functional-analysis",
        (
            ("Hahn–Banach 定理与共轭凸函数", ("Banach 空间与压缩映象原理", "Arzelà 定理", "Hahn–Banach 定理的解析与几何形式", "凸集分离", "Fenchel–Moreau 定理")),
            ("Banach–Steinhaus、开映射与闭图像", ("Baire 引理", "Banach–Steinhaus 定理", "开映射定理", "闭图像定理", "有界与无界线性算子、共轭算子")),
            ("弱拓扑、自反、可分与一致凸空间", ("弱拓扑与弱*拓扑", "Banach–Alaoglu–Bourbaki 定理", "自反与可分空间", "Kakutani 定理", "Milman–Pettis 定理")),
            ("函数空间", ("收敛定理与积分换序", "函数空间的可分性、自反性与对偶", "Fischer–Riesz 与 Riesz 表示定理", "M. Riesz–Fréchet–Kolmogorov 定理")),
            ("Hilbert 空间", ("Hilbert 空间、闭凸集投影与对偶", "Banach 不动点定理", "Lax–Milgram 定理", "Stampacchia 定理")),
            ("紧算子与谱分解", ("紧算子与自共轭算子", "Riesz–Fredholm 理论", "紧算子的谱", "自共轭紧算子的谱分解", "Fredholm 选择定理")),
        ),
    ),
    *_units(
        "differential-geometry",
        (
            ("平面曲线与空间曲线", ("平面曲线", "平面曲线例子", "平面曲线基本定理", "空间曲线", "空间曲线例子", "空间曲线基本定理", "曲线论的整体性结果")),
            ("曲面上的微积分", ("空间中的曲面", "曲面例子", "向量场、流与 Lie 导数", "微分形式与外微分计算", "微分形式的积分", "Stokes 定理", "de Rham 上同调")),
            ("空间中曲面的局部理论", ("第一、第二基本型", "主曲率、Gauss 曲率与平均曲率", "Gauss 映射及其基本性质", "局部曲面例子", "活动标架法", "Gauss 绝妙定理", "极小曲面", "曲面论基本定理")),
            ("曲面上的内蕴几何", ("曲面上的 Riemann 度量", "球面、双曲平面与上半平面", "联络与曲率", "曲面的结构方程", "协变导数与平行移动", "测地线与第一变分公式", "测地线的第二变分")),
            ("Gauss–Bonnet 定理", ("区域上的 Gauss–Bonnet 定理", "闭曲面上的 Gauss–Bonnet 定理")),
            ("微分几何在物理上的应用", ("变分法", "Euler–Lagrange 方程", "Legendre 变换", "Hamilton 方程", "Liouville 定理")),
        ),
    ),
)
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
    model_env: Path


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
        model_env = Path(config.get("model_env_file") or "/home/conrad/.config/activitywatch-advisor/goal-agent.env")
        self.paths = GoalAgentPaths(
            database=database,
            material_root=material_root,
            tavily_env=tavily_env,
            model_env=model_env,
        )
        self.output_root = output_root
        self.settings = settings
        self.config = config
        self.env_file = env_file
        self._now = now or (lambda: datetime.now(ZoneInfo(settings.get("timezone", TIMEZONE))))
        self._model_runner = model_runner or request_goal_json
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
                    metadata_json TEXT NOT NULL DEFAULT '{}',
                    UNIQUE(source_path, sha256)
                );
                CREATE TABLE IF NOT EXISTS course_profile (
                    id TEXT PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    course_code TEXT NOT NULL,
                    teacher TEXT NOT NULL,
                    credits REAL NOT NULL,
                    textbook_json TEXT NOT NULL,
                    assessment_weights_json TEXT NOT NULL,
                    exam_date TEXT,
                    confirmation_status TEXT NOT NULL,
                    nominal_hours INTEGER,
                    hours_detail_json TEXT NOT NULL,
                    hours_warning TEXT,
                    source_kind TEXT NOT NULL,
                    source_note TEXT,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS course_unit (
                    id TEXT PRIMARY KEY,
                    course_id TEXT NOT NULL REFERENCES course_profile(id),
                    chapter_no INTEGER NOT NULL,
                    chapter_title TEXT NOT NULL,
                    section_no INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    sort_order INTEGER NOT NULL,
                    UNIQUE(course_id, chapter_no, section_no)
                );
                CREATE TABLE IF NOT EXISTS course_progress_event (
                    id TEXT PRIMARY KEY,
                    evidence_event_id TEXT UNIQUE NOT NULL REFERENCES evidence_event(id),
                    course_id TEXT NOT NULL REFERENCES course_profile(id),
                    occurred_at TEXT NOT NULL,
                    taught_units_json TEXT NOT NULL,
                    exercise_attempted INTEGER,
                    exercise_correct INTEGER,
                    proof_recall_json TEXT NOT NULL,
                    note TEXT,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS course_unit_mastery (
                    course_id TEXT NOT NULL REFERENCES course_profile(id),
                    unit_id TEXT NOT NULL REFERENCES course_unit(id),
                    mastery INTEGER NOT NULL CHECK(mastery BETWEEN 0 AND 3),
                    last_event_id TEXT NOT NULL REFERENCES course_progress_event(id),
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY(course_id, unit_id)
                );
                """
            )
            self._ensure_column(
                connection,
                "plan_item",
                "course_id",
                "TEXT REFERENCES course_profile(id)",
            )
            self._ensure_column(
                connection,
                "plan_item",
                "input_state",
                "TEXT NOT NULL DEFAULT 'ready'",
            )
            self._ensure_column(
                connection,
                "material_record",
                "metadata_json",
                "TEXT NOT NULL DEFAULT '{}'",
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
            self._seed_course_catalog(connection)
            self._seed(connection)
            self._migrate_existing_course_plan(connection)
            connection.execute(
                "INSERT OR REPLACE INTO meta(key,value) VALUES('schema_version',?)",
                (str(SCHEMA_VERSION),),
            )

    @staticmethod
    def _ensure_column(
        connection: sqlite3.Connection,
        table: str,
        column: str,
        declaration: str,
    ) -> None:
        columns = {
            str(row["name"])
            for row in connection.execute(f"PRAGMA table_info({table})")
        }
        if column not in columns:
            connection.execute(f"ALTER TABLE {table} ADD COLUMN {column} {declaration}")

    def _seed_course_catalog(self, connection: sqlite3.Connection) -> None:
        now = self._now().isoformat(timespec="seconds")
        for profile in COURSE_PROFILES:
            connection.execute(
                "INSERT INTO course_profile("
                "id,name,course_code,teacher,credits,textbook_json,"
                "assessment_weights_json,exam_date,confirmation_status,"
                "nominal_hours,hours_detail_json,hours_warning,source_kind,"
                "source_note,updated_at"
                ") VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) "
                "ON CONFLICT(id) DO UPDATE SET "
                "name=excluded.name,course_code=excluded.course_code,"
                "teacher=excluded.teacher,credits=excluded.credits,"
                "textbook_json=excluded.textbook_json,"
                "assessment_weights_json=excluded.assessment_weights_json,"
                "nominal_hours=excluded.nominal_hours,"
                "hours_detail_json=excluded.hours_detail_json,"
                "hours_warning=excluded.hours_warning,"
                "source_kind=excluded.source_kind,source_note=excluded.source_note,"
                "confirmation_status=CASE "
                "WHEN course_profile.exam_date IS NULL THEN 'partial_confirmed' "
                "ELSE 'confirmed' END,updated_at=excluded.updated_at",
                (
                    profile["id"],
                    profile["name"],
                    profile["course_code"],
                    profile["teacher"],
                    profile["credits"],
                    _json(profile["textbooks"]),
                    _json(profile["assessment_weights"]),
                    None,
                    "partial_confirmed",
                    profile["nominal_hours"],
                    _json(profile["hours_detail"]),
                    profile["hours_warning"],
                    "user_confirmed",
                    "用户于 2026-08-31 提供并确认的课程页面内容；考试日期仍未知。",
                    now,
                ),
            )
        for unit in COURSE_UNITS:
            connection.execute(
                "INSERT INTO course_unit("
                "id,course_id,chapter_no,chapter_title,section_no,title,sort_order"
                ") VALUES(?,?,?,?,?,?,?) "
                "ON CONFLICT(id) DO UPDATE SET "
                "chapter_no=excluded.chapter_no,chapter_title=excluded.chapter_title,"
                "section_no=excluded.section_no,title=excluded.title,"
                "sort_order=excluded.sort_order",
                (
                    unit["id"],
                    unit["course_id"],
                    unit["chapter_no"],
                    unit["chapter_title"],
                    unit["section_no"],
                    unit["title"],
                    unit["sort_order"],
                ),
            )

    def _migrate_existing_course_plan(
        self,
        connection: sqlite3.Connection,
    ) -> None:
        marker = connection.execute(
            "SELECT value FROM meta WHERE key='course_plan_v2_migrated'"
        ).fetchone()
        if marker:
            return
        course_prefixes = {
            "p": ("probability", "概率论"),
            "f": ("functional-analysis", "泛函分析"),
            "d": ("differential-geometry", "微分几何"),
        }
        changes: list[dict[str, Any]] = []
        now = self._now().isoformat(timespec="seconds")
        for row in connection.execute(
            "SELECT p.* FROM plan_item p "
            "LEFT JOIN plan_item_task pt ON pt.plan_item_id=p.id "
            "WHERE p.track_id='track-courses' AND p.archived=0 "
            "AND p.accepted_date IS NULL AND pt.plan_item_id IS NULL"
        ).fetchall():
            match = re.fullmatch(r"w(\d+)-c-([pfd])([12])", str(row["id"]))
            if not match:
                continue
            course_id, course_name = course_prefixes[match.group(2)]
            kind = int(match.group(3))
            title = (
                f"{course_name}：按实际授课小节建立掌握闭环"
                if kind == 1
                else f"{course_name}：定义/定理复述、证明重建与当前章节习题"
            )
            description = (
                "先由用户确认本周实际讲到的小节。Goal Agent 只读取已授权的可见 Markdown、"
                "LaTeX 与 MathInk AI 识别文字；不会根据文件修改时间推断已经学完。"
            )
            before = {
                "title": row["title"],
                "description": row["description"],
                "course_id": row["course_id"],
                "input_state": row["input_state"],
            }
            connection.execute(
                "UPDATE plan_item SET title=?,description=?,course_id=?,"
                "input_state='awaiting_course_progress',updated_at=? WHERE id=?",
                (title, description, course_id, now, row["id"]),
            )
            changes.append(
                {
                    "plan_item_id": row["id"],
                    "field": "course_progress_mode",
                    "before": before,
                    "after": {
                        "title": title,
                        "description": description,
                        "course_id": course_id,
                        "input_state": "awaiting_course_progress",
                    },
                    "reason": "三门课于 2026-08-31 开课，改为按用户确认的实际授课小节与掌握度滚动计划。",
                }
            )
        pending_material_titles = {
            "track-amss-exam": (
                "数学所笔试：真实题源与考查范围待核验",
                "只有授权可区分来源的真实题源后才生成限时训练；不把传闻或重复题源当作基线。",
            ),
            "track-algebra": (
                "抽象代数：真实题组与口头题库待核验",
                "只有授权真实书面题组和口头模拟题库后才生成验收任务。",
            ),
            "track-ergodic": (
                "遍历论：GTM259 与现有笔记待同步",
                "等待已授权的 GTM259、章节笔记和习题同步；章节范围仍由用户确认。",
            ),
        }
        for row in connection.execute(
            "SELECT p.* FROM plan_item p "
            "LEFT JOIN plan_item_task pt ON pt.plan_item_id=p.id "
            "WHERE p.track_id IN ('track-amss-exam','track-ergodic','track-algebra') "
            "AND p.archived=0 AND p.accepted_date IS NULL AND pt.plan_item_id IS NULL"
        ).fetchall():
            title, description = pending_material_titles[row["track_id"]]
            before = {
                "title": row["title"],
                "description": row["description"],
                "input_state": row["input_state"],
            }
            connection.execute(
                "UPDATE plan_item SET title=?,description=?,"
                "input_state='awaiting_material',updated_at=? WHERE id=?",
                (title, description, now, row["id"]),
            )
            changes.append(
                {
                    "plan_item_id": row["id"],
                    "field": "material_readiness",
                    "before": before,
                    "after": {
                        "title": title,
                        "description": description,
                        "input_state": "awaiting_material",
                    },
                    "reason": "真实题源或学习资料尚未完成授权与同步，禁止虚构基线。",
                }
            )
        connection.execute(
            "INSERT OR REPLACE INTO meta(key,value) VALUES('course_plan_v2_migrated',?)",
            (now,),
        )
        if changes and self._current_version(connection):
            self._create_version(
                connection,
                "课程计划改为实际授课进度与掌握度闭环",
                "schema_v2_migration",
                changes,
                "system",
            )

    def _seed(self, connection: sqlite3.Connection) -> None:
        # Source seeds are an idempotent data migration, not only first-run
        # sample data.  Running this before the portfolio guard lets existing
        # Goal Agent databases receive newly curated official/research sources
        # without resetting plans, evidence, chats, or versions.
        self._seed_sources(connection)
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
        connection.execute(
            "INSERT OR REPLACE INTO meta(key,value) VALUES('course_plan_v2_migrated',?)",
            (now,),
        )
        self._create_version(connection, "初始化四轨道与 4 周试运行", "seed", [], "system")

    def _seed_trial_week(self, connection: sqlite3.Connection, now: str) -> None:
        # 1,590 minutes = 26.5 hours.  Each item is at most one weekday cap so
        # the recommendation engine can place it without inventing long
        # uninterrupted sessions.
        rows = (
            ("w1-c-p1", "track-courses", "概率论：按实际授课小节建立掌握闭环", 120, 5, 1),
            ("w1-c-p2", "track-courses", "概率论：定义/定理复述、证明重建与当前章节习题", 90, 5, 2),
            ("w1-c-f1", "track-courses", "泛函分析：按实际授课小节建立掌握闭环", 120, 5, 3),
            ("w1-c-f2", "track-courses", "泛函分析：定义/定理复述、证明重建与当前章节习题", 90, 5, 4),
            ("w1-c-d1", "track-courses", "微分几何：按实际授课小节建立掌握闭环", 120, 5, 5),
            ("w1-c-d2", "track-courses", "微分几何：定义/定理复述、证明重建与当前章节习题", 96, 5, 6),
            ("w1-e-1", "track-amss-exam", "数学所笔试：真实题源与考查范围待核验", 180, 5, 7),
            ("w1-e-2", "track-amss-exam", "数学所笔试：资料确认后再生成限时训练与订正", 138, 5, 8),
            ("w1-t-1", "track-ergodic", "遍历论：确认教材后完成首轮核心阅读", 180, 5, 9),
            ("w1-t-2", "track-ergodic", "遍历论：闭卷复述定义与关键证明策略", 180, 5, 10),
            ("w1-t-3", "track-ergodic", "遍历论：真实习题与待讨论问题记录", 117, 5, 11),
            ("w1-a-1", "track-algebra", "抽象代数：真实题组与口头题库待核验", 159, 5, 12),
        )
        dates = self._recommend_dates([(row[0], row[3]) for row in rows], date(2026, 8, 31), self._week_course_load(date(2026, 8, 31)))
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
                    (
                        "先由用户确认本周实际讲到的小节；只使用已授权的可见 Markdown、LaTeX 与 MathInk AI 识别文字。"
                        if track_id == "track-courses"
                        else "具体章节或题组必须来自已授权资料；资料不足时保持待核验，不生成虚假基线。"
                    ),
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
            dates = self._recommend_dates(rolling, week, self._week_course_load(week))
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
        for item_id, course_id in (
            ("c-p", "probability"),
            ("c-f", "functional-analysis"),
            ("c-d", "differential-geometry"),
        ):
            connection.execute(
                "UPDATE plan_item SET course_id=?,input_state='awaiting_course_progress' "
                "WHERE id GLOB ?",
                (course_id, f"w*-{item_id}[12]"),
            )
        connection.execute(
            "UPDATE plan_item SET input_state='awaiting_material' "
            "WHERE track_id IN ('track-amss-exam','track-ergodic','track-algebra')"
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
            ("paper-seijts-2004", "research", "peer_reviewed", "https://doi.org/10.2307/20159574", "Seijts et al. learning goals for complex tasks", "已引用"),
            ("paper-locke-latham-2002", "research", "peer_reviewed", "https://doi.org/10.1037/0003-066X.57.9.705", "Locke & Latham goal-setting theory", "已引用"),
            ("paper-dunlosky-2013", "research", "peer_reviewed", "https://doi.org/10.1177/1529100612453266", "Dunlosky et al. effective learning techniques", "已引用"),
            ("paper-roediger-2006", "research", "peer_reviewed", "https://doi.org/10.1111/j.1467-9280.2006.01693.x", "Roediger & Karpicke test-enhanced learning", "已引用"),
            ("paper-cepeda-2006", "research", "peer_reviewed", "https://doi.org/10.1037/0033-2909.132.3.354", "Cepeda et al. distributed practice", "已引用"),
            ("paper-kluger-denisi-1996", "research", "peer_reviewed", "https://doi.org/10.1037/0033-2909.119.2.254", "Kluger & DeNisi feedback intervention meta-analysis", "已引用"),
            ("paper-panadero-2017", "research", "peer_reviewed", "https://doi.org/10.3389/fpsyg.2017.00422", "Panadero self-regulated learning review", "已引用"),
        )
        for source_id, kind, grade, url, title, status in sources:
            connection.execute(
                "INSERT OR IGNORE INTO source_record(id,source_kind,grade,url,title,status,reference_only) VALUES(?,?,?,?,?,?,?)",
                (source_id, kind, grade, url, title, status, 1 if "往届" in status else 0),
            )

    @staticmethod
    def _recommend_dates(items: list[tuple[str, int]], start: date, course_load: dict | None = None) -> dict[str, str]:
        if start.weekday() != 0:
            raise ValueError("week start must be Monday")
        burdens = [(course_load or {}).get((start + timedelta(days=i)).isoformat(), 0) for i in range(7)]
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
            candidates.sort(key=lambda i: (-(minimums[i] - used[i]), used[i] / caps[i], burdens[i], i))
            seen: set[tuple[int, int, int]] = set()
            for chosen in candidates:
                signature = (caps[chosen], used[chosen], burdens[chosen])
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
                    connection.execute(
                        "UPDATE material_record SET title=?,source_path=?,modified_at=?,"
                        "page_count=?,status='indexed',metadata_json=? WHERE id=?",
                        (
                            title,
                            source_path,
                            document.get("modified_at"),
                            document.get("page_count"),
                            _json(
                                document.get("metadata")
                                if isinstance(document.get("metadata"), dict)
                                else {}
                            ),
                            record_id,
                        ),
                    )
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
                    "INSERT OR REPLACE INTO material_record("
                    "id,title,source_path,sha256,modified_at,page_count,status,indexed_at,metadata_json"
                    ") VALUES(?,?,?,?,?,?,?,?,?)",
                    (
                        record_id,
                        title,
                        source_path,
                        sha256,
                        document.get("modified_at"),
                        document.get("page_count"),
                        "indexed",
                        self._now().isoformat(timespec="seconds"),
                        _json(document.get("metadata") if isinstance(document.get("metadata"), dict) else {}),
                    ),
                )
            for row in connection.execute("SELECT id FROM material_record"):
                if row["id"] not in active_ids:
                    connection.execute("UPDATE material_record SET status='withdrawn' WHERE id=?", (row["id"],))
                    connection.execute("DELETE FROM material_fts WHERE record_id=?", (row["id"],))
            active_documents = [
                dict(row)
                for row in connection.execute(
                    "SELECT title,source_path FROM material_record WHERE status='indexed'"
                )
            ]
            active_titles = " ".join(
                f"{row['title']} {row['source_path']}" for row in active_documents
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
                if track_id != "track-courses":
                    connection.execute(
                        "UPDATE plan_item SET input_state=? "
                        "WHERE track_id=? AND archived=0 AND accepted_date IS NULL",
                        ("ready" if ready else "awaiting_material", track_id),
                    )
            for course_name, course_id in COURSE_IDS.items():
                ready = course_name in active_titles or course_id in active_titles
                connection.execute(
                    "UPDATE plan_item SET material_status=? "
                    "WHERE course_id=? AND material_required=1",
                    ("ready" if ready else "pending", course_id),
                )
                has_progress = bool(
                    connection.execute(
                        "SELECT 1 FROM course_progress_event WHERE course_id=? LIMIT 1",
                        (course_id,),
                    ).fetchone()
                )
                state = (
                    "awaiting_course_progress"
                    if not has_progress
                    else "ready"
                    if ready
                    else "awaiting_material"
                )
                connection.execute(
                    "UPDATE plan_item SET input_state=? "
                    "WHERE course_id=? AND archived=0 AND accepted_date IS NULL",
                    (state, course_id),
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
            profiles = {
                item["name"]: item
                for item in self._course_profiles_state(connection)
            }
            progress = self._course_progress_state(connection)["by_course"]
            course_results: dict[str, Any] = {}
            for course in COURSES:
                selected = [event for event in events if event["payload"].get("course") == course]
                course_results[course] = course_grade_scenario(selected)
                profile = profiles.get(course, {})
                course_results[course].update(
                    {
                        "profile_status": profile.get(
                            "confirmation_status",
                            "unknown",
                        ),
                        "profile_complete": (
                            profile.get("confirmation_status") == "confirmed"
                        ),
                        "teacher": profile.get("teacher"),
                        "textbooks": profile.get("textbooks", []),
                        "assessment_weights": profile.get(
                            "assessment_weights",
                            {},
                        ),
                        "exam_date": profile.get("exam_date"),
                        "missing_fields": profile.get("missing_fields", []),
                        "hours_warning": profile.get("hours_warning"),
                        "progress": progress.get(course, {}),
                    }
                )
            known = sum(1 for value in course_results.values() if value["state"] != "unknown")
            status = "unknown" if known < 3 else (
                "at_risk" if any(value["state"] == "at_risk" for value in course_results.values()) else "on_track"
            )
            return {
                **common,
                "status": status,
                "course_scenarios": course_results,
                "mastery": (
                    "按实际授课小节与 0–3 掌握度记录；总评预测仍等待真实成绩。"
                    if any(progress.get(course, {}).get("latest") for course in COURSES)
                    else "三门课均待填写本周实际授课小节。"
                ),
            }
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

    def _course_profiles_state(
        self,
        connection: sqlite3.Connection,
    ) -> list[dict[str, Any]]:
        profiles: list[dict[str, Any]] = []
        for row in connection.execute(
            "SELECT * FROM course_profile ORDER BY "
            "CASE name WHEN '概率论' THEN 1 WHEN '泛函分析' THEN 2 ELSE 3 END"
        ):
            item = dict(row)
            item["textbooks"] = _loads(item.pop("textbook_json"), [])
            item["assessment_weights"] = _loads(
                item.pop("assessment_weights_json"),
                {},
            )
            item["hours_detail"] = _loads(item.pop("hours_detail_json"), {})
            item["missing_fields"] = [
                label
                for label, missing in (
                    ("考试日期", not item.get("exam_date")),
                    ("教师", not item.get("teacher")),
                    ("教材", not item.get("textbooks")),
                    ("考核比例", not item.get("assessment_weights")),
                )
                if missing
            ]
            profiles.append(item)
        return profiles

    def _course_progress_state(
        self,
        connection: sqlite3.Connection,
    ) -> dict[str, Any]:
        result: dict[str, Any] = {}
        pending: list[str] = []
        for profile in self._course_profiles_state(connection):
            course_id = profile["id"]
            units = [
                dict(row)
                for row in connection.execute(
                    "SELECT id,chapter_no,chapter_title,section_no,title,sort_order "
                    "FROM course_unit WHERE course_id=? ORDER BY sort_order",
                    (course_id,),
                )
            ]
            mastery_rows = {
                row["unit_id"]: int(row["mastery"])
                for row in connection.execute(
                    "SELECT unit_id,mastery FROM course_unit_mastery WHERE course_id=?",
                    (course_id,),
                )
            }
            for unit in units:
                unit["mastery"] = mastery_rows.get(unit["id"], 0)
            distribution = {
                str(level): sum(
                    1 for value in mastery_rows.values() if value == level
                )
                for level in range(4)
            }
            event = connection.execute(
                "SELECT * FROM course_progress_event WHERE course_id=? "
                "ORDER BY occurred_at DESC,id DESC LIMIT 1",
                (course_id,),
            ).fetchone()
            latest = None
            if event:
                latest = dict(event)
                latest["taught_units"] = _loads(
                    latest.pop("taught_units_json"),
                    [],
                )
                latest["proof_recall"] = _loads(
                    latest.pop("proof_recall_json"),
                    [],
                )
            else:
                pending.append(profile["name"])
            result[profile["name"]] = {
                "course_id": course_id,
                "units": units,
                "total_units": len(units),
                "confirmed_taught_units": len(mastery_rows),
                "coverage_ratio": (
                    round(len(mastery_rows) / len(units), 3) if units else None
                ),
                "mastery_distribution": distribution,
                "latest": latest,
            }
        return {
            "scale": {
                "0": "未接触",
                "1": "听过或能看材料",
                "2": "能复述定义/定理",
                "3": "能独立证明或解题",
            },
            "by_course": result,
            "pending_input": pending,
        }

    def _material_state(self, connection: sqlite3.Connection) -> dict[str, Any]:
        documents = []
        for row in connection.execute(
            "SELECT id,title,source_path,sha256,modified_at,page_count,status,"
            "indexed_at,metadata_json FROM material_record ORDER BY title"
        ):
            item = dict(row)
            item["metadata"] = _loads(item.pop("metadata_json"), {})
            documents.append(item)
        gaps = [
            "概率论：考试日期；每周实际授课小节由用户确认",
            "泛函分析：考试日期；每周实际授课小节由用户确认",
            "微分几何：考试日期；每周实际授课小节由用户确认",
            "数学所笔试：至少三份可区分的真实题源",
            "遍历论：GTM259 已确认；仍需确认 2027-01-31 前章节范围",
            "抽象代数：真实书面题组与口头模拟题库",
            "2028 级正式选拔/夏令营/九月推免通知（发布后替换往届参考）",
        ]
        return {
            "manifest_path": "非笔记内容/任务计划/目标模式资料清单.md",
            "documents": documents,
            "gaps": gaps,
            "status": "ready" if documents else "awaiting_authorization",
        }

    def _model_state(self) -> dict[str, Any]:
        model = (
            self.config.get("model")
            if isinstance(self.config.get("model"), dict)
            else {}
        )
        _load_env_file(self.paths.model_env)
        env_name = str(model.get("api_key_env") or "GOAL_AGENT_API_KEY")
        return {
            "provider": str(model.get("provider") or "openai_compatible"),
            "protocol": str(model.get("protocol") or "responses"),
            "name": str(model.get("name") or "gpt-5.6-sol"),
            "reasoning_effort": str(
                model.get("reasoning_effort") or "medium"
            ),
            "configured": bool(os.environ.get(env_name)),
            "fallback_provider": None,
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
                "course_schedule": schedule_view(self.output_root, now=self._now(), start_date=date.fromisoformat(current_week)),
                "course_profiles": self._course_profiles_state(connection),
                "course_progress": self._course_progress_state(connection),
                "materials": self._material_state(connection),
                "approvals": approvals,
                "sources": sources,
                "chat_messages": chats,
                "tavily": {
                    "configured": self._tavily_configured(),
                    "credential_policy": "复用 Codex Tavily MCP 的同一 API 密钥；Pi 只从私有环境文件读取，不保存到仓库。",
                },
                "model": self._model_state(),
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

    def _week_course_load(self, start: date) -> dict[str, int]:
        view = schedule_view(self.output_root, now=self._now(), start_date=start)
        return {item["date"]: item["protected_minutes"] for item in view["daily_load"]}

    def _adjust_course_dates(self, connection: sqlite3.Connection) -> list[dict[str, Any]]:
        """Review-only soft redistribution. Never subtract lectures from deep caps.

        Strictly reduce course-burden × proposed deep minutes, retaining each
        day's existing deep-work minimum where it was met. Accepted dates and
        past/different-month dates are immovable; the caller audits all changes.
        """
        today = self._now().date()
        rows = [dict(row) for row in connection.execute(
            "SELECT * FROM plan_item WHERE archived=0 AND accepted_date IS NULL "
            "AND auto_adjustable=1 AND status='planned' AND recommended_date>=? ORDER BY sort_order,id",
            (today.isoformat(),),
        )]
        changes = []
        for week in sorted({row["week_start"] for row in rows}):
            start = date.fromisoformat(week)
            burden = self._week_course_load(start)
            days = [(start + timedelta(days=i)).isoformat() for i in range(7)]
            for row in sorted((r for r in rows if r["week_start"] == week), key=lambda r: (-int(r["deep_minutes"]), r["id"])):
                old = row["recommended_date"]
                if old[:7] != today.isoformat()[:7]:
                    continue
                minutes = int(row["deep_minutes"])
                old_day = date.fromisoformat(old)
                minimum = 120 if old_day.weekday() < 5 else 360
                if self._day_load(connection, old) - minutes < minimum:
                    continue
                for target in sorted(days, key=lambda d: (burden.get(d, 0), self._day_load(connection, d), d)):
                    if target < today.isoformat() or target[:7] != old[:7] or burden.get(target, 0) >= burden.get(old, 0):
                        continue
                    cap = 180 if date.fromisoformat(target).weekday() < 5 else 480
                    if self._day_load(connection, target) + minutes > cap:
                        continue
                    connection.execute("UPDATE plan_item SET recommended_date=?,updated_at=? WHERE id=?", (target, self._now().isoformat(timespec="seconds"), row["id"]))
                    changes.append({"plan_item_id": row["id"], "field": "recommended_date", "before": old, "after": target,
                                    "reason": "优先放到课程保护时间较少的同周日期；课外深度学习预算不变"})
                    break
        return changes

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

    def _normalize_course_progress(
        self,
        connection: sqlite3.Connection,
        details: dict[str, Any],
    ) -> dict[str, Any]:
        course_name = _clean_text(details.get("course"), 80)
        course_id = COURSE_IDS.get(course_name)
        if not course_id:
            raise ValueError("course_progress requires a known course")
        raw_units = details.get("taught_units")
        if not isinstance(raw_units, list) or not raw_units:
            raise ValueError("course_progress requires at least one taught unit")
        taught_units: list[dict[str, Any]] = []
        seen: set[str] = set()
        for raw in raw_units[:30]:
            if not isinstance(raw, dict):
                raise ValueError("each taught unit must be an object")
            unit_id = _clean_text(raw.get("unit_id"), 100)
            try:
                mastery = int(raw.get("mastery"))
            except (TypeError, ValueError):
                raise ValueError("course mastery must be 0, 1, 2, or 3") from None
            if mastery not in range(4):
                raise ValueError("course mastery must be 0, 1, 2, or 3")
            row = connection.execute(
                "SELECT id,title FROM course_unit WHERE id=? AND course_id=?",
                (unit_id, course_id),
            ).fetchone()
            if not row:
                raise ValueError("course unit does not belong to the selected course")
            if unit_id in seen:
                continue
            seen.add(unit_id)
            taught_units.append(
                {
                    "unit_id": unit_id,
                    "title": row["title"],
                    "mastery": mastery,
                }
            )
        if not taught_units:
            raise ValueError("course_progress requires at least one unique unit")
        attempted = details.get("exercise_attempted")
        correct = details.get("exercise_correct")
        attempted = None if attempted in (None, "") else int(attempted)
        correct = None if correct in (None, "") else int(correct)
        if attempted is not None and not 0 <= attempted <= 10000:
            raise ValueError("exercise_attempted is outside the accepted range")
        if correct is not None:
            if attempted is None:
                raise ValueError("exercise_correct requires exercise_attempted")
            if not 0 <= correct <= attempted:
                raise ValueError("exercise_correct must be between 0 and attempted")
        proof_recall = details.get("proof_recall")
        if proof_recall in (None, ""):
            proof_recall = []
        if not isinstance(proof_recall, list):
            raise ValueError("proof_recall must be a list")
        normalized_proof: list[dict[str, Any]] = []
        for item in proof_recall[:20]:
            if isinstance(item, str):
                normalized_proof.append({"note": _clean_text(item, 500)})
                continue
            if not isinstance(item, dict):
                raise ValueError("proof_recall items must be text or objects")
            unit_id = _clean_text(item.get("unit_id"), 100)
            if unit_id and unit_id not in seen:
                row = connection.execute(
                    "SELECT 1 FROM course_unit WHERE id=? AND course_id=?",
                    (unit_id, course_id),
                ).fetchone()
                if not row:
                    raise ValueError("proof_recall unit does not belong to the selected course")
            normalized_proof.append(
                {
                    "unit_id": unit_id or None,
                    "result": _clean_text(item.get("result"), 80) or None,
                    "note": _clean_text(item.get("note"), 500) or None,
                }
            )
        return {
            "course": course_name,
            "course_id": course_id,
            "taught_units": taught_units,
            "exercise_attempted": attempted,
            "exercise_correct": correct,
            "proof_recall": normalized_proof,
            "note": _clean_text(details.get("note"), 2000) or None,
        }

    def _save_course_progress(
        self,
        connection: sqlite3.Connection,
        *,
        evidence_event_id: str,
        occurred_at: str,
        normalized: dict[str, Any],
    ) -> list[dict[str, Any]]:
        course_event_id = "course-" + uuid.uuid4().hex
        now = self._now().isoformat(timespec="seconds")
        connection.execute(
            "INSERT INTO course_progress_event("
            "id,evidence_event_id,course_id,occurred_at,taught_units_json,"
            "exercise_attempted,exercise_correct,proof_recall_json,note,created_at"
            ") VALUES(?,?,?,?,?,?,?,?,?,?)",
            (
                course_event_id,
                evidence_event_id,
                normalized["course_id"],
                occurred_at,
                _json(normalized["taught_units"]),
                normalized["exercise_attempted"],
                normalized["exercise_correct"],
                _json(normalized["proof_recall"]),
                normalized["note"],
                now,
            ),
        )
        for unit in normalized["taught_units"]:
            connection.execute(
                "INSERT INTO course_unit_mastery("
                "course_id,unit_id,mastery,last_event_id,updated_at"
                ") VALUES(?,?,?,?,?) "
                "ON CONFLICT(course_id,unit_id) DO UPDATE SET "
                "mastery=excluded.mastery,last_event_id=excluded.last_event_id,"
                "updated_at=excluded.updated_at",
                (
                    normalized["course_id"],
                    unit["unit_id"],
                    unit["mastery"],
                    course_event_id,
                    now,
                ),
            )
        event_day = datetime.fromisoformat(
            occurred_at.replace("Z", "+00:00")
        ).date()
        week = _week_start(event_day).isoformat()
        rows = connection.execute(
            "SELECT * FROM plan_item WHERE course_id=? AND week_start=? "
            "AND archived=0 ORDER BY sort_order",
            (normalized["course_id"], week),
        ).fetchall()
        changes: list[dict[str, Any]] = []
        titles = [unit["title"] for unit in normalized["taught_units"]]
        scope = "、".join(titles[:3])
        if len(titles) > 3:
            scope += f"等 {len(titles)} 个小节"
        for index, row in enumerate(rows):
            if row["accepted_date"]:
                continue
            title = (
                f"{normalized['course']}：复述本周 {scope} 的定义与定理"
                if index == 0
                else f"{normalized['course']}：完成 {scope} 的证明重建与当前章节习题"
            )
            description = (
                f"用户已确认本周实际讲到：{scope}。"
                "Goal Agent 可读取已授权笔记的可见 Markdown/LaTeX、"
                "MathInk 忠实识别文字和标准图片引用；手写占位符本身不算掌握证据。"
            )
            input_state = (
                "ready"
                if row["material_status"] == "ready"
                else "awaiting_material"
            )
            before = {
                "title": row["title"],
                "description": row["description"],
                "input_state": row["input_state"],
                "status": row["status"],
            }
            after = {
                "title": title,
                "description": description,
                "input_state": input_state,
                "status": "in_progress",
            }
            connection.execute(
                "UPDATE plan_item SET title=?,description=?,input_state=?,"
                "status='in_progress',updated_at=? WHERE id=?",
                (title, description, input_state, now, row["id"]),
            )
            if before != after:
                changes.append(
                    {
                        "plan_item_id": row["id"],
                        "field": "course_scope",
                        "before": before,
                        "after": after,
                        "reason": "用户确认了本周实际授课小节与掌握度。",
                    }
                )
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
            course_progress = None
            if evidence_type == "course_progress":
                if track_id != "track-courses":
                    raise ValueError("course_progress must use the courses track")
                course_progress = self._normalize_course_progress(
                    connection,
                    event_payload,
                )
                event_payload = {
                    **event_payload,
                    **course_progress,
                }
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
            if course_progress:
                changes.extend(
                    self._save_course_progress(
                        connection,
                        evidence_event_id=event_id,
                        occurred_at=occurred_at,
                        normalized=course_progress,
                    )
                )
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
            if item["input_state"] != "ready":
                raise ValueError(
                    "plan item is waiting for confirmed course progress or authorized material"
                )
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
        _load_env_file(self.paths.model_env)
        model = {
            **self.settings.get("goal_agent_model", {}),
            **self.config.get("model", {}),
        }
        model.setdefault("provider", "openai_compatible")
        model.setdefault("protocol", "responses")
        model.setdefault("endpoint", "https://sub2api.52ai.pro/v1/responses")
        model.setdefault("name", "gpt-5.6-sol")
        model.setdefault("api_key_env", "GOAL_AGENT_API_KEY")
        model.setdefault("reasoning_effort", "medium")
        model.setdefault("max_output_tokens", 4500)
        model.setdefault("timeout_seconds", 80)
        model.setdefault("retries", 1)
        model.setdefault("structured_output", True)
        default_system = (
            "你是独立的目标 Agent，不是 Next Action。你衡量长期目标距离、解释证据不足、"
            "调整月/周策略。禁止伪造课程考核、题源、成绩或招生规则。少于三周可比数据时必须说未知。"
            "三门课只根据用户确认的实际授课小节、掌握度和已授权笔记制定任务；"
            "MathInk 手写占位符、图片引用或文件修改时间都不能单独证明用户已经掌握。"
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
            if not row or not int(row["auto_adjustable"]) or row["accepted_date"]:
                continue
            if row["recommended_date"] and row["recommended_date"][:7] != now_day.strftime("%Y-%m"):
                continue
            updates: dict[str, Any] = {}
            recommended = patch.get("recommended_date")
            if recommended not in (None, ""):
                recommended = _parse_date(recommended, required=True)
                target = date.fromisoformat(recommended)
                week = date.fromisoformat(row["week_start"])
                if not week <= target <= week + timedelta(days=6):
                    continue
                if target < now_day or target.strftime("%Y-%m") != now_day.strftime("%Y-%m"):
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
            changes.extend(self._adjust_course_dates(connection))
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
                    "UPDATE plan_item SET track_id=?,milestone_id=?,week_start=?,title=?,"
                    "description=?,deep_minutes=?,recommended_date=?,accepted_date=?,"
                    "status=?,value_score=?,material_required=?,material_status=?,"
                    "auto_adjustable=?,sort_order=?,course_id=?,input_state=?,archived=0,"
                    "updated_at=? WHERE id=?",
                    (
                        item["track_id"],
                        item.get("milestone_id"),
                        item["week_start"],
                        item["title"],
                        item.get("description", ""),
                        item["deep_minutes"],
                        item.get("recommended_date"),
                        item.get("accepted_date"),
                        item["status"],
                        item["value_score"],
                        item["material_required"],
                        item["material_status"],
                        item["auto_adjustable"],
                        item["sort_order"],
                        item.get("course_id"),
                        item.get("input_state", "ready"),
                        self._now().isoformat(timespec="seconds"),
                        item["id"],
                    ),
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
