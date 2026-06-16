#!/usr/bin/env python
"""Search searchable PDF body text page by page using pdftotext."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def extract_pages(pdf_path: Path) -> list[str]:
    exe = shutil.which("pdftotext")
    if not exe:
        raise RuntimeError("pdftotext was not found on PATH. Install Poppler or TeX Live's pdftotext.")

    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "text.txt"
        result = subprocess.run(
            [exe, "-layout", "-enc", "UTF-8", str(pdf_path), str(out)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or "pdftotext failed")
        text = out.read_text(encoding="utf-8", errors="replace")

    pages = text.split("\f")
    if pages and not pages[-1].strip():
        pages.pop()
    return pages


def compact(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Search PDF body text with page-aware context.")
    parser.add_argument("pdf", type=Path)
    parser.add_argument("query")
    parser.add_argument("--context", type=int, default=140)
    parser.add_argument("--max", type=int, default=50)
    parser.add_argument("--case-sensitive", action="store_true")
    parser.add_argument("--regex", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    pdf = args.pdf.expanduser().resolve()
    if not pdf.exists() or pdf.suffix.lower() != ".pdf":
        print(f"PDF not found or not a .pdf file: {pdf}", file=sys.stderr)
        return 2

    try:
        pages = extract_pages(pdf)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1

    flags = 0 if args.case_sensitive else re.IGNORECASE
    pattern = re.compile(args.query if args.regex else re.escape(args.query), flags)
    matches = []

    for page_no, page_text in enumerate(pages, start=1):
        text = compact(page_text)
        for match in pattern.finditer(text):
            start = max(0, match.start() - args.context)
            end = min(len(text), match.end() + args.context)
            matches.append(
                {
                    "page": page_no,
                    "match": match.group(0),
                    "context": ("..." if start else "") + text[start:end] + ("..." if end < len(text) else ""),
                }
            )
            if len(matches) >= args.max:
                break
        if len(matches) >= args.max:
            break

    extracted_chars = sum(len(p.strip()) for p in pages)
    output = {
        "pdf": str(pdf),
        "query": args.query,
        "extractor": "pdftotext",
        "page_count": len(pages),
        "extracted_chars": extracted_chars,
        "possible_scanned_pdf": extracted_chars < max(200, len(pages) * 20),
        "match_count": len(matches),
        "matches": matches,
    }

    if args.json:
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return 0

    print(f"PDF: {pdf}")
    print(f"Pages: {len(pages)}; extracted chars: {extracted_chars}")
    if output["possible_scanned_pdf"]:
        print("Warning: little text was extracted; this PDF may be scanned/image-only and need OCR.")
    if not matches:
        print("No matches found in extracted body text.")
    for item in matches:
        print(f"\nPage {item['page']}: {item['match']}")
        print(item["context"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
