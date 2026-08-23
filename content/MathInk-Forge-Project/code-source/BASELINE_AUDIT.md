# MathInk Forge v1.0 — baseline audit

## Pinned baseline

- Upstream: `https://github.com/pcrausaz/obsidian-inkedmark.git`
- Commit: `25515b65ce0ea9de47271f9b41c7c55cbc2605fa`
- Upstream version: `1.3.0`
- Commit date: `2026-08-15T11:56:47-05:00`
- Local branch: `codex/v1.0`
- Local runtime used for the audit: Node `v24.15.0`, npm `11.12.1`
- Installed reference copy: `D:\mathblog\quartz\content\.obsidian\plugins\inkedmark`

The installed reference copy reports InkedMark `1.3.0`. Its settings file was
inspected by key name only; API-key values were not read or copied.

## Baseline quality gates

| Gate                   | Result                     | Evidence                                                                                    |
| ---------------------- | -------------------------- | ------------------------------------------------------------------------------------------- |
| `npm ci`               | PASS                       | 454 packages installed, 0 vulnerabilities                                                   |
| `npm run lint`         | PASS                       | ESLint exited successfully with zero warnings                                               |
| `npm run typecheck`    | PASS                       | `tsc --noEmit` exited successfully                                                          |
| `npm run test`         | PASS                       | 18 files, 189 tests passed                                                                  |
| `npm run build`        | PASS                       | production bundle completed                                                                 |
| `npm run format:check` | BASELINE ENVIRONMENT ISSUE | Windows checkout uses CRLF (`core.autocrlf=true`); Prettier reports every tracked text file |

`format:check` is not treated as a product regression. The downstream config
will explicitly accept the local checkout's line ending while retaining every
other formatting rule.

## Actual input → render → persistence chain

```text
PointerEvent
  → input/pointer-controller.ts
      - pointer capture
      - coalesced-event expansion with parent-event fallback
      - predicted events for wet rendering only
      - pen/touch arbitration via PalmRejection
  → view/ink-surface.ts
      - world-coordinate mapping
      - StrokeBuilder decimation
      - wet render throttled to requestAnimationFrame
      - AddStroke command on commit
  → ink/stroke-builder.ts
      - [x, y, pressure] tuples
      - global pressure toggle and fixed fallback
  → canvas/renderer.ts + ink/freehand.ts
      - perfect-freehand outline
      - wet/dry canvases
      - global highlighter alpha
  → model/document.ts
      - Stroke {id,color,size,tool,pts}
  → model/serialize.ts
      - coordinate/pressure quantization
      - deflate + base64 in %%inkedmark block
```

## Requirement matrix

| v1.0 requirement                                  | Upstream state                 | Downstream action                                                                |
| ------------------------------------------------- | ------------------------------ | -------------------------------------------------------------------------------- |
| Coalesced events without duplicate parent samples | Implemented                    | Preserve and unit-test normalization                                             |
| Predicted points excluded from committed strokes  | Implemented                    | Preserve and expose in diagnostics only                                          |
| Palm rejection / pan / pinch                      | Implemented                    | Regression-only                                                                  |
| Wet/dry rendering                                 | Implemented                    | Reuse                                                                            |
| Stroke eraser / select / undo / redo              | Implemented                    | Regression-only                                                                  |
| Input HUD                                         | Partial                        | Replace ad-hoc counters with reusable statistics and export                      |
| Raw stroke fixture export                         | Missing                        | Add versioned recorder/export                                                    |
| Desktop fixture replay                            | Missing                        | Add replay modal using the production brush path                                 |
| Pressure min/max/curve/gamma                      | Missing                        | Add pure `PressureMapper`                                                        |
| PenPreset model + five defaults                   | Missing                        | Add versioned, validated store                                                   |
| Pen Box one-click switching                       | Missing                        | Add toolbar preset strip and manager modal                                       |
| Preset import/export                              | Missing                        | Add validated JSON round-trip with conflict-safe ids                             |
| Per-stroke style snapshot                         | Missing                        | Add schema v2 optional snapshot; legacy strokes retain v1 rendering              |
| Preset edits do not change history                | Missing                        | Snapshot on pointer-down/commit and test                                         |
| Unknown future schema is never overwritten        | Contradicted                   | Reject versions newer than supported; existing protection path becomes read-only |
| Old v1 documents open unchanged                   | Implemented for current schema | Add explicit v1 fixtures and v2 migration tests                                  |
| Huawei/M-Pencil capability report                 | Not tested                     | Requires physical target device after implementation                             |

## Data and compatibility decisions

1. Keep the existing `inkedmark` frontmatter flag, block label, and `.ink.md`
   format so existing notes remain readable.
2. Use document schema `2` for the additive stroke style snapshot.
3. Keep legacy `color`, `size`, and `tool` fields. New strokes also store a
   `style` snapshot; old strokes without it use the exact legacy rendering path.
4. Reject payload versions newer than the supported schema. `InkView` already
   protects unreadable data blocks by echoing their original bytes on save.
5. The downstream plugin id is `mathink-forge`. It must not be enabled at
   the same time as upstream `inkedmark`, because both intentionally recognize
   the same note format.
6. Development deployment targets a dedicated test Vault. The installed
   upstream plugin and its `data.json` are not overwritten.

## Gate A status

Automatable Gate A work is complete: the upstream commit is pinned, the source
chain and gaps are recorded, the clean baseline passes lint/typecheck/tests/build,
and the installed 1.3.0 plugin has been located without reading secret values.

Five generated, non-sensitive upstream-format `.ink.md` fixtures now live under
`fixtures/legacy/` and exercise v1 open-without-write plus explicit v2 migration.
Real user notes were deliberately not read or copied. The final Huawei gate may
add copied, non-sensitive real fixtures after the user selects them.

## v1 implementation status (2026-08-20)

- PenPreset/Pen Box, PressureMapper, style snapshots, schema-v2 migration,
  Input Lab capture/statistics, Desktop Replay and required synthetic scenarios
  are implemented.
- The production build deploys only `main.js`, `manifest.json`, and `styles.css`
  to `D:\InkedMark-Advanced-TestVault\.obsidian\plugins\mathink-forge`.
- Automated tests and coverage pass. See `MATHINK_FORGE_V1_QA.md` for the remaining
  physical Huawei/M-Pencil, cross-device, and 30-minute endurance gates.
