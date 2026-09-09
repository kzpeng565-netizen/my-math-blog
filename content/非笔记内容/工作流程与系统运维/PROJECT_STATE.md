<!-- ai_provenance: source=codex; date=2026-07-26; verification=server-verified -->

# 半小时行为解释系统——PROJECT_STATE

> 本文档描述系统当前实际状态。技术细节见 PI_SERVER_HANDOFF.md，设计决策见 DECISIONS.md。

## 2026-08-28：新平板 Automate 迁移保护

==新 vivo 平板 `PA2535` 已安装并运行 Automate 1.53.0，主服务与无障碍服务均在运行。Pi 端 `phone-usage-receiver.service` 健康，既有 `tablet_*` 历史归档仍由按日期合并、逐行去重的逻辑保护；迁移前旧平板数据另存于 `/home/conrad/workspace/backups/phone-usage/tablet-migration-20260828-1515-before-new-pa2535/`，并带 `SHA256SUMS`。截至本次检查尚未收到新平板的首次 `tablet_*` 上传，迁移闭环仍待一次真实上传验证。==

<!-- ai_provenance: source=codex; date=2026-08-28; verification=device-and-pi-checked; retrieved_notes="非笔记内容/工作流程与系统运维/PI_SERVER_HANDOFF.md,非笔记内容/工作流程与系统运维/树莓派行为数据与接口索引.md" -->

## 系统是什么

==一个运行在树莓派上的**半小时行为解释系统**。每半小时自动收集电脑（ActivityWatch + Syncthing）、手机和平板（Android Automate）的使用数据，清洗后交 DeepSeek V4 Flash 生成语义时间线和核验报告，并保存到 `data/ai_reports/` 供 Next Action 与 Focus Garden 读取。自 2026-08-07 起，半小时报告不再发送 PushPlus；周报 PushPlus 与各类 ntfy 提醒仍按各自定时器运行。当前阶段不做未授权的自动干预。==

## 当前版本：第五版（可配置事实标签 + 精简双层 AI）

三轮迭代已完成：

- **第一版**：叙事型报告。用户反馈"没有直接回答工作多久、休息多久"——被否定。
- **第二版**：指标先行，程序计算确定性数字（工作时间、休息时间等），AI 只负责语义解释。加入用户确认的休息规则（电脑 AFK ≥ 3 分钟 + 手机熄屏）。
- **第三版**：引入两层 AI 调用——第一次生成语义时间线（work/entertainment/communication/rest/other/uncertain），程序据此计算工作-娱乐混杂指标，第二次 AI 只负责解释结果并生成报告。核心创新是**工作-娱乐混杂检测**：工作中被 AI 判断为娱乐且持续 > 30 秒才算一次偏离，30 秒及以下不计。
- ==**第四版（2026-07-28 历史状态）**：增加只读 Obsidian 任务上下文、last-known-good 回退、上下文归档、影子干预候选和日/周统计。当时影子判断随半小时 PushPlus 消息发送但不执行干预；该半小时 PushPlus 通道已于 2026-08-07 停用，归档与影子候选继续保留。==
- ==**第四版补充（2026-07-28 已部署）**：手机桌面快捷方式异常反馈已接入 `/annotation`。手机只上传 `category` 和可选 `message`；树莓派生成接收时间、编号、当前/候选半小时窗口，并关联最近 90 分钟内接收时间之前的 AI 报告和同窗口事实层。反馈仅作为人工调试标注，不触发 DeepSeek、不修改任务、不自动修复配置。==
- ==**第五版（2026-07-28 已部署）**：清洗后的电脑、手机、平板事实先由 `fact_tagger.py` 按 `config/tag_rules.json` 打可追踪标签；统一保留“前5分钟 + 正式30分钟 + 后5分钟”的40分钟事实窗口。程序锁定高置信度通信、娱乐和确认休息，吸收1—3秒采样缝隙，DeepSeek只组合未锁定候选单元并输出语义；程序恢复精确秒数、拆开越界分组、计算混杂，第二次 DeepSeek只解释精简摘要。==
- ==**第五版补充（2026-07-29 已部署）**：新增每日生活复盘 `daily_life_statistics.py` 与 ntfy 推送入口 `daily_life_notifier.py`。每天 09:00 统计前一天总工作、各类工作、娱乐前三项目、通信、AI使用分项和AI用途前三、手机睡眠边界，并结合 Obsidian 任务、番茄钟和 Profile 生成建议；建议层单独使用 DeepSeek V4 Pro，推送走纯文本 emoji 格式 ntfy，receipt 位于 `data/statistics/ntfy_receipts/daily_life/`。==
- ==**第五版补充（2026-07-29 已部署）**：新增每日生活复盘 `daily_life_statistics.py` 与 ntfy 推送入口 `daily_life_notifier.py`。每天 09:00 统计前一天总工作、各类工作、娱乐前三项目、通信、AI使用分项和AI用途前三、手机睡眠边界，并结合 Obsidian 任务、番茄钟和 Profile 生成建议；建议层单独使用 DeepSeek V4 Pro，推送走纯文本 emoji 格式 ntfy，receipt 位于 `data/statistics/ntfy_receipts/daily_life/`。==
- ==**第五版补充二（2026-07-29 已部署）**：Windows 端新增当前用户计划任务 `Behavior Context Exporter Timer`，每 20 分钟运行只读 Obsidian 上下文导出器；树莓派端新增 `afternoon_task_check.py` 与 `afternoon-task-check.timer`，每天 15:00 综合当天任务完成数与番茄钟进度，必要时调用 DeepSeek V4 Flash 辅助判断，并通过 ntfy 向手机发送高优先级提醒。==

<!-- ai_provenance: source=codex; date=2026-07-28; verification=server-verified; retrieved_notes="非笔记内容/工作流程与系统运维/PI_SERVER_HANDOFF.md,非笔记内容/工作流程与系统运维/DECISIONS.md,非笔记内容/工作流程与系统运维/NEXT_STEPS.md" -->

## 2026-07-28 部署状态

==以下状态已在树莓派上实际部署并核验。==

- **[已由服务器核实]** 项目目录已初始化 Git，当前分支为 `feature/obsidian-behavior-context`。==手机异常反馈接入已提交为 `6462485 feat: add phone annotation intake and review logs`；静默修复仍是已部署但尚未提交的工作区修改：`src/phone_facts.py`、`src/run_half_hour.py`、`src/tablet_facts.py`、`tests/test_cleaning.py`。==
- **[已由服务器核实]** 树莓派、Syncthing 和三个 advisor timer 均处于正常运行状态，系统状态为 `running`。
- **[已由服务器核实]** ==手机异常反馈接入阶段当时有 42 项测试通过；第五版完成后主项目现为 49 项测试全部通过。Windows 导出器 5 项测试此前已通过。==
- **[已由服务器核实]** ==使用 2026-07-28 04:00—04:30 历史数据在隔离输出目录回放：过期平板“亮屏”不再跨日外推，平板事实为 `on_minutes: 0`、`unknown_minutes: 30`；结果为 `model: null`、`push_suppressed_for_inactivity: true`，且全部本地归档仍生成。==
- **[已由服务器核实]** 每日统计、每周统计以及包含影子判断的半小时消息均已通过 PushPlus 实际发送并取得 `accepted` 回执。
- **[已由服务器核实]** AI 状态解释同时保存为 `data/ai_reports/YYYY-MM-DD/HH-MM.json` 和 `.md`；语义时间线、混杂指标、上下文快照、影子候选和发送回执均有独立归档。
- **[已由服务器核实]** ==修复部署后的首次真实 timer 于 2026-07-28 11:08 正常完成；该白天时段手机真实亮屏 1.2 分钟，因此按设计正常调用模型并推送，不属于静默窗口。==
- **[已由服务器核实]** ==`phone-usage-receiver.service` 已增加 `POST /annotation`，继续只监听 `127.0.0.1:8765`。Tailscale Funnel 仍为 `https://pi.taild4d3f7.ts.net` → `http://127.0.0.1:8765`。==
- **[已由用户确认][已由服务器核实]** ==手机真实提交已验收：2026-07-28 19:40:45 和 19:40:58 两条反馈均返回 `201` 并落盘，分别关联 `data/ai_reports/2026-07-28/19-00.md`。此前 19:38 的两次 `401` 已定位为手机端 `Authorization` 头未正确传递，修正后恢复。==
- **[已由服务器核实]** ==标签事实层与双层 AI 瘦身已部署；主项目 49 项测试通过，`git diff --check` 通过。规则文件为 `config/tag_rules.json`，可用 Monaco Lite 直接编辑并以 `python3 src/fact_tagger.py --rules config/tag_rules.json` 校验。==
- **[已由服务器核实]** ==隔离回放 19:00—19:30：完整覆盖1800秒，知乎两段为75秒和65秒，通信8.0分钟，无法判断0分钟；两次 DeepSeek估算合计约0.0069元。20:00—20:30：确认休息11.03分钟、知乎娱乐2.45分钟、确有35秒不确定段，估算约0.0121元。按两窗均值粗算，48窗/日约0.46元，较原约1.3元/日预计下降约65%。==
- **[已由服务器核实]** ==部署后的正式 timer 于22:08完成21:30—22:00生产窗口并成功推送：语义时间线覆盖1800秒，报告校验通过，无缓存命中时两次调用合计估算约0.0137元。==
- ==**[2026-08-07 当前状态]** 上述 PushPlus 成功记录均为历史验收证据；当前半小时服务只生成和归档报告，不再发送微信消息。==

## 当前运行的组件

### 树莓派 (Raspberry Pi 3 Model B, Debian 13, 1GB RAM)

| 组件 | 状态 | 说明 |
|---|---|---|
| `phone-usage-receiver.service` | active | 标准库 `http.server` 接收服务监听 `127.0.0.1:8765`，接收手机/平板共六文件上传，并提供 `/annotation` 手机异常反馈入口 |
| `phone-usage-maintenance.timer` | active | 每日 03:30 归档压缩（>30 天）和清理（>365 天） |
| `activitywatch-advisor.timer` | active, enabled | 每半小时 08/38 分触发分析 |
| `activitywatch-advisor.service` | triggered by timer | 单次执行，完成后退出 |
| `activitywatch-advisor-web.service` | active | Next Action 后端仅监听 `127.0.0.1:8767`，经 tailnet-only `:8450` 访问 |
| `focus-garden.service` | active | 启动入口 `app.py --port 8838`；HTTP 路由实现在 `focus_garden/server.py`，仅监听 `127.0.0.1:8838`，经 tailnet-only `:8460` 访问 |
| `focus-garden-backup.timer` | active | 启动 1 分钟后运行，之后每分钟生成一致性 SQLite 快照 |
| `pi-editor.service` | active | Monaco Lite 后端仅监听 `127.0.0.1:8766`，经 tailnet-only `:8443` 访问 |
| `sysadmin-time-guard.timer` | active, enabled | 每 3 分钟检查最近 60 分钟系统维护活动 |
| `activitywatch-advisor-daily-summary.timer` | disabled, inactive | 旧 PushPlus 日统计已停用，避免 09:00 发送旧版总数摘要 |
| `activitywatch-advisor-daily-life.timer` | active, enabled | ==每天 09:00、10:00、11:00 检查前一天生活复盘；早晨边界未确定时延后，最迟 11:00 生成并通过纯文本 emoji ntfy 推送== |
| `afternoon-task-check.timer` | active, enabled | ==每天 15:00 检查当天 Obsidian 规划任务是否完成过半；未过半时调用 DeepSeek V4 Flash 辅助裁决并通过 ntfy 提醒手机== |
| `activitywatch-advisor-weekly-summary.timer` | active, enabled | 每周一 09:05 发送上一自然周统计 |
| `bedtime-reminder.timer` | active, enabled | ==深夜设备使用 ntfy 提醒；每分钟夜间唤醒，策略窗口为 00:30—04:30== |
| `bedtime-reminder.service` | triggered by timer | ==oneshot 状态机；发送 ntfy、写入 `data/state/bedtime-reminder-state.json` 与 `data/bedtime_reminder/events.jsonl`== |
| `syncthing@conrad.service` | active | 同步 Windows ActivityWatch 数据到树莓派 |
| `tailscaled.service` | active | Tailscale VPN + Funnel（公网入口 for 手机） |
| `cockpit.socket` | active | Web 管理界面 `https://pi.local:9090` |
| `filebrowser.service` | active | 文件管理 `https://pi.local:8080` |

### Windows 电脑

| 组件 | 状态 | 说明 |
|---|---|---|
| ActivityWatch | 运行中 | 记录窗口标题、网页标签页、AFK 状态 |
| ActivityWatch Web Watcher (Edge 插件) | 运行中 | 记录浏览器标签页 URL 和标题 |
| Syncthing | 运行中 | 同步 `C:\Users\15345\ActivityWatchSync` 到树莓派 |
| Behavior Context Exporter | ==已部署，每 20 分钟更新== | ==当前用户计划任务 `Behavior Context Exporter Timer` 已创建并测试通过；只读导出 Profile、计划任务和番茄钟日志到 `C:\Users\15345\BehaviorContextSync`。原管理员安装的 `Behavior Context Exporter` 仍保留，但当前可靠周期由 Timer 任务承担。== |
| Behavior Context Syncthing | 已配置 | Windows Send Only → 树莓派 Receive Only，文件夹 ID 为 `behavior-context` |

### Android 手机

| 组件 | 状态 | 说明 |
|---|---|---|
| Automate `Phone Usage Logger` 流 | 运行中 | 采集 foreground/screen/heartbeat，每 15 分钟上传 |
| Automate 桌面异常反馈快捷方式 | 已验收 | ==通过 `POST /annotation` 上传分类和说明，2026-07-28 已有两条真实手机反馈成功落盘== |
| Clash | 运行中 | 代理（与 HTTPS 上传无冲突，已验证） |

