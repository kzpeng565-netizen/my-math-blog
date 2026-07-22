#!/usr/bin/env python3
"""Convert long runs of blank Markdown lines into printable spacing blocks."""

from __future__ import annotations

import argparse
import difflib
import shutil
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


EXCLUDED_DIRS = {
    ".git",
    ".obsidian",
    ".claude",
    ".claudian",
    ".trash",
    "node_modules",
    "public",
}
VALID_CLASSES = ("blank-s", "blank", "blank-l", "blank-xl")


@dataclass(frozen=True)
class Change:
    start_line: int
    blank_lines: int
    css_class: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Replace long runs of blank lines in Obsidian Markdown with "
            '<div class="blank..."></div>. Dry-run by default.'
        )
    )
    parser.add_argument("paths", nargs="+", help="Markdown files or directories")
    parser.add_argument("--write", action="store_true", help="write changes to disk")
    parser.add_argument("--diff", action="store_true", help="print unified diffs")
    parser.add_argument("--min-lines", type=int, default=3)
    parser.add_argument("--small-max", type=int, default=4)
    parser.add_argument("--medium-max", type=int, default=5)
    parser.add_argument("--large-max", type=int, default=7)
    parser.add_argument("--force-class", choices=VALID_CLASSES)
    parser.add_argument(
        "--backup-suffix",
        default="",
        help="optional backup suffix, for example .bak (only with --write)",
    )
    args = parser.parse_args()
    if args.min_lines < 2:
        parser.error("--min-lines must be at least 2")
    if not (args.small_max <= args.medium_max <= args.large_max):
        parser.error("thresholds must satisfy small-max <= medium-max <= large-max")
    return args


def collect_markdown_files(raw_paths: list[str]) -> list[Path]:
    found: set[Path] = set()
    for raw in raw_paths:
        path = Path(raw).expanduser().resolve()
        if not path.exists():
            raise FileNotFoundError(f"Path does not exist: {path}")
        if path.is_file():
            if path.suffix.lower() != ".md":
                raise ValueError(f"Not a Markdown file: {path}")
            found.add(path)
            continue
        for candidate in path.rglob("*.md"):
            relative_parts = candidate.relative_to(path).parts[:-1]
            if any(part in EXCLUDED_DIRS for part in relative_parts):
                continue
            found.add(candidate.resolve())
    return sorted(found, key=lambda item: str(item).casefold())


def protected_lines(lines: list[str]) -> list[bool]:
    """Mark regions where blank lines must remain untouched."""
    protected = [False] * len(lines)
    state: tuple[str, str | int] | None = None

    for index, line in enumerate(lines):
        stripped = line.strip()

        if state is not None:
            protected[index] = True
            kind, marker = state
            if kind == "frontmatter" and stripped in {"---", "..."}:
                state = None
            elif kind == "fence":
                char, length = str(marker)[0], int(str(marker)[1:])
                if stripped.startswith(char * length):
                    state = None
            elif kind == "math" and stripped == marker:
                state = None
            elif kind == "html" and f"</{marker}>" in stripped.lower():
                state = None
            elif kind == "comment" and "-->" in stripped:
                state = None
            continue

        if index == 0 and stripped == "---":
            protected[index] = True
            state = ("frontmatter", "---")
            continue

        if stripped.startswith("```") or stripped.startswith("~~~"):
            char = stripped[0]
            length = len(stripped) - len(stripped.lstrip(char))
            if length >= 3:
                protected[index] = True
                state = ("fence", f"{char}{length}")
                continue

        if stripped in {"$$", r"\["}:
            protected[index] = True
            state = ("math", "$$" if stripped == "$$" else r"\]")
            continue

        lowered = stripped.lower()
        if "<!--" in stripped:
            protected[index] = True
            if "-->" not in stripped[stripped.find("<!--") + 4 :]:
                state = ("comment", "-->")
            continue

        for tag in ("pre", "script", "style"):
            if f"<{tag}" in lowered:
                protected[index] = True
                if f"</{tag}>" not in lowered:
                    state = ("html", tag)
                break

    return protected


