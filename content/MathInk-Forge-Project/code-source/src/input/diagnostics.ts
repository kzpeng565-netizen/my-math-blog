/** Pure capture, statistics, validation, and production-path replay for Input Lab. */

import { StrokeBuilder } from "../ink/stroke-builder";
import type { StrokeStyleSnapshotV1 } from "../model/stroke-style";
import { normalizePointerMove } from "./input-normalizer";

export const INPUT_FIXTURE_SCHEMA_VERSION = 1;

export interface DiagnosticSample {
  x: number;
  y: number;
  pressure: number;
  tiltX: number;
  tiltY: number;
  timeStamp: number;
  pointerType: string;
  pointerId: number;
  buttons: number;
  twist: number;
}

export type InputRecordType = "down" | "move" | "up" | "cancel";

export interface RawInputRecord {
  type: InputRecordType;
  pointerType: string;
  pointerId: number;
  pressure: number;
  coalesced: number;
  timeStamp: number;
  sample: DiagnosticSample;
  coalescedSamples: DiagnosticSample[];
  predictedSamples: DiagnosticSample[];
  coalescedApiAvailable: boolean;
  predictedApiAvailable: boolean;
  /** `performance.now()` when the handler started; optional for legacy fixtures. */
  handlerStartTimeStamp?: number;
  /** Work performed by the production pointer handler, excluding recorder cloning. */
  processingDurationMs?: number;
}

export interface InputFixtureMetadata {
  name: string;
  capturedAt: string;
  device: string;
  app: string;
  presetId: string;
  synthetic?: boolean;
  notes?: string;
  environment?: {
    deviceModel: string;
    stylus: string;
    operatingSystem: string;
    obsidianVersion: string;
    webViewVersion: string;
    userAgent: string;
  };
}

export interface InputFixture {
  schemaVersion: 1;
  metadata: InputFixtureMetadata;
  records: RawInputRecord[];
}

/** Filesystem-safe basename for a captured fixture (without `.json`). */
export function inputFixtureBaseName(fixture: InputFixture): string {
  const safeName = fixture.metadata.name.replace(/[^a-z0-9._-]+/gi, "-").replace(/^-|-$/g, "");
  return safeName || "input-lab";
}

export interface InputStats {
  eventCount: number;
  strokeCount: number;
  moveEventCount: number;
  committedSampleCount: number;
  predictedSampleCount: number;
  coalescedSampleCount: number;
  cancelCount: number;
  durationMs: number;
  maxMoveGapMs: number;
  medianMoveGapMs: number;
  p95MoveGapMs: number;
  longMoveGapCount: number;
  pressureMin: number;
  pressureMax: number;
  pressureMean: number;
  pressureVariance: number;
  pressureP05: number;
  pressureMedian: number;
  pressureP95: number;
  tiltXMin: number;
  tiltXMax: number;
  tiltYMin: number;
  tiltYMax: number;
  twistMin: number;
  twistMax: number;
  pressureCapability: "variable" | "unproven-fixed" | "insufficient-samples" | "non-pen";
  coalescedApiAvailable: boolean;
  predictedApiAvailable: boolean;
  pointerTypes: string[];
  processingP95Ms: number;
  processingMaxMs: number;
  dispatchDelayP95Ms: number;
  dispatchDelayMaxMs: number;
}

export class InputDiagnosticsRecorder {
  private records: RawInputRecord[] = [];
  private metadata: InputFixtureMetadata | null = null;

  get active(): boolean {
    return this.metadata !== null;
  }

  start(metadata: Omit<InputFixtureMetadata, "capturedAt"> & { capturedAt?: string }): void {
    this.records = [];
    this.metadata = {
      ...metadata,
      capturedAt: metadata.capturedAt ?? new Date().toISOString(),
    };
  }

  record(record: RawInputRecord): void {
    if (!this.metadata) return;
    this.records.push(cloneRecord(record));
  }

  stop(): InputFixture | null {
    if (!this.metadata) return null;
    const fixture: InputFixture = {
      schemaVersion: INPUT_FIXTURE_SCHEMA_VERSION,
      metadata: { ...this.metadata },
      records: this.records.map(cloneRecord),
    };
    this.metadata = null;
    this.records = [];
    return fixture;
  }
}

