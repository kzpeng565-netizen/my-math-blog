---
name: pdf-search
description: Search PDF body text with page numbers using pdftotext. Use when the user asks to find words, phrases, definitions, theorems, formulas, citations, or other content inside .pdf files in the Obsidian vault or local workspace.
---

# PDF Search

Use this skill for PDF body-text search. Prefer the bundled script, which calls `pdftotext` and preserves page breaks.

```powershell
python ".codex\skills\pdf-search\scripts\search_pdf_text.py" "path\to\file.pdf" "search phrase"
```

Common examples:

```powershell
python ".codex\skills\pdf-search\scripts\search_pdf_text.py" "paper.pdf" "Sylow"
python ".codex\skills\pdf-search\scripts\search_pdf_text.py" "paper.pdf" "Radon-Nikodym" --context 200
python ".codex\skills\pdf-search\scripts\search_pdf_text.py" "paper.pdf" "E_2" --regex
```

Report filename, page number, matched text, and short context. If little or no text is extracted, say the PDF is probably scanned/image-only and needs OCR.
