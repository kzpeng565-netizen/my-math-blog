---
name: note-layout
description: Format mathematical Obsidian notes according to the user's Chinese note style. Use when the user asks for 笔记排版, note formatting, cleaning lecture notes, preserving original proofs and remarks, adding Obsidian callouts for important theorems, converting rough math notes into numbered headings, or making generated math explanations/examples match the user's note format.
---

# Note Layout

Use this skill to format the current note, selected text, or pasted content. Preserve the author's content, voice, proof ideas, comments, and remarks.

Default to returning formatted Markdown in chat. Edit a file only when the user explicitly asks to write the result into the note/article or to modify the current note.

## Core Reference

Read and follow `.codex/references/中文数学笔记格式.md`. It is the authoritative distilled format guide based on the user's original Copilot prompt `copilot/copilot-custom-prompts/笔记排版.md`.

If reading vault notes is allowed and a concrete example is needed, inspect `[[笔记实例——中文]]`, but follow the distilled guide over any obsolete formatting in the old example.

## Decision Procedure

1. Identify whether the input is:
   - a full note with sections,
   - a local passage,
   - a theorem/proof explanation,
   - examples/counterexamples,
   - rough AI-generated text.
2. Choose the smallest structure that fits:
   - Full note: use numbered headings, and default the first major section to `# 1. ...`.
   - Local passage: avoid unnecessary headings; use bold labels.
   - Important theorem: use `[!Note]` callout.
   - Definition/corollary/remark: use bold inline labels.
   - Proof explanation: prefer one compact `证明思路` / `证明过程` subsection with `**核心想法**` plus numbered steps; do not promote each proof step to its own heading.
   - Example/counterexample: use `**例子**`, `**验证**`, `**说明**` or `**反例**`, `**前提检查**`, `**结论失败**`.
3. Preserve original mathematical content. Only format, lightly organize, and mark likely corrections.

## Required Format Rules

- Every full-note/article layout starts numbering from `# 1. ...` by default, even when the original note has no explicit number.
- Major section: `# 1.xxx`
- Knowledge unit or important theorem: `## 1.1 xxx`
- Proof idea/process/discussion: `### 1.1.1 xxx` only when it is a whole local subsection under a theorem/knowledge unit.
- Do not split a continuous proof into many `###` headings such as “定义候选族 / 取上确界 / 用 MCT / 反证”. Keep these as numbered steps or bold labels inside one `证明过程` subsection.
- If a proof passage is short or conceptually one proof, collapse it to one heading such as `## 1.3 证明过程` or `### 1.2.1 证明过程`, then use `1. **步骤名**：...`.
- Do not use "例题", "例1", or "Example" as a heading.
- Important theorem:

```markdown
> [!Note] 标题
> 内容
```

- Definition/corollary:

```markdown
**定义**：...
**推论**：...
```

- Important terms: `**加粗内容**`.
- Inline math: `$...$`.
- Display math:

```markdown
$$
...
$$
```

- When a display formula appears near a numbered or bulleted list item, keep the `$$` lines at the beginning of the line with no leading spaces. Prefer prose plus an unindented display block over nested bullets containing indented `$$` blocks, because Obsidian/Markdown can misparse indented display math inside lists.
- In callouts, every formula line must begin with `>`.
- Do not use deprecated color-marker syntax.

## Preservation Rules

1. Keep the original proof content, viewpoint, and expression as much as possible.
2. Keep English text in English and Chinese text in Chinese; in mixed notes, mainly use Chinese.
3. Preserve `%%批注%%`, `*(批注)*`, existing **bold** text, and everything after **Remark**.
4. If a typo or likely mathematical input error is corrected, mark it with `*(修正说明)*`.
5. Do not add answers, extra explanations, or new claims unless the user asks.
6. Do not delete content merely because it is informal; format it first.
7. Local trimming and cleanup are allowed when they remove redundancy or formatting noise, but do not remove mathematical substance.
8. Do not rewrite the whole note unless the user explicitly asks for full reconstruction.

## Mini Example

Input:

```text
紧性 定理 如果X紧,Y hausdorff,f:X到Y连续双射,那么f是同胚. 证明思路 关键是证明闭映射.
```

Formatted output:

```markdown
## 紧空间到 Hausdorff 空间的连续双射

> [!Note] 定理
> 如果 $X$ 紧，$Y$ 是 Hausdorff 空间，$f:X\to Y$ 是连续双射，那么 $f$ 是同胚。

### 证明思路

**核心想法**：只需要证明 $f$ 是闭映射。紧集在连续映射下仍为紧集，而 Hausdorff 空间中的紧集是闭集。

1. **取闭集**：设 $A\subset X$ 是闭集。由于 $X$ 紧，$A$ 也是紧集。
2. **推出像为闭集**：连续性给出 $f(A)$ 紧；又因为 $Y$ 是 Hausdorff 空间，所以 $f(A)$ 闭。
3. **得到同胚**：因此 $f$ 是闭映射。连续双射若是闭映射，则反函数连续，所以 $f$ 是同胚。
```

## Output

If editing a file, use `local_patch` and do not report after formatting-only changes. If the user asks only for formatted output, return only the formatted Markdown unless a brief note is necessary.
