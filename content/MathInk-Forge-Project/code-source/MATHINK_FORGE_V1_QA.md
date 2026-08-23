# MathInk Forge v1.0 QA

This checklist is the release gate for the local advanced fork. Automated items
are reproducible on Windows; device items must be signed off on the target Huawei
tablet and M-Pencil. A release is **No-Go** while any P0 device row remains blank.

## Automated gate

- [x] Pinned upstream baseline and independent plugin id.
- [x] `npm ci` — 454 packages, 0 vulnerabilities at baseline audit.
- [x] `npm run lint` — zero warnings.
- [x] `npm run typecheck`.
- [x] `npm test` — all implementation tests pass.
- [x] `npx vitest run --coverage` — overall lines 94%+, input diagnostics 80%+.
- [x] `npm run build` and deployment to the dedicated test Vault.
- [x] A separate Node 20 clean snapshot repeats `npm ci`, all CI commands,
      coverage and build; generated `main.js` matches the candidate hash.
- [x] Five upstream-v1 notes preserve exact bytes through a clean view
      open/close lifecycle and reopen after explicit v2 migration.
- [x] All five migrated legacy fixtures preserve identical stroke regions
      through ten encode/reopen cycles at the pure data layer. Actual Obsidian
      and cross-device reopen cycles remain device-gated below.
- [x] Twelve Input Lab fixtures include light→heavy, heavy→light, fast, slow,
      circle, integral sign, Chinese and full-formula scenarios.
- [x] Pressure curves are bounded, endpoint-preserving and monotone.
- [x] Preset JSON round-trips exactly; merge collisions receive new ids while
      preserving the exported active pen. Pen Box also exposes a confirmed
      `Replace from JSON` path for full-store restore.
- [x] Single-point, very short, repeated-point and zero-pressure geometry stays
      finite; ten identical replays produce identical geometry.
- [x] Live drawing and replay share one InputNormalizer; parent fallback,
      coalesced no-duplicate behavior and predicted isolation are tested.
- [x] Desktop Replay displays raw/current/reference panels, and all twelve
      fixture outputs match the committed geometry SHA-256 baseline.

Run the full automated gate from a clean checkout:

```powershell
npm ci
npm run format:check
npm run lint
npm run typecheck
npm test
npx vitest run --coverage
npm run build
```

## Huawei Input Lab gate

Before capture, fill the five **Input Lab…** fields in plugin settings. Open a
dedicated `.ink.md` note and run:

1. `Input Lab: start raw input recording`.
2. Draw at least 50 pen samples, deliberately varying pressure; include fast and
   slow strokes, a circle, an integral sign, Chinese, and a formula.
3. Run `Input Lab: stop and export recording`.
4. On Windows run `Input Lab: open Desktop Replay` and load the JSON.

Required result:

- [ ] Exact tablet, M-Pencil, HarmonyOS, Obsidian and WebView versions are in the fixture.
- [ ] `pointerType=pen`; touch and mouse are distinguishable.
- [ ] At least 50 committed pen samples.
- [ ] Pressure verdict is `variable`. If range is below `0.05` or values remain
      near `0.5`, record `unproven-fixed` and use a fixed-width fallback—do not claim pressure support.
- [ ] Median/P95/max gaps and long-gap count are recorded.
- [ ] Handler processing P95/max and WebView dispatch-delay P95/max are recorded.
- [ ] Coalesced/predicted API availability is stated.
- [ ] Predicted samples appear in diagnostics only and do not extend committed replay geometry.
- [ ] Desktop Replay renders the fixture using each of the four pressure curves.
- [ ] The same rapid-stroke pattern is acceptable with Input Lab off and on;
      diagnostic overhead does not create a false performance failure.

## Pen Box device gate

- [ ] All five default pens switch with one tap and show an active state.
- [ ] Twenty sequential switches do not mismatch tool/color/size/pressure.
- [ ] Presets and order survive a full Obsidian restart.
- [ ] Create, edit/rename, copy, delete and reorder each work five times.
- [ ] Export, change/restore the Pen Box, then use `Replace from JSON`; preset
      content, order, and active pen match the exported store.
- [ ] Damaged JSON changes nothing and displays a readable error.
- [ ] Ten strokes written before editing a preset retain identical appearance.
- [ ] Landscape and portrait layouts leave the writing area usable; buttons are touchable.

## Compatibility and endurance gate

- [ ] Open the five files under `fixtures/legacy/` on Windows and Huawei.
- [ ] Merely open/close a copied legacy fixture; its SHA-256 stays unchanged.
- [ ] Modify/save/reopen a copy ten times; count, position, color and width remain stable.
- [ ] A deliberately future `v3:` payload stays protected and is never overwritten.
- [ ] Dedicated `.ink.md`, inline ink, text layer, erase, select/move/delete,
      undo/redo, pinch zoom, pan and palm rejection all pass.
- [ ] Complete a 30-minute mathematics session using black, blue, red and one
      highlighter, including Chinese, English, integral, fraction, superscript,
      circle and fast connected writing.
- [ ] Save on Huawei, edit on Windows, reopen on Huawei; stroke counts agree and
      text layer/inline blocks remain intact.
- [ ] No reproducible missing stroke, duplicate stroke, palm ink or tool-state corruption.

## Evidence record

Copy [DEVICE_TEST_REPORT_TEMPLATE.md](DEVICE_TEST_REPORT_TEMPLATE.md), fill it,
and store the exported JSON plus note hashes outside any public repository if the
content is sensitive. Do not check a box based on synthetic fixtures alone.
