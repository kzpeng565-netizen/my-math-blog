import { describe, expect, it } from "vitest";
import type { DiagnosticSample } from "../../src/input/diagnostics";
import { normalizePointerMove } from "../../src/input/input-normalizer";

const sample = (x: number): DiagnosticSample => ({
  x,
  y: 2,
  pressure: 0.5,
  tiltX: 0,
  tiltY: 0,
  timeStamp: x,
  pointerType: "pen",
  pointerId: 1,
  buttons: 1,
  twist: 0,
});

describe("normalizePointerMove", () => {
  it("falls back to the parent event when no coalesced samples exist", () => {
    const parent = sample(3);
    expect(normalizePointerMove(parent, [], []).committed).toEqual([parent]);
  });

  it("uses coalesced samples without appending a duplicate parent event", () => {
    const normalized = normalizePointerMove(sample(3), [sample(1), sample(2), sample(3)], []);
    expect(normalized.committed.map((item) => item.x)).toEqual([1, 2, 3]);
  });

  it("keeps predicted samples isolated from committed geometry", () => {
    const normalized = normalizePointerMove(sample(1), [], [sample(2), sample(3)]);
    expect(normalized.committed.map((item) => item.x)).toEqual([1]);
    expect(normalized.predicted.map((item) => item.x)).toEqual([2, 3]);
  });
});