### Android 平板

| 组件 | 状态 | 说明 |
|---|---|---|
| Automate 平板采集流 | 运行中 | 采集 tablet_foreground/screen/heartbeat，每约 2 分钟上传 |
| 设备型号 | Huawei | 使用相同 token 和 Funnel 入口，文件名为 tablet_* 前缀 |

## 当前数据量

- 2026-07-25 全天：48 个时段全部有输出（~29 KB/时段，含所有数据层）
- 预估增长：~1.4 MB/天，~0.5 GB/年（不需要立即压缩）
- 手机 archive 尚未自动压缩（今天是第三天，未触发 30 天阈值）

## 已验证的功能（全部通过）

1. 手机 → Tailscale Funnel → 树莓派 数据上传与归档
2. 电脑 → Syncthing → 树莓派 数据同步
3. computer_facts.py / phone_facts.py / tablet_facts.py 独立清洗
4. cross_device.py 三设备时间重叠计算（平板为辅助数据源）
5. DeepSeek 生成语义时间线（非思考模式，避免 token 耗尽）
6. 语义时间线校验（分钟总和、时间连续性、休息规则一致性）
7. 工作-娱乐混杂指标计算（>30s 偏离检测）
8. DeepSeek 生成最终核验报告
9. ==半小时报告本地归档与网页读取；PushPlus 半小时推送的历史验收已完成，但当前通道自 2026-08-07 起停用==
10. systemd timer 自动调度
11. ==Obsidian 三文件只读导出、原子写入和源文件哈希验证==
12. ==Syncthing 独立上下文文件夹单向同步，中文文件名和 UTF-8 内容验证==
13. ==树莓派上下文 schema 校验、last-known-good 回退和实际使用快照归档==
14. ==影子候选生成并归档；当前可由本地报告、网页和独立 ntfy 检查链路核验，不再附加到半小时 PushPlus 消息==
15. ==每日/每周统计生成、白天定时发送和发送回执去重==
16. ==DeepSeek 非法 JSON 时降级归档，不再导致整个 systemd 流程失败==
17. ==电脑无非 AFK 活动且手机、平板均无亮屏时，不调用 AI、不发 PushPlus但继续归档==
18. ==手机或平板最后一条亮屏记录超过 `heartbeat_stale_seconds`（当前 2700 秒）后转为 `unknown`，不会因采集器停止而把亮屏状态无限外推；AI 与通知共用同一个前置静默判断。==
19. ==手机异常反馈 `/annotation`：Bearer token 鉴权、表单/JSON 解析、分类校验、4 KiB 请求体限制、raw JSON 原子写入、daily/UNREVIEWED Markdown 从 raw 重建、最近报告关联、中文 message 保存、手机真实提交验收。==
20. ==可配置规则标签、统一40分钟事实层、程序锁定边界、AI候选单元压缩、越界分组自动拆分、逐次 token/缓存/费用审计。==
21. ==每日生活复盘生成与 ntfy 推送：统计工作/娱乐/通信/AI使用、手机睡眠边界和候选效率问题；DeepSeek V4 Pro 只写建议，不修改程序计算的分钟数。2026-07-29 已手动真实推送一次并取得 ntfy accepted 回执。==
22. ==深夜设备使用 ntfy 提醒：`bedtime_stop` 策略、独立 ntfy 模块、两层升级状态机、120 秒数据新鲜度保护、04:30 强制重置、JSONL 日志和 systemd timer 已部署。详见 [[ntfy提醒系统配置]]。==
23. ==15:00 任务进度 ntfy 提醒：`afternoon_task_check.py` 读取 Obsidian 同步快照、原始任务 Markdown 与番茄钟日志；综合任务完成数量和番茄进度，低于一半时调用 DeepSeek V4 Flash 辅助判断是否发送高优先级 ntfy。`systemd-analyze verify` 通过，`afternoon-task-check.timer` 已启用，下一次触发为 2026-07-29 15:00 CST；测试 `tests.test_afternoon_task_check` 2 项通过。==
24. ==15:00 任务进度提醒真实发送验收：2026-07-29 09:20 CST 手动正式运行 `afternoon_task_check.py --force`，V4 Flash 返回 `should_send: true`，ntfy 返回 `accepted`，message_id 为 `Tbg4g2XHqlSh`。当天已有成功回执，因此 15:00 定时器不会重复发送。==
25. ==DNS 修复：2026-07-29 首次正式发送时 Pi 端 DeepSeek/ntfy 域名解析失败。已关闭 Tailscale DNS 接管并将 NetworkManager `netplan-eth0` 固定 DNS 为 `8.8.8.8 223.5.5.5`；`getent hosts ntfy.sh` 与 `getent hosts api.deepseek.com` 已恢复。==

## 当前限制

- ==正式干预尚未启用；`shadow_mode` 必须保持为 `true`，至少人工观察 3—7 天。==
- ==Windows 导出器代码和配置已经部署，但 Windows Task Scheduler 注册需要用户以管理员 PowerShell 手工执行一次。==
- 目前只实现最近 60 分钟影子预筛选；120 分钟历史和通用 AI 有限提醒仍待后续版本。==深夜停止设备使用已经作为独立确定性 ntfy 策略上线，不依赖 AI、不回写 Obsidian、不使用 Automate 弹窗。==
- 手机跨午夜最后一段数据可能遗漏（Automate 每次只上传当天文件）。
- 微信公众号回复不会写回系统；==当前已新增手机桌面快捷异常反馈作为人工标注入口，但它仍不自动改任务或触发修复。==
- ==2026-07-28 手机异常反馈接入已有 Git 提交 `6462485`；静默修复和第五版标签/成本改造仍未提交，当前修改与新增文件以树莓派 `git status --short` 为准，交接时不得误称工作区干净。==

## 当前交接点

==2026-07-29 每日生活复盘与 ntfy 推送已部署并启用：`activitywatch-advisor-daily-life.timer` 每天 09:00 运行，`report_model.name=deepseek-v4-pro`。正文为程序计算的纯文本 emoji 数字复盘，包含工作分解、娱乐前三、AI分项和AI用途前三；AI建议追加在程序输出之后。旧 `activitywatch-advisor-daily-summary.timer` 已停用。2026-07-28 样例已真实推送成功；systemd 手动启动已验证 receipt 防重复。当前远端工作区仍包含多项未提交修改，交接时不得误称工作区干净。==

<!-- ai_provenance: source=codex; date=2026-07-29; verification=server-verified; retrieved_notes="非笔记内容/工作流程与系统运维/ntfy提醒系统配置.md" -->

==2026-07-29 深夜 ntfy 提醒系统已上线：`bedtime-reminder.timer` 为 enabled/active，`bedtime-reminder.service` 最近运行 success。真实 ntfy 主题只保存在 `/home/conrad/.config/activitywatch-advisor/ntfy.env`，不要写入 Git。00:33 已由真实夜间调度发送第一层提醒，状态为 `LEVEL_1_SENT`。详细配置、测试、停止和回滚命令见 [[ntfy提醒系统配置]]。==

## 半小时影子判断 ntfy 接入记录

**[已由服务器核验，2026-07-29 10:10 CST]**

输出位置：

| 输出 | 路径 |
|---|---|
| 电脑事实 | `/home/conrad/workspace/activitywatch-advisor/data/computer_facts/YYYY-MM-DD/HH-MM.json` |
| 手机事实 | `/home/conrad/workspace/activitywatch-advisor/data/phone_facts/YYYY-MM-DD/HH-MM.json` |
| 平板事实 | `/home/conrad/workspace/activitywatch-advisor/data/tablet_facts/YYYY-MM-DD/HH-MM.json` |
| 合并事实 | `/home/conrad/workspace/activitywatch-advisor/data/combined_facts/YYYY-MM-DD/HH-MM.json` |
| 标签事实层 | `/home/conrad/workspace/activitywatch-advisor/data/tagged_facts/YYYY-MM-DD/HH-MM.json` |
| 语义时间线 | `/home/conrad/workspace/activitywatch-advisor/data/semantic_timelines/YYYY-MM-DD/HH-MM.json` |
| 工作-娱乐混杂指标 | `/home/conrad/workspace/activitywatch-advisor/data/mixing_metrics/YYYY-MM-DD/HH-MM.json` |
| AI 报告 | `/home/conrad/workspace/activitywatch-advisor/data/ai_reports/YYYY-MM-DD/HH-MM.json` 和 `.md` |
| Obsidian 上下文快照 | `/home/conrad/workspace/activitywatch-advisor/data/context_snapshots/YYYY-MM-DD/HH-MM.json` |
| 影子判断候选 | `/home/conrad/workspace/activitywatch-advisor/data/intervention_candidates/YYYY-MM-DD/HH-MM.json` |
| PushPlus 回执 | `/home/conrad/workspace/activitywatch-advisor/data/pushplus_receipts/YYYY-MM-DD/HH-MM.json` |
| 半小时影子 ntfy 回执 | `/home/conrad/workspace/activitywatch-advisor/data/ntfy_receipts/half_hour_shadow/YYYY-MM-DD/HH-MM.json` |
| 处理状态 | `/home/conrad/workspace/activitywatch-advisor/data/state/processing-state.json` |

影子判断规则保留在 `src/behavior_advisor.py::build_shadow_candidate`，当前仍为 shadow-only：只记录候选和发送提醒，不执行干预、不修改 Obsidian 任务。

触发原因：

- `high_stimulation`：语义时间线中知乎、哔哩哔哩、小红书、抖音等高刺激娱乐时间达到 `settings.json` 的 `behavior_advisor.high_stimulation_minutes_threshold`，当前为 8 分钟。
- `late_night_entertainment`：窗口结束时间在 `behavior_advisor.late_night_cutoff` 之后且早于 06:00，并且存在娱乐时间；当前 cutoff 为 00:30。
- `current_window_low_meaningful_activity`：本窗口活跃设备时间至少 20 分钟，有意义工作少于 7.5 分钟，且确认休息为 0。
- `sustained_low_efficiency_60m`：当前窗口加上一条历史候选后，60 分钟活跃设备时间达到 `active_device_minutes_threshold`，当前为 40 分钟；60 分钟有意义活动少于 `low_efficiency_meaningful_minutes_threshold`，当前为 15 分钟；且确认休息为 0。
- `two_windows_without_mainline`：当前窗口没有主线工作，上一窗口也没有主线工作，并且当前活跃超过 5 分钟。

最终 `would_intervene=true` 还需要同时满足：`behavior_advisor.enabled=true`、至少一个触发原因、确认休息为 0、本窗口有意义活动少于 20 分钟。`shadow_mode` 保持 true，因此不会正式干预。番茄钟缺失永不单独触发。

ntfy 接入：

- 新私有环境文件：`/home/conrad/.config/activitywatch-advisor/ntfy-halfhour.env`，权限 `600 conrad:conrad`。
- `activitywatch-advisor.service` 已加载该 env 文件。
- 半小时流程中，只有影子候选 `would_intervene=true` 时才向半小时 ntfy 订阅发送高优先级提醒；否则写 skipped 回执。
- `--no-push` 或全设备无活动静默时，也会跳过半小时影子 ntfy。
- 2026-07-29 10:10 CST 已发送一条通道测试通知，ntfy 返回 `accepted`。

验证命令：

```bash
cd /home/conrad/workspace/activitywatch-advisor
python3 -m py_compile src/run_half_hour.py
python3 -m unittest tests.test_half_hour_shadow_ntfy -v
systemd-analyze verify /etc/systemd/system/activitywatch-advisor.service /etc/systemd/system/activitywatch-advisor.timer
systemctl cat activitywatch-advisor.service | grep EnvironmentFile
```
## 半小时提醒检测系统命名更正

**[已由服务器核验，2026-07-29 10:20 CST]**

正式名称统一为：**半小时提醒检测系统**。不要把对外通知、回执或交接标题称为“影子提醒”。

内部仍保留 `intervention_candidates` 和 `would_intervene` 这套影子判断机制，因为它描述的是“如果正式干预启用，是否会建议介入”的候选计算；但 ntfy 通知只在 `would_intervene=true` 时发送，且通知标题使用“半小时提醒检测系统”。

当前回执路径已调整为：

```text
/home/conrad/workspace/activitywatch-advisor/data/ntfy_receipts/half_hour_reminder_check/YYYY-MM-DD/HH-MM.json
```

半小时主流程返回字段已调整为：

```text
half_hour_reminder_check_ntfy
```
## 2026-07-29 当前状态补充

### 系统维护超时提醒

系统维护超时提醒已部署并运行。==`sysadmin-time-guard.timer` 为 `enabled / active`，现场 `OnCalendar=*-*-* *:00/3:00`，每 3 分钟执行一次。==当前实现不依赖半小时 AI prompt，而是在确定性分类层直接判断最近 30/60 分钟系统维护占比。

本次修正解决了 `ChatGPT.exe` 标题只有 `ChatGPT` 导致维护对话漏计的问题：当 `ChatGPT.exe` 或 `Codex.exe` 与明确系统维护片段间隔不超过 300 秒时，会继承为系统维护。数学、作业、定理、证明、`math`、`homework` 等关键词优先排除，避免数学学习中的 ChatGPT 被识别为系统维护。浏览器不作为通用桥接应用。

验证状态：

- `python3 -m unittest discover -s tests -v`：76 项通过。
- 合成 5 个时间段验证通过。
- 真实 `10:00/10:05/10:10/10:15/10:20` 五个时刻 dry-run 验证通过。
- 2026-07-29 10:30 CST 自动发送一次高优先级系统维护超时提醒，ntfy 返回 `accepted`，message_id 为 `Se0coKi8Fz0j`。
- 当前状态为 `COOLDOWN`，仍需连续 1 小时没有系统维护证据才会重置。

### 半小时提醒检测系统

