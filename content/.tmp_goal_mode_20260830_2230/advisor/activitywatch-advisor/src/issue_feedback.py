from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from common import atomic_write_json, atomic_write_text


ISSUE_CATEGORIES = {
    "ai_suggestion_quality": "AI建议质量",
    "data_wrong_or_missing": "数据明显不对",
    "web_ui": "网页显示/交互问题",
    "notification": "通知推送问题",
    "rule_mismatch": "规则不符合习惯",
    "security_or_access": "安全或访问问题",
    "docs_or_handoff": "文档或交接问题",
    "other": "其他",
}

ISSUE_SEVERITIES = {
    "low": "低：之后再看",
    "medium": "中：影响体验",
    "high": "高：影响判断",
    "blocking": "阻塞：功能不能用",
}

MAX_MESSAGE_CHARS = 2000
MAX_FIELD_CHARS = 240


def _now(now: datetime | None = None) -> datetime:
    current = now or datetime.now(ZoneInfo("Asia/Shanghai"))
    if current.tzinfo is None:
        current = current.replace(tzinfo=ZoneInfo("Asia/Shanghai"))
    return current.astimezone(ZoneInfo("Asia/Shanghai"))


def _clean(value: Any, limit: int = MAX_FIELD_CHARS) -> str:
    return " ".join(str(value or "").replace("\x00", "").split())[:limit]


def _message(value: Any) -> str:
    text = str(value or "").replace("\x00", "").strip()
    return text[:MAX_MESSAGE_CHARS]


def _issue_id(current: datetime) -> str:
    return current.strftime("%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:8]


def receive_issue_feedback(
    payload: dict[str, Any],
    *,
    output_root: Path,
    user_agent: str = "",
    now: datetime | None = None,
) -> dict[str, Any]:
    current = _now(now)
    category = _clean(payload.get("category")) or "other"
    if category not in ISSUE_CATEGORIES:
        category = "other"
    severity = _clean(payload.get("severity")) or "medium"
    if severity not in ISSUE_SEVERITIES:
        severity = "medium"
    message = _message(payload.get("message"))
    if not message:
        raise ValueError("message is required")

    issue = {
        "issue_id": _issue_id(current),
        "created_at": current.isoformat(timespec="seconds"),
        "category": category,
        "category_label": ISSUE_CATEGORIES[category],
        "severity": severity,
        "severity_label": ISSUE_SEVERITIES[severity],
        "message": message,
        "page": _clean(payload.get("page")),
        "suggestion_id": _clean(payload.get("suggestion_id")),
        "report_path": _clean(payload.get("report_path")),
        "status": "open",
        "user_agent": _clean(user_agent, 500),
    }
    raw_path = (
        output_root
        / "issue_feedback"
        / "raw"
        / current.date().isoformat()
        / f"{issue['issue_id']}.json"
    )
    atomic_write_json(raw_path, issue)
    _rebuild_issue_markdown(output_root)
    return {**issue, "raw_path": str(raw_path)}


def recent_issues(output_root: Path, limit: int = 20) -> list[dict[str, Any]]:
    raw_root = output_root / "issue_feedback" / "raw"
    issues = []
    for path in sorted(raw_root.glob("*/*.json"), reverse=True):
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(value, dict):
            issues.append(value)
        if len(issues) >= limit:
            break
    return issues


def _rebuild_issue_markdown(output_root: Path) -> None:
    issues = list(reversed(recent_issues(output_root, limit=500)))
    daily: dict[str, list[dict[str, Any]]] = {}
    for issue in issues:
        day = str(issue.get("created_at", ""))[:10] or "unknown"
        daily.setdefault(day, []).append(issue)
    daily_root = output_root / "issue_feedback" / "daily"
    for day, items in daily.items():
        atomic_write_text(daily_root / f"{day}.md", _render_daily(day, items))
    open_issues = [issue for issue in issues if issue.get("status") == "open"]
    atomic_write_text(output_root / "issue_feedback" / "UNREVIEWED.md", _render_unreviewed(open_issues))


def _render_daily(day: str, issues: list[dict[str, Any]]) -> str:
    lines = [f"# 系统问题反馈：{day}", ""]
    for issue in issues:
        lines.extend(_render_issue(issue))
    return "\n".join(lines).rstrip() + "\n"


def _render_unreviewed(issues: list[dict[str, Any]]) -> str:
    lines = ["# 未处理系统问题反馈", ""]
    if not issues:
        lines.append("当前没有未处理问题。")
    for issue in issues:
        lines.extend(_render_issue(issue))
    return "\n".join(lines).rstrip() + "\n"


def _render_issue(issue: dict[str, Any]) -> list[str]:
    title = (
        f"## [{issue.get('severity_label', issue.get('severity', 'medium'))}] "
        f"{issue.get('category_label', issue.get('category', 'other'))} "
        f"— {issue.get('issue_id', '')}"
    )
    lines = [
        title,
        "",
        f"- 状态：{issue.get('status', 'open')}",
        f"- 时间：{issue.get('created_at', '')}",
        f"- 页面：{issue.get('page', '') or 'unknown'}",
    ]
    if issue.get("suggestion_id"):
        lines.append(f"- 建议 ID：{issue.get('suggestion_id')}")
    if issue.get("report_path"):
        lines.append(f"- 报告路径：{issue.get('report_path')}")
    lines.extend(["", str(issue.get("message", "")).strip(), ""])
    return lines
