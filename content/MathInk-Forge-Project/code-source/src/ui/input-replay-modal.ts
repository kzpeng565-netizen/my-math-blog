/** Desktop Replay UI for captured/synthetic Input Lab JSON fixtures. */

import { Modal, Notice, Setting } from "obsidian";
import { optionsForStrokeStyle, outlineToSvgPath, strokeOutline } from "../ink/freehand";
import type { PenPresetV1 } from "../ink/presets";
import {
  type InputFixture,
  parseInputFixture,
  replayInputFixture,
  replayRawInputFixture,
  summarizeInput,
} from "../input/diagnostics";

const SVG_NS = "http://www.w3.org/2000/svg";

export class InputReplayModal extends Modal {
  private fixture: InputFixture | null = null;
  private presetId: string;
  private rawPreviewEl: HTMLElement | null = null;
  private currentPreviewEl: HTMLElement | null = null;
  private referencePreviewEl: HTMLElement | null = null;
  private referenceLabelEl: HTMLElement | null = null;
  private statsEl: HTMLElement | null = null;

  constructor(
    app: ConstructorParameters<typeof Modal>[0],
    private readonly presets: readonly PenPresetV1[],
  ) {
    super(app);
    this.presetId = presets[0]?.id ?? "";
  }

  override onOpen(): void {
    this.modalEl.addClass("inkedmark-replay-modal");
    this.titleEl.setText("Desktop Replay");
    const root = this.contentEl;
    root.empty();
    root.createEl("p", {
      text: "Load an Input Lab JSON fixture. Replay ignores predicted samples and sends committed samples through the production StrokeBuilder, pressure mapper, and perfect-freehand outline.",
    });

    new Setting(root)
      .setName("Replay pen")
      .addDropdown((dropdown) => {
        for (const preset of this.presets) dropdown.addOption(preset.id, preset.name);
        dropdown.setValue(this.presetId).onChange((value) => {
          this.presetId = value;
          this.renderFixture();
        });
      })
      .addButton((button) =>
        button
          .setButtonText("Open fixture…")
          .setCta()
          .onClick(() => this.chooseFile()),
      );

    this.statsEl = root.createEl("pre", { cls: "inkedmark-replay-stats" });
    this.statsEl.setText("No fixture loaded.");
    const comparison = root.createDiv({ cls: "inkedmark-replay-comparison" });
    this.rawPreviewEl = this.createPreviewPanel(comparison, "Raw input");
    this.currentPreviewEl = this.createPreviewPanel(comparison, "Current output");
    const referencePanel = comparison.createDiv({ cls: "inkedmark-replay-panel" });
    this.referenceLabelEl = referencePanel.createEl("h3", { text: "Reference output" });
    this.referencePreviewEl = referencePanel.createDiv({ cls: "inkedmark-replay-preview" });
  }

  private createPreviewPanel(parent: HTMLElement, label: string): HTMLElement {
    const panel = parent.createDiv({ cls: "inkedmark-replay-panel" });
    panel.createEl("h3", { text: label });
    return panel.createDiv({ cls: "inkedmark-replay-preview" });
  }

  private chooseFile(): void {
    const input = this.contentEl.createEl("input", { cls: "inkedmark-file-input" });
    input.type = "file";
    input.accept = ".json,application/json";
    input.addEventListener("change", () => {
      const file = input.files?.[0];
      if (!file) return;
      void file
        .text()
        .then((text) => {
          this.fixture = parseInputFixture(text);
          this.renderFixture();
        })
        .catch((error: unknown) => {
          new Notice(`MathInk Forge: cannot load fixture — ${String(error)}`);
        });
    });
    input.click();
  }