半小时提醒检测系统已命名更正并接入 ntfy。它只在 `would_intervene=true` 时发送提醒；`would_intervene=false`、`--no-push`、全设备无活动静默时只写 skipped 回执。正式回执路径为：

```text
data/ntfy_receipts/half_hour_reminder_check/YYYY-MM-DD/HH-MM.json
```
## 2026-07-29：Next Action Web 已上线

树莓派端已新增私有网页入口：

```text
https://pi.taild4d3f7.ts.net:8450
```

该入口由 `activitywatch-advisor-web.service` 提供，内部监听 `127.0.0.1:8767`，通过 Tailscale Serve tailnet only 暴露。公开 Funnel 仍只用于手机数据上传和 Automate annotation。

“下一步”功能已完成第一版闭环：点击网页按钮后临时生成决策状态，调用 DeepSeek V4 Pro，返回包含行动、依据和说服性解释的建议，并把状态快照、建议、响应和手动执行结果归档到 `data/next_action/`。

“半小时报告”网页查看已可用。==该段最初上线时 PushPlus 微信推送保持不变；自 2026-08-07 起半小时 PushPlus 已停用，报告仍照常归档并供网页与 Focus Garden 读取。==网页中提交的报告反馈复用 `data/user_annotations/`，与 Automate HTTP 反馈进入同一个 raw/daily/UNREVIEWED 体系。

日报睡眠边界已改为 09:00、10:00、11:00 三次检测。09:00/10:00 若早晨边界仍未出现，只写 pending 状态，不推送日报；11:00 仍未观察到则标记 possible_fault 并生成低置信日报。

验证状态：`python3 -m unittest discover -s tests` 通过 82 项；实际 `POST /api/next-action` 已成功生成一条 V4 Pro 建议。自动执行观察和正式自动干预仍未启用。
## 2026-07-29：Next Action v1.1 已部署

下一步行动助手已更新为 `next-action-v1.1`。本版增强心理学和语言层面的说服力，保持适度亲近感，同时加入 12:00-13:00 吃饭/午休硬规则。

番茄钟规则已修正：番茄钟是中等可靠性正向证据；本系统 `1 🍅 = 40 分钟`，不是 25 分钟；番茄数量表示预估预算或进度标记，不保证实际剩余工作能在剩余番茄内完成。Next Action 已补充 prompt、结构化 `hard_rules` 和后端验证器，避免把 15/25/30 分钟启动片段误称为一个番茄钟。

任务粒度过大的问题本版暂不解决；AI 仍从当天任务标题中选择，但需要把第一步和缩小版动作切到 5-10 分钟可启动的小动作。
## 2026-07-30 状态更新：Next Action 问题反馈入口与 Codex 运维 skill

已完成 Next Action Web 的“问题反馈”入口。该入口用于记录用户在使用下一步行动助手、半小时报告、数据同步、通知、规则匹配或网页界面时发现的问题，方便之后统一交给 Codex 批处理。

当前已部署并验证：

- 网页服务仍由 `activitywatch-advisor-web.service` 提供，监听树莓派本机 `127.0.0.1:8767`。
- 公网入口仍只暴露 Next Action 页面和必要 API，登录后才能提交和查看问题反馈。
- 新增后端模块：`/home/conrad/workspace/activitywatch-advisor/src/issue_feedback.py`。
- 新增测试：`/home/conrad/workspace/activitywatch-advisor/tests/test_issue_feedback.py`。
- 新增数据目录：`/home/conrad/workspace/activitywatch-advisor/data/issue_feedback/`。
- 反馈会保存为 raw JSON，并自动重建 daily Markdown 和 `UNREVIEWED.md`。
- 树莓派端完整测试已通过：`python3 -m unittest discover -s tests`，共 87 项 OK。
- 未登录访问 `/api/issue-feedback/recent` 返回 401，确认问题反馈 API 没有裸露。

同时新增本地 Codex skill：

```text
C:\Users\15345\.codex\skills\pi-ops-system-context
```

这个 skill 的目标是让 Codex 在处理树莓派行为顾问、Next Action、半小时报告、Automate、Funnel、Obsidian context、番茄钟、睡眠统计和问题反馈 backlog 时，先读取固定运维文档和服务地图，再开始执行，减少每次重新解释系统架构的成本。

## 2026-07-30 状态更新：Next Action v1.2 闭环与起床证据

==Next Action 已更新为 `next-action-v1.2`：生成新建议前，后端会检查 `active.json` 对应建议是否已有手动结果。若上一条既未填写执行结果，也未明确“换一个/现在不做”，接口返回 `409 pending_outcome_required`；网页先展示上一条，用户填写“完成了/正在做/没开始”后，再自动继续本次生成请求。==

==用户主动点击“生成建议”被定义为已经醒来且能够交互的直接证据。决策状态、prompt 和后端验证器均禁止再用 `clarify` 询问用户是否起床、醒来或仍在睡。==

验证状态：

- Next Action 针对性测试 9 项通过；
- 项目完整测试 90 项通过；
- 两段网页 JavaScript 均通过语法检查；
- `activitywatch-advisor-web.service` 已重启并保持 active；
- `127.0.0.1:8767` 正常监听，未登录访问返回 401；
- 登录后在存在未闭环建议时，`POST /api/next-action` 实测返回 409、`pending_outcome_required`，并携带待处理建议。

<!-- ai_provenance: source=codex; date=2026-07-30; verification=checked; retrieved_notes="非笔记内容/工作流程与系统运维/PROJECT_STATE.md" -->

## 2026-07-31 状态更新：本地 Cold Turkey 自动开启模块已接入

==半小时行为系统已从“影子候选提醒”扩展出电脑端 Cold Turkey 自动开启模块。Pi 端仍负责判断、归档和提供登录后 API；Windows 端本地 agent 拉取 pending request、弹窗询问、调用 Cold Turkey、并把 ack/final receipt 回传 Pi。==

==Pi 端新增请求/回执链路：`data/computer_interventions/requests/`、`data/computer_interventions/responses/`、`data/computer_interventions/state/windows-main.json`。Next Action Web 新增登录后 API：`GET /api/computer-interventions/pending`、`POST /api/computer-interventions/ack`、`POST /api/computer-interventions/response`。==

==Windows agent 位于 `D:\tools\computer-intervention-agent\`。当前以普通后台进程运行：`D:\anaconda\python.exe D:\tools\computer-intervention-agent\agent.py`。它尚未安装成开机自启动任务或 Windows 服务；重启电脑后需要手动启动，或后续补计划任务。==

==当前行为规则：`常刷网站` 和 `bilibili` 是本地 allowlist 中仅有的可执行 block；默认封锁 30 分钟；连续两次点击“不介入”后，第三次仍触发时强制介入；忽略按“暂不介入”完成请求但不累计拒绝；封锁成功、已处于 agent 估计封锁状态、或观察到恢复会重置拒绝计数。B 站周六全天、周日全天、周一 00:00-12:00 Asia/Shanghai 作为备课例外。==

验证状态：

- ==Pi 端新增测试 `tests/test_computer_intervention.py` 通过。==
- ==Pi 端全量 `python3 -m unittest discover -s tests -v` 通过 93 项。==
- ==`activitywatch-advisor-web.service` 已重启并保持 active；新 API 未登录返回 401。==
- ==2026-07-31 13:38 CST 的请求已由 Windows agent 接收并回传 final；用户选择 `accepted`，`常刷网站` 和 `bilibili` 均返回 Cold Turkey 命令 success，agent 本地估计封锁至 14:08:45。==
- ==弹窗 UI 已调整为高 DPI aware、模块化简约设计：固定底部按钮、中间可滚动内容、较大字体、目标 block 显示名兜底。==

<!-- ai_provenance: source=codex; date=2026-07-31; verification=checked; retrieved_notes="非笔记内容/工作流程与系统运维/PROJECT_STATE.md" -->

## 2026-08-07 状态更新：Cold Turkey 可恢复 lease 与休眠补偿

==Windows agent 继续使用 Cold Turkey `-start <block>` / `-stop <block>` 的可暂停 lease，不使用 `-lock 30`。每个 lease 持久化 `lease_id`、来源和绝对 `lock_until_estimated`；agent 在启动、每轮轮询、处理请求后按 wall-clock 回收过期 lease，因此电脑休眠或 agent 重启后也能补发 `-stop`。==

==Pi 的 Focus Garden release 请求改为 durable pending：不再因 180 秒 TTL 在休眠期间丢失；请求带有 lease ownership，旧 release 不能停止新的 lease。Focus session 只有在 release 已成功入队后才完成结算。==

==2026-08-07 验证：Windows agent lease 测试 6/6 通过；Pi computer intervention 测试 6/6 通过；Focus Garden 本地测试 27/27 通过；两个 Pi 服务重启后保持 active，花园 loopback health 返回 `{"status":"ok"}`。==

<!-- ai_provenance: source=codex; date=2026-08-07; verification=local-tests-and-pi-service-restart; retrieved_notes="非笔记内容/工作流程与系统运维/PROJECT_STATE.md" -->

## 2026-08-02 状态更新：我的专注花园第一版

==Windows 本地新增个人使用的像素风游戏“我的专注花园”，项目位于 `D:\MyFocusGarden`，只监听 `127.0.0.1:8838`。它不新增树莓派端口或服务，不回写 Obsidian、Next Action、行为 facts 或 Cold Turkey 数据库。==

==游戏通过现有 SSH 密钥只读聚合三类树莓派事实：电脑端 final 回执中的主动 `accepted + success`、同一 `suggestion_id` 的 Next Action `accepted + completed`、以及 `daily_life` 中 `resolved + high` 且最后手机活动不晚于可配置阈值的早睡估计。奖励使用稳定事件 ID 写入本地 SQLite，重复同步不会重复发放。==

==本地专注由 Python 后台计时，复用 computer-intervention-agent 的 Cold Turkey executable 与 allowlist；每累计完成 40 分钟发放一份种植奖励，余数结转。花园从 `5×5` 开始，填满后按奇数边长自动扩展。==

验证状态：

- ==4 项本地单元测试通过；==
- ==树莓派只读同步发现 5 份历史奖励：主动接受介入 3 份、早睡估计 2 份、严格 AI 完成闭环 0 份；==
- ==20 种本机 Minecraft Education Edition 植物贴图均已加载，素材目录已加入 `.gitignore`，只限本地个人使用；==
- ==浏览器已检查首页、奖励记录、植物选择弹窗和响应式像素风布局；==
- ==桌面快捷方式为 `C:\Users\15345\Desktop\我的专注花园.lnk`。==

<!-- ai_provenance: source=codex; date=2026-08-02; verification=checked; retrieved_notes="非笔记内容/工作流程与系统运维/本地Cold Turkey自动开启模块.md,非笔记内容/工作流程与系统运维/树莓派行为数据与接口索引.md,非笔记内容/工作流程与系统运维/树莓派下一步行动助手架构.md" -->

## 2026-08-03 常规交接：我的专注花园当前状态

==完整接管资料已整理到 [[我的专注花园/00-交接总览]]，专题包括数据来源与处理、游戏架构、后续优化、运维和扩展手册。运行代码和数据仍以 `D:\MyFocusGarden` 为事实源。==

==现场核验：本地服务 `127.0.0.1:8838` 健康；正式 `pythonw.exe` 进程正在运行；当前 SQLite 有 5 株已种植、0 份待种、无运行中的专注。目录现为 35 种可种植对象：12 种花、6 种树苗、17 种蘑菇。==

==测试已更新为 6 项且全部通过，`node --check static\app.js` 通过。此前 2026-08-02 记录的“20 种、4 项测试”是第一版当时快照，不再代表当前版本。树莓派侧仍无新增端口、服务或写入操作。==

<!-- ai_provenance: source=codex; date=2026-08-03; verification=checked; retrieved_notes="非笔记内容/工作流程与系统运维/我的专注花园/00-交接总览.md" -->

## 2026-08-03 状态更新：我的专注花园迁移至 Pi

==正式运行端已迁移到 `/home/conrad/services/focus-garden`。`focus-garden.service` 只监听 `127.0.0.1:8838`，Tailscale Serve 在 `https://pi.taild4d3f7.ts.net:8460/` 提供 tailnet-only HTTPS；专注花园没有启用 Funnel，也没有监听局域网地址。==

==完整迁移验收、同步检查、恢复和回滚步骤见 [[我的专注花园/05-Pi迁移验收与恢复清单]]。==

==权威 SQLite 位于 Pi；`focus-garden-backup.timer` 每分钟生成一致性快照到 `/home/conrad/workspace/focus-garden-archive/`。Syncthing 将该文件夹从 Pi send-only 同步到 Windows receive-only 的 `D:\MyFocusGardenArchive`，电脑端启用 staggered 版本保留。==

==迁移验收：9 条奖励、8 株植物、1 份待种、无运行中计时；Pi 本地奖励扫描发现 9 条且新增 0；Python 7 项测试通过，HTTPS 健康检查和受版权保护的 PNG 均返回 200。Pi 专注模式固定为安全模拟，不会调用 Windows Cold Turkey。==

<!-- ai_provenance: source=codex; date=2026-08-03; verification=checked; retrieved_notes="非笔记内容/工作流程与系统运维/我的专注花园/00-交接总览.md,非笔记内容/工作流程与系统运维/我的专注花园/04-运维与扩展手册.md" -->

## 2026-08-04 状态更新：专注花园内嵌 Next Action（已部署）

==Windows 开发副本 `D:\MyFocusGarden` 已实现“下一步行动”原生菜单：固定 loopback API 代理将既有建议、反馈、结果、近三条报告与问题反馈带入花园 UI；密码和 Next Action 数据目录均不进入花园。==

==本地与 Pi 的 8 项 Python 测试、配置 JSON 及桌面/390px 浏览器视图均已通过；Pi 的 `focus-garden.service` 已重启且 8838 健康检查正常，未登录代理请求返回既有 Next Action 401。Node 未安装在 Pi，因此前端语法检查沿用已通过的本地结果；真实登录、生成建议与反馈闭环仍待手动验收。==

