---
name: math-blog-writer
description: "Transform user-provided mathematical drafts, homework reflections, or note fragments into concise, faithful, insight-driven Chinese expository blog posts. Use when the user asks to write, polish, restructure, or convert math notes into blog form while preserving strict fidelity, avoiding invented content, avoiding rigid templates, and matching the user's existing math blog style."
---

# Math Blog Writer

Use this skill to turn mathematical drafts into blog-style Chinese Markdown with high insight density and low filler. Default output is chat-only unless the user explicitly says to write into a note/article.

Use `.codex/rubrics/math-blog-writing-rubric.md` for scoring. Follow `.codex/references/中文数学笔记格式.md` for Markdown and formula conventions when available.

## Style Anchors

When the user asks to match the vault style, read relevant passages from these reference notes if available:

- `分析/微分方程/波动方程的能量乘子法.md`
- `拓扑/不保持基点的同伦等价会有什么麻烦.md`
- `拓扑/形变收缩但不是强形变收缩的例子.md`

Extract their reusable style, not their mathematical content:

- Open with a sharp problem, contrast, or takeaway.
- Explain why a trick is natural before listing computations.
- Prefer "问题 -> 障碍 -> 破局点 -> 后果" or "例子 -> 麻烦 -> 机制 -> 启示" when the draft supports it.
- Keep paragraphs compact and mathematical.
- Use precise plain Chinese, not casual filler or forced analogies.
- Let reflection appear only when the draft already contains boundary, condition, or failure analysis.

## Fidelity Rules

- Use only material present in the user's draft, selected note, screenshots, or explicitly referenced sources.
- Do not add unmentioned theorems, counterexamples, applications, historical context, or textbook background.
- Do not invent intuition. If the draft has no analogy, write directly.
- If a derivation is long and the draft indicates it comes from handwriting or screenshots, summarize its purpose and use a placeholder such as `[此处插入草稿截图：能量估计推导]`.
- Mark missing or uncertain assumptions instead of silently repairing them.

## Workflow

1. Identify the source scope: current selection, current note, provided draft, or named notes.
2. Extract four items before writing:
   - 核心问题：the concrete question, obstruction, theorem, example, or confusion.
   - 破局点：the trick, construction, contrast, or viewpoint actually present in the draft.
   - 材料边界：what is allowed and what must not be invented.
   - 文章形状：the natural structure suggested by the material.
3. Choose a structure from the material. Do not force fixed modules such as `The Setup / Heuristic / The Key Trick / Deep Reflection`.
4. Write the blog draft in Chinese Markdown.
5. Score with `.codex/rubrics/math-blog-writing-rubric.md`.
6. If total score is below 85, or if any hard gate is triggered, revise before presenting the final answer.

## Structure Selection

Use one of these shapes only if it fits the draft:

- **Problem-driven**: problem -> naive route -> obstruction -> key idea -> result.
- **Method-driven**: tool -> why ordinary method is clumsy -> multiplier/construction/viewpoint -> reusable lesson.
- **Example-driven**: example -> what it breaks or reveals -> mechanism -> boundary.
- **Comparison-driven**: two notions or methods -> where they agree -> where they split -> lesson.
- **Proof-explanation**: theorem -> core idea -> proof skeleton -> where the proof really uses each condition.

Skip sections that the draft does not support. A short draft should become a short high-density article.

## Anti-Patterns

- Do not become a textbook summary.
- Do not expand "大白话" into vague motivational prose.
- Do not add decorative analogies such as "像..." unless the user supplied that analogy.
- Do not introduce a title hierarchy that makes the article look mechanically generated.
- Do not explain every algebraic line when the blog's value is the structural idea.
- Do not output a scoring report unless the user asks for scoring or review; use scoring internally otherwise.

## Output Rules

- If the user only asks for a blog draft, output the final Markdown article.
- If the user asks for a review, output the scoring report and concrete revision advice.
- If the user explicitly says to write into a note/article, apply the smallest local edit. Do not rewrite the whole note unless requested.
- Pure formatting edits do not need a report.
- For mathematical content insertion, briefly state what was inserted and any uncertainty.

## Minimal Example Prompt

```text
$math-blog-writer
请把这段草稿整理成一篇博客。不要补充我没写过的定理和例子，不要固定三段式；重点提炼核心问题、破局点和最后的数学启示。
```
