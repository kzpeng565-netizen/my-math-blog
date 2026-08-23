/**
 * The interactive drawing engine, shared by the ink note view (`InkView`) and
 * the inline-block editor modal (`InlineInkModal`).
 *
 * Owns the paper-roll surface DOM, the dry/wet canvases, pointer input, tools
 * (pen / highlighter / eraser / select), zoom, undo/redo, and the diagnostic
 * HUD. It knows nothing about files, the text layer, or recognition: hosts
 * subscribe to `onChange` and persist the document however they like.
 *
 * Layout (all inside the host element):
 *
 *   .inkedmark-surface          position:relative, clips
 *     .inkedmark-paper-bg       visible page behind the ink
 *     canvas.dry                pinned to the visible viewport
 *     canvas.wet                pinned to the visible viewport
 *     .inkedmark-scroll         transparent overlay; owns scrolling + input
 *       .inkedmark-paper        spacer that defines the scroll range
 *     .inkedmark-hud            pointer diagnostics (debug only)
 *
 * The canvases are viewport-sized and redrawn on scroll (dry) / per-sample
 * (wet); the scroll overlay provides native scrolling and receives pointer
 * input. World coordinates are derived from the paper spacer's rect, which
 * already folds in both scroll position and horizontal centering.
 */

import {
  DEFAULT_PAPER_HEIGHT,
  ERASER_RADIUS,
  FALLBACK_PRESSURE,
  MIN_SAMPLE_DISTANCE,
  PAPER_GROWTH_MARGIN,
} from "../constants";
import { Renderer, type StrokeStyle } from "../canvas/renderer";
import type { ViewportState } from "../canvas/viewport";
import {
  pointInBounds,
  rectFromCorners,
  strokeHitByPoint,
  strokeIntersectsRect,
} from "../canvas/hit-test";
import { SpatialIndex } from "../canvas/spatial-index";
import { anchorScrollDelta, clampScale } from "../canvas/zoom";
import { StrokeBuilder, type StrokeBuilderOptions, mapPressure } from "../ink/stroke-builder";
import {
  type Bounds,
  type InkDocument,
  type Stroke,
  type Tool,
  documentBounds,
  primaryRegion,
  strokeBounds,
  strokeCount,
} from "../model/document";
import { type StrokeStyleSnapshotV1, cloneStrokeStyle } from "../model/stroke-style";
import { AddStroke, ClearRegion, MoveStrokes, RemoveStrokes } from "../model/commands";
import { History } from "../model/history";
import {
  PointerController,
  type PointerControllerCallbacks,
  type PointerDebugRecord,
  type PointerSample,
} from "../input/pointer-controller";
import {
  InputDiagnosticsRecorder,
  type InputFixture,
  type InputFixtureMetadata,
} from "../input/diagnostics";
import { normalizePointerMove } from "../input/input-normalizer";
import type { ActiveTool, ToolbarState } from "./toolbar";

const MAX_DPR = 3;

export interface InkSurfaceOptions {
  /** Logical paper width in CSS px (the roll fits the surface at scale 1). */
  paperWidth: number;
  /** Request a `desynchronized` 2D context for the wet layer. */
  desynchronizedCanvas: boolean;
  highlighterAlpha: number;
  darkTheme: boolean;
  /** Show the pointer-diagnostics HUD. */
  debug: boolean;
}

export interface InkSurfaceCallbacks {
  /** The document was mutated (stroke added/removed/moved, cleared, undo/redo). */
  onChange(): void;
  /** Something the host may display changed (stroke count, zoom). */
  onStatus?(): void;
  /** Return true to refuse pen input (e.g. the host note is protected). */
  isLocked?(): boolean;
  /** The surface switched tools via keyboard; hosts sync their toolbar. */
  onToolChange?(tool: ActiveTool): void;
}

function padBounds(b: Bounds, pad: number): Bounds {
  return { minX: b.minX - pad, minY: b.minY - pad, maxX: b.maxX + pad, maxY: b.maxY + pad };
}

/**
 * Highest numeric `s<N>` id in the document. Seeding the sequence from the max
 * (not the count) prevents duplicate ids after erases: a file holding s1..s10
 * with two erased has 8 strokes, and counting would mint "s9" — which exists.
 */
export function maxStrokeId(doc: InkDocument): number {
  let max = 0;
  for (const region of doc.regions) {
    for (const stroke of region.strokes) {
      const m = /^s(\d+)$/.exec(stroke.id);
      if (m) max = Math.max(max, Number(m[1]));
    }
  }
  return max;
}