<!-- ai_provenance: source=codex; date=2026-08-04; verification=checked; retrieved_notes="非笔记内容/工作流程与系统运维/我的专注花园/00-交接总览.md,非笔记内容/工作流程与系统运维/树莓派 Next Action Web架构.md" -->

## 2026-08-04 状态更新：Next Action 免密码、仅 Tailnet

==已从 Pi 私有 `web.env` 移除 `NEXT_ACTION_WEB_PASSWORD`，并重启 `activitywatch-advisor-web.service`。Next Action 与花园内嵌代理的 active 接口均返回 200，不再要求登录。==

==为维持私有边界，原公网 Funnel `:10000` 已移除；Next Action 只保留 tailnet-only 的 `:8450`，专注花园仍为 tailnet-only 的 `:8460`。公网 Funnel 仅保留不相关且已有 token 认证的手机接收 `:443`。==

<!-- ai_provenance: source=codex; date=2026-08-04; verification=checked; retrieved_notes="非笔记内容/工作流程与系统运维/PROJECT_STATE.md" -->

## 2026-08-06：New Pomodoro Timer 代码结构交接

==新增 `New-Pomodoro-Timer-代码结构与交接.md`，记录打包插件的模块边界、Timer 状态机、Pi API 同步、Work/Break 规则、配置来源和排障顺序。Pi Focus Garden 会话仍是权威状态；插件只负责显示和发起操作。==

<!-- ai_provenance: source=codex; date=2026-08-06; verification=local-verified; retrieved_notes="New-Pomodoro-Timer-代码结构与交接.md" -->

## 2026-08-06：New Pomodoro Timer 时长与 Work/Break 交互

==插件面板现在提供 Work 预设 `5/20/30/40/45/60`（默认 40）和可编辑的 Break 预设（含跳过休息）；进行中的会话会暂时锁定这两个选择，避免改变 Pi 权威会话。点击表盘数字可启动或暂停；点击 Break 状态会跳过休息并自动进入 Work，点击 Work 状态不执行跳过。==

<!-- ai_provenance: source=codex; date=2026-08-06; verification=local-verified; retrieved_notes="New Pomodoro Timer duration controls and mode interaction" -->

## 2026-08-06 状态更新：统一暂停状态与云端刷新

==New Pomodoro Timer 的暂停入口现在总是先读取 Pi 的权威 Focus Garden session，再允许输入暂停时长；不再依赖可能落后的本地 `running` 标志。网页端暂停会携带 `paused_at`，插件据此冻结倒计时并显示“Pi 云端：本轮已暂停，到点会自动恢复”；暂停时钟不会继续按墙钟流逝。插件保留手动“刷新云端进度”，且运行时每 5 秒同步一次 bootstrap。==

<!-- ai_provenance: source=codex; date=2026-08-06; verification=local-verified; retrieved_notes="New Pomodoro Timer installed runtime, Focus Garden pause API" -->

## 2026-08-05 状态更新：统一的定时暂停

==网页 Focus Garden 与 New Pomodoro Timer 现在共享一次定时暂停：用户先输入 1—120 分钟并确认；Pi 权威 SQLite 记录暂停开始与恢复截止时刻，立即请求既有 Windows agent 解除 Cold Turkey 会话。专注服务的后台 reconciler 每 2 秒检查截止时刻，因此网页和 Obsidian 都关闭时仍会自动恢复电脑锁定与计时。手机 Quick Pomodoro 目前没有远程暂停接口，不能承诺在暂停期停止。==

==每个 session 仍只能暂停一次。确认过暂停后，完成结算的植物成长与关联任务番茄均固定按原计划时长的一半计算；约定的暂停时长会完整延后 session 的结束时间，不能由前端开关决定。==

<!-- ai_provenance: source=codex; date=2026-08-05; verification=local-tests-and-pi-service-restart; retrieved_notes="非笔记内容/工作流程与系统运维/PROJECT_STATE.md" -->

## 2026-08-05：可暂停的番茄锁定会话

==New Pomodoro Timer 与网页 Focus Garden 复用同一个 Windows `computer-intervention-agent`，没有新增番茄专用 agent。Cold Turkey 由 agent 以未硬锁的 `-start` 会话开启，并在暂停、取消或专注完成时用 `-stop` 关闭；不再传 `-lock`。==

==每轮专注只可暂停一次。暂停时 Pi 会保持会话为 paused、阻止结算、请求 agent 解除电脑锁定；恢复时重新下发同一 profile 的 allowlist。曾暂停的会话完成后有效成长和任务番茄累计均按原时长的一半计算（40 分钟即 20 分钟）。==

==Windows agent 的现有心跳增加 `active_locks` 派生的 lease 状态；“系统状态”页显示 Cold Turkey 为 active/idle 以及当前 block。网页与插件都可选深度 profile（常刷网站＋bilibili）或轻度 profile（不锁 bilibili）。==

<!-- ai_provenance: source=codex; date=2026-08-05; verification=local-tests-and-pi-service-restart; retrieved_notes="非笔记内容/工作流程与系统运维/PROJECT_STATE.md" -->

## 2026-08-05 状态更新：花园系统健康面板

==专注花园“系统状态”已改为只读健康面板。它通过 Pi 本机读取服务状态、任务 mutation queue、Obsidian 快照/同步检查的新鲜度、Windows agent 与 Android Focus Bridge 心跳、行为上下文、最近报告及 SQLite 备份新鲜度；不展示任务正文、原始行为日志或任何密钥。==

==新增 `GET /api/system-status`，仍只经既有 8838 loopback 与 8460 tailnet-only Serve 提供。Windows `ComputerInterventionAgent` 已为登录后计划任务，并每 5 分钟向既有 Next Action loopback API 发送轻量 heartbeat；它不新增远程命令能力。==

<!-- ai_provenance: source=codex; date=2026-08-05; verification=server-verified; retrieved_notes="非笔记内容/工作流程与系统运维/PI_SERVER_HANDOFF.md" -->

## 2026-08-06 状态更新：系统状态接口兼容 active_locks

==Windows agent 的 `active_locks` 是列表，系统状态接口原先按字典取键导致空响应。`focus_garden/server.py` 已兼容列表与字典，前端对空响应显示明确提示；本地 22 项测试、Pi 15 项测试通过，服务已重启并从 `:8460` 验证返回 200。==

<!-- ai_provenance: source=codex; date=2026-08-06; verification=server-verified; retrieved_notes="Pi focus-garden journal, deployed server.py and app.js" -->

## 2026-08-06 状态更新：进入页面空元素报错修复

==自动“同步奖励”曾引用已不存在的 `#piStatus`，刚进入页面会出现 `Cannot set properties of null (setting 'textContent')`。已移除残留引用并给 `app.js` 增加版本号；本地 23 项测试、Pi 21 项测试通过，服务保持 active。==

<!-- ai_provenance: source=codex; date=2026-08-06; verification=server-verified; retrieved_notes="Focus Garden static app.js and index.html, Pi service health" -->

## 2026-08-05 状态更新：任务网页写回桥

==已部署任务同步 v1：`ToDo-任务集合.md`、`ToDo-已经规划好的任务.md`、`已完成任务.md` 进入同一同步范围；每个任务以 Obsidian block ID（新 ID 为 8 位小写字母数字）作为稳定键。Pi 只持久化网页操作意图和即时有效任务视图；Pi 不直接写 Markdown，Obsidian 的 Pi Context Sync 插件在打开 Vault 后写回并在新的快照抵达 Pi 后确认队列。==

==我的专注花园已提供“直接安排”表单：可新建、改标题/日期/优先级/番茄数、推迟一天和标记完成，用户无需输入 Tasks emoji。循环任务在 v1 不允许从网页完成。Next Action 状态已合并 Pi 的即时视图，并明确提供上海时区的时间戳、日期、时分与星期。==

==2026-08-05 已部署专注—任务一体化：Focus Garden 的开始页可选关联一个近期任务（默认不关联）并选择电脑＋手机、仅电脑、仅手机或仅计时。完成关联会话后，以该任务专属的 40 分钟累计生成 `advance_tomatoes` queue mutation；Pi Context Sync 使用绝对目标值的单调写回，网络或插件重试不会重复计数。全局植物奖励保持独立。New Pomodoro Timer 已改为花园同款配色、默认 40 分钟，开始工作段会通过 Pi MagicDNS 创建同一 Focus Garden 会话，且不再直接写任务番茄。==

<!-- ai_provenance: source=codex; date=2026-08-05; verification=server-verified; retrieved_notes="非笔记内容/任务计划/ToDo-已经规划好的任务.md" -->

## 2026-08-04：专注花园电脑＋手机正式启用

==Focus Garden 已切换为 `FOCUS_GARDEN_DRY_RUN=0`，保持 8838 loopback 与 8460 tailnet-only；默认“电脑＋手机”专注会通过既有 allowlist 同时触发 Windows Cold Turkey 与手机快速番茄。==

==手机桥接 v1.0.0 已部署：中文界面保留本地调试、确认坐标和网格 Y 偏移校准，写入私有运行日志，并每 5 分钟向花园发送无障碍服务心跳；网页下次打开时会对超 20 分钟的心跳暂停显示右下角提示。==

==专注时长限定为 5、10、20、30、40、45、60 分钟；自定义分钟已移除。新增预约专注和连续专注：连续模式仅选 30/40/45/60 分钟、休息时间与轮数；休息段不尝试解除任何锁定，每轮开始时单独下发锁定。==

<!-- ai_provenance: source=codex; date=2026-08-04; verification=checked; retrieved_notes="非笔记内容/工作流程与系统运维/PROJECT_STATE.md" -->

## 2026-08-04 状态更新：移动端与锁机可靠性

==花园移动端已改为可换行的专注时长按钮、无“本次专注”读数和停止计时入口；等距花园不再保留固定空白高度，图鉴固定为两列。Mushroom Nook 条目已从当前目录隐藏但扩展分类机制和素材仍保留；权威库中既有两株蘑菇已迁为 Minecraft 棕色蘑菇。==

==每次真实锁机启动时，Windows agent 显示短提示，Focus Bridge 显示手机通知。手机因锁屏无法取得目标窗口时，会每 30 秒重新打开已确认的番茄页面，最多 6 次后才回传失败；Windows Cold Turkey 命令失败时也会在 30 秒后重试一次。==

==为保证默认电脑＋手机始终同步，10 分钟已从网页和 API 删除；当前所有公开专注入口统一只接受 5、20、30、40、45、60 分钟。==

<!-- ai_provenance: source=codex; date=2026-08-04; verification=checked; retrieved_notes="非笔记内容/工作流程与系统运维/PROJECT_STATE.md" -->

## 2026-08-06 状态更新：近期动态 v3.1 已部署

==近期动态（recent context）已上线：advisor 新增 src/recent_context.py、src/recent_context_selector.py 与 /api/recent-context* 九个固定接口；Focus Garden 新增「近期动态」侧栏页与 Next Action「当前情境」卡片。数据存于 data/recent_context/state.json（revision + RLock 乐观并发），解析审计 data/recent_context/parse_audit.jsonl。用户原文是唯一权威，AI 解析与筛选只作辅助；解析 prompt 以 recorded_at 为基准；筛选失败自动降级，不中断 Next Action。PROMPT_VERSION 升至 next-action-v1.3；recent_context_used 只保存并校验候选 ID。认证要求 loopback + X-Focus-Garden-Bridge==1。2026-08-06 以 enabled=false 部署两端、Pi 全量测试（advisor 141 项仅 2 项既有失败；garden 23/23）后开启开关，并完成两条 [系统验收测试] 记录的真实解析、生成与归档。==

## 2026-08-07 状态更新：Focus Bridge 公网主链路

==Android Focus Bridge 已升级为 1.1.0：独立前台服务承担 15 秒轮询与 5 分钟心跳，使用 `START_STICKY`、持久通知、开机/应用升级恢复；无障碍服务只负责界面执行。关键 API 默认走普通公网 HTTPS，不依赖 Tailscale，旧 `:8460` 仅作为网络异常时的备用。公网固定路径使用设备独立 Bearer token，密钥只存手机应用私有目录和 Pi 的 `0600` 文件。==

==原计划加入 Focus Garden「系统状态」的 Android Bridge 验收卡已于同日回退：部署时错误覆盖了较新的「近期动态」前端和代理。已从 13:30/13:33 部署前备份恢复 Garden，近期动态 `revision=5`、原有 1 条记录仍在；Pi 与本地原版测试均为 23/23。Android 1.1.0 与公网代理不依赖该页面，继续保留。==

<!-- ai_provenance: source=codex; date=2026-08-07; verification=rollback-and-server-verified; retrieved_notes="非笔记内容/工作流程与系统运维/PROJECT_STATE.md" -->

## 2026-08-07 状态更新：任务待安排区与分钟级近期动态

==Focus Garden 的任务清单现有删除操作；未填写 `⏳` 的网页新任务保留自己的 block ID，并由桌面 Pi Context Sync 写入 `ToDo-任务集合.md` 顶部 `# ⚠️ 树莓派新增 · 待正式安排`。一旦在网页或规划流程中填入安排日，插件会用同一 ID 将该行移动到 `ToDo-已经规划好的任务.md`；Pi 仍只保存 mutation queue，不直接写 Markdown。==

==近期动态的影响区间现可保留两种精度：仅日期继续存 `YYYY-MM-DD`；原文明确到时分时，Flash 解析器存带时区的 `YYYY-MM-DDTHH:MM+08:00`，并按真实起止时刻判断 upcoming/active/ended。解析器和相关性筛选器均固定使用 `deepseek-v4-flash`、`thinking=disabled`；无法可靠解析仍返回 vague/conditional，而非伪造时间。==

