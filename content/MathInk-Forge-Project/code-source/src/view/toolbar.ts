/**
 * Toolbar DOM, shared by the ink view and the inline-block editor modal.
 *
 * Pen / highlighter / eraser / select, a color palette, sizes, a pressure
 * toggle, undo/redo/clear, zoom, and (for ink notes only) the text-layer and
 * recognition buttons.
 */

import { setIcon } from "obsidian";
import type { PenPresetV1 } from "../ink/presets";
import type { FreehandConfigV1, PressureConfigV1 } from "../model/stroke-style";

/** Tools selectable in the toolbar. Only pen/highlighter produce strokes. */
export type ActiveTool = "pen" | "highlighter" | "eraser" | "select";

export interface ToolbarState {
  tool: ActiveTool;
  color: string;
  size: number;
  pressureEnabled: boolean;
  opacity: number;
  pressure: PressureConfigV1;
  freehand: FreehandConfigV1;
  /** Null when the user changed an individual legacy swatch/size control. */
  activePresetId: string | null;
}

export interface ToolbarCallbacks {
  onToolChange(tool: ActiveTool): void;
  onColorChange(color: string): void;
  onSizeChange(size: number): void;
  onPressureToggle(enabled: boolean): void;
  onPresetSelect?(preset: PenPresetV1): void;
  onManagePresets?(): void;
  onUndo(): void;
  onRedo(): void;
  onClear(): void;
  onZoomIn(): void;
  onZoomOut(): void;
  onZoomReset(): void;
  onToggleText(): void;
  onRecognize(): void;
}

export interface ToolbarOptions {
  /** Show the text-layer / recognize buttons (ink notes only). Default true. */
  textTools?: boolean;
  presets?: readonly PenPresetV1[];
}

export class Toolbar {
  private readonly root: HTMLElement;
  private readonly toolButtons = new Map<ActiveTool, HTMLButtonElement>();
  private readonly swatches = new Map<string, HTMLButtonElement>();
  private readonly sizeButtons = new Map<number, HTMLButtonElement>();
  private readonly presetButtons = new Map<string, HTMLButtonElement>();
  private penBoxEl: HTMLElement | null = null;
  private presets: readonly PenPresetV1[];
  private pressureButton!: HTMLButtonElement;
  private recognizeButton: HTMLButtonElement | null = null;
  private statusEl!: HTMLElement;

  constructor(
    container: HTMLElement,
    private readonly palette: readonly string[],
    private readonly sizes: readonly number[],
    private state: ToolbarState,
    private readonly callbacks: ToolbarCallbacks,
    private readonly options: ToolbarOptions = {},
  ) {
    this.presets = (options.presets ?? []).slice(0, 8);
    this.root = container.createDiv({ cls: "inkedmark-toolbar" });
    this.build();
    this.syncActive();
  }

  private build(): void {
    this.addToolButton("pen", "pencil", "Pen (P)");
    this.addToolButton("highlighter", "highlighter", "Highlighter (H)");
    this.addToolButton("eraser", "eraser", "Eraser (E)");
    this.addToolButton("select", "box-select", "Select (V)");
    this.addSeparator();

    if (this.presets.length > 0) {
      this.penBoxEl = this.root.createDiv({ cls: "inkedmark-pen-box" });
      this.buildPenBox();
      this.addSeparator();
    }

    for (const color of this.palette) {
      const swatch = this.root.createEl("button", { cls: "inkedmark-swatch" });
      swatch.style.background = color;
      swatch.setAttribute("aria-label", color);
      swatch.addEventListener("click", () => {
        this.state.color = color;
        this.state.activePresetId = null;
        this.callbacks.onColorChange(color);
        this.syncActive();
      });
      this.swatches.set(color, swatch);
    }
    this.addSeparator();

    for (const size of this.sizes) {
      const button = this.root.createEl("button", { text: String(size) });
      button.setAttribute("aria-label", `Size ${size}`);
      button.addEventListener("click", () => {
        this.state.size = size;
        this.state.activePresetId = null;
        this.callbacks.onSizeChange(size);
        this.syncActive();
      });
      this.sizeButtons.set(size, button);
    }
    this.addSeparator();

    this.pressureButton = this.iconButton("gauge", "Toggle pressure", () => {
      this.state.pressureEnabled = !this.state.pressureEnabled;
      this.state.pressure.enabled = this.state.pressureEnabled;
      this.state.activePresetId = null;
      this.callbacks.onPressureToggle(this.state.pressureEnabled);
      this.syncActive();
    });

    this.iconButton("undo-2", "Undo (Cmd/Ctrl+Z)", () => this.callbacks.onUndo());
    this.iconButton("redo-2", "Redo (Cmd/Ctrl+Shift+Z)", () => this.callbacks.onRedo());
    this.iconButton("trash-2", "Clear", () => this.callbacks.onClear());
    this.addSeparator();

    this.iconButton("zoom-out", "Zoom out", () => this.callbacks.onZoomOut());
    this.iconButton("maximize", "Fit / reset view", () => this.callbacks.onZoomReset());
    this.iconButton("zoom-in", "Zoom in", () => this.callbacks.onZoomIn());
    if (this.options.textTools !== false) {
      this.addSeparator();
      this.iconButton("file-text", "Text layer (transcription)", () =>
        this.callbacks.onToggleText(),
      );
      this.recognizeButton = this.iconButton("scan-text", "Recognize handwriting", () =>
        this.callbacks.onRecognize(),
      );
    }

    // Right-aligned build/diagnostics readout (pushed right via margin-left:auto).
    this.statusEl = this.root.createSpan({ cls: "inkedmark-status" });
  }

