from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from common import (
    atomic_write_json,
    atomic_write_text,
    iso_timestamp,
    load_json,
    parse_timestamp,
)
from computer_facts import extract_computer_facts
from cross_device import compare_devices
from deepseek_client import interpret_with_deepseek
from phone_facts import extract_phone_facts
from pushplus_client import send_report_via_wechat


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SETTINGS = PROJECT_ROOT / "config" / "settings.json"
DEFAULT_PROMPT = PROJECT_ROOT / "prompts" / "half-hour-interpreter.md"


def _automatic_period(timezone_name: str) -> tuple[datetime, datetime]:
    now = datetime.now(ZoneInfo(timezone_name))
    minute = 30 if now.minute >= 30 else 0
    end = now.replace(minute=minute, second=0, microsecond=0)
    return end - timedelta(minutes=30), end


def _parse_period(arguments, timezone_name: str) -> tuple[datetime, datetime]:
    if arguments.start or arguments.end:
        if not (arguments.start and arguments.end):
            raise ValueError("--start and --end must be supplied together")
        start = parse_timestamp(arguments.start, timezone_name)
        end = parse_timestamp(arguments.end, timezone_name)
    else:
        start, end = _automatic_period(timezone_name)
    if end <= start:
        raise ValueError("period end must be later than start")
    if (end - start) > timedelta(hours=2):
        raise ValueError("one run may process at most two hours")
    return start, end


def _report_markdown(report: dict[str, Any], start: datetime, end: datetime) -> str:
    lines = [
        f"# 半小时行为解释：{start:%Y-%m-%d %H:%M}—{end:%H:%M}",
        "",
        report.get("concise_report", "AI 未提供总述。"),
        "",
        "## 电脑端",
        "",
        report.get("computer_interpretation", {}).get(
            "likely_explanation", "没有可靠解释。"
        ),
        "",
        "## 手机端",
        "",
        report.get("phone_interpretation", {}).get(
            "likely_explanation", "没有可靠解释。"
        ),
        "",
        "## 不确定性",
        "",
    ]
    uncertainties = []
    uncertainties.extend(
        report.get("computer_interpretation", {}).get("uncertainties", [])
    )
    uncertainties.extend(
        report.get("phone_interpretation", {}).get("uncertainties", [])
    )
    uncertainties.extend(
        report.get("data_quality_assessment", {}).get("issues", [])
    )
    if uncertainties:
        lines.extend(f"- {item}" for item in uncertainties)
    else:
        lines.append("- 没有额外说明。")
    lines.extend(["", "## 可选择建议", ""])
    suggestions = report.get("gentle_suggestions", [])
    if suggestions:
        lines.extend(f"- {item}" for item in suggestions[:2])
    else:
        lines.append("- 这段数据不需要形成建议。")
    verification_question = report.get("verification_question", "").strip()
    if verification_question:
        lines.extend(
            [
                "",
                "## 抽样核对",
                "",
                verification_question,
            ]
        )
    lines.extend(
        [
            "",
            "---",
            "",
            "本报告只用于检验 AI 的行为解释能力，不会触发任何自动干预。",
            "",
        ]
    )
    return "\n".join(lines)


def _local_no_activity_report(start: datetime, end: datetime) -> dict[str, Any]:
    return {
        "period": f"{iso_timestamp(start)}/{iso_timestamp(end)}",
        "concise_report": "这一时段没有足够的电脑或手机活动证据，因此没有调用 AI。",
        "computer_interpretation": {
            "facts": [],
            "likely_explanation": "电脑活动证据不足。",
            "confidence": "low",
            "uncertainties": ["可能处于离开、睡眠或采集缺失状态。"],
        },
        "phone_interpretation": {
            "facts": [],
            "likely_explanation": "手机活动证据不足。",
            "confidence": "low",
            "uncertainties": ["不能据此判断是否正在休息。"],
        },
        "cross_device_observations": [],
        "likely_activities": [],
        "data_quality_assessment": {
            "level": "low",
            "issues": ["有效活动证据不足。"],
        },
        "gentle_suggestions": [],
        "verification_question": "",
        "_generation": {"provider": "local_rule", "model": None},
    }


