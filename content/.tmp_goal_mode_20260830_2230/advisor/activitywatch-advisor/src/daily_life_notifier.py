from __future__ import annotations

import argparse
import json
import os
from argparse import Namespace
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from common import atomic_write_json
from daily_life_statistics import DEFAULT_ENV, DEFAULT_PROMPT, DEFAULT_SETTINGS, run
from notifications import NtfyNotifier


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / "data"
DEFAULT_NTFY_ENV = Path("/home/conrad/.config/activitywatch-advisor/ntfy.env")
TIMEZONE = ZoneInfo("Asia/Shanghai")


def target_date(now: datetime) -> date:
    return now.date() - timedelta(days=1)


def _receipt_path(output_root: Path, day: date) -> Path:
    return output_root / "statistics" / "ntfy_receipts" / "daily_life" / f"{day.isoformat()}.json"


def _morning_state_path(output_root: Path, day: date) -> Path:
    return output_root / "state" / "daily_life_morning" / f"{day.isoformat()}.json"


def _morning_cutoff_hour(now: datetime) -> int:
    return min(11, max(9, now.astimezone(TIMEZONE).hour))


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return {}


def _load_env_file(path: Path) -> None:
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            key, value = stripped.split("=", 1)
            key = key.strip()
            if key and key not in os.environ:
                os.environ[key] = value.strip().strip('"').strip("'")
    except OSError:
        return


def _message_title(summary: dict[str, Any], day: date) -> str:
    advice = summary.get("ai_advice")
    status = advice.get("status") if isinstance(advice, dict) else None
    suffix = f"｜{status}" if status else ""
    return f"每日行为复盘 {day.isoformat()}{suffix}"


def _message_body(markdown_path: Path, limit: int = 3900) -> str:
    text = markdown_path.read_text(encoding="utf-8").strip()
    if len(text) <= limit:
        return text
    return text[: limit - 80].rstrip() + "\n\n... 内容已截断，请查看服务器上的完整日报。"


def _run_daily_life(
    *,
    day: date,
    output_root: Path,
    settings: Path,
    prompt: Path,
    env_file: Path,
    cutoff_hour: int,
    no_ai: bool,
) -> dict[str, Any]:
    return run(
        Namespace(
            settings=str(settings),
            output_root=output_root,
            prompt=str(prompt),
            env_file=str(env_file),
            date=day,
            no_ai=no_ai,
            morning_cutoff_hour=cutoff_hour,
        )
    )


def notify_daily_life(
    *,
    day: date,
    output_root: Path,
    settings: Path,
    prompt: Path,
    env_file: Path,
    ntfy_env_file: Path = DEFAULT_NTFY_ENV,
    force: bool = False,
    no_push: bool = False,
    no_ai: bool = False,
    notifier: NtfyNotifier | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    output_root = output_root.resolve()
    now = now or datetime.now(TIMEZONE)
    cutoff_hour = _morning_cutoff_hour(now)
    receipt_path = _receipt_path(output_root, day)
    if receipt_path.exists() and not force:
        existing = _read_json(receipt_path)
        if existing.get("status") == "accepted":
            return {
                "status": "already_sent",
                "period": day.isoformat(),
                "receipt": str(receipt_path),
            }

    preflight = _run_daily_life(
        day=day,
        output_root=output_root,
        settings=settings,
        prompt=prompt,
        env_file=env_file,
        cutoff_hour=cutoff_hour,
        no_ai=True,
    )
    summary = _read_json(Path(preflight["json"]))
    sleep = summary.get("phone_sleep_boundary", {}) if summary else {}
    if (
        not force
        and cutoff_hour < 11
        and sleep.get("status") == "pending"
    ):
        state = {
            "status": "pending_sleep_boundary",
            "period": day.isoformat(),
            "cutoff_hour": cutoff_hour,
            "next_retry_hour": cutoff_hour + 1,
            "attempted_at": now.isoformat(timespec="seconds"),
            "json_file": preflight["json"],
            "markdown_file": preflight["markdown"],
            "sleep": sleep,
        }
        atomic_write_json(_morning_state_path(output_root, day), state)
        return state

    generated = preflight
    if not no_ai:
        generated = _run_daily_life(
            day=day,
            output_root=output_root,
            settings=settings,
            prompt=prompt,
            env_file=env_file,
            cutoff_hour=cutoff_hour,
            no_ai=False,
        )
        summary = _read_json(Path(generated["json"]))
    markdown_path = Path(generated["markdown"])

    if no_push:
        delivery = {
            "status": "skipped",
            "provider": "ntfy",
            "reason": "--no-push was supplied",
            "title": _message_title(summary, day),
        }
    else:
        _load_env_file(ntfy_env_file)
        result = (notifier or NtfyNotifier()).send(
            title=_message_title(summary, day),
            message=_message_body(markdown_path),
            priority="default",
            tags=["bar_chart", "calendar"],
        )
        delivery = result.as_dict()

    receipt = {
        **delivery,
        "period": day.isoformat(),
        "generated": generated,
        "markdown_file": str(markdown_path),
        "json_file": generated["json"],
        "attempted_at": now.isoformat(timespec="seconds"),
    }
    atomic_write_json(receipt_path, receipt)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate and send the daily life report through ntfy.")
    parser.add_argument("--date", type=date.fromisoformat)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--settings", type=Path, default=DEFAULT_SETTINGS)
    parser.add_argument("--prompt", type=Path, default=DEFAULT_PROMPT)
    parser.add_argument("--env-file", type=Path, default=DEFAULT_ENV)
    parser.add_argument("--ntfy-env-file", type=Path, default=DEFAULT_NTFY_ENV)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--no-push", action="store_true")
    parser.add_argument("--no-ai", action="store_true")
    args = parser.parse_args()
    day = args.date or target_date(datetime.now(TIMEZONE))
    receipt = notify_daily_life(
        day=day,
        output_root=args.output_root,
        settings=args.settings,
        prompt=args.prompt,
        env_file=args.env_file,
        ntfy_env_file=args.ntfy_env_file,
        force=args.force,
        no_push=args.no_push,
        no_ai=args.no_ai,
    )
    print(json.dumps(receipt, ensure_ascii=False))
    return 0 if receipt.get("status") in {"accepted", "already_sent", "skipped", "pending_sleep_boundary"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
