import { createHash } from "node:crypto";
import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { buildInkFile, parseInkFile } from "../../src/model/serialize";

const fixtureDirectory = join(process.cwd(), "fixtures", "legacy");
const files = readdirSync(fixtureDirectory).filter((name) => name.endsWith(".ink.md"));
const hash = (text: string): string => createHash("sha256").update(text).digest("hex");

describe("upstream v1 document fixtures", () => {
  it("includes at least five non-sensitive legacy notes", () => {
    expect(files.length).toBeGreaterThanOrEqual(5);
  });

  it("opens every fixture without mutating the source bytes", () => {
    for (const name of files) {
      const source = readFileSync(join(fixtureDirectory, name), "utf8");
      const before = hash(source);
      const parsed = parseInkFile(source);
      expect(parsed.doc, name).not.toBeNull();
      expect(hash(source), name).toBe(before);
      expect(parsed.doc?.regions.flatMap((region) => region.strokes).every((s) => !s.style)).toBe(
        true,
      );
    }
  });

  it("migrates only when explicitly rebuilt, then reopens with stable stroke data", () => {
    for (const name of files) {
      const source = readFileSync(join(fixtureDirectory, name), "utf8");
      const parsed = parseInkFile(source);
      if (!parsed.doc) throw new Error(`Unreadable fixture: ${name}`);
      const migrated = buildInkFile(parsed.body, parsed.doc);
      expect(migrated).toContain("\nv2:");
      const reopened = parseInkFile(migrated);
      expect(reopened.doc?.regions).toEqual(parsed.doc.regions);
    }
  });

  it("keeps migrated stroke data stable through ten encode/reopen cycles", () => {
    for (const name of files) {
      const source = readFileSync(join(fixtureDirectory, name), "utf8");
      const initial = parseInkFile(source);
      if (!initial.doc) throw new Error(`Unreadable fixture: ${name}`);
      const expectedRegions = initial.doc.regions;
      let current = buildInkFile(initial.body, initial.doc);

      for (let round = 1; round <= 10; round += 1) {
        const reopened = parseInkFile(current);
        expect(reopened.doc?.regions, `${name}, round ${round}`).toEqual(expectedRegions);
        if (!reopened.doc) throw new Error(`Failed to reopen ${name} on round ${round}`);
        current = buildInkFile(reopened.body, reopened.doc);
      }
    }
  });
});
