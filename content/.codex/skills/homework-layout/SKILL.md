---
name: homework-layout
description: Format homework or exercise problem statements into the user's Obsidian homework layout. Use when the user asks to reformat exercises, problem sets, assignments, homework questions, or multiple subproblems without adding solutions.
---

# Homework Layout

Use this skill to format the current note, selected text, or pasted homework problems. Do not add answers.

## Reference Style

If available, imitate `[[作业排版例文]]`. Do not require it if unavailable.

## Layout Rules

- At the beginning, suggest a homework filename. It should summarize the concrete topic in no more than 10 Chinese characters.
- Use headings like `# 1. Summary Title` to split major groups. The title should summarize the knowledge point.
- If several consecutive problems share the same knowledge area, group them under one heading, but do not force a different problem order.
- Under each heading, use Obsidian callouts for each subproblem:

```markdown
> [!Note] 3-1
> problem text
```

or:

```markdown
> [!Note] Note 3-a
> problem text
```

- Keep the original problem numbers inside callout titles.
- Split every subproblem into its own callout.
- If there is a common stem before the first subproblem, merge that stem into the first subproblem callout.
- Do not add solutions.

## Formula Rule For Callouts

If a callout contains display math or multi-line formulas, every line must begin with `>`, including `$$` lines and each formula line:

```markdown
> $$
> formula line
> $$
```

## Preservation Rules

- Do not change problem order.
- Start `#` headings from 1.
- Preserve original problem numbering.
- Clean formatting, but do not change mathematical meaning.

## Output

Return formatted Markdown or patch only the requested file/selection.