def choose_class(count: int, args: argparse.Namespace) -> str:
    if args.force_class:
        return args.force_class
    if count <= args.small_max:
        return "blank-s"
    if count <= args.medium_max:
        return "blank"
    if count <= args.large_max:
        return "blank-l"
    return "blank-xl"


def convert_text(text: str, args: argparse.Namespace) -> tuple[str, list[Change]]:
    newline = "\r\n" if "\r\n" in text else "\n"
    had_final_newline = text.endswith(("\n", "\r"))
    lines = text.splitlines()
    protected = protected_lines(lines)
    output: list[str] = []
    changes: list[Change] = []
    index = 0

    while index < len(lines):
        if lines[index].strip() or protected[index]:
            output.append(lines[index])
            index += 1
            continue

        end = index
        while end < len(lines) and not lines[end].strip() and not protected[end]:
            end += 1
        count = end - index

        # Leading/trailing whitespace is formatting cleanup, not an answer area.
        if index == 0 or end == len(lines) or count < args.min_lines:
            output.extend(lines[index:end])
            index = end
            continue

        css_class = choose_class(count, args)
        output.extend(["", f'<div class="{css_class}"></div>', ""])
        changes.append(Change(index + 1, count, css_class))
        index = end

    converted = newline.join(output)
    if had_final_newline:
        converted += newline
    return converted, changes


def read_utf8(path: Path) -> tuple[str, bool]:
    raw = path.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    return raw.decode("utf-8-sig"), has_bom


def write_utf8(path: Path, text: str, has_bom: bool) -> None:
    encoding = "utf-8-sig" if has_bom else "utf-8"
    path.write_text(text, encoding=encoding, newline="")


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(Path.cwd().resolve()))
    except ValueError:
        return str(path)


def main() -> int:
    args = parse_args()
    try:
        files = collect_markdown_files(args.paths)
    except (FileNotFoundError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2

    total_regions = 0
    total_lines = 0
    changed_files = 0
    class_counts: Counter[str] = Counter()

    for path in files:
        try:
            original, has_bom = read_utf8(path)
        except UnicodeDecodeError:
            print(f"SKIP non-UTF-8: {display_path(path)}", file=sys.stderr)
            continue
        converted, changes = convert_text(original, args)
        if not changes:
            continue

        changed_files += 1
        total_regions += len(changes)
        total_lines += sum(change.blank_lines for change in changes)
        class_counts.update(change.css_class for change in changes)
        detail = ", ".join(f"{name}={class_counts_for_file(changes, name)}" for name in VALID_CLASSES if class_counts_for_file(changes, name))
        print(f"{'WRITE' if args.write else 'DRY-RUN'} {display_path(path)}: {len(changes)} 个区域 ({detail})")

        if args.diff:
            diff = difflib.unified_diff(
                original.splitlines(keepends=True),
                converted.splitlines(keepends=True),
                fromfile=f"a/{display_path(path)}",
                tofile=f"b/{display_path(path)}",
            )
            sys.stdout.writelines(diff)
            if original and not original.endswith("\n"):
                print()

        if args.write:
            if args.backup_suffix:
                backup = path.with_name(path.name + args.backup_suffix)
                if backup.exists():
                    print(f"ERROR: backup already exists: {backup}", file=sys.stderr)
                    return 3
                shutil.copy2(path, backup)
            write_utf8(path, converted, has_bom)

    mode = "已写入" if args.write else "预览"
    counts = ", ".join(f"{name}={class_counts[name]}" for name in VALID_CLASSES if class_counts[name]) or "无"
    print(
        f"{mode}完成：扫描 {len(files)} 个 Markdown 文件；"
        f"{changed_files} 个文件、{total_regions} 个留白区域、{total_lines} 个原空白行；{counts}。"
    )
    if not args.write and total_regions:
        print("未修改任何文件。确认结果后加 --write。")
    return 0


def class_counts_for_file(changes: list[Change], name: str) -> int:
    return sum(change.css_class == name for change in changes)


if __name__ == "__main__":
    raise SystemExit(main())
