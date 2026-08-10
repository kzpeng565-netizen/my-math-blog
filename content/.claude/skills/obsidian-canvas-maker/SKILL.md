---
name: obsidian-canvas-maker
description: Create, repair, and maintain readable, source-faithful Obsidian Canvas files from Markdown handoff and operations documents. Use when working with .canvas diagrams, module and data-flow layouts, node overlap or scrolling, edge-label collisions, uncertain architecture, Canvas JSON validation, or visual layout QA.
---

# Obsidian Canvas Maker

Create maintainable `.canvas` diagrams whose primary purpose is future maintenance. Keep the Canvas at a stable overview level and put implementation detail in linked Markdown notes. Treat source documents as authoritative; never silently complete an undocumented mechanism.

If the user supplied a task after `/obsidian-canvas-maker`, use it as the task scope:

```text
$ARGUMENTS
```

## Workflow

### 1. Build the source inventory

Before writing Canvas JSON:

1. Locate the handoff file, boundary/interface files, project-state files, decision logs, next-step files, and relevant subfolders.
2. Read the governing documents sufficiently to identify modules, locations, data stores, triggers, schedules, notifications, outputs, failure entrances, recovery paths, and dependency edges.
3. Record at least:
   - module ID and responsibility;
   - running location: phone, tablet, Windows, Pi, network boundary, external service, or document;
   - automatic versus manual operation;
   - input, output, state/configuration file, and persistence location;
   - trigger and schedule;
   - failure symptom, log or status entry point, and fallback;
   - source Markdown link;
   - dependent modules that may be affected by a change.
4. Compare conflicting documents explicitly. Mark stale, contradictory, or unconfirmed mechanisms as `待确认`; do not choose a version by intuition.
5. Decide the node list before arranging positions. Keep overview diagrams near the requested core-node budget; count group, title, legend, and file nodes separately from core modules.

### 2. Choose the Canvas structure

Use the layout that matches the scope:

- **Overall overview:** columns for devices and boundaries, plus a document column.
- **Device-internal diagram:** columns for collection, bridge/execution, network/notification, Pi interaction, failures, and documentation.
- **Service-internal diagram:** columns for ingestion, processing, timers, decision/API, database, feedback, and documentation.

Use groups for modules with the same device or responsibility. Use text nodes for operational summaries, file nodes for linked Markdown, and short edge labels for relationship types. Keep detailed procedures in linked notes instead of expanding every node into a runbook.

### 3. Apply a safe layout baseline

Use conservative geometry:

- group width: about `520`;
- column step: about `560`, leaving a visible gap between adjacent groups;
- content node width: about `420`;
- vertical gap between same-column nodes: at least `100`;
- group padding: at least `20` inside and `100` below the final node;
- title and legend: independently above the main columns, never inside a normal module stack;
- documentation column: far right, with enough height for file-link text.

For mixed Chinese/English text, use visible safety margin rather than a compact line-count estimate:

- ordinary text node: at least `240` high;
- longer operational node: usually `290–400` high;
- failure or multi-line diagnostic node: `450+` when needed.

After changing a node height, reflow every following node in that group and recompute the group height. Never increase heights without moving later nodes.

When using a layout script, map each group to explicit node IDs. Do not infer membership from coordinates after moving groups. Use the group index within the current Canvas, not the Canvas/file index, to calculate columns.

### 4. Design edges for maintenance

Obsidian Canvas edge labels are positioned automatically along an edge and do not provide general collision avoidance, waypoints, or manual label offsets in `.canvas` JSON. Therefore:

- keep labels to one short relation, such as `15 分钟上传`, `Focus API`, `周报`, or `反馈回流`;
- move detailed semantics into the source/target node or linked Markdown;
- avoid several long, parallel edges terminating at the same node;
- choose `fromSide` and `toSide` deliberately, especially for vertical same-column flows;
- do not assume larger nodes will fix edge-label overlap;
- visually inspect long cross-column edges and labels after every major layout change.

If labels collide, shorten or remove the label first, then simplify parallel edges or add a documented intermediate data-flow node. Never fake a label with undocumented content.

### 5. Preserve uncertainty and boundaries

Use a visible `待确认` marker for:

- conflicting old/new instructions;
- a service or flow whose current enablement is unknown;
- an endpoint, proxy, authentication mode, timer interval, environment file, or migration mechanism that is not confirmed;
- an old target architecture that is documented but not implemented.

Keep the distinction between automatic service, human action, notification-only client, read-only replica, and authoritative write endpoint. Show directionality and write authority explicitly for databases and synchronized folders. Preserve all source-backed pending items in the accompanying explanation note.

### 6. Validate before delivery

Run checks in this order:

1. Parse every `.canvas` with a real JSON parser, preferably Node.js. Do not rely only on text grep or a shell JSON parser with uncertain encoding behavior.
2. Check duplicate node IDs, missing node types, dangling edges, empty text nodes, invalid file targets, and missing required fields.
3. Check that every explicit group member stays inside its group bounds after final height calculation.
4. Check text nodes for unnecessary internal-scroll risk; inspect the longest mixed-language nodes directly.
5. Render each Canvas to a preview and inspect both overview scale and at least one dense local region. Look for group overlap, node overlap, labels over nodes, parallel-edge label collisions, clipped text, and excessive empty space.
6. Run `git diff --check` on changed Canvas and explanation files.
7. Re-read the final Canvas against the source inventory. Confirm that uncertain items remain uncertain and that no service or configuration was changed accidentally.

For cleanup, remove only truly empty, unreferenced nodes. Search all edges for a node ID before removing it; repair the edge or confirm the deletion intent first.

## Common failure modes

| Symptom | Cause | Fix |
|---|---|---|
| Text node shows a scrollbar or clipped bottom lines | Height estimate was too optimistic for mixed-language wrapping | Increase height conservatively, reflow the column, and recompute group bounds |
| Groups overlap horizontally | Column gap is smaller than group width, or the wrong index was used | Use explicit group membership, width about `520`, and step about `560` |
| Groups stack after resizing | Columns were assigned from the Canvas index | Recalculate x from the group index within that Canvas |
| Nodes overlap after height changes | Heights changed without moving later nodes | Sort members by intended order and set each next y to the previous bottom plus the gap |
| Edge label crosses another label or node | Automatic label placement has no collision avoidance | Shorten the label, reduce parallel edges, adjust attachment sides, or add a documented intermediate node |
| Empty boxes remain | An old layout left blank, unreferenced text nodes | Verify edge references, then remove only empty unreferenced nodes |
| Conflicting behavior is shown as fact | An undocumented gap was filled by intuition | Add `待确认`, cite the conflicting notes, and preserve both claims where useful |
| Validation fails only in PowerShell | Encoding or parser behavior differs from the UTF-8 JSON | Validate with Node JSON parsing, then run `git diff --check` |
| Preview looks like one giant column | Membership was inferred after moving groups, or the Canvas index was reused | Restore explicit membership maps and recalculate columns from group order |

## Delivery

When handing off:

- link every created or changed `.canvas` file with an absolute local path;
- state each Canvas's purpose and main grouping;
- summarize visual/layout changes separately from source-content changes;
- list unresolved `待确认` items without resolving them silently;
- state whether Pi services, Windows tasks, or application code changed, or whether only diagram/note files changed;
- report structural validation and visual QA results.

Do not commit or restart services unless the user explicitly requests it.
