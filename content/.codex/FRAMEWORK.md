# Math Knowledge Base AI Framework

This framework is a starting point for using Codex through Claudian as a mathematical collaborator.

## Layers

1. `AGENTS.md`: global behavior rules for the vault.
2. `skills/`: reusable workflows that Codex can invoke.
3. `rubrics/`: scoring standards for self-review and iteration.
4. `commands/`: reusable prompt templates for common tasks.
5. `examples/`: concrete demonstrations of how to ask.

## Core Workflows

- Search and synthesize: find relevant notes or PDFs, separate sources, then answer.
- Local edit: patch the requested range directly when the user explicitly asks to write into the note/article. Do not report pure formatting changes. Produce a brief EditAudit only for mathematical content changes, deletion, restructuring, scoring loops, or risk. Use an EditPlan only for broad, structural, risky, or ambiguous changes.
- Example construction: propose examples or counterexamples, verify hypotheses and conclusions, then provide a note-ready version.
- Article restructuring: diagnose the reading path, propose a new outline, then edit only after approval.
- Self-review loop: draft, score, revise weakest dimensions, stop at threshold.

## Recommended Operating Rules

- For questions, explanations, and examples, output in chat by default unless the user explicitly asks to write into a file.
- Use `local_patch` for normal note edits.
- Use `structured_edit` only after approving an outline.
- Use rubrics for generated examples, counterexamples, article structure, and final blog polish.
- Keep generated mathematical claims traceable to a verification or source.

## Minimal Example

User:

```text
Use $math-example-builder and $self-review-loop. For my current note on compactness, construct two examples and one counterexample. Score them with the example rubric. Do not edit files yet.
```

Expected AI behavior:

1. Identify the local mathematical goal.
2. Propose examples.
3. Verify each example.
4. Score against `.codex/rubrics/example-quality-rubric.md`.
5. Revise weak examples.
6. Return note-ready Markdown.