  /** Set the right-aligned status text (build id, stroke count, …). */
  setStatus(text: string): void {
    this.statusEl.setText(text);
  }

  /** Update the recognize button's tooltip (shows the active engine). */
  setRecognizeLabel(label: string): void {
    this.recognizeButton?.setAttribute("aria-label", label);
  }

  private addToolButton(tool: ActiveTool, icon: string, label: string): void {
    const button = this.iconButton(icon, label, () => {
      this.state.tool = tool;
      this.callbacks.onToolChange(tool);
      this.syncActive();
    });
    this.toolButtons.set(tool, button);
  }

  private addPresetButton(parent: HTMLElement, preset: PenPresetV1): void {
    const button = parent.createEl("button", { cls: "inkedmark-preset" });
    const swatch = button.createSpan({ cls: "inkedmark-preset-swatch" });
    swatch.style.background = preset.style.color;
    button.createSpan({ cls: "inkedmark-preset-name", text: preset.name });
    button.setAttribute("aria-label", `Pen preset: ${preset.name}`);
    button.addEventListener("click", () => {
      applyPresetToToolbarState(this.state, preset);
      this.callbacks.onPresetSelect?.(preset);
      this.syncActive();
    });
    this.presetButtons.set(preset.id, button);
  }

  private buildPenBox(): void {
    if (!this.penBoxEl) return;
    this.penBoxEl.empty();
    this.presetButtons.clear();
    for (const preset of this.presets) this.addPresetButton(this.penBoxEl, preset);
    const manage = this.penBoxEl.createEl("button", { cls: "inkedmark-preset-manage" });
    setIcon(manage, "settings-2");
    manage.setAttribute("aria-label", "Manage pen presets");
    manage.addEventListener("click", () => this.callbacks.onManagePresets?.());
  }

  private iconButton(icon: string, label: string, onClick: () => void): HTMLButtonElement {
    const button = this.root.createEl("button");
    setIcon(button, icon);
    button.setAttribute("aria-label", label);
    button.addEventListener("click", onClick);
    return button;
  }

  private addSeparator(): void {
    this.root.createDiv({ cls: "inkedmark-sep" });
  }

  /** Reflect the current state on the buttons. */
  syncActive(): void {
    for (const [tool, button] of this.toolButtons) {
      button.toggleClass("is-active", tool === this.state.tool);
    }
    for (const [color, swatch] of this.swatches) {
      swatch.toggleClass("is-active", color === this.state.color);
    }
    for (const [size, button] of this.sizeButtons) {
      button.toggleClass("is-active", size === this.state.size);
    }
    for (const [id, button] of this.presetButtons) {
      button.toggleClass("is-active", id === this.state.activePresetId);
    }
    this.pressureButton.toggleClass("is-active", this.state.pressureEnabled);
  }

  setState(state: ToolbarState): void {
    this.state = state;
    this.syncActive();
  }

  /** Refresh Pen Box buttons after preset CRUD without rebuilding the host view. */
  setPresets(presets: readonly PenPresetV1[]): void {
    this.presets = presets.slice(0, 8);
    this.buildPenBox();
    this.syncActive();
  }

  destroy(): void {
    this.root.remove();
  }
}

export function toolbarStateFromPreset(preset: PenPresetV1): ToolbarState {
  return {
    tool: preset.style.tool,
    color: preset.style.color,
    size: preset.style.size,
    pressureEnabled: preset.style.pressure.enabled,
    opacity: preset.style.opacity,
    pressure: { ...preset.style.pressure },
    freehand: { ...preset.style.freehand },
    activePresetId: preset.id,
  };
}

export function applyPresetToToolbarState(state: ToolbarState, preset: PenPresetV1): void {
  state.tool = preset.style.tool;
  state.color = preset.style.color;
  state.size = preset.style.size;
  state.pressureEnabled = preset.style.pressure.enabled;
  state.opacity = preset.style.opacity;
  state.pressure = { ...preset.style.pressure };
  state.freehand = { ...preset.style.freehand };
  state.activePresetId = preset.id;
}
