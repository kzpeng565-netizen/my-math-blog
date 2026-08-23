/** Pen Box management and preset editor UI. */

import { Modal, Notice, Setting } from "obsidian";
import {
  clonePreset,
  defaultPenPresets,
  exportPresetStore,
  importPresetStore,
  type PenPresetV1,
  uniquePresetId,
  validatePenPreset,
} from "../ink/presets";
import type { PressureCurve, Tool } from "../model/stroke-style";
import type InkedMarkPlugin from "../main";
import { ConfirmModal } from "./confirm-modal";

export class PenBoxModal extends Modal {
  constructor(
    private readonly plugin: InkedMarkPlugin,
    private readonly onChange: () => void,
  ) {
    super(plugin.app);
  }

  override onOpen(): void {
    this.modalEl.addClass("inkedmark-pen-box-modal");
    this.titleEl.setText("Pen Box");
    this.render();
  }

  private render(): void {
    const root = this.contentEl;
    root.empty();
    root.createEl("p", {
      text: "Tap a saved pen in the toolbar to restore its complete style. Editing a preset never changes existing strokes.",
    });

    const presets = this.plugin.settings.penPresets;
    for (let index = 0; index < presets.length; index++) {
      const preset = presets[index];
      const setting = new Setting(root)
        .setName(preset.name)
        .setDesc(
          `${preset.style.tool} · ${preset.style.size}px · ${preset.style.pressure.curve} pressure`,
        );
      setting.nameEl.addClass("inkedmark-pen-box-setting-name");
      setting.nameEl.setCssProps({ "--inkedmark-preset-color": preset.style.color });

      setting.addButton((button) =>
        button
          .setIcon(preset.id === this.plugin.settings.activePresetId ? "check" : "mouse-pointer-2")
          .setTooltip("Use this pen")
          .onClick(async () => {
            this.plugin.settings.activePresetId = preset.id;
            await this.persist();
            this.render();
          }),
      );
      setting.addButton((button) =>
        button
          .setIcon("pencil")
          .setTooltip("Edit")
          .onClick(() => {
            new PenPresetEditorModal(this.plugin, clonePreset(preset), async (next) => {
              const position = this.plugin.settings.penPresets.findIndex(
                (item) => item.id === preset.id,
              );
              if (position < 0) return;
              this.plugin.settings.penPresets[position] = { ...next, order: position };
              await this.persist();
              this.render();
            }).open();
          }),
      );
      setting.addButton((button) =>
        button
          .setIcon("copy")
          .setTooltip("Duplicate")
          .onClick(async () => {
            const used = new Set(presets.map((item) => item.id));
            const copy = clonePreset(preset);
            copy.id = uniquePresetId(`${preset.id}-copy`, used);
            copy.name = `${preset.name} copy`;
            copy.order = presets.length;
            presets.push(copy);
            await this.persist();
            this.render();
          }),
      );
      setting.addButton((button) =>
        button
          .setIcon("arrow-up")
          .setTooltip("Move up")
          .setDisabled(index === 0)
          .onClick(async () => {
            [presets[index - 1], presets[index]] = [presets[index], presets[index - 1]];
            await this.renumberAndPersist();
            this.render();
          }),
      );
      setting.addButton((button) =>
        button
          .setIcon("arrow-down")
          .setTooltip("Move down")
          .setDisabled(index === presets.length - 1)
          .onClick(async () => {
            [presets[index], presets[index + 1]] = [presets[index + 1], presets[index]];
            await this.renumberAndPersist();
            this.render();
          }),
      );
      setting.addButton((button) => {
        button.buttonEl.addClass("mod-warning");
        button
          .setIcon("trash-2")
          .setTooltip("Delete")
          .setDisabled(presets.length === 1)
          .onClick(async () => {
            const confirmed = await ConfirmModal.confirm(this.plugin.app, {
              title: `Delete “${preset.name}”?`,
              message:
                "Existing strokes keep their captured style. This only removes the reusable pen.",
              cta: "Delete",
            });
            if (!confirmed) return;
            const current = this.plugin.settings.penPresets;
            this.plugin.settings.penPresets = current.filter((item) => item.id !== preset.id);
            if (this.plugin.settings.activePresetId === preset.id) {
              this.plugin.settings.activePresetId = this.plugin.settings.penPresets[0].id;
            }
            await this.renumberAndPersist();
            this.render();
          });
      });
    }

    const actions = root.createDiv({ cls: "inkedmark-pen-box-actions" });
    const add = actions.createEl("button", { text: "New pen" });
    add.addClass("mod-cta");
    add.addEventListener("click", () => this.addPreset());

    const exportButton = actions.createEl("button", { text: "Export JSON" });
    exportButton.addEventListener("click", () => this.exportJson());

    const input = actions.createEl("input", { type: "file" });
    input.accept = ".json,application/json";
    input.addClass("inkedmark-file-input");
    input.addEventListener("change", () => void this.importJson(input, "merge"));
    const importButton = actions.createEl("button", { text: "Import JSON" });
    importButton.addEventListener("click", () => input.click());

    const replaceInput = actions.createEl("input", { type: "file" });
    replaceInput.accept = ".json,application/json";
    replaceInput.addClass("inkedmark-file-input");
    replaceInput.addEventListener("change", () => void this.importJson(replaceInput, "replace"));
    const replaceButton = actions.createEl("button", { text: "Replace from JSON" });
    replaceButton.addEventListener("click", () => replaceInput.click());

    const reset = actions.createEl("button", { text: "Restore defaults" });
    reset.addEventListener("click", () => void this.restoreDefaults());
  }