export class InkSurface {
  readonly surfaceEl: HTMLElement;
  private readonly paperBgEl: HTMLElement;
  private readonly scrollEl: HTMLElement;
  private readonly paperEl: HTMLElement;
  private readonly hudEl: HTMLElement;

  private doc: InkDocument;
  private renderer: Renderer | null;
  private pointer: PointerController | null;
  private resizeObserver: ResizeObserver | null;
  private readonly disposers: Array<() => void> = [];
  private dryFrame = 0;

  private viewport: ViewportState = { scrollY: 0, scale: 1, width: 0 };
  private offsetX = 0;
  private paperWorldWidth = 0;
  private paperWorldHeight = DEFAULT_PAPER_HEIGHT;
  private scale = 1;

  private builder: StrokeBuilder | null = null;
  /** Style captured at pointer-down so mid-stroke UI changes cannot alter it. */
  private activeStrokeStyle: StrokeStyleSnapshotV1 | null = null;
  private strokeSeq = 0;
  private readonly history = new History();
  private readonly index = new SpatialIndex();
  /** id -> stroke, so index hits resolve in O(1) instead of scanning the region. */
  private readonly strokeById = new Map<string, Stroke>();
  private eraseIds = new Set<string>();

  // Selection / move state (select tool).
  private selection = new Set<string>();
  private selectMode: "none" | "marquee" | "move" = "none";
  private marquee: Bounds | null = null;
  private marqueeOrigin: { x: number; y: number } | null = null;
  private moveLast: { x: number; y: number } | null = null;
  private moveDx = 0;
  private moveDy = 0;

  // Wet-render throttle: coalesce many pointermoves into one draw per frame.
  private wetFrame = 0;
  private pendingPredicted: PointerSample[] = [];

  // Bounded retry for layout() when the host has no size yet (first open).
  private layoutRetries = 0;

  // Diagnostic HUD state.
  private debug: boolean;
  private hudLog: Array<{ k: string; n: number }> = [];
  private hudMoves = 0;
  private hudPts = 0;
  private hudMaxGap = 0;
  private hudLastMoveT = 0;
  private hudPressure = 0;
  private hudMaxP = 0;
  private hudPointerType = "";
  private hudPointerId = 0;
  private hudButtons = 0;
  private hudX = 0;
  private hudY = 0;
  private hudTimeStamp = 0;
  private hudTiltX = 0;
  private hudTiltY = 0;
  private hudTwist = 0;
  private hudEventType = "";
  private hudPredicted = 0;
  private hudCoalescedApi = false;
  private hudPredictedApi = false;
  private hudLongGaps = 0;
  private hudSampleCount = 0;
  private hudPressureMin = Infinity;
  private hudPressureSum = 0;
  private hudPressureSumSquares = 0;
  private hudTimer = 0;
  private hudSumDown = 0;
  private hudSumUp = 0;
  private hudSumCancel = 0;
  private readonly inputRecorder = new InputDiagnosticsRecorder();
  private debugBeforeRecording = false;

  /**
   * @param host      element the surface is appended to (a flex column host
   *                  lets `.inkedmark-surface` fill the remaining height)
   * @param toolState shared with the host's Toolbar: the toolbar mutates it in
   *                  place and the surface reads it at gesture time
   */
  constructor(
    host: HTMLElement,
    doc: InkDocument,
    private readonly toolState: ToolbarState,
    private readonly options: InkSurfaceOptions,
    private readonly callbacks: InkSurfaceCallbacks,
  ) {
    this.doc = doc;
    this.debug = options.debug;

    this.surfaceEl = host.createDiv({ cls: "inkedmark-surface" });
    this.paperBgEl = this.surfaceEl.createDiv({ cls: "inkedmark-paper-bg" });
    const dryCanvas = this.surfaceEl.createEl("canvas", {
      cls: "inkedmark-canvas inkedmark-canvas-dry",
    });
    const wetCanvas = this.surfaceEl.createEl("canvas", {
      cls: "inkedmark-canvas inkedmark-canvas-wet",
    });
    this.scrollEl = this.surfaceEl.createDiv({ cls: "inkedmark-scroll" });
    this.paperEl = this.scrollEl.createDiv({ cls: "inkedmark-paper" });
    this.hudEl = this.surfaceEl.createDiv({ cls: "inkedmark-hud" });
    this.hudEl.style.display = this.debug ? "" : "none";

    this.renderer = new Renderer(dryCanvas, wetCanvas, options.desynchronizedCanvas);
    this.renderer.highlighterAlpha = options.highlighterAlpha;
    this.renderer.darkTheme = options.darkTheme;

    this.pointer = new PointerController(
      this.scrollEl,
      (cx, cy) => this.toWorld(cx, cy),
      this.pointerCallbacks,
    );
    this.pointer.attach();

    const onScroll = (): void => this.onScroll();
    this.scrollEl.addEventListener("scroll", onScroll);
    this.disposers.push(() => this.scrollEl.removeEventListener("scroll", onScroll));

    this.resizeObserver = new ResizeObserver(() => this.layout());
    this.resizeObserver.observe(this.surfaceEl);

    this.setDocument(doc);
  }

