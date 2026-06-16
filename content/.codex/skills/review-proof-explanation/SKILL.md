---
name: review-proof-explanation
description: Generate, revise, score, and review theorem proof explanations using the detailed theorem-proof-explanation rubric. Use when the user asks to explain a theorem proof, improve a proof explanation, evaluate proof commentary, make a proof less flat, add proof strategy, or ensure the output reaches at least 85/100 before finalizing.
---

# Review Proof Explanation

Use `.codex/rubrics/theorem-proof-explanation-rubric.md`.

For note-ready Chinese output, follow `.codex/references/中文数学笔记格式.md`.

## Default Goal

Every final proof explanation must score at least 85/100 on the rubric. If a draft scores below 85, revise it before presenting it as final.

Default mode is read-only unless the user explicitly asks to edit a file.

## Generation Workflow

When asked to write or improve a proof explanation:

1. Identify the theorem, assumptions, conclusion, and main proof tool.
2. Write a short **核心想法** explaining the proof in one or two sentences.
3. Before writing details, write the mechanism skeleton:

```text
证明机制：
- 正向机制：
- 反向/唯一性机制：
- 关键桥梁：
- 读者应当带走的一句话：
```

4. Choose the natural proof blocks, such as:
   - 存在性 / 唯一性
   - 构造 / 验证 / 结论
   - 局部步骤 / 全局拼接
5. For each block, state its function before details.
6. For each technical construction, explain why it is introduced.
7. After drafting, score with the rubric, including the Insight Gate.
8. If total score is below 85 or the Insight Gate fails, revise the weakest categories and rescore.
9. Repeat until the score is at least 85 and the Insight Gate passes, or stop after three revision rounds and clearly mark the result as not yet accepted.

## Required Shape

Prefer this shape unless the user's requested format conflicts:

```markdown
**核心想法**：...

**证明机制**：
- **正向机制**：...
- **反向/唯一性机制**：...
- **关键桥梁**：...

1. **第一步关键词**：说明这一步的目标。
   ...

2. **第二步关键词**：说明这一步如何推进证明。
   ...

3. **最后一步关键词**：说明如何得到结论。
   ...
```

For proofs naturally split into two large parts, use:

```markdown
**Step 1：存在性**

**核心思路**：...

1. ...

**Step 2：唯一性**

**核心思路**：...

1. ...
```

Do not use decorative headings. Use headings only when they improve navigation.

## What To Fix When Output Is Flat

If the explanation sounds flat or like a standard answer, revise by adding:

- A sentence connecting the theorem to its main tool.
- The mechanism skeleton: 正向机制, 反向/唯一性机制, 关键桥梁.
- A task list for the proof block, such as “要验证三件事”.
- Short functional labels for steps.
- A highlighted key bridge, such as “最关键的一步是...”.
- A final sentence explaining the conceptual meaning of the theorem.

Do not make the prose flashy. Add navigation and motivation, not empty rhetoric.

## Scoring Output

When the user asks for review, output the full scoring table:

```text
Insight Gate：
- 为什么这个定理应该是真的：通过/不通过
- 关键转化是什么：通过/不通过
- 最难一步为什么成立：通过/不通过
- 封顶规则触发：无/说明

格式与排版：__/15
路线图与结构感：__/20
严谨性与依据：__/25
洞见、机制与构造动机：__/30
表达与读者体验：__/10
总分：__/100

最低分项：
- ...

必须修改：
1. ...
2. ...
3. ...
```

When the user asks for a final polished explanation, include only a short final quality line unless they request the full score:

```text
自检：已按证明解释评分器达到 __/100。
```

## Editing Files

If revising a note file, use `$math-note-editor` in `local_patch` mode by default. Revise only the proof explanation being reviewed, then rescore.
