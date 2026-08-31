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
        internet: list[bool],
        activations: dict[str, bool] | None = None,
    ) -> None:
        self.active = active
        self.internet = list(internet)
        self.current_internet = True
        self.activations = activations or {}
        self.commands: list[list[str]] = []

    def run(self, args: list[str], timeout: int) -> CommandResult:
        del timeout
        self.commands.append(args)
        if args[:4] == ["/usr/bin/nmcli", "-t", "-f", "NAME,DEVICE"]:
            if self.active is None:
                return CommandResult(0, "")
            return CommandResult(0, f"{self.active}:wlan0\n")
        if args[:4] == ["/usr/sbin/ip", "route", "show", "default"]:
            self.current_internet = (
                self.internet.pop(0) if self.internet else False
            )
            return CommandResult(0, "default via 10.0.0.1 dev wlan0\n")
        if args[:2] == ["/usr/bin/curl", "-4"]:
            return CommandResult(
                0 if self.current_internet else 28,
                "204" if self.current_internet else "000",
            )
        if args[:2] == ["/usr/bin/curl", "-6"]:
            return CommandResult(
                0 if self.current_internet else 28,
                "200" if self.current_internet else "000",
            )
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
            "ipv4_probe_url": "https://www.gstatic.com/generate_204",
            "ipv6_probe_url": "https://www.cloudflare.com/",
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

    def test_four_primary_internet_failures_switch_to_hotspot(self) -> None:
        runner = FakeRunner(active="UCAS", internet=[False] * 4)
        controller = self.controller(runner)
        actions = [controller.run_once()["action"] for _ in range(4)]
        self.assertEqual(actions[-1], "switched_to_fallback")
        self.assertEqual(runner.active, "netplan-wlan0-XYH 0563")

    def test_failed_hotspot_activation_restores_primary_and_sets_cooldown(self) -> None:
        runner = FakeRunner(
            active="UCAS",
            internet=[False] * 4,
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
            internet=[True],
        )
        event = self.controller(runner).run_once()
        self.assertEqual(event["action"], "fallback_healthy_hold")
        self.assertEqual(runner.active, "netplan-wlan0-XYH 0563")

    def test_two_hotspot_failures_restore_primary(self) -> None:
        runner = FakeRunner(
            active="netplan-wlan0-XYH 0563",
            internet=[False, False],
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
        runner = FakeRunner(active="Other WiFi", internet=[False])
        event = self.controller(runner).run_once()
        self.assertEqual(event["action"], "manual_other_profile_preserved")
        self.assertEqual(runner.active, "Other WiFi")

    def test_computer_absence_does_not_trigger_when_internet_is_healthy(self) -> None:
        runner = FakeRunner(active="UCAS", internet=[True] * 6)
        controller = self.controller(runner)
        actions = [controller.run_once()["action"] for _ in range(6)]
        self.assertEqual(set(actions), {"primary_healthy"})
        self.assertEqual(runner.active, "UCAS")

    def test_manual_fallback_failure_restores_ucas(self) -> None:
        runner = FakeRunner(
            active="UCAS",
            internet=[],
            activations={
                "netplan-wlan0-XYH 0563": False,
                "UCAS": True,
            },
        )
        event = self.controller(runner).force_fallback()
        self.assertFalse(event["success"])
        self.assertTrue(event["primary_restored"])
        self.assertEqual(runner.active, "UCAS")

    def test_manual_fallback_success(self) -> None:
        runner = FakeRunner(active="UCAS", internet=[])
        event = self.controller(runner).force_fallback()
        self.assertTrue(event["success"])
        self.assertEqual(event["action"], "manual_switched_to_fallback")
        self.assertEqual(runner.active, "netplan-wlan0-XYH 0563")


if __name__ == "__main__":
    unittest.main()
