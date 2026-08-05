from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


QUALITY_ORDER = {"low": 0, "medium": 1, "high": 2}
STATE_LABELS = {
    "focused_work",
    "work_with_brief_checkins",
    "work_with_entertainment_detour",
    "work_disrupted_by_entertainment",
    "entertainment",
    "resting",
    "unclear",
}
CATEGORY_KEYS = (
    "work",
    "entertainment",
    "brief_communication",
    "rest",
    "other",
    "uncertain",
)
CATEGORY_LABELS = {
    "work": "工作",
    "entertainment": "娱乐",
    "brief_communication": "通信",
    "rest": "休息",
    "other": "其他",
    "uncertain": "无法判断",
}


def _request_json_report(
    model: dict[str, Any], messages: list[dict[str, str]]
) -> tuple[dict[str, Any], dict[str, Any]]:
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError("DEEPSEEK_API_KEY is not configured")

    payload = {
        "model": model["name"],
        "messages": messages,
        "thinking": {"type": model.get("thinking", "disabled")},
        "response_format": {"type": "json_object"},
        "max_tokens": int(model["max_tokens"]),
        "stream": False,
    }
    retries = int(model.get("retries", 2))
    last_error: Exception | None = None

    for attempt in range(retries + 1):
        request_data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        request = Request(
            model["endpoint"],
            data=request_data,
            method="POST",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )
        try:
            with urlopen(request, timeout=int(model["timeout_seconds"])) as response:
                response_body = json.loads(response.read().decode("utf-8"))
            content = response_body["choices"][0]["message"].get("content", "")
            if not content.strip():
                if (
                    response_body["choices"][0].get("finish_reason") == "length"
                    and payload.get("thinking", {}).get("type") == "enabled"
                ):
                    payload["thinking"] = {"type": "disabled"}
                raise ValueError(
                    "DeepSeek returned empty content "
                    f"(finish_reason={response_body['choices'][0].get('finish_reason')}, "
                    f"usage={response_body.get('usage', {})})"
                )
            report = json.loads(content)
            if not isinstance(report, dict):
                raise ValueError("DeepSeek output is not a JSON object")
            generation = {
                "provider": "DeepSeek",
                "model": response_body.get("model", model["name"]),
                "finish_reason": response_body["choices"][0].get("finish_reason"),
                "usage": response_body.get("usage", {}),
            }
            return report, generation
        except (
            HTTPError,
            URLError,
            TimeoutError,
            KeyError,
            ValueError,
            json.JSONDecodeError,
        ) as error:
            last_error = error
            if attempt < retries:
                time.sleep(2**attempt)
                continue

    raise RuntimeError(
        f"DeepSeek request failed: {type(last_error).__name__}: {last_error}"
    )


