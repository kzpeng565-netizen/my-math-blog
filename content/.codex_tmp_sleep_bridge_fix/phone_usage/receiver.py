#!/usr/bin/env python3

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, unquote, urlparse
from urllib.request import Request, urlopen
from datetime import datetime
from threading import Lock
import gzip
import hmac
import json
import os
import sys
import tempfile


ROOT = Path("/home/conrad/phone_usage")
ADVISOR_SRC = Path("/home/conrad/workspace/activitywatch-advisor/src")
sys.path.insert(0, str(ADVISOR_SRC))

from user_annotations import AnnotationError, receive_annotation

INCOMING = ROOT / "incoming"
ARCHIVE = ROOT / "archive"
TOKEN = (ROOT / "token.txt").read_text(encoding="utf-8").strip()
FOCUS_BRIDGE_TOKEN_PATH = ROOT / "focus_bridge_token.txt"
FOCUS_GARDEN_BASE_URL = "http://127.0.0.1:8838"

HOST = "127.0.0.1"
PORT = 8765
MAX_UPLOAD_SIZE = 20 * 1024 * 1024
MAX_ANNOTATION_SIZE = 4 * 1024
MAX_BRIDGE_REQUEST_SIZE = 16 * 1024
BRIDGE_PATHS = {
    "/focus-bridge/pending": ("GET", "/api/focus-bridge/pending"),
    "/focus-bridge/decision": ("POST", "/api/focus-bridge/decision"),
    "/focus-bridge/event": ("POST", "/api/focus-bridge/event"),
    "/focus-bridge/heartbeat": ("POST", "/api/focus-bridge/heartbeat"),
}
ALLOWED_FILES = {
    "foreground.jsonl",
    "screen.jsonl",
    "heartbeat.jsonl",
    "tablet_foreground.jsonl",
    "tablet_screen.jsonl",
    "tablet_heartbeat.jsonl",
}
ARCHIVE_LOCKS = {filename: Lock() for filename in ALLOWED_FILES}

INCOMING.mkdir(parents=True, exist_ok=True)
ARCHIVE.mkdir(parents=True, exist_ok=True)


