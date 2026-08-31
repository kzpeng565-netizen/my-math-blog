from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.request
from datetime import datetime
from pathlib import Path


ACTIVITYWATCH_API = "http://127.0.0.1:5600/api/0/info"
ACTIVITYWATCH_SYNC = Path(r"D:\ActivityWatch\aw-server-rust\aw-sync.exe")
SYNC_DIRECTORY = Path(r"C:\Users\15345\ActivityWatchSync")
STATE_DIRECTORY = Path(os.environ["LOCALAPPDATA"]) / "ActivityWatchPiSync"
LOG_DIRECTORY = STATE_DIRECTORY / "logs"
STATUS_FILE = STATE_DIRECTORY / "status.json"


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def append_log(message: str) -> None:
    log_file = LOG_DIRECTORY / f"sync-{datetime.now():%Y-%m-%d}.log"
    with log_file.open("a", encoding="utf-8") as handle:
        handle.write(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {message}\n")


def write_status(status: dict[str, object]) -> None:
    temporary = STATUS_FILE.with_suffix(".json.tmp")
    temporary.write_text(
        json.dumps(status, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, STATUS_FILE)


def main() -> int:
    SYNC_DIRECTORY.mkdir(parents=True, exist_ok=True)
    LOG_DIRECTORY.mkdir(parents=True, exist_ok=True)

    status: dict[str, object] = {
        "checked_at": now_iso(),
        "ok": False,
        "activitywatch_version": None,
        "sync_directory": str(SYNC_DIRECTORY),
        "last_error": None,
    }

    try:
        if not ACTIVITYWATCH_SYNC.is_file():
            raise FileNotFoundError(f"aw-sync not found: {ACTIVITYWATCH_SYNC}")

        with urllib.request.urlopen(ACTIVITYWATCH_API, timeout=10) as response:
            info = json.load(response)
        status["activitywatch_version"] = info.get("version")

        append_log("Sync started")
        log_file = LOG_DIRECTORY / f"sync-{datetime.now():%Y-%m-%d}.log"
        creation_flags = (
            getattr(subprocess, "DETACHED_PROCESS", 0x00000008)
            | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0x00000200)
        )
        with log_file.open("ab") as log_handle:
            completed = subprocess.run(
                [
                    str(ACTIVITYWATCH_SYNC),
                    "--sync-dir",
                    str(SYNC_DIRECTORY),
                    "sync-advanced",
                    "--mode",
                    "push",
                ],
                stdin=subprocess.DEVNULL,
                stdout=log_handle,
                stderr=subprocess.STDOUT,
                creationflags=creation_flags,
                check=False,
            )

        if completed.returncode != 0:
            raise RuntimeError(
                f"aw-sync exited with code {completed.returncode}. See log: {log_file}"
            )

        status["ok"] = True
        append_log("Sync completed")
        return 0
    except Exception as error:
        status["last_error"] = f"{type(error).__name__}: {error}"
        append_log(f"Sync failed: {status['last_error']}")
        return 1
    finally:
        status["checked_at"] = now_iso()
        write_status(status)


if __name__ == "__main__":
    raise SystemExit(main())
