---
name: ai-content-format-cleanup
description: Clean up AI-generated mathematical or explanatory content for compact Obsidian notes. Use when the user asks to整理AI内容, remove excessive headings, convert LaTeX delimiters, tighten prose, or make AI text match the user's concise note style.
---

# AI Content Format Cleanup

Use this skill for selected text, pasted content, or a requested note section.

## Rules

1. Wrap inline LaTeX with `$...$` and display LaTeX with `$$...$$`; replace `\(...\)` and `\[...\]`.
2. Remove all unnecessary headings. Use **bold** for emphasis instead of headings unless the user asks for a full note structure.
3. Delete extra blank lines. In Obsidian, display formulas do not need extra blank lines before or after nearby prose.
4. Make the content more concise, but do not change the main meaning.
5. Preserve mathematical correctness and mark uncertainty instead of smoothing over gaps.

## Output

Return cleaned Markdown. If editing a file, use `local_patch` and only touch the requested content.