function cloneSample(sample: DiagnosticSample): DiagnosticSample {
  return { ...sample };
}

function cloneRecord(record: RawInputRecord): RawInputRecord {
  return {
    ...record,
    sample: cloneSample(record.sample),
    coalescedSamples: record.coalescedSamples.map(cloneSample),
    predictedSamples: record.predictedSamples.map(cloneSample),
  };
}

function percentile(values: number[], quantile: number): number {
  if (values.length === 0) return 0;
  const sorted = values.slice().sort((a, b) => a - b);
  return sorted[Math.min(sorted.length - 1, Math.ceil(sorted.length * quantile) - 1)];
}

export function summarizeInput(fixture: InputFixture): InputStats {
  const moveRecords = fixture.records.filter((record) => record.type === "move");
  const committed = fixture.records.flatMap((record) =>
    record.type === "move"
      ? normalizePointerMove(record.sample, record.coalescedSamples, record.predictedSamples)
          .committed
      : record.type === "cancel"
        ? []
        : [record.sample],
  );
  const gaps: number[] = [];
  for (let index = 1; index < moveRecords.length; index++) {
    gaps.push(Math.max(0, moveRecords[index].timeStamp - moveRecords[index - 1].timeStamp));
  }
  const pressures = committed.map((sample) => sample.pressure);
  const tiltX = committed.map((sample) => sample.tiltX);
  const tiltY = committed.map((sample) => sample.tiltY);
  const twists = committed.map((sample) => sample.twist);
  const first = fixture.records[0]?.timeStamp ?? 0;
  const last = fixture.records[fixture.records.length - 1]?.timeStamp ?? first;
  const pressureMean = pressures.length
    ? pressures.reduce((sum, value) => sum + value, 0) / pressures.length
    : 0;
  const pressureVariance = pressures.length
    ? pressures.reduce((sum, value) => sum + (value - pressureMean) ** 2, 0) / pressures.length
    : 0;
  const hasPen = fixture.records.some((record) => record.pointerType === "pen");
  const pressureRange = pressures.length ? Math.max(...pressures) - Math.min(...pressures) : 0;
  const fixedHalfRatio = pressures.length
    ? pressures.filter((value) => Math.abs(value - 0.5) < 0.001).length / pressures.length
    : 0;
  const processingDurations = fixture.records
    .map((record) => record.processingDurationMs)
    .filter((value): value is number => typeof value === "number" && Number.isFinite(value));
  // PointerEvent.timeStamp and performance.now() share the same time origin in
  // modern WebViews. Ignore implausible values from older epoch-based engines.
  const dispatchDelays = fixture.records
    .map((record) =>
      typeof record.handlerStartTimeStamp === "number"
        ? record.handlerStartTimeStamp - record.timeStamp
        : NaN,
    )
    .filter((value) => Number.isFinite(value) && value >= 0 && value < 60_000);
  const pressureCapability = !hasPen
    ? "non-pen"
    : pressures.length < 50
      ? "insufficient-samples"
      : pressureRange < 0.05 || fixedHalfRatio >= 0.9
        ? "unproven-fixed"
        : "variable";
  return {
    eventCount: fixture.records.length,
    strokeCount: fixture.records.filter((record) => record.type === "down").length,
    moveEventCount: moveRecords.length,
    committedSampleCount: committed.length,
    predictedSampleCount: fixture.records.reduce(
      (sum, record) => sum + record.predictedSamples.length,
      0,
    ),
    coalescedSampleCount: moveRecords.reduce(
      (sum, record) => sum + record.coalescedSamples.length,
      0,
    ),
    cancelCount: fixture.records.filter((record) => record.type === "cancel").length,
    durationMs: Math.max(0, last - first),
    maxMoveGapMs: gaps.length ? Math.max(...gaps) : 0,
    medianMoveGapMs: percentile(gaps, 0.5),
    p95MoveGapMs: percentile(gaps, 0.95),
    longMoveGapCount: gaps.filter((gap) => gap > 32).length,
    pressureMin: pressures.length ? Math.min(...pressures) : 0,
    pressureMax: pressures.length ? Math.max(...pressures) : 0,
    pressureMean,
    pressureVariance,
    pressureP05: percentile(pressures, 0.05),
    pressureMedian: percentile(pressures, 0.5),
    pressureP95: percentile(pressures, 0.95),
    tiltXMin: tiltX.length ? Math.min(...tiltX) : 0,
    tiltXMax: tiltX.length ? Math.max(...tiltX) : 0,
    tiltYMin: tiltY.length ? Math.min(...tiltY) : 0,
    tiltYMax: tiltY.length ? Math.max(...tiltY) : 0,
    twistMin: twists.length ? Math.min(...twists) : 0,
    twistMax: twists.length ? Math.max(...twists) : 0,
    pressureCapability,
    coalescedApiAvailable: fixture.records.some((record) => record.coalescedApiAvailable),
    predictedApiAvailable: fixture.records.some((record) => record.predictedApiAvailable),
    pointerTypes: [...new Set(fixture.records.map((record) => record.pointerType))].sort(),
    processingP95Ms: percentile(processingDurations, 0.95),
    processingMaxMs: processingDurations.length ? Math.max(...processingDurations) : 0,
    dispatchDelayP95Ms: percentile(dispatchDelays, 0.95),
    dispatchDelayMaxMs: dispatchDelays.length ? Math.max(...dispatchDelays) : 0,
  };
}

