---
name: review-proof-explanation
description: Score and review explanations of theorem proofs using the theorem-proof-explanation rubric. Use when the user asks to evaluate, grade, review, improve, or revise a proof explanation for formatting, rigor, justification, core idea, construction motivation, and global proof strategy.
---

# Review Proof Explanation

Use `.codex/rubrics/theorem-proof-explanation-rubric.md`.

Default mode: read-only. Do not edit files unless the user explicitly asks for revision.

For note-ready Chinese proof explanations, follow `.codex/references/中文数学笔记格式.md`.

## Review Output

```text
Format And Readability: __/30
Rigor And Justification: __/40
Essence And Proof Strategy: __/30
Total: __/100

Strong points:
- ...

Weak points:
- ...

Required revisions:
1. ...
2. ...
3. ...
```

## Revision Rule

If the user asks to revise after scoring, use `$math-note-editor` in `local_patch` mode by default. Revise only the proof explanation being reviewed, then rescore with the same rubric.
