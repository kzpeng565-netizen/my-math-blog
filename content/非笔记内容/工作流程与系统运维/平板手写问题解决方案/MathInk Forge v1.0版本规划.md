# MathInk Forge v1.0 版本规划

> [!info] 版本含义
> 本文的 v1.0 指个人二次开发项目 `MathInk Forge v1.0`。上游 InkedMark 在 2026-08-20 的公开版本已经是 1.3.0；实施时必须记录具体上游 commit SHA，本文不把“上游 1.3.0”与“二次开发 v1.0”混为一谈。

<!-- ai_provenance: source=codex; date=2026-08-20; verification=source-backed; retrieved_notes="非笔记内容/工作流程与系统运维/平板手写问题解决方案/ChatGPT需求整理与初始计划.md" -->

## 一、版本目标

v1.0 的目标不是做出完整的专业手写软件，而是建立一个可以每天用于数学学习的最小闭环：

> 在目标华为平板上，用 M-Pencil 在 Obsidian 内稳定书写；常用数学笔一键切换；真实压感在设备允许时正确生效；笔迹保存后能够在 Windows 和平板上稳定重现；Codex 可以用实机采样在电脑端重放、测试和继续改进。

v1.0 成功后，日常流程应缩短为：

```text
打开 Obsidian 数学笔记
        ↓
选择常用笔预设
        ↓
直接手写推导
        ↓
保存并在电脑端继续整理/读取
```

## 二、发布阻断级目标

以下目标全部为 P0。任意一项未通过，均不能标记 v1.0 完成。

### 1. 固定且可复现的开发基线

- 建立独立二次开发仓库；
- 记录上游仓库地址、基线 commit SHA、Node/npm 版本；
- 决定独立插件 ID 和目录，防止上游更新覆盖；
- 明确原版与二次开发版不能同时启用；
- `npm ci`、lint、typecheck、test、build 均可在 Windows 重复执行。

### 2. Huawei Input Lab

在目标华为平板的 Obsidian WebView 内提供诊断页或诊断模式，实时显示并可导出：

- `pointerType`、`pointerId`、buttons；
- x/y、timestamp、事件来源；
- pressure 的当前值、最小值、最大值、均值、方差和分位数；
- tiltX/tiltY、twist 等存在时的值；
- pointer event 数、coalesced event 数；
- 事件间隔的 median、P95、最大值和长间隔计数；
- 设备型号、M-Pencil 代次、HarmonyOS、Obsidian 与 WebView 版本。

诊断必须能够区分：

1. 真实变化的压力；
2. 不支持压感时常见的固定 `0.5` 占位值；
3. 触摸或鼠标输入；
4. API 不存在或被 WebView 屏蔽。

### 3. Raw Stroke Dataset 与 Desktop Replay

- 可以从平板导出带 schema 版本的 JSON fixture；
- 可以在 Windows 加载 fixture 并经过与实机相同的 InputNormalizer、PressureMapper 和 Brush Engine 重绘；
- 至少建立 8 组固定样本：轻到重、重到轻、快写、慢写、圆、积分号、中文、完整数学公式；
- fixture 保留原始样本，不把渲染后的点冒充原始输入；
- 预测点不写入最终持久化数据。

### 4. PenPreset 数据模型与持久化

每支笔至少保存：

- 稳定 ID、名称、排序；
- pen/highlighter；
- color、size、opacity；
- pressure 开关、输入/输出范围、曲线和 gamma；
- thinning、smoothing、streamline；
- start/end taper；
- preset schema version。

必须支持：

- 新建、编辑、复制、删除、重命名、排序；
- JSON 导入与导出；
- 重启 Obsidian 后完整恢复；
- 非法数据拒绝导入并给出可理解的错误；
- ID 冲突时生成新 ID，不覆盖现有笔。

### 5. Pen Box 一键切换

- 工具栏直接显示 5–8 支常用笔；
- 点击一次即可恢复这支笔的完整配置；
- 当前激活笔有清晰状态；
- 新建和编辑进入二级界面，主书写界面不堆叠高级参数；
- 笔盒在触屏上不遮挡主要书写区域，按钮具备足够触控尺寸。

