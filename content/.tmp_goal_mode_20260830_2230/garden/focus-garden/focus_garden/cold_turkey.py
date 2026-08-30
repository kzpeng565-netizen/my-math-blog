from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any


class ColdTurkeyController:
    def __init__(self, settings: dict[str, Any]):
        self.settings = settings["cold_turkey"]
        self.agent_config_path = Path(self.settings["agent_config"])

    def _resolved(self) -> tuple[Path, set[str]]:
        config = json.loads(self.agent_config_path.read_text(encoding="utf-8"))
        executable = Path(config.get("cold_turkey_exe") or self.settings["executable"])
        allowed = set((config.get("allowed_blocks") or {}).keys())
        return executable, allowed

    def start(self, blocks: list[str], minutes: int) -> list[dict[str, Any]]:
        dry_run = os.environ.get("FOCUS_GARDEN_DRY_RUN") == "1" or self.settings.get("mode") == "dry_run"
        if dry_run:
            return [
                {"block": block, "status": "simulated", "exit_code": 0, "minutes": minutes}
                for block in blocks
            ]

        executable, allowed = self._resolved()
        unknown = set(blocks) - allowed
        if unknown:
            raise ValueError(f"Cold Turkey block 不在 allowlist: {sorted(unknown)}")
        if not executable.exists():
            raise FileNotFoundError(str(executable))

        results = []
        for block in blocks:
            # This development fallback mirrors the agent-owned, stoppable
            # lease.  A timed Cold Turkey hard lock cannot be released on pause.
            command = [str(executable), "-start", block]
            creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
            proc = subprocess.run(command, capture_output=True, text=True, timeout=20, creationflags=creationflags)
            results.append({"block": block, "status": "success" if proc.returncode == 0 else "failed",
                            "exit_code": proc.returncode, "minutes": minutes, "mode": "agent_lease",
                            "output_excerpt": (proc.stdout or proc.stderr or "")[:300]})
        return results

    def stop(self, blocks: list[str]) -> list[dict[str, Any]]:
        dry_run = os.environ.get("FOCUS_GARDEN_DRY_RUN") == "1" or self.settings.get("mode") == "dry_run"
        if dry_run:
            return [{"block": block, "status": "released", "exit_code": 0} for block in blocks]
        executable, allowed = self._resolved()
        unknown = set(blocks) - allowed
        if unknown:
            raise ValueError(f"Cold Turkey block not in allowlist: {sorted(unknown)}")
        return [
            {"block": block, "status": "released" if (proc := subprocess.run([str(executable), "-stop", block], capture_output=True, text=True, timeout=20, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))).returncode == 0 else "failed", "exit_code": proc.returncode}
            for block in blocks
        ]
