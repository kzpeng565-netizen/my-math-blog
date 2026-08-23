import { createHash } from "node:crypto";
import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { optionsForStrokeStyle, outlineToSvgPath, strokeOutline } from "../../src/ink/freehand";
import { defaultPenPresets } from "../../src/ink/presets";
import { parseInputFixture, replayInputFixture } from "../../src/input/diagnostics";

const inputDirectory = join(process.cwd(), "fixtures", "input");
const baselinePath = join(process.cwd(), "fixtures", "baselines", "geometry-v1.sha256.json");

describe("Desktop Replay geometry baseline", () => {
  it("matches the committed v1 SHA-256 snapshot for every synthetic fixture", () => {
    const presets = defaultPenPresets();
    const actual: Record<string, string> = {};
    for (const file of readdirSync(inputDirectory)
      .filter((name) => name.endsWith(".json"))
      .sort()) {
      const fixture = parseInputFixture(readFileSync(join(inputDirectory, file), "utf8"));
      const preset = presets.find((item) => item.id === fixture.metadata.presetId) ?? presets[0];
      const geometry = replayInputFixture(fixture, preset.style)
        .map((points) =>
          outlineToSvgPath(strokeOutline(points, optionsForStrokeStyle(preset.style), true)),
        )
        .join("\n");
      actual[file] = createHash("sha256").update(geometry).digest("hex");
    }

    const expected = JSON.parse(readFileSync(baselinePath, "utf8")) as Record<string, string>;
    expect(actual).toEqual(expected);
  });
});