v1.0 至少自带：

1. 黑色公式笔；
2. 蓝色正文笔；
3. 红色批注笔；
4. 黄色高亮笔；
5. 绿色高亮笔。

### 6. PressureMapper 与参数化笔刷

- 使用独立纯函数完成压力归一化、钳制、曲线和输出范围映射；
- 内置 Linear、Soft、Medium、Hard 四条单调曲线；
- 真实压感可用时关闭 `perfect-freehand` 的模拟压力；
- 压感不可用时显式使用固定宽度或速度模拟回退，并在诊断界面说明；
- v1.0 只实现 `PerfectFreehandEngine`，不引入 C++/WASM 笔刷依赖；
- 任意合法参数不得产生 NaN、Infinity、空路径或画布崩溃。

### 7. 历史笔迹外观稳定

- 每条新 stroke 保存必要的 style snapshot；
- 修改、删除或导入预设不改变已经写出的 stroke；
- 旧 InkedMark 文档缺少新字段时仍按旧效果打开；
- 仅打开旧文档不能触发自动改写；
- 真正修改并保存时才进行受测试的惰性迁移；
- 未知的新 schema 版本必须只读或拒绝覆盖。

### 8. 保留上游核心能力

v1.0 不得破坏：

- dedicated `*.ink.md` 与 inline ink；
- 保存、关闭、重新打开；
- stroke eraser；
- 框选、移动、删除；
- undo/redo；
- pinch zoom、触摸平移和 palm rejection；
- Markdown text layer；
- Windows 与移动端的基本加载。

## 三、实现途径

### Stage 0：基线审查与安全准备

1. Fork/clone 上游并固定 commit SHA；
2. 阅读 README、CLAUDE.md、SPECIFICATION.md、QA.md、RELEASE.md、package.json；
3. 运行全部质量门；
4. 画出真实的 input → stroke → render → serialize 链路；
5. 建立需求矩阵：已有、扩展、重构、实机验证、延期；
6. 复制 5–20 份无敏感内容的旧笔记作为只读兼容 fixtures；
7. 对真实 Vault 做备份，开发和破坏性测试只在专用测试 Vault 进行。

交付物：`BASELINE_AUDIT.md`、固定 SHA、测试 Vault、旧文档 fixtures。

### Stage 1：统一输入与 Huawei Input Lab

1. 在现有 pointer controller 之后抽出 `InputNormalizer`；
2. 统一父事件、coalesced events 和预测事件的消费规则；
3. 扩展现有 debug HUD，避免另建平行诊断链；
4. 增加统计聚合和 raw stroke 录制；
5. 使用 Obsidian API 或浏览器下载能力导出 JSON，不依赖 Node/Electron；
6. 在目标华为平板实测并形成设备能力报告。

阶段门：能可靠回答 M-Pencil pressure、tilt、采样和 coalesced events 是否真实可用。

### Stage 2：Preset、Style Snapshot 与迁移 RFC

1. 定义 `PenPresetV1` 和校验器；
2. 定义 stroke style snapshot 的最小字段；
3. 定义默认值、ID 冲突、导入失败和未知版本行为；
4. 为上游旧文档写 decode/migrate/encode fixture 测试；
5. 先让测试覆盖迁移规则，再改实际序列化代码。

阶段门：修改预设不改变旧 stroke；旧笔记不因打开而被改写。

### Stage 3：PressureMapper 与 BrushEngineAdapter

1. 实现可单元测试的 PressureMapper；
2. 用 `easing` 和输入预处理映射到 `perfect-freehand`；
3. 把现有 freehand wrapper 收敛为 `PerfectFreehandEngine`；
4. 建立参数边界、异常值和单点/短笔画测试；
5. 使用 Stage 1 的 fixtures 对四条曲线生成固定视觉基线。

阶段门：相同 fixture + 相同 preset 得到确定性结果；所有合法参数均可安全渲染。

### Stage 4：Pen Box UI

