import json
import os
import tempfile
import threading
import unittest
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

from focus_garden.server import GardenHTTPServer, GardenService, NextActionProxy


class GardenServiceTests(unittest.TestCase):
    def test_phone_focus_dispatch_uses_deadline_ladder_and_independent_release(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as folder:
            database = str(Path(folder) / "service.sqlite3")
            with patch.dict(os.environ, {
                "FOCUS_GARDEN_DB": database,
                "FOCUS_GARDEN_DISPATCH_INTERVENTIONS": "1",
            }):
                service = GardenService(Path(__file__).resolve().parents[1])

                def intervention(name, method, body=None, **_kwargs):
                    if name == "manual_focus":
                        return 201, {"request": {"mode": "execute", "lease_id": "lease-123"}}, None
                    target = body["targets"][0]
                    return 201, {"request": {"mode": "release", "request_id": f"release-{target}"}}, None

                service.next_action.intervention = MagicMock(side_effect=intervention)
                session = service.start_focus("study", 60, ["windows", "phone"])
                start_body = service.next_action.intervention.call_args_list[0].kwargs["body"]
                self.assertEqual(start_body["focus_deadline_at"], session["ends_at"])
                self.assertEqual(start_body["allowed_phone_minutes"], [5, 20, 30, 40, 45, 60])

                service.release_focus_lease(session)
                release_calls = service.next_action.intervention.call_args_list[1:]
                self.assertEqual(
                    [call.kwargs["body"]["targets"] for call in release_calls],
                    [["phone"], ["windows"]],
                )
                self.assertEqual(release_calls[0].kwargs["body"]["blocks"], [])
                self.assertTrue(release_calls[1].kwargs["body"]["blocks"])

    def test_focus_lease_id_only_uses_execute_dispatcher_receipt(self):
        session = {
            "cold_turkey": [
                {"status": "release_queued", "dispatcher": {"request": {"mode": "release", "lease_id": "old"}}},
                {"status": "queued", "dispatcher": {"request": {"mode": "execute", "lease_id": "lease-123"}}},
            ]
        }
        self.assertEqual(GardenService._focus_lease_id(session), "lease-123")
        self.assertEqual(GardenService._focus_lease_id({"cold_turkey": []}), "")

    def test_next_action_proxy_only_forwards_fixed_loopback_paths_and_cookie(self):
        response = MagicMock()
        response.status = 200
        response.read.return_value = b'{"suggestion_id":"safe"}'
        response.headers = {"Set-Cookie": "next_action_session=signed; HttpOnly"}
        context = MagicMock()
        context.__enter__.return_value = response
        proxy = NextActionProxy({"next_action": {"base_url": "http://127.0.0.1:8767"}})
        with patch("focus_garden.server.urlopen", return_value=context) as open_url:
            status, data, cookie = proxy.request(
                "generate", "POST", body={"exclude_suggestion_id": "old"}, cookie="session=browser",
            )
        request = open_url.call_args.args[0]
        self.assertEqual(status, 200)
        self.assertEqual(data["suggestion_id"], "safe")
        self.assertEqual(cookie, "next_action_session=signed; HttpOnly")
        self.assertEqual(request.full_url, "http://127.0.0.1:8767/api/next-action")
        self.assertEqual(request.get_header("Cookie"), "session=browser")
        self.assertEqual(json.loads(request.data.decode("utf-8"))["exclude_suggestion_id"], "old")
        with self.assertRaises(ValueError):
            proxy.request_path("/api/next-action/../../secrets", body={})

    def test_task_sync_proxy_only_forwards_fixed_loopback_paths_with_bridge_header(self):
        response = MagicMock()
        response.status = 200
        response.read.return_value = b'{"revision":3}'
        response.headers = {}
        context = MagicMock()
        context.__enter__.return_value = response
        proxy = NextActionProxy({"next_action": {"base_url": "http://127.0.0.1:8767"}})
        with patch("focus_garden.server.urlopen", return_value=context) as open_url:
            status, data, _ = proxy.task_sync("mutations", "POST", body={"operation": "complete"})
        request = open_url.call_args.args[0]
        self.assertEqual(status, 200)
        self.assertEqual(data["revision"], 3)
        self.assertEqual(request.full_url, "http://127.0.0.1:8767/api/task-sync/mutations")
        self.assertEqual(request.get_header("X-focus-garden-bridge"), "1")
        with self.assertRaises(ValueError):
            proxy.task_sync("ack", "POST", body={})

        with patch("focus_garden.server.urlopen", return_value=context) as open_url:
            proxy.task_sync("primary", "POST", body={"task_id": "^8m2kx7q4"})
        self.assertEqual(
            open_url.call_args.args[0].full_url,
            "http://127.0.0.1:8767/api/task-sync/primary",
        )

    def test_safe_mode_does_not_require_windows_cold_turkey_files(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as folder:
            database = str(Path(folder) / "service.sqlite3")
            with patch.dict(os.environ, {"FOCUS_GARDEN_DRY_RUN": "1", "FOCUS_GARDEN_DB": database}):
                service = GardenService(Path(__file__).resolve().parents[1])
                service.cold_turkey.agent_config_path = Path(folder) / "missing.json"
                session = service.start_focus("study", 5)
                self.assertEqual(session["status"], "running")
                self.assertTrue(all(item["status"] == "simulated" for item in session["cold_turkey"]))
                self.assertIn("steam游戏", session["blocks"])

    def test_system_status_is_read_only_and_tolerates_missing_pi_paths(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as folder:
            database = str(Path(folder) / "service.sqlite3")
            with patch.dict(os.environ, {"FOCUS_GARDEN_DRY_RUN": "1", "FOCUS_GARDEN_DB": database}):
                service = GardenService(Path(__file__).resolve().parents[1])
                with patch.object(service, "advisor_data_root", Path(folder) / "missing-advisor"):
                    with patch.object(service, "_service_state", return_value={"name": "x", "state": "active"}):
                        status = service.system_status()
                self.assertEqual(status["privacy"]["writer"], "Pi SQLite only")
                self.assertEqual(status["tasks"]["pending_mutation_count"], 0)
                self.assertEqual(status["services"][0]["state"], "active")

    def test_system_status_tolerates_list_active_locks(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as folder:
            database = str(Path(folder) / "service.sqlite3")
            with patch.dict(os.environ, {"FOCUS_GARDEN_DRY_RUN": "1", "FOCUS_GARDEN_DB": database}):
                service = GardenService(Path(__file__).resolve().parents[1])
                advisor_root = Path(folder) / "advisor"
                agent_dir = advisor_root / "computer_interventions" / "state"
                agent_dir.mkdir(parents=True)
                (agent_dir / "windows-main.json").write_text(json.dumps({
                    "last_heartbeat_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                    "active_locks": ["bilibili", "常刷网站"],
                }), encoding="utf-8")
                task_dir = advisor_root / "task_sync"
                task_dir.mkdir(parents=True)
                (task_dir / "state.json").write_text(json.dumps({
                    "revision": 2, "mutations": None,
                }), encoding="utf-8")
                with patch.object(service, "advisor_data_root", advisor_root):
                    with patch.object(service, "_service_state", return_value={"name": "x", "state": "active"}):
                        status = service.system_status()
                self.assertEqual(status["bridges"]["windows"]["lease_blocks"], ["bilibili", "常刷网站"])
                self.assertEqual(status["bridges"]["windows"]["lease_state"], "active")
                self.assertEqual(status["tasks"]["pending_mutation_count"], 0)

    def test_system_status_explains_steam_unlock_gate_without_task_text(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as folder:
            database = str(Path(folder) / "service.sqlite3")
            with patch.dict(os.environ, {"FOCUS_GARDEN_DRY_RUN": "1", "FOCUS_GARDEN_DB": database}):
                service = GardenService(Path(__file__).resolve().parents[1])
                gate = {
                    "date": "2026-08-15",
                    "completed_tomatoes": 4,
                    "required_completed_tomatoes": 5,
                    "tomato_requirement_met": False,
                    "primary_task_id": "^private-task",
                    "primary_task_title": "private task text",
                    "primary_task_completed": False,
                    "eligible": False,
                }
                with patch.object(service, "steam_gate_status", return_value=gate) as steam_gate:
                    with patch.object(service, "_service_state", return_value={"name": "x", "state": "active"}):
                        status = service.system_status()
                indicator = status["steam_unlock"]
                self.assertTrue(indicator["available"])
                self.assertEqual(indicator["completed_tomatoes"], 4)
                self.assertEqual(indicator["required_completed_tomatoes"], 5)
                self.assertTrue(indicator["primary_task_set"])
                self.assertFalse(indicator["primary_task_completed"])
                self.assertEqual(
                    indicator["blocking_reasons"],
                    ["还差 1 个完成番茄", "今天的主要任务尚未完成"],
                )
                self.assertNotIn("primary_task_title", indicator)
                steam_gate.assert_called_once_with(timeout_seconds=3)

    def test_steam_gate_awards_completed_task_total_and_ignores_partial_open_progress(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as folder:
            database = str(Path(folder) / "service.sqlite3")
            with patch.dict(os.environ, {"FOCUS_GARDEN_DRY_RUN": "1", "FOCUS_GARDEN_DB": database}):
                service = GardenService(Path(__file__).resolve().parents[1])
                today = datetime.now().astimezone().date().isoformat()
                advisor_state = {
                    "tasks": {"today": [{
                        "task_id": "^partial", "tomatoes_completed": 2,
                        "tomatoes_total": 4, "status": "open",
                    }]},
                    "completed_today": [
                        {
                            "task_id": "^older-completed", "tomatoes_completed": 0,
                            "tomatoes_total": 5, "status": "completed", "occurrence_date": today,
                        },
                        {
                            "task_id": "^private-task", "tomatoes_completed": None,
                            "tomatoes_total": 5, "status": "completed", "occurrence_date": today,
                        },
                    ],
                    "steam_unlock_gate": {
                        "completed_tomatoes": 2,
                        "required_completed_tomatoes": 6,
                        "primary_task_id": "^private-task",
                        "primary_task_completed": True,
                        "eligible": False,
                    },
                }
                service.next_action.task_sync = MagicMock(return_value=(200, advisor_state, None))
                gate = service.steam_gate_status()
                self.assertEqual(gate["completed_tomatoes"], 5)
                self.assertEqual(gate["required_completed_tomatoes"], 5)
                self.assertTrue(gate["tomato_requirement_met"])
                self.assertTrue(gate["eligible"])
                self.assertEqual(gate["tomato_count_source"], "completed_tasks_planned_tomatoes")

    def test_system_status_explains_unavailable_steam_unlock_gate(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as folder:
            database = str(Path(folder) / "service.sqlite3")
            with patch.dict(os.environ, {"FOCUS_GARDEN_DRY_RUN": "1", "FOCUS_GARDEN_DB": database}):
                service = GardenService(Path(__file__).resolve().parents[1])
                with patch.object(service, "steam_gate_status", side_effect=ConnectionError("offline")):
                    indicator = service.steam_unlock_indicator()
                self.assertFalse(indicator["available"])
                self.assertFalse(indicator["eligible"])
                self.assertIn("继续保持 Steam 锁定", indicator["blocking_reasons"][0])

    def test_system_status_appends_steam_unlock_indicator_last(self):
        root = Path(__file__).resolve().parents[1]
        script = (root / "static" / "lease-status.js").read_text(encoding="utf-8")
        self.assertIn("Steam 解锁指标", script)
        self.assertIn("完成番茄", script)
        self.assertIn("今日主要任务", script)
        self.assertIn("两项必须同时满足", script)
        self.assertGreater(script.rfind("board.appendChild(unlockCard)"), script.rfind("board.appendChild(card)"))

    def test_usage_frequency_combines_focus_with_next_action_archives(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as folder:
            database = str(Path(folder) / "service.sqlite3")
            with patch.dict(os.environ, {"FOCUS_GARDEN_DRY_RUN": "1", "FOCUS_GARDEN_DB": database}):
                service = GardenService(Path(__file__).resolve().parents[1])
                completed = service.db.create_focus("study", 40, "2026-08-03T00:00:00+00:00", "2026-08-03T00:40:00+00:00")
                service.db.complete_focus(completed["id"])
                with service.db._connection() as conn:
                    conn.execute("UPDATE focus_sessions SET completed_at=? WHERE id=?", ("2026-08-06T03:00:00+00:00", completed["id"]))
                advisor_root = Path(folder) / "advisor" / "next_action"
                suggestions = advisor_root / "suggestions" / "2026-08-06"
                responses = advisor_root / "responses" / "2026-08-06"
                outcomes = advisor_root / "outcomes" / "2026-08-06"
                suggestions.mkdir(parents=True)
                responses.mkdir(parents=True)
                outcomes.mkdir(parents=True)
                (suggestions / "asked.json").write_text(json.dumps({"suggestion_id": "s1", "created_at": "2026-08-06T12:00:00+08:00"}), encoding="utf-8")
                (responses / "accepted.json").write_text(json.dumps({"suggestion_id": "s1", "result": "accepted", "received_at": "2026-08-06T12:05:00+08:00"}), encoding="utf-8")
                (outcomes / "completed.json").write_text(json.dumps({"suggestion_id": "s1", "result": "completed", "received_at": "2026-08-06T12:40:00+08:00"}), encoding="utf-8")
                with patch.object(service, "advisor_data_root", advisor_root.parent):
                    usage = service.usage_frequency(datetime.fromisoformat("2026-08-07T12:00:00+08:00"))
                current = usage["days"][1]["current"]
                self.assertEqual(current, {"focus_minutes": 40, "asked_suggestions": 1, "accepted_suggestions": 1, "completed_suggestions": 1})

    def test_focus_start_uses_safe_cold_turkey_mode(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as folder:
            database = str(Path(folder) / "service.sqlite3")
            with patch.dict(os.environ, {"FOCUS_GARDEN_DRY_RUN":"1", "FOCUS_GARDEN_DB":database}):
                service = GardenService(Path(__file__).resolve().parents[1])
                session = service.start_focus("study", 5)
                self.assertEqual(session["status"], "running")
                self.assertTrue(session["cold_turkey"])
                self.assertTrue(all(item["status"] == "simulated" for item in session["cold_turkey"]))
                service.db.cancel_focus(session["id"])
                self.assertIsNone(service.db.focus())

    def test_every_focus_locks_steam_even_when_windows_was_not_selected(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as folder:
            database = str(Path(folder) / "service.sqlite3")
            with patch.dict(os.environ, {"FOCUS_GARDEN_DRY_RUN": "1", "FOCUS_GARDEN_DB": database}):
                service = GardenService(Path(__file__).resolve().parents[1])
                session = service.start_focus(
                    "study", 20, [], task_id="^8m2kx7q4", task_title="Linked task", source="obsidian"
                )
                self.assertEqual((session["task_id"], session["source"]), ("^8m2kx7q4", "obsidian"))
                self.assertIn("windows", session["targets"])
                self.assertEqual(session["blocks"], ["steam游戏"])
                self.assertTrue(all(item["status"] == "simulated" for item in session["cold_turkey"]))

    def test_focus_pause_auto_resumes_once_and_keeps_half_credit_rule(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as folder:
            database = str(Path(folder) / "service.sqlite3")
            with patch.dict(os.environ, {"FOCUS_GARDEN_DRY_RUN": "1", "FOCUS_GARDEN_DB": database}):
                service = GardenService(Path(__file__).resolve().parents[1])
                session = service.start_focus("study", 20, [])
                paused = service.pause_focus(1)
                self.assertTrue(paused["paused"])
                self.assertEqual(paused["pause_minutes"], 1)
                self.assertIn("resume_at", paused)
                with self.assertRaises(ValueError):
                    service.pause_focus(1)
                # The reconciler must resume independently of a web page or
                # Obsidian instance; make the confirmed deadline due.
                with service.db._connection() as conn:
                    conn.execute(
                        "UPDATE focus_pauses SET resume_at=? WHERE session_id=?",
                        ((datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat(timespec="seconds"), session["id"]),
                    )
                service.reconcile_focus()
                resumed = service.db.focus(session["id"])
                self.assertFalse(resumed["paused"])
                self.assertTrue(resumed["was_paused"])
                start = datetime.fromisoformat(session["ends_at"])
                end = datetime.fromisoformat(resumed["ends_at"])
                self.assertEqual(int((end - start).total_seconds()), 60)

    def test_focus_schedule_and_cycle_validate_the_published_duration_sets(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as folder:
            database = str(Path(folder) / "service.sqlite3")
            with patch.dict(os.environ, {"FOCUS_GARDEN_DRY_RUN": "1", "FOCUS_GARDEN_DB": database}):
                service = GardenService(Path(__file__).resolve().parents[1])
                with self.assertRaises(ValueError):
                    service.start_focus("study", 25, ["phone"])
                with self.assertRaises(ValueError):
                    service.create_schedule("study", 10, ["phone"], "2030-01-01T08:00:00+00:00")
                scheduled = service.create_schedule("study", 20, ["windows"], "2030-01-01T08:00:00+00:00")
                self.assertEqual(scheduled["kind"], "scheduled")
                cycle = service.create_continuous_focus("study", 30, 5, 2, ["phone"])
                self.assertEqual(cycle["rounds"], 2)

    def test_plant_reward_decodes_url_encoded_reward_id(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as folder:
            database = str(Path(folder) / "service.sqlite3")
            with patch.dict(os.environ, {"FOCUS_GARDEN_DRY_RUN": "1", "FOCUS_GARDEN_DB": database}):
                service = GardenService(Path(__file__).resolve().parents[1])
                reward_id = "pi:intervention:test-event"
                service.db.import_rewards([{
                    "id": reward_id,
                    "type": "early_sleep",
                    "reason": "test",
                    "occurred_at": "2026-08-02T12:00:00+00:00",
                    "source": "test",
                    "payload": {},
                }])
                server = GardenHTTPServer(("127.0.0.1", 0), service)
                thread = threading.Thread(target=server.serve_forever, daemon=True)
                thread.start()
                try:
                    url = (
                        f"http://127.0.0.1:{server.server_address[1]}"
                        "/api/rewards/pi%3Aintervention%3Atest-event/plant"
                    )
                    request = urllib.request.Request(
                        url,
                        data=json.dumps({"species_id": "dandelion"}).encode("utf-8"),
                        headers={"Content-Type": "application/json"},
                        method="POST",
                    )
                    with urllib.request.urlopen(request) as response:
                        planted = json.load(response)
                        status = response.status
                    self.assertEqual(status, 201)
                    self.assertEqual(planted["reward_id"], reward_id)
                finally:
                    server.shutdown()
                    server.server_close()
                    thread.join(timeout=2)

    def test_catalog_keeps_only_minecraft_mushrooms(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as folder:
            database = str(Path(folder) / "service.sqlite3")
            with patch.dict(os.environ, {"FOCUS_GARDEN_DRY_RUN": "1", "FOCUS_GARDEN_DB": database}):
                root = Path(__file__).resolve().parents[1]
                service = GardenService(root)
                mushrooms = [plant for plant in service.catalog if plant["category"] == "mushroom"]
                self.assertEqual({plant["id"] for plant in mushrooms}, {"red_mushroom", "brown_mushroom"})
                self.assertTrue(all((root / "static" / plant["sprite"]).is_file() for plant in mushrooms))

    def test_catalog_groups_new_and_mushroom_content_as_advanced_with_local_sprites(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as folder:
            database = str(Path(folder) / "service.sqlite3")
            with patch.dict(os.environ, {"FOCUS_GARDEN_DRY_RUN": "1", "FOCUS_GARDEN_DB": database}):
                root = Path(__file__).resolve().parents[1]
                service = GardenService(root)
                expected_advanced = {
                    "red_mushroom", "brown_mushroom", "cherry_sapling", "mangrove_propagule",
                    "sunflower", "peony", "torchflower", "spore_blossom", "beehive",
                    "flowering_azalea_bush", "rose_bush", "bamboo_shoot", "pumpkin", "lilac",
                }
                published = {plant["id"] for plant in service.catalog}
                advanced = {plant["id"] for plant in service.catalog if plant.get("tier") == "advanced"}
                self.assertTrue(expected_advanced.issubset(published))
                self.assertEqual(advanced, expected_advanced)
                self.assertEqual(len([plant for plant in service.catalog if plant.get("tier") == "basic"]), 18)
                self.assertTrue(all(
                    (root / "static" / plant["sprite"]).is_file()
                    for plant in service.catalog if plant["id"] in expected_advanced
                ))

    def test_catalog_page_has_basic_and_advanced_filters(self):
        root = Path(__file__).resolve().parents[1]
        page = (root / "static" / "index.html").read_text(encoding="utf-8")
        script = (root / "static" / "app.js").read_text(encoding="utf-8")
        self.assertIn('id="catalogTierTabs"', page)
        self.assertIn('data-catalog-tier="basic"', script)
        self.assertIn('data-catalog-tier="advanced"', script)
        self.assertIn("state.catalogTier=button.dataset.catalogTier;renderCatalog()", script)

    def test_sync_script_does_not_reference_removed_pi_status_element(self):
        root = Path(__file__).resolve().parents[1]
        page = (root / "static" / "index.html").read_text(encoding="utf-8")
        script = (root / "static" / "app.js").read_text(encoding="utf-8")
        self.assertNotIn("#piStatus", script)
        self.assertIn('id="syncText"', page)

    def test_focus_profile_picker_is_centered_and_has_its_own_control_style(self):
        root = Path(__file__).resolve().parents[1]
        page = (root / "static" / "index.html").read_text(encoding="utf-8")
        styles = (root / "static" / "style.css").read_text(encoding="utf-8")
        self.assertIn('class="focus-profile-control"', page)
        self.assertIn('class="focus-profile-select"', page)
        self.assertIn('aria-label="专注模式"', page)
        self.assertIn('.focus-options{display:grid;place-items:center', styles)
        self.assertIn('.focus-profile-select:after', styles)

    def test_task_postponement_badge_is_used_in_list_and_calendar(self):
        root = Path(__file__).resolve().parents[1]
        script = (root / "static" / "app.js").read_text(encoding="utf-8")
        styles = (root / "static" / "style.css").read_text(encoding="utf-8")
        self.assertIn("operation:'postpone'", script)
        self.assertIn('拖延 · ${days}天', script)
        self.assertGreaterEqual(script.count("procrastinationBadge(task)"), 3)
        self.assertIn("task.procrastinated?' is-procrastinated'", script)
        self.assertIn(".task-procrastination-badge", styles)
        self.assertIn(".calendar-task.is-procrastinated", styles)

    def test_recent_context_proxy_only_forwards_fixed_loopback_paths_with_bridge_header(self):
        response = MagicMock()
        response.status = 200
        response.read.return_value = b'{"revision":1}'
        response.headers = {}
        context = MagicMock()
        context.__enter__.return_value = response
        proxy = NextActionProxy({"next_action": {"base_url": "http://127.0.0.1:8767"}})
        with patch("focus_garden.server.urlopen", return_value=context) as open_url:
            status, data, _ = proxy.recent_context(
                "create", "POST", body={"content": "mingtian", "expected_revision": 0}
            )
        request = open_url.call_args.args[0]
        self.assertEqual(status, 200)
        self.assertEqual(data["revision"], 1)
        self.assertEqual(request.full_url, "http://127.0.0.1:8767/api/recent-context")
        self.assertEqual(request.get_header("X-focus-garden-bridge"), "1")
        with self.assertRaises(ValueError):
            proxy.recent_context("ack", "POST", body={})
        with self.assertRaises(ValueError):
            proxy.recent_context("update", "POST", body={}, note_id="../secrets")
        with patch("focus_garden.server.urlopen", return_value=context) as open_url2:
            proxy.recent_context("pin", "POST", body={"expected_revision": 1}, note_id="rc_abc123")
        request2 = open_url2.call_args.args[0]
        self.assertEqual(
            request2.full_url,
            "http://127.0.0.1:8767/api/recent-context/rc_abc123/pin",
        )
        self.assertEqual(request2.get_header("X-focus-garden-bridge"), "1")

    def test_recent_context_proxy_rejects_unknown_http_paths(self):
        proxy = NextActionProxy({"next_action": {"base_url": "http://127.0.0.1:8767"}})
        for target in ("list", "relevant", "create", "update", "archive", "unarchive", "pin", "unpin", "confirm"):
            self.assertIn(target, proxy._RECENT_CONTEXT_PATHS)
        with self.assertRaises(ValueError):
            proxy.recent_context("explode", "GET")

    def test_goal_agent_proxy_only_forwards_fixed_loopback_paths_with_bridge_header(self):
        response = MagicMock()
        response.status = 200
        response.read.return_value = b'{"plan_version":1}'
        response.headers = {}
        context = MagicMock()
        context.__enter__.return_value = response
        proxy = NextActionProxy({"next_action": {"base_url": "http://127.0.0.1:8767"}})
        with patch("focus_garden.server.urlopen", return_value=context) as open_url:
            status, data, _ = proxy.goal_agent("state", "GET")
        request = open_url.call_args.args[0]
        self.assertEqual((status, data["plan_version"]), (200, 1))
        self.assertEqual(request.full_url, "http://127.0.0.1:8767/api/goal-agent/state")
        self.assertEqual(request.get_header("X-focus-garden-bridge"), "1")
        self.assertIsNone(request.get_header("Cookie"))
        with self.assertRaises(ValueError):
            proxy.goal_agent("files", "GET")

        with patch("focus_garden.server.urlopen", return_value=context) as scoped_url:
            proxy.goal_agent_scoped(
                "/api/goal-agent/plan-items/w1-c-p1/accept-day",
                body={"request_id": "garden-12345678", "base_plan_version": 1},
            )
        scoped_request = scoped_url.call_args.args[0]
        self.assertEqual(
            scoped_request.full_url,
            "http://127.0.0.1:8767/api/goal-agent/plan-items/w1-c-p1/accept-day",
        )
        self.assertEqual(scoped_request.get_header("X-focus-garden-bridge"), "1")
        with self.assertRaises(ValueError):
            proxy.goal_agent_scoped(
                "/api/goal-agent/../../private",
                body={"request_id": "garden-12345678", "base_plan_version": 1},
            )

if __name__ == "__main__":
    unittest.main()
