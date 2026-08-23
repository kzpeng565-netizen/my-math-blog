import { describe, expect, it } from "vitest";
import { applyPressureCurve, mapConfiguredPressure } from "../../src/ink/pressure";
import { DEFAULT_PRESSURE_CONFIG, type PressureCurve } from "../../src/model/stroke-style";

describe("pressure curves", () => {
  const curves: PressureCurve[] = ["linear", "soft", "medium", "hard"];

  for (const curve of curves) {
    it(`${curve} is bounded, endpoint preserving, and monotone`, () => {
      expect(applyPressureCurve(0, curve)).toBe(0);
      expect(applyPressureCurve(1, curve)).toBe(1);
      let previous = 0;
      for (let i = 0; i <= 100; i++) {
        const current = applyPressureCurve(i / 100, curve);
        expect(current).toBeGreaterThanOrEqual(previous);
        expect(current).toBeGreaterThanOrEqual(0);
        expect(current).toBeLessThanOrEqual(1);
        previous = current;
      }
    });
  }

  it("orders soft above linear and hard below linear at mid pressure", () => {
    expect(applyPressureCurve(0.5, "soft")).toBeGreaterThan(0.5);
    expect(applyPressureCurve(0.5, "hard")).toBeLessThan(0.5);
  });
});

describe("mapConfiguredPressure", () => {
  it("maps calibrated endpoints into the configured output range", () => {
    const config = {
      ...DEFAULT_PRESSURE_CONFIG,
      inputMin: 0.2,
      inputMax: 0.8,
      outputMin: 0.3,
      outputMax: 0.9,
      curve: "linear" as const,
    };
    expect(mapConfiguredPressure(0.2, config)).toBeCloseTo(0.3);
    expect(mapConfiguredPressure(0.8, config)).toBeCloseTo(0.9);
  });

  it("uses fallback for disabled, zero, and non-finite input", () => {
    const config = { ...DEFAULT_PRESSURE_CONFIG, enabled: false, fallback: 0.42 };
    expect(mapConfiguredPressure(0.8, config)).toBeCloseTo(0.42);
    expect(mapConfiguredPressure(0, { ...config, enabled: true })).toBeCloseTo(0.42);
    expect(mapConfiguredPressure(Number.NaN, { ...config, enabled: true })).toBeCloseTo(0.42);
  });

  it("applies gamma after the named curve", () => {
    const base = {
      ...DEFAULT_PRESSURE_CONFIG,
      curve: "linear" as const,
      outputMin: 0,
      outputMax: 1,
    };
    expect(mapConfiguredPressure(0.5, { ...base, gamma: 2 })).toBeCloseTo(0.25);
  });
});