  /** Release listeners, observers and pending frames. The DOM is left to the host. */
  destroy(): void {
    if (this.dryFrame) window.cancelAnimationFrame(this.dryFrame);
    if (this.hudTimer) window.clearTimeout(this.hudTimer);
    if (this.wetFrame) window.cancelAnimationFrame(this.wetFrame);
    this.dryFrame = this.hudTimer = this.wetFrame = 0;
    this.pointer?.detach();
    this.pointer = null;
    this.resizeObserver?.disconnect();
    this.resizeObserver = null;
    for (const dispose of this.disposers.splice(0)) dispose();
    this.renderer = null;
  }

  // --- Document -------------------------------------------------------------

  /** Replace the edited document (history is reset). The surface mutates `doc` in place. */
  setDocument(doc: InkDocument): void {
    this.doc = doc;
    this.strokeSeq = maxStrokeId(doc);
    this.history.clear();
    this.selection = new Set();
    this.eraseIds = new Set();
    this.rebuildIndex();
    this.layout();
    this.callbacks.onStatus?.();
  }

  get document(): InkDocument {
    return this.doc;
  }

  get zoom(): number {
    return this.scale;
  }

  strokeCount(): number {
    return strokeCount(this.doc);
  }

  private rebuildIndex(): void {
    const strokes = primaryRegion(this.doc).strokes;
    this.index.rebuild(strokes);
    this.strokeById.clear();
    for (const stroke of strokes) this.strokeById.set(stroke.id, stroke);
  }

  private changed(): void {
    this.callbacks.onStatus?.();
    this.callbacks.onChange();
  }

  // --- Host-facing controls -------------------------------------------------

  setDarkTheme(dark: boolean): void {
    if (!this.renderer) return;
    this.renderer.darkTheme = dark;
    this.renderDry();
  }

  /** Reset zoom to 1 and scroll back to the top ("fit / reset"). */
  resetView(): void {
    this.scale = 1;
    this.scrollEl.scrollTo({ top: 0, left: 0 });
    this.layout();
    this.callbacks.onStatus?.();
  }

  zoomIn(): void {
    this.zoomBy(1.25);
  }

  zoomOut(): void {
    this.zoomBy(1 / 1.25);
  }

  setTool(tool: ActiveTool): void {
    this.toolState.tool = tool;
    if (tool !== "select") this.clearSelection();
  }

  /** Enable/disable the on-screen pointer-event overlay (also resets counters). */
  setDebug(enabled: boolean): void {
    this.debug = enabled;
    if (enabled) {
      this.hudLog = [];
      this.hudSumDown = 0;
      this.hudSumUp = 0;
      this.hudSumCancel = 0;
      this.hudMoves = 0;
      this.hudPts = 0;
      this.hudPredicted = 0;
      this.hudMaxGap = 0;
      this.hudLastMoveT = 0;
      this.hudMaxP = 0;
      this.hudLongGaps = 0;
      this.hudSampleCount = 0;
      this.hudPressureMin = Infinity;
      this.hudPressureSum = 0;
      this.hudPressureSumSquares = 0;
      this.hudCoalescedApi = false;
      this.hudPredictedApi = false;
    }
    if (!enabled && this.hudTimer) {
      window.clearTimeout(this.hudTimer);
      this.hudTimer = 0;
    }
    this.hudEl.style.display = enabled ? "" : "none";
    if (enabled) this.renderHud();
  }

