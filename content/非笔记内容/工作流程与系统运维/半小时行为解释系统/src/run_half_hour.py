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
    state = report.get("state_assessment", {})
    allocation = report.get("estimated_time_allocation", {})
    fragmentation = report.get("fragmentation_assessment", {})
    lines = [
        f"# 半小时状态核验：{start:%Y-%m-%d %H:%M}—{end:%H:%M}",
        "",
        state.get("one_sentence")
        or report.get("concise_report", "AI 未提供状态结论。"),
        "",
        "## 时间核算",
        "",
        "| 类型 | 估计 | 合理范围 |",
        "|---|---:|---:|",
    ]
    for key, label in (
        ("work", "工作"),
        ("rest", "休息"),
        ("other", "其他"),
        ("uncertain", "无法判断"),
    ):
        item = allocation.get(key, {})
        estimate = item.get("estimate_minutes", 0)
        interval = item.get("range_minutes", [estimate, estimate])
        interval_text = (
            f"{interval[0]}—{interval[1]} 分钟"
            if isinstance(interval, list) and len(interval) == 2
            else "未提供"
        )
        lines.append(f"| {label} | {estimate} 分钟 | {interval_text} |")
    lines.extend(
        [
            "",
            "## 碎片化",
            "",
            f"- 等级：{fragmentation.get('level', 'unknown')}",
            f"- 有意义的上下文块：{fragmentation.get('meaningful_context_blocks', 0)}",
            f"- 上下文切换：{fragmentation.get('context_switch_count', 0)} 次",
            f"- 少于一分钟的短块：{fragmentation.get('short_context_blocks', 0)}",
            f"- 至少五分钟的持续块：{fragmentation.get('sustained_context_blocks', 0)}",
            f"- 最长连续上下文：{fragmentation.get('longest_context_minutes', 0)} 分钟",
            "",
            fragmentation.get("interpretation", "没有提供碎片化解释。"),
            "",
            "## 时间线",
            "",
        ]
    )
    timeline = report.get("timeline_summary", [])
    if timeline:
        for item in timeline:
            lines.append(
                f"- {item.get('time_range', '')}｜{item.get('likely_state', '')}"
                f"｜{item.get('minutes', 0)} 分钟："
                + "；".join(item.get("evidence", []))
            )
    else:
        lines.append("- 没有形成可靠时间线。")
    lines.extend(
        [
            "",
            "## 电脑与手机",
            "",
            f"- 电脑：{report.get('computer_summary', '没有可靠解释。')}",
            f"- 手机：{report.get('phone_summary', '没有可靠解释。')}",
            "",
            "## 会改变结论的不确定性",
            "",
        ]
    )
    uncertainties = report.get("material_uncertainties", [])
    if uncertainties:
        lines.extend(f"- {item}" for item in uncertainties[:2])
    else:
        lines.append("- 没有达到报告阈值的不确定性。")
    verification_question = report.get("verification_question", "").strip()
    lines.extend(
        [
            "",
            "## 核验问题",
            "",
            verification_question or "这段状态和时间估计是否符合实际？",
            "",
            "---",
            "",
            "本报告只用于检验 AI 的状态解释能力，不会触发任何自动干预。",
            "",
        ]
    )
    return "\n".join(lines)


def _local_no_activity_report(start: datetime, end: datetime) -> dict[str, Any]:
    period_minutes = round((end - start).total_seconds() / 60, 2)
    return {
        "period": f"{iso_timestamp(start)}/{iso_timestamp(end)}",
        "state_assessment": {
            "label": "unclear",
            "confidence": "low",
            "one_sentence": f"这{period_minutes}分钟没有足够设备活动，状态无法判断。",
        },
        "observed_metrics": {
            "computer_active_minutes": 0.0,
            "computer_afk_minutes": period_minutes,
            "phone_screen_on_minutes": 0.0,
            "no_detected_device_interaction_minutes": period_minutes,
        },
        "estimated_time_allocation": {
            "work": {
                "estimate_minutes": 0.0,
                "range_minutes": [0.0, period_minutes],
                "evidence": [],
            },
            "rest": {
                "estimate_minutes": 0.0,
                "range_minutes": [0.0, period_minutes],
                "evidence": [],
            },
            "other": {
                "estimate_minutes": 0.0,
                "range_minutes": [0.0, period_minutes],
                "evidence": [],
            },
            "uncertain": {
                "estimate_minutes": period_minutes,
                "range_minutes": [0.0, period_minutes],
                "evidence": ["没有足够设备活动证据。"],
            },
            "total_minutes": period_minutes,
        },
        "fragmentation_assessment": {
            "level": "low",
            "meaningful_context_blocks": 0,
            "context_switch_count": 0,
            "short_context_blocks": 0,
            "sustained_context_blocks": 0,
            "longest_context_minutes": 0.0,
            "interpretation": "没有足够活动，不能评价工作碎片化。",
        },
        "timeline_summary": [],
        "computer_summary": "没有检测到足够电脑活动。",
        "phone_summary": "没有检测到足够手机活动。",
        "material_uncertainties": ["无设备交互不能区分休息、离开和离线工作。"],
        "data_quality": {
            "level": "low",
            "material_issues": ["有效活动证据不足。"],
        },
        "concise_report": f"状态不明；{period_minutes}分钟均无法可靠分类。",
        "gentle_suggestions": [],
        "verification_question": "这段时间是在休息、离开设备，还是进行离线活动？",
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
        "schema_version": 2,
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
