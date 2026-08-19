# InkedMark 二次开发项目需求与实施方向

## 一、项目目标

基于 Obsidian 的 InkedMark 插件进行二次开发，使其更适合长期数学学习、数学笔记和手写推导场景。

项目重点不是重新开发一个完整笔记软件，也不是脱离 Obsidian 单独做手写应用，而是在尽量保留 InkedMark 现有架构、Markdown 集成、Obsidian 数据管理和跨平台能力的前提下，显著增强其手写体验。

最终目标是：

- Obsidian 继续作为唯一的知识管理环境；
    
- Markdown 笔记和手写笔记能够自然共存；
    
- 手写体验接近成熟平板笔记软件；
    
- 支持 Huawei M-Pencil 等触控笔的压力信息；
    
- 用户可以创建和保存自己的笔刷预设；
    
- 电脑端可以使用 Codex 等 AI 持续修改、测试和维护插件；
    
- 修改后的插件可以正常运行于支持 Android APK 的旧版 HarmonyOS 华为平板 Obsidian；
    
- 尽量维持 Windows、Android、iPad 等平台之间的兼容性，而不是做成只能运行于华为设备的专用版本。
    

---

# 二、当前实际使用场景

目前主要工作流程是：

- 平板承担数学手写、推导、草稿和思考；
    
- 电脑使用 Obsidian 管理正式数学笔记；
    
- AI 读取 Obsidian 知识库，辅助整理、分析、学习和问答。
    

现有问题是：

平板手写和 Obsidian 笔记之间存在明显割裂。

数学内容经常需要：

- 在平板上先手写；
    
- 再回电脑整理；
    
- 再输入 Obsidian；
    
- 之后 AI 才能读取。
    

这造成较高的二次整理成本。

同时，普通电子手写软件虽然书写体验较好，但搜索、双链、长期知识管理和 AI 集成能力不足。

因此希望直接把高质量手写能力引入 Obsidian，使：

> 手写、Markdown、知识管理和 AI 工作流处于同一个环境中。

---

# 三、项目定位

本项目应当理解为：

> 在 InkedMark 基础上增加一个更成熟的 Ink Engine 和 Pen Box，而不是简单增加几个颜色按钮。

建议整体保持以下结构：

```text
Obsidian / InkedMark
        │
        ▼
Pen Box / 笔盒
        │
        ▼
Brush / Ink Engine
        │
        ▼
Input Layer
        │
        ▼
Stylus / Huawei M-Pencil
```

其中：

### Obsidian / InkedMark

继续负责：

- Markdown；
    
- 笔记文件；
    
- 手写内容嵌入；
    
- Vault；
    
- 搜索；
    
- 双链；
    
- AI 可访问的数据；
    
- 桌面和移动端运行环境。
    

### Pen Box

负责：

- 用户创建自己的笔；
    
- 保存笔的完整参数；
    
- 快速调用；
    
- 修改；
    
- 排序；
    
- 复制；
    
- 删除；
    
- 导入导出。
    

### Brush / Ink Engine

负责：

- 笔宽；
    
- 压感；
    
- 压力曲线；
    
- 笔锋；
    
- smoothing；
    
- streamline；
    
- taper；
    
- opacity；
    
- highlighter；
    
- 不同笔型；
    
- 后续可能的 tilt、texture 等。
    

### Input Layer

负责读取触控笔数据，包括：

- x / y；
    
- timestamp；
    
- pressure；
    
- tilt；
    
- coalesced events；
    
- pointer type；
    
- 设备能够提供的其他 PointerEvent 数据。
    

---

# 四、第一项工作：完整检查 InkedMark 当前代码

正式修改之前，需要先对 InkedMark 仓库进行完整检查。

重点确认：

## 1. 项目整体架构

确认：

- 插件入口；
    
- 文件结构；
    
- drawing view；
    
- inline handwriting；
    
- canvas renderer；
    
- wet/dry stroke rendering；
    
- toolbar；
    
- settings；
    
- document model；
    
- serialization；
    
- migration；
    
- tests；
    
- build 流程。
    

明确哪些模块可以保留，哪些模块适合扩展，哪些模块需要重构。

---

## 2. 当前手写输入流程

重点检查从：

```text
PointerEvent
→ pointer controller
→ stroke builder
→ stroke model
→ freehand algorithm
→ renderer
```

完整链路。

确认当前是否以及如何处理：

- pressure；
    
- tiltX；
    
- tiltY；
    
- timestamp；
    
- coalesced events；
    
