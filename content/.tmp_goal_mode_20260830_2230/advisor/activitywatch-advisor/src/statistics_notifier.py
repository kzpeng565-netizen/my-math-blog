from __future__ import annotations

import argparse
import json
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from behavior_statistics import aggregate
from common import atomic_write_json
from pushplus_client import send_statistics_via_wechat


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / "data"
TIMEZONE = ZoneInfo("Asia/Shanghai")


def resolve_period(kind: str, now: datetime) -> tuple[list[date], str]:
    if kind == "daily":
        target = now.date() - timedelta(days=1)
        return [target], target.isoformat()
    current_week_start = now.date() - timedelta(days=now.date().weekday())
    previous_week_start = current_week_start - timedelta(days=7)
    days = [previous_week_start + timedelta(days=offset) for offset in range(7)]
    iso_year, iso_week, _ = previous_week_start.isocalendar()
    return days, f"{iso_year}-W{iso_week:02d}"


def notify(
    kind: str,
    output_root: Path,
    now: datetime,
    force: bool = False,
    no_push: bool = False,
) -> dict:
    days, period = resolve_period(kind, now)
    statistics = aggregate(output_root, days, period)
    statistics_path = output_root / "statistics" / kind / f"{period}.json"
    atomic_write_json(statistics_path, statistics)
    receipt_path = (
        output_root / "statistics" / "pushplus_receipts" / kind / f"{period}.json"
    )
    if receipt_path.exists() and not force:
        try:
            existing = json.loads(receipt_path.read_text(encoding="utf-8"))
            if existing.get("status") == "accepted":
                return {
                    "status": "already_sent",
                    "kind": kind,
                    "period": period,
                    "receipt": str(receipt_path),
                }
        except (OSError, json.JSONDecodeError):
            pass
    if no_push:
        delivery = {
            "status": "skipped",
            "channel": "wechat",
            "reason": "--no-push was supplied",
        }
    else:
        delivery = send_statistics_via_wechat(statistics, kind)
    receipt = {
        **delivery,
        "kind": kind,
        "period": period,
        "statistics_file": str(statistics_path),
        "attempted_at": now.isoformat(timespec="seconds"),
    }
    atomic_write_json(receipt_path, receipt)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kind", choices=("daily", "weekly"), required=True)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--no-push", action="store_true")
    arguments = parser.parse_args()
    result = notify(
        arguments.kind,
        arguments.output_root.resolve(),
        datetime.now(TIMEZONE),
        arguments.force,
        arguments.no_push,
    )
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["status"] in {"accepted", "already_sent", "skipped"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
