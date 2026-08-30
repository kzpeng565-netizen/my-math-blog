from __future__ import annotations

import hashlib
import json
import random
import re
import sqlite3
import threading
import uuid
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


INTERVENTION_ACCEPTED = "intervention_accepted"
INTERVENTION_BASIC = "intervention_basic"
DAILY_FULL_TOMATO_ADVANCED = "daily_full_tomato_advanced"
STEAM_NIGHT_CLOSED = "steam_night_closed"


class GardenDatabase:
    def __init__(self, path: Path, plant_tiers: dict[str, str] | None = None):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self.plant_tiers = dict(plant_tiers or {})
        self._init_schema()
        self._reconcile_progression()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path, timeout=20)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    @contextmanager
    def _connection(self):
        conn = self._connect()
        try:
            with conn:
                yield conn
        finally:
            conn.close()

    def _init_schema(self) -> None:
        with self._connection() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS rewards (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    occurred_at TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    source TEXT NOT NULL,
                    payload_json TEXT NOT NULL DEFAULT '{}',
                    status TEXT NOT NULL DEFAULT 'pending'
                        CHECK(status IN ('pending','planted')),
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_rewards_status_time
                    ON rewards(status, occurred_at DESC);

                CREATE TABLE IF NOT EXISTS garden_plants (
                    id TEXT PRIMARY KEY,
                    reward_id TEXT NOT NULL UNIQUE REFERENCES rewards(id),
                    species_id TEXT NOT NULL,
                    tier TEXT NOT NULL DEFAULT 'basic',
                    x INTEGER NOT NULL,
                    y INTEGER NOT NULL,
                    planted_at TEXT NOT NULL,
                    UNIQUE(x, y)
                );

                CREATE TABLE IF NOT EXISTS reward_exchanges (
                    source_reward_id TEXT PRIMARY KEY REFERENCES rewards(id),
                    advanced_reward_id TEXT NOT NULL REFERENCES rewards(id),
                    exchanged_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS daily_achievements (
                    date TEXT PRIMARY KEY,
                    planned_tomatoes INTEGER NOT NULL,
                    completed_tomatoes INTEGER NOT NULL,
                    task_count INTEGER NOT NULL,
                    eligible INTEGER NOT NULL DEFAULT 0,
                    evaluated_at TEXT NOT NULL,
                    reward_id TEXT UNIQUE REFERENCES rewards(id),
                    evidence_json TEXT NOT NULL DEFAULT '{}'
                );

                CREATE TABLE IF NOT EXISTS focus_sessions (
                    id TEXT PRIMARY KEY,
                    profile_id TEXT NOT NULL,
                    duration_minutes INTEGER NOT NULL,
                    task_id TEXT,
                    task_title TEXT,
                    source TEXT NOT NULL DEFAULT 'garden',
                    started_at TEXT NOT NULL,
                    ends_at TEXT NOT NULL,
                    status TEXT NOT NULL CHECK(status IN ('running','completed','cancelled','failed')),
                    cold_turkey_json TEXT NOT NULL DEFAULT '[]',
                    completed_at TEXT
                );
                CREATE INDEX IF NOT EXISTS idx_focus_status ON focus_sessions(status);

                -- A pause is intentionally a separate record: existing sessions
                -- remain compatible with the old running/completed status check.
                -- One row per session makes the "pause once" rule atomic.
                CREATE TABLE IF NOT EXISTS focus_pauses (
                    session_id TEXT PRIMARY KEY REFERENCES focus_sessions(id),
                    paused_at TEXT NOT NULL,
                    requested_minutes INTEGER NOT NULL,
                    resume_at TEXT NOT NULL
                );

                -- A completed focus session can be attached to one Obsidian
                -- task.  This ledger is intentionally separate from the
                -- garden-wide 40-minute reward counter: task progress must
                -- never be inferred from unrelated focus time.
                CREATE TABLE IF NOT EXISTS task_focus_balances (
                    task_id TEXT PRIMARY KEY,
                    credit_minutes INTEGER NOT NULL DEFAULT 0,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS task_focus_settlements (
                    session_id TEXT PRIMARY KEY REFERENCES focus_sessions(id),
                    task_id TEXT NOT NULL,
                    tomatoes INTEGER NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending'
                        CHECK(status IN ('pending','queued','skipped')),
                    target_completed INTEGER,
                    mutation_id TEXT,
                    detail TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_task_focus_settlements_status
                    ON task_focus_settlements(status, created_at);

                CREATE TABLE IF NOT EXISTS focus_plans (
                    id TEXT PRIMARY KEY,
                    kind TEXT NOT NULL CHECK(kind IN ('scheduled','cycle')),
                    profile_id TEXT NOT NULL,
                    focus_minutes INTEGER NOT NULL,
                    rest_minutes INTEGER NOT NULL DEFAULT 0,
                    rounds INTEGER NOT NULL DEFAULT 1,
                    current_round INTEGER NOT NULL DEFAULT 0,
                    targets_json TEXT NOT NULL,
                    starts_at TEXT NOT NULL,
                    next_action_at TEXT NOT NULL,
                    status TEXT NOT NULL CHECK(status IN ('scheduled','focus','break','completed','cancelled','failed')),
                    last_session_id TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_focus_plans_due
                    ON focus_plans(status, next_action_at);

                CREATE TABLE IF NOT EXISTS bridge_health (
                    device_id TEXT PRIMARY KEY,
                    last_seen_at TEXT NOT NULL,
                    status TEXT NOT NULL,
                    detail TEXT NOT NULL DEFAULT '',
                    metadata_json TEXT NOT NULL DEFAULT '{}',
                    first_seen_at TEXT,
                    heartbeat_count INTEGER NOT NULL DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS bridge_heartbeat_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_id TEXT NOT NULL,
                    seen_at TEXT NOT NULL,
                    status TEXT NOT NULL,
                    metadata_json TEXT NOT NULL DEFAULT '{}'
                );
                CREATE INDEX IF NOT EXISTS idx_bridge_heartbeat_events_device_time
                    ON bridge_heartbeat_events(device_id, seen_at DESC);

                CREATE TABLE IF NOT EXISTS counters (
                    key TEXT PRIMARY KEY,
                    value INTEGER NOT NULL
                );
                INSERT OR IGNORE INTO counters(key, value) VALUES('garden_size', 5);
                INSERT OR IGNORE INTO counters(key, value) VALUES('focus_credit_minutes', 0);
                """
            )
            columns = {row[1] for row in conn.execute("PRAGMA table_info(garden_plants)")}
            if "tier" not in columns:
                conn.execute("ALTER TABLE garden_plants ADD COLUMN tier TEXT NOT NULL DEFAULT 'basic'")
            focus_columns = {row[1] for row in conn.execute("PRAGMA table_info(focus_sessions)")}
            for name, definition in (
                ("task_id", "TEXT"),
                ("task_title", "TEXT"),
                ("source", "TEXT NOT NULL DEFAULT 'garden'"),
                ("was_paused", "INTEGER NOT NULL DEFAULT 0"),
                ("credited_minutes", "INTEGER"),
                ("targets_json", "TEXT NOT NULL DEFAULT '[]'"),
                ("blocks_json", "TEXT NOT NULL DEFAULT '[]'"),
            ):
                if name not in focus_columns:
                    conn.execute(f"ALTER TABLE focus_sessions ADD COLUMN {name} {definition}")
            bridge_columns = {row[1] for row in conn.execute("PRAGMA table_info(bridge_health)")}
            for name, definition in (
                ("metadata_json", "TEXT NOT NULL DEFAULT '{}'"),
                ("first_seen_at", "TEXT"),
                ("heartbeat_count", "INTEGER NOT NULL DEFAULT 0"),
            ):
                if name not in bridge_columns:
                    conn.execute(f"ALTER TABLE bridge_health ADD COLUMN {name} {definition}")
            pause_columns = {row[1] for row in conn.execute("PRAGMA table_info(focus_pauses)")}
            if "resume_at" not in pause_columns:
                # Existing paused rows predate scheduled resume.  Their requested
                # duration remains the intended pause duration during migration.
                conn.execute("ALTER TABLE focus_pauses ADD COLUMN resume_at TEXT")
                conn.execute(
                    "UPDATE focus_pauses SET resume_at=datetime(paused_at, '+' || requested_minutes || ' minutes') "
                    "WHERE resume_at IS NULL"
                )
            advanced_ids = [plant_id for plant_id, tier in self.plant_tiers.items() if tier == "advanced"]
            if advanced_ids:
                placeholders = ",".join("?" for _ in advanced_ids)
                conn.execute(f"UPDATE garden_plants SET tier='advanced' WHERE species_id IN ({placeholders})", advanced_ids)
            exchange_sql = conn.execute(
                "SELECT sql FROM sqlite_master WHERE type='table' AND name='reward_exchanges'"
            ).fetchone()[0]
            if "advanced_reward_id TEXT NOT NULL UNIQUE" in exchange_sql:
                conn.executescript(
                    """ALTER TABLE reward_exchanges RENAME TO reward_exchanges_legacy;
                       CREATE TABLE reward_exchanges (
                         source_reward_id TEXT PRIMARY KEY REFERENCES rewards(id),
                         advanced_reward_id TEXT NOT NULL REFERENCES rewards(id),
                         exchanged_at TEXT NOT NULL
                       );
                       INSERT INTO reward_exchanges(source_reward_id,advanced_reward_id,exchanged_at)
                         SELECT source_reward_id,advanced_reward_id,exchanged_at FROM reward_exchanges_legacy;
                       DROP TABLE reward_exchanges_legacy;"""
                )

    @staticmethod
    def _row(row: sqlite3.Row | None) -> dict[str, Any] | None:
        if row is None:
            return None
        result = dict(row)
        for key in ("payload_json", "cold_turkey_json", "targets_json", "blocks_json", "metadata_json", "evidence_json"):
            if key in result:
                result[key.removesuffix("_json")] = json.loads(result.pop(key) or "{}")
        if "payload" in result and "tier" not in result:
            result["tier"] = result["payload"].get("tier", "basic")
        return result

    def _reconcile_progression(self, conn: sqlite3.Connection | None = None) -> int:
        if conn is not None:
            return self._reconcile_intervention_rewards(conn)
        with self._lock, self._connection() as managed:
            return self._reconcile_intervention_rewards(managed)

    def _reconcile_intervention_rewards(self, conn: sqlite3.Connection) -> int:
        """Mint one basic entitlement for each unclaimed group of three acceptances."""
        rows = conn.execute(
            """SELECT r.* FROM rewards r
               LEFT JOIN garden_plants p ON p.reward_id=r.id
               WHERE r.type=? AND p.reward_id IS NULL
               ORDER BY r.occurred_at, r.id""",
            (INTERVENTION_ACCEPTED,),
        ).fetchall()
        inserted = 0
        for offset in range(0, len(rows) - 2, 3):
            group = rows[offset:offset + 3]
            source_ids = [row["id"] for row in group]
            digest = hashlib.sha256("|".join(source_ids).encode()).hexdigest()[:20]
            reward_id = f"derived:intervention-basic:{digest}"
            before = conn.total_changes
            conn.execute(
                """INSERT OR IGNORE INTO rewards
                   (id,type,occurred_at,reason,source,payload_json,status,created_at)
                   VALUES(?,?,?,?,?,?,'pending',?)""",
                (
                    reward_id, INTERVENTION_BASIC, group[-1]["occurred_at"],
                    "主动接受系统介入 3 次，获得 1 个初级植物资格",
                    "derived",
                    json.dumps({"tier": "basic", "source_event_ids": source_ids, "rule": "3 interventions -> 1 basic"}, ensure_ascii=False),
                    utc_now(),
                ),
            )
            inserted += conn.total_changes - before
        return inserted

    def _available_basic_rows(self, conn: sqlite3.Connection) -> list[sqlite3.Row]:
        rows = conn.execute(
            """SELECT r.* FROM rewards r
               WHERE r.type != ? AND r.status='pending'
                 AND NOT EXISTS (SELECT 1 FROM reward_exchanges e WHERE e.source_reward_id=r.id)
               ORDER BY r.occurred_at, r.id""",
            (INTERVENTION_ACCEPTED,),
        ).fetchall()
        return [row for row in rows if json.loads(row["payload_json"] or "{}").get("tier", "basic") == "basic"]

    def import_rewards(self, events: Iterable[dict[str, Any]]) -> int:
        inserted = 0
        with self._lock, self._connection() as conn:
            for event in events:
                before = conn.total_changes
                conn.execute(
                    """INSERT OR IGNORE INTO rewards
                       (id,type,occurred_at,reason,source,payload_json,status,created_at)
                       VALUES(?,?,?,?,?,?,'pending',?)""",
                    (
                        event["id"], event["type"], event["occurred_at"],
                        event["reason"], event.get("source", "pi"),
                        json.dumps(event.get("payload", {}), ensure_ascii=False), utc_now(),
                    ),
                )
                inserted += conn.total_changes - before
            self._reconcile_progression(conn)
        return inserted

    def record_steam_night_closed(self, event_id: str, occurred_at: str) -> dict[str, Any]:
        """Mint one idempotent basic opportunity for an explicit close choice."""
        safe_event_id = str(event_id).strip()
        if not re.fullmatch(r"[A-Za-z0-9:._+-]{8,120}", safe_event_id):
            raise ValueError("invalid Steam close event id")
        reward_id = f"steam-night-closed:{safe_event_id}"
        self.import_rewards([{
            "id": reward_id,
            "type": STEAM_NIGHT_CLOSED,
            "occurred_at": str(occurred_at),
            "reason": "23:30 夜间提示中主动关闭 Steam 游戏",
            "source": "windows_agent",
            "payload": {"tier": "basic", "event_id": safe_event_id},
        }])
        reward = next((item for item in self.rewards(limit=500) if item["id"] == reward_id), None)
        if reward is None:
            raise RuntimeError("Steam close reward could not be read back")
        return reward

    def rewards(self, status: str | None = None, limit: int = 200) -> list[dict[str, Any]]:
        sql = """SELECT * FROM rewards r WHERE r.type != ?
                 AND NOT EXISTS (SELECT 1 FROM reward_exchanges e WHERE e.source_reward_id=r.id)"""
        args: list[Any] = [INTERVENTION_ACCEPTED]
        if status:
            sql += " AND status=?"
            args.append(status)
        sql += " ORDER BY occurred_at DESC LIMIT ?"
        args.append(limit)
        with self._connection() as conn:
            return [self._row(r) for r in conn.execute(sql, args).fetchall()]  # type: ignore[misc]

    def garden_size(self, conn: sqlite3.Connection | None = None) -> int:
        owns = conn is None
        conn = conn or self._connect()
        try:
            return int(conn.execute("SELECT value FROM counters WHERE key='garden_size'").fetchone()[0])
        finally:
            if owns:
                conn.close()

    def _place_plant(self, conn: sqlite3.Connection, reward_id: str, species_id: str,
                     species_tier: str) -> dict[str, Any]:
        size = self.garden_size(conn)
        occupied = {(row[0], row[1]) for row in conn.execute("SELECT x,y FROM garden_plants")}
        while True:
            radius = size // 2
            free = [(x, y) for y in range(-radius, radius + 1)
                    for x in range(-radius, radius + 1) if (x, y) not in occupied]
            if free:
                break
            size += 2
            conn.execute("UPDATE counters SET value=? WHERE key='garden_size'", (size,))
        seed = int(hashlib.sha256(f"{reward_id}:{species_id}".encode()).hexdigest()[:16], 16)
        x, y = random.Random(seed).choice(free)
        plant_id = str(uuid.uuid4())
        planted_at = utc_now()
        conn.execute(
            "INSERT INTO garden_plants(id,reward_id,species_id,tier,x,y,planted_at) VALUES(?,?,?,?,?,?,?)",
            (plant_id, reward_id, species_id, species_tier, x, y, planted_at),
        )
        conn.execute("UPDATE rewards SET status='planted' WHERE id=?", (reward_id,))
        return {"id": plant_id, "reward_id": reward_id, "species_id": species_id,
                "x": x, "y": y, "planted_at": planted_at, "garden_size": size}

    def plant_reward(self, reward_id: str, species_id: str, species_tier: str = "basic") -> dict[str, Any]:
        """Use one named entitlement to plant a species of the same tier."""
        with self._lock, self._connection() as conn:
            conn.execute("BEGIN IMMEDIATE")
            reward = conn.execute("SELECT * FROM rewards WHERE id=?", (reward_id,)).fetchone()
            if reward is None:
                raise KeyError("奖励不存在")
            if reward["type"] == INTERVENTION_ACCEPTED:
                raise ValueError("主动介入需累计 3 次后领取初级植物")
            if conn.execute("SELECT 1 FROM reward_exchanges WHERE source_reward_id=?", (reward_id,)).fetchone():
                raise ValueError("该初级种植机会已兑换为高级植物")
            if reward["status"] != "pending":
                existing = conn.execute("SELECT * FROM garden_plants WHERE reward_id=?", (reward_id,)).fetchone()
                if existing:
                    return self._row(existing)  # type: ignore[return-value]
                raise ValueError("奖励已经处理")
            reward_tier = json.loads(reward["payload_json"] or "{}").get("tier", "basic")
            if reward_tier != species_tier:
                raise ValueError(f"{reward_tier} 种植机会只能选择同等级植物")
            return self._place_plant(conn, reward_id, species_id, species_tier)

    def record_daily_scorecards(self, scorecards: Iterable[dict[str, Any]], today: str) -> int:
        """Finalize past daily tomato challenges and mint each advanced reward once."""
        awarded = 0
        now = utc_now()
        with self._lock, self._connection() as conn:
            conn.execute("BEGIN IMMEDIATE")
            for card in scorecards:
                day = str(card.get("date", ""))
                if len(day) != 10 or day >= today:
                    continue
                planned = max(0, int(card.get("planned_tomatoes", 0) or 0))
                completed = max(0, int(card.get("completed_tomatoes", 0) or 0))
                task_count = max(0, int(card.get("task_count", 0) or 0))
                eligible = planned >= 7 and completed >= planned
                reward_id = f"daily-full-tomato:{day}" if eligible else None
                evidence = json.dumps({
                    "date": day, "planned_tomatoes": planned, "completed_tomatoes": completed,
                    "task_count": task_count, "rule": "planned >= 7 and completed >= planned",
                }, ensure_ascii=False, separators=(",", ":"))
                if eligible:
                    before = conn.total_changes
                    conn.execute(
                        """INSERT OR IGNORE INTO rewards
                           (id,type,occurred_at,reason,source,payload_json,status,created_at)
                           VALUES(?,?,?,?,?,?,'pending',?)""",
                        (reward_id, DAILY_FULL_TOMATO_ADVANCED, now,
                         f"{day} 完成全部 {planned} 个番茄钟，获得 1 次高级植物种植机会",
                         "daily_achievement",
                         json.dumps({"tier": "advanced", "date": day, "planned_tomatoes": planned,
                                     "completed_tomatoes": completed}, ensure_ascii=False), now),
                    )
                    awarded += conn.total_changes - before
                conn.execute(
                    """INSERT INTO daily_achievements
                       (date,planned_tomatoes,completed_tomatoes,task_count,eligible,evaluated_at,reward_id,evidence_json)
                       VALUES(?,?,?,?,?,?,?,?)
                       ON CONFLICT(date) DO UPDATE SET
                         planned_tomatoes=max(daily_achievements.planned_tomatoes,excluded.planned_tomatoes),
                         completed_tomatoes=max(daily_achievements.completed_tomatoes,excluded.completed_tomatoes),
                         task_count=max(daily_achievements.task_count,excluded.task_count),
                         eligible=max(daily_achievements.eligible,excluded.eligible),
                         evaluated_at=excluded.evaluated_at,
                         reward_id=COALESCE(daily_achievements.reward_id,excluded.reward_id),
                         evidence_json=excluded.evidence_json""",
                    (day, planned, completed, task_count, int(eligible), now, reward_id, evidence),
                )
        return awarded

    def daily_achievements(self, limit: int = 93) -> list[dict[str, Any]]:
        with self._connection() as conn:
            rows = conn.execute(
                "SELECT * FROM daily_achievements ORDER BY date DESC LIMIT ?", (max(1, min(limit, 366)),)
            ).fetchall()
            return [self._row(row) for row in rows]  # type: ignore[misc]

    def plant_advanced_from_basic(self, species_id: str, species_tier: str) -> dict[str, Any]:
        """Spend three unclaimed basic opportunities to plant one advanced species."""
        if species_tier != "advanced":
            raise ValueError("高级种植只能选择高级植物")
        with self._lock, self._connection() as conn:
            conn.execute("BEGIN IMMEDIATE")
            source_rows = self._available_basic_rows(conn)[:3]
            if len(source_rows) < 3:
                raise ValueError("需要积攒 3 次初级种植机会才能种植高级植物")
            source_ids = [row["id"] for row in source_rows]
            digest = hashlib.sha256("|".join(source_ids).encode()).hexdigest()[:20]
            reward_id = f"derived:advanced-exchange:{digest}"
            now = utc_now()
            conn.execute(
                """INSERT OR IGNORE INTO rewards
                   (id,type,occurred_at,reason,source,payload_json,status,created_at)
                   VALUES(?,?,?,?,?,?,'pending',?)""",
                (reward_id, "advanced_exchange", now,
                 "积攒 3 次初级种植机会，兑换 1 次高级植物种植",
                 "derived", json.dumps({"tier": "advanced", "source_reward_ids": source_ids,
                                        "rule": "3 basic opportunities -> 1 advanced"}, ensure_ascii=False), now),
            )
            for source_id in source_ids:
                conn.execute(
                    "INSERT OR IGNORE INTO reward_exchanges(source_reward_id,advanced_reward_id,exchanged_at) VALUES(?,?,?)",
                    (source_id, reward_id, now),
                )
            planted = self._place_plant(conn, reward_id, species_id, species_tier)
            planted["consumed_basic_reward_ids"] = source_ids
            return planted

    def garden(self) -> dict[str, Any]:
        with self._connection() as conn:
            plants = [dict(r) for r in conn.execute(
                """SELECT p.*, r.type AS reward_type, r.reason, r.occurred_at
                   FROM garden_plants p JOIN rewards r ON r.id=p.reward_id
                   ORDER BY p.planted_at"""
            )]
            return {"size": self.garden_size(conn), "plants": plants}

    def create_focus(self, profile_id: str, duration: int, started_at: str, ends_at: str,
                     *, task_id: str | None = None, task_title: str | None = None,
                     source: str = "garden", targets: list[str] | None = None,
                     blocks: list[str] | None = None) -> dict[str, Any]:
        with self._lock, self._connection() as conn:
            running = conn.execute("SELECT * FROM focus_sessions WHERE status='running'").fetchone()
            if running:
                return self._row(running)  # type: ignore[return-value]
            session_id = str(uuid.uuid4())
            conn.execute(
                """INSERT INTO focus_sessions
                   (id,profile_id,duration_minutes,task_id,task_title,source,started_at,ends_at,status,targets_json,blocks_json)
                   VALUES(?,?,?,?,?,?,?,?, 'running',?,?)""",
                (session_id, profile_id, duration, task_id, task_title, source, started_at, ends_at,
                 json.dumps(targets or [], ensure_ascii=False), json.dumps(blocks or [], ensure_ascii=False)),
            )
            row = conn.execute("SELECT * FROM focus_sessions WHERE id=?", (session_id,)).fetchone()
            return self._row(row)  # type: ignore[return-value]

    def focus(self, session_id: str | None = None) -> dict[str, Any] | None:
        with self._connection() as conn:
            if session_id:
                row = conn.execute("SELECT * FROM focus_sessions WHERE id=?", (session_id,)).fetchone()
            else:
                row = conn.execute(
                    "SELECT * FROM focus_sessions WHERE status='running' ORDER BY started_at DESC LIMIT 1"
                ).fetchone()
            result = self._row(row)
            if result:
                pause = conn.execute(
                    "SELECT paused_at,requested_minutes,resume_at FROM focus_pauses WHERE session_id=?", (result["id"],)
                ).fetchone()
                result["paused"] = bool(pause)
                if pause:
                    result["paused_at"] = pause["paused_at"]
                    result["pause_minutes"] = pause["requested_minutes"]
                    result["resume_at"] = pause["resume_at"]
            return result

    def pause_focus(self, session_id: str, requested_minutes: int) -> dict[str, Any]:
        if not 1 <= requested_minutes <= 120:
            raise ValueError("pause minutes must be between 1 and 120")
        with self._lock, self._connection() as conn:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute("SELECT * FROM focus_sessions WHERE id=?", (session_id,)).fetchone()
            if not row or row["status"] != "running":
                raise ValueError("no running focus session")
            if int(row["was_paused"] or 0):
                raise ValueError("this focus session has already used its one pause")
            paused_at = datetime.now(timezone.utc)
            resume_at = paused_at + timedelta(minutes=requested_minutes)
            conn.execute("INSERT INTO focus_pauses(session_id,paused_at,requested_minutes,resume_at) VALUES(?,?,?,?)",
                         (session_id, paused_at.isoformat(timespec="seconds"), requested_minutes,
                          resume_at.isoformat(timespec="seconds")))
            conn.execute("UPDATE focus_sessions SET was_paused=1 WHERE id=?", (session_id,))
        return self.focus(session_id)  # type: ignore[return-value]

    def resume_focus(self, session_id: str) -> dict[str, Any]:
        with self._lock, self._connection() as conn:
            conn.execute("BEGIN IMMEDIATE")
            pause = conn.execute(
                "SELECT paused_at,requested_minutes,resume_at FROM focus_pauses WHERE session_id=?", (session_id,)
            ).fetchone()
            row = conn.execute("SELECT * FROM focus_sessions WHERE id=?", (session_id,)).fetchone()
            if not row or row["status"] != "running" or not pause:
                raise ValueError("focus session is not paused")
            # The pause length is the confirmed commitment, not the time a
            # browser happened to be open.  This makes automatic resume stable.
            extra = int(pause["requested_minutes"]) * 60
            ends_at = datetime.fromisoformat(row["ends_at"]) + timedelta(seconds=extra)
            conn.execute("UPDATE focus_sessions SET ends_at=? WHERE id=?", (ends_at.isoformat(timespec="seconds"), session_id))
            conn.execute("DELETE FROM focus_pauses WHERE session_id=?", (session_id,))
        return self.focus(session_id)  # type: ignore[return-value]

    def set_focus_execution(self, session_id: str, executions: list[dict[str, Any]], failed: bool = False) -> None:
        with self._lock, self._connection() as conn:
            if failed:
                conn.execute(
                    "UPDATE focus_sessions SET cold_turkey_json=?, status='failed' WHERE id=? AND status='running'",
                    (json.dumps(executions, ensure_ascii=False), session_id),
                )
            else:
                # Execution receipts are diagnostic metadata.  In particular,
                # the release receipt written after completion must not revive
                # the finished session as `running`.
                conn.execute(
                    "UPDATE focus_sessions SET cold_turkey_json=? WHERE id=?",
                    (json.dumps(executions, ensure_ascii=False), session_id),
                )

    def cancel_focus(self, session_id: str) -> None:
        with self._lock, self._connection() as conn:
            conn.execute("UPDATE focus_sessions SET status='cancelled' WHERE id=? AND status='running'", (session_id,))

    def complete_focus(self, session_id: str) -> int:
        with self._lock, self._connection() as conn:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute("SELECT * FROM focus_sessions WHERE id=?", (session_id,)).fetchone()
            if not row or row["status"] != "running" or conn.execute("SELECT 1 FROM focus_pauses WHERE session_id=?", (session_id,)).fetchone():
                return 0
            credited_minutes = int(row["duration_minutes"]) // 2 if int(row["was_paused"] or 0) else int(row["duration_minutes"])
            completed_at = utc_now()
            conn.execute("UPDATE focus_sessions SET status='completed', completed_at=?, credited_minutes=? WHERE id=?", (completed_at, credited_minutes, session_id))
            credit = int(conn.execute("SELECT value FROM counters WHERE key='focus_credit_minutes'").fetchone()[0])
            total = credit + credited_minutes
            count, remainder = divmod(total, 40)
            conn.execute("UPDATE counters SET value=? WHERE key='focus_credit_minutes'", (remainder,))
            for index in range(count):
                reward_id = f"focus:{session_id}:{index + 1}"
                conn.execute(
                    """INSERT OR IGNORE INTO rewards
                       (id,type,occurred_at,reason,source,payload_json,status,created_at)
                       VALUES(?,?,?,?,?,?,'pending',?)""",
                    (reward_id, "focus_completed", completed_at,
                     f"完成 {credited_minutes} 分钟有效专注，累计满 40 分钟",
                     "local", json.dumps({"session_id": session_id, "minutes": row["duration_minutes"], "credited_minutes": credited_minutes, "paused": bool(row["was_paused"])}), completed_at),
                )
            task_id = str(row["task_id"] or "").strip()
            if task_id:
                balance_row = conn.execute(
                    "SELECT credit_minutes FROM task_focus_balances WHERE task_id=?", (task_id,)
                ).fetchone()
                task_total = int(balance_row["credit_minutes"]) if balance_row else 0
                earned_tomatoes, task_remainder = divmod(task_total + credited_minutes, 40)
                conn.execute(
                    """INSERT INTO task_focus_balances(task_id,credit_minutes,updated_at) VALUES(?,?,?)
                       ON CONFLICT(task_id) DO UPDATE SET credit_minutes=excluded.credit_minutes,
                       updated_at=excluded.updated_at""",
                    (task_id, task_remainder, completed_at),
                )
                if earned_tomatoes:
                    conn.execute(
                        """INSERT OR IGNORE INTO task_focus_settlements
                           (session_id,task_id,tomatoes,status,created_at,updated_at)
                           VALUES(?,?,?,'pending',?,?)""",
                        (session_id, task_id, earned_tomatoes, completed_at, completed_at),
                    )
            return count

    def pending_task_focus_settlements(self) -> list[dict[str, Any]]:
        with self._connection() as conn:
            return [dict(row) for row in conn.execute(
                "SELECT * FROM task_focus_settlements WHERE status='pending' ORDER BY created_at, session_id"
            ).fetchall()]

    def mark_task_focus_settlement(self, session_id: str, status: str, *, target_completed: int | None = None,
                                   mutation_id: str | None = None, detail: str = "") -> None:
        if status not in {"queued", "skipped"}:
            raise ValueError("invalid task focus settlement status")
        with self._lock, self._connection() as conn:
            conn.execute(
                """UPDATE task_focus_settlements
                   SET status=?,target_completed=?,mutation_id=?,detail=?,updated_at=? WHERE session_id=?""",
                (status, target_completed, mutation_id, detail[:300], utc_now(), session_id),
            )

    def focus_history(self, limit: int = 50) -> list[dict[str, Any]]:
        with self._connection() as conn:
            return [self._row(r) for r in conn.execute(
                "SELECT * FROM focus_sessions ORDER BY started_at DESC LIMIT ?", (limit,)
            ).fetchall()]  # type: ignore[misc]

    def completed_focus_summary(self, start: datetime, end: datetime) -> dict[str, int]:
        """Return completed Garden focus time in a timezone-safe interval."""
        start_utc = start.astimezone(timezone.utc)
        end_utc = end.astimezone(timezone.utc)
        with self._connection() as conn:
            rows = conn.execute(
                "SELECT duration_minutes,completed_at FROM focus_sessions "
                "WHERE status='completed' AND completed_at IS NOT NULL"
            ).fetchall()
        matched = []
        for row in rows:
            try:
                completed_at = datetime.fromisoformat(str(row["completed_at"]))
                if completed_at.tzinfo is None:
                    completed_at = completed_at.replace(tzinfo=timezone.utc)
                if start_utc <= completed_at.astimezone(timezone.utc) < end_utc:
                    matched.append(row)
            except (TypeError, ValueError):
                continue
        return {
            "focus_minutes": sum(int(row["duration_minutes"] or 0) for row in matched),
            "completed_count": len(matched),
        }

    def create_focus_plan(self, kind: str, profile_id: str, focus_minutes: int,
                          rest_minutes: int, rounds: int, targets: list[str], starts_at: str) -> dict[str, Any]:
        if kind not in {"scheduled", "cycle"}:
            raise ValueError("unknown focus plan kind")
        plan_id, now = str(uuid.uuid4()), utc_now()
        with self._lock, self._connection() as conn:
            conn.execute(
                """INSERT INTO focus_plans
                   (id,kind,profile_id,focus_minutes,rest_minutes,rounds,targets_json,starts_at,next_action_at,status,created_at,updated_at)
                   VALUES(?,?,?,?,?,?,?,?,?,'scheduled',?,?)""",
                (plan_id, kind, profile_id, focus_minutes, rest_minutes, rounds,
                 json.dumps(targets, ensure_ascii=False), starts_at, starts_at, now, now),
            )
            return self._row(conn.execute("SELECT * FROM focus_plans WHERE id=?", (plan_id,)).fetchone())  # type: ignore[return-value]

    def focus_plans(self, limit: int = 12) -> list[dict[str, Any]]:
        with self._connection() as conn:
            return [self._row(row) for row in conn.execute(
                "SELECT * FROM focus_plans WHERE status IN ('scheduled','focus','break') ORDER BY next_action_at LIMIT ?", (limit,)
            ).fetchall()]  # type: ignore[misc]

    def next_due_focus_plan(self, now: str) -> dict[str, Any] | None:
        with self._connection() as conn:
            row = conn.execute(
                """SELECT * FROM focus_plans WHERE status IN ('scheduled','break')
                   AND next_action_at<=? ORDER BY next_action_at LIMIT 1""", (now,)
            ).fetchone()
            return self._row(row)

    def mark_focus_plan_started(self, plan_id: str, session_id: str) -> None:
        with self._lock, self._connection() as conn:
            conn.execute(
                """UPDATE focus_plans SET status='focus', current_round=current_round+1,
                   last_session_id=?, updated_at=? WHERE id=? AND status IN ('scheduled','break')""",
                (session_id, utc_now(), plan_id),
            )

    def advance_focus_plan_for_session(self, session_id: str, completed_at: str) -> None:
        with self._lock, self._connection() as conn:
            row = conn.execute(
                "SELECT * FROM focus_plans WHERE last_session_id=? AND status='focus'", (session_id,)
            ).fetchone()
            if not row:
                return
            if int(row["current_round"]) >= int(row["rounds"]):
                conn.execute("UPDATE focus_plans SET status='completed', updated_at=? WHERE id=?", (completed_at, row["id"]))
                return
            finished = datetime.fromisoformat(completed_at)
            next_action = (finished + timedelta(minutes=int(row["rest_minutes"]))).isoformat(timespec="seconds")
            conn.execute(
                "UPDATE focus_plans SET status='break', next_action_at=?, updated_at=? WHERE id=?",
                (next_action, completed_at, row["id"]),
            )

    def cancel_focus_plan_for_session(self, session_id: str) -> None:
        with self._lock, self._connection() as conn:
            conn.execute(
                "UPDATE focus_plans SET status='cancelled', updated_at=? WHERE last_session_id=? AND status='focus'",
                (utc_now(), session_id),
            )

    def fail_focus_plan(self, plan_id: str) -> None:
        with self._lock, self._connection() as conn:
            conn.execute(
                "UPDATE focus_plans SET status='failed', updated_at=? WHERE id=?",
                (utc_now(), plan_id),
            )

    def record_bridge_heartbeat(self, device_id: str, status: str, detail: str = "",
                                metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        seen = utc_now()
        metadata_json = json.dumps(metadata or {}, ensure_ascii=False, separators=(",", ":"))
        cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat(timespec="seconds")
        with self._lock, self._connection() as conn:
            conn.execute(
                """INSERT INTO bridge_health
                   (device_id,last_seen_at,status,detail,metadata_json,first_seen_at,heartbeat_count)
                   VALUES(?,?,?,?,?,?,1)
                   ON CONFLICT(device_id) DO UPDATE SET last_seen_at=excluded.last_seen_at,
                   status=excluded.status, detail=excluded.detail,
                   metadata_json=excluded.metadata_json,
                   heartbeat_count=bridge_health.heartbeat_count+1""",
                (device_id, seen, status, detail[:240], metadata_json, seen),
            )
            conn.execute(
                "INSERT INTO bridge_heartbeat_events(device_id,seen_at,status,metadata_json) VALUES(?,?,?,?)",
                (device_id, seen, status, metadata_json),
            )
            conn.execute("DELETE FROM bridge_heartbeat_events WHERE seen_at < ?", (cutoff,))
            return self._row(conn.execute(
                "SELECT * FROM bridge_health WHERE device_id=?", (device_id,)
            ).fetchone())  # type: ignore[return-value]

    def bridge_health(self, device_id: str) -> dict[str, Any] | None:
        with self._connection() as conn:
            row = conn.execute("SELECT * FROM bridge_health WHERE device_id=?", (device_id,)).fetchone()
            return self._row(row)

    def bridge_heartbeat_history(self, device_id: str, limit: int = 512) -> list[dict[str, Any]]:
        with self._connection() as conn:
            rows = conn.execute(
                """SELECT device_id,seen_at,status,metadata_json
                   FROM bridge_heartbeat_events WHERE device_id=?
                   ORDER BY seen_at DESC LIMIT ?""",
                (device_id, max(1, min(int(limit), 2048))),
            ).fetchall()
            return [self._row(row) for row in rows]  # type: ignore[misc]

    def stats(self) -> dict[str, Any]:
        with self._connection() as conn:
            rewards = {r[0]: r[1] for r in conn.execute("SELECT type,COUNT(*) FROM rewards GROUP BY type")}
            planted = conn.execute("SELECT COUNT(*) FROM garden_plants").fetchone()[0]
            focus_minutes = conn.execute(
                "SELECT COALESCE(SUM(duration_minutes),0) FROM focus_sessions WHERE status='completed'"
            ).fetchone()[0]
            credit = conn.execute("SELECT value FROM counters WHERE key='focus_credit_minutes'").fetchone()[0]
            intervention_unclaimed = conn.execute(
                """SELECT COUNT(*) FROM rewards r LEFT JOIN garden_plants p ON p.reward_id=r.id
                   WHERE r.type=? AND p.reward_id IS NULL""",
                (INTERVENTION_ACCEPTED,),
            ).fetchone()[0]
            basic_available = len(self._available_basic_rows(conn))
            basic_planted = conn.execute("SELECT COUNT(*) FROM garden_plants WHERE tier='basic'").fetchone()[0]
            advanced_planted = conn.execute("SELECT COUNT(*) FROM garden_plants WHERE tier='advanced'").fetchone()[0]
            direct_advanced_available = conn.execute(
                """SELECT COUNT(*) FROM rewards
                   WHERE status='pending' AND json_extract(payload_json,'$.tier')='advanced'"""
            ).fetchone()[0]
            advanced_exchange_available = basic_available // 3
            advanced_available = advanced_exchange_available + direct_advanced_available
            return {"rewards_by_type": rewards, "planted": planted,
                    "focus_minutes": focus_minutes, "focus_credit_minutes": credit,
                    "intervention_progress": intervention_unclaimed % 3,
                    "basic_available": basic_available, "basic_planted": basic_planted,
                    "basic_progress": basic_available,
                    "advanced_planted": advanced_planted, "advanced_available": advanced_available,
                    "advanced_direct_available": direct_advanced_available,
                    "advanced_exchange_available": advanced_exchange_available}
