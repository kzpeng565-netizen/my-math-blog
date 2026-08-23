import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";

describe("Input Lab stop/export command", () => {
  it("searches all ink leaves instead of relying on the active view", () => {
    const source = readFileSync(join(process.cwd(), "src", "main.ts"), "utf8");
    const methodStart = source.indexOf("private recordingInputLabView()");
    const methodEnd = source.indexOf("override onunload()", methodStart);
    const method = source.slice(methodStart, methodEnd);

    expect(methodStart).toBeGreaterThanOrEqual(0);
    expect(methodEnd).toBeGreaterThan(methodStart);
    expect(method).toContain("getLeavesOfType(VIEW_TYPE_INK)");
    expect(method).toContain("isInputLabRecording");
    expect(method).not.toContain("getActiveViewOfType");
  });

  it("writes recordings through the Vault API instead of a WebView Blob download", () => {
    const source = readFileSync(join(process.cwd(), "src", "main.ts"), "utf8");
    const methodStart = source.indexOf("private async exportInputLabFixture");
    const methodEnd = source.indexOf("override onunload()", methodStart);
    const method = source.slice(methodStart, methodEnd);

    expect(methodStart).toBeGreaterThanOrEqual(0);
    expect(method).toContain('normalizePath("MathInk Forge Input Lab")');
    expect(method).toContain("this.app.vault.create(path");
    expect(method).not.toContain("createObjectURL");
  });
});
