# Theorem Proof Explanation Rubric

Use this rubric when evaluating an explanation of a theorem proof, especially for blog notes, study notes, or AI-generated proof commentary.

Threshold: 88/100. If rigor is below 30/40, revise before accepting. If essence is below 22/30, the explanation may be correct but not useful enough.

## 1. Format And Readability: 30

- No unnecessary headings: 5
  - Do not use section titles when the proof can be explained directly.
  - Prefer compact prose, bold emphasis, numbered steps, and bullet points.
- Structured but not bloated: 6
  - Use **bold key phrases**, `1. 2. 3.` numbering, and bullet points where they help scanning.
  - Avoid decorative structure and long preambles.
- Correct math formatting: 6
  - Inline formulas use `$...$`.
  - Display formulas use `$$...$$`.
  - Do not leave raw TeX outside math delimiters.
- Compact display math: 4
  - Do not insert extra blank lines between adjacent display formulas.
  - Keep related equations visually close.
- Step markers: 5
  - Each proof step should have a simple transition such as "First", "Next", "Finally", "Step 1", or a short equivalent.
  - The reader should always know what the current step is doing.
- Overall density: 4
  - The explanation is compact enough to read smoothly.
  - No repeated filler such as "it is obvious", "clearly", or empty motivational sentences.

## 2. Rigor And Justification: 40

- Logical order: 10
  - Assumptions, definitions, constructions, and conclusions appear in a coherent order.
  - No conclusion is used before it is proved or introduced.
- Justified claims: 12
  - Important claims have a reason: a definition, theorem, computation, diagram, or previously established fact.
  - Nontrivial implications are not skipped.
- Hypotheses are used correctly: 7
  - The explanation identifies where key hypotheses enter.
  - It does not silently strengthen or weaken the theorem.
- No inflated language: 4
  - Avoid grand, vague, or overconfident wording.
  - Prefer precise statements over rhetorical flourish.
- Error and uncertainty handling: 7
  - If a step is subtle, say why it is subtle.
  - If a proof gap remains, mark it explicitly instead of hiding it with polished prose.

## 3. Essence And Proof Strategy: 30

- Core idea summary: 8
  - The explanation includes one or two sentences stating the central idea of the proof.
  - This summary should appear before or near the beginning of the detailed proof.
- Construction motivation: 8
  - For complicated objects, maps, sequences, covers, filtrations, diagrams, or reductions, explain why they are introduced.
  - The reader should see the logic behind the construction, not only the construction itself.
- Global proof thread: 8
  - The steps are connected by a clear strategy.
  - The explanation does not feel like a list of isolated algebraic or logical moves.
- Local-to-global clarity: 3
  - Each technical step is tied back to the goal of the proof.
- Reusable insight: 3
  - The explanation helps the reader recognize the method in similar proofs.

## Required Review Output

When scoring, use this format:

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

## Revision Rule

Revise the proof explanation if:

- Total score is below 88.
- Rigor And Justification is below 30.
- Essence And Proof Strategy is below 22.
- The proof has no explicit core idea summary.
- The proof contains formulas not wrapped in `$...$` or `$$...$$`.
