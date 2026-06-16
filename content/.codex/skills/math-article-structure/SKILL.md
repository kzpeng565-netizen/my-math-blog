---
name: math-article-structure
description: Diagnose and improve the structure of mathematical blog articles and long notes. Use when the user asks to reorganize sections, improve exposition flow, clarify the main thread, reorder definitions/examples/proofs, produce an outline, or make an article easier to read without losing mathematical content.
---

# Math Article Structure

First pass is read-only unless the user explicitly asks to edit.

## Structure Diagnosis

Return:

```text
Current main thread:
Reader prerequisites:
Where readers may get lost:
Dependency issues:
Proposed outline:
Move map:
Sections to preserve unchanged:
Sections needing local rewrite:
Rubric score:
```

## Editing Rules

- Use `structured_edit` only after approval.
- Move content before rewriting content.
- Preserve mathematical claims and proof substance.
- Keep examples near the concepts they illuminate.
- Use `.codex/rubrics/article-structure-rubric.md` for scoring.
