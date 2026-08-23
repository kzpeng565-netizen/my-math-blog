# PROJECT_STATE

<!-- ai_provenance: source=codex; date=2026-08-23; verification=checked -->

## 状态摘要

- 阶段：v1.0 收尾前的输入性能定位。
- 当前最高优先级：快速书写跟笔稍慢、连续笔画偶发掉笔。
- 策略：平板已回退旧版，先完成基线和单变量 A/B，再实施修复。
- 发布状态：尚未达到 v1.0 验收。

## 设备环境

- 平板：HUAWEI MatePad BAH3-W09。
- 手写笔：第一代 M-Pencil。
- 系统：HarmonyOS 3.0.0.167。
- Obsidian：1.13.7。
- Huawei WebView：114.0.5.302。
- 测试 Vault：`/storage/emulated/0/Documents/测试仓库`。
- 插件目录：`/storage/emulated/0/Documents/测试仓库/.obsidian/plugins/mathink-forge/`。

## 当前平板部署版

`artifacts/deployed-rollback/` 与平板已核对一致：

| 文件 | SHA-256 |
| --- | --- |
| `main.js` | `16D2C97D79EEC954A6CFC5B7F2ED99C52B4FA0F48375AD4756737EC361BF00EF` |
| `manifest.json` | `209821D82CEEFF24118571E831BE73654E766D8629C216248BEC6749B2EC43A9` |
| `styles.css` | `AE3960C8B6F717454D817A2973BC546EB5FDF6A456E47351B60EF39A669966F1` |

## 当前调查源码

- 分支：`codex/v1.0`。
- 上游基线 HEAD：`25515b65ce0ea9de47271f9b41c7c55cbc2605fa`。
- 源码工作区存在大量未提交的 v1.0 改动；本目录保存的是文件快照，不包含原仓库 `.git`。
- `artifacts/unconfirmed-current/main.js` SHA-256：`30F5D86BB0CDFDBB522E96A0225B3B0F72CDEE4F49B628C0DCB4900CD61B0328`。
- 此构建包含尚未确认的性能相关调整，当前未部署。

## 已掌握的笔记证据

- 旧快照：103 笔、1140 个点。
- 最新保存笔记：207 笔、2231 个点。
- 期间创建 105 笔，删除 1 笔，净增 104 笔。
- 最大 ID：`s208`；缺少 `s183`，与一次删除一致。
- 没有单点笔画；当前有 7 个两点笔画。
- 压力原始编码范围 89–229，换算约 0.349–0.898。
- 最新笔记文件 SHA-256：`CACFEA20502B1C527F3C3D199B925D30D59ADD96C0D3630168BE782D075ABB7D`。

这些统计能证明保存结构大体完整，但不能单独证明实时输入没有丢掉尚未进入文档的 pointerdown。

## 自动化与功能现状

- 最近一次完整自动化记录：29 个测试文件、246 个测试通过，覆盖率约 96.65%。
- 桌面侧已经验证笔画数量显示、撤销、重做正常。
- 平板插件已能加载并书写。
- 尚缺：定位快速书写延迟/掉笔；真实 JSON 导出文件；剩余物理设备 QA。

## 已知问题

1. 快速书写时跟笔稍慢，并可能掉笔。
2. 用户执行导出后，预期目录没有 JSON 文件；导出链路未闭环。
3. Input Lab/HUD、纸张自动扩展、每笔结束的布局工作与事件日志都有可能影响热路径，但目前都只是待验证假设。

## 风险

- 把多个推测性修复打成一包会无法判断根因。
- 只看界面笔画数量可能漏掉输入层根本没有收到的笔画。
- 在 Vault 内直接安装依赖会产生大量无关文件；开发副本应复制到 Vault 外。
