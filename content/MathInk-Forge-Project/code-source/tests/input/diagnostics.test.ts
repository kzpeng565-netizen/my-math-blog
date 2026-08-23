import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { defaultPenPresets } from "../../src/ink/presets";
import {
  InputDiagnosticsRecorder,
  inputFixtureBaseName,
  parseInputFixture,
  replayInputFixture,
  replayRawInputFixture,
  summarizeInput,
} from "../../src/input/diagnostics";

const fixtureDirectory = join(process.cwd(), "fixtures", "input");
const fixtureFiles = readdirSync(fixtureDirectory).filter((name) => name.endsWith(".json"));

describe("Input Lab fixture corpus", () => {
  it("contains at least eight versioned synthetic raw-input fixtures", () => {
    expect(fixtureFiles.length).toBeGreaterThanOrEqual(8);
    for (const file of fixtureFiles) {
      const fixture = parseInputFixture(readFileSync(join(fixtureDirectory, file), "utf8"));
      expect(fixture.schemaVersion).toBe(1);
      expect(fixture.metadata.synthetic).toBe(true);
    }
  });

  it("covers the eight required handwriting scenarios", () => {
    const names = fixtureFiles.map(
      (file) => parseInputFixture(readFileSync(join(fixtureDirectory, file), "utf8")).metadata.name,
    );
    for (const required of [
      "pressure-ramp",
      "heavy-to-light",
      "fast-flick",
      "slow-line",
      "circle",
      "integral-sign",
      "chinese-character-yong",
      "math-formula-integral-x2",
    ]) {
      expect(names).toContain(required);
    }
  });

  it("replays every fixture through the production input assembly path", () => {
    const style = defaultPenPresets()[0].style;
    for (const file of fixtureFiles) {
      const fixture = parseInputFixture(readFileSync(join(fixtureDirectory, file), "utf8"));
      const strokes = replayInputFixture(fixture, style);
      expect(strokes.length, file).toBeGreaterThanOrEqual(1);
      expect(strokes.flat().every(Number.isFinite), file).toBe(true);
    }
  });

  it("counts but never commits predicted samples", () => {
    const fixture = parseInputFixture(
      readFileSync(join(fixtureDirectory, "08-predicted-tail.json"), "utf8"),
    );
    expect(summarizeInput(fixture).predictedSampleCount).toBe(2);
    expect(summarizeInput(fixture)).toMatchObject({
      tiltXMin: 0,
      tiltXMax: 0,
      tiltYMin: 0,
      tiltYMax: 0,
      twistMin: 0,
      twistMax: 0,
    });
    const [stroke] = replayInputFixture(fixture, defaultPenPresets()[0].style);
    expect(stroke).toHaveLength(12); // down + 2 coalesced + final, three values each
    expect(replayRawInputFixture(fixture)[0].map((sample) => sample.x)).toEqual([10, 30, 50, 55]);
  });

  it("preserves a cancelled stroke's committed raw samples for diagnosis", () => {
    const fixture = parseInputFixture(
      readFileSync(join(fixtureDirectory, "06-cancel-salvage.json"), "utf8"),
    );
    expect(replayRawInputFixture(fixture)[0].length).toBeGreaterThan(1);
  });
});

describe("InputDiagnosticsRecorder", () => {
  it("creates a safe, non-empty fixture filename", () => {
    const fixture = parseInputFixture(readFileSync(join(fixtureDirectory, "05-dot.json"), "utf8"));
    fixture.metadata.name = "  Huawei / fast handwriting  ";
    expect(inputFixtureBaseName(fixture)).toBe("Huawei-fast-handwriting");
    fixture.metadata.name = "中文";
    expect(inputFixtureBaseName(fixture)).toBe("input-lab");
  });

  it("summarizes optional handler and dispatch timing without breaking legacy fixtures", () => {
    const fixture = parseInputFixture(readFileSync(join(fixtureDirectory, "05-dot.json"), "utf8"));
    expect(summarizeInput(fixture)).toMatchObject({
      processingMaxMs: 0,
      dispatchDelayMaxMs: 0,
    });
    fixture.records[0].handlerStartTimeStamp = fixture.records[0].timeStamp + 7;
    fixture.records[0].processingDurationMs = 3;
    expect(summarizeInput(fixture)).toMatchObject({
      processingP95Ms: 3,
      processingMaxMs: 3,
      dispatchDelayP95Ms: 7,
      dispatchDelayMaxMs: 7,
    });
  });

  it("isolates the exported fixture from later mutation", () => {
    const fixture = parseInputFixture(readFileSync(join(fixtureDirectory, "05-dot.json"), "utf8"));
    const recorder = new InputDiagnosticsRecorder();
    recorder.start({ ...fixture.metadata, capturedAt: fixture.metadata.capturedAt });
    recorder.record(fixture.records[0]);
    const exported = recorder.stop();
    fixture.records[0].sample.x = 999;
    expect(exported?.records[0].sample.x).toBe(40);
  });

  it("does not claim real pressure below the 50-pen-sample gate", () => {
    const fixture = parseInputFixture(
      readFileSync(join(fixtureDirectory, "03-pressure-ramp.json"), "utf8"),
    );
    for (const record of fixture.records) record.pointerType = "pen";
    expect(summarizeInput(fixture).pressureCapability).toBe("insufficient-samples");
  });

  it("marks 50 fixed-half pen samples as unproven pressure", () => {
    const fixture = parseInputFixture(
      readFileSync(join(fixtureDirectory, "03-pressure-ramp.json"), "utf8"),
    );
    for (const record of fixture.records) record.pointerType = "pen";
    const template = fixture.records[1];
    fixture.records = [
      fixture.records[0],
      ...Array.from({ length: 48 }, (_, index) => ({
        ...template,
        timeStamp: index + 1,
        sample: { ...template.sample, pressure: 0.5, timeStamp: index + 1 },
        coalescedSamples: [
          { ...template.sample, pressure: 0.5, timeStamp: index + 1, x: index + 1 },
        ],
      })),
      {
        ...fixture.records[2],
        timeStamp: 50,
        sample: { ...fixture.records[2].sample, pressure: 0.5 },
      },
    ];
    expect(summarizeInput(fixture).pressureCapability).toBe("unproven-fixed");
  });
});
