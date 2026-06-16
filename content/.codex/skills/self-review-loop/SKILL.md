---
name: self-review-loop
description: Score drafts, edits, examples, counterexamples, and article structures against explicit rubrics, then revise iteratively until a threshold is met. Use when the user asks for automatic improvement, quality gates, self-scoring, iterative refinement, or "keep trying until good enough".
---

# Self Review Loop

Use a task-specific rubric from `.codex/rubrics/` when available. Otherwise use `.codex/rubrics/self-review-rubric.md`.

## Loop

1. Draft or inspect the current result.
2. Score each rubric dimension.
3. Identify the weakest one or two dimensions.
4. Revise only what addresses those weaknesses.
5. Rescore.
6. Stop when the threshold is met, after three iterations, or when more progress needs user input.
7. If a task-specific rubric requires a minimum score, do not present a below-threshold draft as final. Mark it as not yet accepted and explain what still blocks improvement.

## Output

```text
Rubric:
Iteration:
Scores:
Weakest dimensions:
Revision made:
Final score:
Remaining risks:
```

Do not use the loop to justify broad deletion. If the fix requires large structural changes, ask for approval first.
