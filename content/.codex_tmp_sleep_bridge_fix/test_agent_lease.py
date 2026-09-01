import json
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import agent as agent_module


class Completed:
    def __init__(self, returncode=0, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


class AgentLeaseTests(unittest.TestCase):
    def test_overnight_schedule_window_ends_at_next_noon(self):
        timezone = datetime.now().astimezone().tzinfo
        late = datetime(2026, 8, 14, 23, 45, tzinfo=timezone)
        morning = datetime(2026, 8, 15, 11, 59, tzinfo=timezone)
        self.assertEqual(
            agent_module.scheduled_window(late, "23:30", "12:00")[1],
            datetime(2026, 8, 15, 12, 0, tzinfo=timezone),
        )
        self.assertEqual(
            agent_module.scheduled_window(morning, "23:30", "12:00")[0],
            datetime(2026, 8, 14, 23, 30, tzinfo=timezone),
        )
        self.assertIsNone(
            agent_module.scheduled_window(
                datetime(2026, 8, 15, 12, 0, tzinfo=timezone), "23:30", "12:00"
            )
        )

    def make_agent(self, directory, state):
        root = Path(directory)
        config_path = root / "config.json"
        state_path = root / "state.json"
        config_path.write_text(
            json.dumps(
                {
                    "api_base": "https://example.invalid",
                    "auth_required": False,
                    "cold_turkey_exe": "fake-cold-turkey.exe",
                    "allowed_blocks": {
                        "bilibili": {
                            "cold_turkey_block": "bilibili",
                            "display_name": "bilibili",
                            "default_lock_minutes": 30,
                        }
                    },
                }
            ),
            encoding="utf-8",
        )
        state_path.write_text(json.dumps(state), encoding="utf-8")
        config_patch = patch.object(agent_module, "CONFIG_PATH", config_path)
        state_patch = patch.object(agent_module, "STATE_PATH", state_path)
        config_patch.start()
        state_patch.start()
        self.addCleanup(state_patch.stop)
        self.addCleanup(config_patch.stop)
        result = agent_module.InterventionAgent()
        result.client = object()
        return result, state_path

    @staticmethod
    def lease(until, lease_id="lease-1"):
        return {
            "bilibili": {
                "block": "bilibili",
                "mode": "agent_lease",
                "lease_id": lease_id,
                "lock_until_estimated": until.isoformat(timespec="seconds"),
            }
        }

    def test_expired_lease_is_stopped(self):
        with tempfile.TemporaryDirectory() as directory:
            agent, _ = self.make_agent(
                directory,
                {"active_locks": self.lease(datetime.now().astimezone() - timedelta(seconds=1))},
            )
            with patch.object(agent_module.subprocess, "run", return_value=Completed()) as run:
                agent.reconcile_expired_leases()
            run.assert_called_once()
            self.assertEqual(run.call_args.args[0], ["fake-cold-turkey.exe", "-stop", "bilibili"])
            self.assertEqual(agent.state["active_locks"], {})

    def test_unexpired_lease_is_not_stopped(self):
        with tempfile.TemporaryDirectory() as directory:
            agent, _ = self.make_agent(
                directory,
                {"active_locks": self.lease(datetime.now().astimezone() + timedelta(minutes=5))},
            )
            with patch.object(agent_module.subprocess, "run") as run:
                agent.reconcile_expired_leases()
            run.assert_not_called()

    def test_restart_reconciles_expired_persisted_lease(self):
        with tempfile.TemporaryDirectory() as directory:
            state = {"active_locks": self.lease(datetime.now().astimezone() - timedelta(minutes=20))}
            agent, state_path = self.make_agent(directory, state)
            with patch.object(agent_module.subprocess, "run", return_value=Completed()):
                agent.reconcile_expired_leases()
            restarted = agent_module.InterventionAgent()
            self.assertEqual(restarted.state["active_locks"], {})
            self.assertEqual(json.loads(state_path.read_text(encoding="utf-8"))["active_locks"], {})

    def test_start_journals_lease_before_invoking_cold_turkey(self):
        with tempfile.TemporaryDirectory() as directory:
            agent, state_path = self.make_agent(directory, {"active_locks": {}})

            def command_after_journal(*_args, **_kwargs):
                persisted = json.loads(state_path.read_text(encoding="utf-8"))
                lease = persisted["active_locks"]["bilibili"]
                self.assertEqual(lease["lease_id"], "lease-before-start")
                self.assertEqual(lease["lease_state"], "starting")
                return Completed()

            with patch.object(agent_module.subprocess, "run", side_effect=command_after_journal):
                result = agent.start_cold_turkey(
                    "bilibili", "bilibili", 30, lease_id="lease-before-start"
                )
            self.assertEqual(result["status"], "success")
            self.assertEqual(agent.state["active_locks"]["bilibili"]["lease_state"], "active")

    def test_old_release_cannot_stop_newer_lease(self):
        with tempfile.TemporaryDirectory() as directory:
            agent, _ = self.make_agent(
                directory,
                {"active_locks": self.lease(datetime.now().astimezone() + timedelta(minutes=5), "new-lease")},
            )
            with patch.object(agent_module.subprocess, "run") as run:
                result = agent.stop_cold_turkey("bilibili", "bilibili", expected_lease_id="old-lease")
            run.assert_not_called()
            self.assertEqual(result["status"], "lease_superseded")

    def test_failed_expiry_stop_is_kept_for_retry(self):
        with tempfile.TemporaryDirectory() as directory:
            agent, _ = self.make_agent(
                directory,
                {"active_locks": self.lease(datetime.now().astimezone() - timedelta(seconds=1))},
            )
            with patch.object(
                agent_module.subprocess, "run", return_value=Completed(1, stderr="temporary failure")
            ):
                agent.reconcile_expired_leases()
            lease = agent.state["active_locks"]["bilibili"]
            self.assertEqual(lease["last_release_status"], "unknown_command_result")
            self.assertIn("temporary failure", lease["release_error"])

    def test_failed_release_is_not_final(self):
        with tempfile.TemporaryDirectory() as directory:
            agent, _ = self.make_agent(directory, {"active_locks": self.lease(datetime.now().astimezone() + timedelta(minutes=5))})
            with patch.object(
                agent_module.subprocess, "run", return_value=Completed(1, stderr="temporary failure")
            ):
                response = agent.handle_request(
                    {
                        "request_id": "release-1",
                        "mode": "release",
                        "targets": [{"name": "bilibili", "lease_id": "lease-1"}],
                    }
                )
            self.assertFalse(response["final"])
            self.assertEqual(response["decision"], "release_pending")

    def test_legacy_release_without_lease_id_cannot_stop_current_lock(self):
        with tempfile.TemporaryDirectory() as directory:
            agent, _ = self.make_agent(
                directory,
                {"active_locks": self.lease(datetime.now().astimezone() + timedelta(minutes=5))},
            )
            with patch.object(agent_module.subprocess, "run") as run:
                response = agent.handle_request(
                    {
                        "request_id": "legacy-release-1",
                        "mode": "release",
                        "targets": [{"name": "bilibili"}],
                    }
                )
            run.assert_not_called()
            self.assertTrue(response["final"])
            self.assertEqual(response["decision"], "legacy_release_ignored")
            self.assertEqual(response["executions"][0]["status"], "lease_id_required")
            self.assertIn("bilibili", agent.state["active_locks"])

    def test_forced_execution_waits_for_configured_save_countdown(self):
        with tempfile.TemporaryDirectory() as directory:
            agent, _ = self.make_agent(directory, {"active_locks": {}})
            request = {
                "request_id": "forced-steam-1",
                "mode": "execute",
                "source": "forced_intervention",
                "targets": [
                    {
                        "name": "bilibili",
                        "enabled": True,
                        "lock_minutes": 30,
                        "pre_lock_countdown_seconds": 60,
                    }
                ],
            }
            with patch.object(agent_module, "show_pre_lock_countdown") as countdown, \
                 patch.object(agent_module, "show_execution_notice"), \
                 patch.object(agent, "start_cold_turkey", return_value={"status": "success"}):
                response = agent.handle_request(request)
            countdown.assert_called_once()
            self.assertEqual(countdown.call_args.args[1], 60)
            self.assertEqual(response["decision"], "forced")

    def test_night_schedule_closes_game_and_hard_locks_until_next_noon(self):
        with tempfile.TemporaryDirectory() as directory:
            agent, _ = self.make_agent(directory, {"active_locks": {}})
            agent.config["allowed_blocks"]["steam游戏"] = {
                "cold_turkey_block": "steam游戏",
                "display_name": "Steam 游戏",
                "default_lock_minutes": 30,
            }
            agent.config["scheduled_locks"] = [{
                "id": "steam-night", "name": "steam游戏",
                "start": "23:30", "end": "12:00",
                "pre_lock_countdown_seconds": 0,
            }]
            timezone = datetime.now().astimezone().tzinfo
            now = datetime(2026, 8, 14, 23, 30, tzinfo=timezone)
            agent.garden_client = MagicMock()
            agent.garden_client.award_steam_close.return_value = {"id": "reward-1"}
            with patch.object(agent_module, "ask_steam_night_user", return_value={"decision": "close"}), \
                 patch.object(agent, "close_configured_steam_game", return_value={"status": "closed"}), \
                 patch.object(agent, "start_hard_cold_turkey", return_value={"status": "success"}) as start:
                agent.reconcile_scheduled_locks(now)
            self.assertEqual(start.call_args.args[:3], ("steam游戏", "steam游戏", 750))
            self.assertEqual(start.call_args.kwargs["source"], "scheduled_night_hard_lock")
            self.assertTrue(agent.state["scheduled_lock_runs"]["steam-night"]["hard_lock_started"])
            agent.garden_client.award_steam_close.assert_called_once()

    def test_hard_lock_rejects_invalid_block_even_when_cli_returns_zero(self):
        with tempfile.TemporaryDirectory() as directory:
            agent, _ = self.make_agent(directory, {"active_locks": {}})
            rejected = Completed()
            rejected.stderr = "Error: Invalid block name. Note that block names are case-sensitive."
            with patch.object(agent_module.subprocess, "run", return_value=rejected):
                result = agent.start_hard_cold_turkey("steam游戏", "steam游戏", 5)
            self.assertEqual(result["status"], "command_rejected")
            self.assertEqual(result["exit_code"], 0)

    def test_hard_lock_uses_supported_lock_argument(self):
        with tempfile.TemporaryDirectory() as directory:
            agent, _ = self.make_agent(directory, {"active_locks": {}})
            with patch.object(agent_module.subprocess, "run", return_value=Completed()) as run:
                result = agent.start_hard_cold_turkey("bilibili", "bilibili", 750)
            self.assertEqual(
                run.call_args.args[0],
                ["fake-cold-turkey.exe", "-start", "bilibili", "-lock", "750"],
            )
            self.assertEqual(result["status"], "success")
            self.assertEqual(agent.state.get("active_locks", {}), {})

    def test_legacy_night_run_does_not_prompt_again_after_upgrade(self):
        with tempfile.TemporaryDirectory() as directory:
            timezone = datetime.now().astimezone().tzinfo
            window_start = datetime(2026, 8, 14, 23, 30, tzinfo=timezone)
            agent, _ = self.make_agent(directory, {
                "active_locks": {},
                "scheduled_lock_runs": {
                    "steam-night": {
                        "window_start": window_start.isoformat(timespec="seconds"),
                        "lease_id": "schedule:steam-night:legacy",
                    }
                },
            })
            agent.config["allowed_blocks"]["steam游戏"] = {
                "cold_turkey_block": "steam游戏", "display_name": "Steam 游戏"
            }
            agent.config["scheduled_locks"] = [{
                "id": "steam-night", "name": "steam游戏",
                "start": "23:30", "end": "12:00",
                "pre_lock_countdown_seconds": 60,
            }]
            morning = datetime(2026, 8, 15, 11, 30, tzinfo=timezone)
            with patch.object(agent_module, "ask_steam_night_user") as prompt, \
                 patch.object(agent, "start_hard_cold_turkey") as hard_lock:
                agent.reconcile_scheduled_locks(morning)
            prompt.assert_not_called()
            hard_lock.assert_not_called()
            self.assertTrue(
                agent.state["scheduled_lock_runs"]["steam-night"]["migrated_from_legacy_lease"]
            )

    def test_defer_is_bounded_at_one_am(self):
        timezone = datetime.now().astimezone().tzinfo
        window_start = datetime(2026, 8, 14, 23, 30, tzinfo=timezone)
        self.assertEqual(
            agent_module.InterventionAgent._defer_datetime(window_start, "01:00", "01:00"),
            datetime(2026, 8, 15, 1, 0, tzinfo=timezone),
        )
        with self.assertRaises(ValueError):
            agent_module.InterventionAgent._defer_datetime(window_start, "01:15", "01:00")

    def test_day_gate_renews_hard_lock_until_eligible(self):
        with tempfile.TemporaryDirectory() as directory:
            agent, _ = self.make_agent(directory, {"active_locks": {}})
            agent.config["allowed_blocks"]["steam游戏"] = {
                "cold_turkey_block": "steam游戏", "display_name": "Steam 游戏"
            }
            agent.garden_client = MagicMock()
            agent.garden_client.get_steam_gate.return_value = {
                "date": "2026-08-15", "eligible": False
            }
            now = datetime(2026, 8, 15, 12, 1, tzinfo=datetime.now().astimezone().tzinfo)
            with patch.object(agent, "start_hard_cold_turkey", return_value={"status": "success"}) as start:
                agent.reconcile_steam_day_gate(now)
            start.assert_called_once()
            self.assertEqual(start.call_args.args[2], 5)

    def test_day_gate_stops_renewing_when_eligible(self):
        with tempfile.TemporaryDirectory() as directory:
            agent, _ = self.make_agent(directory, {"active_locks": {}})
            agent.garden_client = MagicMock()
            agent.garden_client.get_steam_gate.return_value = {
                "date": "2026-08-15", "eligible": True
            }
            now = datetime(2026, 8, 15, 12, 1, tzinfo=datetime.now().astimezone().tzinfo)
            with patch.object(agent, "start_hard_cold_turkey") as start:
                agent.reconcile_steam_day_gate(now)
            start.assert_not_called()


if __name__ == "__main__":
    unittest.main()