  private renderFixture(): void {
    if (
      !this.fixture ||
      !this.rawPreviewEl ||
      !this.currentPreviewEl ||
      !this.referencePreviewEl ||
      !this.referenceLabelEl ||
      !this.statsEl
    ) {
      return;
    }
    const preset = this.presets.find((item) => item.id === this.presetId) ?? this.presets[0];
    if (!preset) return;
    const referencePreset =
      this.presets.find((item) => item.id === this.fixture?.metadata.presetId) ?? this.presets[0];
    if (!referencePreset) return;
    const stats = summarizeInput(this.fixture);
    this.statsEl.setText(
      [
        `${this.fixture.metadata.name} · ${this.fixture.metadata.device}`,
        `${stats.strokeCount} stroke(s), ${stats.committedSampleCount} committed samples, ${stats.predictedSampleCount} predicted`,
        `duration ${stats.durationMs.toFixed(1)} ms · median/P95/max gap ${stats.medianMoveGapMs.toFixed(1)}/${stats.p95MoveGapMs.toFixed(1)}/${stats.maxMoveGapMs.toFixed(1)} ms · long gaps ${stats.longMoveGapCount}`,
        `pressure ${stats.pressureMin.toFixed(2)}–${stats.pressureMax.toFixed(2)} (mean ${stats.pressureMean.toFixed(2)}, variance ${stats.pressureVariance.toFixed(4)}, P05/P50/P95 ${stats.pressureP05.toFixed(2)}/${stats.pressureMedian.toFixed(2)}/${stats.pressureP95.toFixed(2)})`,
        `tiltX ${stats.tiltXMin.toFixed(1)}–${stats.tiltXMax.toFixed(1)}° · tiltY ${stats.tiltYMin.toFixed(1)}–${stats.tiltYMax.toFixed(1)}° · twist ${stats.twistMin.toFixed(1)}–${stats.twistMax.toFixed(1)}°`,
        `pressure verdict: ${stats.pressureCapability} · coalesced API ${stats.coalescedApiAvailable ? "yes" : "no"} · predicted API ${stats.predictedApiAvailable ? "yes" : "no"} · cancel ${stats.cancelCount}`,
        `handler P95/max ${stats.processingP95Ms.toFixed(1)}/${stats.processingMaxMs.toFixed(1)} ms · dispatch delay P95/max ${stats.dispatchDelayP95Ms.toFixed(1)}/${stats.dispatchDelayMaxMs.toFixed(1)} ms`,
      ].join("\n"),
    );

    this.renderRawPreview(this.rawPreviewEl, this.fixture);
    this.renderBrushPreview(this.currentPreviewEl, this.fixture, preset);
    this.referenceLabelEl.setText(`Reference output · ${referencePreset.name}`);
    this.renderBrushPreview(this.referencePreviewEl, this.fixture, referencePreset);
  }

  private renderRawPreview(target: HTMLElement, fixture: InputFixture): void {
    target.empty();
    const strokes = replayRawInputFixture(fixture);
    const all = strokes.flat();
    if (all.length === 0) {
      target.setText("Fixture contains no raw strokes.");
      return;
    }
    const svg = document.createElementNS(SVG_NS, "svg");
    svg.setAttribute("role", "img");
    svg.setAttribute("aria-label", `Raw input of ${fixture.metadata.name}`);
    this.setViewBox(
      svg,
      all.map((sample) => [sample.x, sample.y]),
    );
    for (const stroke of strokes) {
      const path = document.createElementNS(SVG_NS, "path");
      path.setAttribute(
        "d",
        stroke
          .map((sample, index) => `${index === 0 ? "M" : "L"} ${sample.x} ${sample.y}`)
          .join(" "),
      );
      path.setAttribute("fill", "none");
      path.setAttribute("stroke", "var(--text-normal)");
      path.setAttribute("stroke-width", "1.5");
      path.setAttribute("vector-effect", "non-scaling-stroke");
      svg.append(path);
    }
    for (const record of fixture.records) {
      for (const sample of record.predictedSamples) {
        const point = document.createElementNS(SVG_NS, "circle");
        point.setAttribute("cx", String(sample.x));
        point.setAttribute("cy", String(sample.y));
        point.setAttribute("r", "1.8");
        point.setAttribute("fill", "var(--text-error)");
        svg.append(point);
      }
    }
    target.append(svg);
  }

  private renderBrushPreview(
    target: HTMLElement,
    fixture: InputFixture,
    preset: PenPresetV1,
  ): void {
    target.empty();
    const svg = document.createElementNS(SVG_NS, "svg");
    svg.setAttribute("role", "img");
    svg.setAttribute("aria-label", `Replay preview of ${fixture.metadata.name}`);
    const strokes = replayInputFixture(fixture, preset.style);
    const outlines = strokes.map((points) =>
      strokeOutline(points, optionsForStrokeStyle(preset.style), true),
    );
    const all = outlines.flat();
    if (all.length === 0) {
      target.setText("Fixture contains no replayable strokes.");
      return;
    }
    this.setViewBox(svg, all);
    for (const outline of outlines) {
      const pathData = outlineToSvgPath(outline);
      if (!pathData) continue;
      const path = document.createElementNS(SVG_NS, "path");
      path.setAttribute("d", pathData);
      path.setAttribute("fill", preset.style.color);
      path.setAttribute("fill-opacity", String(preset.style.opacity));
      svg.append(path);
    }
    target.append(svg);
  }

  private setViewBox(svg: SVGSVGElement, points: number[][]): void {
    const xs = points.map((point) => point[0]);
    const ys = points.map((point) => point[1]);
    const minX = Math.min(...xs) - 12;
    const minY = Math.min(...ys) - 12;
    const width = Math.max(24, Math.max(...xs) - minX + 12);
    const height = Math.max(24, Math.max(...ys) - minY + 12);
    svg.setAttribute("viewBox", `${minX} ${minY} ${width} ${height}`);
  }
}