  /**
   * Keyboard shortcuts (undo/redo, delete selection, tool letters). Returns
   * true when the event was consumed. Hosts decide which element listens.
   */
  handleKeyDown(event: KeyboardEvent): boolean {
    const target = event.target as HTMLElement | null;
    if (target && (target.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(target.tagName))) {
      return false;
    }

    const mod = event.metaKey || event.ctrlKey;
    if (mod && event.key.toLowerCase() === "z") {
      event.preventDefault();
      if (event.shiftKey) this.redo();
      else this.undo();
      return true;
    }

    if ((event.key === "Delete" || event.key === "Backspace") && this.selection.size > 0) {
      event.preventDefault();
      this.deleteSelection();
      return true;
    }

    const tool = ({ p: "pen", h: "highlighter", e: "eraser", v: "select" } as const)[
      event.key.toLowerCase()
    ];
    if (!tool || mod || event.altKey) return false;
    this.setTool(tool);
    this.callbacks.onToolChange?.(tool);
    return true;
  }

  // --- Layout / rendering ---------------------------------------------------

  layout(): void {
    if (!this.renderer) return;
    const cssW = this.surfaceEl.clientWidth;
    const cssH = this.surfaceEl.clientHeight;
    if (cssW === 0 || cssH === 0) {
      // First-open race: the host may not be attached/measured yet (a blank
      // canvas until something re-triggers layout). Retry briefly; the
      // ResizeObserver covers anything slower than this.
      if (this.layoutRetries < 60) {
        this.layoutRetries++;
        window.requestAnimationFrame(() => this.layout());
      }
      return;
    }
    this.layoutRetries = 0;

    // The roll's world width fits the surface at scale 1; zoom scales the visuals.
    this.paperWorldWidth = Math.min(this.options.paperWidth, cssW);
    this.ensurePaperSize();

    const dpr = Math.min(window.devicePixelRatio || 1, MAX_DPR);
    this.renderer.resize(cssW, cssH, dpr);
    this.syncViewport();
    this.renderDry();
  }

  /** Size the paper spacer (scroll range) in scaled/screen px. */
  private ensurePaperSize(): void {
    const bounds = documentBounds(this.doc);
    const contentBottom = bounds ? bounds.maxY + PAPER_GROWTH_MARGIN : 0;
    const surfaceH = this.surfaceEl.clientHeight;
    this.paperWorldHeight = Math.max(DEFAULT_PAPER_HEIGHT, contentBottom, surfaceH / this.scale);
    this.paperEl.setCssStyles({
      width: `${Math.ceil(this.paperWorldWidth * this.scale)}px`,
      height: `${Math.ceil(this.paperWorldHeight * this.scale)}px`,
    });
  }

  /**
   * Pen-up hot path: grow from only the new stroke. Re-scanning every point in
   * the document and forcing layout after each short stroke caused increasing
   * inter-stroke stalls on tablets.
   */
  private growPaperForStroke(stroke: Stroke): void {
    const bounds = strokeBounds(stroke);
    if (!bounds) return;
    const requiredHeight = bounds.maxY + PAPER_GROWTH_MARGIN;
    if (requiredHeight <= this.paperWorldHeight) return;
    this.paperWorldHeight = requiredHeight;
    this.paperEl.style.height = `${Math.ceil(this.paperWorldHeight * this.scale)}px`;
  }

  /** Derive scroll/offset (world) from the live paper vs surface rects. */
  private syncViewport(): void {
    if (!this.renderer) return;
    const surf = this.surfaceEl.getBoundingClientRect();
    const paper = this.paperEl.getBoundingClientRect();
    this.offsetX = paper.left - surf.left;
    const scrollY = (surf.top - paper.top) / this.scale;
    this.viewport = { scrollY, scale: this.scale, width: this.paperWorldWidth };
    this.renderer.setViewport(this.viewport, this.offsetX);
    this.paperBgEl.style.left = `${this.offsetX}px`;
    this.paperBgEl.style.width = `${paper.width}px`;
  }

  private onScroll(): void {
    this.syncViewport();
    this.scheduleDry();
  }

  /** Zoom about a client-space anchor, keeping the world point under it fixed. */
  private applyZoom(nextScale: number, anchorX: number, anchorY: number): void {
    const before = this.toWorld(anchorX, anchorY);
    this.scale = clampScale(nextScale);
    this.ensurePaperSize();
    this.syncViewport();
    const after = this.toWorld(anchorX, anchorY);
    const delta = anchorScrollDelta(before, after, this.scale);
    this.scrollEl.scrollLeft += delta.x;
    this.scrollEl.scrollTop += delta.y;
    this.syncViewport();
    this.renderDry();
    this.callbacks.onStatus?.();
  }

  private zoomBy(factor: number): void {
    const rect = this.surfaceEl.getBoundingClientRect();
    this.applyZoom(this.scale * factor, rect.left + rect.width / 2, rect.top + rect.height / 2);
  }

