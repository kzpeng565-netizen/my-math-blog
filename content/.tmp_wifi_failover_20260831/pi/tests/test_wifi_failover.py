from __future__ import annotations

import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from wifi_failover import CommandResult, WifiFailover


class FakeRunner:
    def __init__(
        self,
        *,
        active: str | None,
        tailnet: list[bool],
        activations: dict[str, bool] | None = None,
    ) -> None:
        self.active = active
        self.tailnet = list(tailnet)
        self.activations = activations or {}
        self.commands: list[list[str]] = []

    def run(self, args: list[str], timeout: int) -> CommandResult:
        del timeout
        self.commands.append(args)
        if args[:4] == ["/usr/bin/nmcli", "-t", "-f", "NAME,DEVICE"]:
            if self.active is None:
                return CommandResult(0, "")
            return CommandResult(0, f"{self.active}:wlan0\n")
        if args[:2] == ["/usr/bin/tailscale", "ping"]:
            value = self.tailnet.pop(0) if self.tailnet else False
            return CommandResult(0 if value else 1, "pong from xyh\n" if value else "")
        if args[:3] == ["/usr/bin/nmcli", "connection", "up"]:
            profile = args[3]
            success = self.activations.get(profile, True)
            if success:
                self.active = profile
                return CommandResult(0, "activated")
            return CommandResult(10, "", "not found")
        raise AssertionError(args)


class WifiFailoverTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        root = Path(self.temporary.name)
        self.config = {
            "enabled": True,
            "primary_profile": "UCAS",
            "fallback_profile": "netplan-wlan0-XYH 0563",
            "windows_peer": "xyh",
            "primary_failure_threshold": 4,
            "fallback_failure_threshold": 2,
            "failed_switch_cooldown_seconds": 600,
            "state_path": str(root / "state.json"),
            "events_path": str(root / "events.jsonl"),
            "lock_path": str(root / "lock"),
        }
        self.now = datetime(2026, 8, 31, 8, 0, tzinfo=timezone.utc)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def controller(self, runner: FakeRunner) -> WifiFailover:
        return WifiFailover(
            self.config,
            runner=runner,
            clock=lambda: self.now,
        )

    def test_four_primary_failures_switch_to_hotspot(self) -> None:
        runner = FakeRunner(active="UCAS", tailnet=[False] * 4)
        controller = self.controller(runner)
        actions = [controller.run_once()["action"] for _ in range(4)]
        self.assertEqual(actions[-1], "switched_to_fallback")
        self.assertEqual(runner.active, "netplan-wlan0-XYH 0563")

    def test_failed_hotspot_activation_restores_primary_and_sets_cooldown(self) -> None:
        runner = FakeRunner(
            active="UCAS",
            tailnet=[False] * 4,
            activations={
                "netplan-wlan0-XYH 0563": False,
                "UCAS": True,
            },
        )
        controller = self.controller(runner)
        for _ in range(3):
            controller.run_once()
        event = controller.run_once()
        self.assertEqual(event["action"], "fallback_failed_primary_restored")
        self.assertTrue(event["primary_restored"])
        state = json.loads(Path(self.config["state_path"]).read_text())
        self.assertIsNotNone(state["cooldown_until"])
        self.assertEqual(runner.active, "UCAS")

    def test_healthy_hotspot_is_held_instead_of_flapping_back(self) -> None:
        runner = FakeRunner(
            active="netplan-wlan0-XYH 0563",
            tailnet=[True],
        )
        event = self.controller(runner).run_once()
        self.assertEqual(event["action"], "fallback_healthy_hold")
        self.assertEqual(runner.active, "netplan-wlan0-XYH 0563")

    def test_two_hotspot_failures_restore_primary(self) -> None:
        runner = FakeRunner(
            active="netplan-wlan0-XYH 0563",
            tailnet=[False, False],
        )
        controller = self.controller(runner)
        self.assertEqual(
            controller.run_once()["action"],
            "fallback_failure_accumulating",
        )
        self.assertEqual(
            controller.run_once()["action"],
            "fallback_failed_switched_primary",
        )
        self.assertEqual(runner.active, "UCAS")

    def test_manual_other_wifi_is_never_overridden(self) -> None:
        runner = FakeRunner(active="Other WiFi", tailnet=[False])
        event = self.controller(runner).run_once()
        self.assertEqual(event["action"], "manual_other_profile_preserved")
        self.assertEqual(runner.active, "Other WiFi")


if __name__ == "__main__":
    unittest.main()
