# review-proof-explanation

Use `$self-review-loop`.

Task:

Review an explanation of a theorem proof using `.codex/rubrics/theorem-proof-explanation-rubric.md`.

Focus:

- Formatting: no unnecessary headings, compact layout, `$...$` and `$$...$$`, no extra blank lines between display formulas.
- Rigor: clear logic, justified claims, no inflated language.
- Essence: one or two sentence core idea, motivation for complex constructions, and a global proof thread.

Output:

```text
Format And Readability: __/30
Rigor And Justification: __/40
Essence And Proof Strategy: __/30
Total: __/100

Strong points:
- ...

Weak points:
- ...

Required revisions:
1. ...
2. ...
3. ...
```

Do not edit files unless the user asks for revision. If asked to revise, use `local_patch` unless the user explicitly requests a rewrite.