  private scheduleDry(): void {
    if (this.dryFrame) return;
    this.dryFrame = window.requestAnimationFrame(() => {
      this.dryFrame = 0;
      this.renderDry();
    });
  }

  private renderDry(): void {
    // `eraseIds` is empty except during a live erase gesture (preview).
    this.renderer?.renderDocument(
      this.doc,
      this.toolState.pressureEnabled,
      this.eraseIds,
      this.selectionBounds(),
    );
  }

  private selectionBounds(): Bounds | null {
    if (this.selection.size === 0) return null;
    let acc: Bounds | null = null;
    for (const id of this.selection) {
      const stroke = this.strokeById.get(id);
      if (!stroke) continue;
      const b = strokeBounds(stroke);
      if (!b) continue;
      acc = acc
        ? {
            minX: Math.min(acc.minX, b.minX),
            minY: Math.min(acc.minY, b.minY),
            maxX: Math.max(acc.maxX, b.maxX),
            maxY: Math.max(acc.maxY, b.maxY),
          }
        : b;
    }
    return acc;
  }

  /** The drawing tool for a produced stroke (eraser/select never produce one). */
  private strokeTool(): Tool {
    return this.toolState.tool === "highlighter" ? "highlighter" : "pen";
  }

  private currentStyle(): StrokeStyle {
    return {
      version: 1,
      color: this.toolState.color,
      size: this.toolState.size,
      tool: this.strokeTool(),
      opacity: this.toolState.opacity,
      pressure: {
        ...this.toolState.pressure,
        enabled: this.strokeTool() === "pen" && this.toolState.pressureEnabled,
      },
      freehand: { ...this.toolState.freehand },
    };
  }

  startInputRecording(
    metadata: Omit<InputFixtureMetadata, "capturedAt"> & { capturedAt?: string },
  ): void {
    this.debugBeforeRecording = this.debug;
    this.setDebug(true);
    this.inputRecorder.start(metadata);
  }

  stopInputRecording(): InputFixture | null {
    const fixture = this.inputRecorder.stop();
    if (fixture) this.setDebug(this.debugBeforeRecording);
    return fixture;
  }

  get isInputRecording(): boolean {
    return this.inputRecorder.active;
  }

  private builderOpts(style: StrokeStyleSnapshotV1 = this.currentStyle()): StrokeBuilderOptions {
    return {
      minDistance: MIN_SAMPLE_DISTANCE,
      pressureEnabled: style.pressure.enabled,
      fallbackPressure: style.pressure.fallback ?? FALLBACK_PRESSURE,
      pressureConfig: style.pressure,
    };
  }

  // --- Input ----------------------------------------------------------------

  private toWorld(clientX: number, clientY: number): { x: number; y: number } {
    const rect = this.paperEl.getBoundingClientRect();
    const scale = this.scale || 1;
    return { x: (clientX - rect.left) / scale, y: (clientY - rect.top) / scale };
  }

  private readonly pointerCallbacks: PointerControllerCallbacks = {
    onStart: (sample) => {
      if (this.callbacks.isLocked?.()) return;
      if (this.toolState.tool === "eraser") {
        this.eraseIds = new Set();
        this.eraseAt(sample);
        return;
      }
      if (this.toolState.tool === "select") {
        this.selectStart(sample);
        return;
      }
      this.activeStrokeStyle = this.currentStyle();
      this.builder = new StrokeBuilder(this.builderOpts(this.activeStrokeStyle));
      this.builder.add(sample);
      this.renderer?.clearWet();
    },
    onMove: (coalesced, predicted) => {
      if (this.toolState.tool === "eraser") {
        for (const sample of coalesced) this.eraseAt(sample);
        return;
      }
      if (this.toolState.tool === "select") {
        this.selectMove(coalesced[coalesced.length - 1]);
        return;
      }
      if (!this.builder) return;
      // Retain every coalesced sample immediately (cheap), but defer the
      // expensive outline draw to one rAF per frame — drawing more often than
      // the display refreshes is wasted work that starves incoming events.
      for (const sample of coalesced) this.builder.add(sample);
      this.pendingPredicted = predicted;
      this.scheduleWet();
    },
    onEnd: (sample) => {
      if (this.toolState.tool === "eraser") {
        this.eraseCommit();
        return;
      }
      if (this.toolState.tool === "select") {
        this.selectEnd();
        return;
      }
      this.finishStroke(sample);
    },
    onCancel: () => {
      if (this.toolState.tool === "eraser") {
        this.eraseIds = new Set();
        this.renderDry();
        return;
      }
      if (this.toolState.tool === "select") {
        this.selectCancel();
        return;
      }
      // Salvage rather than discard: iOS can fire pointercancel on a normal pen
      // lift (e.g. when the surface briefly interprets the drag as a scroll), so
      // dropping the stroke here would make just-drawn ink vanish.
      this.finishStroke(null);
    },
    onPan: (deltaY) => {
      // Native touch-scroll is disabled (touch-action: none); drive it manually.
      // Setting scrollTop fires a scroll event -> onScroll() -> dry redraw.
      this.scrollEl.scrollTop += deltaY;
    },
    onPinch: (info) => {
      // Two-finger midpoint pan, then zoom about the pinch center.
      this.scrollEl.scrollLeft -= info.dxCss;
      this.scrollEl.scrollTop -= info.dyCss;
      this.applyZoom(this.scale * info.scaleFactor, info.centerX, info.centerY);
    },
    onDebug: (record) => this.onDebug(record),
  };

