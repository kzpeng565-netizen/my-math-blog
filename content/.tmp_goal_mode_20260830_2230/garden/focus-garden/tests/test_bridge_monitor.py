import unittest
from datetime import datetime, timedelta, timezone

from focus_garden.bridge_monitor import evaluate_bridge_qualification


class BridgeMonitorTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 8, 7, 5, 30, tzinfo=timezone.utc)

    @staticmethod
    def metadata(at: datetime, **overrides):
        value = {
            "runtime_mode": "foreground_service",
            "transport": "public_https",
            "app_version": "1.3.3",
            "service_instance_id": "service-one",
            "accessibility_enabled": True,
            "accessibility_connected": True,
            "notification_access_enabled": True,
            "notification_listener_connected": True,
            "lock_status": "idle",
            "last_execution_error": "",
            "last_poll_at": at.isoformat(timespec="seconds"),
            "last_poll_status": "no_pending",
            "last_error": "",
        }
        value.update(overrides)
        return value

    def test_requires_continuous_observation(self):
        health = {"last_seen_at": self.now.isoformat(), "metadata": self.metadata(self.now)}
        history = [{"seen_at": (self.now - timedelta(minutes=n)).isoformat(),
                    "metadata": self.metadata(self.now - timedelta(minutes=n))}
                   for n in (0, 5, 10)]
        result = evaluate_bridge_qualification(health, history, self.now)
        self.assertEqual(result["state"], "observing")
        self.assertEqual(result["healthy_heartbeat_count"], 3)

    def test_qualifies_after_seven_heartbeats(self):
        health = {"last_seen_at": self.now.isoformat(), "metadata": self.metadata(self.now)}
        history = [{"seen_at": (self.now - timedelta(minutes=n)).isoformat(),
                    "metadata": self.metadata(self.now - timedelta(minutes=n))}
                   for n in range(0, 31, 5)]
        self.assertEqual(evaluate_bridge_qualification(health, history, self.now)["state"], "qualified")

    def test_tailnet_fallback_does_not_qualify(self):
        health = {"last_seen_at": self.now.isoformat(),
                  "metadata": self.metadata(self.now, transport="tailnet_fallback", fallback_active=True)}
        result = evaluate_bridge_qualification(health, [], self.now)
        self.assertEqual(result["state"], "degraded")
        self.assertEqual(next(c for c in result["checks"] if c["id"] == "network")["state"], "fail")

    def test_notification_listener_is_required(self):
        health = {"last_seen_at": self.now.isoformat(),
                  "metadata": self.metadata(self.now, notification_listener_connected=False)}
        result = evaluate_bridge_qualification(health, [], self.now)
        self.assertEqual(result["state"], "degraded")
        self.assertEqual(next(c for c in result["checks"] if c["id"] == "notification_listener")["state"], "fail")

    def test_execution_failure_is_visible(self):
        health = {"last_seen_at": self.now.isoformat(),
                  "metadata": self.metadata(self.now, lock_status="failed",
                                            lock_attempts=3,
                                            last_execution_error="lock_not_confirmed_after_3_attempts")}
        result = evaluate_bridge_qualification(health, [], self.now)
        check = next(c for c in result["checks"] if c["id"] == "lock_execution")
        self.assertEqual(result["state"], "degraded")
        self.assertEqual(check["state"], "fail")
        self.assertIn("lock_not_confirmed", check["detail"])

    def test_duplicate_request_guard_is_visible(self):
        health = {"last_seen_at": self.now.isoformat(),
                  "metadata": self.metadata(
                      self.now, duplicate_execution_requests_blocked=2
                  )}
        result = evaluate_bridge_qualification(health, [], self.now)
        check = next(c for c in result["checks"] if c["id"] == "request_idempotency")
        self.assertEqual(check["state"], "pass")
        self.assertIn("2", check["detail"])


if __name__ == "__main__":
    unittest.main()
