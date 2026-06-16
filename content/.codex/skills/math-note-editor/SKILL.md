---
name: math-note-editor
description: Edit mathematical Obsidian notes with narrow, auditable changes. Use when the user asks to revise, polish, reorganize, expand, or clean up math notes, proofs, definitions, examples, theorem statements, or blog-note passages while preserving existing content and avoiding broad deletion.
---

# Math Note Editor

Default to chat-only unless the user explicitly asks to write into a note/article. Preserve the user's note unless a broader mode is explicit.

## Edit Protocol

Use these defaults:

- If the user asks for an explanation, example, counterexample, review, or polished paragraph without saying to write it into a file, output in chat only.
- If the user says "写进文章", "放到当前笔记", "插入到这里", "修改这一段", or similar, directly apply a `local_patch` at the relevant location.
- Do not ask for approval or produce an EditPlan for routine local additions, formatting, proof explanations, example insertions, typo fixes, or small polishing tasks.
- Produce an EditPlan only for broad restructuring, uncertain placement, risky mathematical changes, or deletion/substantial rewrite.

For broad/risky changes, produce:

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
- Some local deletion, compression, or replacement is allowed when the user asks to simplify, polish, or clean up, but it must stay within the requested scope and preserve mathematical meaning.
- Do not rewrite the whole note or article unless the user explicitly asks for full rewrite/reconstruction.
- Keep local voice and notation.
- Keep Obsidian math format: inline `$...$`, display `$$...$$`.
- Mark uncertain claims instead of silently strengthening them.

## Audit

Do not report after pure formatting/layout changes.

After mathematical content changes, deletion, restructuring, scoring loops, or risky edits, report:

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
