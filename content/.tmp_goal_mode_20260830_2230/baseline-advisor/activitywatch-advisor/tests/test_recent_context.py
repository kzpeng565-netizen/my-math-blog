import json
import sys
import tempfile
import threading
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from recent_context import (
    PARSE_SYSTEM_PROMPT,
    RecentContextConflictError,
    RecentContextCorruptError,
    RecentContextNotFoundError,
    coarse_candidates,
    confirm_note,
    create_note,
    list_notes,
    load_notes,
    relevant_notes,
    set_archived,
    set_pinned,
    update_note,
)

TZ = ZoneInfo("Asia/Shanghai")
NOW = datetime(2026, 8, 6, 22, 0, 0, tzinfo=TZ)


def settings(parser_enabled=False, **overrides):
    cfg = {
        "enabled": True,
        "direct_window_hours": 24,
        "preparation_window_days": 7,
        "review_after_days": 14,
        "parser_enabled": parser_enabled,
        "parser_model": "deepseek-v4-flash",
        "parser_thinking": False,
        "parser_timeout_seconds": 10,
        "selector_enabled": True,
        "selector_model": "deepseek-v4-flash",
        "selector_thinking": False,
        "selector_candidate_limit": 30,
        "selector_output_limit": 6,
        "selector_timeout_seconds": 10,
        "card_limit": 3,
        "max_content_chars": 500,
        "max_impact_chars": 100,
    }
    cfg.update(overrides)
    return {
        "timezone": "Asia/Shanghai",
        "model": {"endpoint": "https://api.deepseek.com/chat/completions"},
        "recent_context": cfg,
    }


def fake_generation(usage=None):
    return {
        "usage": usage
        or {
            "prompt_tokens": 120,
            "completion_tokens": 35,
            "total_tokens": 155,
        }
    }


