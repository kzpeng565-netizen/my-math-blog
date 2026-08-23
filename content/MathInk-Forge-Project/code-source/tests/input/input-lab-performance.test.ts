import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";

const source = readFileSync(join(process.cwd(), "src", "view", "ink-surface.ts"), "utf8");

function method(name: string, nextMarker: string): string {
  const start = source.indexOf(name);
  const end = source.indexOf(nextMarker, start);
  expect(start).toBeGreaterThanOrEqual(0);
  expect(end).toBeGreaterThan(start);
  return source.slice(start, end);
}

describe("tablet input hot-path guards", () => {
  it("restores the pre-recording HUD state after Input Lab stops", () => {
    const body = method("stopInputRecording()", "get isInputRecording");
    expect(body).toContain("this.setDebug(this.debugBeforeRecording)");
  });

  it("does not rescan the whole document or force paper layout on every pen-up", () => {
    const body = method("private finishStroke", "// --- Eraser");
    expect(body).toContain("this.growPaperForStroke(stroke)");
    expect(body).not.toContain("ensurePaperSize");
    expect(body).not.toContain("documentBounds");
  });

  it("keeps live HUD statistics constant-time", () => {
    const body = method("private renderHud", "// --- Strokes");
    expect(body).not.toContain(".sort(");
    expect(body).not.toContain("hudPercentile");
  });
});
