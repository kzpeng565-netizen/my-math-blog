# 我的专注花园 · 系统运维 Canvas 导航与维护说明

<!-- ai_provenance: source=claude; date=2026-08-08; verification=json-validated; based_on=工作流程与系统运维 目录下交接/边界文档（2026-08-08 版） -->

本目录存放 4 张用于辅助长期维护的 Obsidian Canvas。它们不是新的权威源——**运行真相以 Pi 生产环境与交接文档为准**，Canvas 只是索引和导航层。每张图的节点都带职责、运行位置、关键路径/端口，并有对应文档的 file 节点（紫色，可直接点击打开）。

## 文件清单与用途

| 文件 | 用途 | 主要分组 |
|---|---|---|
| `00-总体流程总览.canvas` | 跨设备全景：数据如何从手机/平板/电脑流入 Pi，如何处理、决策、通知回流。改任何一端前先看这里 | 手机端 / 平板端 / 电脑端 / 网络边界(Tailscale) / 树莓派 / 外部服务 / 权威文档 |
| `01-手机端内部流程.canvas` | 手机侧两条链路：Automate 采集上传 + Focus Bridge 介入桥接，以及与 Pi 的交互（token 校验、介入调度、幂等） | Automate 采集 / Focus Bridge 组件 / 执行端 / 网络路径 / Pi 交互侧 / 故障排查入口 / 文档 |
| `02-电脑端内部流程.canvas` | Windows 侧：ActivityWatch 采集与同步、Obsidian 任务上下文单向链路、New Pomodoro Timer 与 Pi 会话同步、介入 Agent 与 Cold Turkey、Clash 代理绕过 | ActivityWatch / Obsidian 与番茄钟 / 介入 Agent 域 / 管理支撑 / Pi 交互侧 / 文档 |
| `03-Pi内部流程.canvas` | Pi 侧全景：接收层、半小时处理链、Obsidian 上下文、提醒 timers、Next Action 决策、专注花园与备份、反馈回流 | 数据接收层 / 半小时处理链 / Obsidian 上下文 / 提醒与统计 / Next Action / 专注花园 / 反馈回流 / 文档 |

## 读图约定（每张图右上角也有图例节点）

- 🟢 绿 = 自动流程 / 服务；🟡 黄 = 数据 / 配置 / 状态；🔵 青 = 网络边界 / 接口
- 🟣 紫 = 文档节点（点击直接打开对应交接笔记）
- 🔴 红 = 人工操作 / 故障入口；🟠 橙 = ⚠️ 待确认
- 边 = 数据流 / 触发关系（标签为传输内容与方式）；边上的依赖关系同时提示**修改影响面**：改一个模块前，先看它的入边（它依赖谁）和出边（谁依赖它）

## ⚠️ 待确认项汇总（不要自行补全）

按 Canvas 归属列出；均来自文档间的冲突或文档明确标注"未实施/无法确认"。

### 总体（00）
1. 平板行为采集现状：文档存在 `tablet_*` 上传接口与 `tablet_facts`（总流程图含平板采集），但近期文档称"平板不作为提醒触发设备"，且只有 USB 投屏记录。**是否恢复采集未知**。
2. Focus Bridge 公网主链路 `pi.taild4d3f7.ts.net/focus-bridge/*` 是否经 Tailscale Funnel 代理，文档未明说（迁移流程只写 public_https 主链路 + tailnet_fallback）。

### 手机端（01）
3. 手机是否安装/启用 Tailscale：旧文档（2026-07-24）称"手机不装 Tailscale"（与 Clash 单 VPN 冲突），迁移流程（2026-08-07）要求新手机登录 Tailnet 用于 `:8460` 备用链路。以迁移流程为准核实。
4. Automate 自动清理 flow（删 15 天前 JSONL）文档标注"尚未实施"；旧版无日期 JSONL 是否已清理未知。
5. Automate 私有 flow 的异机备份未建立（等 Restic 加密仓库启用后补带版本号 .flo 导出）。
6. 手机 Automate 六文件上传流当前是否在跑，HANDOFF 第 8 节列为"无法确认"（需看当天新数据）。
7. Focus Bridge 正式签名 APK 下 `adb run-as` 不可用，应用内一次性配对"尚未实现"。

