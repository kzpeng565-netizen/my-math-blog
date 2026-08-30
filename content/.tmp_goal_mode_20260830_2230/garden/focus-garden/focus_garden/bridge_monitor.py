from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Iterable

HEARTBEAT_MAX_AGE_SECONDS = 7 * 60
POLL_MAX_AGE_SECONDS = 90
MAX_HEALTHY_GAP_SECONDS = 8 * 60
QUALIFICATION_SECONDS = 30 * 60
QUALIFICATION_HEARTBEATS = 7
MIN_APP_VERSION = (1, 3, 3)


def _parse_time(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _version(value: Any) -> tuple[int, int, int] | None:
    try:
        parts = str(value).split(".")
        if len(parts) < 3:
            return None
        return tuple(int(part.split("-")[0]) for part in parts[:3])  # type: ignore[return-value]
    except (TypeError, ValueError):
        return None


def _metadata(record: dict[str, Any] | None) -> dict[str, Any]:
    value = (record or {}).get("metadata")
    return value if isinstance(value, dict) else {}


def _is_contract_healthy(record: dict[str, Any]) -> bool:
    metadata = _metadata(record)
    return (
        (_version(metadata.get("app_version")) or (0, 0, 0)) >= MIN_APP_VERSION
        and metadata.get("runtime_mode") == "foreground_service"
        and metadata.get("transport") == "public_https"
        and metadata.get("accessibility_enabled") is True
        and metadata.get("accessibility_connected") is True
        and metadata.get("notification_access_enabled") is True
        and metadata.get("notification_listener_connected") is True
        and not metadata.get("last_execution_error")
    )


def evaluate_bridge_qualification(
    health: dict[str, Any] | None,
    history: Iterable[dict[str, Any]],
    now: datetime | None = None,
) -> dict[str, Any]:
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    if not health:
        return {"state": "never", "label": "尚未验收", "summary": "尚未收到 Focus Bridge 心跳.",
                "checks": [], "observed_seconds": 0, "healthy_heartbeat_count": 0}

    metadata = _metadata(health)
    seen_at = _parse_time(health.get("last_seen_at"))
    heartbeat_age = max(0, int((now - seen_at).total_seconds())) if seen_at else None
    poll_at = _parse_time(metadata.get("last_poll_at"))
    poll_age = max(0, int(((seen_at or now) - poll_at).total_seconds())) if poll_at else None
    version = _version(metadata.get("app_version"))
    heartbeat_ok = heartbeat_age is not None and heartbeat_age <= HEARTBEAT_MAX_AGE_SECONDS
    version_ok = version is not None and version >= MIN_APP_VERSION
    foreground_ok = metadata.get("runtime_mode") == "foreground_service"
    network_ok = metadata.get("transport") == "public_https"
    accessibility_ok = metadata.get("accessibility_enabled") is True and metadata.get("accessibility_connected") is True
    notification_ok = (metadata.get("notification_access_enabled") is True and
                       metadata.get("notification_listener_connected") is True)
    execution_error = str(metadata.get("last_execution_error") or "")
    lock_status = str(metadata.get("lock_status") or "idle")
    execution_ok = not execution_error and lock_status != "failed"
    duplicates_blocked = max(0, int(metadata.get("duplicate_execution_requests_blocked", 0) or 0))
    poll_ok = (poll_age is not None and poll_age <= POLL_MAX_AGE_SECONDS and
               str(metadata.get("last_poll_status", "")).lower() not in {"", "error", "failed", "stopped"})

    ordered = sorted((item for item in history if _parse_time(item.get("seen_at"))),
                     key=lambda item: _parse_time(item.get("seen_at")) or now)
    chain: list[dict[str, Any]] = []
    later: datetime | None = None
    for item in reversed(ordered):
        item_at = _parse_time(item.get("seen_at"))
        if item_at is None or not _is_contract_healthy(item):
            break
        if later is not None and (later - item_at).total_seconds() > MAX_HEALTHY_GAP_SECONDS:
            break
        chain.append(item)
        later = item_at
    chain.reverse()
    chain_times = [item for item in (_parse_time(x.get("seen_at")) for x in chain) if item is not None]
    observed_seconds = max(0, int((chain_times[-1] - chain_times[0]).total_seconds())) if len(chain_times) >= 2 else 0
    gaps = [int((right - left).total_seconds()) for left, right in zip(chain_times, chain_times[1:])]
    stability_ok = len(chain) >= QUALIFICATION_HEARTBEATS and observed_seconds >= QUALIFICATION_SECONDS and (not gaps or max(gaps) <= MAX_HEALTHY_GAP_SECONDS)
    checks = [
        {"id": "heartbeat", "label": "心跳新鲜", "state": "pass" if heartbeat_ok else "fail", "detail": "刚刚收到" if heartbeat_age is not None and heartbeat_age < 60 else f"{heartbeat_age // 60} 分钟前" if heartbeat_age is not None else "时间无效"},
        {"id": "version", "label": "新版状态协议", "state": "pass" if version_ok else "fail", "detail": str(metadata.get("app_version") or "旧版/未上报")},
        {"id": "foreground", "label": "前台常驻服务", "state": "pass" if foreground_ok else "fail", "detail": str(metadata.get("runtime_mode") or "未上报")},
        {"id": "network", "label": "Pi 网络路径", "state": "pass" if network_ok else "fail", "detail": "公网 HTTPS（不依赖 Tailscale）" if network_ok else "仅备用通道或未建立"},
        {"id": "accessibility", "label": "无障碍连接", "state": "pass" if accessibility_ok else "fail", "detail": "已启用且已连接" if accessibility_ok else "未连接或状态未知"},
        {"id": "notification_listener", "label": "锁机结果确认", "state": "pass" if notification_ok else "fail", "detail": "通知使用权已启用且监听已连接" if notification_ok else "通知使用权未启用或监听未连接"},
        {"id": "lock_execution", "label": "最近锁机执行", "state": "pass" if execution_ok else "fail", "detail": execution_error or (f"已确认 {metadata.get('lock_minutes')} 分钟" if lock_status == "confirmed" else f"{lock_status} · 第 {metadata.get('lock_attempts', 0)} 次" if lock_status not in {"", "idle"} else "尚无失败")},
        {"id": "request_idempotency", "label": "重复请求防护", "state": "pass", "detail": f"已拦截 {duplicates_blocked} 次重复执行" if duplicates_blocked else "已启用 · 尚未触发"},
        {"id": "poll", "label": "命令轮询", "state": "pass" if poll_ok else "fail", "detail": f"{poll_age} 秒前 · {metadata.get('last_poll_status')}" if poll_age is not None else "未上报"},
        {"id": "stability", "label": "连续后台观察", "state": "pass" if stability_ok else "pending", "detail": f"{len(chain)}/{QUALIFICATION_HEARTBEATS} 次 · {observed_seconds // 60}/{QUALIFICATION_SECONDS // 60} 分钟"},
    ]
    if not heartbeat_ok:
        state, label, summary = "stale", "失联", "新版 Bridge 当前没有持续上报心跳。"
    elif not all((version_ok, foreground_ok, network_ok, accessibility_ok,
                  notification_ok, execution_ok, poll_ok)):
        state, label, summary = "degraded", "未合格", "心跳在线，但常驻、权限、锁机确认或轮询检查未通过。"
    elif not stability_ok:
        state, label, summary = "observing", "观察中", "即时检查已通过，正在累计 30 分钟连续后台证据。"
    else:
        state, label, summary = "qualified", "合格", "前台常驻、无障碍、锁机确认、轮询和连续心跳均通过。"
    return {"state": state, "label": label, "summary": summary, "checks": checks,
            "observed_seconds": observed_seconds, "healthy_heartbeat_count": len(chain),
            "max_gap_seconds": max(gaps) if gaps else None,
            "required_observation_seconds": QUALIFICATION_SECONDS,
            "required_heartbeat_count": QUALIFICATION_HEARTBEATS,
            "app_version": metadata.get("app_version"),
            "service_instance_id": metadata.get("service_instance_id"),
            "service_uptime_seconds": metadata.get("service_uptime_seconds"),
            "last_error": metadata.get("last_error") or ""}
