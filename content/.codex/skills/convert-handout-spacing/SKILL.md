---
name: convert-handout-spacing
description: Safely convert runs of manually inserted blank lines in Obsidian Markdown handouts into consistent, printable HTML spacing blocks. Use when the user asks to batch-process 讲义留白、多余空行、连续换行、答题空间, or replace many blank lines with blank-s/blank/blank-l/blank-xl blocks for Obsidian preview or PDF export.
---

# 批量转换讲义留白

把人为按出的连续空行转换为可控的留白块。保留正常段落间距，不改代码块、YAML、显示公式或 HTML 预格式化区域。

## 工作流程

1. 明确范围。优先使用用户指定的文件、文件夹或当前笔记；除非用户明确要求，否则不要扫描整个 Vault。
2. 检查目标文件与当前 Git 状态，避免覆盖无关修改。
3. 确认 `.obsidian/snippets/handout-blank-space.css` 是否存在：
   - 不存在时，把 `assets/handout-blank-space.css` 复制到该位置。
   - 已存在时不要覆盖；先检查其中是否已有 `.blank-s`、`.blank`、`.blank-l`、`.blank-xl`。
4. 必须先预览，不带 `--write` 运行脚本：

   ```powershell
   python ".codex/skills/convert-handout-spacing/scripts/convert_blank_lines.py" "目标文件或文件夹"
   ```

5. 需要查看实际替换内容时加 `--diff`。根据预览结果确认范围和分级是否合理。
6. 用户已经明确要求修改或批量处理时，执行写入：

   ```powershell
   python ".codex/skills/convert-handout-spacing/scripts/convert_blank_lines.py" "目标文件或文件夹" --write
   ```

7. 再运行一次 dry-run；预期显示 `0 个留白区域`。最后检查 `git diff --stat` 和相关文件的 diff。
8. 报告修改的文件数、转换区域数、各尺寸数量，以及 CSS 是否已安装。提醒用户在 Obsidian 的“设置 → 外观 → CSS 代码片段”中启用 `handout-blank-space`。

## 默认分级

脚本只转换至少 3 个连续空白行，1–2 个空白行保持原样：

- 3–4 行 → `<div class="blank-s"></div>`（12 mm）
- 5 行 → `<div class="blank"></div>`（28 mm）
- 6–7 行 → `<div class="blank-l"></div>`（50 mm）
- 8 行及以上 → `<div class="blank-xl"></div>`（80 mm）

若用户希望所有区域统一尺寸，使用 `--force-class blank`（也可为 `blank-s`、`blank-l`、`blank-xl`）。若用户给出不同阈值，使用 `--small-max`、`--medium-max`、`--large-max` 调整。

## 安全边界

- 默认是 dry-run；没有 `--write` 时不得改文件。
- 跳过 YAML frontmatter、围栏代码块、`$$ ... $$`、`\[ ... \]`、HTML 注释，以及 `pre/script/style` 块内部的空行。
- 跳过文件开头和结尾的空行；不把尾部空行变成答题区。
- 目录扫描只处理 `.md`，并排除 `.git`、`.obsidian`、`.claude`、`.claudian`、`.trash`、`node_modules`、`public`。
- 不根据题目语义擅自扩大或缩小留白；默认按原空行数量分级。个别作图题需要更大空间时，在批处理后用局部 patch 调整 class。
- 不整篇重写 Markdown。只接受脚本产生的局部替换，并审阅 diff。

## 常用参数

```text
--diff                    输出 unified diff（仍不写入）
--write                   写回文件
--min-lines 3             最少连续空白行数
--small-max 4             blank-s 的最大空白行数
--medium-max 5            blank 的最大空白行数
--large-max 7             blank-l 的最大空白行数
--force-class blank       所有命中统一使用一个 class
--backup-suffix .bak      写入前为改动文件创建备份（可选）
```