def atomic_write(target: Path, body: bytes) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        dir=target.parent,
        prefix=f".{target.name}.",
        suffix=".tmp",
    )

    try:
        with os.fdopen(descriptor, "wb") as temporary_file:
            temporary_file.write(body)
            temporary_file.flush()
            os.fsync(temporary_file.fileno())
        os.chmod(temporary_name, 0o600)
        os.replace(temporary_name, target)
    except Exception:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def parse_event_line(line: str) -> tuple[float, str, str]:
    event = json.loads(line)
    timestamp = event.get("timestamp") if isinstance(event, dict) else None
    if not isinstance(timestamp, str):
        raise ValueError("missing timestamp")
    event_time = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    canonical_line = json.dumps(
        event,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    return event_time.timestamp(), event_time.date().isoformat(), canonical_line


def merge_archive(day: str, filename: str, new_events: list[tuple[float, str]]) -> None:
    target = ARCHIVE / day / filename
    compressed_target = target.with_suffix(target.suffix + ".gz")

    with ARCHIVE_LOCKS[filename]:
        merged_events: dict[str, float] = {}

        if target.exists():
            existing_text = target.read_text(encoding="utf-8")
            for line in existing_text.splitlines():
                if line.strip():
                    timestamp, _, canonical_line = parse_event_line(line)
                    merged_events[canonical_line] = timestamp

        if compressed_target.exists():
            with gzip.open(compressed_target, "rt", encoding="utf-8") as source:
                for line in source:
                    if line.strip():
                        timestamp, _, canonical_line = parse_event_line(line)
                        merged_events[canonical_line] = timestamp

        for timestamp, canonical_line in new_events:
            merged_events[canonical_line] = timestamp

        ordered_lines = [
            line
            for line, _ in sorted(
                merged_events.items(),
                key=lambda item: (item[1], item[0]),
            )
        ]
        archive_body = ("\n".join(ordered_lines) + "\n").encode("utf-8")

        if compressed_target.exists() and not target.exists():
            atomic_write(
                compressed_target,
                gzip.compress(archive_body, mtime=0),
            )
        else:
            atomic_write(target, archive_body)


class UploadServer(ThreadingHTTPServer):
    daemon_threads = True
    request_queue_size = 16


class UploadHandler(BaseHTTPRequestHandler):
    server_version = "PhoneUsageReceiver/1.0"

    def setup(self) -> None:
        super().setup()
        self.connection.settimeout(15)

    def send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(
            payload,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path in BRIDGE_PATHS:
            self.handle_bridge_proxy("GET", path)
            return
        if path == "/health":
            self.send_json(200, {"ok": True, "service": "phone-usage"})
            return
        if urlparse(self.path).path == "/annotation":
            self.send_json(405, {"ok": False, "error": "method_not_allowed"})
            return
        self.send_json(404, {"ok": False, "error": "not_found"})

    def do_PUT(self) -> None:
        if urlparse(self.path).path == "/annotation":
            self.send_json(405, {"ok": False, "error": "method_not_allowed"})
            return
        self.handle_upload()

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path in BRIDGE_PATHS:
            self.handle_bridge_proxy("POST", path)
            return
        if path == "/annotation":
            self.handle_annotation()
            return
        self.handle_upload()

    def do_OPTIONS(self) -> None:
        if urlparse(self.path).path == "/annotation":
            self.send_json(405, {"ok": False, "error": "method_not_allowed"})
            return
        self.send_json(404, {"ok": False, "error": "not_found"})

    def bearer_token(self) -> str | None:
        header = self.headers.get("Authorization", "")
        prefix = "Bearer "
        if not header.startswith(prefix):
            return None
        return header[len(prefix):].strip()

    def read_limited_body(self, max_size: int) -> bytes | None:
        length_header = self.headers.get("Content-Length")
        if length_header is None:
            self.send_json(
                411,
                {"ok": False, "error": "content_length_required"},
            )
            return None
        try:
            length = int(length_header)
        except ValueError:
            self.send_json(
                400,
                {"ok": False, "error": "invalid_content_length"},
            )
            return None
        if length < 0 or length > max_size:
            self.send_json(413, {"ok": False, "error": "request_too_large"})
            return None
        body = self.rfile.read(length)
        if len(body) != length:
            self.send_json(400, {"ok": False, "error": "incomplete_body"})
            return None
        return body

    def parse_annotation_body(self, body: bytes) -> dict:
        try:
            text = body.decode("utf-8")
        except UnicodeDecodeError:
            raise AnnotationError("not_utf8")

        content_type = self.headers.get("Content-Type", "").split(";", 1)[0].strip()
        if content_type == "application/json":
            try:
                payload = json.loads(text or "{}")
            except json.JSONDecodeError:
                raise AnnotationError("invalid_json")
            if not isinstance(payload, dict):
                raise AnnotationError("invalid_json")
            return payload

        if content_type in {
            "",
            "application/x-www-form-urlencoded",
        }:
            parsed = parse_qs(text, keep_blank_values=True, strict_parsing=False)
            return {key: values[-1] if values else "" for key, values in parsed.items()}

        raise AnnotationError("unsupported_content_type")

    def handle_annotation(self) -> None:
        supplied_token = self.bearer_token()
        if supplied_token is None:
            self.send_json(401, {"ok": False, "error": "unauthorized"})
            return
        if not hmac.compare_digest(supplied_token, TOKEN):
            self.send_json(403, {"ok": False, "error": "forbidden"})
            return

        body = self.read_limited_body(MAX_ANNOTATION_SIZE)
        if body is None:
            return

        try:
            payload = self.parse_annotation_body(body)
            annotation = receive_annotation(
                payload.get("category"),
                payload.get("message", ""),
            )
        except AnnotationError as exc:
            self.send_json(400, {"ok": False, "error": exc.error})
            return
        except Exception as exc:
            print(
                f"annotation save failed: {exc.__class__.__name__}",
                flush=True,
            )
            self.send_json(500, {"ok": False, "error": "save_failed"})
            return

        self.send_json(
            201,
            {
                "ok": True,
                "annotation_id": annotation["annotation_id"],
                "received_at": annotation["received_at"],
                "category": annotation["category"],
                "related_report": annotation["primary_related_report"],
            },
        )

    def handle_bridge_proxy(self, method: str, path: str) -> None:
        route = BRIDGE_PATHS.get(path)
        if route is None or route[0] != method:
            self.send_json(405, {"ok": False, "error": "method_not_allowed"})
            return
        try:
            expected_token = FOCUS_BRIDGE_TOKEN_PATH.read_text(encoding="utf-8").strip()
        except OSError:
            self.send_json(503, {"ok": False, "error": "bridge_not_paired"})
            return
        supplied_token = self.bearer_token()
        if not expected_token or supplied_token is None:
            self.send_json(401, {"ok": False, "error": "unauthorized"})
            return
        if not hmac.compare_digest(supplied_token, expected_token):
            self.send_json(403, {"ok": False, "error": "forbidden"})
            return

        body = None
        if method == "POST":
            body = self.read_limited_body(MAX_BRIDGE_REQUEST_SIZE)
            if body is None:
                return
            try:
                parsed = json.loads(body.decode("utf-8") or "{}")
            except (UnicodeDecodeError, json.JSONDecodeError):
                self.send_json(400, {"ok": False, "error": "invalid_json"})
                return
            if not isinstance(parsed, dict):
                self.send_json(400, {"ok": False, "error": "invalid_json"})
                return

        request = Request(
            FOCUS_GARDEN_BASE_URL + route[1],
            data=body,
            headers={"Accept": "application/json", "Content-Type": "application/json; charset=utf-8"},
            method=method,
        )
        try:
            with urlopen(request, timeout=12) as response:
                payload = json.loads(response.read().decode("utf-8") or "{}")
                self.send_json(response.status, payload)
        except HTTPError as exc:
            try:
                payload = json.loads(exc.read().decode("utf-8") or "{}")
            except (UnicodeDecodeError, json.JSONDecodeError):
                payload = {"ok": False, "error": "bridge_upstream_error"}
            self.send_json(exc.code, payload)
        except (OSError, URLError, TimeoutError):
            self.send_json(503, {"ok": False, "error": "bridge_upstream_unavailable"})

    def handle_upload(self) -> None:
        path = unquote(urlparse(self.path).path)
        prefix = "/upload/"
        if not path.startswith(prefix):
            self.send_json(404, {"ok": False, "error": "not_found"})
            return

        filename = path[len(prefix):]
        if filename not in ALLOWED_FILES:
            self.send_json(404, {"ok": False, "error": "not_found"})
            return

        supplied_token = self.headers.get("X-Upload-Token", "")
        if not hmac.compare_digest(supplied_token, TOKEN):
            self.send_json(401, {"ok": False, "error": "unauthorized"})
            return

        length_header = self.headers.get("Content-Length")
        if length_header is None:
            self.send_json(
                411,
                {"ok": False, "error": "content_length_required"},
            )
            return

        try:
            length = int(length_header)
        except ValueError:
            self.send_json(
                400,
                {"ok": False, "error": "invalid_content_length"},
            )
            return

        if length < 0 or length > MAX_UPLOAD_SIZE:
            self.send_json(413, {"ok": False, "error": "file_too_large"})
            return

        body = self.rfile.read(length)
        if len(body) != length:
            self.send_json(400, {"ok": False, "error": "incomplete_body"})
            return

        try:
            text = body.decode("utf-8")
        except UnicodeDecodeError:
            self.send_json(400, {"ok": False, "error": "not_utf8"})
            return

        line_count = 0
        lines_by_day: dict[str, list[tuple[float, str]]] = {}
        try:
            for line_number, line in enumerate(text.splitlines(), start=1):
                if not line.strip():
                    continue
                timestamp, day, canonical_line = parse_event_line(line)
                lines_by_day.setdefault(day, []).append(
                    (timestamp, canonical_line)
                )
                line_count += 1
        except (json.JSONDecodeError, ValueError, TypeError) as exc:
            self.send_json(
                400,
                {
                    "ok": False,
                    "error": "invalid_json_line_or_timestamp",
                    "line": line_number,
                    "detail": str(exc),
                },
            )
            return

        for day, events in lines_by_day.items():
            merge_archive(day, filename, events)

        atomic_write(INCOMING / filename, body)
        self.send_json(
            200,
            {
                "ok": True,
                "file": filename,
                "bytes": len(body),
                "lines": line_count,
                "days": sorted(lines_by_day),
            },
        )

    def log_message(self, message_format: str, *args) -> None:
        path = urlparse(self.path).path
        if (
            path != "/health"
            and path != "/annotation"
            and not path.startswith("/upload/")
            and path not in BRIDGE_PATHS
        ):
            return
        print(
            f"{self.client_address[0]} "
            f"[{self.log_date_time_string()}] "
            f"{message_format % args}",
            flush=True,
        )


if __name__ == "__main__":
    server = UploadServer((HOST, PORT), UploadHandler)
    print(f"Phone usage receiver listening on {HOST}:{PORT}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nReceiver stopped.", flush=True)
    finally:
        server.server_close()