export function parseInputFixture(text: string): InputFixture {
  const raw: unknown = JSON.parse(text);
  if (!isRecord(raw) || raw.schemaVersion !== INPUT_FIXTURE_SCHEMA_VERSION) {
    throw new Error("Unsupported Input Lab fixture schema.");
  }
  if (!isRecord(raw.metadata) || !Array.isArray(raw.records)) {
    throw new Error("Input Lab fixture is missing metadata or records.");
  }
  const metadata = raw.metadata;
  for (const key of ["name", "capturedAt", "device", "app", "presetId"] as const) {
    if (typeof metadata[key] !== "string") throw new Error(`Invalid fixture metadata: ${key}.`);
  }
  const records = raw.records.map((value, index) => normalizeRecord(value, index));
  return {
    schemaVersion: INPUT_FIXTURE_SCHEMA_VERSION,
    metadata: {
      name: metadata.name as string,
      capturedAt: metadata.capturedAt as string,
      device: metadata.device as string,
      app: metadata.app as string,
      presetId: metadata.presetId as string,
      ...(typeof metadata.synthetic === "boolean" ? { synthetic: metadata.synthetic } : {}),
      ...(typeof metadata.notes === "string" ? { notes: metadata.notes } : {}),
      ...(isRecord(metadata.environment)
        ? {
            environment: {
              deviceModel:
                typeof metadata.environment.deviceModel === "string"
                  ? metadata.environment.deviceModel
                  : "",
              stylus:
                typeof metadata.environment.stylus === "string" ? metadata.environment.stylus : "",
              operatingSystem:
                typeof metadata.environment.operatingSystem === "string"
                  ? metadata.environment.operatingSystem
                  : "",
              obsidianVersion:
                typeof metadata.environment.obsidianVersion === "string"
                  ? metadata.environment.obsidianVersion
                  : "",
              webViewVersion:
                typeof metadata.environment.webViewVersion === "string"
                  ? metadata.environment.webViewVersion
                  : "",
              userAgent:
                typeof metadata.environment.userAgent === "string"
                  ? metadata.environment.userAgent
                  : "",
            },
          }
        : {}),
    },
    records,
  };
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function finite(value: unknown): value is number {
  return typeof value === "number" && Number.isFinite(value);
}

function normalizeSample(value: unknown, label: string): DiagnosticSample {
  if (!isRecord(value)) throw new Error(`Invalid ${label} sample.`);
  for (const key of ["x", "y", "pressure", "tiltX", "tiltY", "timeStamp"] as const) {
    if (!finite(value[key])) throw new Error(`Invalid ${label} sample field: ${key}.`);
  }
  return {
    x: value.x as number,
    y: value.y as number,
    pressure: value.pressure as number,
    tiltX: value.tiltX as number,
    tiltY: value.tiltY as number,
    timeStamp: value.timeStamp as number,
    pointerType: typeof value.pointerType === "string" ? value.pointerType : "unknown",
    pointerId: finite(value.pointerId) ? value.pointerId : 0,
    buttons: finite(value.buttons) ? value.buttons : 0,
    twist: finite(value.twist) ? value.twist : 0,
  };
}

function normalizeRecord(value: unknown, index: number): RawInputRecord {
  if (!isRecord(value) || !["down", "move", "up", "cancel"].includes(String(value.type))) {
    throw new Error(`Invalid input record at index ${index}.`);
  }
  const sample = normalizeSample(value.sample, `record ${index}`);
  const coalescedSamples = Array.isArray(value.coalescedSamples)
    ? value.coalescedSamples.map((item) => normalizeSample(item, `record ${index} coalesced`))
    : [];
  const predictedSamples = Array.isArray(value.predictedSamples)
    ? value.predictedSamples.map((item) => normalizeSample(item, `record ${index} predicted`))
    : [];
  return {
    type: value.type as InputRecordType,
    pointerType: typeof value.pointerType === "string" ? value.pointerType : sample.pointerType,
    pointerId: finite(value.pointerId) ? value.pointerId : sample.pointerId,
    pressure: finite(value.pressure) ? value.pressure : sample.pressure,
    coalesced: coalescedSamples.length,
    timeStamp: finite(value.timeStamp) ? value.timeStamp : sample.timeStamp,
    sample,
    coalescedSamples,
    predictedSamples,
    coalescedApiAvailable:
      typeof value.coalescedApiAvailable === "boolean" ? value.coalescedApiAvailable : false,
    predictedApiAvailable:
      typeof value.predictedApiAvailable === "boolean" ? value.predictedApiAvailable : false,
    ...(finite(value.handlerStartTimeStamp)
      ? { handlerStartTimeStamp: value.handlerStartTimeStamp }
      : {}),
    ...(finite(value.processingDurationMs)
      ? { processingDurationMs: value.processingDurationMs }
      : {}),
  };
}

/** Replay committed samples through the same StrokeBuilder and pressure mapping as live ink. */
export function replayInputFixture(
  fixture: InputFixture,
  style: StrokeStyleSnapshotV1,
  minDistance = 0.35,
): number[][] {
  const strokes: number[][] = [];
  let builder: StrokeBuilder | null = null;
  for (const record of fixture.records) {
    if (record.type === "down") {
      if (builder && !builder.isEmpty) strokes.push(builder.points());
      builder = new StrokeBuilder({
        minDistance,
        pressureEnabled: style.pressure.enabled,
        fallbackPressure: style.pressure.fallback,
        pressureConfig: style.pressure,
      });
      builder.add(record.sample);
    } else if (record.type === "move" && builder) {
      const normalized = normalizePointerMove(
        record.sample,
        record.coalescedSamples,
        record.predictedSamples,
      );
      for (const sample of normalized.committed) builder.add(sample);
    } else if (record.type === "up" && builder) {
      builder.addFinal(record.sample);
      if (!builder.isEmpty) strokes.push(builder.points());
      builder = null;
    } else if (record.type === "cancel" && builder) {
      if (!builder.isEmpty) strokes.push(builder.points());
      builder = null;
    }
  }
  if (builder && !builder.isEmpty) strokes.push(builder.points());
  return strokes;
}

/**
 * Assemble the committed raw samples into stroke groups for visual inspection.
 * This uses the same normalization rule as live drawing and production replay,
 * but intentionally stops before pressure mapping and brush geometry.
 */
export function replayRawInputFixture(fixture: InputFixture): DiagnosticSample[][] {
  const strokes: DiagnosticSample[][] = [];
  let current: DiagnosticSample[] | null = null;
  for (const record of fixture.records) {
    if (record.type === "down") {
      if (current?.length) strokes.push(current);
      current = [record.sample];
    } else if (record.type === "move" && current) {
      current.push(
        ...normalizePointerMove(record.sample, record.coalescedSamples, record.predictedSamples)
          .committed,
      );
    } else if (record.type === "up" && current) {
      current.push(record.sample);
      strokes.push(current);
      current = null;
    } else if (record.type === "cancel" && current) {
      strokes.push(current);
      current = null;
    }
  }
  if (current?.length) strokes.push(current);
  return strokes;
}
