# MathInk Forge v1.0 release and rollback

## Baseline and data format

- Upstream: `https://github.com/pcrausaz/obsidian-inkedmark.git`
- Pinned commit: `25515b65ce0ea9de47271f9b41c7c55cbc2605fa`
- Fork plugin/version: `mathink-forge` / `1.0.0`
- Document payload: schema v2; legacy v1 remains readable.
- New strokes keep legacy `color`, `size`, `tool` plus an immutable style snapshot.
- Unknown future payload versions are protected from overwrite.
- Pen Box `Import JSON` merges with collision-safe ids; `Replace from JSON`
  restores the complete exported store after confirmation. Merge imports retain
  the exported active pen even when its id is renamed.

## Build and install

```powershell
npm ci
npm run build
```

Copy only `main.js`, `manifest.json`, and `styles.css` into:

```text
<TestVault>/.obsidian/plugins/mathink-forge/
```

Enable `MathInk Forge` in Community plugins. Never enable upstream
`inkedmark` in the same Vault. Development currently deploys to
`D:\InkedMark-Advanced-TestVault\.obsidian\plugins\mathink-forge`.

Candidate ZIP SHA-256:
`3D71EEF68ED84846E3EB2C988378C1BF6FE05C7133E31B7F3D402BDCE3A920E8`.

## Known limits

- Huawei pressure capability is WebView/device-specific and must be established
  from a 50+ pen-sample Input Lab fixture; fixed `0.5` is not proof of pressure.
- Huawei fast-writing latency/missing-stroke retesting is still P0; this package
  is a candidate, not an accepted release, until the off/on Input Lab comparison passes.
- v1.0 does not implement tilt nibs, textured pencil, partial-stroke erasing,
  pressure-sensitive erasers, native Huawei SDKs, or a WASM brush engine.
- Desktop Replay compares raw input, current output and the fixture-preset
  reference output; committed SHA-256 geometry baselines catch deterministic
  regression, but synthetic fixtures cannot replace the Huawei endurance and
  cross-device gates.

## Rollback

An offline copy of the previous known-working upstream 1.3.0 release triplet is
stored at `D:\MathInk-Forge-Release\rollback-upstream-inkedmark-1.3.0.zip`.
It intentionally excludes `data.json`.

1. Close Obsidian on every device and back up the affected `.ink.md` files.
2. Disable `MathInk Forge`.
3. Restore the prior three-file plugin package to the `mathink-forge` folder,
   or remove that folder and re-enable upstream `inkedmark`—never both together.
4. Files explicitly saved by v1.0 use schema v2. Upstream 1.3.0 does not know the
   style snapshot, so retain the v1.0 package when those notes must be edited.
5. Verify a copied test note before touching the real Vault. If a note carries an
   unreadable/future payload, preserve its bytes and do not save it through another editor.

The dedicated test Vault and the user's installed upstream plugin directory are
separate; the v1 build does not overwrite the existing upstream installation or `data.json`.
