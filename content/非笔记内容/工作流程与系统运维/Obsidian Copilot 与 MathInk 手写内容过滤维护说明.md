# Obsidian Copilot 与 MathInk 手写内容过滤维护说明

更新时间：2026-09-01

## 1. 目的与硬性边界

本次修改解决两个问题：

1. Copilot 在读取普通 Markdown、行内 MathInk 或完整 `.ink.md` 笔记时，不应把压缩笔画编码作为自然语言上下文交给模型。
2. MathInk 对整份多页手写笔记的云识别不再把全部页面缩成一张图片，而是逐页、串行提交给当前已配置的识别 provider。

硬性边界：

- Copilot 的过滤只作用于送入 AI、搜索和索引的内存副本；不得调用 `vault.modify`、`vault.process` 或 adapter write 修改源笔记。
- fenced `inkedmark` 块只向 Copilot 投影首个非空 `caption:`；`v1:`、`v2:` 等 payload 仍完整保存在原笔记。
- 完整 `.ink.md` 中的 `%%inkedmark ... %%` 数据块只在 AI 副本中省略；MathInk 文件本身不删除。
- 当前 Markdown 文件批量识别只改各块的 `caption:` 行，payload、fence 类型、顺序和外围正文不变。
- Copilot 的 `data.json` 不由部署覆盖；Vault QA、模型、API、Embedding、Project 和排除规则沿用原设置。

## 2. 工程与部署位置

- Copilot 源码：`D:\Obsidian-Copilot-MathInk-Project`
- Copilot 实现提交：`77728ff3090d98c26e03a71484e84744ee9eaec1`
- MathInk 源码：`D:\MathInk-Forge-Project\code-source`
- Vault：`D:\mathblog\quartz\content`
- Copilot 部署目录：`.obsidian/plugins/copilot`
- MathInk 部署目录：`.obsidian/plugins/mathink-forge`

## 3. Copilot 修改过的读取路径

统一清洗函数是 `src/utils/mathInkMarkdown.ts` 中的 `sanitizeMathInkMarkdown(content)`。以下读取路径已接入：

| 类别 | 接入位置 |
| --- | --- |
| Markdown/活动笔记/嵌入笔记 | `src/tools/FileParserManager.ts`、`src/contextProcessor.ts`、`src/utils.ts` |
| 自定义命令与选中文本 | `src/commands/customCommandUtils.ts` |
| Project 上下文 | `src/LLMProviders/projectManager.ts` |
| Vault 索引与 token 统计 | `src/search/indexOperations.ts`、`src/search/searchUtils.ts`、`src/search/v3/chunks.ts` |
| Grep、标题、标签、时间和词法检索 | `src/search/v3/scanners/GrepScanner.ts`、`FilterRetriever.ts`、`TieredLexicalRetriever.ts` |
| 语义/远程/旧索引结果防御层 | `src/search/hybridRetriever.ts`、`selfHostRetriever.ts`、`miyo/MiyoSemanticRetriever.ts`、`v3/MergedSemanticRetriever.ts` |
| `readNote` 工具 | `src/tools/NoteTools.ts` |
| @mention 与相关笔记预览 | `AtMentionCommandPlugin.tsx`、`RelevantNotes.tsx`、`notePreviewUtils.ts` |
| 索引状态命令的空文件判断 | `src/commands/index.ts` |

没有全局替换 Obsidian 的 `Vault.read/cachedRead`，因此 Copilot 的写入、Composer、对话持久化、用户记忆和项目配置仍读取原文件，不会因 AI 清洗而丢失手写编码。

## 4. 原有 Quick Command 行为

当前已安装 Copilot 曾在压缩 bundle 中直接加入两个本地行为。本次已迁回源码：

- Quick Command 请求前加入 `当前时间：...`。
- 完成结果写入 `copilot/copilot-conversations/quickcmd-<timestamp>.md`。

源码位置：`src/commands/quickCommandLocalBehavior.ts` 与 `CustomCommandChatModal.tsx`。

## 5. MathInk 分页识别

### 5.1 整份笔记

`Recognize handwriting in this note` 和自动识别现在按以下流程工作：

