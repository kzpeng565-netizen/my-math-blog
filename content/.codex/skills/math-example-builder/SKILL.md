---
name: math-example-builder
description: Construct, test, and refine mathematical examples and counterexamples for notes and blog articles. Use when the user asks for examples, nonexamples, counterexamples, edge cases, motivating examples, exercises, sanity checks, or verification of whether an object satisfies hypotheses or refutes a claim.
---

# Math Example Builder

Build examples as mathematical objects plus verification, not as decorative prose.

## Example Output

```text
Concept:
Example:
Hypotheses check:
What it illustrates:
Minimality or naturalness:
Note-ready Markdown:
```

## Counterexample Output

```text
Claim being tested:
Counterexample:
Hypotheses check:
Conclusion failure:
Why this is natural:
Possible variants:
Note-ready Markdown:
```

## Quality Rules

- Verify every hypothesis and conclusion.
- Prefer simple examples first.
- If a claim is false only under missing hypotheses, state the missing hypothesis.
- For advanced claims, include a proof sketch or a source request.
- Use `.codex/rubrics/example-quality-rubric.md` when scoring or iterating.