<!-- ai_provenance: source=codex; date=2026-08-07; verification=local-and-pi-tests-plus-live-endpoints; retrieved_notes="非笔记内容/工作流程与系统运维/PROJECT_STATE.md" -->

## 2026-08-07 状态更新：Next Action 两轮行动澄清

==Next Action 现支持最多两轮“卡点 → 更新行动”的短对话。每轮与初始建议一样使用 `deepseek-v4-pro`、`thinking=enabled`，将用户的一句阻力重新纳入完整判断后生成新的可执行行动版本；第二轮会明确收到第一轮的用户卡点、助手回应和产生的行动版本，不只看当前结果。不会创建/修改任务、安排、番茄钟或花园记录。接受请求携带 `expected_action_revision`，服务端只接受 active suggestion 的当前最后版本，并把 `accepted_action_id/revision` 写入反馈记录，旧版本和过期点击一律拒绝。==

<!-- ai_provenance: source=codex; date=2026-08-07; verification=targeted-unit-test-plus-pi-loopback; retrieved_notes="非笔记内容/工作流程与系统运维/我的专注花园/树莓派 Next Action Web架构.md" -->

## 2026-08-07 状态更新：Focus Bridge 1.2.1 介入选择页

==Android Focus Bridge 已部署 `1.2.1 (14)`：收到 offer 后，手机未锁定时打开原生介入页，显示“接受 / 拒绝”和 10 秒整数倒计时；锁屏时继续检查最多 2 分钟，仍不可用则提交 `ignored`。页面期间重新锁屏会关闭页面，解锁后重新给出完整 10 秒。决定持久化并重试，提交成功前不会被新的轮询结果覆盖；已损坏为连续问号或替换字符的说明会回退为应用内置中文。==

==真机验收完成：测试 `accepted` 于 22:02:52 写入 Pi，22:03:04 手机开始 5 分钟正式流程，22:03:05 “不做手机控”校准确认成功，22:03:06 Pi 收到 final event。另有 10 秒无操作自动 `ignored` 的闭环验收。==

<!-- ai_provenance: source=codex; date=2026-08-07; verification=user-confirmed-plus-device-and-pi-event; retrieved_notes="非笔记内容/工作流程与系统运维/我的专注花园/专注花园桥接手机APP.md" -->

## 2026-08-07 状态更新：Cold Turkey legacy release 队列回归已隔离

==一次 `accepted` 后立刻 `release` 的根因是旧版 Focus Garden 在 2026-08-05—06 写入了 2,761 条没有 `lease_id` 的 `manual_focus_pause` 请求；后续 durable 扫描把它们重新交给 Agent。Windows Agent 现拒绝无 lease 的 `-stop`；Pi 将这批原始 JSON 移至 `data/computer_interventions/archive/release/legacy-unleased/`，不再进入派发目录。==

==新的 release 必须携带与启动请求相同的 `lease_id`；带 lease 的 release 只有在 Agent 回传 final 后才会移至 `archive/release/completed/`。未确认的带 lease release 不按时间删除，以保留电脑休眠或离线后的解锁补偿。Focus Garden 生产端已恢复从启动 dispatcher receipt 提取 lease、先安全入队 release 再结算或取消 session。==

<!-- ai_provenance: source=codex; date=2026-08-07; verification=windows-and-pi-tests-plus-live-queue-check; retrieved_notes="非笔记内容/工作流程与系统运维/PROJECT_STATE.md" -->

## 2026-08-07 状态更新：闲鱼归类为购物

==已将闲鱼固定为 `shopping`，覆盖网页标题/idlefish 域名、手机与平板应用名，以及 `com.taobao.idlefish` 包名。该规则以程序锁定段生效，语义模型不能改写为娱乐；购物会在半小时报告、推送和每日汇总中单列，且不计入高刺激、娱乐偏离或工作—娱乐切换，因此不会以 `work_entertainment_alternation` 触发 Cold Turkey。==

<!-- ai_provenance: source=codex; date=2026-08-07; verification=pi-targeted-tests-and-replay; retrieved_notes="非笔记内容/工作流程与系统运维/PROJECT_STATE.md" -->

## 2026-08-07 状态更新：可编辑迁移体系已落地

==Pi 已建立源码级迁移体系，生产服务仍从原路径运行。`/home/conrad/workspace/editable/` 提供 Advisor、Focus Garden、手机接收器和 Monaco Lite 的可编辑副本；迁移控制仓库位于 `/home/conrad/workspace/pi-portable-system/`。安全源码快照每 6 小时导出到 `/home/conrad/workspace/pi-system-migration/current/`，再由 Syncthing 以 Pi Send Only、Windows Receive Only 同步到 `D:\PiSystemMigration`。==

==Focus Garden 的 51 个 Minecraft 来源素材仅存在于 Pi 私有生产目录与忽略它们的私有编辑副本，Git 跟踪数和迁移快照包含数均为 0。所有生产仓库无远程并安装拒绝 push 的钩子；编辑副本只允许指向 `/home/conrad/` 的本机远程。Restic 已安装，但外部加密仓库和密码尚未配置，因此私有数据备份定时器保持 disabled；不得为求“完整”而把素材加入公开仓库或普通源码同步。==

<!-- ai_provenance: source=codex; date=2026-08-07; verification=pi-and-windows-export-audit; retrieved_notes="Pi live system and migration repositories" -->

## 2026-08-07 状态更新：客户端配置与构建已版本化

==手机/电脑迁移基线现统一记录于 `D:\PiClientMigration\CURRENT.json`。当前 release 为 `2026.08.07-r1`：Focus Bridge `1.3.1 (16)` 保存经验证 APK 与完整 Git bundle；Windows Computer Agent、Behavior Context Exporter 保存本地 Git tag、bundle 和脱敏配置模板；ActivityWatch 同步脚本、Pi Editor bypass 与 6 个计划任务 XML 作为恢复证据保留。==

==三个客户端源码目录已建立本地 Git，均无远程且默认拒绝 push。真实 token、密码、SSH 私钥、Syncthing 身份、用户数据、Automate 含 token 的原始 flow 和 Minecraft 来源素材没有进入 release。完整配置顺序见 [[Pi系统手机端与电脑端迁移配置流程]]。==

<!-- ai_provenance: source=codex; date=2026-08-07; verification=build-tests-bundle-and-manifest-verified; retrieved_notes="local Android and Windows client configurations" -->

## 2026-08-08 状态更新：Focus Bridge 1.3.3 请求级幂等

==Android 已安装 `1.3.3 (18)`。新增持久化 request 执行账本、累计三次上限、`result_pending`、24小时完成墓碑和轮询 generation；同一 request 在旧响应、结果重传或进程重启后不能创建第二轮。通知监听保存短暂 `getaway_pomo` 事件，不再排除全部 `AUTO_CANCEL`，同时过滤已知“今天准备怎么过”推广提示。==

==Pi Advisor 的 final event 处理增加锁和完成 ID 幂等，重复请求只返回 `already_completed`，不写第二份 response。Focus Garden 权威版系统状态新增“重复请求防护”，最低合格版本改为 1.3.3；未覆盖 static、SQLite 或近期动态。真机5分钟执行在第2次捕获真实通知后 success，之后无第3次或第二轮，Pi pending 为空且只有一份 final。==

<!-- ai_provenance: source=codex; date=2026-08-08; verification=device-and-pi-tested; retrieved_notes="我的专注花园/专注花园桥接手机APP.md,PI_SERVER_HANDOFF.md" -->

## 2026-08-08 状态更新：Next Action 召回 v2 部署闭环

==近期动态召回、循环任务投影、任务时间窗和置信度兼容性已全部在 Pi 生产树生效：粗筛 30 条，V4 Flash 筛选最终六条，并读取逾期一天至未来两天的任务安排；健康/考试/硬截止与当前或 24 小时内动态拥有可审计的强制名额。最终模型保留 Flash 的排序，而不是按动态创建时间覆盖。==

==2026-08-08 22 时完成部署复核：生产源文件哈希与已验收版本一致；相关单元测试 56/56 通过；Next Action `:8450` 与 Focus Garden `:8460` 均由 Windows 端实际返回 HTTP 200，Pi 两项 loopback 服务均为 active。没有待部署运行代码或待重启服务。==

<!-- ai_provenance: source=codex; date=2026-08-08; verification=pi-source-hash-targeted-tests-and-tailnet-endpoints; retrieved_notes="PI_SERVER_HANDOFF.md,我的专注花园/树莓派 Next Action Web架构.md" -->

## 2026-08-09 状态更新：Windows Cold Turkey Agent 崩溃自恢复 P0

==Windows `computer-intervention-agent` 已将 Cold Turkey lease 在 `-start` 前以 fsync 原子写入 `starting` 状态，成功后更新为 `active`；因此 Python/Tcl 崩溃发生在启动命令附近时，重启后的 Agent 仍保有该 lease 并可在到期时精确回收。==

==Tk 的确认页和“锁机已开始”提示改由独立 `intervention_ui.pyw` 子进程显示，UI 崩溃不再终止 Agent 核心。新增常驻 `ComputerInterventionAgentWatchdog` 与每两分钟 `ComputerInterventionAgentWatchdogKick`；它们以 `agent-health.json` 心跳拉起崩溃或冻结的 Agent，同时保留原任务的失败重启。2026-08-09 已在无 active lease 条件下终止 PID 4468，验证 Watchdog 拉起 PID 35652。==

<!-- ai_provenance: source=codex; date=2026-08-09; verification=windows-unit-tests-and-live-crash-recovery; retrieved_notes="PROJECT_STATE.md" -->

## 2026-08-09 状态更新：Focus Garden 任务日历

==Focus Garden 的任务页已删除占屏的 TASK LIST 大横幅；“刷新清单”移到顶部“同步奖励”左侧。“任务清单 / 查看日历”双视图加宽至 640px，与正文视觉宽度协调。当前待办的“今天”会并入有效日期等于今天的循环任务；最近六天从今天起按桌面 3×2、手机单列完整展示任务、Priority 与番茄进度，本月视图以任务数和预计番茄数缩略显示，`highest` 改为醒目黄点并在其后显示数量。==

==日期详情使用独立弹窗。未归档且 active/upcoming 的近期动态按系统解析出的完整影响区间整合：跨度 1–2 天的动态进入对应日期，跨度至少 3 天或无法确定结束日的动态统一放在六天日历末尾；动态卡只显示原文和系统理解范围。本月格子不显示动态数量，点击日期后才显示当天可映射动态。双击任务或动态会切回对应管理页并载入稳定 ID，手机使用显式编辑按钮；跳转本身不保存。==

==本次只更新 Pi 权威生产树的 `static/{app.js,index.html,style.css}`，未改变 task-sync/recent-context API、SQLite 或 Obsidian 写回边界，也无需重启服务。Pi 32/32 测试、JavaScript 语法、loopback 三接口、系统级 `focus-garden.service` active、`127.0.0.1:8838` 监听及 Tailnet `:8460` HTTP 200 均通过；桌面与 390px 移动端已完成真实浏览器验收。==

<!-- ai_provenance: source=codex; date=2026-08-09; verification=pi-tests-tailnet-browser-responsive; retrieved_notes="我的专注花园/00-交接总览.md,我的专注花园/04-运维与扩展手册.md,PI_SERVER_HANDOFF.md" -->

## 2026-08-09 状态更新：Next Action 等待状态跨页恢复

==“为我找下一步”现在会在浏览器会话内持久化生成开始时刻和生成前建议 ID；等待卡每秒显示已等待时间（如 `1分20秒`）。切到“开始专注”再返回、或在同一标签页刷新后，页面会恢复“正在为你找下一步”，每两秒只查询已有 active suggestion，绝不再次 POST 生成。旧建议仍存在时不会被误当成新结果。==