1. 普通纸张按固定纸高枚举页面；PDF 按真实 PDF page bounds 枚举。
2. 每个非空页面渲染一张独立图片，严格按页码串行调用 provider，并传入一基页码。
3. 空白页不发送云请求。
4. `recognizedPageHashes` 记录逐页成功状态；没有变化的页面不重复计费。
5. 当前页命令仍只发送视口中心页。
6. 旧整体识别文本只有在所有非空页均成功后才原子迁移为分页文本；任一页失败时保留旧文本。
7. 已完成分页迁移的笔记允许成功页独立更新；失败页保留旧文本及旧 hash。

关键实现：

- `src/recognition/page-batch.ts`
- `src/recognition/page.ts`
- `src/recognition/text-layer.ts`
- `src/view/ink-view.ts`

### 5.2 当前 Markdown 文件全部行内手写

新增命令：

- ID：`mathink-forge:recognize-all-inline-handwriting-current-file`
- 名称：`Recognize all inline handwriting in current file`

每个 fenced `inkedmark` 块单独提交识别。异步返回后按 payload 和相同 payload 的出现序号重新定位；块已被编辑、删除或替换时跳过，不覆盖用户修改。Manual provider 不执行无人值守批处理。

## 6. 备份与当前哈希

### 6.1 Copilot

备份：`D:\Obsidian-Copilot-MathInk-Project\artifacts\backups\copilot-pre-mathink-20260901-120536`

- 部署 `main.js`：`777E2B300DF8268E8302F5AFC786AE06E8C6ED9CF02ECE02A558E3F5221012EB`
- `data.json`：`871E76130C1F499854F5E0C31550B154DA9D0394C6BEF775733509F03ED41934`
- 部署前后 `data.json` 哈希一致。

### 6.2 MathInk

备份：`D:\MathInk-Forge-Project\artifacts\backups\mathink-pre-paged-recognition-20260901-122453`

- 部署 `main.js`：`8A6923FB4DEFD2228D16D0F052F6848F3A71EC9F6F5469E3BA5F795BBFB358EA`
- `data.json`：`A1DFCF96C14BA7A103CF08A90C8F9D98EE0046D7E38AEBC79B0C2729AE8B55AB`
- 构建产物与 Vault 中四件套哈希一致。

## 7. 验证结果

### Copilot

- 单元测试：118 suites、2131 tests 全部通过。
- 新增清洗/Quick Command 测试：8 tests 通过。
- TypeScript、ESLint、生产构建通过。
- 本次修改文件的 Prettier 检查通过。
- 全仓库 Prettier 仍被原有 `src/LLMProviders/chatModelManager.ts` 格式问题阻断；未为本任务修改该无关文件。
- 插件已重新加载；`data.json` 未变化，构建中仍包含 Vault QA 与原 Quick Command 保存路径。

### MathInk

- 完整测试：53 files 通过、1 integration file 跳过；408 tests 通过、1 live test 跳过。
- TypeScript、标准 ESLint、生产构建通过。
- `lint:review` 仍有既有 `serialize.ts`、PDF、Pen Box 和样式规则问题；本次新增代码的标准 lint 已通过。
- 新命令和 page-by-page 文案已在部署 bundle 中确认。

## 8. Copilot 索引状态

旧 Copilot 索引已完整备份，但截至 2026-09-01 本轮尚未执行强制重建。

原因：强制重建会把整个 Vault 的**清洗后文本**重新发送给当前配置的 embedding provider，并可能消耗外部 API 配额。执行前必须再次得到对该次全库外传和费用的明确授权。

在重建前：

- 新读取和新索引路径已经清洗。
- 旧缓存/旧索引结果在多个检索出口再次清洗。
- 但从旧索引中间位置截断的历史 chunk 仍不能视为已完成彻底清除；完整闭环仍以 Force reindex 成功为准。

## 9. 回滚

### Copilot

1. 停用 Copilot 或关闭 Obsidian。
2. 从 Copilot 备份目录恢复 `main.js`、`manifest.json`、`styles.css`、`data.json`。
3. 如已经重建索引，再从 `indexes/` 恢复 `.obsidian/copilot-index-*`。
4. 核对 `SHA256_MANIFEST.json` 后重新加载插件。

### MathInk

1. 停用 MathInk Forge 或关闭 Obsidian。
2. 从 MathInk 备份的 `deployed-plugin/` 恢复 `main.js`、`manifest.json`、`styles.css`、`pdf.worker.min.mjs`、`data.json`。
3. 核对备份清单后重新加载插件。

不得使用 `git reset` 或全仓库格式化回滚本任务。
