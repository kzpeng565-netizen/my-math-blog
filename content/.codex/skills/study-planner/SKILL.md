---
name: study-planner
description: "Plan semester coursework and homework from the user's Obsidian task collection into executable Obsidian Tasks entries. Use when the user asks to schedule course assignments, inspect linked homework notes, estimate mathematics exercises with 20/40/60-minute tiers, or write an academic study plan during teaching weeks. Read the task-management files, avoid duplicates, preserve assignment wikilinks, write planned entries, and remove only successfully planned archived task blocks."
---

# Study Planner

Use this skill to turn the user's own items in `ToDo-任务集合.md` into planned Obsidian Tasks entries. Do not invent review tasks or add extra study plans that are not listed in the task collection.

Use `.codex/rubrics/study-planning-rubric.md` to check the result before finalizing.

## Canonical Files

Read these files before planning:

- `非笔记内容/任务计划/任务管理readme.md`
- `非笔记内容/任务计划/ToDo-任务集合.md`
- `非笔记内容/任务计划/ToDo-已经规划好的任务.md`

The task collection is the source of truth for tasks to add. The already-planned file is the source of truth for avoiding duplicates.

If a task collection block contains an Obsidian wikilink that points to a homework note, treat that wikilink as part of the task identity and preserve it in the final Tasks line.

## Required Workflow

1. Read the three canonical files.
2. Split `ToDo-任务集合.md` into independent task blocks using `---` separators.
3. For each block, decide whether it is already planned by comparing course name, linked note, task title, and obvious aliases against `ToDo-已经规划好的任务.md`.
4. If a block contains an Obsidian wikilink such as `[[15.测度性质与分解习题]]`, follow the link and read the linked note to determine the actual task content.
5. For homework notes, count `[!Note]` blocks as the primary unit of work. If there are no `[!Note]` blocks, use numbered exercise headings or explicit listed questions.
6. Estimate time and priority, then create one Tasks line per independent homework/major item. Do not split one homework note into many Tasks lines, but do not merge two different homework links merely because they belong to the same course.
7. Append the newly planned Tasks code and a concise advice note to the end of `ToDo-已经规划好的任务.md`; never delete, overwrite, or reorganize previously planned content in that file.
8. Remove only task blocks that both (a) were successfully planned and (b) contain an Obsidian wikilink to an archived homework/task note. If a homework/task block in `ToDo-任务集合.md` has no wikilink, keep it in the collection even after creating a planned Tasks line, because it has not been archived yet.
9. Keep unplanned blocks in `ToDo-任务集合.md` when links cannot be opened or task content is missing. If the task content is visible but no DDL can be inferred, still include it in the schedule, use the current date as `⏳`, omit a firm due date only when Tasks syntax would break, and add `(ddl未知)` to the task name; blocks without Obsidian wikilinks must still remain in the collection after planning.
10. In the final response, show the Tasks lines that were written, summarize why each estimate was chosen, and list any blocks left unplanned.

## Link Following

If the collection contains only a link, the linked note must be inspected before planning.

Preserve homework wikilinks in the final Tasks line. For example, a collection block `实分析[[15.测度性质与分解习题]]` should become a task name like `完成实分析作业[[15.测度性质与分解习题]]`, not merely `完成实分析作业`.

When resolving a wikilink:

- Search by exact filename stem first.
- Prefer Markdown notes inside the vault root.
- If multiple candidates exist, choose the one whose path best matches the course context in the task block.
- If no note is found, do not estimate. Say: `请补充 xx 文件的具体内容，否则无法排入计划。`

## Time Estimation

Use `1 🍅 = 40 分钟`.

For mathematics homework, assign every problem or `[!Note]` block to exactly one of three tiers:

- **20 分钟**：简单概念题、定义直接应用、短计算、单一结论、套用定理即可完成的题目。
- **40 分钟**：一般定理应用题或推广题，需要串联 1-2 个核心定理，步骤较多但路线明确。
- **60 分钟**：比较难的构造题或证明题，证明路线不标准、构造性强、计算很长，或一个 `[!Note]`/题目内有三个及以上小问。