  private addPreset(): void {
    const presets = this.plugin.settings.penPresets;
    const draft = clonePreset(defaultPenPresets()[0]);
    draft.id = uniquePresetId("new-pen", new Set(presets.map((item) => item.id)));
    draft.name = "New pen";
    draft.order = presets.length;
    new PenPresetEditorModal(this.plugin, draft, async (next) => {
      this.plugin.settings.penPresets.push(next);
      this.plugin.settings.activePresetId = next.id;
      await this.renumberAndPersist();
      this.render();
    }).open();
  }

  private exportJson(): void {
    const text = exportPresetStore(
      this.plugin.settings.penPresets,
      this.plugin.settings.activePresetId,
    );
    const url = URL.createObjectURL(new Blob([text], { type: "application/json" }));
    const anchor = this.contentEl.createEl("a", { cls: "inkedmark-file-input" });
    anchor.href = url;
    anchor.download = "mathink-forge-pen-box.json";
    anchor.click();
    anchor.remove();
    window.setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  private async importJson(input: HTMLInputElement, mode: "merge" | "replace"): Promise<void> {
    const file = input.files?.[0];
    input.value = "";
    if (!file) return;
    try {
      const imported = importPresetStore(
        await file.text(),
        mode === "merge" ? this.plugin.settings.penPresets : [],
      );
      if (mode === "replace") {
        const confirmed = await ConfirmModal.confirm(this.plugin.app, {
          title: "Replace the Pen Box from JSON?",
          message:
            "This replaces all reusable presets and their order. Existing strokes are not changed.",
          cta: "Replace",
        });
        if (!confirmed) return;
        this.plugin.settings.penPresets = imported.presets;
      } else {
        this.plugin.settings.penPresets.push(...imported.presets);
      }
      this.plugin.settings.activePresetId = imported.activePresetId;
      await this.renumberAndPersist();
      this.render();
      new Notice(
        mode === "replace"
          ? `MathInk Forge: replaced the Pen Box with ${imported.presets.length} preset(s).`
          : `MathInk Forge: imported ${imported.presets.length} pen preset(s).`,
      );
    } catch (error) {
      new Notice(
        `MathInk Forge: import failed — ${error instanceof Error ? error.message : String(error)}`,
        8000,
      );
    }
  }

  private async restoreDefaults(): Promise<void> {
    const confirmed = await ConfirmModal.confirm(this.plugin.app, {
      title: "Restore the default Pen Box?",
      message: "This replaces reusable presets only. Existing strokes are not changed.",
      cta: "Restore",
    });
    if (!confirmed) return;
    this.plugin.settings.penPresets = defaultPenPresets();
    this.plugin.settings.activePresetId = this.plugin.settings.penPresets[0].id;
    await this.persist();
    this.render();
  }

  private async renumberAndPersist(): Promise<void> {
    this.plugin.settings.penPresets.forEach((preset, index) => {
      preset.order = index;
    });
    await this.persist();
  }

  private async persist(): Promise<void> {
    await this.plugin.saveSettings();
    this.onChange();
  }
}

class PenPresetEditorModal extends Modal {
  constructor(
    plugin: InkedMarkPlugin,
    private readonly draft: PenPresetV1,
    private readonly onSave: (preset: PenPresetV1) => Promise<void>,
  ) {
    super(plugin.app);
  }