def _normalize_report(
    report: dict[str, Any],
    computer_facts: dict[str, Any],
    phone_facts: dict[str, Any],
    cross_device_facts: dict[str, Any],
    semantic_timeline: dict[str, Any],
    mixing_metrics: dict[str, Any],
) -> dict[str, Any]:
    observed = cross_device_facts["time_accounting_observed"]
    overlap = cross_device_facts["overlap_minutes"]
    report["observed_metrics"] = {
        "computer_active_minutes": observed["computer_not_afk_minutes"],
        "computer_afk_minutes": observed["computer_afk_minutes"],
        "phone_screen_on_minutes": observed["phone_screen_on_minutes"],
        "simultaneous_computer_active_phone_on_minutes": overlap[
            "computer_not_afk_and_phone_on"
        ],
        "no_detected_device_interaction_minutes": observed.get(
            "no_detected_device_interaction_minutes", 0
        ),
        "confirmed_rest_minutes": observed["confirmed_rest_minutes"],
    }

    allocation_seconds = {key: 0.0 for key in CATEGORY_KEYS}
    allocation_evidence = {key: [] for key in CATEGORY_KEYS}
    timeline_summary: list[dict[str, Any]] = []
    for segment in semantic_timeline.get("segments", []):
        activity = segment["activity"]
        allocation_seconds[activity] += float(segment["duration_seconds"])
        evidence = [str(item) for item in segment.get("evidence", [])]
        allocation_evidence[activity].extend(evidence)
        start = str(segment["start"])[11:16]
        end = str(segment["end"])[11:16]
        timeline_summary.append(
            {
                "time_range": f"{start}-{end}",
                "likely_state": CATEGORY_LABELS[activity],
                "minutes": round(float(segment["duration_seconds"]) / 60, 2),
                "task": segment.get("task", ""),
                "work_category": segment.get("work_category", ""),
                "relationship_to_work": segment.get(
                    "relationship_to_work", "uncertain"
                ),
                "devices": segment.get("devices", []),
                "evidence": evidence,
                "confidence": segment.get("confidence", "low"),
            }
        )
    report["estimated_time_allocation"] = {
        key: {
            "estimate_minutes": round(allocation_seconds[key] / 60, 2),
            "range_minutes": [
                round(allocation_seconds[key] / 60, 2),
                round(allocation_seconds[key] / 60, 2),
            ],
            "evidence": list(dict.fromkeys(allocation_evidence[key]))[:4],
        }
        for key in CATEGORY_KEYS
    }
    report["estimated_time_allocation"]["total_minutes"] = observed[
        "period_minutes"
    ]
    report["timeline_summary"] = timeline_summary
    report["primary_work_task"] = semantic_timeline.get(
        "primary_work_task", ""
    )

    model_mixing = report.setdefault("mixing_assessment", {})
    interpretation = model_mixing.get("interpretation", "")
    report["mixing_assessment"] = {
        **mixing_metrics,
        "interpretation": interpretation
        or mixing_metrics.get("interpretation_note", ""),
    }
    report.pop("fragmentation_assessment", None)

    allocation = report["estimated_time_allocation"]
    primary_task = report["primary_work_task"] or "未明确主要任务"
    work_minutes = allocation["work"]["estimate_minutes"]
    entertainment_minutes = allocation["entertainment"]["estimate_minutes"]
    communication_minutes = allocation["brief_communication"]["estimate_minutes"]
    rest_minutes = allocation["rest"]["estimate_minutes"]
    deviation_count = mixing_metrics["entertainment_deviation_count"]
    deviation_minutes = mixing_metrics["entertainment_deviation_minutes"]
    longest_deviation = mixing_metrics[
        "longest_entertainment_deviation_minutes"
    ]
    if deviation_count:
        mixing_sentence = (
            f"工作中出现{deviation_count}次超过30秒的娱乐偏离，"
            f"共{deviation_minutes}分钟，最长{longest_deviation}分钟。"
        )
    else:
        mixing_sentence = "没有发现工作过程中超过30秒的娱乐偏离。"
    deterministic_summary = (
        f"主要任务：{primary_task}。工作{work_minutes}分钟，"
        f"娱乐{entertainment_minutes}分钟，通信{communication_minutes}分钟，"
        f"确认休息{rest_minutes}分钟。{mixing_sentence}"
    )
    report["concise_report"] = deterministic_summary
    report.setdefault("state_assessment", {})[
        "one_sentence"
    ] = deterministic_summary

    computer_quality = computer_facts.get("quality", {})
    phone_quality = phone_facts.get("quality", {})
    levels = [
        computer_quality.get("level", "low"),
        phone_quality.get("level", "low"),
    ]
    quality_level = min(levels, key=lambda level: QUALITY_ORDER.get(level, -1))
    material_issues = [
        *computer_quality.get("material_issues", []),
        *phone_quality.get("material_issues", []),
    ]
    report["data_quality"] = {
        "level": quality_level,
        "material_issues": material_issues,
    }
    report["material_uncertainties"] = list(
        dict.fromkeys(
            [
                *semantic_timeline.get("material_uncertainties", []),
                *report.get("material_uncertainties", []),
            ]
        )
    )[:2]
    report["gentle_suggestions"] = []
    return report


