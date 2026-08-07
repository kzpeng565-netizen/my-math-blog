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
## 2026-07-29：Next Action Web 已上线

树莓派端已新增私有网页入口：

```text
https://pi.taild4d3f7.ts.net:8450
```

该入口由 `activitywatch-advisor-web.service` 提供，内部监听 `127.0.0.1:8767`，通过 Tailscale Serve tailnet only 暴露。公开 Funnel 仍只用于手机数据上传和 Automate annotation。

“下一步”功能已完成第一版闭环：点击网页按钮后临时生成决策状态，调用 DeepSeek V4 Pro，返回包含行动、依据和说服性解释的建议，并把状态快照、建议、响应和手动执行结果归档到 `data/next_action/`。

“半小时报告”网页查看已可用，PushPlus 微信推送保留不变。网页中提交的报告反馈复用 `data/user_annotations/`，与 Automate HTTP 反馈进入同一个 raw/daily/UNREVIEWED 体系。

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
