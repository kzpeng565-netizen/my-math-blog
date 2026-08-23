/** Pure, versioned visual style stored on each committed stroke. */

export type Tool = "pen" | "highlighter";
export type PressureCurve = "linear" | "soft" | "medium" | "hard";

export interface PressureConfigV1 {
  enabled: boolean;
  inputMin: number;
  inputMax: number;
  outputMin: number;
  outputMax: number;
  curve: PressureCurve;
  gamma: number;
  /** Used when pressure is disabled, missing, or non-positive. */
  fallback: number;
}

export interface FreehandConfigV1 {
  thinning: number;
  smoothing: number;
  streamline: number;
  startTaper: number;
  endTaper: number;
}

export interface StrokeStyleSnapshotV1 {
  version: 1;
  color: string;
  size: number;
  opacity: number;
  tool: Tool;
  pressure: PressureConfigV1;
  freehand: FreehandConfigV1;
}

export const DEFAULT_PRESSURE_CONFIG: PressureConfigV1 = {
  enabled: true,
  inputMin: 0,
  inputMax: 1,
  outputMin: 0.2,
  outputMax: 1,
  curve: "medium",
  gamma: 1,
  fallback: 0.5,
};

export const DEFAULT_FREEHAND_CONFIG: FreehandConfigV1 = {
  thinning: 0.6,
  smoothing: 0.5,
  streamline: 0.5,
  startTaper: 0,
  endTaper: 0,
};

export function cloneStrokeStyle(style: StrokeStyleSnapshotV1): StrokeStyleSnapshotV1 {
  return {
    ...style,
    pressure: { ...style.pressure },
    freehand: { ...style.freehand },
  };
}

export function legacyStrokeStyle(
  color: string,
  size: number,
  tool: Tool,
  usePressure: boolean,
  highlighterAlpha: number,
): StrokeStyleSnapshotV1 {
  const pressure = {
    ...DEFAULT_PRESSURE_CONFIG,
    enabled: tool === "pen" && usePressure,
  };
  return {
    version: 1,
    color,
    size,
    opacity: tool === "highlighter" ? highlighterAlpha : 1,
    tool,
    pressure,
    freehand: {
      ...DEFAULT_FREEHAND_CONFIG,
      thinning: pressure.enabled ? 0.6 : 0,
    },
  };
}