### 电脑端（02）
8. ComputerInterventionAgent 启动形态：旧文档（07-31）说"普通后台进程，非计划任务"，迁移流程（08-07）列"登录后计划任务"。按最新段应为计划任务，未在旧文档同步。
9. 介入 API 认证：agent 配置 `auth_required=false` 与旧文档"未登录 401"记录并存（2026-08-04 起网页免密码，安全边界=Tailnet+loopback）。
10. `PiEditorTailscaleBypass` 任务周期：迁移流程写"每 1 分钟"，Web 管理指南写"每 5 分钟"。
11. Context Exporter 计划任务规范口径：旧机保留旧 `Behavior Context Exporter Timer` 兜底，新装机只建统一 `Behavior Context Exporter`（登录+20 分钟）。
12. Pi 端 `:8450` 本机自测超时是 Tailscale Serve 已知限制，不是故障（排查时勿误判）。

### Pi 端（03）
13. 半小时提醒检测的 `shadow_mode` 启用状态（是否已从影子转入有限提醒）文档无结论。
14. sysadmin-time-guard 发送使用的私有 env 文件未指明（ntfy.env 还是 ntfy-halfhour.env）；检测窗口"60 分钟"与"30/60 分钟占比"两处表述不一。
15. 每日日报推送渠道在专注花园文档未指明（HANDOFF/总流程图确认是 ntfy）。
16. `跨设备使用数据项目_树莓派端DeepSeek接管说明.md` 规划的 usage-hub（SQLite、半小时/每日汇总）**未实现**；实际是纯 JSONL 归档。勿按该旧目标架构操作。
17. Next Action "免密码"与花园文档早期"仍需密码"描述冲突——以 2026-08-04 起的免密码 + tailnet/loopback 边界为准。
18. `selector_candidate_limit` 数值：04 手册写 20，08-08 部署记录为 30（以 30 为最新）。
19. 专注花园 SQLite 无 schema version / 迁移工具（P1 待办）。

### 文档层通用
20. DECISIONS.md 决策编号重复（D62–D65、D68、D69 各两套），D20/D21/D56 被取代但状态未同步；NEXT_STEPS 旧条目未按最新日期段刷新。引用时以最新日期段落为准。

## 维护建议

1. **改模块前**：在对应 Canvas 找该模块节点 → 看入边（依赖）与出边（影响）→ 打开紫色文档节点读细节 → 改完按 `pi-ops-system-context` 的 update-protocol 更新交接文档 → 最后回 Canvas 修正节点文本。
2. **新增模块**：在同组内加节点（绿色=自动 / 黄色=数据 / 青色=接口），并补入边出边；同步加对应交接文档的 file 节点。
3. **待确认项**：橙节点只标记文档事实，不要猜测补全；核实后在节点文本里去掉 ⚠️ 并更新本说明的清单。
4. **与权威图的关系**：`../树莓派行为系统总流程图.md` 的 Mermaid 是权威版本（其中的 jpg 历史快照已过时）；本 Canvas 与其一致，若改流程先改 Mermaid 再同步 Canvas。
5. 本目录不保存任何 token / 密码 / 密钥值，只引用文件路径与端口。
6. **手工重建 Canvas JSON 时，每个节点必须带 `type` 字段**（`text` / `file` / `group`）。Obsidian 会丢弃缺少 `type` 的节点，并在下次保存时把残缺状态写回磁盘（2026-08-08 曾因缺 `type` 丢失全部正文节点与边，已从 git 恢复）。日常修改请直接用 Obsidian 内置 Canvas 编辑器，不要手工编辑 JSON。

## 2026-08-09 视觉与维护性修复

本次保留原有 4 张 Canvas 的职责与 20–30 个核心节点目标，统一为宽松列式布局：分组宽约 500、列间距约 560、同组节点垂直间隔至少 100；标题和图例独立置于主体上方，文档列收拢到右侧。内容节点统一加大宽高并保留明显的底部安全余量，避免中英文混排在 Canvas 内出现滚动条；所有模块节点补充显式 `职责：` 行，JSON、状态文件、服务名不再单独承担解释；文档节点改为“可点击 Markdown 链接 + 文档职责”。边标签同步缩短为维护索引词，详细机制仍放在节点对应的 Markdown 中，以减少标签和连线互相遮挡。电脑端修正了旧版 Cold Turkey `-lock 30` 表述，改为当前交接中的 lease + 到期回收；Pi 图补出旧目标 `usage-hub` 未实现的边界，并把 `shadow_mode`、认证、`selector_candidate_limit` 等冲突项保留为橙色待确认。

<!-- ai_provenance: source=codex; date=2026-08-09; verification=source-backed-and-canvas-json-validated; retrieved_notes="PI_SERVER_HANDOFF.md,PROJECT_STATE.md,DECISIONS.md,NEXT_STEPS.md,我的专注花园/00-交接总览.md,我的专注花园/专注花园桥接手机APP.md" -->
