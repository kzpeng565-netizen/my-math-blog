# MathInk Forge v1.0 — Huawei device test report

- Date/time: 2026-08-20 (Asia/Shanghai)
- Tester: user, with Codex-assisted ADB evidence collection
- Tablet exact model: HUAWEI MatePad `BAH3-W09` (`HWBAH3` / vendor model `orlando`)
- M-Pencil generation: 1st generation (user-confirmed); Android input device name is `M-Pencil`
- HarmonyOS version: `3.0.0`; build `BAH3-W09 3.0.0.167(C00E160R1P5)`
- Android compatibility version: `10`
- EMUI property: `EmotionUI_13.0.0`
- Obsidian version: `1.13.7` (`versionCode=364`)
- Huawei WebView version: `114.0.5.302` (`com.huawei.webview`, versionCode `21705`)
- MathInk Forge build: `1.0.0 / release`
- Candidate ZIP SHA-256: `3D71EEF68ED84846E3EB2C988378C1BF6FE05C7133E31B7F3D402BDCE3A920E8`
- Test Vault: `/storage/emulated/0/Documents/测试仓库`
- Plugin directory: `/storage/emulated/0/Documents/测试仓库/.obsidian/plugins/mathink-forge`
- Input fixture filename and SHA-256: pending
- Test note filename and before/after SHA-256: pending

## Installation evidence

- QtScrcpy-bundled ADB connected device serial `8UXNU20509100338` as status `device`.
- Existing upstream `inkedmark` directory and its `data.json` were retained unchanged.
- Previous enabled-plugin list was backed up as
  `.obsidian/community-plugins.before-mathink-forge.json`.
- Enabled-plugin list now contains only `mathink-forge`.
- Tablet-side release hashes:
  - `main.js`: `30F5D86BB0CDFDBB522E96A0225B3B0F72CDEE4F49B628C0DCB4900CD61B0328`
  - `manifest.json`: `209821D82CEEFF24118571E831BE73654E766D8629C216248BEC6749B2EC43A9`
  - `styles.css`: `AE3960C8B6F717454D817A2973BC546EB5FDF6A456E47351B60EF39A669966F1`
- All three tablet hashes match the candidate staging artifacts.
- All five Input Lab metadata fields were written to the plugin settings while
  Obsidian was stopped, pushed with SHA-256
  `08FEAB4BD2DB3375D580E772163DDC692375F2A38870BB17067AF7C8D35F72B9`,
  and read back after restart with the expected values.
- Obsidian restarted successfully with no plugin-load error in logcat.
- The accessibility tree exposed the plugin-provided `Edit handwriting` inline
  block while only `mathink-forge` was enabled, proving the plugin loaded and
  registered its ink processor on the Huawei device.
- Android input service exposes `M-Pencil` with a pressure motion range of
  `0.000–1.000`. This is OS-level capability evidence only; it does **not** prove
  that Obsidian WebView emits variable pressure.

## Input Lab result

- Existing real note evidence: 103 saved strokes / 1140 points, with pressure
  `0.35294–0.89804`; all strokes have style snapshots. This proves variable
  pressure reached persisted geometry, but does not replace the raw event fixture.
- Reported defect: following ink feels slow and rapid writing can miss strokes.
- First corrective build removes whole-document bounds scans/layout writes from
  ordinary pen-up, makes live HUD aggregation constant-time at 4 Hz, restores
  the prior HUD state on stop, records handler/dispatch timing, and exports JSON
  through the Vault API. It is installed and awaiting same-pattern off/on retest.
- The prior Blob export displayed a success notice but produced no file in Huawei
  shared storage; it is not accepted as evidence.

- Pen sample count: pending
- Pressure min/max/mean/variance/P05/P50/P95: pending
- Pressure verdict (`variable`, `unproven-fixed`, `insufficient-samples`): pending
- Move gap median/P95/max; long-gap count: pending
- Coalesced API available: pending
- Predicted API available: pending
- Tilt/twist values observed: pending
- Desktop Replay result: pending
- Handler processing P95/max: pending
- WebView dispatch-delay P95/max: pending

## Thirty-minute session

- Start/end: pending
- Pens used: pending
- Required glyphs/operations completed: pending
- Undo/redo/eraser/select/zoom/pan/palm-rejection result: pending
- Huawei → Windows → Huawei round-trip result: pending
- Stroke count on Huawei / Windows / Huawei: pending
- Text layer and inline ink result: pending
- Reproducible defects (steps + fixture): pending

## Decision

- [ ] GO — every P0 row in `MATHINK_FORGE_V1_QA.md` passed.
- [x] NO-GO — Input Lab, touch/Pen Box, endurance and cross-device P0 evidence remains pending.

Signature/date: pending
