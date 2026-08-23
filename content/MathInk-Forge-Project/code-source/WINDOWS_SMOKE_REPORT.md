# MathInk Forge v1.0 — Windows smoke report

Date: 2026-08-20 (Asia/Shanghai)

## Environment

- Obsidian: `1.13.6`
- Vault: `D:\InkedMark-Advanced-TestVault`
- Plugin: `MathInk Forge` / `mathink-forge` / `1.0.0 · release`
- Plugin directory:
  `D:\InkedMark-Advanced-TestVault\.obsidian\plugins\mathink-forge`
- Upstream `inkedmark` is not listed in the test Vault's
  `.obsidian/community-plugins.json`.

## Proven observations

- Obsidian opened a window titled
  `InkedMark-Advanced-TestVault - Obsidian 1.13.6`.
- The command palette exposed MathInk Forge commands including Create
  handwriting note, Desktop Replay, input debug overlay, and changelog.
- `Create handwriting note` created and opened `Handwriting note.ink.md`.
- The ink view exposed Pen, Highlighter, Eraser, Select, five default preset
  buttons, Pen Box manager, seven color swatches, five sizes, pressure,
  undo/redo, clear, zoom, text layer, and recognition controls.
- The status read `v1.0.0 · release · 0 strokes · 100%` on a new note.
- Manual mouse drawing increased the live status to 9 strokes.
- The saved schema-v2 file contained 9 strokes with style snapshots and seven
  observed colors: black, white, red, blue, green, orange, and purple.
- `Ctrl+Z` changed the live count from 9 to 8. After the save debounce, the
  file also contained 8 styled strokes, proving the undo reached persistence.
- After an Obsidian reload, the user reopened the note and confirmed that the
  displayed stroke count was still 8, proving the saved state survived a real
  application reload.
- The user then manually confirmed a fresh post-reload draw/undo/redo sequence
  behaved correctly in the live view (8 → 9 → 8 → 9).
- Desktop Replay opened in the actual Obsidian process and exposed its replay
  pen selector, fixture button, and `Raw input`, `Current output`, and
  `Reference output` comparison panels.
- `Input Lab: start raw input recording` started successfully and automatically
  exposed the enhanced HUD. The live text contained pointer id/buttons,
  coordinates/timestamp, pressure min/max/mean/variance/P05/P50/P95,
  tilt/twist, gap median/P95/max and long-gap count, event/coalesced/predicted
  counts, committed stroke count, and API availability.
- During this smoke test, the stop/export command disappeared after the command
  palette took focus. The command had incorrectly depended on the active view.
  The implementation now searches all ink leaves for the recording view and
  the fix has passed formatting, lint, typecheck, 246 tests (including
  source-level regression guard), coverage, and a production build. Manual
  stop/export retesting remains pending.
- Initial post-undo file SHA-256:
  `CD400051A0CB3A7A55555480F23AD6D5D0B4350F5F2D98B4553777994ABDA9B2`.
- After the real reload/reopen, the current file SHA-256 is
  `DF43095689755C9A46DCA1843B5693C6026CEBF86075125F252C2F9D60B931A1`;
  direct payload decoding still reports schema v2 and exactly 8 strokes
  (`s4` through `s11`).

## Still to verify interactively

- Persist the final post-redo 9-stroke state and confirm it after another reopen.
- Preset buttons, rather than legacy color swatches, restore the complete
  style tuple on click.
- Highlighter, eraser, selection/move/delete, clear, zoom, text layer, inline
  ink, Input Lab stop/export, and Desktop Replay fixture loading.
- Restart persistence and ten save/reopen rounds.

This is a Windows smoke report only. It does not satisfy the Huawei/M-Pencil,
touch-layout, 30-minute endurance, or Huawei → Windows → Huawei P0 gates.

The direct disk snapshot taken after the user-reported live undo/redo pass still
contained the earlier 8-stroke payload, so this report does not yet claim that
the final redo state reached disk.
