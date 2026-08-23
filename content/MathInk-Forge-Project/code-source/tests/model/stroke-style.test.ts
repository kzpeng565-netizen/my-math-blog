import { describe, expect, it } from "vitest";
import {
  DEFAULT_FREEHAND_CONFIG,
  DEFAULT_PRESSURE_CONFIG,
  cloneStrokeStyle,
  legacyStrokeStyle,
  type StrokeStyleSnapshotV1,
} from "../../src/model/stroke-style";

describe("stroke style snapshots", () => {
  it("deep-clones nested pressure and freehand configuration", () => {
    const source: StrokeStyleSnapshotV1 = {
      version: 1,
      color: "#123456",
      size: 4,
      opacity: 0.8,
      tool: "pen",
      pressure: { ...DEFAULT_PRESSURE_CONFIG },
      freehand: { ...DEFAULT_FREEHAND_CONFIG },
    };
    const clone = cloneStrokeStyle(source);
    clone.pressure.gamma = 2;
    clone.freehand.smoothing = 0.9;
    expect(source.pressure.gamma).toBe(1);
    expect(source.freehand.smoothing).toBe(0.5);
  });

  it("reconstructs the exact legacy pen pressure mode", () => {
    const style = legacyStrokeStyle("#1a1a1a", 3, "pen", true, 0.35);
    expect(style.opacity).toBe(1);
    expect(style.pressure.enabled).toBe(true);
    expect(style.freehand.thinning).toBe(0.6);
  });

  it("reconstructs legacy highlighter opacity and fixed width", () => {
    const style = legacyStrokeStyle("#ffd43b", 12, "highlighter", true, 0.37);
    expect(style.opacity).toBe(0.37);
    expect(style.pressure.enabled).toBe(false);
    expect(style.freehand.thinning).toBe(0);
  });
});