  override onOpen(): void {
    this.modalEl.addClass("inkedmark-pen-editor-modal");
    this.titleEl.setText("Edit pen preset");
    const root = this.contentEl;
    root.empty();

    new Setting(root).setName("Name").addText((text) =>
      text.setValue(this.draft.name).onChange((value) => {
        this.draft.name = value;
      }),
    );
    new Setting(root).setName("Tool").addDropdown((dropdown) =>
      dropdown
        .addOptions({ pen: "Pen", highlighter: "Highlighter" })
        .setValue(this.draft.style.tool)
        .onChange((value) => {
          this.draft.style.tool = value as Tool;
        }),
    );
    new Setting(root).setName("Color").addColorPicker((picker) =>
      picker.setValue(this.draft.style.color).onChange((value) => {
        this.draft.style.color = value;
      }),
    );
    this.numberField(root, "Size", this.draft.style.size, 0.25, 64, 0.25, (value) => {
      this.draft.style.size = value;
    });
    this.percentSlider(root, "Opacity", this.draft.style.opacity, (value) => {
      this.draft.style.opacity = value;
    });

    new Setting(root).setName("Use pressure").addToggle((toggle) =>
      toggle.setValue(this.draft.style.pressure.enabled).onChange((value) => {
        this.draft.style.pressure.enabled = value;
      }),
    );
    new Setting(root).setName("Pressure curve").addDropdown((dropdown) =>
      dropdown
        .addOptions({ linear: "Linear", soft: "Soft", medium: "Medium", hard: "Hard" })
        .setValue(this.draft.style.pressure.curve)
        .onChange((value) => {
          this.draft.style.pressure.curve = value as PressureCurve;
        }),
    );
    this.numberField(root, "Input minimum", this.draft.style.pressure.inputMin, 0, 1, 0.01, (v) => {
      this.draft.style.pressure.inputMin = v;
    });
    this.numberField(root, "Input maximum", this.draft.style.pressure.inputMax, 0, 1, 0.01, (v) => {
      this.draft.style.pressure.inputMax = v;
    });
    this.numberField(
      root,
      "Output minimum",
      this.draft.style.pressure.outputMin,
      0,
      1,
      0.01,
      (v) => {
        this.draft.style.pressure.outputMin = v;
      },
    );
    this.numberField(
      root,
      "Output maximum",
      this.draft.style.pressure.outputMax,
      0,
      1,
      0.01,
      (v) => {
        this.draft.style.pressure.outputMax = v;
      },
    );
    this.numberField(root, "Gamma", this.draft.style.pressure.gamma, 0.1, 5, 0.05, (v) => {
      this.draft.style.pressure.gamma = v;
    });
    this.numberField(root, "Thinning", this.draft.style.freehand.thinning, -1, 1, 0.05, (v) => {
      this.draft.style.freehand.thinning = v;
    });
    this.numberField(root, "Smoothing", this.draft.style.freehand.smoothing, 0, 1, 0.05, (v) => {
      this.draft.style.freehand.smoothing = v;
    });
    this.numberField(root, "Streamline", this.draft.style.freehand.streamline, 0, 1, 0.05, (v) => {
      this.draft.style.freehand.streamline = v;
    });
    this.numberField(root, "Start taper", this.draft.style.freehand.startTaper, 0, 512, 1, (v) => {
      this.draft.style.freehand.startTaper = v;
    });
    this.numberField(root, "End taper", this.draft.style.freehand.endTaper, 0, 512, 1, (v) => {
      this.draft.style.freehand.endTaper = v;
    });

    const actions = root.createDiv({ cls: "inkedmark-pen-box-actions" });
    const save = actions.createEl("button", { text: "Save pen" });
    save.addClass("mod-cta");
    save.addEventListener("click", () => {
      this.draft.name = this.draft.name.trim();
      const errors = validatePenPreset(this.draft);
      if (errors.length > 0) {
        new Notice(`MathInk Forge: ${errors.join(" ")}`, 8000);
        return;
      }
      void this.onSave(clonePreset(this.draft))
        .then(() => this.close())
        .catch((error: unknown) => {
          new Notice(`MathInk Forge: could not save pen — ${String(error)}`, 8000);
        });
    });
    const cancel = actions.createEl("button", { text: "Cancel" });
    cancel.addEventListener("click", () => this.close());
  }

  private numberField(
    root: HTMLElement,
    name: string,
    initial: number,
    min: number,
    max: number,
    step: number,
    onChange: (value: number) => void,
  ): void {
    new Setting(root).setName(name).addText((text) => {
      text.inputEl.type = "number";
      text.inputEl.min = String(min);
      text.inputEl.max = String(max);
      text.inputEl.step = String(step);
      text.setValue(String(initial)).onChange((value) => {
        const parsed = Number(value);
        if (Number.isFinite(parsed)) onChange(parsed);
      });
    });
  }

  private percentSlider(
    root: HTMLElement,
    name: string,
    initial: number,
    onChange: (value: number) => void,
  ): void {
    new Setting(root).setName(name).addSlider((slider) =>
      slider
        .setLimits(0, 100, 1)
        .setValue(Math.round(initial * 100))
        .onChange((value) => onChange(value / 100)),
    );
  }
}