Do not assign 60 minutes merely because a theorem name is advanced or the topic is important. Standard applications and routine extensions of heavy theorems are usually 40 minutes unless they require a genuinely difficult construction/proof or have three or more subquestions.

Do not create extra categories such as "calculation type", "proof type", or "formatting time". Do not estimate from the user's familiarity or weakness. Difficulty is based only on:

- theorem logic complexity,
- whether the task is a routine application/extension or a genuinely difficult construction/proof,
- amount of calculation,
- number of subquestions inside the same `[!Note]` or problem,
- whether textbook/PPT lookup is needed.

Total tomatoes:

```text
总分钟 = 20 * 简单题数 + 40 * 中等题数 + 60 * 困难题数
总番茄钟 = ceil(总分钟 / 40)
```

For non-math homework, use the same 20/40/60 tier idea when the task is question-based. If the task cannot be counted from visible content, leave `[🍅:: ]` and explain what must be supplied.

## Priority Mapping

Use Obsidian Tasks priority semantics:

- `🔺` = Highest
- `⏫` = High
- `🔼` = Medium
- no symbol = Normal
- `🔽` = Low
- `⏬` = Lowest

Estimate priority from:

- hard deadline,
- how close or overdue the deadline is,
- whether it is course homework,
- whether it relates to an upcoming exam,
- whether it needs textbook/PPT lookup and may expand.

Do not call these symbols "four quadrants". They are Tasks priority markers.

Suggested mapping:

- `🔺`: due today/tomorrow, overdue hard homework, or immediate course deadline.
- `⏫`: important course task due soon or exam-adjacent homework.
- `🔼`: useful but less urgent course/knowledge work.
- no symbol: ordinary task without strong pressure.
- `🔽`: low-priority task.
- `⏬`: can be safely deferred.

## Dates

Use the current date from the environment.

If the task gives an explicit deadline, respect it. If not:

- 实分析作业：默认周四课上截止。
- 拓扑作业：默认周四晚上习题课截止。
- 微分方程作业：默认周二截止，最晚周三习题课。
- 原子物理：优先使用任务集合或老师通知中的截止时间。
- Unknown course/task: do not invent a firm date. Still include the task when its content is visible, mark the task name with `(ddl未知)`, and use the current date as the scheduled day. If a due date is required by the local Tasks workflow, use the scheduled date as a placeholder and clearly explain that the real DDL is unknown.

`⏳` is the scheduled day. Choose a start date no later than the deadline, usually today for urgent/overdue work and 1-3 days before the deadline for larger tasks.

`📅` is the due date.

## Tasks Format

Every planned task line must use this shape:

```markdown
- [ ] #task 任务名 [🍅:: 0/预计番茄钟] 优先级 ⏳ YYYY-MM-DD 📅 YYYY-MM-DD
```

Rules:

- Keep task names short.
- Preserve the original homework wikilink from `ToDo-任务集合.md` in the task name when present, e.g. `完成实分析作业[[15.测度性质与分解习题]]`.
- Do not list all exercise numbers in the task description.
- Keep one line per independent homework note or major item.
- Do not merge two different homework links into one Tasks line just because they are from the same course; preserve the user's assignment-level phrasing and links.
- If estimated time is impossible, use `[🍅:: ]` and keep the task block in the collection. If only DDL is unknown but the content is visible, do not leave it unplanned; add `(ddl未知)` to the task name and explain the placeholder date.
- A task collection block without any Obsidian wikilink may still be planned when its content and deadline are visible, but it must remain in `ToDo-任务集合.md`; only linked, archived blocks may be removed after successful planning.
- Do not use `tasks` fences inside the files unless the local file already uses them. The final chat response may show a Markdown code block.

## Advice Note

After the Tasks lines appended to `ToDo-已经规划好的任务.md`, include a concise plain-text note with:

- task focus,
- limited starting advice,
- difficulty summary,
- any missing information.

Keep the advice short. It should help start execution, not become a study plan.

## Final Response

After editing files, report:

```text
已写入的 Tasks 代码：
...

简短说明：
- ...

未规划/保留在任务集合：
- ...
```

Also state that the planned blocks were removed from `ToDo-任务集合.md`.

