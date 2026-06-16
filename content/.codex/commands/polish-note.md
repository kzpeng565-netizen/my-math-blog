# polish-note

Use `$math-note-editor` and mode: `local_patch`.

Task:

Polish the requested section of a mathematical note. Preserve the structure, claims, examples, links, and notation unless explicitly asked otherwise.

Rules:

- Do not rewrite the whole note.
- Keep formulas in Obsidian-compatible LaTeX.
- Mark uncertain mathematical claims instead of silently strengthening them.
- After editing, score with `.codex/rubrics/math-note-rubric.md`.

Output an EditAudit after changes.
