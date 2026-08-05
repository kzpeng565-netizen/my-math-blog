from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


PUSHPLUS_ENDPOINT = "https://www.pushplus.plus/send"
PUSHPLUS_CHANNEL = "wechat"
PUSHPLUS_TEMPLATE = "markdown"


def _compact_text(value: Any, limit: int) -> str:
    text = " ".join(str(value or "").split())
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def build_wechat_message(
    report: dict[str, Any],
    start: datetime,
    end: datetime,
    shadow_candidate: dict[str, Any] | None = None,
) -> tuple[str, str]:
    quality = report.get("data_quality", {})
    level = quality.get("level", "unknown")
    issues = quality.get("material_issues", [])
    state = report.get("state_assessment", {})
    allocation = report.get("estimated_time_allocation", {})
    mixing = report.get("mixing_assessment", {})
    summary = _compact_text(report.get("concise_report"), 650)
    question = _compact_text(report.get("verification_question"), 240)

    title = f"行为核验 {start:%H:%M}—{end:%H:%M}"
    lines = [
        "## AI 对这半小时的理解",
        "",
        summary or "没有形成可靠解释。",
        "",
        f"**状态：** `{state.get('label', 'unclear')}`",
        (
            f"**时间估计：** 工作 {allocation.get('work', {}).get('estimate_minutes', 0)} 分钟"
            f"｜娱乐 {allocation.get('entertainment', {}).get('estimate_minutes', 0)} 分钟"
            f"｜通信 {allocation.get('brief_communication', {}).get('estimate_minutes', 0)} 分钟"
            f"｜休息 {allocation.get('rest', {}).get('estimate_minutes', 0)} 分钟"
            f"｜其他 {allocation.get('other', {}).get('estimate_minutes', 0)} 分钟"
            f"｜无法判断 {allocation.get('uncertain', {}).get('estimate_minutes', 0)} 分钟"
        ),
        (
            f"**工作—娱乐混杂：** {mixing.get('level', 'unknown')}"
            f"｜娱乐偏离 {mixing.get('entertainment_deviation_count', 0)} 次"
            f"｜共 {mixing.get('entertainment_deviation_minutes', 0)} 分钟"
            f"｜最长 {mixing.get('longest_entertainment_deviation_minutes', 0)} 分钟"
        ),
        (
            f"**不计为娱乐偏离：** 通信 {mixing.get('brief_communication_minutes', 0)} 分钟"
            f"｜同任务工具切换 {mixing.get('same_task_tool_switches_not_scored', 0)} 次"
        ),
        "",
        f"**数据质量：** `{level}`",
    ]
    if issues:
        lines.extend(
            [
                "",
                "**主要不确定性：**",
                *[f"- {_compact_text(item, 180)}" for item in issues[:2]],
            ]
        )
    lines.extend(["", "**请核验：**"])
    if question:
        lines.append(question)
    else:
        lines.append("这段解释整体是否符合实际？")
    if shadow_candidate is not None:
        observations = shadow_candidate.get("observations", {})
        reasons = shadow_candidate.get("trigger_reasons", [])
        recommended = shadow_candidate.get("recommended_task")
        lines.extend(
            [
                "",
                "## 影子判断",
                "",
                (
                    "**如果正式模式已启用：** "
                    + ("会建议干预" if shadow_candidate.get("would_intervene") else "不会干预")
                ),
                "**触发原因：** " + ("、".join(reasons) if reasons else "无"),
                (
                    f"**观察值：** 高刺激 {observations.get('high_stimulation_minutes', 0)} 分钟"
                    f"｜本窗口有意义活动 {observations.get('meaningful_minutes', 0)} 分钟"
                    f"｜60分钟有意义活动 {observations.get('meaningful_minutes_60m', 0)} 分钟"
                    f"｜确认休息 {observations.get('confirmed_rest_minutes', 0)} 分钟"
                ),
                (
                    f"**上下文：** {shadow_candidate.get('context_source', 'unavailable')}"
                    f"｜年龄 {shadow_candidate.get('context_age_minutes')} 分钟"
                ),
            ]
        )
        if recommended:
            lines.append(
                "**候选下一步：** "
                + _compact_text(recommended.get("title"), 180)
                + f"（{recommended.get('priority', 'normal')}）"
            )
        lines.append("> 这里只展示影子判断结果，没有执行干预或修改任务。")
    lines.extend(
        [
            "",
            "请在 Codex 中反馈：**正确 / 部分正确 / 错误**，需要时补一句实际情况。",
            "",
            "> 当前仅用于检验 AI 的理解，不会触发屏蔽、提醒或计划修改。",
        ]
    )
    return title, "\n".join(lines)


