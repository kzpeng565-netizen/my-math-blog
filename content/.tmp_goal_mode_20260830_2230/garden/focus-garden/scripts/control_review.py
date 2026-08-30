from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from focus_garden.control_metrics import ControlMetrics  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Freeze the weekly Focus Garden control review")
    parser.add_argument("--force", action="store_true", help="replace an existing frozen review")
    parser.add_argument("--daily", action="store_true", help="write only the daily delay-debt snapshot")
    args = parser.parse_args()
    settings = json.loads((ROOT / "config" / "settings.json").read_text(encoding="utf-8"))
    operations = settings.get("operations", {})
    metrics = ControlMetrics(
        ROOT / settings["database"],
        Path(operations.get("advisor_data_root", "/home/conrad/workspace/activitywatch-advisor/data")),
        Path(operations.get("obsidian_sync_root", "/home/conrad/workspace/behavior-context-sync")),
        ROOT / "data" / "control-review.json",
    )
    if args.daily:
        result = metrics.save_daily_snapshot(force=args.force)
        print(json.dumps({
            "write_state": result.get("write_state"),
            "date": result.get("date"),
            "delay_debt": result.get("delay_debt"),
            "postponed_task_count": result.get("postponed_task_count"),
        }, ensure_ascii=False))
        return 0
    result = metrics.write_snapshot(force=args.force)
    print(json.dumps({
        "write_state": result.get("write_state"),
        "generated_at": result.get("generated_at"),
        "frozen_until": result.get("frozen_until"),
        "state": (result.get("state") or {}).get("code"),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
