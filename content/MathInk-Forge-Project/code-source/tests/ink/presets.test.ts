import { describe, expect, it } from "vitest";
import {
  defaultPenPresets,
  exportPresetStore,
  importPresetStore,
  normalizePresetList,
  uniquePresetId,
  validatePenPreset,
} from "../../src/ink/presets";

describe("default pen presets", () => {
  it("ships the five required math-writing pens", () => {
    const presets = defaultPenPresets();
    expect(presets).toHaveLength(5);
    expect(presets.map((item) => item.id)).toEqual([
      "math-black",
      "body-blue",
      "review-red",
      "highlight-yellow",
      "highlight-green",
    ]);
    expect(presets.every((item) => validatePenPreset(item).length === 0)).toBe(true);
  });

  it("returns independent deep copies", () => {
    const first = defaultPenPresets();
    const second = defaultPenPresets();
    first[0].style.pressure.gamma = 4;
    expect(second[0].style.pressure.gamma).toBe(1);
  });
});

describe("preset import/export", () => {
  it("round-trips an exported store", () => {
    const presets = defaultPenPresets();
    const imported = importPresetStore(exportPresetStore(presets, "review-red"));
    expect(imported.presets).toEqual(presets);
    expect(imported.activePresetId).toBe("review-red");
  });

  it("renames ids that conflict with existing pens", () => {
    const presets = defaultPenPresets();
    const imported = importPresetStore(exportPresetStore([presets[0]], presets[0].id), presets);
    expect(imported.presets[0].id).toBe("math-black-2");
    expect(imported.activePresetId).toBe("math-black-2");
  });

  it("keeps the exported active pen selected when every imported id is renamed", () => {
    const presets = defaultPenPresets();
    const imported = importPresetStore(exportPresetStore(presets, "review-red"), presets);
    expect(imported.presets.map((item) => item.id)).toEqual([
      "math-black-2",
      "body-blue-2",
      "review-red-2",
      "highlight-yellow-2",
      "highlight-green-2",
    ]);
    expect(imported.activePresetId).toBe("review-red-2");
  });

  it("rejects corrupt JSON without returning a partial store", () => {
    expect(() => importPresetStore("{bad json")).toThrow("not valid JSON");
  });

  it("rejects a preset with an invalid pressure range", () => {
    const preset = defaultPenPresets()[0];
    preset.style.pressure.inputMin = 0.8;
    preset.style.pressure.inputMax = 0.2;
    expect(validatePenPreset(preset)).toContain(
      "Pressure input range must be increasing inside 0–1.",
    );
  });
});

describe("preset normalization", () => {
  it("falls back to defaults for missing or wholly invalid settings", () => {
    expect(normalizePresetList(null)).toHaveLength(5);
    expect(normalizePresetList([{ nope: true }])).toHaveLength(5);
  });

  it("creates stable conflict-free ids", () => {
    expect(uniquePresetId("Math Black", new Set(["math-black", "math-black-2"]))).toBe(
      "math-black-3",
    );
  });
});