  // --- Diagnostic HUD -------------------------------------------------------

  private onDebug(record: PointerDebugRecord): void {
    this.inputRecorder.record(record);
    if (!this.debug) return;
    this.hudPointerType = record.pointerType;
    this.hudPressure = record.pressure;
    this.hudPointerId = record.pointerId;
    this.hudButtons = record.sample.buttons;
    this.hudX = record.sample.x;
    this.hudY = record.sample.y;
    this.hudTimeStamp = record.timeStamp;
    this.hudTiltX = record.sample.tiltX;
    this.hudTiltY = record.sample.tiltY;
    this.hudTwist = record.sample.twist;
    this.hudEventType = record.type;
    this.hudPredicted += record.predictedSamples.length;
    this.hudCoalescedApi ||= record.coalescedApiAvailable;
    this.hudPredictedApi ||= record.predictedApiAvailable;

    switch (record.type) {
      case "down":
        this.hudSumDown += 1;
        this.hudMoves = 0;
        this.hudPts = 0;
        this.hudMaxGap = 0;
        this.hudMaxP = 0;
        this.hudLastMoveT = record.timeStamp;
        this.pushHud("dn");
        break;
      case "move": {
        this.hudMoves += 1;
        this.hudPts += record.coalesced;
        if (record.pressure > this.hudMaxP) this.hudMaxP = record.pressure;
        const gap = record.timeStamp - this.hudLastMoveT;
        if (gap > this.hudMaxGap) this.hudMaxGap = gap;
        if (gap >= 0) {
          if (gap > 32) this.hudLongGaps += 1;
        }
        this.hudLastMoveT = record.timeStamp;
        const last = this.hudLog[this.hudLog.length - 1];
        if (last && last.k === "m") last.n += 1;
        else this.pushHud("m");
        break;
      }
      case "up":
        this.hudSumUp += 1;
        this.pushHud("up");
        break;
      case "cancel":
        this.hudSumCancel += 1;
        this.pushHud("cx");
        break;
    }
    const committed =
      record.type === "move"
        ? normalizePointerMove(record.sample, record.coalescedSamples, record.predictedSamples)
            .committed
        : record.type === "cancel"
          ? []
          : [record.sample];
    for (const sample of committed) {
      this.hudSampleCount += 1;
      this.hudPressureMin = Math.min(this.hudPressureMin, sample.pressure);
      this.hudPressureSum += sample.pressure;
      this.hudPressureSumSquares += sample.pressure * sample.pressure;
      if (sample.pressure > this.hudMaxP) this.hudMaxP = sample.pressure;
    }
    this.scheduleHud();
  }

  private pushHud(k: string): void {
    this.hudLog.push({ k, n: 1 });
    if (this.hudLog.length > 30) this.hudLog.shift();
  }

  private scheduleHud(): void {
    if (this.hudTimer) return;
    // Four updates per second keep the overlay useful without competing with
    // wet-ink rendering for every animation frame.
    this.hudTimer = window.setTimeout(() => {
      this.hudTimer = 0;
      this.renderHud();
    }, 250);
  }

