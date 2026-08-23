import { createHash } from "node:crypto";
import { describe, expect, it } from "vitest";
import {
  optionsForStrokeStyle,
  outlineForStroke,
  outlineToSvgPath,
  penOptions,
  strokeOutline,
} from "../../src/ink/freehand";
import { defaultPenPresets } from "../../src/ink/presets";

const style = defaultPenPresets()[0].style;
const options = optionsForStrokeStyle(style);

describe("PerfectFreehandEngine adapter", () => {
  it.each([
    ["single point", [10, 10, 0.5]],
    ["very short", [10, 10, 0.3, 10.01, 10.01, 0.8]],
    ["repeated points", [10, 10, 0.3, 10, 10, 0.6, 10, 10, 0.9]],
    ["zero pressure", [0, 0, 0, 20, 20, 0]],
  ])("renders %s without non-finite geometry", (_name, points) => {
    const outline = strokeOutline(points as number[], options, true);
    expect(outline.length).toBeGreaterThan(0);
    expect(outline.flat().every(Number.isFinite)).toBe(true);
    expect(outlineToSvgPath(outline)).not.toContain("NaN");
    expect(outlineToSvgPath(outline)).not.toContain("Infinity");
  });

  it("produces deterministic geometry across ten replays", () => {
    const points = [0, 0, 0.2, 12, 8, 0.35, 25, 4, 0.7, 40, 18, 0.9];
    const hashes = Array.from({ length: 10 }, () =>
      createHash("sha256")
        .update(outlineToSvgPath(strokeOutline(points, options, true)))
        .digest("hex"),
    );
    expect(new Set(hashes)).toHaveLength(1);
  });

  it("maps pressure mode into perfect-freehand simulation mode", () => {
    expect(penOptions(3, true).simulatePressure).toBe(false);
    expect(penOptions(3, false)).toMatchObject({ thinning: 0, simulatePressure: true });
  });

  it("outlines a committed stroke through the convenience adapter", () => {
    const outline = outlineForStroke(
      { id: "s1", color: "#000000", size: 3, tool: "pen", pts: [0, 0, 0.5] },
      options,
    );
    expect(outline.flat().every(Number.isFinite)).toBe(true);
  });
});
