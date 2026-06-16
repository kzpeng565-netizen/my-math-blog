---
name: example-expander
description: "Expand exactly one mathematical example from a user-given idea, tool, homework pattern, or existing example. Use when the user wants a single creative, high-distinctness example, counterexample, variant, or cross-domain analogue, with A/B/C exploration modes: A same knowledge point, B same knowledge area but different theorem/tool, C different knowledge area but same idea."
---

# Example Expander

Use this skill to construct exactly one mathematical example unless the user explicitly asks for more.

Default output is chat-only. Do not edit files unless the user explicitly says to write into a note/article.

Use `.codex/rubrics/example-expansion-rubric.md` for scoring. Follow `.codex/references/中文数学笔记格式.md` for note-ready Chinese Markdown.

## Exploration Type

Always label the example as one type:

- **A 类：同一个知识点的类似例子**
  - Same knowledge point.
  - Useful for variants, boundary cases, extreme cases, nonstandard objects, or examples that deepen one concept.
- **B 类：同一个知识范围内的类似例子，但不重复同一个定理/工具**
  - Same broad area, such as real analysis, topology, algebra, measure theory.
  - Must avoid reusing the existing example's core theorem/tool.
- **C 类：不同知识范围，但 idea 相同**
  - Cross-domain analogue.
  - Must explain the shared mechanism, not just a surface analogy.

If the user does not specify A/B/C, infer one type from the request and state why. Do not generate all three types unless the user asks.

## Required Input Extraction

Before constructing the example, extract:

```text
用户 idea：
已有例子画像：
- 对象：
- 使用工具：
- 暴露机制：
- 局限：
目标类型：A/B/C
```

If the existing example is not given, infer it from the current note or user text when available. If unavailable, say the distinctness score is provisional.

## Construction Output

Use this shape:

```text
例子类型：A/B/C
选择理由：

用户 idea：
已有例子画像：
- 对象：
- 使用工具：
- 暴露机制：
- 局限：

构造思路：
...

关键试错过程简述：
...

新例子：
- 对象：
- 使用工具：
- 与已有例子的区分点：
- 如何体现同一个 idea：

完整构造过程：
...

验证：
1. ...
2. ...

笔记价值：
...

评分：
- 贴合用户 idea：__/20
- 区分度：__/25
- 创造性：__/15
- 数学正确性与验证：__/20
- 构造过程透明度：__/15
- 笔记价值与表达：__/5
- 总分：__/100

是否达标：是/否
```

## Construction Rules

- Do not simply change symbols, names, or dimensions.
- For A 类, keep the same knowledge point but reveal a genuinely new side.
- For B 类, stay in the same broad area but avoid the same core theorem/tool.
- For C 类, move to a different broad area and explain the shared mechanism.
- Always verify hypotheses and conclusion.
- Mark uncertainty rather than presenting a shaky example as correct.
- Prefer examples that can become future blog/note material.

## Acceptance Rules

The final example must satisfy all gates:

- Total score at least 85.
- Fit to user idea at least 16/20.
- Distinctness at least 20/25.
- Creativity at least 10/15.
- Mathematical correctness at least 17/20.
- Construction transparency at least 12/15.

If distinctness is below 20, reconstruct the example instead of polishing it.

If mathematical correctness is below 17, rebuild or clearly mark it as an exploratory candidate, not a final example.

If construction transparency is below 12, add a better construction idea, reproducible process, and useful trial-and-error summary.

## Trial-And-Error Summary

Include a brief, useful exploration note, not a hidden chain of thought. It should explain:

- which obvious candidate was rejected,
- why it was too similar, too weak, or mathematically wrong,
- what change produced the final example.

Good style:

```text
一开始可以尝试把已有例子从 $\mathbb R$ 换到 $\mathbb R^2$，但这只是换空间，区分度太低。更好的方向是换工具：仍在实分析中，但从紧性转向一致连续性，这样保留“局部到整体”的 idea，同时避免重复使用同一个定理。
```

Bad style:

```text
我尝试了很多方法，最后找到了这个例子。
```

## File Editing

If the user says to write into a note/article, insert only the accepted final example at the relevant location using `local_patch`. Do not report after pure formatting changes; report briefly only if new mathematical content is inserted or uncertainty remains.