- palm rejection；
    
- pointerType；
    
- sampling；
    
- smoothing。
    

---

## 3. 当前数据模型

确认每条 Stroke 当前保存哪些数据。

尤其检查：

- point 数据；
    
- pressure；
    
- color；
    
- size；
    
- tool；
    
- pen/highlighter 类型；
    
- serialization；
    
- compression；
    
- version migration。
    

后续扩展数据结构时，必须保证旧 InkedMark 笔记仍可正常打开。

---

## 4. 当前笔刷实现

重点研究 InkedMark 对 `perfect-freehand` 的使用方式。

确认：

- 哪些参数目前已经开放；
    
- 哪些参数被写死；
    
- pressure 如何映射；
    
- thinning；
    
- smoothing；
    
- streamline；
    
- taper；
    
- simulated pressure；
    
- polygon / outline 生成方式。
    

优先利用已有成熟算法，不重新发明笔迹算法。

---

# 五、需要进行的外部资料调研

正式设计新的 Brush Engine 前，需要搜索和研究成熟实现。

重点包括以下几类。

## 1. perfect-freehand

研究其所有可调参数和适合手写的能力，例如：

- pressure；
    
- size；
    
- thinning；
    
- smoothing；
    
- streamline；
    
- easing；
    
- taper；
    
- cap；
    
- simulated pressure。
    

判断第一阶段能在多大程度上直接依赖 perfect-freehand。

---

## 2. Web Pointer Events

研究浏览器 / WebView 可以提供的触控笔信息，例如：

- pressure；
    
- tiltX；
    
- tiltY；
    
- twist；
    
- tangentialPressure；
    
- altitudeAngle；
    
- azimuthAngle；
    
- coalesced events。
    

重点确认 Android / HarmonyOS WebView 实际可用情况。

---

## 3. Google Ink / Ink Stroke Modeler

研究 Google 已公开的 Ink 架构和开源实现。

重点参考：

- Stroke Input；
    
- Brush；
    
- BrushFamily；
    
- Stroke geometry；
    
- prediction；
    
- smoothing；
    
- low-latency authoring；
    
- pressure；
    
- tilt；
    
- custom brushes；
    
- eraser。
    

主要用于借鉴架构、算法思想和开放实现。

不要直接把 Android 原生架构强行集成到 Obsidian，除非后续确认必要。

---

## 4. 成熟笔记软件

调研：

- Huawei Notes；
    
- Goodnotes；
    
- Notability；
    
- Samsung Notes；
    
- OneNote；
    
- Concepts；
    
- 其他优秀 Stylus 应用。
    

重点学习：

- 笔盒 UI；
    
- 常用笔切换；
    
- 长按编辑；
    
- 色彩预设；
    
- 笔宽选择；
    
- pressure 行为；
    
- eraser 行为；
    
- highlighter 行为；
    
- toolbar ergonomics。
    

主要借鉴用户交互和效果，不要求逆向商业软件实现。

---

# 六、核心功能需求

## 1. Pen Box / 自定义笔盒

用户必须能够创建自己的笔刷预设。

每一支笔应当独立保存自己的全部参数。

例如用户可以创建：

- 黑色公式笔；
    
- 蓝色正文笔；
    
- 红色批注笔；
    
- 铅笔；
    
- 钢笔；
    
- 黄色荧光笔；
    
- 绿色荧光笔。
    

用户点击笔盒中的一支笔后，应当立即恢复这支笔的完整配置，而不是重新分别选择：

- tool；
    
- color；
    
- width；
    
- pressure。
    

---

## 2. 笔预设管理

至少考虑支持：

- 新建；
    
- 修改；
    
- 复制；
    
- 删除；
    
- 重命名；
    
- 排序；
    
- 收藏；
    
- 导入；
    
- 导出。
    

UI 方向可以参考成熟笔记软件。

原则是：

> 常用笔一次点击即可切换。

高级参数可以隐藏在长按或编辑页面中。

---

# 七、每支笔需要支持的参数

第一阶段至少考虑以下参数。

## 基础参数

- 颜色；
    
- 基础宽度；
    
- opacity；
    
- pen / highlighter；
    
- brush type。
    

---

## Pressure

需要真正支持 pressure，而不只是简单把 0～1 原样传入。

至少考虑：

- 是否启用压力；
    
- minimum pressure；
    
- maximum pressure；
    
- pressure sensitivity；
    
- pressure gamma；
    
- pressure curve；
    
- thinning。
    

建议内置若干曲线：

- Linear；
    