def _validate_report(
    report: dict[str, Any],
    period_minutes: float,
    confirmed_rest_minutes: float = 0.0,
) -> list[str]:
    errors: list[str] = []
    state_label = report.get("state_assessment", {}).get("label")
    if state_label not in STATE_LABELS:
        errors.append("state_assessment.label不在允许列表中")

    allocation = report.get("estimated_time_allocation", {})
    estimates: dict[str, float] = {}
    for key in CATEGORY_KEYS:
        item = allocation.get(key, {})
        try:
            estimate = float(item["estimate_minutes"])
            interval = item["range_minutes"]
            lower, upper = float(interval[0]), float(interval[1])
        except (KeyError, TypeError, ValueError, IndexError):
            errors.append(f"estimated_time_allocation.{key}格式错误")
            continue
        estimates[key] = estimate
        if not lower <= estimate <= upper:
            errors.append(f"{key}的估计值不在range_minutes内")
    if (
        len(estimates) == len(CATEGORY_KEYS)
        and abs(sum(estimates.values()) - period_minutes) > 0.2
    ):
        errors.append("各类语义时间估计总和不等于时段长度")
    if (
        "rest" in estimates
        and abs(estimates["rest"] - confirmed_rest_minutes) > 0.2
    ):
        errors.append(
            "休息分钟数必须等于跨设备无操作规则确认的confirmed_rest_minutes"
        )

    timeline = report.get("timeline_summary", [])
    timeline_totals = {key: 0.0 for key in CATEGORY_KEYS}
    label_to_key = {value: key for key, value in CATEGORY_LABELS.items()}
    timeline_total = 0.0
    for item in timeline:
        try:
            minutes = float(item["minutes"])
        except (KeyError, TypeError, ValueError):
            errors.append("timeline_summary存在无效分钟数")
            continue
        timeline_total += minutes
        key = label_to_key.get(item.get("likely_state"))
        if key:
            timeline_totals[key] += minutes
        else:
            errors.append("timeline_summary使用了未允许的状态标签")
    if abs(timeline_total - period_minutes) > 0.2:
        errors.append("timeline_summary分钟数总和不等于时段长度")
    if len(estimates) == len(CATEGORY_KEYS):
        for key in CATEGORY_KEYS:
            if abs(timeline_totals[key] - estimates[key]) > 0.2:
                errors.append(f"timeline_summary中的{key}分钟数与时间核算不一致")

    serialized = json.dumps(report, ensure_ascii=False)
    banned_phrases = (
        "ChatGPT的具体交互内容未知",
        "亮屏不代表",
        "心跳事件距离",
        "网页覆盖率仅",
        "手机打断",
        "上下文切换频繁",
        "高度碎片化",
    )
    for phrase in banned_phrases:
        if phrase in serialized:
            errors.append(f"包含无信息量或无证据表述：{phrase}")
    return errors


def interpret_with_deepseek(
    settings: dict[str, Any],
    prompt_path: Path,
    computer_facts: dict[str, Any],
    phone_facts: dict[str, Any],
    cross_device_facts: dict[str, Any],
    semantic_timeline: dict[str, Any],
    mixing_metrics: dict[str, Any],
    obsidian_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    model = settings["model"]
    system_prompt = prompt_path.read_text(encoding="utf-8")
    evidence = {
        "computer_facts": computer_facts,
        "phone_facts": phone_facts,
        "cross_device_facts": cross_device_facts,
        "semantic_timeline": semantic_timeline,
        "deterministic_work_entertainment_mixing": mixing_metrics,
        "read_only_obsidian_context": obsidian_context,
    }
    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": "请根据语义时间线和确定性混杂指标输出状态核验JSON：\n"
            + json.dumps(evidence, ensure_ascii=False, separators=(",", ":")),
        },
    ]

    correction_attempts = 0
    generation: dict[str, Any] = {}
    report: dict[str, Any] = {}
    errors: list[str] = []
    period_minutes = float(
        cross_device_facts["time_accounting_observed"]["period_minutes"]
    )
    confirmed_rest_minutes = float(
        cross_device_facts["time_accounting_observed"]["confirmed_rest_minutes"]
    )
    for correction_attempts in range(3):
        report, generation = _request_json_report(model, messages)
        report = _normalize_report(
            report,
            computer_facts,
            phone_facts,
            cross_device_facts,
            semantic_timeline,
            mixing_metrics,
        )
        errors = _validate_report(
            report, period_minutes, confirmed_rest_minutes
        )
        if not errors:
            break
        messages.extend(
            [
                {
                    "role": "assistant",
                    "content": json.dumps(report, ensure_ascii=False),
                },
                {
                    "role": "user",
                    "content": (
                        "上一个JSON未通过一致性检查。请保持事实不变，修正以下问题，"
                        "并返回完整JSON，不要解释：\n- "
                        + "\n- ".join(errors)
                    ),
                },
            ]
        )

    report["_validation"] = {
        "passed": not errors,
        "errors": errors,
        "correction_attempts": correction_attempts,
    }
    report["_generation"] = generation
    return report
