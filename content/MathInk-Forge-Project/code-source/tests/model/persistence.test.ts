import { createHash } from "node:crypto";
import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { InkPersistenceState } from "../../src/model/persistence";
import { buildInkFile, parseInkFile } from "../../src/model/serialize";

const fixtureDirectory = join(process.cwd(), "fixtures", "legacy");
const fixtureFiles = readdirSync(fixtureDirectory).filter((name) => name.endsWith(".ink.md"));
const hash = (text: string): string => createHash("sha256").update(text).digest("hex");

describe("InkPersistenceState", () => {
  it("preserves every clean legacy note byte-for-byte across open and close", () => {
    for (const name of fixtureFiles) {
      const source = readFileSync(join(fixtureDirectory, name), "utf8");
      const parsed = parseInkFile(source);
      if (!parsed.doc) throw new Error(`Unreadable fixture: ${name}`);
      const state = new InkPersistenceState();
      state.load(source, false);

      const output = state.output(() => buildInkFile(parsed.body, parsed.doc!));
      expect(hash(output), name).toBe(hash(source));
      expect(output, name).toBe(source);
    }
  });

  it("migrates a legacy note to v2 only after a real edit", () => {
    const source = readFileSync(join(fixtureDirectory, fixtureFiles[0]), "utf8");
    const parsed = parseInkFile(source);
    if (!parsed.doc) throw new Error("Unreadable legacy fixture");
    const state = new InkPersistenceState();
    state.load(source, false);
    state.markDirty();

    const output = state.output(() => buildInkFile(parsed.body, parsed.doc!));
    expect(output).not.toBe(source);
    expect(output).toContain("\nv2:");
    expect(parseInkFile(output).doc?.regions).toEqual(parsed.doc.regions);
  });

  it("never rewrites a protected load, even if a mutation is requested", () => {
    const source = "body\n\n%%inkedmark\nv99:not-readable\n%%\n";
    const state = new InkPersistenceState();
    state.load(source, true);
    expect(state.isProtected).toBe(true);
    state.markDirty();
    expect(state.output(() => "replacement")).toBe(source);
  });

  it("resets loaded-byte state when the view is cleared for a new file", () => {
    const state = new InkPersistenceState();
    state.load("old", false);
    expect(state.isProtected).toBe(false);
    state.reset();
    expect(state.output(() => "new")).toBe("new");
  });
});
