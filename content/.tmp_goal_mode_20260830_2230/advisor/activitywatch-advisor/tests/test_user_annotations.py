import json
import os
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path


SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

from user_annotations import (
    AnnotationError,
    build_annotation,
    find_primary_related_report,
    receive_annotation,
    rebuild_markdown_summaries,
    validate_annotation_fields,
)


class UserAnnotationTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)
        self.annotation_root = self.root / "data" / "user_annotations"
        self.received_at = datetime.fromisoformat("2026-07-28T15:40:12+08:00")

    def tearDown(self):
        self.directory.cleanup()

    def test_valid_category_zero_with_message(self):
        category, message = validate_annotation_fields(0, " 报告判断错了 ")
        self.assertEqual(category, 0)
        self.assertEqual(message, "报告判断错了")

    def test_valid_category_zero_with_empty_message(self):
        category, message = validate_annotation_fields("0", "")
        self.assertEqual(category, 0)
        self.assertEqual(message, "")

    def test_category_four_requires_message(self):
        with self.assertRaises(AnnotationError) as raised:
            validate_annotation_fields(4, " ")
        self.assertEqual(raised.exception.error, "message_required")

    def test_invalid_numeric_category(self):
        with self.assertRaises(AnnotationError) as raised:
            validate_annotation_fields(5, "x")
        self.assertEqual(raised.exception.error, "invalid_category")

    def test_invalid_text_category(self):
        with self.assertRaises(AnnotationError) as raised:
            validate_annotation_fields("abc", "x")
        self.assertEqual(raised.exception.error, "invalid_category")

    def test_message_too_long(self):
        with self.assertRaises(AnnotationError) as raised:
            validate_annotation_fields(0, "字" * 501)
        self.assertEqual(raised.exception.error, "message_too_long")

    def test_chinese_message_is_saved(self):
        annotation = receive_annotation(
            0,
            "本地接口测试",
            self.received_at,
            self.annotation_root,
            self.root,
        )
        path = self.annotation_root / "raw" / "2026-07-28" / (
            annotation["annotation_id"] + ".json"
        )
        saved = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(saved["message"], "本地接口测试")
        self.assertEqual(saved["category"], "wrong_behavior_judgment")

    def test_missing_related_report_still_saves(self):
        annotation = receive_annotation(
            0,
            "无报告也保存",
            self.received_at,
            self.annotation_root,
            self.root,
        )
        self.assertIsNone(annotation["primary_related_report"])
        self.assertTrue((self.annotation_root / "UNREVIEWED.md").exists())

    def test_related_report_uses_recent_existing_report(self):
        report_dir = self.root / "data" / "ai_reports" / "2026-07-28"
        report_dir.mkdir(parents=True)
        report = report_dir / "15-00.md"
        report.write_text("# report\n", encoding="utf-8")
        os.utime(report, (self.received_at.timestamp() - 120,) * 2)
        for directory in [
            "context_snapshots",
            "computer_facts",
            "phone_facts",
            "tablet_facts",
            "combined_facts",
            "semantic_timelines",
            "mixing_metrics",
        ]:
            path = self.root / "data" / directory / "2026-07-28" / "15-00.json"
            path.parent.mkdir(parents=True)
            path.write_text("{}", encoding="utf-8")
        related = find_primary_related_report(self.received_at, self.root)
        self.assertEqual(related, "data/ai_reports/2026-07-28/15-00.md")
        annotation = build_annotation(0, "关联测试", self.received_at, self.root)
        self.assertEqual(
            annotation["related_paths"]["phone_facts"],
            "data/phone_facts/2026-07-28/15-00.json",
        )

    def test_current_and_candidate_windows_are_recorded(self):
        annotation = build_annotation(0, "", self.received_at, self.root)
        self.assertEqual(
            annotation["current_half_hour_window"]["start"],
            "2026-07-28T15:30:00+08:00",
        )
        self.assertEqual(len(annotation["candidate_half_hour_windows"]), 2)
        self.assertEqual(
            annotation["candidate_half_hour_windows"][0]["start"],
            "2026-07-28T15:00:00+08:00",
        )

    def test_markdown_is_rebuilt_from_raw_json(self):
        first = receive_annotation(
            0,
            "第一条",
            self.received_at,
            self.annotation_root,
            self.root,
        )
        receive_annotation(
            1,
            "",
            datetime.fromisoformat("2026-07-28T15:45:00+08:00"),
            self.annotation_root,
            self.root,
        )
        daily = self.annotation_root / "daily" / "2026-07-28.md"
        daily.unlink()
        rebuild_markdown_summaries(self.annotation_root)
        text = daily.read_text(encoding="utf-8")
        self.assertIn(first["annotation_id"], text)
        self.assertIn("第一条", text)
        self.assertIn("未填写", text)

    def test_unreviewed_markdown_is_descending(self):
        first = receive_annotation(
            0,
            "早",
            self.received_at,
            self.annotation_root,
            self.root,
        )
        second = receive_annotation(
            1,
            "晚",
            datetime.fromisoformat("2026-07-28T15:45:00+08:00"),
            self.annotation_root,
            self.root,
        )
        text = (self.annotation_root / "UNREVIEWED.md").read_text(encoding="utf-8")
        self.assertLess(text.index(second["annotation_id"]), text.index(first["annotation_id"]))

    def test_two_submissions_generate_different_ids(self):
        first = receive_annotation(
            0,
            "",
            self.received_at,
            self.annotation_root,
            self.root,
        )
        second = receive_annotation(
            0,
            "",
            self.received_at,
            self.annotation_root,
            self.root,
        )
        self.assertNotEqual(first["annotation_id"], second["annotation_id"])


if __name__ == "__main__":
    unittest.main()
