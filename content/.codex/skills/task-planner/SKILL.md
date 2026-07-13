---
name: task-planner
description: "Plan a holiday or other unstructured period across study projects, life errands, tutoring, driving, appointments, and personal systems. Use when the user asks to organize a vacation, group a mixed Obsidian task collection into projects and categories, balance learning with personal responsibilities, or write executable Obsidian Tasks without excessive fragmentation or over-merging. Infer projects, build moderate-size execution bundles, validate daily capacity, write categorized Tasks, and preserve unresolved source items."
---

# Holiday Task Planner

Turn the user's holiday tasks into a categorized, capacity-safe plan. Analyze fine-grained actions internally, but output a compact set of coherent execution bundles. Do not invent goals, deadlines, appointments, availability, or confirmed outcomes.

Use `.codex/rubrics/task-planning-rubric.md` to score and revise the result before finalizing.

## Canonical Files

Read these files before planning:

- `非笔记内容/任务计划/假期任务管理readme.md`
- `非笔记内容/任务计划/ToDo-任务集合.md`
- `非笔记内容/任务计划/ToDo-已经规划好的任务.md`

For `$task-planner`, the holiday README takes precedence. Treat `任务管理readme.md` and links that request it as legacy semester instructions belonging to `$study-planner`; do not apply their course, examination, four-quadrant, or fixed-course-deadline rules.

Treat the collection as the source of tasks and the planned file as the source for duplicate detection. Read relevant holiday-plan, tutoring, reading, driving, appointment, or project wikilinks when needed. Use the current environment date.

Read `references/holiday-planning-rules.md` before classifying, grouping, estimating, or scheduling.

## Required Workflow

1. Read the canonical files and relevant wikilinks. Extract the holiday range, fixed commitments, stated capacity, priorities, and work-pattern preferences.
2. Split the collection into source units. Classify each unit as an executable action, project outcome, constraint/preference, or advice/reference. Only actions and project outcomes may produce Tasks lines.
3. Compare names, projects, wikilinks, dates, locations, and aliases with the planned file. Exclude duplicates.
4. Extract atomic actions for internal analysis. Record each action's project, completion condition, time evidence, date window, dependency, context/location, energy demand, and uncertainty. Do not emit Tasks yet.
5. Infer a small set of user-specific categories, then cluster actions into projects by shared outcome. Categories are display groups; projects drive aggregation. Do not create empty or purely template-driven categories.
6. Estimate atomic actions, then combine compatible actions into execution bundles using the reference rules. Prefer 2–6 🍅 per Tasks line, reconsider mergeable 1 🍅 lines, and split bundles above 8 🍅 unless they are indivisible fixed events.
7. Separate long outcomes into a few meaningful stages. For the next 1–7 days, schedule concrete bundles. For later weeks, prefer milestones in the plan note unless the user explicitly requests full-holiday Tasks.
8. Calculate daily capacity after fixed events, travel, waiting, preparation, and buffer. Use the fallback capacity from the holiday README only when the user supplies none. Sum planned tomatoes for every scheduled date and revise until no day exceeds capacity.
9. Assign dates and priorities. Respect dependencies and do not schedule a contingent follow-up as if an external result were guaranteed.
10. Run a granularity review: merge same-project, same-day short lines when compatible; split lines that combine dates, locations, dependencies, energy modes, or more than 8 🍅; remove any task derived only from advice or explanation.
11. Append one dated planning batch to `ToDo-已经规划好的任务.md`. Inside the batch, use dynamically numbered `## N. 类别名称` headings and place every Tasks line under exactly one category.
12. Append a concise plan note with capacity, deferred work, uncertainties, and at most three starting suggestions. Never overwrite or reorganize existing planned content.
13. Remove a source unit only when it was successfully written, its boundary is unambiguous, and removal preserves unresolved context. Remove a whole `---` block only when all its tasks were planned.
14. Report categorized Tasks written, aggregation decisions, daily capacity check, unresolved items, and removed source units.

## Link Handling

Resolve wikilinks by exact filename stem first, then choose the vault note matching the project context. Preserve identity-bearing wikilinks in the final task name. If a link is unavailable, keep that source item unresolved and state what is missing; continue with independent items.

## Dates and Priority

Use `⏳` for the actual scheduled day and `📅` only for a real or clearly stated due date. When no due date exists, omit `📅` rather than copying the scheduled date.

Use Obsidian Tasks priority semantics: `🔺` Highest, `⏫` High, `🔼` Medium, no symbol Normal, `🔽` Low, `⏬` Lowest. Do not call them Eisenhower quadrants.

## Output Format

Use a dated batch with inferred categories:

```markdown
# YYYY-MM-DD 假期任务规划

## 1. 类别名称

- [ ] #task 任务名 [🍅:: 0/预计番茄钟] 优先级 ⏳ YYYY-MM-DD 📅 YYYY-MM-DD

## 2. 类别名称

- [ ] #task 任务名 [🍅:: 0/预计番茄钟] ⏳ YYYY-MM-DD
```

Omit Normal priority and nonexistent due dates. Keep names compact; a parenthetical list of 2–4 tightly related deliverables is allowed when it makes a merged bundle verifiable. Use `[🍅:: ]` only when visible information cannot support a responsible estimate, and keep that source item unresolved.

## Final Response

Show the exact categorized Tasks written. Summarize why actions were merged or split, show each scheduled date's tomato total against capacity, list unresolved items, and state which source units were removed.
