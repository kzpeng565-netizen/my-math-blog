---
name: self-review-loop
description: "Score a draft, note, proof explanation, example, or generated content against a specified rubric, identify the lowest-scoring items, and iteratively revise locally until the acceptance threshold is met. Use when the user asks for self-review, scoring, rubric-based iteration, or improving AI output until it reaches a required score."
---

# Self Review Loop

Use this skill to evaluate content with a rubric and revise only the parts needed to pass.

Default output is chat-only unless the user explicitly asks to write into a note or article.

## Workflow

1. Identify the target content and the rubric.
2. Score each rubric item honestly.
3. Apply hard caps or rejection rules from the rubric.
4. If the score passes, output the final content or a short review.
5. If the score does not pass, revise the lowest-scoring part first.
6. Repeat scoring after revision until the content passes or a real blocker remains.

## Rules

- Do not rewrite the whole text when a local revision can fix the problem.
- Do not hide uncertainty. If math correctness is unclear, mark it instead of forcing a high score.
- Do not output a long scoring report unless the user asks for review or scoring details.
- If editing a file, preserve the surrounding note structure and only patch the relevant section.

## Minimal Output

When the user asks for scoring:

```text
总分：__/100
是否达标：是/否
最低分项：
必须修改：
1. ...
2. ...
```
