/** Versioned pen-preset model, defaults, validation, and import/export. */

import {
  DEFAULT_FREEHAND_CONFIG,
  DEFAULT_PRESSURE_CONFIG,
  type PressureConfigV1,
  type StrokeStyleSnapshotV1,
  type Tool,
  cloneStrokeStyle,
} from "../model/stroke-style";

export const PRESET_SCHEMA_VERSION = 1;

export interface PenPresetV1 {
  schemaVersion: 1;
  id: string;
  name: string;
  order: number;
  style: StrokeStyleSnapshotV1;
}

export interface PenPresetExportV1 {
  schemaVersion: 1;
  activePresetId: string;
  presets: PenPresetV1[];
}

function pressure(enabled: boolean, outputMin = 0.2, outputMax = 1): PressureConfigV1 {
  return {
    ...DEFAULT_PRESSURE_CONFIG,
    enabled,
    outputMin,
    outputMax,
  };
}

function preset(
  id: string,
  name: string,
  order: number,
  tool: Tool,
  color: string,
  size: number,
  opacity: number,
): PenPresetV1 {
  const pressureConfig = pressure(tool === "pen", tool === "pen" ? 0.35 : 0.5, 0.9);
  return {
    schemaVersion: PRESET_SCHEMA_VERSION,
    id,
    name,
    order,
    style: {
      version: 1,
      color,
      size,
      opacity,
      tool,
      pressure: pressureConfig,
      freehand: {
        ...DEFAULT_FREEHAND_CONFIG,
        thinning: tool === "pen" ? 0.3 : 0,
        smoothing: tool === "pen" ? 0.55 : 0.65,
        streamline: tool === "pen" ? 0.45 : 0.6,
      },
    },
  };
}

export const DEFAULT_PEN_PRESETS: readonly PenPresetV1[] = [
  preset("math-black", "Black formula", 0, "pen", "#1a1a1a", 3, 1),
  preset("body-blue", "Blue text", 1, "pen", "#1971c2", 3, 1),
  preset("review-red", "Red annotation", 2, "pen", "#e03131", 3, 1),
  preset("highlight-yellow", "Yellow highlight", 3, "highlighter", "#ffd43b", 12, 0.38),
  preset("highlight-green", "Green highlight", 4, "highlighter", "#69db7c", 12, 0.34),
];

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function finiteIn(value: unknown, min: number, max: number): value is number {
  return typeof value === "number" && Number.isFinite(value) && value >= min && value <= max;
}

function validColor(value: unknown): value is string {
  return typeof value === "string" && /^#[0-9a-f]{6}$/i.test(value);
}

function validTool(value: unknown): value is Tool {
  return value === "pen" || value === "highlighter";
}

export function validatePenPreset(value: unknown): string[] {
  const errors: string[] = [];
  if (!isRecord(value)) return ["Preset must be an object."];
  if (value.schemaVersion !== PRESET_SCHEMA_VERSION) errors.push("Unsupported preset schema.");
  if (typeof value.id !== "string" || !/^[a-z0-9][a-z0-9-]{0,63}$/i.test(value.id)) {
    errors.push("Preset id must contain only letters, numbers, and hyphens.");
  }
  if (typeof value.name !== "string" || value.name.trim().length < 1 || value.name.length > 64) {
    errors.push("Preset name must contain 1–64 characters.");
  }
  if (!finiteIn(value.order, 0, 10_000)) errors.push("Preset order is invalid.");
  const style = isRecord(value.style) ? value.style : null;
  if (!style) return [...errors, "Preset style is missing."];
  if (style.version !== 1) errors.push("Unsupported stroke-style version.");
  if (!validTool(style.tool)) errors.push("Tool must be pen or highlighter.");
  if (!validColor(style.color)) errors.push("Color must be a six-digit hex value.");
  if (!finiteIn(style.size, 0.25, 64)) errors.push("Size must be between 0.25 and 64.");
  if (!finiteIn(style.opacity, 0, 1)) errors.push("Opacity must be between 0 and 1.");

  const p = isRecord(style.pressure) ? style.pressure : null;
  if (!p) {
    errors.push("Pressure configuration is missing.");
  } else {
    if (typeof p.enabled !== "boolean") errors.push("Pressure enabled flag is invalid.");
    if (
      !finiteIn(p.inputMin, 0, 1) ||
      !finiteIn(p.inputMax, 0, 1) ||
      !(Number(p.inputMax) > Number(p.inputMin))
    ) {
      errors.push("Pressure input range must be increasing inside 0–1.");
    }
    if (!finiteIn(p.outputMin, 0, 1) || !finiteIn(p.outputMax, 0, 1)) {
      errors.push("Pressure output range must stay inside 0–1.");
    }
    if (!(
      p.curve === "linear" ||
      p.curve === "soft" ||
      p.curve === "medium" ||
      p.curve === "hard"
    )) {
      errors.push("Pressure curve is invalid.");
    }
    if (!finiteIn(p.gamma, 0.1, 5)) errors.push("Pressure gamma must be between 0.1 and 5.");
    if (!finiteIn(p.fallback, 0, 1)) errors.push("Fallback pressure must be between 0 and 1.");
  }

  const f = isRecord(style.freehand) ? style.freehand : null;
  if (!f) {
    errors.push("Freehand configuration is missing.");
  } else {
    if (!finiteIn(f.thinning, -1, 1)) errors.push("Thinning must be between -1 and 1.");
    if (!finiteIn(f.smoothing, 0, 1)) errors.push("Smoothing must be between 0 and 1.");
    if (!finiteIn(f.streamline, 0, 1)) errors.push("Streamline must be between 0 and 1.");
    if (!finiteIn(f.startTaper, 0, 512)) errors.push("Start taper must be between 0 and 512.");
    if (!finiteIn(f.endTaper, 0, 512)) errors.push("End taper must be between 0 and 512.");
  }
  return errors;
}

