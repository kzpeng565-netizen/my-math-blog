# Math Knowledge Base Collaboration Protocol

This vault is a mathematical knowledge base and blog workspace. Work conservatively, preserve the author's voice, and prefer small auditable edits over broad rewrites.

## Default Behavior

- Treat Markdown notes as user-owned source material, not disposable drafts.
- Default output is chat-only. If the user asks a question, requests an explanation, asks for examples, or does not explicitly say to write into a note/article, answer in the chat and do not edit files.
- If the user explicitly says to write into the article/note, add or patch the relevant location directly with the smallest useful edit.
- Default file-edit mode is `local_patch`: edit only the requested section or the smallest useful range.
- Do not delete definitions, theorems, proofs, examples, citations, wikilinks, callouts, block anchors, frontmatter, or media embeds unless the user explicitly asks.
- Do not produce an `EditPlan` for routine local additions, formatting, proof-explanation insertion, example insertion, typo fixes, or small polishing tasks.
- Produce an `EditPlan` only when the change is broad, structural, risky, ambiguous, or may delete/substantially rewrite existing content.
- If the request is exploratory, analytical, or broad, answer first and do not write files unless the user asks for edits.
- Unless the user explicitly asks for full reconstruction/rewrite, do not rewrite the whole note or article.
- Distinguish sources: current note, other vault notes, PDF sources, model knowledge, and web sources.
- For mathematical claims that are nontrivial, provide a verification sketch or mark uncertainty.
- For Chinese mathematical explanations, examples, counterexamples, or proof commentary, follow `.codex/references/中文数学笔记格式.md` when note-ready formatting is requested.

## Edit Modes

- `local_patch`: default. Fix or expand a local passage without changing the global structure.
- `structured_edit`: reorganize headings or section order. Requires an EditPlan first.
- `rewrite`: rewrite large portions only when explicitly requested.
- `read_only`: analyze, score, or plan without modifying files.

## Required Edit Audit

Do not report after pure formatting/layout changes. For formatting-only tasks, complete the change silently.

Report briefly only when the edit changes mathematical content, deletes content, restructures sections, uses a scoring loop, or introduces a mathematical risk:

- Files changed.
- Scope of edits.
- Content added.
- Content removed, if any.
- Mathematical risks or claims needing user review.
- Rubric score when a rubric was used.

## Quality Gate

When the user asks for automatic improvement, use the relevant rubric under `.codex/rubrics/` and iterate locally until the threshold is met or a blocker is identified. Never hide uncertainty by polishing prose.