- Soft；
    
- Medium；
    
- Hard。
    

未来可以考虑 Custom Curve。

---

## 笔锋

笔锋不要只设计成一个单独的“笔锋强度”。

应当逐步考虑：

- Pressure → width；
    
- Velocity → width；
    
- stroke direction；
    
- nib direction；
    
- tilt；
    
- start taper；
    
- end taper。
    

第一阶段可以先实现 pressure-based width 和 taper。

---

## 稳定与平滑

允许不同笔分别设置：

- smoothing；
    
- streamline；
    
- stabilization。
    

不同用途的笔应该允许不同参数。

例如：

数学公式笔：

- 比较稳定；
    
- 较小线宽变化；
    
- 较弱 pressure。
    

自然书写笔：

- 较明显 pressure；
    
- 更自然笔锋。
    

---

# 八、颜色体系

颜色不应该只是一个全局 Color Picker。

用户应该能够：

- 给每一支笔保存自己的颜色；
    
- 保存常用颜色；
    
- 快速切换；
    
- 创建自己的颜色体系。
    

例如：

```text
黑色公式笔
蓝色正文笔
红色批注笔
绿色辅助笔
黄色高亮
绿色高亮
```

点击笔预设即可同时切换颜色和其他参数。

---

# 九、橡皮擦

需要考虑独立的 Eraser Engine。

第一阶段优先实现：

## Stroke Eraser

碰到一条 stroke 后删除整条笔迹。

支持：

- 基础半径；
    
- pressure-sensitive radius。
    

例如：

轻压时橡皮较小，重压时擦除范围变大。

---

后续阶段再考虑：

## Partial Stroke Eraser

真正切断一条 stroke，只删除被擦到的部分。

该功能复杂度较高，不作为最早阶段的必要功能。

---

# 十、Huawei M-Pencil 输入检测

在大量开发笔刷之前，需要先确认实际设备能够提供哪些输入。

建议首先制作 Huawei Input Diagnostic / Input Lab。

能够实时显示：

- pointerType；
    
- pressure；
    
- tiltX；
    
- tiltY；
    
- timestamp；
    
- event frequency；
    
- coalesced event 数量；
    
- event gap；
    
- 其他可获得的 stylus 数据。
    

目标是回答几个关键问题：

1. M-Pencil pressure 是否可以被 Obsidian WebView 正常读取？
    
2. pressure 范围是否真实变化？
    
3. tilt 是否存在？
    
4. event sampling rate 是否足够？
    
5. coalesced events 是否可用？
    
6. 是否存在明显输入延迟或数据丢失？
    

只有确认实际硬件数据之后，才决定是否开发 tilt brush 等高级功能。

---

# 十一、Raw Stroke Dataset

Diagnostic 不应该只显示数据。

需要考虑增加：

> Record Stroke Input

把用户真实书写时产生的原始输入保存成测试数据。

例如记录：

- x；
    
- y；
    
- timestamp；
    
- pressure；
    
- tilt；
    
- 其他 stylus 数据。
    

建立标准测试数据集，例如：

```text
pressure-light-heavy
fast-writing
slow-writing
curves
circles
integral
math-formula
chinese-writing
english-writing
```

这些数据用于电脑端重放。

---

# 十二、Desktop Stroke Replay

这是 AI 辅助开发的重要功能。

目标是：

在 Windows 电脑上，不需要真正拿 M-Pencil，也可以加载真实华为平板采集的数据并重新渲染笔迹。

流程：

```text
Huawei M-Pencil
        ↓
Raw Stroke Dataset
        ↓
电脑
        ↓
Stroke Replay
        ↓
Brush Engine
        ↓
Rendered Result
```

这样 Codex 修改：

- pressure curve；
    
- smoothing；
    
- thinning；
    
- taper；
    
- brush algorithm；
    

以后可以直接在电脑上看到结果。

减少：

> 改电脑代码 → 复制到平板 → 写几笔 → 回电脑继续修改

这种低效率循环。

---

# 十三、Brush Lab

后续建议增加一个内部开发工具：

> Brush Lab

用于开发和调试笔刷。

提供标准测试：

- 从轻到重；
    
- 从重到轻；
    
- 快速横线；
    
- 慢速横线；
    
- 曲线；
    
- 圆；
    
- 中文；
    
- 英文；
    
- 数学公式；
    
- 积分号；
    
- 极限；
    
- 分数；
    
- 上下标。
    

修改笔刷参数后能够实时重绘。

---

# 十四、成熟软件效果参考