class RecentContextStorageTests(unittest.TestCase):
    def test_create_requires_revision_and_returns_note(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaises(ValueError):
                create_note(root, "内容", "影响", None, settings())
            result = create_note(root, "明天下午临时要去实验室", "明天下午", 0, settings())
            self.assertEqual(result["revision"], 1)
            note = result["note"]
            self.assertTrue(note["id"].startswith("rc_"))
            self.assertEqual(note["content"], "明天下午临时要去实验室")
            self.assertEqual(note["impact_text"], "明天下午")
            self.assertEqual(note["status"], "conditional")
            state = json.loads((root / "recent_context" / "state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["schema_version"], 1)
            self.assertEqual(state["revision"], 1)
            self.assertEqual(len(state["notes"]), 1)

    def test_revision_conflict_raises_409_semantics(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            create_note(root, "一", "今天", 0, settings())
            with self.assertRaises(RecentContextConflictError) as ctx:
                create_note(root, "二", "明天", 0, settings())
            self.assertEqual(ctx.exception.current_revision, 1)
            # Correct revision works.
            create_note(root, "二", "明天", 1, settings())
            self.assertEqual(load_notes(root)[0]["content"], "一")

    def test_created_at_immutable_and_edit_keeps_it(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            created = create_note(root, "原文", "今天", 0, settings())
            note_id = created["note"]["id"]
            updated = update_note(root, note_id, 1, settings(), content="新原文", now=NOW)
            self.assertEqual(updated["note"]["created_at"], created["note"]["created_at"])
            self.assertNotEqual(updated["note"]["updated_at"], created["note"]["updated_at"])
            self.assertEqual(updated["note"]["content"], "新原文")

    def test_archive_pin_confirm_and_list(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            created = create_note(root, "动态", "本周", 0, settings(), now=NOW)
            note_id = created["note"]["id"]
            set_pinned(root, note_id, 1, True, now=NOW)
            pinned = set_archived(root, note_id, 2, True, now=NOW)
            self.assertTrue(pinned["note"]["pinned"])
            self.assertTrue(pinned["note"]["archived"])
            listed = list_notes(root, now=NOW)
            self.assertEqual(listed["notes"], [])
            archived = list_notes(root, include_archived=True, now=NOW)
            self.assertEqual(len(archived["notes"]), 1)
            restored = set_archived(root, note_id, 3, False, now=NOW)
            self.assertFalse(restored["note"]["archived"])
            confirmed = confirm_note(root, note_id, 4, now=NOW)
            self.assertGreaterEqual(confirmed["note"]["confirmed_at"], created["note"]["confirmed_at"])
            with self.assertRaises(RecentContextNotFoundError):
                set_pinned(root, "rc_missing_0000", 5, True, now=NOW)

    def test_validation_limits(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaises(ValueError):
                create_note(root, "", "今天", 0, settings())
            with self.assertRaises(ValueError):
                create_note(root, "x" * 501, "今天", 0, settings())
            with self.assertRaises(ValueError):
                create_note(root, "内容", "y" * 101, 0, settings())

    def test_rlock_serializes_concurrent_mutations(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            created = create_note(root, "并发", "今天", 0, settings())
            note_id = created["note"]["id"]
            outcomes = []

            def worker(kind):
                try:
                    if kind == "archive":
                        set_archived(root, note_id, 1, True, now=NOW)
                    else:
                        set_pinned(root, note_id, 1, True, now=NOW)
                    outcomes.append(kind)
                except RecentContextConflictError:
                    outcomes.append("conflict")

            threads = [threading.Thread(target=worker, args=(kind,)) for kind in ("archive", "pin")]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
            self.assertEqual(sorted(outcomes), ["archive", "conflict"])
            note = list_notes(root, include_archived=True, now=NOW)["notes"][0]
            self.assertEqual(note["archived"] + note["pinned"], 1)
            state = json.loads((root / "recent_context" / "state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["revision"], 2)

    def test_corrupt_file_503_and_single_backup(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "recent_context" / "state.json"
            path.parent.mkdir(parents=True)
            path.write_text("{not valid json", encoding="utf-8")
            with self.assertRaises(RecentContextCorruptError):
                list_notes(root, now=NOW)
            with self.assertRaises(RecentContextCorruptError):
                create_note(root, "x", "今天", 0, settings())
            backups = list(path.parent.glob("state.json.corrupt-*"))
            self.assertEqual(len(backups), 1)
            with self.assertRaises(RecentContextCorruptError):
                list_notes(root, now=NOW)
            self.assertEqual(len(list(path.parent.glob("state.json.corrupt-*"))), 1)
            self.assertTrue(path.exists())

    def test_missing_file_initializes_empty(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertEqual(list_notes(root, now=NOW)["notes"], [])
            self.assertEqual(load_notes(root), [])


class RecentContextStatusTests(unittest.TestCase):
    def _seed(self, root, impact, parse, created="2026-08-06T21:30:00+08:00"):
        revision = list_notes(root, now=NOW)["revision"]
        result = create_note(root, "动态：" + impact, impact, revision, settings(), now=datetime.fromisoformat(created))
        note_id = result["note"]["id"]
        with patch("recent_context._request_json_report", return_value=({}, fake_generation())):
            from recent_context import _run_parse_and_persist
            notes = load_notes(root)
            note = next(n for n in notes if n["id"] == note_id)
            _run_parse_and_persist(root, note, settings(), "Asia/Shanghai", datetime.fromisoformat(created))
        # Overwrite parse deterministically (bypass AI).
        path = root / "recent_context" / "state.json"
        state = json.loads(path.read_text(encoding="utf-8"))
        for note in state["notes"]:
            if note["id"] == note_id:
                note["parse"] = parse
        path.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
        return note_id

    def test_day_status_active_upcoming_ended(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            nid = self._seed(root, "今天", {"v": 1, "hash": "x", "type": "day", "date": "2026-08-06", "confidence": "high"})
            listed = list_notes(root, now=NOW)["notes"]
            self.assertEqual(next(n for n in listed if n["id"] == nid)["status"], "active")
            nid2 = self._seed(root, "明天", {"v": 1, "hash": "x", "type": "day", "date": "2026-08-07", "confidence": "high"})
            listed = list_notes(root, now=NOW)["notes"]
            self.assertEqual(next(n for n in listed if n["id"] == nid2)["status"], "upcoming")
            nid3 = self._seed(root, "昨天", {"v": 1, "hash": "x", "type": "day", "date": "2026-08-05", "confidence": "high"})
            listed = list_notes(root, now=NOW)["notes"]
            self.assertEqual(next(n for n in listed if n["id"] == nid3)["status"], "ended")

    def test_range_status_and_parse_text(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            nid = self._seed(root, "区间", {"v": 1, "hash": "x", "type": "range", "start": "2026-08-10", "end": "2026-08-15", "confidence": "high"})
            listed = list_notes(root, now=NOW)["notes"]
            note = next(n for n in listed if n["id"] == nid)
            self.assertEqual(note["status"], "upcoming")
            self.assertEqual(note["parse_text"], "8月10日至8月15日")

    def test_minute_precise_range_status_and_text(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            nid = self._seed(root, "明天14:30到16:00", {"v": 2, "hash": "x", "type": "range", "start": "2026-08-07T14:30+08:00", "end": "2026-08-07T16:00+08:00", "confidence": "high"})
            note = next(n for n in list_notes(root, now=NOW)["notes"] if n["id"] == nid)
            self.assertEqual(note["status"], "upcoming")
            self.assertEqual(note["parse_text"], "8月7日 14:30至16:00")
            active = datetime(2026, 8, 7, 15, 0, tzinfo=TZ)
            self.assertEqual(next(n for n in list_notes(root, now=active)["notes"] if n["id"] == nid)["status"], "active")

    def test_cross_year_day_parse(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            nid = self._seed(root, "跨年", {"v": 1, "hash": "x", "type": "day", "date": "2027-01-03", "confidence": "high"},
                             created="2026-12-31T21:30:00+08:00")
            listed = list_notes(root, now=NOW)["notes"]
            self.assertEqual(next(n for n in listed if n["id"] == nid)["status"], "upcoming")

    def test_conditional_and_needs_review(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            nid = self._seed(root, "等老师回复", {"v": 1, "hash": "x", "type": "event", "relation": "until", "confidence": "medium"})
            listed = list_notes(root, now=NOW)["notes"]
            note = next(n for n in listed if n["id"] == nid)
            self.assertEqual(note["status"], "conditional")
            # 15 days later -> needs_review (pinned cannot bypass)
            later = datetime(2026, 8, 22, 12, 0, 0, tzinfo=TZ)
            set_pinned(root, nid, 1, True, now=later)
            listed = list_notes(root, now=later)["notes"]
            self.assertEqual(next(n for n in listed if n["id"] == nid)["status"], "needs_review")
            confirm_note(root, nid, 2, now=later)
            listed = list_notes(root, now=later)["notes"]
            self.assertEqual(next(n for n in listed if n["id"] == nid)["status"], "conditional")

    def test_daypart_not_hard_expiry(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            nid = self._seed(root, "明天下午", {"v": 1, "hash": "x", "type": "daypart", "date": "2026-08-07", "part": "afternoon", "confidence": "high"})
            listed = list_notes(root, now=NOW)["notes"]
            self.assertEqual(next(n for n in listed if n["id"] == nid)["status"], "upcoming")
            self.assertEqual(next(n for n in listed if n["id"] == nid)["parse_text"], "8月7日下午")


class RecentContextCoarseTests(unittest.TestCase):
    def _note(self, note_id, content, impact, created, parse, archived=False, pinned=False, confirmed=None):
        note = {
            "id": note_id,
            "content": content,
            "impact_text": impact,
            "created_at": created,
            "updated_at": created,
            "confirmed_at": confirmed or created,
            "archived": archived,
            "pinned": pinned,
            "parse": parse,
        }
        return note

    def test_coarse_excludes_ended_archived_needs_review_and_far_future(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            notes = [
                self._note("rc_a", "已结束", "昨天", "2026-08-05T10:00:00+08:00", {"v": 1, "hash": "a", "type": "day", "date": "2026-08-05", "confidence": "high"}),
                self._note("rc_b", "已归档", "今天", "2026-08-06T10:00:00+08:00", {"v": 1, "hash": "b", "type": "day", "date": "2026-08-06", "confidence": "high"}, archived=True),
                self._note("rc_c", "老事件", "等确认", "2026-07-01T10:00:00+08:00", {"v": 1, "hash": "c", "type": "event", "relation": "until", "confidence": "medium"}),
                self._note("rc_d", "太远", "下个月", "2026-08-06T10:00:00+08:00", {"v": 1, "hash": "d", "type": "day", "date": "2026-09-01", "confidence": "high"}),
                self._note("rc_e", "明天", "明天", "2026-08-06T10:00:00+08:00", {"v": 1, "hash": "e", "type": "day", "date": "2026-08-07", "confidence": "high"}),
                self._note("rc_f", "今天", "今天", "2026-08-06T10:00:00+08:00", {"v": 1, "hash": "f", "type": "day", "date": "2026-08-06", "confidence": "high"}),
            ]
            result = coarse_candidates(notes, NOW, settings())
            ids = [note["id"] for note in result["candidates"]]
            self.assertNotIn("rc_a", ids)
            self.assertNotIn("rc_b", ids)
            self.assertNotIn("rc_c", ids)
            self.assertNotIn("rc_d", ids)
            self.assertIn("rc_e", ids)
            self.assertIn("rc_f", ids)
            self.assertIn("rc_f", result["forced_ids"])
            self.assertIn("rc_e", result["forced_ids"])

    def test_conditional_recent_is_candidate(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            notes = [
                self._note("rc_g", "等回复", "直到老师回复", "2026-08-05T10:00:00+08:00", {"v": 1, "hash": "g", "type": "event", "relation": "until", "confidence": "medium"}),
            ]
            result = coarse_candidates(notes, NOW, settings())
            self.assertEqual([note["id"] for note in result["candidates"]], ["rc_g"])
            self.assertEqual(result["forced_ids"], [])

    def test_candidate_limit_30(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            notes = [
                self._note(f"rc_{i:03d}", f"动态{i}", "未来几天", "2026-08-06T10:00:00+08:00",
                           {"v": 1, "hash": "x", "type": "vague", "confidence": "low"})
                for i in range(31)
            ]
            result = coarse_candidates(notes, NOW, settings())
            self.assertEqual(len(result["candidates"]), 30)


class RecentContextParserTests(unittest.TestCase):
    def test_parser_input_anchors_recorded_at_and_prompt(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            captured = {}

            def fake(model, messages):
                captured["messages"] = messages
                return (
                    {"type": "daypart", "date": "2026-08-07", "part": "afternoon", "confidence": "high"},
                    fake_generation(),
                )

            with patch("recent_context._request_json_report", side_effect=fake):
                result = create_note(root, "明天下午临时要去实验室", "明天下午", 0, settings(parser_enabled=True), now=NOW)
            user = json.loads(captured["messages"][-1]["content"])
            self.assertEqual(user["recorded_at"], NOW.isoformat(timespec="seconds"))
            self.assertIn("必须以 recorded_at 为基准", captured["messages"][0]["content"])
            note = result["note"]
            self.assertEqual(note["parse"]["date"], "2026-08-07")
            self.assertEqual(note["parse"]["part"], "afternoon")
            audit = (root / "recent_context" / "parse_audit.jsonl").read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(audit), 1)
            record = json.loads(audit[0])
            self.assertTrue(record["success"])
            self.assertEqual(record["note_id"], note["id"])
            self.assertEqual(record["prompt"], "recent-context-parse-v2")
            self.assertEqual(record["usage"]["input_tokens"], 120)

    def test_parser_timeout_keeps_note_and_saves_error(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch("recent_context._request_json_report", side_effect=RuntimeError("timeout")):
                result = create_note(root, "内容", "模糊", 0, settings(parser_enabled=True), now=NOW)
            note = result["note"]
            self.assertEqual(note["content"], "内容")
            self.assertNotIn("parse", note)
            state = json.loads((root / "recent_context" / "state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["notes"][0]["parse"]["error"], "parse_failed")
            audit = (root / "recent_context" / "parse_audit.jsonl").read_text(encoding="utf-8").strip().splitlines()
            self.assertFalse(json.loads(audit[0])["success"])

    def test_parser_invalid_json_saves_error(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch("recent_context._request_json_report", return_value=("not a dict", fake_generation())):
                result = create_note(root, "内容", "模糊", 0, settings(parser_enabled=True), now=NOW)
            state = json.loads((root / "recent_context" / "state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["notes"][0]["parse"]["error"], "parse_failed")

    def test_stale_parse_cannot_overwrite_new_edit(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch("recent_context._request_json_report", return_value=({"type": "day", "date": "2026-08-07", "confidence": "high"}, fake_generation())):
                created = create_note(root, "第一版", "明天", 0, settings(parser_enabled=True), now=NOW)
            note_id = created["note"]["id"]
            with patch("recent_context._request_json_report", return_value=({"type": "day", "date": "2026-08-10", "confidence": "high"}, fake_generation())):
                updated = update_note(root, note_id, 1, settings(parser_enabled=True), content="第二版", now=NOW)
            self.assertEqual(updated["note"]["parse"]["date"], "2026-08-10")
            # Simulate an old parser result (old source hash) trying to write back.
            from recent_context import _run_parse_and_persist, _source_hash
            stale = {
                "id": note_id,
                "content": "第一版",
                "impact_text": "明天",
                "created_at": created["note"]["created_at"],
            }
            stale_parse = {"v": 1, "hash": _source_hash("第一版", "明天"), "type": "day", "date": "2026-08-07", "confidence": "high"}
            _run_parse_and_persist(root, stale, settings(parser_enabled=False), "Asia/Shanghai", NOW)
            state = json.loads((root / "recent_context" / "state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["notes"][0]["parse"]["date"], "2026-08-10")

    def test_relevant_notes_returns_items_and_omitted_count(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch("recent_context._request_json_report", return_value=({"type": "day", "date": "2026-08-07", "confidence": "high"}, fake_generation())):
                create_note(root, "明天", "明天", 0, settings(parser_enabled=True), now=NOW)
            result = relevant_notes(root, now=NOW)
            self.assertEqual(result["as_of"], NOW.isoformat(timespec="seconds"))
            self.assertEqual(len(result["items"]), 1)
            self.assertEqual(result["omitted_count"], 0)
            self.assertIn("parse_text", result["items"][0])
    def test_normalize_parse_types_and_invalid_outputs(self):
        from recent_context import _normalize_parse
        day = _normalize_parse({"type": "day", "date": "2026-08-07", "confidence": "high"}, "h")
        self.assertEqual(day, {"v": 2, "hash": "h", "type": "day", "date": "2026-08-07", "confidence": "high"})
        rng = _normalize_parse({"type": "range", "start": "2026-08-10", "end": "2026-08-15", "confidence": "high"}, "h")
        self.assertEqual(rng["start"], "2026-08-10")
        self.assertEqual(rng["end"], "2026-08-15")
        precise = _normalize_parse({"type": "range", "start": "2026-08-10T14:30+08:00", "end": "2026-08-10T16:00+08:00", "confidence": "high"}, "h")
        self.assertEqual(precise["start"], "2026-08-10T14:30+08:00")
        event = _normalize_parse({"type": "event", "relation": "until", "confidence": "medium"}, "h")
        self.assertEqual(event["relation"], "until")
        self.assertNotIn("date", event)
        self.assertNotIn("start", event)
        open_ = _normalize_parse({"type": "open", "confidence": "low"}, "h")
        self.assertEqual(open_["type"], "open")
        vague = _normalize_parse({"type": "vague", "confidence": "low"}, "h")
        self.assertEqual(vague["type"], "vague")
        # Invalid outputs must raise (mapped to parse error upstream).
        with self.assertRaises(ValueError):
            _normalize_parse({"type": "range", "start": "2026-08-15", "end": "2026-08-10", "confidence": "high"}, "h")
        with self.assertRaises(ValueError):
            _normalize_parse({"type": "day", "date": "not-a-date", "confidence": "high"}, "h")
        with self.assertRaises(ValueError):
            _normalize_parse({"type": "fancy"}, "h")
        with self.assertRaises(ValueError):
            _normalize_parse("not a dict", "h")

if __name__ == "__main__":
    unittest.main()
