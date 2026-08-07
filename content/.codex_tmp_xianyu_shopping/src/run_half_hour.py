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
from behavior_advisor import build_shadow_candidate
from behavior_statistics import update_statistics
from computer_intervention import (
    build_computer_intervention_request,
    save_computer_intervention_request,
)
from cross_device import compare_devices
from deepseek_client import interpret_with_deepseek
from fact_tagger import build_tagged_fact_view
from notifications import NtfyNotifier
from phone_facts import extract_phone_facts
from obsidian_context import load_obsidian_context
from tablet_facts import extract_tablet_facts
from pushplus_client import send_report_via_wechat
from semantic_analysis import (
    calculate_work_entertainment_mixing,
    extract_semantic_timeline_with_deepseek,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SETTINGS = PROJECT_ROOT / "config" / "settings.json"
DEFAULT_PROMPT = PROJECT_ROOT / "prompts" / "half-hour-interpreter.md"
DEFAULT_SEGMENT_PROMPT = PROJECT_ROOT / "prompts" / "semantic-segmenter.md"
DEFAULT_TAG_RULES = PROJECT_ROOT / "config" / "tag_rules.json"


def _should_skip_push_for_inactive_devices(
    computer: dict[str, Any],
    phone: dict[str, Any],
    tablet: dict[str, Any],
    minimum_evidence_seconds: float,
) -> bool:
    computer_active_seconds = (
        float(computer.get("activity", {}).get("not_afk_minutes", 0)) * 60
    )
    phone_on_seconds = (
        float(phone.get("screen", {}).get("on_minutes", 0)) * 60
    )
    tablet_on_seconds = (
        float(tablet.get("screen", {}).get("on_minutes", 0)) * 60
    )
    return (
        computer_active_seconds < minimum_evidence_seconds
        and phone_on_seconds < minimum_evidence_seconds
        and tablet_on_seconds < minimum_evidence_seconds
    )


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
    mixing = report.get("mixing_assessment", {})
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
        ("entertainment", "娱乐"),
        ("shopping", "购物"),
        ("brief_communication", "通信"),
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
            "## 工作—娱乐混杂",
            "",
            f"- 等级：{mixing.get('level', 'unknown')}",
            f"- 超过30秒的娱乐偏离：{mixing.get('entertainment_deviation_count', 0)} 次",
            f"- 娱乐偏离总时长：{mixing.get('entertainment_deviation_minutes', 0)} 分钟",
            f"- 最长娱乐偏离：{mixing.get('longest_entertainment_deviation_minutes', 0)} 分钟",
            f"- 工作与娱乐转换：{mixing.get('work_entertainment_transition_count', 0)} 次",
            f"- 通信（不计入娱乐混杂）：{mixing.get('brief_communication_minutes', 0)} 分钟",
            f"- 同任务工具切换（不计分）：{mixing.get('same_task_tool_switches_not_scored', 0)} 次",
            f"- 最长连续工作：{mixing.get('longest_continuous_work_minutes', 0)} 分钟",
            "",
            mixing.get("interpretation", "没有提供工作—娱乐混杂解释。"),
            "",
            "## 主要时间线",
            "",
        ]
    )
    timeline = report.get("timeline_summary", [])
    notable_timeline = [
        item
        for item in timeline
        if float(item.get("minutes", 0)) >= 0.5
        or item.get("likely_state") in {"娱乐", "休息", "无法判断"}
    ]
    if notable_timeline:
        for item in notable_timeline:
            evidence = "；".join(item.get("evidence", [])[:2])
            lines.append(
                f"- {item.get('time_range', '')}｜{item.get('likely_state', '')}"
                f"｜{item.get('minutes', 0)} 分钟"
                f"｜{item.get('task', '')}"
                + (f"：{evidence}" if evidence else "")
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
            f"- 平板（辅助数据）：{report.get('tablet_summary', '没有可靠解释。')}",
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


def _compact_text(value: Any, limit: int) -> str:
    text = " ".join(str(value or "").split())
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def build_half_hour_reminder_check_message(
    intervention: dict[str, Any],
    start: datetime,
    end: datetime,
) -> tuple[str, str]:
    observations = intervention.get("observations", {})
    reasons = intervention.get("trigger_reasons", [])
    task = intervention.get("recommended_task") or {}
    title = f"半小时提醒检测系统 {start:%H:%M}—{end:%H:%M}"
    lines = [
        "半小时提醒检测系统判断：这个窗口需要介入提醒。",
        "",
        "触发原因：" + ("、".join(reasons) if reasons else "无"),
        (
            "观察值："
            f"高刺激 {observations.get('high_stimulation_minutes', 0)} 分钟；"
            f"本窗口有意义活动 {observations.get('meaningful_minutes', 0)} 分钟；"
            f"60分钟有意义活动 {observations.get('meaningful_minutes_60m', 0)} 分钟；"
            f"确认休息 {observations.get('confirmed_rest_minutes', 0)} 分钟。"
        ),
        (
            f"上下文：{intervention.get('context_source', 'unavailable')}；"
            f"年龄 {intervention.get('context_age_minutes')} 分钟。"
        ),
    ]
    if task:
        lines.append("候选下一步：" + _compact_text(task.get("title"), 180))
    lines.append("这里只发送提醒检测结果，不执行干预、不修改任务。")
    return title, "\n".join(lines)


def send_half_hour_reminder_check_via_ntfy(
    intervention: dict[str, Any],
    start: datetime,
    end: datetime,
    *,
    notifier: NtfyNotifier | None = None,
    no_push: bool = False,
) -> dict[str, Any]:
    if no_push:
        return {
            "status": "skipped",
            "provider": "ntfy",
            "reason": "--no-push was supplied",
            "would_intervene": bool(intervention.get("would_intervene")),
        }
    if not intervention.get("would_intervene"):
        return {
            "status": "skipped",
            "provider": "ntfy",
            "reason": "shadow_candidate_would_not_intervene",
            "would_intervene": False,
        }
    title, message = build_half_hour_reminder_check_message(intervention, start, end)
    result = (notifier or NtfyNotifier()).send(
        title=title,
        message=message,
        priority="high",
        tags=["warning"],
    )
    payload = result.as_dict()
    payload["would_intervene"] = True
    return payload


def _local_no_activity_report(
    start: datetime, end: datetime, cross: dict[str, Any]
) -> dict[str, Any]:
    period_minutes = round((end - start).total_seconds() / 60, 2)
    observed = cross["time_accounting_observed"]
    time_acc = cross["time_accounting_observed"]
    confirmed_rest = float(time_acc["confirmed_rest_minutes"])
    uncertain_minutes = round(period_minutes - confirmed_rest, 2)
    return {
        "period": f"{iso_timestamp(start)}/{iso_timestamp(end)}",
        "state_assessment": {
            "label": "resting"
            if confirmed_rest >= period_minutes - 0.2
            else "unclear",
            "confidence": "high" if confirmed_rest else "low",
            "one_sentence": (
                f"跨设备无操作规则确认休息{confirmed_rest}分钟，"
                f"其余{uncertain_minutes}分钟无法判断。"
            ),
        },
        "observed_metrics": {
            "computer_active_minutes": time_acc["computer_not_afk_minutes"],
            "computer_afk_minutes": time_acc["computer_afk_minutes"],
            "phone_screen_on_minutes": time_acc["phone_screen_on_minutes"],
            "simultaneous_computer_active_phone_on_minutes": round(
                cross.get("overlap_minutes", {}).get("computer_not_afk_and_phone_on", 0), 2
            ),
            "no_detected_device_interaction_minutes": observed.get(
                "no_primary_device_interaction_minutes",
                observed.get("no_detected_device_interaction_minutes", 0)
            ),
            "confirmed_rest_minutes": confirmed_rest,
        },
        "estimated_time_allocation": {
            "work": {
                "estimate_minutes": 0.0,
                "range_minutes": [0.0, period_minutes],
                "evidence": [],
            },
            "entertainment": {
                "estimate_minutes": 0.0,
                "range_minutes": [0.0, 0.0],
                "evidence": [],
            },
            "shopping": {
                "estimate_minutes": 0.0,
                "range_minutes": [0.0, 0.0],
                "evidence": [],
            },
            "brief_communication": {
                "estimate_minutes": 0.0,
                "range_minutes": [0.0, 0.0],
                "evidence": [],
            },
            "rest": {
                "estimate_minutes": confirmed_rest,
                "range_minutes": [confirmed_rest, confirmed_rest],
                "evidence": ["符合跨设备连续无操作休息规则。"]
                if confirmed_rest
                else [],
            },
            "other": {
                "estimate_minutes": 0.0,
                "range_minutes": [0.0, period_minutes],
                "evidence": [],
            },
            "uncertain": {
                "estimate_minutes": uncertain_minutes,
                "range_minutes": [uncertain_minutes, uncertain_minutes],
                "evidence": ["没有足够设备活动证据。"],
            },
            "total_minutes": period_minutes,
        },
        "mixing_assessment": {
            "level": "none",
            "entertainment_deviation_count": 0,
            "entertainment_deviation_minutes": 0.0,
            "all_entertainment_minutes": 0.0,
            "longest_entertainment_deviation_minutes": 0.0,
            "work_entertainment_transition_count": 0,
            "brief_communication_minutes": 0.0,
            "longest_continuous_work_minutes": 0.0,
            "same_task_tool_switches_not_scored": 0,
            "raw_foreground_context_switches_not_scored": 0,
            "deviations": [],
            "interpretation": "没有足够活动，未发现工作—娱乐混杂。",
        },
        "timeline_summary": [],
        "computer_summary": "没有检测到足够电脑活动。",
        "phone_summary": "没有检测到足够手机活动。",
        "material_uncertainties": ["无设备交互不能区分休息、离开和离线工作。"],
        "data_quality": {
            "level": "low",
            "material_issues": ["有效活动证据不足。"],
        },
        "concise_report": (
            f"确认休息{confirmed_rest}分钟，"
            f"其余{uncertain_minutes}分钟无法可靠分类。"
        ),
        "gentle_suggestions": [],
        "verification_question": "这段时间是在休息、离开设备，还是进行离线活动？",
        "_generation": {"provider": "local_rule", "model": None},
    }


def _local_semantic_failure_report(
    start: datetime, end: datetime, cross: dict[str, Any], errors: list[str]
) -> dict[str, Any]:
    report = _local_no_activity_report(start, end, cross)
    period_minutes = round((end - start).total_seconds() / 60, 2)
    confirmed_rest = float(
        cross["time_accounting_observed"]["confirmed_rest_minutes"]
    )
    uncertain_minutes = round(period_minutes - confirmed_rest, 2)
    report["state_assessment"] = {
        "label": "unclear",
        "confidence": "low",
        "one_sentence": (
            f"设备事实已采集，但AI时间段解释未通过校验；"
            f"确认休息{confirmed_rest}分钟，其余{uncertain_minutes}分钟暂不归类。"
        ),
    }
    report["computer_summary"] = "电脑事实已保存，等待语义时间段重新解释。"
    report["phone_summary"] = "手机事实已保存，等待语义时间段重新解释。"
    report["tablet_summary"] = "平板事实已保存，等待语义时间段重新解释。"
    report["material_uncertainties"] = ["AI语义时间线未通过一致性检查。"]
    report["data_quality"]["material_issues"] = [
        *report["data_quality"].get("material_issues", []),
        "AI语义时间线未通过一致性检查。",
    ]
    report["concise_report"] = report["state_assessment"]["one_sentence"]
    report["verification_question"] = "这段时间的主要活动是什么？"
    report["_validation"] = {"passed": False, "errors": errors}
    return report


def run(arguments) -> dict[str, Any]:
    settings_path = Path(arguments.settings).resolve()
    settings = load_json(settings_path)
    start, end = _parse_period(arguments, settings["timezone"])
    output_root = Path(settings["output_root"])
    day = start.strftime("%Y-%m-%d")
    period_id = start.strftime("%H-%M")

    computer_path = output_root / "computer_facts" / day / f"{period_id}.json"
    phone_path = output_root / "phone_facts" / day / f"{period_id}.json"
    tablet_path = output_root / "tablet_facts" / day / f"{period_id}.json"
    combined_path = output_root / "combined_facts" / day / f"{period_id}.json"
    tagged_path = output_root / "tagged_facts" / day / f"{period_id}.json"
    semantic_path = (
        output_root / "semantic_timelines" / day / f"{period_id}.json"
    )
    mixing_path = output_root / "mixing_metrics" / day / f"{period_id}.json"
    report_json_path = output_root / "ai_reports" / day / f"{period_id}.json"
    report_md_path = output_root / "ai_reports" / day / f"{period_id}.md"
    context_archive_path = (
        output_root / "context_snapshots" / day / f"{period_id}.json"
    )
    intervention_path = (
        output_root / "intervention_candidates" / day / f"{period_id}.json"
    )
    half_hour_reminder_check_receipt_path = (
        output_root
        / "ntfy_receipts"
        / "half_hour_reminder_check"
        / day
        / f"{period_id}.json"
    )

    if report_json_path.exists() and not arguments.force:
        return {
            "status": "already_processed",
            "report": str(report_json_path),
            "period": f"{iso_timestamp(start)}/{iso_timestamp(end)}",
        }

    computer = extract_computer_facts(settings, start, end)
    phone = extract_phone_facts(settings, start, end)
    tablet = extract_tablet_facts(settings, start, end)
    suppress_inactive_push = _should_skip_push_for_inactive_devices(
        computer,
        phone,
        tablet,
        float(settings["processing"]["minimum_evidence_seconds"]),
    )
    cross = compare_devices(computer, phone, settings, tablet)
    atomic_write_json(computer_path, computer)
    atomic_write_json(phone_path, phone)
    atomic_write_json(tablet_path, tablet)
    context = load_obsidian_context(
        Path(
            settings.get(
                "obsidian_context_path",
                "/home/conrad/workspace/behavior-context-sync/context_snapshot.json",
            )
        ),
        output_root / "context_cache" / "current.json",
    )
    atomic_write_json(context_archive_path, context)

    tagged: dict[str, Any] | None = None
    if suppress_inactive_push:
        semantic = {
            "schema_version": 1,
            "source": "local_no_activity",
            "period": computer["period"],
            "primary_work_task": "",
            "segments": [],
            "material_uncertainties": ["有效设备活动不足，未调用AI解释时间段。"],
            "_validation": {"passed": True, "errors": []},
            "_generation": {"provider": "local_rule", "model": None},
        }
        mixing = calculate_work_entertainment_mixing(
            semantic, cross, settings
        )
        report = _local_no_activity_report(start, end, cross)
    else:
        context_minutes = int(
            settings["processing"].get("semantic_context_minutes", 5)
        )
        context_start = start - timedelta(minutes=context_minutes)
        context_end = end + timedelta(minutes=context_minutes)
        context_computer = extract_computer_facts(
            settings, context_start, context_end
        )
        context_phone = extract_phone_facts(settings, context_start, context_end)
        context_tablet = extract_tablet_facts(
            settings, context_start, context_end
        )
        try:
            tagged = build_tagged_fact_view(
                settings,
                Path(arguments.tag_rules).resolve(),
                start,
                end,
                context_computer,
                context_phone,
                context_tablet,
                cross,
            )
            atomic_write_json(tagged_path, tagged)
            semantic = extract_semantic_timeline_with_deepseek(
                settings,
                Path(arguments.segment_prompt).resolve(),
                tagged,
                context.get("ai_context") if context.get("available") else None,
            )
        except Exception as error:
            semantic = {
                "schema_version": 1,
                "source": "ai_error_fallback",
                "period": computer["period"],
                "primary_work_task": "",
                "segments": [],
                "material_uncertainties": [
                    "AI语义时间线请求失败；设备事实已保留。"
                ],
                "_validation": {
                    "passed": False,
                    "errors": [f"{type(error).__name__}: {error}"],
                },
                "_generation": {"provider": "local_fallback", "model": None},
            }
        mixing = calculate_work_entertainment_mixing(semantic, cross, settings)
        if semantic.get("_validation", {}).get("passed"):
            report = interpret_with_deepseek(
                settings,
                Path(arguments.prompt).resolve(),
                computer,
                phone,
                cross,
                semantic,
                mixing,
                context.get("ai_context") if context.get("available") else None,
            )
        else:
            report = _local_semantic_failure_report(
                start,
                end,
                cross,
                semantic.get("_validation", {}).get("errors", []),
            )

    atomic_write_json(semantic_path, semantic)
    atomic_write_json(mixing_path, mixing)
    combined = {
        "schema_version": 4,
        "period": computer["period"],
        "computer_facts_file": str(computer_path),
        "phone_facts_file": str(phone_path),
        "tablet_facts_file": str(tablet_path),
        "tagged_facts_file": str(tagged_path) if tagged is not None else None,
        "semantic_timeline_file": str(semantic_path),
        "mixing_metrics_file": str(mixing_path),
        "cross_device_facts": cross,
    }
    atomic_write_json(combined_path, combined)
    previous_candidates: list[dict[str, Any]] = []
    candidate_dir = output_root / "intervention_candidates" / day
    for previous_path in sorted(candidate_dir.glob("*.json"))[-2:]:
        if previous_path != intervention_path:
            try:
                previous_candidates.append(load_json(previous_path))
            except (OSError, ValueError):
                pass
    intervention = build_shadow_candidate(
        settings, end, semantic, mixing, cross, context, previous_candidates
    )
    atomic_write_json(intervention_path, intervention)
    computer_intervention_request = None
    computer_intervention_request_path = None
    if not arguments.no_push:
        computer_intervention_request = build_computer_intervention_request(
            settings, start, end, intervention, semantic
        )
        if computer_intervention_request is not None:
            computer_intervention_request_path = save_computer_intervention_request(
                output_root,
                computer_intervention_request,
            )

    atomic_write_json(report_json_path, report)
    atomic_write_text(report_md_path, _report_markdown(report, start, end))
    statistics = update_statistics(output_root, start.date())
    if arguments.no_push:
        delivery = {
            "status": "skipped",
            "channel": "wechat",
            "reason": "--no-push was supplied",
        }
    elif suppress_inactive_push:
        delivery = {
            "status": "skipped",
            "channel": "wechat",
            "reason": "all_devices_inactive",
            "detail": (
                "电脑无非AFK活动，且手机和平板均无亮屏证据；"
                "报告已归档但不发送通知。"
            ),
        }
    else:
        delivery = send_report_via_wechat(
            report, start, end, intervention
        )
    half_hour_reminder_check_delivery = send_half_hour_reminder_check_via_ntfy(
        intervention,
        start,
        end,
        no_push=arguments.no_push or suppress_inactive_push,
    )
    receipt_path = output_root / "pushplus_receipts" / day / f"{period_id}.json"
    atomic_write_json(receipt_path, delivery)
    atomic_write_json(
        half_hour_reminder_check_receipt_path,
        half_hour_reminder_check_delivery,
    )
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
        "tablet_facts": str(tablet_path),
        "combined_facts": str(combined_path),
        "tagged_facts": str(tagged_path) if tagged is not None else None,
        "semantic_timeline": str(semantic_path),
        "mixing_metrics": str(mixing_path),
        "context_snapshot": str(context_archive_path),
        "context_source": context.get("context_source"),
        "intervention_candidate": str(intervention_path),
        "computer_intervention_request": str(computer_intervention_request_path)
        if computer_intervention_request_path is not None
        else None,
        "daily_statistics": str(statistics["daily"]),
        "weekly_statistics": str(statistics["weekly"]),
        "report_json": str(report_json_path),
        "report_markdown": str(report_md_path),
        "model": report.get("_generation", {}).get("model"),
        "pushplus": delivery,
        "half_hour_reminder_check_ntfy": half_hour_reminder_check_delivery,
        "push_suppressed_for_inactivity": suppress_inactive_push,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate one half-hour behavior report")
    parser.add_argument("--settings", default=str(DEFAULT_SETTINGS))
    parser.add_argument("--prompt", default=str(DEFAULT_PROMPT))
    parser.add_argument(
        "--segment-prompt", default=str(DEFAULT_SEGMENT_PROMPT)
    )
    parser.add_argument("--tag-rules", default=str(DEFAULT_TAG_RULES))
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