  private renderHud(): void {
    if (!this.debug) return;
    const seq = this.hudLog.map((t) => (t.k === "m" ? `m·${t.n}` : t.k)).join(" ");
    const pressureMin = this.hudSampleCount ? this.hudPressureMin : 0;
    const pressureMean = this.hudSampleCount ? this.hudPressureSum / this.hudSampleCount : 0;
    const pressureVariance = this.hudSampleCount
      ? Math.max(0, this.hudPressureSumSquares / this.hudSampleCount - pressureMean ** 2)
      : 0;
    this.hudEl.setText(
      `${seq}\n` +
        `${this.hudEventType || "-"} ${this.hudPointerType || "-"} id=${this.hudPointerId} buttons=${this.hudButtons} x/y=${this.hudX.toFixed(1)}/${this.hudY.toFixed(1)} t=${this.hudTimeStamp.toFixed(1)}\n` +
        `p=${this.hudPressure.toFixed(2)} tilt=${this.hudTiltX.toFixed(0)}/${this.hudTiltY.toFixed(0)} twist=${this.hudTwist.toFixed(0)} · n=${this.hudSampleCount} min/max/mean/var=${pressureMin.toFixed(2)}/${this.hudMaxP.toFixed(2)}/${pressureMean.toFixed(2)}/${pressureVariance.toFixed(4)}\n` +
        `gap max=${this.hudMaxGap.toFixed(1)}ms long=${this.hudLongGaps} · full percentiles are calculated after export\n` +
        `Σ dn=${this.hudSumDown} mv=${this.hudMoves} up=${this.hudSumUp} cx=${this.hudSumCancel} coal=${this.hudPts} pred=${this.hudPredicted} commit=${strokeCount(this.doc)} · API coal/pred=${this.hudCoalescedApi ? "yes" : "no"}/${this.hudPredictedApi ? "yes" : "no"}`,
    );
  }

  // --- Strokes --------------------------------------------------------------

  private scheduleWet(): void {
    if (this.wetFrame || !this.builder) return;
    this.wetFrame = window.requestAnimationFrame(() => {
      this.wetFrame = 0;
      if (!this.builder) return;
      const pts = this.builder.points();
      const style = this.activeStrokeStyle ?? this.currentStyle();
      const opts = this.builderOpts(style);
      for (const sample of this.pendingPredicted) {
        pts.push(sample.x, sample.y, mapPressure(sample.pressure, opts));
      }
      this.renderer?.renderWet(pts, style);
    });
  }

  private finishStroke(final: PointerSample | null): void {
    if (this.wetFrame) {
      window.cancelAnimationFrame(this.wetFrame);
      this.wetFrame = 0;
    }
    const builder = this.builder;
    const style = this.activeStrokeStyle ?? this.currentStyle();
    this.builder = null;
    this.activeStrokeStyle = null;
    this.renderer?.clearWet();
    if (!builder) return;

    if (final) builder.addFinal(final);
    // A single retained point is a valid dot; only drop truly empty strokes.
    if (builder.length < 1) return;

    const stroke: Stroke = {
      id: `s${++this.strokeSeq}`,
      color: style.color,
      size: style.size,
      tool: style.tool,
      pts: builder.points(),
      style: cloneStrokeStyle(style),
    };
    // Record via the command stack (applies the add), then paint just this
    // stroke incrementally rather than re-outlining the whole document.
    this.history.push(this.doc, new AddStroke(stroke));
    this.index.insert(stroke);
    this.strokeById.set(stroke.id, stroke);

    this.growPaperForStroke(stroke);
    this.renderer?.appendCommittedStroke(stroke, style.pressure.enabled);
    this.changed();
  }

  // --- Eraser ---------------------------------------------------------------

  /** Add any strokes under the eraser to the pending set and preview-hide them. */
  private eraseAt(sample: { x: number; y: number }): void {
    const radius = ERASER_RADIUS / (this.viewport.scale || 1);
    let changed = false;
    for (const id of this.index.queryPoint(sample.x, sample.y, radius)) {
      if (this.eraseIds.has(id)) continue;
      const stroke = this.strokeById.get(id);
      if (stroke && strokeHitByPoint(stroke, sample.x, sample.y, radius)) {
        this.eraseIds.add(id);
        changed = true;
      }
    }
    if (changed) this.renderDry();
  }

  /** Commit the erase gesture as a single undoable RemoveStrokes command. */
  private eraseCommit(): void {
    const ids = this.eraseIds;
    this.eraseIds = new Set();
    if (ids.size === 0) return;
    this.history.push(this.doc, new RemoveStrokes(ids));
    for (const id of ids) {
      this.index.remove(id);
      this.strokeById.delete(id);
    }
    this.renderDry();
    this.changed();
  }

  // --- Selection / move -----------------------------------------------------

