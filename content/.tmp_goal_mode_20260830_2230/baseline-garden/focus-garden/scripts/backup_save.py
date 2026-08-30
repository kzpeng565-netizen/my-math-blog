from __future__ import annotations

import argparse
import json
import os
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path


def newest_source_mtime(source: Path) -> float:
    candidates = [source, Path(str(source) + "-wal")]
    return max((path.stat().st_mtime for path in candidates if path.exists()), default=0.0)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create an atomic, consistent Focus Garden save snapshot")
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--destination", required=True, type=Path)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    source = args.source.resolve()
    destination = args.destination.resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not source.is_file():
        raise FileNotFoundError(source)
    if not args.force and destination.exists() and destination.stat().st_mtime >= newest_source_mtime(source):
        print("unchanged")
        return

    temporary = destination.with_name(destination.name + ".tmp")
    temporary.unlink(missing_ok=True)
    try:
        with closing(sqlite3.connect(f"file:{source}?mode=ro", uri=True)) as source_db:
            with closing(sqlite3.connect(temporary)) as backup_db:
                source_db.backup(backup_db)
                integrity = backup_db.execute("PRAGMA integrity_check").fetchone()[0]
                if integrity != "ok":
                    raise RuntimeError(f"backup integrity check failed: {integrity}")
        os.replace(temporary, destination)
    finally:
        temporary.unlink(missing_ok=True)

    manifest = {
        "schema": 1,
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_name": source.name,
        "snapshot_name": destination.name,
        "integrity_check": "ok",
    }
    manifest_path = destination.with_name("manifest.json")
    manifest_tmp = manifest_path.with_name(manifest_path.name + ".tmp")
    manifest_tmp.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(manifest_tmp, manifest_path)
    print(destination)


if __name__ == "__main__":
    main()
