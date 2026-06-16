# Math Knowledge Base Collaboration Protocol

This vault is a mathematical knowledge base and blog workspace. Work conservatively, preserve the author's voice, and prefer small auditable edits over broad rewrites.

## Default Behavior

- Treat Markdown notes as user-owned source material, not disposable drafts.
- Default to `local_patch`: edit only the requested section or the smallest useful range.
- Do not delete definitions, theorems, proofs, examples, citations, wikilinks, callouts, block anchors, frontmatter, or media embeds unless the user explicitly asks.
- Before non-mechanical changes, produce an `EditPlan` with scope, intended additions, intended removals, risks, and whether user approval is needed.
- If the request is exploratory, analytical, or broad, answer first and do not write files unless the user asks for edits.
- Distinguish sources: current note, other vault notes, PDF sources, model knowledge, and web sources.
- For mathematical claims that are nontrivial, provide a verification sketch or mark uncertainty.
- For Chinese mathematical explanations, examples, counterexamples, or proof commentary, follow `.codex/references/中文数学笔记格式.md` when note-ready formatting is requested.

## Edit Modes

- `local_patch`: default. Fix or expand a local passage without changing the global structure.
- `structured_edit`: reorganize headings or section order. Requires an EditPlan first.
- `rewrite`: rewrite large portions only when explicitly requested.
- `read_only`: analyze, score, or plan without modifying files.

## Required Edit Audit

After editing, report:

- Files changed.
- Scope of edits.
- Content preserved.
- Content added.
- Content removed, if any.
- Mathematical risks or claims needing user review.
- Rubric score when a rubric was used.

## Quality Gate

When the user asks for automatic improvement, use the relevant rubric under `.codex/rubrics/` and iterate locally until the threshold is met or a blocker is identified. Never hide uncertainty by polishing prose.
