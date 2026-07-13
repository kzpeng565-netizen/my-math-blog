# Holiday Planning Rules

Use these rules to classify source material, infer projects, build execution bundles, estimate time, and validate the schedule.

## Source Classification

Classify every source unit before generating Tasks:

- **Action**: directly executable and verifiable.
- **Project outcome**: requires multiple stages or sessions.
- **Constraint/preference**: controls scheduling but is not itself a task.
- **Advice/reference**: examples, scripts, criteria, explanations, or methods used to perform a task.

Do not convert each numbered sentence, suggestion, screening rule, or learning question into a task. A long block may contain all four classes.

## Project and Category Inference

Infer a project from shared outcome, not merely shared nouns. For example, resume preparation, outreach, follow-up, and order comparison belong to the broader tutoring-acquisition project but may be different execution stages.

Infer categories after projects are known. Use short user-facing names such as tutoring, mathematics study, driving, life/errands, or personal systems only when the input supports them. Order categories by current priority, fixed dates, and dependency pressure. Emit only non-empty categories.

## Controlled Aggregation

Extract and estimate atomic actions internally. Turn compatible atoms into one execution bundle when they share:

- one project and execution stage;
- one day or scheduling window;
- one location, tool set, or work context;
- one combined completion condition;
- no external wait or decision boundary between them.

Prefer bundles of 2–6 🍅. Permit up to 8 🍅 when the bundle is coherent and fits the verified day. A single 1 🍅 task is allowed only for an independent fixed event, a blocking confirmation, or a short action that cannot share context with another task.

Split a bundle when dates, locations, energy modes, outputs, or dependencies differ; when an external reply can change the next action; when the name needs a long list to define completion; or when the total exceeds 8 🍅. Split large work into a few stages, not into one line per tomato.

Use this review after drafting:

```text
same project + same day + same context + no wait boundary + combined <= 8 🍅
=> merge unless separate tracking has clear value

different day/location/output/dependency/energy mode OR combined > 8 🍅
=> split
```

Do not merge unrelated errands merely to reach 2 🍅. Do not merge an entire week of reading and writing into one scheduled-day task.

## Task Types

### Study projects

Separate reading/comprehension, exercises, notes, writing, revision, and mentor communication when they need different dates or produce independent outputs. A broad goal such as finishing four chapters is a project. Near-term work becomes 2–6 🍅 bundles; later work remains a milestone until its week approaches unless full-holiday Tasks are explicitly requested.

### Life and driving

Include preparation, round-trip travel, waiting, and the errand. Combine online errands when they share context; combine physical errands only when they share a realistic route. Treat arranging an appointment as a separate blocker when the actual event is not confirmed.

### Tutoring acquisition

Typical stages are materials, batch outreach, lead follow-up, trial lesson, comparison, and acceptance. Merge resume, proof materials, and a tracking sheet when prepared in one work block. Keep outreach separate from later follow-up when replies are required. Do not create teaching sessions before an order and time are confirmed.

When data exists, use:

```text
真实时薪 = 扣除信息费后的总收入 /（授课 + 通勤 + 等待 + 必要备课）
```

### Tutoring delivery

Account for preparation, travel, teaching, and follow-up. Merge them only when they form one compact session and share a date; otherwise keep the stages separate.

## Estimation

Use `1 🍅 = 40 minutes`. Estimate atomic actions before aggregation and sum them without adding arbitrary coordination time.

For mathematics exercises, classify each visible problem or `[!Note]` block:

- 20 minutes: direct definition/theorem use, short calculation, or one simple conclusion.
- 40 minutes: routine proof/application requiring several steps or 1–2 central results.
- 60 minutes: nonstandard construction/proof, long calculation, or at least three substantial subquestions.

Calculate `ceil(total minutes / 40)`. Do not infer difficulty from an advanced theorem name alone.

For reading and writing, estimate from visible scope, proof density, and required output. Fallback anchors are: bounded skim 1–2 🍅; dense concept/proof unit 2–4 🍅; structured notes 1–3 🍅; blog outline 1 🍅; draft 3–5 🍅; revision 1–2 🍅.

For errands and tutoring, estimate total occupied time. If missing travel, scope, waiting, or appointment information materially changes the result, use `[🍅:: ]` and keep the item unresolved instead of inventing precision.

## Capacity and Energy

Use stated capacity first. Otherwise use the holiday README fallback of at most 6 planned tomatoes per day. Only raise this to at most 8 when the user identifies a high-intensity day or a schedule that clearly supports it.

Subtract fixed events, travel, waiting, and preparation before allocating flexible work. Preserve 15–20% unallocated time when capacity is stated as clock hours rather than already-buffered tomatoes.

Place mathematics, proof reading, and substantive writing in high-energy blocks. Place outreach, formatting, online errands, and follow-up in lower-energy blocks. On travel- or tutoring-heavy days, schedule only light study unless capacity explicitly supports more.

After drafting, build a per-date table:

```text
date | planned tomatoes | available tomatoes | pass/fail
```

Revise every failed date before writing. An unknown-duration task prevents claiming that date is capacity-safe; either obtain the estimate, schedule it alone with caution, or keep it unresolved.

## Priority and Conflict Resolution

Determine priority from hard deadlines, blocking dependencies, contribution to stated goals, closing opportunity windows, consequence, batching value, and recovery cost.

- `🔺`: immediate hard commitment or critical blocker.
- `⏫`: due soon, high consequence, or central milestone at risk.
- `🔼`: meaningful progress toward a core goal without immediate pressure.
- no symbol: ordinary current-horizon task.
- `🔽`: useful but safely deferrable.
- `⏬`: optional and first to yield under overload.

When demand exceeds capacity: preserve fixed events and hard deadlines; then prerequisites and the primary goal; reduce secondary scope; defer optional work; expose any remaining tradeoff. Never double-book location-bound work or assume an unconfirmed external outcome.