export function clonePreset(value: PenPresetV1): PenPresetV1 {
  return { ...value, style: cloneStrokeStyle(value.style) };
}

export function defaultPenPresets(): PenPresetV1[] {
  return DEFAULT_PEN_PRESETS.map(clonePreset);
}

export function uniquePresetId(base: string, used: ReadonlySet<string>): string {
  const clean =
    base
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "")
      .slice(0, 48) || "pen";
  if (!used.has(clean)) return clean;
  for (let i = 2; ; i++) {
    const candidate = `${clean}-${i}`;
    if (!used.has(candidate)) return candidate;
  }
}

export function normalizePresetList(value: unknown): PenPresetV1[] {
  if (!Array.isArray(value)) return defaultPenPresets();
  const valid = value
    .filter((candidate): candidate is PenPresetV1 => validatePenPreset(candidate).length === 0)
    .map(clonePreset)
    .sort((a, b) => a.order - b.order)
    .map((item, order) => ({ ...item, order }));
  return valid.length > 0 ? valid : defaultPenPresets();
}

export function exportPresetStore(presets: readonly PenPresetV1[], activePresetId: string): string {
  const payload: PenPresetExportV1 = {
    schemaVersion: PRESET_SCHEMA_VERSION,
    activePresetId,
    presets: presets.map(clonePreset),
  };
  return JSON.stringify(payload, null, 2);
}

export interface ImportedPresetStore {
  presets: PenPresetV1[];
  activePresetId: string;
}

export function importPresetStore(
  text: string,
  existing: readonly PenPresetV1[] = [],
): ImportedPresetStore {
  let raw: unknown;
  try {
    raw = JSON.parse(text);
  } catch {
    throw new Error("Preset file is not valid JSON.");
  }
  if (
    !isRecord(raw) ||
    raw.schemaVersion !== PRESET_SCHEMA_VERSION ||
    !Array.isArray(raw.presets)
  ) {
    throw new Error("Preset file has an unsupported schema.");
  }
  if (raw.presets.length === 0) throw new Error("Preset file contains no pens.");

  const used = new Set(existing.map((item) => item.id));
  const imported: PenPresetV1[] = [];
  const importedIdBySourceId = new Map<string, string>();
  for (const candidate of raw.presets) {
    const errors = validatePenPreset(candidate);
    if (errors.length > 0) throw new Error(errors.join(" "));
    const source = clonePreset(candidate as PenPresetV1);
    const nextId = uniquePresetId(source.id, used);
    used.add(nextId);
    if (!importedIdBySourceId.has(source.id)) importedIdBySourceId.set(source.id, nextId);
    imported.push({ ...source, id: nextId, order: existing.length + imported.length });
  }
  const requested = typeof raw.activePresetId === "string" ? raw.activePresetId : "";
  const active = importedIdBySourceId.get(requested) ?? imported[0].id;
  return { presets: imported, activePresetId: active };
}

export function styleForPreset(presetValue: PenPresetV1): StrokeStyleSnapshotV1 {
  return cloneStrokeStyle(presetValue.style);
}
