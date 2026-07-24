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
    report: dict[str, Any], start: datetime, end: datetime
) -> tuple[str, str]:
    quality = report.get("data_quality", {})
    level = quality.get("level", "unknown")
    issues = quality.get("material_issues", [])
    state = report.get("state_assessment", {})
    allocation = report.get("estimated_time_allocation", {})
    fragmentation = report.get("fragmentation_assessment", {})
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
            f"｜休息 {allocation.get('rest', {}).get('estimate_minutes', 0)} 分钟"
            f"｜无法判断 {allocation.get('uncertain', {}).get('estimate_minutes', 0)} 分钟"
        ),
        (
            f"**碎片化：** {fragmentation.get('level', 'unknown')}"
            f"｜切换 {fragmentation.get('context_switch_count', 0)} 次"
            f"｜最长连续 {fragmentation.get('longest_context_minutes', 0)} 分钟"
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

    title, content = build_wechat_message(report, start, end)
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