  private selectStart(sample: { x: number; y: number }): void {
    const bounds = this.selectionBounds();
    // Grab-to-move only when pressing inside the current selection box (padded).
    if (bounds && pointInBounds(sample.x, sample.y, padBounds(bounds, 8))) {
      this.selectMode = "move";
      this.moveLast = { x: sample.x, y: sample.y };
      this.moveDx = 0;
      this.moveDy = 0;
      return;
    }
    this.selectMode = "marquee";
    this.selection = new Set();
    this.marqueeOrigin = { x: sample.x, y: sample.y };
    this.marquee = rectFromCorners(sample.x, sample.y, sample.x, sample.y);
    this.renderDry();
    this.renderer?.renderMarquee(this.marquee);
  }

  private selectMove(sample: { x: number; y: number } | undefined): void {
    if (!sample) return;
    if (this.selectMode === "marquee" && this.marqueeOrigin) {
      this.marquee = rectFromCorners(
        this.marqueeOrigin.x,
        this.marqueeOrigin.y,
        sample.x,
        sample.y,
      );
      this.renderer?.renderMarquee(this.marquee);
      return;
    }
    if (this.selectMode === "move" && this.moveLast) {
      const dx = sample.x - this.moveLast.x;
      const dy = sample.y - this.moveLast.y;
      this.translateSelection(dx, dy);
      this.moveDx += dx;
      this.moveDy += dy;
      this.moveLast = { x: sample.x, y: sample.y };
      this.renderDry();
    }
  }

  private selectEnd(): void {
    if (this.selectMode === "marquee" && this.marquee) {
      this.applyMarqueeSelection(this.marquee);
      this.marquee = null;
      this.marqueeOrigin = null;
      this.selectMode = "none";
      this.renderer?.clearWet();
      this.renderDry();
      return;
    }
    if (this.selectMode === "move") {
      const dx = this.moveDx;
      const dy = this.moveDy;
      this.selectMode = "none";
      this.moveLast = null;
      if (dx !== 0 || dy !== 0) {
        // Undo the live translation, then record it as a command (which re-applies
        // it) so the move sits correctly on the undo stack.
        this.translateSelection(-dx, -dy);
        this.history.push(this.doc, new MoveStrokes(this.selection, dx, dy));
        this.rebuildIndex();
        this.renderDry();
        this.changed();
      }
    }
  }

  private selectCancel(): void {
    if (this.selectMode === "move") this.translateSelection(-this.moveDx, -this.moveDy);
    this.selectMode = "none";
    this.marquee = null;
    this.marqueeOrigin = null;
    this.moveLast = null;
    this.renderer?.clearWet();
    this.renderDry();
  }

  private applyMarqueeSelection(rect: Bounds): void {
    this.selection = new Set();
    for (const id of this.index.queryBounds(rect)) {
      const stroke = this.strokeById.get(id);
      if (stroke && strokeIntersectsRect(stroke, rect)) this.selection.add(id);
    }
  }

  private translateSelection(dx: number, dy: number): void {
    if (dx === 0 && dy === 0) return;
    for (const id of this.selection) {
      const stroke = this.strokeById.get(id);
      if (!stroke) continue;
      for (let i = 0; i < stroke.pts.length; i += 3) {
        stroke.pts[i] += dx;
        stroke.pts[i + 1] += dy;
      }
    }
  }

  private deleteSelection(): void {
    if (this.selection.size === 0) return;
    const ids = this.selection;
    this.selection = new Set();
    this.history.push(this.doc, new RemoveStrokes(ids, "Delete selection"));
    for (const id of ids) {
      this.index.remove(id);
      this.strokeById.delete(id);
    }
    this.renderDry();
    this.changed();
  }

  private clearSelection(): void {
    if (this.selection.size === 0) return;
    this.selection = new Set();
    this.renderDry();
  }

  // --- History --------------------------------------------------------------

  undo(): void {
    if (!this.history.undo(this.doc)) return;
    this.rebuildIndex();
    this.renderDry();
    this.changed();
  }

  redo(): void {
    if (!this.history.redo(this.doc)) return;
    this.rebuildIndex();
    this.renderDry();
    this.changed();
  }

  /** Remove every stroke (one undoable step). Returns false when already empty. */
  clearStrokes(): boolean {
    const region = primaryRegion(this.doc);
    if (region.strokes.length === 0) return false;
    this.history.push(this.doc, new ClearRegion());
    this.index.clear();
    this.strokeById.clear();
    this.selection = new Set();
    this.renderDry();
    this.changed();
    return true;
  }
}
