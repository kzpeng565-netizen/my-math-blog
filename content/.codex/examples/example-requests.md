# Example Requests

## Query Existing Knowledge

```text
Search my vault for notes related to cellular homology and RP^n. Summarize only candidate note titles and relevant headings first; do not read full linked notes yet.
```

## Construct Examples

```text
Use $math-example-builder. For the section on compactness, give two examples: one metric-space example and one topological-space example. Verify each and score with the example rubric. Do not edit files.
```

## Construct Counterexamples

```text
Use $math-example-builder and $self-review-loop. Test the claim: every continuous bijection is a homeomorphism. Construct a counterexample suitable for a blog reader, verify it, and provide note-ready Markdown.
```

## Local Patch

```text
Use $math-note-editor in local_patch mode. In the current note, only revise the paragraph after the statement of the Radon-Nikodym theorem. Preserve the theorem statement and proof.
```

## Article Structure

```text
Use $math-article-structure. Review this article's structure and give a move map. Do not edit until I approve the outline.
```

## PDF Search

```text
Use $pdf-search. In the PDF at path/to/paper.pdf, search the body text for "spectral sequence" and return page numbers with context.
```