def run(arguments) -> dict[str, Any]:
    settings_path = Path(arguments.settings).resolve()
    settings = load_json(settings_path)
    start, end = _parse_period(arguments, settings["timezone"])
    output_root = Path(settings["output_root"])
    day = start.strftime("%Y-%m-%d")
    period_id = start.strftime("%H-%M")

    computer_path = output_root / "computer_facts" / day / f"{period_id}.json"
    phone_path = output_root / "phone_facts" / day / f"{period_id}.json"
    combined_path = output_root / "combined_facts" / day / f"{period_id}.json"
    report_json_path = output_root / "ai_reports" / day / f"{period_id}.json"
    report_md_path = output_root / "ai_reports" / day / f"{period_id}.md"

    if report_json_path.exists() and not arguments.force:
        return {
            "status": "already_processed",
            "report": str(report_json_path),
            "period": f"{iso_timestamp(start)}/{iso_timestamp(end)}",
        }

    computer = extract_computer_facts(settings, start, end)
    phone = extract_phone_facts(settings, start, end)
    cross = compare_devices(computer, phone, settings["timezone"])
    combined = {
        "schema_version": 1,
        "period": computer["period"],
        "computer_facts_file": str(computer_path),
        "phone_facts_file": str(phone_path),
        "cross_device_facts": cross,
    }
    atomic_write_json(computer_path, computer)
    atomic_write_json(phone_path, phone)
    atomic_write_json(combined_path, combined)

    evidence_seconds = (
        float(computer["activity"]["not_afk_minutes"])
        + float(phone["screen"]["on_minutes"])
    ) * 60
    if evidence_seconds < int(settings["processing"]["minimum_evidence_seconds"]):
        report = _local_no_activity_report(start, end)
    else:
        report = interpret_with_deepseek(
            settings,
            Path(arguments.prompt).resolve(),
            computer,
            phone,
            cross,
        )

    atomic_write_json(report_json_path, report)
    atomic_write_text(report_md_path, _report_markdown(report, start, end))
    if arguments.no_push:
        delivery = {
            "status": "skipped",
            "channel": "wechat",
            "reason": "--no-push was supplied",
        }
    else:
        delivery = send_report_via_wechat(report, start, end)
    receipt_path = output_root / "pushplus_receipts" / day / f"{period_id}.json"
    atomic_write_json(receipt_path, delivery)
    state = {
        "last_successful_period_start": iso_timestamp(start),
        "last_successful_period_end": iso_timestamp(end),
        "last_report": str(report_json_path),
    }
    atomic_write_json(output_root / "state" / "processing-state.json", state)
    return {
        "status": "completed",
        "period": f"{iso_timestamp(start)}/{iso_timestamp(end)}",
        "computer_facts": str(computer_path),
        "phone_facts": str(phone_path),
        "combined_facts": str(combined_path),
        "report_json": str(report_json_path),
        "report_markdown": str(report_md_path),
        "model": report.get("_generation", {}).get("model"),
        "pushplus": delivery,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate one half-hour behavior report")
    parser.add_argument("--settings", default=str(DEFAULT_SETTINGS))
    parser.add_argument("--prompt", default=str(DEFAULT_PROMPT))
    parser.add_argument("--start", help="ISO 8601 period start")
    parser.add_argument("--end", help="ISO 8601 period end")
    parser.add_argument("--force", action="store_true")
    parser.add_argument(
        "--no-push",
        action="store_true",
        help="Generate files without sending the PushPlus WeChat message",
    )
    arguments = parser.parse_args()
    try:
        result = run(arguments)
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except Exception as error:
        print(
            json.dumps(
                {"status": "failed", "error": f"{type(error).__name__}: {error}"},
                ensure_ascii=False,
            ),
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
