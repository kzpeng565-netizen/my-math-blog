from __future__ import annotations

import argparse
import json
import sqlite3
from contextlib import closing
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit a Focus Garden SQLite save")
    parser.add_argument("database", type=Path)
    args = parser.parse_args()
    with closing(sqlite3.connect(f"file:{args.database.resolve()}?mode=ro", uri=True)) as connection:
        result = {
            "database": str(args.database),
            "integrity": connection.execute("PRAGMA integrity_check").fetchone()[0],
            "rewards": connection.execute("SELECT COUNT(1) FROM rewards").fetchone()[0],
            "plants": connection.execute("SELECT COUNT(1) FROM garden_plants").fetchone()[0],
            "pending": connection.execute(
                "SELECT COUNT(1) FROM rewards WHERE status='pending'"
            ).fetchone()[0],
            "running": connection.execute(
                "SELECT COUNT(1) FROM focus_sessions WHERE status='running'"
            ).fetchone()[0],
        }
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