1. 先完成 5 支内置笔和一键切换；
2. 再完成新建、编辑、复制、删除、排序；
3. 最后完成 JSON 导入/导出和冲突处理；
4. 主工具栏只显示常用笔，详细参数进入编辑面板；
5. 在横屏和竖屏华为平板上检查遮挡、误触和触控尺寸。

阶段门：不进入设置页即可完成一整页数学笔记的常用切笔。

### Stage 5：Desktop Replay 与回归测试

1. 加载标准 fixture；
2. 选择 preset 并实时重绘；
3. 并排显示 raw input、当前输出和参考图；
4. 为无 NaN/越界、确定性输出、路径 bounds 和序列化建立自动测试；
5. 保存少量稳定 PNG 或几何快照用于 visual regression。

阶段门：Codex 在没有 M-Pencil 的 Windows 环境中也能复现并验证主要笔刷改动。

### Stage 6：实机验收、打包与回退

1. 在专用测试 Vault 执行完整验收清单；
2. 在 Windows 和目标华为平板打开同一批测试笔记；
3. 完成 30 分钟数学书写耐久测试；
4. 生成 `main.js`、`manifest.json`、`styles.css`；
5. 写明基线 SHA、安装方法、已知限制和回退方法；
6. 保留上一可用版本安装包。

## 四、验收标准

### A. 自动质量门

- `npm ci` 成功；
- lint 零 warning；
- typecheck 成功；
- 全部单元测试成功；
- production build 成功；
- CI 在干净环境重复通过；
- `model/`、`ink/`、新增 input/preset/migration 纯逻辑的覆盖率不低于 80%。

### B. 输入诊断验收

- Huawei Input Lab 能导出完整 JSON；
- 一次诊断至少包含 50 个 pen 样本才判断压感能力；
- 若 `max(pressure) - min(pressure) < 0.05` 或压力长期固定为 `0.5`，报告必须标记为“未证明真实压感”，不得显示“压感正常”；
- coalesced events 存在时只消费合并样本，不重复消费父事件；
- API 缺失时普通 `pointermove` 路径仍可书写；
- 报告包含事件间隔 median/P95/max，不只给平均值。

### C. Pen Box 验收

- 5 支默认笔均可一次点击切换；
- 连续切换 20 次，颜色、宽度、工具和压力参数无错配；
- 重启 Obsidian 后预设内容和顺序完全恢复；
- 新建、编辑、复制、删除、排序各执行 5 次无错误；
- 导出后清空测试设置并重新导入，得到等价配置；
- 导入损坏 JSON 不改变现有配置；
- 编辑预设前写 10 条 stroke，编辑后旧 stroke 的几何与样式不变。

### D. 压力与笔刷验收

- 四条压力曲线满足端点确定、输出有界、单调不减；
- 同一 fixture 与 preset 重放 10 次得到相同几何结果；
- 单点、极短笔画、重复点、零时间差和异常压力值均不产生 NaN/Infinity；
- 真实压感可用时，轻压和重压 fixture 的平均线宽存在稳定、可见差异；
- 压感不可用时仍能用固定宽度流畅书写，并明确显示 fallback 状态；
- pen 与 highlighter 的 opacity 和混合效果在 Windows/华为平板上均可接受。

### E. 数据兼容验收

- 至少 5 份上游旧笔记可打开；建议最终扩大到 20 份；
- 旧笔记仅打开并关闭时文件 hash 不变；
- 修改并保存后可再次打开，笔画数量、位置、颜色和宽度保持；
- 连续保存/关闭/重开 10 轮无数据丢失；
- 未知 schema 和损坏 payload 不被静默覆盖；
- Windows 与华为平板打开同一文件，笔画数量一致且没有明显视觉漂移。

### F. 日常使用验收

在目标华为平板完成一次 30 分钟真实数学书写：

- 至少使用黑色公式笔、蓝色正文笔、红色批注笔和一种高亮笔；
- 写出中文、英文、积分、分式、上下标、圆和快速连写；
- 期间执行撤销、重做、橡皮、缩放和平移；
- 不出现可复现的丢笔、重复笔画、意外手掌落墨或工具状态错乱；
- 书写后保存，在 Windows 打开并继续编辑，再回平板打开；
- 往返操作过程不破坏 Markdown text layer 或 inline ink block。