==权威生产文件为 `/home/conrad/services/focus-garden/static/{app.js,index.html}`，已同步到 Windows 镜像 `D:\MyFocusGarden\static\`。Pi 端可回滚副本：`backups/20260809-224234-next-action-wait-state/`；Windows 镜像副本：`D:\MyFocusGarden\.backups\20260809-2244-next-action-wait-state/`。==

<!-- ai_provenance: source=codex; date=2026-08-09; verification=javascript-syntax-pi-loopback-and-windows-tailnet; retrieved_notes="PI_SERVER_HANDOFF.md,我的专注花园/树莓派 Next Action Web架构.md" -->

## 2026-08-09 状态更新：任务完成账本与每日满番茄奖励

==Pi 已上线按“任务 ID + 日期”记账的完成账本。普通任务与受支持的每周循环任务完成后仍保留在“今天”，显示为灰色勾选项且不再提供编辑；同时从开放任务集合及 Next Action/Agent 输入中排除。循环任务点击“完成本次”后，Pi 记录当天实例，并通过既有 mutation queue 把模板安排日推进 7 天、番茄完成数归零；Obsidian 两个插件与 Agent 无需修改。==

==每日计划番茄数按当天首次观察后的最大值单调保存。次日 04:10 后结算前一天：若计划至少 7 个且全部完成，日历显示大勾并发放一次可直接种植的高级植株机会。奖励以日期幂等，不折算为 3 个普通奖励；最近六天、日期弹窗与本月视图都读取同一结算记录。==

<!-- ai_provenance: source=codex; date=2026-08-09; verification=pi-unit-tests-live-services-and-tailnet-browser; retrieved_notes="PI_SERVER_HANDOFF.md,我的专注花园/01-数据来源与处理.md,我的专注花园/02-游戏架构.md" -->

## 2026-08-12 状态更新：拖延任务标记与 Next Action 优先级

==Focus Garden 的“推迟一天”现由独立 `postpone` 意图进入 Advisor；Pi 在 `data/task_sync/state.json` 中累计每个任务实际向后移动的天数。累计推迟 1 天只记录，达到 2 天即输出 `procrastinated=true`，并在当前待办和任务日历任务卡显示“拖延 · N天”。普通日期编辑不累计；任务完成或删除后清除该任务的拖延计数。现有历史无法从旧快照可靠反推，因此从本次部署后的“推迟一天”操作开始累计。==

==Next Action 提示词版本升为 `next-action-v1.4-procrastination-priority`。只要存在仍可行动的拖延任务，候选排序、硬规则、模型结果校验和本地 fallback 均要求先从拖延任务中选择，并明确累计推迟天数；午休、深夜睡眠等既有非任务硬规则仍优先。==

<!-- ai_provenance: source=codex; date=2026-08-12; verification=pi-tests-services-and-tailnet; retrieved_notes="PI_SERVER_HANDOFF.md,我的专注花园/树莓派 Next Action Web架构.md,我的专注花园/04-运维与扩展手册.md" -->


## 2026-08-14 状态更新：Steam 半小时监控、夜间锁定与专注联动

==Steam 客户端、Steam 商店和当前已识别的 Steam 游戏（含 `Game.exe / 祈愿诗篇`）现由确定性规则锁定为 `entertainment`。半小时主流程只统计 report scope 内带 `steam_entertainment` 标签的时长，并把 `steam_activity_minutes` 写入介入候选；每次 08/38 分检查中，该值严格超过 5 分钟便以独立 `steam_activity` 原因令 `would_intervene=true`，把 Cold Turkey `steam游戏` 加入共享提醒，不再依赖其他行为触发理由。首次拒绝保留提醒，第二次连续拒绝转强制执行；强制 Steam 锁定前 Windows 弹出不可关闭的 60 秒存档倒计时。==

==Focus Garden 的 `focus.always_windows_blocks=["steam游戏"]` 是服务端不变量：每次专注都会按该 session 的剩余时长锁 Steam，即使用户只选手机或以后新增专注 profile；暂停、取消、结束和休眠补偿仍沿用 lease ownership 的 `-stop` 路径。2026-08-14 的初版夜间可回收 lease 已由下述 2026-08-15 硬锁与解锁门槛替代。==

<!-- ai_provenance: source=codex; date=2026-08-14; verification=windows-unit-tests-pi-targeted-tests-services-tailnet-and-deterministic-sample; retrieved_notes="DECISIONS.md,PI_SERVER_HANDOFF.md,我的专注花园/02-游戏架构.md" -->

## 2026-08-15 状态更新：Steam 夜间硬锁、主要任务与解锁门槛

==23:30 现在由 Windows Agent 显示 60 秒 Steam 收尾框，可立即关闭精确游戏路径 `C:\steam\steamapps\common\Magical Girl Celesphonia\Game.exe` 并获得一次普通植物奖励，或按 15 分钟档延时，最晚到次日 01:00。无操作或延时到点后先给足 60 秒存档时间，再关闭游戏并使用 Cold Turkey `-lock` 硬锁至 12:00；倒计时窗口按控件实际请求高度动态扩展，数字和“秒”均保留完整下边距。==

==任务清单仅在今天和明天的任务上显示“设为主要”，每个日期至多一个；按钮位于原四按钮上一行右侧。当天必须获得至少 5 个完成任务番茄且当天主要任务已经完成，Steam 解锁门槛才通过：一项任务整项完成时一次性按其 `tomatoes_total` 计入，未完成任务的中途进度（如 `2/4`）完全不计；解锁指标最多显示到 `5/5`。否则 12:00 后 Windows Agent 继续滚动续上 5 分钟硬锁，Pi 离线时采取不解锁。主要任务同步进入 Next Action，但只作既有拖延、时段、健康和休息规则之后的软性参考。==

<!-- ai_provenance: source=codex; date=2026-08-15; verification=windows-19-tests-advisor-37-tests-garden-targeted-tests-live-api-and-browser-ui; retrieved_notes="DECISIONS.md,PI_SERVER_HANDOFF.md,我的专注花园/02-游戏架构.md" -->

## 2026-08-15 状态更新：系统状态显示 Steam 解锁原因

==Focus Garden“系统状态”的健康面板最后新增“Steam 解锁指标”宽卡。它同时显示总体状态、当天完成番茄的当前值/要求值、今日主要任务是否设置及是否完成，并把所有阻塞原因合并展示；例如 `0 / 5` 时会明确写“还差 5 个完成番茄”，未设主要任务时另列“今天尚未设置主要任务”。任务同步暂不可用时显示数据不可用并说明系统会保守保持锁定。==

==`GET /api/system-status` 新增不含任务标题和正文的 `steam_unlock` 摘要，读取 Advisor gate 最多等待 3 秒。页面验收确认该卡位于系统状态健康卡片列表的最后；2026-08-15 当前实况为 `0/6`、未设置主要任务、未达成。==

<!-- ai_provenance: source=codex; date=2026-08-15; verification=pi-targeted-tests-live-api-and-browser-dom; retrieved_notes="PI_SERVER_HANDOFF.md,我的专注花园/04-运维与扩展手册.md" -->

## 2026-08-15 状态更新：Focus Garden 周级控制层

==Pi 已上线只读控制聚合器与系统状态首屏 UI。主指标固定为 M、D、W、L、A、F、U、R；AI 仅作辅助诊断，不计算 R_c。D 的权威来源是显式“推迟一天”形成的 `postponements.postponed_days`，只汇总仍未完成任务，按优先级加权并逐项封顶 7 天。每日 D 快照与七日冻结周评审均由 systemd timer 驱动；控制层不直接修改硬规则。==

==初始冻结结论为 S7，冻结至 2026-08-22 13:17（Asia/Shanghai）。原因是数学任务匹配覆盖不足且 D 历史基线刚开始积累。当前可读摘要：D=4（2 项，最大推迟 2 天），A=21.4%，F=100%，U=71.4%，R=12.1%；这些数值用于诊断，不合成为自律总分。==

<!-- ai_provenance: source=codex; date=2026-08-15; verification=pi-tests-live-api-services-timers-tailnet-browser-and-mirror; retrieved_notes="我的专注花园/系统层控制&识别系统执行效果.md,PI_SERVER_HANDOFF.md" -->

## 2026-08-15 状态更新：控制指标可手动同步

==Focus Garden 系统状态首屏新增“同步状态”。`POST /api/control/sync` 立即更新今日 D 与实时聚合，保存到 `data/control-live.json`；当前周冻结结论继续由 `data/control-review.json` 提供。界面会区分“数据已同步 · 决策冻结”和“待周评审”，并显示最近同步时间。==

==同步接口经 Tailnet 实测保持 S7 和原冻结截止时间不变；生产控制测试 6/6、Windows 全量 43/43。数据充足后的准入门槛、同类日期稳健基线、单参数实验、回滚条件和永久人工维护边界已写入 Focus Garden 控制设计文档。==

<!-- ai_provenance: source=codex; date=2026-08-15; verification=pi-api-browser-and-windows-tests; retrieved_notes="我的专注花园/系统层控制&识别系统执行效果.md,PI_SERVER_HANDOFF.md" -->

## 2026-08-31 状态更新：独立目标模式 Goal Agent

==“我的专注花园”已上线独立“目标模式”。Goal Agent 的职责是衡量距离长期目标的证据、管理月/周计划并调整策略；Next Action 仍只推荐当前行动。两者提示词、模型配置、聊天、SQLite 和审计历史相互独立，只通过 task-sync 中的共享任务与稳定完成证据联动。==

==当前 Portfolio 为“2028 级保研到数学所何伟鲲方向”，四轨道权重为专业课 40%、数学所笔试 20%、遍历论与导师交流 30%、抽象代数 10%。首个 4 周试运行从 2026-08-31 到 09-27，每周 1590 分钟；工作日推荐不超过 180 分钟，周末每一天不超过 480 分钟。生产计划为 v1，本周 12 项、证据 0、授权资料 0，因此四轨道和吞吐量均正确显示“未知”，没有生成虚假进度。==

==Goal Agent 运行在 Advisor `127.0.0.1:8767` 内，权威库为 `data/goal_agent/goal-agent.sqlite3`；Focus Garden `127.0.0.1:8838` 只通过固定白名单代理 Goal API，外部入口仍是 tailnet-only `:8460`。周日 20:30 的 `goal-agent-review.timer` 已启用。Tavily 已安全复用 Codex MCP 的同一把密钥，Pi 实测公共查询 HTTP 200；密钥只在私有环境文件中。==

==验收结果：Advisor 199/199、Pi Garden 48/48、Goal 增量 12/12、Windows 导出器 11/11、Windows Garden 镜像 48/48。Goal SQLite `quick_check=ok`、权限 600；旧计划版本写请求实测返回 409 且不产生证据。尚未点击真实“确认这一天”、未运行真实 AI 对话，也尚未经历第一次自然周复盘。==

<!-- ai_provenance: source=codex; date=2026-08-31; verification=pi-production-tests-tailnet-api-tavily-and-windows-mirror; retrieved_notes="计划模式/00-目标模式总览与方案设计.md,计划模式/02-当前完成与待补充.md" -->

## 2026-08-31 状态更新：目标模式 v2 课程闭环与 GPT-5.6 Sol

==Goal Agent 生产已升至 schema v3、plan version 5。本周保持 12 项、1590 分钟；2026-09-01 起由 GTM259 与抽象代数先行，概率论保持 awaiting_course_progress。新课堂笔记自动生成“实际主题 + 建议目录映射 + 教材对照”草稿，用户确认后才计入进度；作业按文件名发现并拆成多个不超过 180 分钟的学习任务。==

==课程档案已录入教师、教材、大纲、考核比例和课时冲突，考试日期仍未知。生产库新增 course_profile、course_unit、course_progress_event、course_unit_mastery；共 3 个课程档案、110 个稳定小节。用户提交 course_progress 后，系统只改写同课程本周两项任务的标题、说明和 ready 状态，不改变周总分钟。未 ready 的任务不能确认日期或写入 task-sync。==

==Windows Behavior Context Exporter 升级到 v6，已授权四个学习目录、教材 PDF 和课程档案，共 45 份资料、0 个错误。`几何/微分几何/1.1.md` 已按 MathInk 可见层索引：普通 Markdown、LaTeX 和忠实识别文字保留，笔迹 payload、base64、图片二进制和画布坐标不导出。==

==Goal Agent 独立使用 `gpt-5.6-sol`、Responses API、`medium` 推理，密钥位于 Pi 私有 `goal-agent.env`（600）。中转站不接受 JSON Schema 时仅在同一模型/协议内退回提示词 JSON 契约，不使用 DeepSeek fallback；Next Action 与其他 AI 组件路由不变。验证结果为 Goal 24/24、Advisor 209/209、Pi/Windows Garden 49/49、导出器 13/13；Pi 真实复盘返回合法 JSON、0 项修改和 8 条公开搜索结果。模型误报单日 636 分钟后，确定性 API 复核为 456 分钟并拒绝该事实判断。==

<!-- ai_provenance: source=codex; date=2026-08-31; verification=pi-tests-tailnet-api-sqlite-migration-exporter-and-browser; retrieved_notes="计划模式/02-当前完成与待补充.md,计划模式/05-v2课程进度与GPT-5.6迁移验收.md" -->

## 2026-08-31 状态更新：UCAS 漫游检测与电脑热点自动回退

==Pi 间歇性 Tailnet 掉线已定位为板载 2.4 GHz Wi-Fi 在两个 UCAS BSSID/信道之间反复重关联，不是 UCAS 整体网络、Pi 负载、欠压或 Focus Garden 服务故障。电脑使用独立 5 GHz BSSID且稳定。当前暂不锁定 Pi BSSID。==

==Windows `XYH 0563` 热点由用户按需开启；自动 Startup launcher 和常驻 watchdog 已移除，但 `D:\tools\pi-network-fallback` 中的热点保障脚本完整保留。Pi `wifi-failover.timer` 每 30 秒检查默认路由、IPv4 204 和 IPv6 HTTPS；双栈连续 4 次失败才尝试热点。电脑 Tailnet peer 不参与触发，电脑被带走不会误切换。热点未开启时，Pi 会恢复 UCAS并进入冷却。==

==Pi 热点 profile 已完成两次真实连接：Windows 客户端数 0→1，热点期间 SSH/Garden 可用，自动回切后恢复 UCAS。触屏面板已新增“一键恢复热点连接”，后端与自动 failover 共用脚本，连接失败立即恢复 UCAS。测试 9/9，timer enabled/active，面板循环进程已重启。==

<!-- ai_provenance: source=codex; date=2026-08-31; verification=wifi-logs-real-switch-tests-systemd-and-on-demand-hotspot-policy; retrieved_notes="树莓派UCAS无线漫游与电脑热点自动回退.md" -->


## 2026-08-31：课表导入与系统适配

==课表已导入 Advisor，24 条规则展开去重后为 214 次课程、11 种课程名称。Next Action、Goal Agent、半小时/每日复盘和花园页面共用同一课表。默认出勤，课前20分钟至下课受保护；不增加统计、番茄或奖励，不改变课外学习预算，不新增推送。==

详见 [[树莓派课程表导入与系统适配]]。

<!-- ai_provenance: source=codex; date=2026-08-31; verification=checked; retrieved_notes="PROJECT_STATE.md" -->

## 2026-08-31 状态更新：任务类型快速证据反馈 v2

==Goal 模式“证据与资料”已上线任务驱动的快速表单。本周任务卡可直接“记进度”，课程卡可“记录上课”；课程、练习、证明、成绩、限时真题、阅读、讲解、口试和受阻分别只显示本类型字段。课程成绩绑定已确认考核比例；做题区分最终正确与独立正确；真题同时记录独立、新题、限时和评分条件。未填和未核验值保持未知，不转成 0。==

==Goal Agent 保存结构化 performance/conditions 和判断边界，并在完整复盘时根据最近证据检索已授权材料片段。确定性达标指标先检查题源、辅助、核对、限时和新颖度，模型不能把单次自评或不完整条件提升为长期掌握。生产当前 plan version 5；Advisor 253 tests（skipped=1）、Pi Garden 50 tests、Windows exporter 13 tests 全部通过，Tailnet 页面/API 返回 200。`<25 秒` 仍需真实用户逐类型计时，不以自动化速度宣称达标。==

<!-- ai_provenance: source=codex; date=2026-08-31; verification=pi-full-tests-loopback-tailnet-browser-and-windows-mirror; retrieved_notes="计划模式/06-任务类型快速证据反馈v2部署验收.md" -->

## 2026-09-01 状态更新：半小时提醒、Steam 锁机、手机桥接与作息目标

==现场确认 `activitywatch-advisor.timer` 仍按每小时 08/38 分运行，2026-09-01 半小时报告连续写入；ntfy 半小时检测只在 `would_intervene=true` 时发送，其他窗口的 `shadow_candidate_would_not_intervene` 是策略性跳过，不是定时器未启动。==

==修复 Windows agent 的 Cold Turkey 假成功：实际 `-list-blocks` 中可用 block 为 `steam`，原配置调用不存在的 `steam游戏` 时虽返回 exit code 0 但输出 `Invalid block name`。现保留策略显示名 `steam游戏`，映射到实际 block `steam`，并在硬锁函数先检查错误文本。==

==截图中的 Android `UnknownHostException` 是当时手机无法解析 Funnel 主机名；权限连接不是根因。当前 Pi 最近多条心跳为 `app_version=1.3.4`、`transport=public_https`、`last_poll_status=no_pending`、无 `last_error`。Android 源码新增前台心跳请求去重和更明确的失败日志，APK 已离线构建通过；待 ADB 设备重新出现后覆盖安装并做真机复测。==

==Focus Garden 首页新增“作息目标”卡片和 `/api/sleep-goal`。目标周期为 2026-09-01 至 2027-01-17，每七天至少 5 天不晚于 00:30，另外 2 天不晚于 01:00；数据来自 Advisor `daily_life` 的手机夜间亮屏边界，只作估计，不等同于生理入睡。==

详细交接与回滚路径见 [[半小时提醒_手机桥接_作息统计修复交接]]。

==2026-09-01 23:30 Steam 自然周期已验证：选择 UI 记录 `UI launch`/`UI finished`，无操作后 `decision=timeout`，随后 `hard_lock_result.cold_turkey_block=steam`、`status=success` 且无 Invalid block name。==

==2026-09-01 23:46 设备侧最终闭环：使用独立 ADB server 5038 核对手机 `V2241A/PD2241` 与 vivo Pad5e `PA2535/DPD2345M`；手机覆盖安装 Focus Bridge 1.3.4 (19) 成功，安装后 Pi 连续收到 `public_https` 心跳且 `last_error` 为空；平板 AutomateAccessibilityService 仍 binding。==


<!-- ai_provenance: source=codex; date=2026-09-01; verification=pi-production-api-systemd-windows-agent-tests-android-build; retrieved_notes="PI_SERVER_HANDOFF.md,树莓派行为数据与接口索引.md" -->


<!-- ai_provenance: source=codex; date=2026-09-03; verification=checked; retrieved_notes="目标模式/09-Goal Agent三阶段上下文与手写语义检索实施计划.md" -->

## 2026-09-03：Goal Agent 三阶段上下文、手写可见层与语义检索（隔离 staging）

==三阶段实现已在本地隔离 staging 完成：Context Pack/readiness、MathInk 安全投影与 10 条请求回放；低切分 Semantic note/window 索引与 20 条开发集评测；operation registry、批量授权执行验证和 Garden UI 协作。Advisor staging 为 156 passed、1 skipped，Garden staging service 为 27 passed。==

==Pi 生产部署尚未执行。2026-09-03 的 Pi MagicDNS、最后已知局域网地址和 Tailnet `:8460` 均连接超时，因此没有修改生产源码、数据库、服务或静态资源。==

详见 [[目标模式/09-Goal Agent三阶段实施验收记录-2026-09-03]]；本地回退备份为 `D:\mathblog\quartz\content\.codex_tmp_goal_backups\goal-implementation-final-verified-20260903-105406`。

<!-- ai_provenance: source=codex; date=2026-09-03; verification=pad5e-chrome-pi-ssh-http-and-policy-netmap; retrieved_notes="Tailscale中继配置与当前故障交接-2026-09-03.md" -->

## 2026-09-03：Tailscale Peer Relay ACL 修复与 Pad5e 页面恢复

==本次故障根因是 Access controls 中只保留了 Peer Relay capability grant，没有保留普通设备互访的 `ip` grant。补充 `kzpeng565@gmail.com` → `autogroup:self` 的 `ip: ["*"]` 后，Tailscale 网络图恢复普通节点间访问。==

- Pad5e `PA2535` / `100.124.57.79` 的 Tailscale VPN 为 Connected，`tun1` 正常；Chrome 实际加载 Paseo 与 Focus Garden。
- Paseo `https://xyh.taild4d3f7.ts.net/` 与 Focus Garden `https://pi.taild4d3f7.ts.net:8460/` 均从 Pad5e 返回 HTTP 200。
- Pi `tailscaled.service`、`focus-garden.service` active；Pi 本地 `127.0.0.1:8838` 返回 200，`:8460` Serve 仍为 tailnet-only；本次没有修改 Pi 服务、数据库或静态资源。
- 当前页面恢复使用 DERP(sin)，Peer Relay 候选仍存在，但 `peer-relay(...:40000)` 还需连续 5 次及跨校园 Wi-Fi/手机热点验收。
- 后续仍需手动测试 Pad5e 切回 `vivo X90` 热点和熄屏约 30 分钟后的恢复；Pi `tailscale serve status` 中已有历史 Funnel 项需另行安全审计。

