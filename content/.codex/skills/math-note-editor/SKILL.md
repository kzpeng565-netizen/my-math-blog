---
name: math-note-editor
description: Edit mathematical Obsidian notes with narrow, auditable changes. Use when the user asks to revise, polish, reorganize, expand, or clean up math notes, proofs, definitions, examples, theorem statements, or blog-note passages while preserving existing content and avoiding broad deletion.
---

# Math Note Editor

Default to `local_patch`. Preserve the user's note unless a broader mode is explicit.

## Edit Protocol

Before non-mechanical edits, produce:

```text
EditPlan:
- Mode:
- Target file/section:
- Preserve:
- Add:
- Remove:
- Mathematical risks:
- Need approval:
```

Only edit after approval when the change is broad, structural, or uncertain.

## Preservation Rules

- Do not delete definitions, theorems, proofs, examples, citations, wikilinks, callouts, block anchors, media embeds, or frontmatter unless explicitly requested.
- Keep local voice and notation.
- Keep Obsidian math format: inline `$...$`, display `$$...$$`.
- Mark uncertain claims instead of silently strengthening them.

## Audit

After edits, report:

```text
EditAudit:
- Files changed:
- Scope:
- Preserved:
- Added:
- Removed:
- Rubric score:
- Risks:
```

Use `.codex/rubrics/math-note-rubric.md` when scoring is requested or the edit is substantial.
