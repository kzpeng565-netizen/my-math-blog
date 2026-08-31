import json
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from web_app import AppState, Handler


class TestServer(ThreadingHTTPServer):
    app_state = None


def _settings(root: Path) -> dict:
    return {
        "output_root": str(root / "data"),
        "timezone": "Asia/Shanghai",
        "model": {
            "endpoint": "https://example.invalid/chat",
            "name": "test-model",
            "thinking": "disabled",
            "max_tokens": 100,
            "timeout_seconds": 1,
            "retries": 0,
        },
        "goal_agent": {
            "database_path": str(root / "goal.sqlite3"),
            "material_root": str(root / "materials"),
            "prompt_path": str(root / "goal-agent.md"),
            "tavily_env_file": str(root / "missing-tavily.env"),
            "model_env_file": str(root / "missing-goal-model.env"),
            "model": {
                "provider": "openai_compatible",
                "protocol": "responses",
                "endpoint": "https://example.invalid/v1/responses",
                "name": "gpt-5.6-sol",
                "api_key_env": "GOAL_AGENT_API_KEY",
                "reasoning_effort": "medium",
                "max_output_tokens": 4500,
                "timeout_seconds": 1,
                "retries": 0,
            },
        },
    }


class GoalAgentApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        settings_path = self.root / "settings.json"
        settings_path.write_text(json.dumps(_settings(self.root)), encoding="utf-8")
        self.server = TestServer(("127.0.0.1", 0), Handler)
        self.server.app_state = AppState(settings_path, self.root / "missing.env")
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.port = self.server.server_address[1]

    def tearDown(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        self.temporary.cleanup()

    def _request(self, path: str, method: str = "GET", body: dict | None = None,
                 bridge: bool = True) -> tuple[int, dict]:
        raw = json.dumps(body).encode("utf-8") if body is not None else None
        request = urllib.request.Request(
            f"http://127.0.0.1:{self.port}{path}", data=raw, method=method
        )
        if bridge:
            request.add_header("X-Focus-Garden-Bridge", "1")
        if raw is not None:
            request.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                return response.status, json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            return error.code, json.loads(error.read().decode("utf-8"))

    def test_goal_surface_requires_focus_garden_bridge(self) -> None:
        status, _ = self._request("/api/goal-agent/state", bridge=False)
        self.assertEqual(status, 401)
        status, state = self._request("/api/goal-agent/state")
        self.assertEqual(status, 200)
        self.assertTrue(state["boundaries"]["next_action_is_separate"])
        self.assertEqual(state["schema_version"], 2)
        self.assertEqual(state["model"]["name"], "gpt-5.6-sol")
        self.assertEqual(len(state["course_profiles"]), 3)
        status, plan = self._request("/api/goal-agent/plan")
        self.assertEqual(status, 200)
        self.assertEqual(plan["plan_version"], 1)

    def test_feedback_write_and_plan_version_conflict(self) -> None:
        status, created = self._request(
            "/api/goal-agent/feedback",
            "POST",
            {
                "request_id": "api-feedback-12345678",
                "base_plan_version": 1,
                "track_id": "track-courses",
                "evidence_type": "progress_update",
                "deep_minutes": 120,
                "confidence": 3,
            },
        )
        self.assertEqual(status, 201)
        self.assertIn("event_id", created)
        status, conflict = self._request(
            "/api/goal-agent/feedback",
            "POST",
            {
                "request_id": "api-stale-12345678",
                "base_plan_version": 0,
                "track_id": "track-courses",
                "evidence_type": "progress_update",
                "deep_minutes": 30,
            },
        )
        self.assertEqual(status, 409)
        self.assertEqual(conflict["code"], "plan_version_conflict")
        self.assertEqual(conflict["current_plan_version"], 1)

    def test_course_progress_feedback_is_exposed_in_state(self) -> None:
        status, created = self._request(
            "/api/goal-agent/feedback",
            "POST",
            {
                "request_id": "api-course-12345678",
                "base_plan_version": 1,
                "track_id": "track-courses",
                "evidence_type": "course_progress",
                "deep_minutes": 90,
                "details": {
                    "course": "微分几何",
                    "taught_units": [
                        {
                            "unit_id": "differential-geometry-01-01",
                            "mastery": 2,
                        }
                    ],
                    "exercise_attempted": 2,
                    "exercise_correct": 1,
                },
            },
        )
        self.assertEqual(status, 201)
        self.assertGreater(created["plan_version"], 1)
        status, state = self._request("/api/goal-agent/state")
        self.assertEqual(status, 200)
        progress = state["course_progress"]["by_course"]["微分几何"]
        self.assertEqual(progress["confirmed_taught_units"], 1)
        self.assertNotIn("微分几何", state["course_progress"]["pending_input"])

    def test_unknown_goal_subpath_is_not_widened_by_bridge(self) -> None:
        status, _ = self._request("/api/goal-agent/private-files")
        self.assertEqual(status, 404)


if __name__ == "__main__":
    unittest.main()
