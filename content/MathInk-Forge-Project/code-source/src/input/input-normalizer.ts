import type { DiagnosticSample } from "./diagnostics";

export interface NormalizedPointerMove {
  /** Samples committed to stroke geometry. Always contains at least the parent event. */
  committed: DiagnosticSample[];
  /** Preview-only samples. Callers must never commit these to the document. */
  predicted: DiagnosticSample[];
}

/**
 * Convert one raw pointermove record into the samples used by the ink engine.
 * Browsers may return an empty coalesced list; in that case the parent event is
 * the sole committed sample. When coalesced samples exist the parent is not
 * appended, avoiding a duplicate tail point on Chromium/WebKit.
 */
export function normalizePointerMove(
  parent: DiagnosticSample,
  coalesced: readonly DiagnosticSample[],
  predicted: readonly DiagnosticSample[],
): NormalizedPointerMove {
  return {
    committed: coalesced.length > 0 ? [...coalesced] : [parent],
    predicted: [...predicted],
  };
}