### G. 发布物验收

- 安装包包含且只依赖 Obsidian 插件所需发布文件；
- 版本说明记录上游基线 SHA、设备测试矩阵、已知限制和数据迁移说明；
- 有明确的卸载/回退步骤；
- 上一可用安装包和测试笔记备份可恢复；
- 原版与二次开发版的互斥说明清楚可见。

## 五、v1.0 不做的功能

- tilt/directional nib；
- 铅笔纹理和 GPU 特效；
- partial stroke eraser；
- pressure-sensitive eraser radius；
- Google Ink/WASM 集成；
- OCR、手写识别和 AI 自动调参；
- 华为原生 SDK、Android 原生模块或修改 Obsidian APK；
- 多人协作、云服务和完整商业手写软件复刻。

这些功能只有在 v1.0 的数据模型、输入诊断、回放和兼容测试稳定后才进入后续版本。

## 六、Go / No-Go 规则

出现以下任一情况，应停止新增功能并先解决基础问题：

- 旧笔记可能被静默损坏或覆盖；
- 输入链稳定丢点、重复点或出现不可接受的延迟；
- 无法证明真实压感，却把固定 `0.5` 当作压感；
- 修改预设会改变历史笔迹；
- Windows 与目标华为平板无法稳定打开同一文档；
- 质量门不能在干净环境重复通过；
- 没有可执行的回退方案。

## 七、启动实施前需要记录的信息

- 华为平板准确型号；
- M-Pencil 代次；
- HarmonyOS 版本；
- Obsidian 版本；
- Android System WebView/Chromium 版本；
- 当前 InkedMark 安装来源和版本；
- 上游基线 commit SHA；
- 测试 Vault 路径；
- 旧笔记 fixtures 的备份位置。

## 八、参考资料

