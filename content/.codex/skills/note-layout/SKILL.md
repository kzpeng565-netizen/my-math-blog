---
name: note-layout
description: Format mathematical Obsidian notes according to the user's existing note style. Use when the user asks for note formatting, note layout, cleaning up lecture notes, preserving original proofs and remarks, adding Obsidian callouts for important theorems, or converting rough math notes into the user's numbered heading style.
---

# Note Layout

Use this skill to format the current note, selected text, or pasted content. Preserve the author's content and voice.

## Reference Style

Use `.codex/references/中文数学笔记格式.md` as the distilled style guide. It is based on the user's original Copilot prompt `copilot/copilot-custom-prompts/笔记排版.md`. If more detail is needed and reading vault notes is allowed, use `[[笔记实例——中文]]` only as a concrete example.

## Heading Rules

If the content has sections:

- Use `# 1. Title` for the first major section.
- Use `## 1.1 Title` for important theorems or knowledge units under that section.
- Use `### 1.1.1 Title` for concrete proof ideas, proof processes, discussions, or local explanations.
- Do not use "例题", "例1", or similar example labels as any level of heading.

If the content has no clear sections:

- Use only a compact `##` heading that summarizes the knowledge point or content.

## Callouts And Emphasis

- Important theorems: use an Obsidian callout:

```markdown
> [!Note] Title
> theorem content
```

- Definitions and small corollaries: keep inline and emphasize labels such as **定义** and **推论**.
- Important terms: use **bold**.

## Preservation Rules

1. Format and organize the note, but preserve the original proof content, viewpoints, and expression as much as possible.
2. Read carefully and check likely typos or content errors from context. Mark your correction with italic parentheses, e.g. `*(changed from ...)*`.
3. If the original text is English, keep English. If the original text is Chinese, keep Chinese. In mixed notes, mainly use Chinese.
4. Preserve comments such as `%%comment%%`, `*(comment)*`, existing **bold** text, and everything after the author's **Remark** labels.
5. Do not add answers, extra explanations, or new claims unless the user asks.

## Output

If editing a file, use `local_patch` and report an EditAudit. If the user asks only for formatted output, return the formatted Markdown.