<!-- ai_provenance: source=codex; date=2026-09-03; verification=production-deployed-and-tested; retrieved_notes="目标模式/09-Goal Agent三阶段上下文与手写语义检索实施计划.md,目标模式/09-Goal Agent三阶段实施验收记录-2026-09-03.md" -->

## 2026-09-03：三阶段实现已部署到 Pi，Semantic 保持 shadow-only

==Pi 生产逐文件部署已完成。Advisor 的 Goal Agent/Context Pack/Semantic index/Operation Gateway/task-sync 来源标签和提示词，以及 Focus Garden 的 Context Pack/operation 代理和授权界面均已激活；Pi 原有 settings、Focus Garden 配置、control_metrics、sleep_goal、course_schedule 和私有素材均保留。==

- Pi 代码 dated backup：`/home/conrad/workspace/backups/goal-agent-three-stage-20260903-120507/`；post-deploy Goal SQLite 一致副本 `quick_check=ok`；
- Advisor 标准库全量：277 tests OK，skipped=1；
- Focus Garden 标准库全量：52 tests OK；
- `activitywatch-advisor-web.service`、`focus-garden.service`、`goal-agent-intake.timer`、`goal-agent-review.timer`：active；
- Tailnet `:8460`：schema 4、plan 6、GPT-5.6 Sol；Context Pack compile/get、HTML cache-busting 和数据库 payload 安全检查通过。

==生产 embedding provider 未配置，Semantic 当前明确保持 `not_ready`/`retrieval_degraded` shadow-only。真实 Qwen3-Embedding-8B development 评测和主召回激活仍是待完成门禁；不以本地确定性 embedder 结果冒充生产质量。==
生产 embedding scope dry-run manifest：`/home/conrad/workspace/activitywatch-advisor/data/goal_agent/semantic-scope-dry-run-20260903.json`；范围 133 个已授权文档、1807 个窗口，manifest 不含正文，provider 缺失时 `activation_allowed=false`。

<!-- ai_provenance: source=codex; date=2026-09-03; verification=relay-vps-ssh-tailscaled-metrics-pad5e-hotspot-chrome; retrieved_notes="Tailscale中继配置与当前故障交接-2026-09-03.md" -->

## 2026-09-03：Peer Relay 服务修复与热点路径验收

==中继 VPS 已建立 root 密钥 SSH，`tailscaled.service` 重启后 active，UDP `40000` 和静态端点保持正确。Pad5e 切换到 `vivo X90` 手机热点后，Windows→Pad5e 连续 5 次均显示 `peer-relay(47.116.106.206:40000)`，VPS VNI 88 双向包持续增长，Paseo/Focus Garden HTTP 与 Chrome 页面均通过。==

UCAS 路径仍主要使用 DERP(sin)，作为不同网络的回退结果单独记录；不能用 UCAS 的 DERP 结果否定热点路径下已通过的 Peer Relay。后续保留 UCAS/热点各自的网络稳定性与熄屏恢复验收。
<!-- ai_provenance: source=codex; date=2026-09-03; verification=custom-derp-ucas-10x-debug-derp-long-lived-pad5e-tcp443-http; retrieved_notes="Tailscale中继配置与当前故障交接-2026-09-03.md" -->

## 2026-09-03：自建 DERP 在 UCAS 下验收通过

==方案二已完成基础验收：ECS `derp.pengmath.me` 的 TCP443/UDP3478、Let's Encrypt、region 900 `pym` 和 `verify-clients` 正常；Windows/Pi 在 UCAS 下各 10/10 DERP/STUN 诊断成功，Pad5e UCAS 长连接已出现在 ECS derper，Paseo/Focus Garden HTTP 200。==

自建 DERP 作为 direct/Peer Relay 不可用时的近距离 TCP443 回退，公共 DERP 保持开启；Pad5e 熄屏恢复和 24 小时稳定性仍待观察。

<!-- ai_provenance: source=codex; date=2026-09-03; verification=production-recheck-after-progress-and-cache-implementation; retrieved_notes="目标模式/09-Goal Agent三阶段上下文与手写语义检索实施计划.md" -->

## 2026-09-03：Goal Agent 三阶段最新复核

==三阶段代码继续保持 Pi 生产可用：Advisor 281 tests OK（skipped=1）、Focus Garden 52 tests OK、相关服务和 Goal timers active、Tailnet Goal 入口 HTTP 200、Goal SQLite quick/integrity check 均 OK。==

==Semantic 当前 active build 仍为旧的 `sem-4d2cce788bff40eab58002bedb7366a1`，1836 个 ready window；旧的 Semantic + FTS hybrid 搜索不变。新代码包含安全来源锚点、输入 hash、note-level cache 和重建进度元数据，但新的 Qwen summary-anchor build 尚未发送或激活。==

==阶段二按停止条件保持 `semantic_shadow_only`。旧 production development evaluation 的 Semantic Recall@5=83.33%，FTS/hybrid=100%，forbidden=0、duplicate-primary=0；不能把纯 Semantic 90% 门槛或新锚点评测称为已通过。==


<!-- ai_provenance: source=codex; date=2026-09-03; verification=production-recheck-stale-index-and-context-replay; retrieved_notes="目标模式/09-Goal Agent三阶段上下文与手写语义检索实施计划.md" -->

## 2026-09-03：Semantic 索引漂移检测与 Context Pack 回放

==生产发现 1836 个授权窗口中有 1 个尚未 embedding。Semantic ready_info 现按 active build、model、授权窗口覆盖率计算：当前报告 `stale`，而不是错误报告 `ready`；Context Pack 自动进入 retrieval_degraded，FTS 继续可用。==

==Pi Advisor 282 tests OK（skipped=1），Focus Garden 52 tests OK；Tailnet 三个入口 HTTP 200；10 条生产 Context Pack 回放 10/10 通过且不写入、不调用外部 provider；SQLite quick/integrity check OK。==


<!-- ai_provenance: source=codex; date=2026-09-03; verification=production-summary-anchor-v3-evaluation-and-hybrid-fix; retrieved_notes="目标模式/09-Goal Agent三阶段上下文与手写语义检索实施计划.md" -->

## 2026-09-03：Goal Agent 三阶段最终完成

==summary-anchor v3 Qwen 索引已生产激活并通过 24 条评测：unscoped Semantic Recall@5=95.83%，scope-constrained Semantic/Hybrid=100%，warm p95=402.28ms，duplicate/forbidden=0。阶段一、二、三全部完成。==

==Pi Advisor 285 tests OK（skipped=1），Focus Garden 52 tests OK；Tailnet、服务、SQLite 和 Context Pack 门禁通过。材料后续变化会使 Semantic 自动 `stale` 并回退 FTS，待日常增量 rebuild。==

## 2026-09-04：OpenLux Luna 路由、材料分析提示词与半小时报告迁移

- Goal Agent 材料分析和周复盘已切换到 `https://api.openlux.ai/v1/responses` 的 `gpt-5.6-luna`，Responses `reasoning_effort=medium`；目标模式聊天仍保持 `gpt-5.6-sol`。
- 目标模式进入时先执行材料发现；`goal-agent-intake.service` 已改为 `--discover-only`，不会在后台自动调用模型。材料卡片点击“分析”才针对单文件调用 Luna。
- 课堂笔记提示词已改为概念结构分析：合并同一理论链条，把推论、命题、注和公式编号放入来源定位，不再把原始标题机械平铺；课堂掌握度改为必须人工选择，不再默认 1。
- 半小时报告链路的 parser、recent-context selector 和 report 已切换为 OpenLux Luna medium；不影响目标模式聊天和其他明确独立路由。
- Luna 密钥来源为 Windows `C:\Users\15345\Desktop\luna的密钥.txt`，Pi 运行期仅保存于 `/home/conrad/.config/activitywatch-advisor/goal-agent-luna.env`，权限 `600`；未写入仓库、前端、SQLite 或文档。
- 旧 AI 配置已备份并通过 SHA256 校验：`/home/conrad/workspace/backups/ai-routing-before-luna-20260904-203500/`。备份包含旧 settings、Goal/recent-context 代码和提示词，以及原 Goal 环境文件。
- 验收：Advisor 全量 `285 tests OK (skipped=1)`；Focus Garden `52 tests OK`；真实材料分析 smoke 使用 `gpt-5.6-luna/medium` 并将泛函分析材料整理为 5 个概念主题；周复盘 smoke 为 Luna/medium；半小时 parser 与 selector smoke 均为 Luna/medium；相关服务 active。
- 仍需用户在真实 Focus Garden 页面确认一次：进入目标模式时只识别不分析，点击“分析”后显示新的分组结果；聊天继续走 Sol。