不建议把逆向、监听商业软件内部日志作为项目主要路线。

更推荐建立：

> Reference Images + Raw Stroke Fixtures

例如：

使用同一个人、同一支 M-Pencil，在 Huawei Notes 中书写一组标准内容。

保存效果截图作为视觉参考：

```text
Huawei Notes
- pressure test
- integral
- chinese text
- math formula
- curves
```

然后在 InkedMark 中使用相同的标准输入数据。

AI 可以比较：

```text
目标效果
vs
当前 InkedMark 效果
```

然后调整：

- pressure；
    
- thickness；
    
- smoothing；
    
- taper；
    
- opacity；
    
- brush algorithm。
    

---

# 十五、AI 辅助笔刷调优

希望最终开发流程能够支持：

```text
Reference Image
+
Raw Stroke Dataset
+
Current Brush Parameters
        ↓
AI
        ↓
生成多组候选参数
        ↓
A / B / C / D
        ↓
用户选择更喜欢的一组
        ↓
继续微调
```

AI 不只是负责写代码，也可以负责：

- 分析效果差异；
    
- 给出参数建议；
    
- 生成候选 Preset；
    
- 比较 before / after；
    
- 自动执行 visual regression。
    

最终保存成新的用户笔预设。

---

# 十六、Brush Engine 架构要求

不要把所有笔型永久绑定到一个算法。

建议设计一个抽象 Brush Engine。

例如：

```text
BrushEngine

├─ PerfectFreehandEngine
│  ├─ Technical Pen
│  ├─ Ballpoint
│  └─ Fountain Pen
│
├─ PencilEngine
│
├─ MarkerEngine
│
└─ EraserEngine
```

第一阶段可以主要依赖 `perfect-freehand`。

未来如果出现更成熟算法，可以增加新 Engine，而不是推翻整个笔记数据结构。

---

# 十七、笔迹数据与 Preset 必须分离

这一点非常重要。

PenPreset 是：

> 用户以后继续使用的笔模板。

而已经写进笔记的 Stroke 必须保存：

> 当时实际使用的视觉参数。

不能简单只保存：

```text
presetId = "math-black"
```

否则用户以后修改 `math-black`，旧笔记可能全部改变外观。

应该让每条 Stroke 保存对应的 style snapshot，至少保存能够稳定重现历史笔迹的必要参数。

目标是：

> 几年以后重新打开笔记，旧笔迹仍保持原样。

---

# 十八、兼容旧 InkedMark 数据

所有数据结构修改都必须考虑：

- schema version；
    
- migration；
    
- backward compatibility。
    

旧 InkedMark 笔记必须继续能够读取。

增加：

- tilt；
    
- timestamp；
    
- brush；
    
- pressure curve；
    
- style snapshot；
    

时，不允许破坏现有数据。

---

# 十九、跨平台要求

一个核心要求是：

> 插件必须继续保持 Obsidian 普通插件的开发模式。

优先使用：

- TypeScript；
    
- JavaScript；
    
- Web Canvas；
    
- Pointer Events；
    
- Web APIs；
    
- 必要时 WASM。
    

尽量避免：

- Huawei SDK；
    
- Android native API；
    
- Kotlin；
    
- Java；
    
- 修改 Obsidian APK；
    
- 强依赖特定系统接口。
    

原因是需要保持：

```text
Windows
Codex / VS Code
        ↓
npm build
        ↓
Obsidian Plugin
        ↓
同步到 Huawei Tablet
        ↓
Reload Plugin
```

这一开发体验。

---

# 二十、Huawei 不是唯一目标平台

华为平板和 M-Pencil 是当前主要设备和主要测试目标。

但插件设计不应该写成：

> HuaweiInkPlugin

更合理的目标是：

> Advanced InkedMark / Advanced Web Stylus Engine

在浏览器 PointerEvent 能够提供相应数据的情况下，理论上也应该能够支持：

- Huawei tablet；
    
- Android tablet；
    
- iPad；
    
- Windows touch device；
    
- 其他 stylus。
    

---

# 二十一、开发原则

开发过程中优先遵循：

### 1. 不重写已经成熟的东西

能够使用：

- InkedMark；
    
- perfect-freehand；
    
- Google 开源算法；
    
- Web Pointer Events；
    

解决的问题不要从零重新实现。

---

### 2. 用户体验优先

目标不是提供几十个参数。

目标是：

> 默认已经很好写。

高级用户再进入设置调节。

日常写数学时，应该主要通过 Pen Box 快速切换。