- [InkedMark 官方仓库](https://github.com/pcrausaz/obsidian-inkedmark)
- [InkedMark 技术规格](https://github.com/pcrausaz/obsidian-inkedmark/blob/main/SPECIFICATION.md)
- [perfect-freehand 官方文档](https://github.com/steveruizok/perfect-freehand)
- [W3C Pointer Events Level 3](https://www.w3.org/TR/pointerevents3/)
- [Google Ink Stroke Modeler](https://github.com/google/ink-stroke-modeler)
- [Obsidian 移动端插件开发](https://docs.obsidian.md/Plugins/Getting%20started/Mobile%20development)
- [Obsidian 插件开发政策](https://docs.obsidian.md/community-directory/developer-policies)
- [Huawei Notes 官方使用说明](https://consumer.huawei.com/en/support/content/en-us15960169/)
- [Samsung Notes 官方手写说明](https://www.samsung.com/in/support/mobile-devices/how-to-use-samsung-notes/)
- [Concepts Tool Wheel 官方手册](https://concepts.app/en/manual/workspace)

## 九、实施状态（2026-08-20）

> [!warning] 当前结论：软件实现与自动门禁完成，v1.0 发布仍为 No-Go
> Windows 上可自动完成的实现、测试、构建、隔离部署和打包已经完成；但本计划把华为平板/M-Pencil 实机能力、30 分钟书写与华为→Windows→华为往返列为 P0，因此在真机证据填写前不能声称 v1.0 已最终验收。

- 独立源码仓库：`D:\InkedMark-Advanced`；
- 分支：`codex/v1.0`；上游固定为 `25515b65ce0ea9de47271f9b41c7c55cbc2605fa`；
- 正式名称：`MathInk Forge`；独立插件 ID：`mathink-forge`，未覆盖 Vault 中已有的 `inkedmark` 及其 `data.json`；
- 专用测试 Vault：`D:\InkedMark-Advanced-TestVault`；
- 发布包：`D:\MathInk-Forge-Release\mathink-forge-1.0.0.zip`；
- 回退包：`D:\MathInk-Forge-Release\rollback-upstream-inkedmark-1.3.0.zip`，仅含上游 1.3.0 三个发布文件，明确排除 `data.json`；
- 华为实机测试包：`D:\MathInk-Forge-Device-Test-Kit.zip`，包含候选包、回退包、12 组输入 fixture、5 份旧笔记、QA、设备报告模板和完整性哈希；
- 已实现：5 支默认笔、Pen Box CRUD/排序/导入导出、四条压力曲线、每笔 style snapshot、v1→v2 真正的惰性迁移（未编辑时保留原始字节）、未来 schema 拒绝覆盖、Input Lab 增强实时 HUD/录制/统计/导出、共用 InputNormalizer、Desktop Replay 三栏对比；
- 数据集：12 组输入 fixture，包含轻→重、重→轻、快写、慢写、圆、积分号、中文和完整公式；另有 5 份无敏感内容的上游 v1 兼容笔记；
- 自动结果：format、lint、plugin-review lint、typecheck、239 项测试、production build 全部通过；总体行覆盖率 `96.71%`，`ink/` 为 `96.52%`，`input/` 为 `88.38%`，`model/` 为 `98.85%`；12 组 fixture 均有固定 SHA-256 几何基线；
- ==已重新执行一次干净 `npm ci`：按锁文件安装 454 个包，审计为 0 个漏洞；随后重新执行 format、lint、plugin-review lint、typecheck、239 项测试、coverage 与 production build，全部通过。==
- 构建产物只有 `main.js`、`manifest.json`、`styles.css`，与测试 Vault 部署文件 SHA-256 一致；
- 仓库内验收文件：`MATHINK_FORGE_V1_QA.md`、`DEVICE_TEST_REPORT_TEMPLATE.md`、`RELEASE_V1.0.md`、`BASELINE_AUDIT.md`；
- 交接入口：`HANDOFF.md`，并配套 `DECISIONS.md`、`PROJECT_STATE.md`、`NEXT_STEPS.md`。
- Windows 冒烟报告：`WINDOWS_SMOKE_REPORT.md`；已实证插件命令加载、新建手写笔记、完整工具栏、9 条鼠标笔画保存、颜色切换、style snapshot 与持久化撤销，剩余交互项仍未冒充通过。
- ==2026-08-20 复测：Obsidian 重新加载后，测试笔记仍正确显示 8 条已保存笔画；实测发现 Input Lab 停止/导出命令依赖 active view 而消失，现已改为查找实际录制中的 ink leaf，并重新通过 239 项测试（含回归保护）、覆盖率与 production build。停止/导出的人工复测仍待完成。==
- ==五份旧笔记在迁移后均通过纯数据层连续编码/重开 10 轮，stroke regions 保持一致；真实 Obsidian 与跨设备的 10 轮重开仍按 P0 实机门禁执行。==
- ==用户已确认重新加载后的新建笔画、撤销、重做在界面中按 `8→9→8→9` 正常工作；当前磁盘快照仍是此前的 8 笔状态，因此最终重做到磁盘并重开的证据仍单独保留为待验项。==
- ==当前候选包 SHA-256：`432B33349C21F5B0774B6EA10FF501F1E9F40001C064D6C3BB13A1EF1C17AE27`；华为实机测试包 SHA-256：`3DAC94A3FFD1FFFE0C67CA33B4131BFFE286A7BC3E384F3363487031C6E7CE81`。==
<!-- ai_provenance: source=codex; date=2026-08-20; verification=user-confirmed; retrieved_notes="非笔记内容/工作流程与系统运维/平板手写问题解决方案/MathInk Forge v1.0版本规划.md" -->

剩余发布阻断项：

1. 在目标华为平板填写准确型号、M-Pencil 代次、HarmonyOS、Obsidian 与 WebView 版本；
2. 导出至少 50 个 pen 样本，确认压力 verdict、median/P95/max 间隔和 coalesced/predicted API；
3. 完成 Pen Box 20 次切换、CRUD/排序各 5 次、重启恢复和损坏 JSON 测试；
4. 完成 30 分钟数学书写以及橡皮、框选、撤销/重做、缩放、平移和防误触验收；
5. 完成华为→Windows→华为往返与旧笔记 10 轮保存/重开；
6. 将真机 JSON、文件 hash 和结论填写到设备测试报告，全部 P0 通过后再把发布结论改为 Go。
