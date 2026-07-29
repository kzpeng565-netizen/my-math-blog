<!-- ai_provenance: source=codex; date=2026-07-26; verification=server-verified -->

# 半小时行为解释系统——PROJECT_STATE

> 本文档描述系统当前实际状态。技术细节见 PI_SERVER_HANDOFF.md，设计决策见 DECISIONS.md。

## 系统是什么

一个运行在树莓派上的**半小时行为解释系统**。每半小时自动收集电脑（ActivityWatch + Syncthing）、手机和平板（Android Automate）的使用数据，清洗后交 DeepSeek V4 Flash 生成语义时间线和核验报告，通过 PushPlus 微信公众号推送给用户。当前阶段**只核验 AI 的理解能力，不做任何自动干预**。

## 当前版本：第五版（可配置事实标签 + 精简双层 AI）

三轮迭代已完成：

- **第一版**：叙事型报告。用户反馈"没有直接回答工作多久、休息多久"——被否定。
- **第二版**：指标先行，程序计算确定性数字（工作时间、休息时间等），AI 只负责语义解释。加入用户确认的休息规则（电脑 AFK ≥ 3 分钟 + 手机熄屏）。
- **第三版**：引入两层 AI 调用——第一次生成语义时间线（work/entertainment/communication/rest/other/uncertain），程序据此计算工作-娱乐混杂指标，第二次 AI 只负责解释结果并生成报告。核心创新是**工作-娱乐混杂检测**：工作中被 AI 判断为娱乐且持续 > 30 秒才算一次偏离，30 秒及以下不计。
- ==**第四版（2026-07-28 当前）**：增加只读 Obsidian 任务上下文、last-known-good 回退、上下文归档、影子干预候选和日/周统计。影子判断随原半小时 PushPlus 消息发送，但不会执行干预。全设备无活动时停止 AI 调用并跳过 PushPlus，仍完整归档。==
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

## 当前运行的组件

### 树莓派 (Raspberry Pi 3 Model B, Debian 13, 1GB RAM)

| 组件 | 状态 | 说明 |
|---|---|---|
| `phone-usage-receiver.service` | active | 标准库 `http.server` 接收服务监听 `127.0.0.1:8765`，接收手机/平板共六文件上传，并提供 `/annotation` 手机异常反馈入口 |
| `phone-usage-maintenance.timer` | active | 每日 03:30 归档压缩（>30 天）和清理（>365 天） |
| `activitywatch-advisor.timer` | active, enabled | 每半小时 08/38 分触发分析 |
| `activitywatch-advisor.service` | triggered by timer | 单次执行，完成后退出 |
| `activitywatch-advisor-daily-summary.timer` | disabled, inactive | 旧 PushPlus 日统计已停用，避免 09:00 发送旧版总数摘要 |
| `activitywatch-advisor-daily-life.timer` | active, enabled | 每天 09:00 生成前一天每日生活复盘，并通过纯文本 emoji ntfy 推送；建议层使用 DeepSeek V4 Pro |
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
9. PushPlus 微信公众号推送
10. systemd timer 自动调度
11. ==Obsidian 三文件只读导出、原子写入和源文件哈希验证==
12. ==Syncthing 独立上下文文件夹单向同步，中文文件名和 UTF-8 内容验证==
13. ==树莓派上下文 schema 校验、last-known-good 回退和实际使用快照归档==
14. ==影子候选生成并随半小时 PushPlus 消息供人工核验，正式干预保持关闭==
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

系统维护超时提醒已部署并运行。`sysadmin-time-guard.timer` 为 `enabled / active`，每 5 分钟执行一次。当前实现不依赖半小时 AI prompt，而是在确定性分类层直接判断最近 30/60 分钟系统维护占比。

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