---

### 3. Preset 优先

用户不应该每天调整：

- pressure；
    
- width；
    
- smoothing。
    

这些参数调整完成后应该保存为笔。

---

### 4. AI 可测试

项目从一开始就要建立：

- raw stroke fixtures；
    
- replay；
    
- automated tests；
    
- visual regression；
    
- reference images。
    

尽量让 Codex 自己能够判断一次修改是否造成退化。

---

### 5. 不过早实现高级功能

优先确保：

- pressure；
    
- pen preset；
    
- pen box；
    
- width；
    
- color；
    
- smoothing；
    
- reliable rendering。
    

之后再考虑：

- tilt；
    
- pencil texture；
    
- directional nib；
    
- partial eraser；
    
- advanced GPU effects。
    

---

# 二十二、建议的大致开发阶段

## Phase 0：Repository Audit + Research

完成：

- 阅读 InkedMark 代码；
    
- 画出当前架构；
    
- 确认数据链路；
    
- 阅读相关文档和开源项目；
    
- 找出需要修改的模块；
    
- 建立开发分支。
    

这一阶段先不要大规模修改功能。

---

## Phase 1：Huawei Input Lab

完成：

- stylus diagnostics；
    
- pressure detection；
    
- tilt detection；
    
- event statistics；
    
- raw stroke recording；
    
- JSON export；
    
- desktop replay。
    

确认 M-Pencil 实际能够提供什么数据。

---

## Phase 2：PenPreset + Pen Box

完成：

- PenPreset 数据模型；
    
- 笔盒；
    
- 新建；
    
- 编辑；
    
- 删除；
    
- 复制；
    
- 排序；
    
- 快速切换；
    
- 颜色；
    
- 宽度；
    
- pressure 配置。
    

---

## Phase 3：Pressure / Brush Engine

在现有 perfect-freehand 上增加：

- pressure mapping；
    
- pressure curve；
    
- min/max；
    
- gamma；
    
- thinning；
    
- smoothing；
    
- streamline；
    
- taper。
    

制作几个适合数学笔记的默认笔。

---

## Phase 4：Brush Lab + AI Tuning

完成：

- standardized fixtures；
    
- visual comparison；
    
- reference images；
    
- before / after；
    
- 参数候选；
    
- preset export/import。
    

让 AI 能够辅助真正的笔感调试。

---

## Phase 5：Advanced Brushes

根据实际需求逐步增加：

- fountain pen；
    
- pencil；
    
- marker；
    
- tilt；
    
- directional nib；
    
- texture。
    

---

## Phase 6：Advanced Eraser

增加：

- pressure-sensitive eraser；
    
- partial stroke eraser；
    
- stroke splitting。
    

---

# 二十三、第一阶段暂时不要求完成的东西

当前不要优先：

- 完整复刻 Goodnotes；
    
- 完整复刻 Huawei Notes；
    
- OCR；
    
- handwriting recognition；
    
- AI 自动识别所有手写内容；
    
- 云端服务；
    
- 多人协作；
    
- 原生 Android 应用；
    
- 修改 Obsidian APK；
    
- 高复杂度 GPU 笔刷；
    
- 完整铅笔材质模拟。
    

核心目标始终是：

> 首先让 Obsidian 内的数学书写真正舒服。

---

# 二十四、希望 Codex 首先完成的工作

在写任何大型功能之前，请先：

1. 获取并完整检查 InkedMark 当前仓库；
    
2. 阅读 README、CLAUDE.md、SPECIFICATION、package.json 以及相关测试；
    
3. 梳理整个 stylus input → stroke → render → serialize 流程；
    
4. 标出涉及 pressure、tilt、perfect-freehand、toolbar、settings、document model 的代码位置；
    
5. 检查当前 mobile / Android 支持方式；
    
6. 调研 perfect-freehand、Pointer Events、Google Ink / ink-stroke-modeler 等成熟实现；
    
7. 判断以上需求哪些可以直接扩展现有模块，哪些需要新抽象；
    
8. 给出建议的模块架构；
    
9. 给出数据兼容和 migration 方案方向；
    
10. 给出分阶段实施计划；
    
11. 在完成代码审查和方案设计以前，不要进行大规模重构。
    

最终原则：

> 在尽可能少破坏 InkedMark 原有能力的情况下，把它发展成一个适合数学学习、拥有成熟 Pen Box 和高级 Stylus 参数、能够由 AI 持续调试和维护、同时保持 Obsidian 跨平台运行能力的手写插件。