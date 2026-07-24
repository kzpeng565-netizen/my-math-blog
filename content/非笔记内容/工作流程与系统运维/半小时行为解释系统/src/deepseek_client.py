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
    "fragmented_work",
    "mixed_work_and_rest",
    "resting",
    "unclear",
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
    request_data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    retries = int(model.get("retries", 2))
    last_error: Exception | None = None

    for attempt in range(retries + 1):
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
        "no_detected_device_interaction_minutes": observed[
            "no_detected_device_interaction_minutes"
        ],
        "confirmed_rest_minutes": observed["confirmed_rest_minutes"],
    }

    deterministic = cross_device_facts["computer_fragmentation_metrics"]
    model_fragmentation = report.setdefault("fragmentation_assessment", {})
    model_fragmentation.update(
        {
            "meaningful_context_blocks": deterministic[
                "meaningful_context_blocks"
            ],
            "context_switch_count": deterministic["context_switch_count"],
            "short_context_blocks": deterministic[
                "short_context_blocks_under_60_seconds"
            ],
            "sustained_context_blocks": deterministic[
                "sustained_context_blocks_at_least_5_minutes"
            ],
            "longest_context_minutes": deterministic["longest_context_minutes"],
        }
    )

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
    report["material_uncertainties"] = report.get(
        "material_uncertainties", []
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
    category_keys = ("work", "rest", "other", "uncertain")
    estimates: dict[str, float] = {}
    for key in category_keys:
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
    if len(estimates) == 4 and abs(sum(estimates.values()) - period_minutes) > 0.2:
        errors.append("工作、休息、其他、无法判断的估计总和不等于时段长度")
    if (
        "rest" in estimates
        and abs(estimates["rest"] - confirmed_rest_minutes) > 0.2
    ):
        errors.append(
            "休息分钟数必须等于跨设备无操作规则确认的confirmed_rest_minutes"
        )

    timeline = report.get("timeline_summary", [])
    timeline_totals = {key: 0.0 for key in category_keys}
    label_to_key = {
        "工作": "work",
        "休息": "rest",
        "其他": "other",
        "无法判断": "uncertain",
    }
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
    if len(estimates) == 4:
        for key in category_keys:
            if abs(timeline_totals[key] - estimates[key]) > 0.2:
                errors.append(f"timeline_summary中的{key}分钟数与时间核算不一致")

    serialized = json.dumps(report, ensure_ascii=False)
    banned_phrases = (
        "ChatGPT的具体交互内容未知",
        "亮屏不代表",
        "心跳事件距离",
        "网页覆盖率仅",
        "手机打断",
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
) -> dict[str, Any]:
    model = settings["model"]
    system_prompt = prompt_path.read_text(encoding="utf-8")
    evidence = {
        "computer_facts": computer_facts,
        "phone_facts": phone_facts,
        "cross_device_facts": cross_device_facts,
    }
    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": "请根据事实层输出状态核验JSON：\n"
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
            report, computer_facts, phone_facts, cross_device_facts
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
