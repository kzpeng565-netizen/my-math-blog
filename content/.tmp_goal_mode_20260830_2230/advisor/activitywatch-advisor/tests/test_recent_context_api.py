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


def _settings(root):
    return {
        "output_root": str(root / "data"),
        "timezone": "Asia/Shanghai",
        "model": {"endpoint": "https://api.deepseek.com/chat/completions"},
        "recent_context": {
            "enabled": True,
            "parser_enabled": False,
            "selector_enabled": False,
            "max_content_chars": 500,
            "max_impact_chars": 100,
            "review_after_days": 14,
        },
    }


class RecentContextApiTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        settings_path = self.root / "settings.json"
        settings_path.write_text(json.dumps(_settings(self.root)), encoding="utf-8")
        self.server = TestServer(("127.0.0.1", 0), Handler)
        self.server.app_state = AppState(settings_path, self.root / "env")
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.port = self.server.server_address[1]

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self._tmp.cleanup()

    def _request(self, path, method="GET", body=None, header=True):
        data = json.dumps(body).encode("utf-8") if body is not None else None
        request = urllib.request.Request(
            f"http://127.0.0.1:{self.port}{path}", data=data, method=method
        )
        if header:
            request.add_header("X-Focus-Garden-Bridge", "1")
        if data is not None:
            request.add_header("Content-Type", "application/json")
        for attempt in range(3):
            try:
                with urllib.request.urlopen(request, timeout=10) as response:
                    raw = response.read().decode("utf-8")
                    return response.status, (json.loads(raw) if raw else {})
            except urllib.error.HTTPError as error:
                raw = error.read().decode("utf-8")
                return error.code, (json.loads(raw) if raw else {})
            except (ConnectionAbortedError, ConnectionResetError, TimeoutError) as error:
                if attempt == 2:
                    raise
                continue
        raise AssertionError("request did not complete")

    def test_auth_requires_loopback_and_bridge_header(self):
        status, _ = self._request("/api/recent-context", header=False)
        self.assertEqual(status, 401)
        status, body = self._request("/api/recent-context", header=True)
        self.assertEqual(status, 200)
        self.assertIn("notes", body)
        self.assertEqual(body["revision"], 0)

    def test_subpath_auth_also_requires_header(self):
        status, _ = self._request("/api/recent-context/relevant", header=False)
        self.assertEqual(status, 401)
        status, body = self._request("/api/recent-context/relevant", header=True)
        self.assertEqual(status, 200)
        self.assertIn("as_of", body)

    def test_create_and_revision_conflict(self):
        status, body = self._request(
            "/api/recent-context", "POST", {"content": "明天去实验室", "impact_text": "明天下午", "expected_revision": 0}
        )
        self.assertEqual(status, 201)
        self.assertEqual(body["revision"], 1)
        note_id = body["note"]["id"]
        status, conflict = self._request(
            "/api/recent-context", "POST", {"content": "第二条", "impact_text": "今天", "expected_revision": 0}
        )
        self.assertEqual(status, 409)
        self.assertEqual(conflict["code"], "revision_conflict")
        self.assertEqual(conflict["current_revision"], 1)
        status, body = self._request(
            "/api/recent-context", "POST", {"content": "第二条", "impact_text": "今天", "expected_revision": 1}
        )
        self.assertEqual(status, 201)
        self.assertEqual(body["revision"], 2)

    def test_missing_expected_revision_rejected(self):
        status, _ = self._request("/api/recent-context", "POST", {"content": "x", "impact_text": "今天"})
        self.assertEqual(status, 400)

    def test_id_scoped_mutations(self):
        created = self._request(
            "/api/recent-context", "POST", {"content": "动态", "impact_text": "本周", "expected_revision": 0}
        )[1]
        note_id = created["note"]["id"]
        status, body = self._request(
            f"/api/recent-context/{note_id}/pin", "POST", {"expected_revision": 1}
        )
        self.assertEqual(status, 200)
        self.assertTrue(body["note"]["pinned"])
        status, body = self._request(
            f"/api/recent-context/{note_id}/archive", "POST", {"expected_revision": 2}
        )
        self.assertEqual(status, 200)
        self.assertTrue(body["note"]["archived"])
        status, body = self._request("/api/recent-context", header=True)
        self.assertEqual(len(body["notes"]), 0)
        status, body = self._request("/api/recent-context?include_archived=1", header=True)
        self.assertEqual(len(body["notes"]), 1)
        status, body = self._request(
            f"/api/recent-context/{note_id}/confirm", "POST", {"expected_revision": 3}
        )
        self.assertEqual(status, 200)
        status, body = self._request(
            f"/api/recent-context/{note_id}/update", "POST",
            {"expected_revision": 4, "content": "新内容", "impact_text": "明天"},
        )
        self.assertEqual(status, 200)
        self.assertEqual(body["note"]["content"], "新内容")

    def test_unknown_subpath_rejected_even_with_header(self):
        status, _ = self._request("/api/recent-context/foo/explode", "POST", {"expected_revision": 0})
        self.assertEqual(status, 404)

    def test_corrupt_state_returns_503(self):
        state_dir = self.root / "data" / "recent_context"
        state_dir.mkdir(parents=True)
        (state_dir / "state.json").write_text("{broken", encoding="utf-8")
        status, body = self._request("/api/recent-context", header=True)
        self.assertEqual(status, 503)
        self.assertEqual(body["error"], "recent_context_state_corrupt")
        status, _ = self._request(
            "/api/recent-context", "POST", {"content": "x", "impact_text": "今天", "expected_revision": 0}
        )
        self.assertEqual(status, 503)
        self.assertEqual(len(list(state_dir.glob("state.json.corrupt-*"))), 1)


if __name__ == "__main__":
    unittest.main()