def send_report_via_wechat(
    report: dict[str, Any],
    start: datetime,
    end: datetime,
    shadow_candidate: dict[str, Any] | None = None,
    *,
    timeout_seconds: int = 20,
    retries: int = 1,
) -> dict[str, Any]:
    token = os.environ.get("PUSHPLUS_TOKEN")
    if not token:
        return {
            "status": "skipped",
            "channel": PUSHPLUS_CHANNEL,
            "reason": "PUSHPLUS_TOKEN is not configured",
        }

    title, content = build_wechat_message(
        report, start, end, shadow_candidate
    )
    return send_markdown_via_wechat(
        title,
        content,
        timeout_seconds=timeout_seconds,
        retries=retries,
    )


def send_markdown_via_wechat(
    title: str,
    content: str,
    *,
    timeout_seconds: int = 20,
    retries: int = 1,
) -> dict[str, Any]:
    token = os.environ.get("PUSHPLUS_TOKEN")
    if not token:
        return {
            "status": "skipped",
            "channel": PUSHPLUS_CHANNEL,
            "reason": "PUSHPLUS_TOKEN is not configured",
        }
    payload = {
        "token": token,
        "title": title,
        "content": content,
        "template": PUSHPLUS_TEMPLATE,
        "channel": PUSHPLUS_CHANNEL,
    }
    request_data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    last_error: Exception | None = None

    for attempt in range(retries + 1):
        request = Request(
            PUSHPLUS_ENDPOINT,
            data=request_data,
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        try:
            with urlopen(request, timeout=timeout_seconds) as response:
                response_body = json.loads(response.read().decode("utf-8"))
            if response_body.get("code") != 200:
                raise RuntimeError(
                    f"PushPlus rejected request: code={response_body.get('code')}"
                )
            return {
                "status": "accepted",
                "channel": PUSHPLUS_CHANNEL,
                "template": PUSHPLUS_TEMPLATE,
                "message_id": response_body.get("data"),
                "title": title,
            }
        except (
            HTTPError,
            URLError,
            TimeoutError,
            ValueError,
            json.JSONDecodeError,
            RuntimeError,
        ) as error:
            last_error = error
            if attempt < retries:
                time.sleep(2**attempt)
                continue

    return {
        "status": "failed",
        "channel": PUSHPLUS_CHANNEL,
        "error": f"{type(last_error).__name__}: {last_error}",
    }


def build_statistics_message(
    statistics: dict[str, Any], kind: str
) -> tuple[str, str]:
    minutes = statistics.get("estimated_minutes", {})
    mixing = statistics.get("work_entertainment_mixing", {})
    candidates = statistics.get("shadow_candidates", {})
    label = "每日" if kind == "daily" else "每周"
    title = f"{label}行为统计 {statistics.get('period', '')}"
    lines = [
        f"## {label}行为统计",
        "",
        f"**统计周期：** {statistics.get('period', '')}",
        f"**有效半小时报告：** {statistics.get('report_count', 0)} 份",
        "",
        (
            f"**时间估计：** 工作 {minutes.get('work', 0)} 分钟"
            f"｜娱乐 {minutes.get('entertainment', 0)} 分钟"
            f"｜通信 {minutes.get('brief_communication', 0)} 分钟"
            f"｜休息 {minutes.get('rest', 0)} 分钟"
            f"｜其他 {minutes.get('other', 0)} 分钟"
            f"｜无法判断 {minutes.get('uncertain', 0)} 分钟"
        ),
        (
            f"**工作—娱乐混杂：** 娱乐偏离 {mixing.get('deviation_count', 0)} 次"
            f"｜共 {mixing.get('deviation_minutes', 0)} 分钟"
        ),
        (
            f"**影子判断：** 共 {candidates.get('candidate_count', 0)} 个窗口"
            f"｜其中 {candidates.get('would_intervene_count', 0)} 个会建议干预"
            f"｜PushPlus 已送达 {candidates.get('push_count', 0)} 个窗口"
        ),
        "",
        "> " + statistics.get("interpretation_warning", ""),
        "",
        "请重点检查：是否把正常数学学习或合理休息误判成低效，候选任务是否符合实际规划。",
    ]
    return title, "\n".join(lines)


def send_statistics_via_wechat(
    statistics: dict[str, Any], kind: str
) -> dict[str, Any]:
    title, content = build_statistics_message(statistics, kind)
    return send_markdown_via_wechat(title, content)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Send an existing behavior report through PushPlus WeChat"
    )
    parser.add_argument("report", type=Path)
    arguments = parser.parse_args()
    report = json.loads(arguments.report.read_text(encoding="utf-8"))
    start_text, end_text = report["period"].split("/", 1)
    result = send_report_via_wechat(
        report,
        datetime.fromisoformat(start_text),
        datetime.fromisoformat(end_text),
    )
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["status"] == "accepted" else 1


if __name__ == "__main__":
    raise SystemExit(main())
