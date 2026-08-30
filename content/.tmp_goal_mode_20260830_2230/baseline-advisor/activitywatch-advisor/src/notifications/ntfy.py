from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .base import NotificationResult


PRIORITY_BY_LEVEL = {
    1: "default",
    2: "high",
}

TAGS_BY_LEVEL = {
    1: ["hourglass"],
    2: ["warning"],
}

NTFY_PRIORITY_VALUE = {
    "min": 1,
    "low": 2,
    "default": 3,
    "high": 4,
    "urgent": 5,
}


@dataclass(frozen=True)
class NtfyConfig:
    server: str
    topic: str
    enabled: bool = True
    timeout_seconds: int = 10
    retries: int = 1

    @classmethod
    def from_env(cls) -> "NtfyConfig":
        enabled = os.environ.get("NTFY_ENABLED", "true").strip().lower()
        return cls(
            server=os.environ.get("NTFY_SERVER", "https://ntfy.sh").strip(),
            topic=os.environ.get("NTFY_TOPIC", "").strip(),
            enabled=enabled not in {"0", "false", "no", "off"},
            timeout_seconds=int(os.environ.get("NTFY_TIMEOUT_SECONDS", "10")),
            retries=max(0, int(os.environ.get("NTFY_RETRIES", "1"))),
        )


class NtfyNotifier:
    def __init__(self, config: NtfyConfig | None = None) -> None:
        self.config = config or NtfyConfig.from_env()

    def send(
        self,
        *,
        title: str,
        message: str,
        priority: str = "default",
        tags: Iterable[str] | None = None,
    ) -> NotificationResult:
        if not self.config.enabled:
            return NotificationResult(
                status="skipped",
                provider="ntfy",
                title=title,
                priority=priority,
                error="NTFY_ENABLED is false",
            )
        if not self.config.topic:
            return NotificationResult(
                status="skipped",
                provider="ntfy",
                title=title,
                priority=priority,
                error="NTFY_TOPIC is not configured",
            )

        server = self.config.server.rstrip("/")
        payload = {
            "topic": self.config.topic,
            "title": title,
            "message": message,
            "priority": NTFY_PRIORITY_VALUE.get(priority, 3),
            "tags": list(tags or []),
        }
        request_data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        last_error: Exception | None = None

        for attempt in range(self.config.retries + 1):
            request = Request(
                server,
                data=request_data,
                method="POST",
                headers={"Content-Type": "application/json"},
            )
            try:
                with urlopen(request, timeout=self.config.timeout_seconds) as response:
                    body = response.read().decode("utf-8")
                response_data = json.loads(body) if body else {}
                return NotificationResult(
                    status="accepted",
                    provider="ntfy",
                    title=title,
                    priority=priority,
                    attempt_count=attempt + 1,
                    message_id=str(response_data.get("id") or ""),
                )
            except (
                HTTPError,
                URLError,
                TimeoutError,
                ValueError,
                json.JSONDecodeError,
            ) as error:
                last_error = error
                if attempt < self.config.retries:
                    time.sleep(2**attempt)

        return NotificationResult(
            status="failed",
            provider="ntfy",
            title=title,
            priority=priority,
            attempt_count=self.config.retries + 1,
            error=f"{type(last_error).__name__}: {last_error}",
        )


def send_notification(
    *,
    level: int,
    policy_id: str,
    title: str,
    message: str,
    priority: str | None = None,
    tags: Iterable[str] | None = None,
    notifier: NtfyNotifier | None = None,
) -> NotificationResult:
    del policy_id
    actual_priority = priority or PRIORITY_BY_LEVEL.get(level, "default")
    actual_tags = list(tags) if tags is not None else TAGS_BY_LEVEL.get(level, [])
    return (notifier or NtfyNotifier()).send(
        title=title,
        message=message,
        priority=actual_priority,
        tags=actual_tags,
    )
