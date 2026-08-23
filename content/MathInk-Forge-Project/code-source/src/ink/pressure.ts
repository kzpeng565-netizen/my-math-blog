/** Pure pressure mapping and curve evaluation. */

import type { PressureConfigV1, PressureCurve } from "../model/stroke-style";

export function clamp01(value: number): number {
  if (!Number.isFinite(value)) return 0;
  return value < 0 ? 0 : value > 1 ? 1 : value;
}

export function applyPressureCurve(value: number, curve: PressureCurve): number {
  const x = clamp01(value);
  switch (curve) {
    case "soft":
      return 1 - (1 - x) * (1 - x);
    case "medium":
      return x * x * (3 - 2 * x);
    case "hard":
      return x * x;
    case "linear":
    default:
      return x;
  }
}

/** Map raw device pressure to the normalized pressure stored in a stroke. */
export function mapConfiguredPressure(raw: number, config: PressureConfigV1): number {
  if (!config.enabled || !Number.isFinite(raw) || raw <= 0) return clamp01(config.fallback);

  const inputSpan = config.inputMax - config.inputMin;
  if (!(inputSpan > 0)) return clamp01(config.fallback);
  const normalized = clamp01((raw - config.inputMin) / inputSpan);
  const curved = applyPressureCurve(normalized, config.curve);
  const gamma = Number.isFinite(config.gamma) && config.gamma > 0 ? config.gamma : 1;
  const shaped = Math.pow(curved, gamma);
  const outputMin = clamp01(config.outputMin);
  const outputMax = clamp01(config.outputMax);
  const low = Math.min(outputMin, outputMax);
  const high = Math.max(outputMin, outputMax);
  return low + shaped * (high - low);
}