## 2026-09-04：AI 课程目录映射与待确认队列刷新修复

- 课堂笔记分析现在把当前课程目录的 `course_catalog` 一并传给 Luna；Luna 必须返回有效 `catalog_unit_id` 或 `null`，并给出 `catalog_reason`。有效映射会在填写表单时自动预选；没有可靠对应时自动保持“不映射”，仍可人工调整后整体确认。
- 课程目录映射仍属于用户最终确认的一部分；分析阶段不会直接写入课程掌握度或课程目录覆盖。
- 修复“忽略”后的慢刷新：目标模式进入时继续 discovery；忽略、分析、分类、确认等普通操作使用 `state?discover=0` 快速状态刷新，不重复扫描全部材料。`state(refresh_materials=False)` 实测约 121 ms。
- 泛函分析真实候选重新分析成功：Luna/medium 生成概念分组并返回自动目录映射；候选仍保持 `awaiting_confirmation`，没有自动写入课程进度。
- 回归：Advisor 77 项 Goal/模型/recent-context 测试通过；Focus Garden 52 项测试通过；服务仍为 active。

## 2026-09-04：作业时间估计改为按题目难度分档

- 作业分析不再依据“证明题/选择题/普通题”等题目类型直接赋予时间。
- Luna 分析每道题的完成难度：`easy`、`moderate`、`hard`、`very_hard`，系统固定映射为 20、40、60、90 分钟；最终分钟数由系统根据 difficulty 计算，不直接信任模型任意分钟值。
- Luna 提示词要求综合推理链长度、构造要求、先修知识跨度、步骤数量、多个引理/反例需求和预计卡点判断难度；信息不足时使用 `moderate` 并标记不确定性。
- 未调用 Luna 的确定性回退不再根据题目类型判断，统一使用 `moderate=40` 并标记为 fallback；这不是正式难度判断。
- 作业确认提交后，系统先创建 Goal SQLite 中的 `assignment`、`assignment_block` 和未确认的 `plan_item`，并计算推荐日期；此时尚未进入 Obsidian Tasks/task-sync 队列。
- 只有继续点击“确认全部无冲突学习块”并通过容量检查后，系统才逐项执行 `accept-day`、写入 task-sync mutation queue；随后仍需桌面 Obsidian 写入器执行并收到 snapshot ack，才能报告为已同步。
- 当前回退备份：`/home/conrad/workspace/backups/assignment-estimation-before-difficulty-20260904-223500/`。
- Advisor 全量回归：285 tests OK（skipped=1）。

## 2026-09-05：简化 Luna 作业完成时间判断规则

- 作业题仍使用四档：20、40、60、90 分钟；Luna 先输出 `easy/moderate/hard/very_hard`，系统固定映射分钟数。
- 提示词改为直观完成时间判断，不再要求过度精细分析：三个或更多小问按整体难度选 60/90；定理直接应用或常规题选 20/40；涉及构造选 60/90；两个小问或多步常规题通常选 40/60。
- 同一道顶层编号题的小问保持为一个 problem，不拆散；`difficulty_reason` 只用一句话说明小问数量、常规应用或构造等主要依据。
- 仍禁止仅依据“证明题/计算题/选择题”等题型直接分档；信息不足时回退 40 分钟并标记不确定。
- 真实泛函分析作业 smoke：题目1（两个证明小问、多性质论证）=60 分钟，题目2（两个常规小问）=40 分钟，合并为100分钟学习块；模型为 OpenLux `gpt-5.6-luna`、medium。
- 回退备份：`/home/conrad/workspace/backups/assignment-luna-prompt-before-simple-rules-20260905/`；Goal Agent 38 项专项测试通过。

## 2026-09-05：目标模式渐进加载、手动重载与空文本候选修复

- 新增轻量只读接口 `GET /api/goal-agent/summary`：不等待材料摄取锁，只返回总目标、轨道摘要和当前周任务；Pi 回环 3 次实测约 `33 ms`，Windows 经真实 `:8460` Tailnet 入口约 `187 ms`。
- 目标模式首屏先并行加载 `summary + plan`，当前任务出现后再后台加载证据、资料、聊天和审批历史；进入目标模式不再自动扫描全部材料。
- 修复 Focus Garden 固定代理曾丢弃 `?discover=0` 的问题；详细状态现在确实绕过材料发现。Garden 回环实测约 `0.28–1.44 s`，Windows Tailnet 实测约 `0.80 s`。
- 页面内保留首次加载结果；切换菜单后返回直接复用内存状态。右上角新增“重载目标模式”，只有点击该按钮或完成写操作后才主动刷新目标数据。
- “同步奖励”只在“我的花园”和“奖励记录”显示；“刷新清单”仍只在任务清单显示；“重载目标模式”只在目标模式显示。
- 没有安全可见文字的材料不再进入待确认队列；已撤回或已改名且仍处于失败状态的候选会自动标记为 `superseded`。截图中的 `概率论习题1.md` 与 `概率论习题02.md` 旧候选已移出队列，当前活动的同类空文本错误为 `0`。
- 回归：Advisor 41 项专项测试、Focus Garden 28 项测试均通过；两个服务已重启并为 `active`。以上为 API/代码自动验证，仍需在 vivo Pad5e 浏览器确认视觉与自然使用体验。

## 2026-09-05：Goal Agent 聊天优先级、索引门禁、引用与冲突校准

- 生产配置新增 `goal_agent.rebuild_semantic_before_answer=true`。每次聊天或完整复盘在编译 Context Pack 前运行语义索引重建；重建失败或最终检索状态不是 `semantic` 时停止回答，不再静默生成 `retrieval_degraded` 建议。
- 无材料变化时，重建执行完整覆盖/哈希校验但复用当前 build，不调用 embedding provider、不创建新版本和历史向量，避免 790MB Goal SQLite 因每次回答归档而持续膨胀。材料变化时才嵌入缺失窗口并保留可回滚版本。
- Context Pack 新增 `priority_context`：真实未完成作业按已确认 `due_date` 优先；DDL 未知的必修课作业继续给临时顺序，但必须标注“DDL未知，需核验”，并以尽量在下周一或下一次相关课程前完成作为规划目标，而非虚构 DDL。
- 日期语义固定：只有 `due_date` 可称 DDL/截止/到期；`recommended_date` 是推荐日，`accepted_date` 是用户确认执行日，`scheduled_date` 是任务安排日。过去的推荐日只能称“推荐日已过/计划欠账”。
- 作业保持最高优先级，但每完成一到两个作业块可穿插一个其他学习块或必要健康任务，且继续受每日容量约束。
- 修复任务引用：宽泛的“周末做什么”不再产生 20 个低置信度引用；显式 GTM259/Recurrence/Sylow/Hahn–Banach/章节信号保留 medium/high 引用；同一 Goal plan 与 task-sync 项合并。
- 修复阶段冲突：同一 planning batch 的“第1–4周”与“第5–12周” recurring task 只激活当前阶段。2026-09-05 生产 effective state 已抑制未来第5–12周 7项任务，保留第1–4周任务；源 Vault 任务未删除，抑制记录在 `prevented_conflicts`。
- 当前语义索引仍为 `stale`，缺 4 个窗口；下一次真实聊天会先重建这 4 个窗口，成功后才回答。因该 smoke 会把授权材料投递给 SiliconFlow embedding provider，并把 Context Pack 发送到聊天模型，未在没有单独敏感传输批准时主动执行。
- 生产全量回归：296 tests OK，1 skipped；Advisor、Focus Garden、intake timer 均 active。
- 已安装个人 Skill：`C:\Users\15345\.codex\skills\goal-mode-calibration`，显示名“目标模式校准”。

## 2026-09-05：Goal Mode 详情加载锁修复

- 根因：`/api/goal-agent/state?discover=0` 会在每次详情请求前重复执行材料导入；已完成导入的 `material_record` 仍被无条件更新，多个 Garden 请求与 `goal-agent-intake.service` 竞争 Goal SQLite 写锁，Advisor 线程因 `database is locked` 异常断开，Garden 才显示 `Remote end closed connection without response`。
- 修复：Pi 生产 `src/goal_agent.py` 串行化进程内材料导入，按安全材料索引签名跳过无变化重导入，跳过已存在 FTS/窗口的无变化材料写入，并将 SQLite busy timeout 从 20 秒提高到 60 秒。保留精确回滚备份 `/home/conrad/workspace/activitywatch-advisor/backups/20260905-1945-goal-state-lock-fix/`。
- 验证：`py_compile`、Goal Agent/API/Context Replay 44 项测试、SQLite `quick_check=ok`；Advisor 与 Focus Garden 详情接口均返回 HTTP 200、209239 bytes；六路并发详情请求均成功；semantic index 为 `ready`，相关服务与 intake timer 为 `active`。
- 限界：Pi 本机对自己的 `:8460` Tailnet Serve 回环不可用；本次 Windows 端 Tailscale 本地 API 权限不足，未完成真实浏览器端 Tailnet UI 验收，需用可访问 Tailnet 的客户端再点开当前任务确认视觉显示。

<!-- ai_provenance: source=codex; date=2026-09-08; verification=pi-production-schema-v5-80-goal-tests-53-garden-tests-no-model-review-smoke; retrieved_notes="目标模式/12-Goal Mode月计划与滚动周复盘部署验收-2026-09-08.md" -->

## 2026-09-08：Goal Mode 月计划—滚动周计划—复盘闭环上线

==生产 Goal SQLite 已迁移到 schema v5：未来周只保留 title/rough_minutes；周复盘封存 review_fact 后依次运行复盘器、规划器和审查器，保存未生效 planning_draft，整版批准后才原子更新月计划、周粗计划和目标周详细任务。==

==三门必修课作业预留初始为每门每周 200 分钟，至少两个可靠作业样本后按滚动中位数 +15% 调整，自动范围 120–360 分钟；吞吐量不足三个完整自然周或实际耗时覆盖率不足 80% 时继续使用 1590 分钟基准。==

==生产迁移保留 52 个计划项、6 个确认日期、3 个完成状态和 6 个 task 映射；24 个未来旧预制项只归档不删除。Advisor 80 tests、Garden 53 tests、生产/离线 SQLite quick/integrity、Tailnet 四个入口以及不调用模型的 27-fact 复盘 smoke 均通过。==

Goal 完成表单现要求整数实际分钟或显式“未记录”；提交成功后任务保留在“今日已完成”并显示完成同步状态。并发 Context Pack 编译已串行化，完整复盘代理窗口为 900 秒。Pad5e 只剩真实页面触控验收；设备可 ping，但本次没有可用 ADB transport/当次无线调试端口。

<!-- ai_provenance: source=codex; date=2026-09-09; verification=pi-production-schema-v6-real-review-exporter-tests-integrity; retrieved_notes="目标模式/目标模式：整体架构与数据流.md" -->

## 2026-09-09：Goal Mode 复盘可靠性、任务拒绝与最新课堂笔记修复上线

==生产 Goal SQLite 已迁移到 schema v6。草案拒绝只要求草案仍为 pending，不再错误比较当前计划版本；批准仍严格校验 base_plan_version。截图中的 v21 旧草案已在当前 v24 下成功拒绝，重复拒绝保持幂等且计划版本未变化。==

==完整复盘已改为持久化后台任务：POST 只入队，`goal-agent-review-worker.service` 通过租约、心跳和过期重领独立执行。真实验收中原任务在服务重启后被重领，发现事实更新后自动 supersede，并由替代任务完成复盘和草案生成。==

- `plan_item` 现持久化确定性优先级及依据，并支持未同步、未确认日期任务的拒绝/七日内恢复；拒绝项从活动容量排除但保留审计记录。
- Windows 导出器修复陈旧锁永久阻塞问题；规范任务 `Behavior Context Exporter Timer` 已安装为登录启动、每 20 分钟运行和错过后补跑。旧任务因动作/配置不同按规则保留。
- 材料导出由 134 份恢复；真实复盘快照含 142 份材料和三门课 2026-09-08 最新笔记，随后定时导出继续增长到 144 份。系统立即把 2026-09-09 新出现的微分几何 `4..md` 识别为最新待分析候选；文档数量是动态指标，待确认笔记只作为数据缺口，不自动推断课程进度。
- 真实后台复盘 `review-job-ff33657159724b14bd045ca6324a0dac` 完成，报告引用 15 个事实；本周已有 1590 分钟任务并占用 600 分钟作业预留，审查器因此接受 0 个新增任务，没有为填满容量凑数。
- 生产回归：Advisor 316 tests OK（skipped=1），Garden 53 tests OK，Windows exporter 14 tests OK；Goal SQLite `quick_check=ok`、`integrity_check=ok`；Advisor、Garden、review worker 和周日 timer 均 active。
- 已把生产验证后的 Garden `server.py`、`app.js`、`style.css`、`index.html`、`goal-v3.js` 和测试镜像到 `D:\MyFocusGarden`；镜像全量 53 tests OK，旧文件备份在 `D:\MyFocusGarden\backups\goal-mode-20260909-schema-v6-mirror\`。
- 精确回滚备份：`/home/conrad/backups/goal-mode-20260908-234725/`；最终初始化锁修复的单文件备份位于 `/home/conrad/backups/goal-mode-20260909-final-init-fix/`。Pad5e 在 Tailscale 在线，但当前无线调试动态端口不可用，设备级触控验收仍待补充。
