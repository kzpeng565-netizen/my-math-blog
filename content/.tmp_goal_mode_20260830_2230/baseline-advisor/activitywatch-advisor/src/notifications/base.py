from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NotificationResult:
    status: str
    provider: str
    title: str
    priority: str
    attempt_count: int = 0
    error: str | None = None
    message_id: str | None = None

    @property
    def accepted(self) -> bool:
        return self.status == "accepted"

    def as_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "provider": self.provider,
            "title": self.title,
            "priority": self.priority,
            "attempt_count": self.attempt_count,
            "error": self.error,
            "message_id": self.message_id,
        }
