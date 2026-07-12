---
name: task-planner
description: "Plan a holiday or other unstructured period across study projects, life errands, tutoring acquisition and delivery, driving practice, appointments, and fixed commitments. Use when the user asks to organize a vacation, create a weekly or daily plan, process an Obsidian task collection, balance learning with personal responsibilities, or write executable Obsidian Tasks. Read the user's task-management files, estimate total occupancy including travel and preparation, respect capacity and dependencies, write the plan, and safely preserve unresolved source items."
---

# Holiday Task Planner

Turn the user's own holiday tasks into a realistic layered plan. Plan study, life, and tutoring together instead of optimizing one category in isolation. Do not invent goals, reviews, habits, deadlines, or appointments that are absent from the source material.

Use `.codex/rubrics/task-planning-rubric.md` to check the result before finalizing.

## Canonical Files

Read these files before planning:

- `非笔记内容/任务计划/任务管理readme.md`
- `非笔记内容/任务计划/ToDo-任务集合.md`
- `非笔记内容/任务计划/ToDo-已经规划好的任务.md`

Treat the task collection as the source of tasks and the already-planned file as the source for duplicate detection. Also read any linked holiday plan, calendar, tutoring order, homework, reading, driving, or appointment note needed to understand a task.

Use the current environment date. Extract the holiday range, fixed commitments, weekly availability, stated priorities, and preferred work pattern from the files or current request. Do not assume semester course times or course-specific deadlines.

Read `references/holiday-planning-rules.md` before splitting, estimating, prioritizing, or scheduling tasks.

## Required Workflow

1. Read the canonical files and relevant wikilinks.
2. Split the collection by `---` when present. Within a large mixed block, recognize headings, numbered lists, checklists, dates, and paragraphs as possible source units; do not treat an entire multi-project block as one task.
3. Compare task name, project, wikilink, date, location, and obvious aliases with the already-planned file. Do not emit duplicates.
4. Normalize each new item into: task type, project, completion condition, visible scope, duration evidence, deadline, earliest start, fixed or flexible timing, dependencies, location/travel, energy demand, and uncertainty.
5. Separate outcomes from actions. Convert holiday outcomes into weekly milestones and near-term executable actions. Keep a user-supplied weekly structure unless it is impossible under current capacity.
6. Calculate capacity after fixed commitments, travel, basic recovery, and a 15–20% buffer. Never fill every available hour. If demand exceeds capacity, preserve hard commitments and core goals, defer lower-value work, and report the conflict.
7. Estimate full occupancy and priority using the reference rules. Include preparation, travel, waiting, delivery, and follow-up when they consume time.
8. Schedule the next 1–7 days concretely. For later weeks, prefer milestones and flexible weekly targets over invented daily precision. When the user explicitly requests a full-holiday plan, create dated weekly milestones plus only the necessary fixed events.
9. Write one Tasks line per independently executable action, fixed event, or meaningful milestone. Batch repetitive actions only when they share one completion condition and time window.
10. Append new Tasks lines and a concise plan note to `ToDo-已经规划好的任务.md`. Never delete, overwrite, or reorganize existing planned content.
11. Remove a source unit only when it was successfully written, its boundary is unambiguous, and removing it will not destroy context for unresolved items. Remove a whole `---` block only when every task in it was planned. Otherwise keep it and rely on duplicate detection in later runs.
12. Report written Tasks lines, capacity or conflict decisions, and every source item kept because it was unresolved or unsafe to remove.

## Link Handling

Resolve a wikilink by exact filename stem first, then choose the vault note whose path matches the task context. Preserve identity-bearing wikilinks in the final task name.

If a linked note is unavailable, do not invent its scope. Keep the source item and state which note or information is needed. A missing link does not prevent other independent tasks in the same block from being planned.

## Dates and Priority

Respect explicit deadlines and fixed dates. Use `⏳` for the scheduled day and `📅` only for a real or clearly stated due date. When no due date exists, schedule the task without `📅`; do not duplicate the scheduled date as a fake deadline.

Use Obsidian Tasks priority semantics: `🔺` Highest, `⏫` High, `🔼` Medium, no symbol Normal, `🔽` Low, `⏬` Lowest. Do not call these markers Eisenhower quadrants.

## Tasks Format

Use one of these valid shapes:

```markdown
- [ ] #task 任务名 [🍅:: 0/预计番茄钟] 优先级 ⏳ YYYY-MM-DD 📅 YYYY-MM-DD
- [ ] #task 任务名 [🍅:: 0/预计番茄钟] 优先级 ⏳ YYYY-MM-DD
```

Omit the priority marker when priority is Normal. Keep task names short, preserve useful wikilinks, and do not put estimates or long explanations in the name. Use `[🍅:: ]` only when visible information cannot support a responsible estimate, and keep that source item unresolved.

## Plan Note

After the appended Tasks lines, add a short plain-text note containing:

- the current planning horizon and main focus;
- the capacity or buffer assumption;
- at most three starting or batching suggestions;
- missing information and scheduling conflicts.

Keep this note operational. Do not turn it into a second, unrelated plan.

## Final Response

Show the exact Tasks lines written, summarize the key scheduling decisions, list unresolved items retained in the collection, and state which source blocks or units were removed.
