<!-- ai_provenance: source=codex; date=2026-07-26; verification=server-verified; retrieved_notes="D:\mathblog\quartz\content\非笔记内容\工作流程与系统运维\手机使用记录系统——树莓派端操作与维护指南.md","D:\mathblog\quartz\content\非笔记内容\工作流程与系统运维\手机使用记录系统——手机端操作与维护指南.md","C:/Users/15345/.codex/skills/manage-pi-server/references/server-layout.md" -->

# 半小时行为解释系统——接管交接文档

## 2026-08-07 更新：停用半小时微信推送

<!-- ai_provenance: source=codex; date=2026-08-07; verification=server-verified; retrieved_notes="非笔记内容/工作流程与系统运维/PI_SERVER_HANDOFF.md,非笔记内容/工作流程与系统运维/树莓派行为数据与接口索引.md" -->

==用户确认：半小时报告仍原样写入 `data/ai_reports/YYYY-MM-DD/HH-MM.{json,md}`，专注花园的只读系统状态继续读取最新报告；但 `activitywatch-advisor.service` 不再向微信 PushPlus 发送。服务专用 drop-in `disable-half-hour-pushplus.conf` 通过 `UnsetEnvironment=PUSHPLUS_TOKEN` 清除半小时服务的有效令牌；基础 unit 对可选 `pushplus.env` 的历史引用仍存在，不代表半小时推送启用。报告生成、归档、统计、影子候选和半小时 ntfy 提醒检查不受影响。==

> [!summary]
> 本文档供后续 AI Agent 接管此项目时使用。标记体系：**[已由旧对话确认]**、**[已由服务器核实]**、**[仅讨论过]**、**[当前无法确认]**。

## 1. 项目目标与总体架构

**[已由旧对话确认]**

==用户（Conrad）建立一个**个人行为反馈中枢**，在树莓派上每半小时自动收集电脑、手机和平板使用数据，经独立清洗、可配置标签和确定性时间组装后交 AI 解释，生成可供网页、Next Action 与 Focus Garden 读取的本地报告。半小时 PushPlus 已于 2026-08-07 停用；周报 PushPlus 和各类 ntfy 通知仍由独立定时器管理。==

<!-- ai_provenance: source=codex; date=2026-07-28; verification=server-verified; retrieved_notes="非笔记内容/工作流程与系统运维/PROJECT_STATE.md,非笔记内容/工作流程与系统运维/DECISIONS.md,非笔记内容/工作流程与系统运维/NEXT_STEPS.md" -->

==**[历史能力][已由用户确认][已由服务器核实] 第四版增加了只读 Obsidian 上下文、影子判断、日/周统计、当时的 PushPlus 人工核验和全设备无活动静默。第五版保留上下文、归档、影子候选与静默判断，但不再发送半小时 PushPlus。**==

==**[已由用户确认][已由服务器核实] 同日完成第五版：清洗事实先经过可配置标签层，统一向语义模型提供40分钟精简事实；程序锁定确定性段并恢复精确时间，AI只解释未锁定候选。第二次模型只接收活动总量、至少30秒的重要片段和设备Top摘要。**==

总体数据流：

```text
电脑: ActivityWatch (Windows) ---> Syncthing ---> /home/conrad/workspace/activitywatch-sync/ (树莓派)
                                                           |
手机: Automate (Android) ---> HTTPS PUT ---> Tailscale Funnel ---> phone-usage-receiver.service (127.0.0.1:8765)
                                                           |
                                                    /home/conrad/phone_usage/archive/
                                                           |
手机反馈: Automate 桌面快捷方式 ---> HTTPS POST /annotation ---> phone-usage-receiver.service
                                                           |
                                      data/user_annotations/raw + daily + UNREVIEWED
                                                           |
Obsidian: Profile/Tasks/番茄钟 ---> Windows 只读导出器 ---> Syncthing Send Only
                                                           |
                              /home/conrad/workspace/behavior-context-sync/ (Receive Only)
                                                           |
                                      obsidian_context.py (校验 + last-known-good)
                                                           |
                     +-------------------------------------+
                     |
            activitywatch-advisor.timer (每半小时 08/38 分触发)
                     |
          +----------+-----------+
          |                      |
    computer_facts.py    phone_facts.py    tablet_facts.py
          |                      |                |
    computer_facts/       phone_facts/      tablet_facts/
          |                      |                |
          +----------+-----------+----------------+
                     |
           cross_device.py (三设备融合，平板为辅助)
                     |
           combined_facts/
                     |
           fact_tagger.py + config/tag_rules.json
                     |
           tagged_facts/ (统一40分钟、可追踪tag、程序锁定边界)
                     |
           DeepSeek V4 Flash 第1次: 只组合未锁定候选单元
                     |
           semantic_analysis.py (恢复精确秒数 + 越界拆分 + 混杂指标)
                     |
           DeepSeek V4 Flash 第2次: 解释精简语义摘要
                     |
           ai_reports/ (JSON + Markdown) + intervention_candidates/
                     |
           ai_reports/ → 本地归档 + Next Action / Focus Garden 网页读取
           pushplus_client.py → 半小时发送已停用（保留历史代码与回执）
                     |
           statistics_notifier.py → PushPlus 周报周一 09:05（旧日报 timer 已停用）
           daily_life_notifier.py → ntfy 每日生活复盘 09:00（纯文本 emoji，建议层用 DeepSeek V4 Pro）
           afternoon_task_check.py → ntfy 15:00 任务进度提醒（V4 Flash 辅助判断）
```

> [!important]
> ==**[已由用户确认][已由服务器核实] 当电脑没有非 AFK 活动（含无电脑消息/数据），且手机、平板均无亮屏证据时，不调用 DeepSeek；仍归档事实、上下文和统计所需状态。原“不发送 PushPlus”分支现属于历史兼容逻辑，因为半小时 PushPlus 已整体停用。**==

## 2. 手机、电脑与树莓派之间的数据流

### 2.1 电脑端 → 树莓派

**[已由旧对话确认][已由服务器核实]**

- ActivityWatch 安装在 Windows 上，持续记录窗口标题、网页标签页、AFK 状态
- ActivityWatch 数据存储在本地 SQLite 数据库
- Syncthing (`C:\Users\15345\ActivityWatchSync`) 将 ActivityWatch 数据同步到树莓派 `/home/conrad/workspace/activitywatch-sync/`
- 数据库中只有一个 bucket: `7bc64a74-0bba-41c8-b3ab-b88258fee0a8`
- `computer_facts.py` 从该 SQLite 数据库读取原始事件，清洗为事实摘要

### 2.2 手机端 → 树莓派

**[已由旧对话确认][已由服务器核实]**

- Android 上使用 Automate 运行 `Phone Usage Logger` 流
- 每 15 分钟通过 HTTPS PUT 上传三个文件到 `https://pi.taild4d3f7.ts.net/upload/`（Tailscale Funnel）
- 三文件：`foreground.jsonl`（前台应用）、`screen.jsonl`（亮/灭屏）、`heartbeat.jsonl`（心跳）
- Funnel 代理到 `127.0.0.1:8765`（`phone-usage-receiver.service`）
- 接收端验证 token，按日期归档到 `/home/conrad/phone_usage/archive/YYYY-MM-DD/`
- 同一天多次上传会自动合并去重
- 超过 30 天压缩为 `.jsonl.gz`，超过 365 天删除

<!-- ai_provenance: source=codex; date=2026-07-28; verification=server-verified; retrieved_notes="非笔记内容/工作流程与系统运维/PROJECT_STATE.md,非笔记内容/工作流程与系统运维/DECISIONS.md,非笔记内容/工作流程与系统运维/NEXT_STEPS.md" -->

### 2.2.1 手机异常反馈 → 树莓派

**[已由用户真实提交验收][已由服务器核实]**

==Android Automate 另有一个桌面快捷方式用于记录系统异常反馈。它不上传设备状态或报告编号，只提交分类索引和可选说明：==

```text
POST https://pi.taild4d3f7.ts.net/annotation
Authorization: Bearer <现有手机上传 token>
Content-Type: application/x-www-form-urlencoded

category=0..4
message=可选说明
```

==`/annotation` 也支持 `application/json`，但手机端正式协议是表单提交。成功响应为 `201` JSON；任意 `2xx` 对手机视为成功。缺少 Authorization 返回 `401`，token 错误返回 `403`，分类或说明不合法返回 `400`，请求体超过 4 KiB 返回 `413`。==

固定分类：

| index | code | label |
|---|---|---|
| 0 | `wrong_behavior_judgment` | AI行为判断错误 |
| 1 | `data_or_device_error` | 数据缺失或设备状态错误 |
| 2 | `invalid_ai_output` | AI输出数据不符合要求 |
| 3 | `bad_recommendation` | 推荐任务或建议不合适 |
| 4 | `other` | 其他问题 |

==`category=4` 时 `message` 必须非空；其他分类允许空说明。`message` 去掉首尾空白后最多 500 个 Unicode 字符。用户输入不得参与文件路径或文件名生成。==

### 2.3 数据格式

**[已由旧对话确认]**

```json
{"timestamp":"2026-07-24T17:00:00+08:00","device":"phone","event":"foreground","package":"com.tencent.mm"}
{"timestamp":"2026-07-24T17:05:00+08:00","device":"phone","event":"screen","state":"off"}
{"timestamp":"2026-07-24T17:15:00+08:00","device":"phone","event":"heartbeat"}
```

## 3. 数据文件及其作用

**[已由旧对话确认][已由服务器核实]**

| 数据层 | 路径（树莓派） | 生成者 | 作用 |
|---|---|---|---|
| ActivityWatch 原始数据库 | `/home/conrad/workspace/activitywatch-sync/7bc64a74.../test.db` | Syncthing | 电脑活动原始 SQLite |
| 手机原始归档 | `/home/conrad/phone_usage/archive/YYYY-MM-DD/` | phone-usage-receiver | 手机 foreground/screen/heartbeat JSONL |
| 手机传入镜像 | `/home/conrad/phone_usage/incoming/` | phone-usage-receiver | 最近一次上传的原始请求体 |
| 电脑事实 | `data/computer_facts/YYYY-MM-DD/HH-MM.json` | computer_facts.py | 去重、AFK 处理后的电脑活动事实 |
| 手机事实 | `data/phone_facts/YYYY-MM-DD/HH-MM.json` | phone_facts.py | 去重、亮灭屏重建后的手机活动事实 |
| 平板事实 | `data/tablet_facts/YYYY-MM-DD/HH-MM.json` | tablet_facts.py | 去重、亮灭屏重建后的平板活动事实（辅助数据源） |
| 合并事实 | `data/combined_facts/YYYY-MM-DD/HH-MM.json` | cross_device.py | 两台设备的时间重叠统计 |
| 语义时间线 | `data/semantic_timelines/YYYY-MM-DD/HH-MM.json` | DeepSeek 第1次 | 互斥语义段（work/entertainment/communication/rest/other/uncertain） |
| 混杂指标 | `data/mixing_metrics/YYYY-MM-DD/HH-MM.json` | semantic_analysis.py | 程序确定性计算的工作-娱乐混杂 |
| AI 报告 | `data/ai_reports/YYYY-MM-DD/HH-MM.{json,md}` | DeepSeek 第2次 | 最终解释报告 |
| 用户异常反馈 raw | `data/user_annotations/raw/YYYY-MM-DD/<annotation_id>.json` | phone-usage-receiver + user_annotations.py | ==手机桌面快捷方式提交的人工调试标注，事实记录，不由 AI 自动改写== |
| 用户异常反馈当日汇总 | `data/user_annotations/daily/YYYY-MM-DD.md` | user_annotations.py | ==从 raw JSON 原子重建的当日可读视图== |
| 用户异常反馈未处理总表 | `data/user_annotations/UNREVIEWED.md` | user_annotations.py | ==从 raw JSON 原子重建，按接收时间倒序展示 `status=unreviewed`== |
| PushPlus 回执 | `data/pushplus_receipts/YYYY-MM-DD/HH-MM.json` | pushplus_client.py | 微信推送状态 |
| 处理状态 | `data/state/processing-state.json` | run_half_hour.py | 最后一次成功处理的时段 |
| 上下文 LKG 缓存 | `data/context_cache/current.json` | obsidian_context.py | 最近一份通过校验的 Obsidian 快照 |
| 实际上下文归档 | `data/context_snapshots/YYYY-MM-DD/HH-MM.json` | run_half_hour.py | 记录当时 AI 实际看到的任务、来源和年龄 |
| 影子候选 | `data/intervention_candidates/YYYY-MM-DD/HH-MM.json` | behavior_advisor.py | 记录如果正式模式启用是否会建议干预；不执行 |
| 每日统计 | `data/statistics/daily/YYYY-MM-DD.json` | behavior_statistics.py | 聚合当日报告、混杂和影子候选 |
| 每周统计 | `data/statistics/weekly/YYYY-Www.json` | behavior_statistics.py | 聚合自然周 |
| 统计推送回执 | `data/statistics/pushplus_receipts/{daily,weekly}/` | statistics_notifier.py | 去重和审计日/周统计发送 |
| 每日生活复盘 | `data/statistics/daily_life/YYYY-MM-DD.{json,md}` | daily_life_statistics.py | ==统计工作、工作分解、娱乐前三、通信、AI使用分项、AI用途前三、手机睡眠边界，并保存 DeepSeek V4 Pro 建议== |
| 每日生活复盘 ntfy 回执 | `data/statistics/ntfy_receipts/daily_life/YYYY-MM-DD.json` | daily_life_notifier.py | ==ntfy 推送去重和审计== |
| 15:00 任务进度 ntfy 回执 | `data/statistics/ntfy_receipts/afternoon_task_check/YYYY-MM-DD.json` | afternoon_task_check.py | ==记录当天任务数量、完成数、番茄进度、V4 Flash 裁决、发送结果；`--no-push` dry run 会标记 `dry_run: true`== |
| 深夜提醒状态 | `data/state/bedtime-reminder-state.json` | bedtime_reminder.py | ==`bedtime_stop` 当前状态、事件 ID、第一层发送时间、第二层次数和冷却时间== |
| 深夜提醒日志 | `data/bedtime_reminder/events.jsonl` | bedtime_reminder.py | ==ntfy 两层提醒的状态迁移、数据年龄、设备摘要和发送结果== |

## 4. 树莓派上相关目录、脚本、服务及运行状态

### 4.1 目录

**[已由服务器核实]**

| 路径 | 用途 |
|---|---|
| `/home/conrad/workspace/activitywatch-advisor/` | 行为解释系统主目录 |
| `.../src/` | Python 脚本（run_half_hour.py, computer_facts.py, phone_facts.py, tablet_facts.py, cross_device.py, deepseek_client.py, semantic_analysis.py, pushplus_client.py, common.py） |
| `.../prompts/` | half-hour-interpreter.md, semantic-segmenter.md |
| `.../config/settings.json` | 应用名映射、模型配置、阈值参数 |
| `.../config/tag_rules.json` | ==可增删、禁用、调优的事实标签与高置信度锁定规则；不要把规则硬编码进 prompt== |
| `.../src/fact_tagger.py` | ==规则校验、统一40分钟事实块、程序标签、AI候选压缩；CLI 可解释单块命中过程== |
| `.../data/` | 所有输出（见上表） |
| `.../data/tagged_facts/YYYY-MM-DD/HH-MM.json` | ==完整可审计的标签事实层；AI实际接收的是其精简候选视图== |
| `.../tests/` | test_cleaning.py、test_user_annotations.py 等 |
| `.../systemd/` | systemd unit 文件 |
| `/home/conrad/.config/activitywatch-advisor/env` | DeepSeek API 密钥（权限 600） |
| `/home/conrad/.config/activitywatch-advisor/pushplus.env` | PushPlus 用户令牌（权限 600） |
| `/home/conrad/phone_usage/` | 手机数据接收端（receiver.py, maintenance.py, token.txt） |
| `/home/conrad/workspace/behavior-context-sync/` | Obsidian 上下文 Syncthing Receive Only 目录 |
| `.../src/obsidian_context.py` | 上下文校验、精简与 last-known-good 回退 |
| `.../src/behavior_advisor.py` | 确定性影子预筛选 |
| `.../src/behavior_statistics.py` | 日/周聚合 |
| `.../src/statistics_notifier.py` | 日/周 PushPlus 通知与回执去重 |
| `.../src/user_annotations.py` | ==手机异常反馈校验、编号、报告关联、raw JSON 保存和 Markdown 重建== |
| `.../src/afternoon_task_check.py` | ==每天 15:00 检查当天 Obsidian 任务是否完成过半；可调用 DeepSeek V4 Flash 辅助判断，并通过 ntfy 提醒手机== |
| `.../config/bedtime_reminder.json` | ==深夜设备使用提醒策略配置：00:30—04:30、两层升级、25分钟冷却、120秒数据新鲜度== |
| `.../src/bedtime_reminder.py` | ==深夜 ntfy 提醒状态机、触发判断、文件锁、状态持久化和 JSONL 日志== |
| `.../src/notifications/ntfy.py` | ==可复用 ntfy 发送模块；主题从私有 env 读取，不硬编码== |
| `.../tools/test_ntfy.py` | ==复用正式 ntfy 模块的 level 1 / level 2 测试命令== |
| `.../tests/test_afternoon_task_check.py` | ==任务进度提醒解析和番茄钟兜底测试== |
| `/home/conrad/.config/activitywatch-advisor/ntfy.env` | ==ntfy 私有配置，权限 600；真实主题不得写入 Git 或 Markdown== |
| `D:\mathblog\tools\behavior-context-exporter\` | Windows 实际运行的只读导出器、配置、测试及安装/卸载脚本 |

### 4.2 服务

**[已由服务器核实]**

| 服务 | 状态 | 说明 |
|---|---|---|
| `phone-usage-receiver.service` | active | 手机/平板数据上传接收与手机异常反馈接收，监听 `127.0.0.1:8765` |
| `phone-usage-maintenance.timer` | active | 每日约 03:30 归档压缩/清理 |
| `activitywatch-advisor.timer` | active, enabled | 每半小时 08/38 分触发分析 |
| `activitywatch-advisor.service` | inactive (dead, triggered by timer) | 单次分析，完成后退出 |
| `activitywatch-advisor-web.service` | active | Next Action：`127.0.0.1:8767` → tailnet-only `:8450` |
| `focus-garden.service` | active | `app.py --port 8838` 启动，路由在 `focus_garden/server.py`；`127.0.0.1:8838` → tailnet-only `:8460` |
| `focus-garden-backup.timer` | active | 开机 1 分钟后及之后每分钟生成 SQLite 一致性快照 |
| `pi-editor.service` | active | Monaco Lite：`127.0.0.1:8766` → tailnet-only `:8443` |
| `sysadmin-time-guard.timer` | active, enabled | 每 3 分钟检查系统维护活动 |
| `activitywatch-advisor-daily-summary.timer` | disabled, inactive | 旧 PushPlus 日统计已停用，避免 09:00 发送旧版总数摘要 |
| `activitywatch-advisor-daily-life.timer` | active, enabled | ==每天 09:00、10:00、11:00 检查早晨边界；满足条件即生成前一天生活复盘，最迟 11:00 处理并通过纯文本 emoji ntfy 推送== |
| `afternoon-task-check.timer` | active, enabled | ==每天 15:00 检查当天 Obsidian 任务完成数和番茄钟是否过半；必要时通过 ntfy 高优先级提醒手机== |
| `activitywatch-advisor-weekly-summary.timer` | active, enabled | 周一 09:05 发送上一自然周统计 |
| `bedtime-reminder.timer` | active, enabled | ==深夜设备使用 ntfy 提醒调度；每分钟夜间唤醒，策略窗口 00:30—04:30== |
| `bedtime-reminder.service` | inactive/dead after success | ==oneshot 状态机；成功后 inactive 是正常状态== |
| `syncthing@conrad.service` | active | 同步 ActivityWatch 数据 |
| `tailscaled.service` | active | Tailscale VPN + Funnel |
| `cockpit.socket` | active | Web 管理 9090 |
| `filebrowser.service` | active | 文件管理 8080 |

**[已由服务器核实]** 最新一次修复后 systemd timer 触发：`2026-07-28 11:08`（已完成，service 最终为 inactive/dead 的正常 oneshot 状态）。该时段手机真实亮屏 1.2 分钟，故正常调用模型并推送；平板旧亮屏已转为 `unknown`，未再造成虚假活动。

**[已由服务器核实]** ==`phone-usage-receiver.service` 仍只监听 `127.0.0.1:8765`。Tailscale Funnel 当前仍将 `https://pi.taild4d3f7.ts.net` 代理到 `http://127.0.0.1:8765`；`/upload/` 使用原 `X-Upload-Token`，`/annotation` 使用 `Authorization: Bearer <token>`。systemd unit 的 `ReadWritePaths` 已包含 `/home/conrad/phone_usage` 和 `/home/conrad/workspace/activitywatch-advisor/data/user_annotations`。==

### 4.3 配置要点

**[已由服务器核实]**

- 模型：DeepSeek V4 Flash (`https://api.deepseek.com/chat/completions`)
- ==每日生活复盘建议层：`settings.json` 中 `report_model.name = deepseek-v4-pro`；它只解释脚本给出的候选项和明日优先任务，不重算分钟数。推送正文先展示程序计算的完整数字复盘，AI建议只能追加在后面。ntfy 正文使用纯文本 emoji 格式，不依赖 Markdown。==
- ==15:00 任务进度提醒使用 `settings.json` 中 `model.name = deepseek-v4-flash`，但强制关闭 thinking 并把 `max_tokens` 限制在 1200 以内。V4 Flash 只输出是否发送提醒的 JSON 裁决；失败时使用确定性规则兜底。==
- 计时器偏移到 `08` 和 `38` 分，为手机约 15 分钟上传留时间
- 语义切段使用非思考模式（`semantic_model.thinking = "disabled"`）
- ==语义上下文固定为40分钟：正式30分钟加前后各5分钟；不再分别发送重叠的30分钟和40分钟 JSON。==
- ==标签规则支持 `enabled`、`priority`、`add_tags`、`remove_tags`、`locked_activity` 和 `force_boundary`；规则修改后先执行 `python3 src/fact_tagger.py --rules config/tag_rules.json`。==
- ==DeepSeek每次请求保存 prompt/completion/cache token、请求次数和按 `settings.json` 价格估算的人民币成本。==
- 确认休息规则：电脑 AFK >= 3 分钟 **且** 手机熄屏；平板亮屏只降低置信度
- AI/推送静默规则：电脑无非 AFK 活动 **且** 手机、平板均无当前亮屏证据；==手机或平板屏幕事件超过 2700 秒后转为 `unknown`，不再沿用旧亮屏==
- 娱乐偏离：工作中被 AI 判为娱乐且持续 > 30 秒
- 当前已连接设备：`computer`, `phone`, `tablet`（平板为辅助数据源）
- Obsidian 上下文：schema v1，导出器 v2，树莓派只读
- `behavior_advisor.shadow_mode = true`，正式干预不得提前启用
- 全设备无活动证据阈值使用 `processing.minimum_evidence_seconds`（当前 30 秒）
- ==手机异常反馈使用 `ZoneInfo("Asia/Shanghai")` 生成接收时间；`annotation_id` 由时间戳和随机后缀组成，不依赖用户输入；目录权限 700，文件权限 600。==
- ==反馈关联算法：扫描最近 `data/ai_reports`，选取已存在、生成/修改时间不晚于 `received_at`、90 分钟内时间最近的 `.md` 报告作为 `primary_related_report`；再按该报告的日期和 `HH-MM` 文件名寻找同窗口事实层。==
- ==ntfy 私有配置位于 `/home/conrad/.config/activitywatch-advisor/ntfy.env`，权限 600；文档不得记录 topic/token。`daily_life_notifier.py` 手动运行时也会默认读取该文件。==
- ==深夜设备使用提醒详见 [[ntfy提醒系统配置]]：主通道为 ntfy，第一层 `default`，第二层 `high`，每次升级前重新检查手机/电脑活动，数据年龄超过120秒不升级。它与每日生活复盘共用 ntfy 配置，但状态机、日志和 systemd timer 完全独立。==
- ==15:00 任务进度提醒详见 [[ntfy提醒系统配置]]：只读 Obsidian 任务和番茄钟，不修改任务；`--no-push` dry run 不会阻止当天 15:00 正式检查。==
- ==DNS 当前由 NetworkManager 管理：`netplan-eth0` 忽略 DHCP DNS，固定使用 `8.8.8.8 223.5.5.5`；Tailscale `accept-dns=false`。这是 2026-07-29 修复 DeepSeek/ntfy 解析失败后的状态。Tailscale Funnel 仍保持开启。==

## 5. 已验证成功的功能

**[已由旧对话确认][已由服务器核实]**

1. 手机 Automate 流采集并上传 foreground/screen/heartbeat -- 已验证
2. 手机数据通过 Tailscale Funnel HTTPS 到达树莓派 -- 已验证
3. `phone-usage-receiver` 接收、验证、去重、合并、归档 -- 已验证
4. ActivityWatch Windows 端采集并通过 Syncthing 同步到树莓派 -- 已验证
5. `computer_facts.py` 从 SQLite 提取并清洗电脑事实 -- 已验证
6. `phone_facts.py` 从 JSONL 提取并清洗手机事实 -- 已验证
7. `tablet_facts.py` 从 JSONL 提取并清洗平板事实 -- 已验证
8. DeepSeek 语义时间线生成（第1次调用）-- 已验证
9. 程序校验语义时间线并计算混杂指标 -- 已验证
10. DeepSeek 报告生成（第2次调用）-- 已验证
11. PushPlus 微信公众号推送 -- 已验证
12. 定时器每半小时自动触发全流程 -- 已验证（2026-07-25 全天 48 个时段均已产出报告）
13. 手机心率检测与休息规则 -- 已验证
14. 工作-娱乐混杂指标（>30s 偏离判定）-- 已验证
15. Obsidian 三文件只读导出、任务解析、中文路径及原子写入 -- 已验证（Windows 5 项测试）
16. Behavior Context Syncthing Send Only → Receive Only、中文文件名和 SHA-256 -- 已验证
17. 上下文 schema 校验、冲突文件忽略、last-known-good 回退和完全不可用降级 -- 已验证
18. 影子候选生成、归档并合并进半小时 PushPlus 消息 -- 已验证
19. 每日/每周统计定时生成、PushPlus 实际发送及回执去重 -- 已验证
20. DeepSeek 非法 JSON 降级为本地低置信度报告，不中断主流程 -- 已验证
21. 全设备无活动时 `model: null`、PushPlus `all_devices_inactive`、仍完整归档 -- 已验证
22. ==过期手机/平板亮屏状态不再跨时段外推，且同一个前置静默判断同时跳过 DeepSeek 和 PushPlus -- 已用 2026-07-28 04:00—04:30 历史窗口隔离回放验证。==
23. ==手机异常反馈接入 -- 已验证。localhost 集成测试覆盖表单、JSON、中文 message、空说明、`category=4` 空说明、非法分类、超长 message、缺失/错误 token、报告不存在仍保存、Markdown 从 raw 重建和同秒不同 ID。==
24. ==手机真实提交 -- 已验证。2026-07-28 19:40:45 与 19:40:58 两条真实反馈均返回 `201`，保存到 `data/user_annotations/raw/2026-07-28/`，并重建当日 Markdown 与 `UNREVIEWED.md`。==
25. ==第五版标签事实层 -- 已验证。`config/tag_rules.json` 当前10条启用规则，规则 SHA-256 可追踪；统一40分钟事实层、候选单元压缩、程序锁定边界和越界分组拆分均有测试覆盖。主项目现有49项测试通过。==
26. ==第五版真实调用 -- 已验证。19:00和20:00隔离回放均覆盖1800秒；正式21:30—22:00窗口由22:08 timer成功运行并推送，无缓存时两次调用合计估算约0.0137元。==
27. ==深夜设备使用 ntfy 提醒 -- 已验证。`bedtime_stop` 两层状态机、私有 `ntfy.env`、systemd timer、level 1/2 ntfy 测试和 61 项主项目测试均已通过；2026-07-29 00:33 真实夜间调度已发送第一层。详见 [[ntfy提醒系统配置]]。==

**[已由服务器核实]** 2026-07-25 的数据：`ai_reports/` 下有 48 个 JSON+MD 文件（00:00 至 23:30），所有时段均有产出。

## 6. 出现过的问题和处理过程

**[已由旧对话确认]**

| 问题 | 处理 |
|---|---|
| Windows 上传脚本弹出 PowerShell 窗口 | 改为 Syncthing 文件同步，不再需要本地上传脚本 |
| 浏览器网页覆盖率显示 36.3% | 实际是 web watcher 与窗口事件的重叠计算方式问题；改为窗口标题与 observed_pages 匹配，域名关联率达 100% |
| 第一版报告为叙事型，用户反馈没有直接回答"工作多久、休息多久" | 第二版改为指标先行，程序确定性数字覆盖 AI |
| AI 把 AFK 期间使用微信误判为休息 | 用户明确休息规则：电脑 AFK >= 3 分钟 + 手机熄屏 ✅ |
| 手机上传晚于定时器触发 | 定时器推迟到 08/38 分 |
| AI 多次输出固定免责声明 | 第二版简化 Prompt，只保留会改变结论的 1-2 条不确定性 |
| 碎片化指标（切换次数）不合适 | 用户明确需求是"工作-娱乐混杂"而非"切换次数"；第三版改为基于语义时间线的偏离检测 |
| 番茄钟 `end-begin` 明显超过 40 分钟 | 用户说明来自中途暂停后继续；工作量只按 `duration`，墙钟跨度不视为坏数据或低效 |
| DeepSeek 返回非法 JSON 导致 systemd service failed | 捕获 AI 请求/解析异常，保留事实并生成本地低置信度报告，随后实际重跑成功 |
| 午夜收到大量无活动消息 | 改为全设备状态静默：无电脑非 AFK 活动且手机/平板无亮屏时，停止 AI 和 PushPlus但继续归档 |
| 2026-07-28 凌晨 02:00—08:00 仍每半小时推送 | 根因是平板 2026-07-27 00:41:44 的最后一条 `screen=on` 在无心跳时被无限外推，每个时段误算为平板亮屏 30 分钟。现以 `heartbeat_stale_seconds=2700` 限制屏幕状态寿命，过期后记为 `unknown`；静默判断移到 AI 分支之前并复用于 PushPlus。 |
| 日报/周报在午夜发送 | 调整为日报 09:00、周报周一 09:05 |
| 手机反馈首次真实测试返回 401 | 2026-07-28 19:38 两次请求到达 `/annotation`，但缺少合法 Bearer 鉴权头；确认 Automate 请求头应为 `Authorization: Bearer <token>`，修正后 19:40 两次真实提交均返回 201 并落盘。 |
| DeepSeek 成本约1.3元/日且时间段偶有吞并 | 增加可配置标签事实层，统一为40分钟精简输入；程序锁定通信/休息等边界并吸收1—3秒采样缝隙，AI只返回候选单元语义，程序恢复精确秒数并拆开越界分组；第二次调用只解释摘要。 |

## 7. 当前接管状态

==**[已由服务器核实] 系统状态为 `running`，三个 advisor timer 均 active。手机异常反馈接入已提交为 `6462485 feat: add phone annotation intake and review logs`。静默修复与第五版标签/成本改造已经部署但尚未提交；当前工作区包含9个修改文件和2个新增文件，必须以树莓派项目中的 `git status --short` 为准，不得误称工作区干净。部署前备份位于 `/home/conrad/workspace/backups/activitywatch-advisor-pre-tag-20260728-211923/`。**==

## 8. 尚未完成或尚未验证的事项

**[已由服务器核实]** 当前尚未完成：

- Windows Task Scheduler 尚需用户以管理员 PowerShell 运行一次安装脚本
- 影子模式尚未完成 3—7 天人工观察，不得启用正式提醒
- 第五版虽已通过历史回放和一次正式 timer，但整体准确率仍需用 `/annotation` 连续观察 3—7 天；当前只能确认时间边界和已知行为识别更稳定
- 120 分钟历史、正式 60 分钟冷却和有限提醒尚未实现
- 微信核验回复自动回写尚未实现
- ==手机异常反馈已有入口和 raw/Markdown 记录，但尚未实现人工处理界面、`status` 更新流程或基于反馈的 prompt/config 候选修改流程。==

**[仅讨论过]**：

- 替代信息流平台（树莓派信息过滤）-- 仅讨论
- 自动管控（Cold Turkey / 不做手机控联动）-- Cold Turkey 电脑端已于 2026-07-31 部分落地；不做手机控联动仍仅讨论
- AI 维护提示词和 Skills -- 仅讨论

**[当前无法确认]** 的事项：

- 手机端 Automate 流是否仍然正常运行（需查看今天上新数据确认）
- DeepSeek API 密钥是否需要轮换（架构文档建议在部署后轮换）
- 正式提醒启用前的影子误报率是否足够低

## 9. 下一步最合理的操作顺序

**[建议顺序]**

1. ==**安装 Windows 定时导出任务**：管理员 PowerShell 运行 `D:\mathblog\tools\behavior-context-exporter\scripts\install_exporter_task.ps1`。==
2. ==**观察第五版准确率与费用 3—7 天**：核对数学学习、知乎、通信、确认休息和真实不确定段；用 `/annotation` 统计每100份报告的行为误判数。==
3. ==**维护标签规则**：只编辑 `config/tag_rules.json`，先执行规则校验，再隔离回放已知窗口；一次只改一类规则。==
4. ==**检查日/周统计**：日报 09:00、周报周一 09:05；核对报告数与分钟数。==
5. **数据增长监控**：运行一周后计算真实日增长量。
6. **API 密钥轮换**：在 DeepSeek 控制台生成新密钥并更新私有环境文件。
7. **完整版验收**：确认无活动时仍停止 AI、继续归档；确认通用 AI 干预的冷却期、单动作和数据不足不提醒。==另行观察 [[ntfy提醒系统配置]] 中的深夜提醒完整夜间链路，尤其是 04:30 重置。==
8. **信息过滤平台**：在行为数据可靠后再建设替代信息供给系统。

## 10. 后续 Agent 接管时的注意事项

**[必须遵守]**

1. **SSH 连接**：使用 `ssh -o BatchMode=yes pi.local`；密钥在 `C:\Users\15345\.ssh\pi_server_ed25519`
2. **不要暴露密钥**：DeepSeek API 密钥在 `/home/conrad/.config/activitywatch-advisor/env`（600 权限）；PushPlus token 在 `.../pushplus.env`；上传 token 在 `/home/conrad/phone_usage/token.txt`
3. **服务只监听 localhost**：`phone-usage-receiver` 只在 `127.0.0.1:8765`，通过 Tailscale Funnel 对外暴露
4. **定时器是 enabled**：修改后需要 `systemctl daemon-reload`
5. **配置文件的位置**：`settings.json` 和 `tag_rules.json` 在 `activitywatch-advisor/config/`；不要与 `.config/activitywatch-advisor/env` 混淆
6. **输出数据结构**：computer_facts、phone_facts、tablet_facts 和 tagged_facts 均为可复用层，全天分析时可直接读取而不重新处理原始事件
7. **手机数据可能有延迟**：约 15 分钟上传一次，timer 在 08/38 分运行就是为了等待最近一轮上传
8. **休息规则是用户确认的**：不要修改 AFK >= 3 分钟 + 手机熄屏的判断逻辑
9. **推送是单向的**：微信公众号回复不会写回系统；==手机桌面快捷 `/annotation` 是当前人工反馈入口==
10. **不要修改 `server-layout.md` 未经过验证的部分**
11. **Obsidian vault 路径**：`D:\mathblog\quartz\content`，项目文档应放在 `非笔记内容/工作流程与系统运维/`
12. **此文件是交接文档**：后续 Agent 接手时应先阅读此文件，再阅读 `server-layout.md` 和 `半小时行为解释系统——架构与维护.md`
13. ==**Obsidian 是唯一任务权威源**：不得从树莓派修改任务、日期、完成状态或番茄钟进度。==
14. ==**番茄钟只作弱参考**：使用声明 `duration`；无记录不是无学习，长墙钟跨度可来自暂停。==
15. ==**全设备无活动必须静默**：不调用 DeepSeek、不发 PushPlus，但所有本地归档必须继续。==
16. ==**通用 AI 正式干预未启用**：`shadow_mode` 必须保持 `true`，除非用户在观察 3—7 天后明确授权。深夜停止设备使用是独立的确定性 ntfy 策略，已上线；不要把两者混为一谈。==
17. ==**ntfy 主题保密**：真实 `NTFY_TOPIC` 只存在于 `/home/conrad/.config/activitywatch-advisor/ntfy.env`；交接、README 和 Git 示例只写占位符。==
18. ==**AI 报告有存档**：`data/ai_reports/` 同时保留 JSON 和 Markdown，不要只依赖微信消息。==
19. ==**不要恢复旧的移动设备状态外推**：手机或平板超过 `heartbeat_stale_seconds` 的最后屏幕事件必须视为 `unknown`；`unknown` 不等于亮屏，也不应阻止无活动静默。==
20. ==**AI 和通知必须共用前置静默结果**：不得在调用 DeepSeek 后才单独判断是否推送。==
21. ==**不要把反馈当作自动修复指令**：`data/user_annotations/raw/` 是人工调试标注，AI 不得自动修改 raw JSON，不得在接收请求时调用 DeepSeek，也不得直接改任务或配置。==

## 11. Obsidian 上下文与通知子系统操作手册

### 11.1 Windows 导出

**[已由本机核实]**

```powershell
cd D:\mathblog\tools\behavior-context-exporter
python .\behavior_context_exporter.py
python -m unittest discover -s .\tests -v
```

输出目录：

```text
C:\Users\15345\BehaviorContextSync
├── context_snapshot.json
├── sync_heartbeat.json
├── raw\
└── logs\
```

==导出器只读源笔记；源文件内容哈希已验证与快照一致。源文件未变化且导出器版本未变化时，只更新心跳。错误不得覆盖上一份正确快照。==

安装/卸载 Windows 定时任务：

```powershell
& 'D:\mathblog\tools\behavior-context-exporter\scripts\install_exporter_task.ps1'
& 'D:\mathblog\tools\behavior-context-exporter\scripts\remove_exporter_task.ps1'
```

安装时若出现 Access Denied，必须以管理员身份运行。日常任务使用 `pythonw.exe`，每 20 分钟执行并禁止并发。

### 11.2 Syncthing

**[已由服务器核实]**

- 文件夹 ID：`behavior-context`
- Windows：`C:\Users\15345\BehaviorContextSync`，Send Only
- 树莓派：`/home/conrad/workspace/behavior-context-sync`，Receive Only
- 忽略：`logs`、`exporter.lock`、`*.tmp`
- 不得混入 `activitywatch-sync`

### 11.3 树莓派检查命令

```bash
cd /home/conrad/workspace/activitywatch-advisor
git status --short --branch
python3 -m unittest discover -s tests -v
systemctl is-system-running
systemctl list-timers \
  activitywatch-advisor.timer \
  activitywatch-advisor-daily-summary.timer \
  activitywatch-advisor-weekly-summary.timer \
  --no-pager
journalctl -u activitywatch-advisor.service -n 100 --no-pager
```

检查本次静默修复：

```bash
cd /home/conrad/workspace/activitywatch-advisor
git diff -- src/phone_facts.py src/run_half_hour.py src/tablet_facts.py tests/test_cleaning.py
python3 -m unittest discover -s tests -v
journalctl -u activitywatch-advisor.service --since today --no-pager \
  | grep '"push_suppressed_for_inactivity": true'
```

==修复前文件备份位于 `/home/conrad/workspace/backups/activitywatch-advisor/2026-07-28-stale-tablet-ai-short-circuit/`。隔离回放目录位于 `/tmp/activitywatch-advisor-regression-20260728/`，不属于正式归档。==

查看最近归档：

```bash
find data/ai_reports -type f | sort | tail
find data/context_snapshots -type f | sort | tail
find data/intervention_candidates -type f | sort | tail
find data/pushplus_receipts -type f | sort | tail
find data/statistics/pushplus_receipts -type f | sort | tail
find data/user_annotations/raw -type f | sort | tail
tail -80 data/user_annotations/UNREVIEWED.md
```

检查手机异常反馈：

```bash
cd /home/conrad/workspace/activitywatch-advisor
systemctl is-active phone-usage-receiver.service
ss -lntp | grep ':8765 '
tailscale funnel status
journalctl -u phone-usage-receiver.service --since "1 hour ago" --no-pager \
  | grep '/annotation'
find data/user_annotations -maxdepth 3 -type f | sort
```

### 11.4 systemd 安装或恢复

```bash
cd /home/conrad/workspace/activitywatch-advisor
sudo install -m 0644 systemd/activitywatch-advisor-daily-summary.service /etc/systemd/system/
sudo install -m 0644 systemd/activitywatch-advisor-daily-summary.timer /etc/systemd/system/
sudo install -m 0644 systemd/activitywatch-advisor-weekly-summary.service /etc/systemd/system/
sudo install -m 0644 systemd/activitywatch-advisor-weekly-summary.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now \
  activitywatch-advisor.timer \
  activitywatch-advisor-daily-summary.timer \
  activitywatch-advisor-weekly-summary.timer
```

### 11.5 卸载新增上下文层

1. 暂停或移除 Syncthing `behavior-context` 文件夹；
2. 禁用并移除 daily/weekly summary timer 和 service；
3. 在 Git 中恢复本功能提交涉及的代码；
4. 可选删除 `data/context_cache`、`data/context_snapshots`、`data/intervention_candidates` 和 `data/statistics`；
5. ==不得删除或修改 Obsidian 三份源笔记。==

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
## 2026-07-29 接管补充：提醒系统

### 系统维护超时提醒

==`sysadmin-time-guard.timer` 已启用，现场 `OnCalendar=*-*-* *:00/3:00`，每 3 分钟运行 `src/sysadmin_time_guard.py`。==该系统直接读取最近 60 分钟 ActivityWatch 电脑前台时间线，不依赖半小时 AI prompt。此次修正位于确定性分类层：

- `ChatGPT.exe` / `Codex.exe` 可作为上下文桥接应用。
- 只有当它们与明确系统维护片段间隔不超过 300 秒时，才继承为系统维护。
- 数学/作业/定理/证明/`math`/`homework` 等排除词优先，不继承。
- 浏览器不是通用桥接应用；浏览器页面必须自己命中 Pi/systemd/ntfy 等维护证据才算维护。

关键文件：

```text
/home/conrad/workspace/activitywatch-advisor/config/sysadmin_time_guard.json
/home/conrad/workspace/activitywatch-advisor/src/sysadmin_time_guard.py
/home/conrad/workspace/activitywatch-advisor/tests/test_sysadmin_time_guard.py
/home/conrad/workspace/activitywatch-advisor/data/state/sysadmin-time-guard-state.json
/home/conrad/workspace/activitywatch-advisor/data/sysadmin_time_guard/events.jsonl
```

2026-07-29 10:30 CST 自动运行已发送一次高优先级提醒，并进入 `COOLDOWN`。状态重置条件仍是连续 1 小时没有系统维护证据。

### 半小时提醒检测系统

正式名称为“半小时提醒检测系统”。它接在半小时 AI 主流程后，只在 `intervention_candidates` 中 `would_intervene=true` 时向独立 ntfy 半小时订阅发送提醒；不会执行干预，不会修改 Obsidian 任务。

回执路径：

```text
data/ntfy_receipts/half_hour_reminder_check/YYYY-MM-DD/HH-MM.json
```

私有 ntfy env：

```text
/home/conrad/.config/activitywatch-advisor/ntfy-halfhour.env
```

真实 topic 不得写入 Git、README 或交接文档。
## 2026-07-29：Next Action Web 交接补充

私有网页入口：

```text
https://pi.taild4d3f7.ts.net:8450
```

该入口为 Tailscale Serve tailnet only，代理到：

```text
http://127.0.0.1:8767
```

相关服务和文件：

```text
activitywatch-advisor-web.service
/home/conrad/workspace/activitywatch-advisor/src/web_app.py
/home/conrad/workspace/activitywatch-advisor/src/next_action.py
/home/conrad/workspace/activitywatch-advisor/systemd/activitywatch-advisor-web.service
/home/conrad/workspace/activitywatch-advisor/docs/next-action-web-architecture.md
```

数据归档：

```text
data/next_action/state_snapshots/
data/next_action/suggestions/
data/next_action/responses/
data/next_action/outcomes/
data/next_action/active.json
```

半小时报告网页反馈复用：

```text
data/user_annotations/raw/
data/user_annotations/daily/
data/user_annotations/UNREVIEWED.md
```

常用检查：

```bash
cd /home/conrad/workspace/activitywatch-advisor
python3 -m unittest discover -s tests
systemctl status activitywatch-advisor-web.service --no-pager
journalctl -u activitywatch-advisor-web.service --no-pager -n 80
curl -fsS http://127.0.0.1:8767/api/half-hour/reports
tailscale serve status
```

注意：下一步行动助手只在用户主动点击时调用 V4 Pro。它不是自动执行观察系统，也不会自动修改 Obsidian 任务、prompt、配置或反馈 raw JSON。
## 2026-07-29：Next Action v1.1 交接补充

当前版本：

```text
next-action-v1.1
```

关键变化：

- `src/next_action.py` 增加 `routine_context=lunch_rest`。
- 12:00-13:00 默认禁止 `task` 类型建议，回退到吃饭/离屏休息。
- `hard_rules.pomodoro_role` 明确番茄钟数量只是预估预算/进度标记，不是完成保证。
- `hard_rules.pomodoro_minutes = 40`；本系统 `1 🍅 = 40 分钟`，不是 25 分钟。若模型把 15/25/30 分钟启动片段说成一个番茄钟，`_validate_suggestion()` 会拒绝该输出。
- 模型 system message 增加 v1.1 addendum：温和、具体、适度亲近；说服启动最小动作，避免鸡汤和训诫。

部署后需重启：

```bash
sudo systemctl restart activitywatch-advisor-web.service
```
## 2026-07-30 接管补充：Next Action 问题反馈入口

Next Action Web 已新增问题反馈入口，用于记录用户发现的系统问题，便于后续 Codex 统一处理。

### 入口与认证

==本节记录 2026-07-30 上线时的历史入口；原公网 `:10000` Funnel 已于 2026-08-04 撤除。当前 Next Action 仅通过 Tailnet Serve `https://pi.taild4d3f7.ts.net:8450`，或通过 Focus Garden 的 tailnet-only `:8460` 代理访问。==

```text
https://pi.taild4d3f7.ts.net:8450
```

服务仍只监听本机：

```text
127.0.0.1:8767
```

==当前 Next Action 网页密码认证已关闭，安全边界是 Tailnet 和 loopback 代理。以下私有环境路径仅作为历史配置位置保留，不表示当前请求需要登录：==

```text
/home/conrad/.config/activitywatch-advisor/web.env
```

不要把密码、cookie secret 或其它私有 token 写入文档、仓库或对话输出。

### 新增代码与数据路径

```text
/home/conrad/workspace/activitywatch-advisor/src/issue_feedback.py
/home/conrad/workspace/activitywatch-advisor/tests/test_issue_feedback.py
/home/conrad/workspace/activitywatch-advisor/data/issue_feedback/
```

数据结构：

```text
data/issue_feedback/raw/YYYY-MM-DD/<issue_id>.json
data/issue_feedback/daily/YYYY-MM-DD.md
data/issue_feedback/UNREVIEWED.md
```

`raw` 是事实源；daily 和 `UNREVIEWED.md` 由程序从 raw 重建。

### 新增 API

```text
POST /api/issue-feedback
GET  /api/issue-feedback/recent
```

==两者当前在 `:8450` Tailnet 或 Focus Garden 受限代理内使用，不再要求网页密码登录；不得据此恢复公网 Funnel。==

提交字段：

```text
category
severity
message
page
suggestion_id
report_path
```

分类包括：AI 建议质量、数据错误或缺失、网页界面、通知、规则不匹配、安全或访问、文档或交接、其它。

### 验证命令

```bash
cd /home/conrad/workspace/activitywatch-advisor
python3 -m unittest tests.test_issue_feedback
python3 -m unittest discover -s tests
systemctl status activitywatch-advisor-web.service --no-pager
```

2026-07-30 部署后验证结果：主测试 87 项 OK；网页服务重启后 active；未登录访问 `/api/issue-feedback/recent` 返回 401。

## 2026-07-30 交接补充：Next Action v1.2

当前版本：

```text
next-action-v1.2
```

==生成新建议时，`src/web_app.py` 先调用 `pending_active_suggestion()`。如果 `active.json` 对应建议没有 outcome，且最近 response 不是 `alternative_requested` 或 `declined`，接口返回：==

```json
{
  "code": "pending_outcome_required",
  "suggestion": {}
}
```

状态码为 409。网页会显示旧建议并暂存本次生成意图；用户点击“完成了/正在做/没开始”后，前端自动重新请求新建议。“换一个”和“现在不做”已构成关闭响应，不受此拦截。

==`build_decision_state()` 还会写入 `request_context.user_is_awake_for_decision_purposes=true`。用户主动点击生成按钮必须被视为已醒的直接证据；prompt 和 `_reject_awake_clarification()` 均禁止询问是否起床或醒来。==

部署验证：

```text
Next Action tests: 9 OK
All tests: 90 OK
Web JavaScript blocks: 2 validated
activitywatch-advisor-web.service: active
127.0.0.1:8767: listening
Unauthenticated API: 401
Pending outcome API: 409 pending_outcome_required
```

原文件备份位于：

```text
/home/conrad/workspace/backups/activitywatch-advisor-20260730-next-action-v12/
```

<!-- ai_provenance: source=codex; date=2026-07-30; verification=checked; retrieved_notes="非笔记内容/工作流程与系统运维/PI_SERVER_HANDOFF.md" -->

## 2026-07-31 交接补充：电脑端 Cold Turkey 介入

==半小时行为解释器在影子候选 `would_intervene=true` 且未使用 `--no-push` 时，会额外生成电脑端介入请求。请求、回执和 agent 状态分别归档在：==

```text
data/computer_interventions/requests/YYYY-MM-DD/<request_id>.json
data/computer_interventions/responses/YYYY-MM-DD/*.json
data/computer_interventions/state/windows-main.json
```

==Next Action Web 服务新增给 Windows agent 使用的登录后 API：==

```text
GET  /api/computer-interventions/pending?computer_id=windows-main
POST /api/computer-interventions/ack
POST /api/computer-interventions/response
```

==Windows 端 agent 位于 `D:\tools\computer-intervention-agent\`，只允许执行本地 allowlist 中的 Cold Turkey block：`常刷网站` 与 `bilibili`。默认命令路径为 `D:\Cold Turkey\Cold Turkey Blocker.exe`，普通介入执行可暂停的 `-start <block>` lease，由 agent 按绝对到期时间执行 `-stop <block>`，不使用 `-lock 30`。拒绝两次后第三次强制介入；封锁成功、agent 判断目标已处于本地估计封锁状态、或系统观察到恢复，都会重置拒绝计数。B 站 block 在周六全天、周日全天、周一 00:00-12:00 Asia/Shanghai 例外。==

<!-- ai_provenance: source=codex; date=2026-07-31; verification=checked; retrieved_notes="非笔记内容/工作流程与系统运维/PI_SERVER_HANDOFF.md" -->

## Windows No-Console Agent Launch (2026-08-04)

`ComputerInterventionAgent` is an interactive Scheduled Task because the agent must
show Tk dialogs in the logged-in desktop session. Its action is now:

```text
D:\anaconda\pythonw.exe "D:\tools\computer-intervention-agent\launch_agent.pyw"
```

The `Cold Turkey *.lnk` desktop status shortcut similarly targets
`D:\anaconda\pythonw.exe` with `launch_status_ui.pyw`; neither entry point uses
PowerShell or `python.exe`. Both launchers redirect diagnostics to the local
`data\agent.log` and `data\status_ui.log` files. Reinstall with
`install-agent-scheduled-task.ps1` and `install-status-shortcut.ps1` after moving
the tool directory. The status UI recognizes `pythonw.exe` / `launch_agent.pyw`.

## 2026-08-03 交接补充：我的专注花园 Pi 服务

==正式应用目录为 `/home/conrad/services/focus-garden`，服务为 `focus-garden.service`，只监听 `127.0.0.1:8838`。私人入口为 `https://pi.taild4d3f7.ts.net:8460/`，`tailscale serve status` 必须显示 `tailnet only`；不要为它启用 Funnel。==

==本地完整接管清单见 [[我的专注花园/05-Pi迁移验收与恢复清单]]。==

==权威数据库为 `/home/conrad/services/focus-garden/data/focus-garden.sqlite3`。`focus-garden-backup.timer` 每分钟运行一次一致性快照，目标为 `/home/conrad/workspace/focus-garden-archive/focus-garden.sqlite3`；该 Syncthing 文件夹在 Pi 为 send-only，在 Windows 为 receive-only。==

常用检查：

```bash
systemctl status focus-garden.service focus-garden-backup.timer --no-pager
journalctl -u focus-garden.service --no-pager -n 100
curl -fsS http://127.0.0.1:8838/api/health
tailscale serve status
syncthing cli config folders focus-garden-archive dump-json
```

==Pi 服务设置 `FOCUS_GARDEN_PI_LOCAL=1` 和 `FOCUS_GARDEN_DRY_RUN=1`：奖励扫描直接读取本机 activitywatch-advisor JSON；网页专注只计时，不调用 Windows Cold Turkey。受版权保护的 PNG 留在私有应用目录，不在存档同步目录。==

<!-- ai_provenance: source=codex; date=2026-08-03; verification=checked; retrieved_notes="非笔记内容/工作流程与系统运维/我的专注花园/00-交接总览.md,非笔记内容/工作流程与系统运维/我的专注花园/04-运维与扩展手册.md" -->

## 2026-08-03 常规交接补充：我的专注花园

==本段是迁移前现场记录，已被同日“我的专注花园 Pi 服务”交接取代。当前 Pi 已有专属服务、数据库、备份定时器和 tailnet-only Serve。==

==完整数据条件和调用过程见 [[我的专注花园/01-数据来源与处理]]；Pi 启停、备份、验证和排障见 [[我的专注花园/04-运维与扩展手册]]。专注花园只允许既有的 tailnet-only 8460 Serve，不得启用 Funnel 或公网端口。==

==当前 Pi 服务健康，35 种可种植对象已加载，7 项测试通过。若访问失败，先验证 Tailscale 与服务状态；不要把 Linux 密码或 token 写进游戏配置。==

<!-- ai_provenance: source=codex; date=2026-08-03; verification=checked; retrieved_notes="非笔记内容/工作流程与系统运维/我的专注花园/00-交接总览.md,非笔记内容/工作流程与系统运维/我的专注花园/04-运维与扩展手册.md" -->

## 2026-08-02 接管补充：我的专注花园

==本地项目位于 `D:\MyFocusGarden`，正式启动文件为 `launch.pyw`，安全测试入口为 `run-safe-test.ps1`，桌面快捷方式为“我的专注花园”。本地 HTTP 仅监听 `127.0.0.1:8838`，SQLite 存档在 `data/focus-garden.sqlite3`。==

树莓派侧没有新增文件、端口或服务。游戏使用 SSH 只读以下目录：

```text
data/computer_interventions/responses/
data/next_action/responses/
data/next_action/outcomes/
data/statistics/daily_life/
```

==同步失败时先在 Windows 运行 `ssh -o BatchMode=yes pi.local` 检查密钥和 mDNS；不要在游戏配置中保存 Linux 密码、Next Action Web 密码或任何 token。Cold Turkey 仍复用 `D:\tools\computer-intervention-agent\config.json` 的 executable 和 allowlist。==

本地验证：

```powershell
cd D:\MyFocusGarden
python -m unittest discover -s tests -v
node --check static\app.js
python app.py --dry-run
```

<!-- ai_provenance: source=codex; date=2026-08-02; verification=checked; retrieved_notes="非笔记内容/工作流程与系统运维/PI_SERVER_HANDOFF.md" -->

## 2026-07-31 常规交接：本地 Cold Turkey 自动开启模块

### 当前状态

==模块已完成第一版部署。Pi 端生成请求并保存回执；Windows 本地 agent 负责弹窗和 Cold Turkey 执行。2026-07-31 13:38 CST 已实测真实请求处理成功，`常刷网站` 与 `bilibili` 均收到 Cold Turkey `-start <block> -lock 30` 命令并返回 success。==

==当前 agent 以普通后台进程运行，不是 Windows 服务或计划任务。检查命令：==

```powershell
Get-CimInstance Win32_Process |
  Where-Object { $_.Name -in @('python.exe','python3.exe') -and $_.CommandLine -like '*computer-intervention-agent*' } |
  Select-Object ProcessId,CreationDate,CommandLine
```

正常应看到类似：

```text
D:\anaconda\python.exe D:\tools\computer-intervention-agent\agent.py
```

### Windows 本地文件

```text
D:\tools\computer-intervention-agent\agent.py
D:\tools\computer-intervention-agent\status_ui.py
D:\tools\computer-intervention-agent\config.json
D:\tools\computer-intervention-agent\run-agent.ps1
D:\tools\computer-intervention-agent\run-status-ui.ps1
D:\tools\computer-intervention-agent\state.json
```

==`config.json` 包含本地登录配置，不要把其中密码复制到文档或对话中。文档只记录路径和字段语义。==

启动命令：

```powershell
Start-Process -FilePath 'D:\anaconda\python.exe' `
  -ArgumentList 'D:\tools\computer-intervention-agent\agent.py' `
  -WorkingDirectory 'D:\tools\computer-intervention-agent' `
  -WindowStyle Hidden
```

桌面状态入口：

```text
C:\Users\15345\Desktop\Cold Turkey 自动开启状态.lnk
```

==双击会打开 `status_ui.py`，用于查看后台 agent 是否运行、Pi API 是否正常、上一次 request/执行结果、当前 agent 估计封锁状态，并可点击“启动 agent”。这个状态 UI 不执行 Cold Turkey，只展示状态和启动后台 agent。==

### Pi 端数据和 API

请求、回执、状态：

```text
/home/conrad/workspace/activitywatch-advisor/data/computer_interventions/requests/YYYY-MM-DD/<request_id>.json
/home/conrad/workspace/activitywatch-advisor/data/computer_interventions/responses/YYYY-MM-DD/*.json
/home/conrad/workspace/activitywatch-advisor/data/computer_interventions/state/windows-main.json
```

登录后 API：

```text
GET  /api/computer-interventions/pending?computer_id=windows-main
POST /api/computer-interventions/ack
POST /api/computer-interventions/response
```

本地验证：

```bash
cd /home/conrad/workspace/activitywatch-advisor
python3 -m unittest tests.test_computer_intervention -v
python3 -m unittest discover -s tests -v
systemctl status activitywatch-advisor-web.service --no-pager
```

2026-07-31 验证结果：新增测试 3 项 OK；全量测试 93 项 OK；`activitywatch-advisor-web.service` active；未登录访问新 API 返回 401。

### 弹窗 UI

==弹窗已改为高 DPI aware 的模块化简约设计：顶部判断卡、三张观察值卡、触发原因、将处理的模块、固定底部按钮和倒计时。主体可滚动，底部操作始终可见。`ignored` 文案为“未响应将按暂不介入处理，但不累计拒绝”。==

测试 UI 时不要触发 Cold Turkey，可用临时 Python import 调用 `ask_user()`，但注意用 Unicode escape 构造中文测试数据，避免 PowerShell 管道编码污染。

### 常见排障

- ==没有弹窗：先查本机是否有 `agent.py` 进程；再查 `config.json` 是否有登录密码或是否设置 `NEXT_ACTION_WEB_PASSWORD`。==
- ==Pi 有 request 但无 response：说明 agent 没拉到请求、登录失败、或进程已退出。看 `data/computer_interventions/requests/` 与 `responses/` 对比。==
- ==Pi 上 `last_seen_at` 不新：当前没有独立心跳，只有 ack/final 才更新；不能单靠它判断离线。==
- ==中文显示成问号：检查 `agent.py` 是否使用 UTF-8 保存；目标显示名优先走 `display_name` 与 allowlist。==
- ==不应直接改 Cold Turkey 内部 SQLite。第一版只走官方命令行 `-start <block> -lock <minutes>`。==

<!-- ai_provenance: source=codex; date=2026-07-31; verification=checked; retrieved_notes="非笔记内容/工作流程与系统运维/PI_SERVER_HANDOFF.md" -->

## 2026-08-04 已部署：专注花园 Next Action 菜单

==本地 `D:\MyFocusGarden` 的 UI 与固定 loopback 代理已部署到 Pi，并完成 8 项 Python 测试和服务重启。未新增端口、Serve/Funnel 路由或环境密钥：花园仍只监听 `127.0.0.1:8838`，内部仅访问既有 `127.0.0.1:8767`。待按 `我的专注花园/04-运维与扩展手册` 用真实登录完成手动验收。==

<!-- ai_provenance: source=codex; date=2026-08-04; verification=checked; retrieved_notes="非笔记内容/工作流程与系统运维/PI_SERVER_HANDOFF.md,非笔记内容/工作流程与系统运维/我的专注花园/04-运维与扩展手册.md" -->

## 2026-08-04：Next Action 免密码访问

==`/home/conrad/.config/activitywatch-advisor/web.env` 中的 `NEXT_ACTION_WEB_PASSWORD` 已在私有备份后移除，并重启 `activitywatch-advisor-web.service`。不要在文档、仓库或对话中记录原值。==

==安全边界同时收紧：已用 Tailscale 移除 `https://pi.taild4d3f7.ts.net:10000` 的公网 Funnel；Next Action 仅通过 tailnet-only `https://pi.taild4d3f7.ts.net:8450/` 和花园 tailnet-only `https://pi.taild4d3f7.ts.net:8460/` 访问。若以后需要公网入口，必须先恢复独立认证并重新评估。==

==现场验证：8767 与 8838 均只监听 `127.0.0.1`；两层 `/api/next-action/active` 均为 HTTP 200；Funnel 仅剩原有的 443 手机接收服务。私有环境备份位于 `/home/conrad/workspace/backups/next-action-password-disable-20260804-121956/`。==

<!-- ai_provenance: source=codex; date=2026-08-04; verification=checked; retrieved_notes="非笔记内容/工作流程与系统运维/PI_SERVER_HANDOFF.md" -->

## 2026-08-06：New Pomodoro Timer 架构交接

==插件结构说明已写入 `New-Pomodoro-Timer-代码结构与交接.md`。今后排查插件与 Pi 不一致时，先看 Pi `/api/bootstrap` 和 SQLite 会话，再看插件 `focusGardenSession`、`Timer.state` 与 `paused_at/resume_at`；不要用 `data.json` 判断云端专注或奖励。==

<!-- ai_provenance: source=codex; date=2026-08-06; verification=local-verified; retrieved_notes="New-Pomodoro-Timer-代码结构与交接.md" -->

## 2026-08-06：插件 Work/Break 控件交接

==New Pomodoro Timer v1.2.3-focus-garden.8 已在本地插件目录更新。Work 仅使用 Pi 支持的 5/20/30/40/45/60 分钟预设，默认 40；Break 可选 0/5/10/15/20/30 分钟。Break 状态可跳过并自动开始 Work，Work 不可跳过；表盘数字保留启动入口。==

<!-- ai_provenance: source=codex; date=2026-08-06; verification=local-verified; retrieved_notes="New Pomodoro Timer v1.2.3-focus-garden.8" -->

## 2026-08-06：Focus Garden 请求顺序与暂停显示

==`computer_intervention._request_files()` 按请求文件实际写入时间保留最新 80 条，不能按文件名字典序；否则大量 `manual-focus-release-*` 会遮蔽更新的 `manual-focus-时间戳-*`，使 Windows agent 收不到启动或恢复锁机请求。Windows `ComputerInterventionAgent` 已使用 5 秒轮询；不要调回 30 秒。==

==New Pomodoro Timer 每 5 秒只读 `https://pi.taild4d3f7.ts.net:8460/api/bootstrap`，并提供手动刷新。暂停操作先强制刷新 Pi session；若 Pi 返回 paused，插件显示暂停并以 `paused_at` 冻结剩余时间，到 `resume_at` 再恢复。Pi SQLite 仍是唯一状态权威，网页和插件都不直接写 Markdown。==

<!-- ai_provenance: source=codex; date=2026-08-06; verification=server-verified; retrieved_notes="advisor computer_intervention.py, Windows agent runtime, New Pomodoro Timer" -->

## 2026-08-05：Focus Garden 自动暂停恢复

==数据库暂停记录增加恢复截止时刻。POST /api/focus/pause 仍只允许每个 session 一次，接收 1—120 分钟并向现有 Windows agent 排队 release；focus-garden 的 2 秒 reconciler 到期后自动走 resume，恢复相同的电脑 profile 与 blocks。静态网页由 static/focus-pause-ui.js 显示倒计时，没有手动“继续”入口；New Pomodoro Timer 本地计时也在同一截止时刻自动继续。手机 Quick Pomodoro 暂无远程停止 API，暂停期不改变其已启动时长。==

==部署前备份位于 /home/conrad/backups/focus-garden/20260805-auto-pause。已通过 20 项本地单测、两个 JavaScript 语法检查，Pi 重启后 focus-garden.service active、127.0.0.1:8838 bootstrap 与 pause UI 静态文件均返回成功。==

<!-- ai_provenance: source=codex; date=2026-08-05; verification=local-tests-and-pi-service-restart; retrieved_notes="非笔记内容/工作流程与系统运维/PROJECT_STATE.md" -->

## 2026-08-05：番茄可暂停 lease 部署

==Pi 已部署 `focus_garden/database.py`、`server.py`、`cold_turkey.py`，Advisor 的 `computer_intervention.py`、`web_app.py`，以及 `/static/lease-status.js`。部署前备份位于 `/home/conrad/backups/focus-garden/20260805-pomodoro-lease` 和 `/home/conrad/backups/activitywatch-advisor/20260805-pomodoro-lease`。==

==新增接口：`POST /api/focus/pause {pause_minutes}`、`POST /api/focus/resume`，以及仅供同机 Focus Garden 调用的 Advisor `POST /api/interventions/manual-focus/release {blocks, lease_id, session_id}`。release 请求是 durable pending，不因电脑休眠超过 180 秒而丢失；不要对外暴露 Advisor，Garden 仍只通过 loopback 请求它。==

==Windows `D:\tools\computer-intervention-agent\agent.py` 已改为现有 agent 的 `mode=release` 分支和 Cold Turkey `-start`/`-stop` lease，计划任务 `ComputerInterventionAgent` 已重启。系统状态 API 的 `bridges.windows.lease_state` 与 `lease_blocks` 是网页展示的唯一来源。==

<!-- ai_provenance: source=codex; date=2026-08-05; verification=local-tests-and-pi-service-restart; retrieved_notes="非笔记内容/工作流程与系统运维/PI_SERVER_HANDOFF.md" -->

## 2026-08-05：Focus Garden 系统健康面板与 Windows heartbeat

==`focus-garden.service` 新增只读 `GET /api/system-status`。它在同机汇总五项 systemd 服务、`data/task_sync/state.json` queue、Obsidian snapshot/heartbeat、`windows-main` agent state、Android bridge、context cache、最近半小时报告及同步 archive SQLite 的更新时间；接口不返回任务正文、行为原始数据或密钥。浏览器只从既有 tailnet-only `:8460` 访问它，未新增端口、Serve/Funnel 或写入能力。==

==`activitywatch-advisor-web.service` 新增 `POST /api/computer-interventions/heartbeat`，仅记录 Windows agent 的轻量在线事实。`D:\tools\computer-intervention-agent\agent.py` 每 300 秒调用一次；agent 仍只使用 allowlist 执行本机 Cold Turkey，heartbeat 失败不会中止 pending request 的轮询。`ComputerInterventionAgent` 当前为用户登录后的计划任务，入口是 `D:\anaconda\pythonw.exe` 与 `launch_agent.pyw`。==

==2026-08-05 验证：`focus-garden.service`、backup timer、advisor web/timer 和 Syncthing 均 active；`/api/system-status` 显示任务 queue 为 0、Windows 与 Android bridge 在线、archive backup 新鲜。部署前备份位于 `/home/conrad/workspace/activitywatch-advisor/backups/system-health-20260805-204533/`。Pi 上花园测试 15/15 通过；advisor 全量测试 101 项中 100 通过、1 项既有 Next Action fixture 因期望任务标题未进入测试状态而失败，未改动 `next_action.py`。==

<!-- ai_provenance: source=codex; date=2026-08-05; verification=server-verified; retrieved_notes="非笔记内容/工作流程与系统运维/PROJECT_STATE.md,非笔记内容/工作流程与系统运维/NEXT_STEPS.md" -->

## 2026-08-06：系统状态接口兼容列表 active_locks

==2026-08-06 排查：`/api/system-status` 因 `active_locks` 为列表而按字典 `.keys()` 报错，HTTP 连接空响应导致浏览器“Unexpected end of JSON input”。已部署兼容列表/字典的 `focus_garden/server.py`，并在 `static/app.js` 对空响应给出明确提示。备份位于 `/home/conrad/workspace/backups/focus-garden-system-status-20260806-1018/`；本地 22 项测试、Pi 15 项测试通过，服务重启后 loopback 与 `:8460` 均返回 200，五个核心服务 active。==

<!-- ai_provenance: source=codex; date=2026-08-06; verification=server-verified; retrieved_notes="Pi focus-garden journal, deployed server.py and app.js" -->

## 2026-08-06：进入页面空元素报错修复

==`static/app.js` 的同步函数仍引用已从 `index.html` 移除的 `#piStatus`，导致每次进入页面触发 `Cannot set properties of null`。已删除残留写入，并将 `app.js` 改为带 `?v=20260806.2` 版本号。备份位于 `/home/conrad/workspace/backups/focus-garden-sync-pistatus-20260806-1344/`；本地 23 项测试、Pi 21 项测试通过，`:8460` 已确认新脚本不含 `piStatus`。==

<!-- ai_provenance: source=codex; date=2026-08-06; verification=server-verified; retrieved_notes="Focus Garden static app.js and index.html, Pi service health" -->

## 2026-08-05：Windows 到 Pi 统一使用 MagicDNS

==Pi Context Sync 的 SSH 校验、`D:\MyFocusGarden` 开发副本的只读 Pi 同步，以及 Windows 的 `ssh pi.local` 别名均已改为使用 `pi.taild4d3f7.ts.net`。不得在运行配置中固定 `100.109.89.52` 或局域网 DHCP 地址；Tailscale IP 仅可作为当时的诊断信息。MagicDNS SSH 与快照哈希校验已实际通过。==

<!-- ai_provenance: source=codex; date=2026-08-05; verification=checked; retrieved_notes="非笔记内容/工作流程与系统运维/PI_SERVER_HANDOFF.md" -->

## 2026-08-05：任务网页同步 v1

==已部署 `/api/task-sync/state`、`/api/task-sync/mutations`、`/api/task-sync/ack` 于 advisor（仅 127.0.0.1:8767）。状态文件为 `data/task_sync/state.json`；它是网页 mutation queue，不是 Markdown 的权威副本。Focus Garden 在同机以固定 `X-Focus-Garden-Bridge: 1` 代理 `/api/tasks` 与 `/api/tasks/mutations`；Obsidian 插件以独立固定 header 调用 state/ack。==

==运行文件：`/home/conrad/workspace/activitywatch-advisor/src/task_sync.py`、`next_action.py`、`web_app.py`；花园为 `/home/conrad/services/focus-garden/focus_garden/server.py`、`static/index.html`、`static/app.js`。部署前的备份位于 `/home/conrad/workspace/activitywatch-advisor/backups/task-sync-20260805-132419/`，热修复前的 `next_action.py` 另有同目录备份。两项 systemd 服务在 2026-08-05 验证为 active。==

==Next Action 的 `build_decision_state` 会先合并有效任务，再把 `current_timestamp`、`current_date`、`current_time`、`current_weekday`、`timezone` 和 `utc_offset` 传给 AI。循环任务的网页完成操作必须返回错误；不得绕过 Obsidian 插件直接改任务 Markdown。==

<!-- ai_provenance: source=codex; date=2026-08-05; verification=server-verified; retrieved_notes="非笔记内容/工作流程与系统运维/树莓派 Next Action Web架构.md" -->

## 2026-08-05：Focus Garden 任务清单页面

==已将“直接安排任务”从 Next Action 拆出，新增侧栏“任务清单”页。静态文件仍为 `/home/conrad/services/focus-garden/static/index.html` 与 `static/app.js`；页面不引入新 API、端口或公开路由，继续只使用既有的 `/api/tasks` 和 `/api/tasks/mutations` loopback bridge。部署前备份在 `/home/conrad/workspace/activitywatch-advisor/backups/focus-garden-task-list-20260805-171019/`。==

## 2026-08-08：任务清单即时刷新修复

==`static/app.js` 的 API 请求默认 `no-store`；“刷新清单”向 `/api/tasks` 添加时间戳，编辑／推迟／完成／删除收到 mutation 的 `effective` 后立刻回显，并再读取最新有效视图。第二次现场追踪确认原“推迟一天”仍停在原日期并非缓存：旧代码以本地零点加一天后调用 `toISOString()`，在 `Asia/Shanghai` 会因 UTC 转换退回前一日期。现由 `shiftCalendarDate()` 直接计算 `YYYY-MM-DD` 日历字段，`2026-08-06 + 1` 回归验证为 `2026-08-07`，脚本版本更新为 `20260808.2`。Advisor `task_sync.py` 的 ack 同时新增 mutation 语义校验，导出快照未真实反映 update/create/advance_tomatoes 或 complete/delete 时，即使哈希匹配也拒绝确认并保留 queue；同一任务的连续修改按最终字段值合并校验。每周循环表达式 `every week on Monday` 至 `Sunday` 会在 effective view 中投影到今天或下一次对应星期，同时保留原日期审计字段，不改 Markdown。`test_task_sync.py` 现为 8/8。没有新增 API、端口或 Markdown 写入路径。缓存修复回滚副本为 `/home/conrad/services/focus-garden/backups/20260808-0920-task-refresh/`；日期修复回滚副本为 `/home/conrad/services/focus-garden/backups/20260808-0928-postpone-timezone/`；ack 保护回滚副本为 `/home/conrad/workspace/activitywatch-advisor/backups/20260808-0934-task-ack-verification/`；循环投影与连续修改合并回滚副本分别为 `/home/conrad/workspace/activitywatch-advisor/backups/20260808-0944-weekly-recurrence-projection/`、`/home/conrad/workspace/activitywatch-advisor/backups/20260808-0950-task-ack-coalesce/`。==

<!-- ai_provenance: source=codex; date=2026-08-08; verification=reproduced-with-live-task-plus-calendar-regression-ack-guard-and-pi-tailnet-endpoint; retrieved_notes="非笔记内容/工作流程与系统运维/我的专注花园/00-交接总览.md" -->

## 2026-08-05：Focus Garden 关联任务与番茄结算

==`focus_sessions` 已迁移增加 `task_id`、`task_title` 与 `source`；`task_focus_balances` 和 `task_focus_settlements` 是任务专属 40 分钟累计账本。`GardenService.reconcile_focus()` 完成会话后，才通过固定 loopback bridge 向 advisor 的 `/api/task-sync/mutations` 投递 `advance_tomatoes`。这不是 Pi 直写 Markdown：advisor 只保留 queue，Pi Context Sync 读取 effective task view 后以单调的绝对目标更新 `[🍅:: current/total]`，再导出快照并 ack。==

==`advance_tomatoes` payload 的 `settlement_id` 必须是稳定 session ID，advisor 对相同 ID 去重；任务没有正数 🍅 预估、已从快照消失或已经达到预估时，settlement 标记为 skipped，只保留 Focus Garden 历史。Focus Garden 的全局 `focus_credit_minutes` 与任务账本完全分离。==

==公开入口仍仅为 `https://pi.taild4d3f7.ts.net:8460` 的 tailnet-only Serve。`POST /api/focus/start` 新接受可选 `task_id`、`task_title`、`source`，以及空 targets（仅计时）；非空 targets 继续只允许 `windows` / `phone`，并复用已有受限介入通道。==

<!-- ai_provenance: source=codex; date=2026-08-05; verification=server-verified; retrieved_notes="非笔记内容/工作流程与系统运维/我的专注花园/00-交接总览.md" -->

## 2026-08-05：Focus Garden 分级植物规则

==`focus_garden/database.py` 现在在 Pi 权威 SQLite 内派生奖励资格：3 次未兑换 `intervention_accepted` 才创建 1 个 `intervention_basic` 初级种植机会；3 个尚未使用的初级机会才可在一次 `advanced_exchange` 中原子消耗，种下 1 个高级植物。种植 API 依据 `config/plants.json` 的 `tier` 在服务端强制校验；`reward_exchanges` 记录被兑换的机会，防止复用。花园底部显示初级机会数与可用高级种植次数。未增加端口、外部依赖或公开路由。==

<!-- ai_provenance: source=codex; date=2026-08-05; verification=local-tests-passed; retrieved_notes="非笔记内容/工作流程与系统运维/我的专注花园/00-交接总览.md,非笔记内容/工作流程与系统运维/我的专注花园/02-游戏架构.md" -->

## 2026-08-04：专注花园正式电脑＋手机桥接

==`focus-garden.service` 保持 `127.0.0.1:8838` 与 `:8460` 的 tailnet-only Serve，但 `FOCUS_GARDEN_DRY_RUN=0`，`FOCUS_GARDEN_DISPATCH_INTERVENTIONS=1`。网页状态应显示“正式锁定”；切换或排障后用 `curl -fsS http://127.0.0.1:8838/api/health` 和 `GET /api/bootstrap` 检查。==

==Android `com.conrad.focusbridge` v1.0.0 通过 `/api/focus-bridge/heartbeat` 每 5 分钟记录 `android-main`。记录保存在花园权威 SQLite 的 `bridge_health`；超过 20 分钟为 stale，网页只在加载时提示。手机本地日志位于 App 私有文件区，不上传。==

==专注 API：`POST /api/focus/start` 只接受 5/10/20/30/40/45/60；`POST /api/focus/schedule` 创建一次预约；`POST /api/focus/continuous` 创建 30/40/45/60 分钟的多轮计划。连续计划状态保存在 SQLite `focus_plans`，每轮专注结束后进入休息；休息不执行解锁。==

==Windows agent 的 `D:\tools\computer-intervention-agent\config.json` 必须使用 tailnet-only `https://pi.taild4d3f7.ts.net:8450` 且 `auth_required=false`；不要记录或输出该文件中的任何密码字段。其 `state.json` 的 `last_poll_status=no_pending` 表示链路待命。==

<!-- ai_provenance: source=codex; date=2026-08-04; verification=checked; retrieved_notes="非笔记内容/工作流程与系统运维/PI_SERVER_HANDOFF.md" -->

## 2026-08-04：移动端布局、蘑菇迁移与锁机重试

==已部署花园静态页修复：手机端时长按钮为 4 列换行，移除本次专注读数与停止计时入口；图鉴为两列；花园阶段不再固定最小高度，桌面植物说明不被花园框裁切、手机端不显示悬浮说明。当前 `plants.json` 只发布 Minecraft 红/棕蘑菇，Mushroom Nook 素材文件和分类扩展代码未删除。==

==迁移前已以 SQLite backup API 生成 `/home/conrad/services/focus-garden/data/focus-garden-before-minecraft-mushrooms-20260804-225207.sqlite3`；权威库中一株 Mushroom Nook 与一株红蘑菇均已改为 `brown_mushroom`。==

==Windows agent 已加入非阻塞的“专注锁机已开始”短提示；其 Cold Turkey 命令不成功时在 30 秒后重试一次。Focus Bridge v1.0.1 在手机锁屏导致可访问窗口不可用时，每 30 秒重新尝试启动已确认的快速番茄，最多 6 次；第一次尝试即显示手机通知。新 APK 已编译，但设备安装命令等待 Package Manager，需在解锁后重新单次安装确认。==

<!-- ai_provenance: source=codex; date=2026-08-04; verification=checked; retrieved_notes="非笔记内容/工作流程与系统运维/PI_SERVER_HANDOFF.md" -->

## 2026-08-06：近期动态 v3.1 交接补充

==新增模块：src/recent_context.py（存储/RLock/revision/损坏恢复/解析/动态状态/粗筛）、src/recent_context_selector.py（V4 Flash 非思考筛选 + 本地降级）。数据：data/recent_context/state.json + parse_audit.jsonl。API（全部要求 loopback + X-Focus-Garden-Bridge==1）：GET /api/recent-context[?include_archived=1]、GET /api/recent-context/relevant；POST /api/recent-context、/{id}/update、/{id}/archive、/{id}/unarchive、/{id}/pin、/{id}/unpin、/{id}/confirm。写接口必须带 expected_revision；冲突 409 {code:revision_conflict,current_revision}；损坏 503 recent_context_state_corrupt（损坏文件只复制一次为 state.json.corrupt-<ts>，不回退空状态）。next_action.py PROMPT_VERSION=next-action-v1.3，build_decision_state 之后 attach recent_context（代码粗筛→AI 筛选→最多 6 条），最终 AI 需返回 decision_trace.recent_context_used（服务端子集校验）。Focus Garden：侧栏「近期动态」页 + Next Action「当前情境」卡（≤3 条，代码粗筛，不调筛选 AI）；代理白名单 _RECENT_CONTEXT_PATHS。settings.json 新增 recent_context 段（enabled/direct_window_hours=24/preparation_window_days=7/review_after_days=14/parser_*/selector_*）。验收：2026-08-06 本地真实 AI 冒烟 + Pi 全量测试（advisor 141 仅 2 项既有失败、garden 23/23）+ enabled=false→true 分阶段 + 两条测试记录归档。回滚：保留 data/recent_context/ 永不删除。==

## 2026-08-07：Cold Turkey lease 休眠补偿部署

==Windows `D:\tools\computer-intervention-agent\agent.py` 已加入 wall-clock lease 回收：agent 启动、每轮轮询和处理请求后检查 `active_locks[*].lock_until_estimated`，过期即执行 `-stop`；状态持久化后，电脑休眠或 agent 重启不会跳过到期解锁。release 请求带 `lease_id` ownership，旧 release 不会关闭新的 lease；失败 release 不发送 final 完成回执，会保留 pending 继续重试。==

==Advisor 的 `computer_intervention.py` 与 `web_app.py` 已将 Focus release 改为 durable pending、稳定请求 ID，并优先保留所有 release 文件，不受普通请求 80 条扫描窗口影响。Focus Garden `server.py` 已改为先确保 release 入队再完成 session，避免到期异常造成已结算但未解锁。==

==部署前备份：`/home/conrad/workspace/backups/cold-turkey-lease-20260807-132900/` 与 `/home/conrad/workspace/backups/focus-garden-cold-turkey-lease-20260807-133000/`。`activitywatch-advisor-web.service`、`focus-garden.service` 已重启并保持 active；loopback health 返回 200。==

==验证：Windows agent 测试 6/6、Advisor intervention 测试 6/6、Focus Garden 本地测试 27/27 通过。Advisor 全量测试仍有 2 项既有 task/Next Action fixture 失败，与本次 lease 改动无关，未修改相关模块。==

<!-- ai_provenance: source=codex; date=2026-08-07; verification=local-tests-and-pi-service-restart; retrieved_notes="非笔记内容/工作流程与系统运维/PI_SERVER_HANDOFF.md" -->

## 2026-08-07：Focus Bridge 1.1.0 公网主链路

==Android 工程：`D:\MyFocusGarden\focus-bridge-android`。1.1.0 将轮询/心跳迁入 `BridgeForegroundService`（15 秒/5 分钟、失败心跳 60 秒重试、`START_STICKY`），BootReceiver 在开机和包升级后恢复服务。公网是关键链路；Tailnet `https://pi.taild4d3f7.ts.net:8460` 仅作 IOException 备用。==

==公网代理复用 `phone-usage-receiver.service` 与 Funnel 443，只开放四个固定路径：`GET /focus-bridge/pending`、`POST /focus-bridge/heartbeat`、`POST /focus-bridge/decision`、`POST /focus-bridge/event`，上游只允许 `127.0.0.1:8838` 对应接口，请求体上限 16 KiB。代码：`/home/conrad/phone_usage/receiver.py`；设备密钥：`/home/conrad/phone_usage/focus_bridge_token.txt`（0600，禁止写入日志、Git、文档或终端输出）。==

==Focus Garden 验收模块及其页面已回退。原因：首次部署使用了缺少「近期动态」的旧本地副本，覆盖了 Pi 较新前端。恢复来源：`/home/conrad/workspace/backups/focus-garden-cold-turkey-lease-20260807-133000/server.py` 与 `/home/conrad/workspace/backups/focus-bridge-monitor-20260807-1333/static/`；错误版本另存于 `/home/conrad/workspace/backups/focus-garden-rollback-20260807-1425/`。未回滚 SQLite，近期动态数据未删除。==

==回退验证：Android `assembleDebug` 与真机安装此前已成功；公网心跳代理继续保留。Focus Garden 本地与 Pi 原版测试 23/23，`focus-garden.service` active；`/api/recent-context` 返回 `revision=5` 和 1 条记录，Tailnet 页面重新出现「近期动态」。==

<!-- ai_provenance: source=codex; date=2026-08-07; verification=rollback-and-server-verified; retrieved_notes="非笔记内容/工作流程与系统运维/PI_SERVER_HANDOFF.md" -->

## 2026-08-07：任务待安排区、删除与分钟级近期动态

==任务 queue 新增 `delete` mutation；有效任务视图新增 `unassigned` 分组。电脑端 Pi Context Sync 是唯一 Markdown 写入器：没有 `⏳` 的 create/update 写入 `ToDo-任务集合.md` 顶部 `# ⚠️ 树莓派新增 · 待正式安排`，保留 `^blockid`；有 `⏳` 时移动至 `ToDo-已经规划好的任务.md`，完成移至 `已完成任务.md`，删除从原文件移除。不要让 Pi 直接改 Vault。==

==`src/recent_context.py` 的 `range.start/end` 现在接受日期或分钟级 `YYYY-MM-DDTHH:MM+08:00`；日期端点仍按整日边界解释。确定性状态判断使用该精度；语义解析与相关性筛选继续固定 `deepseek-v4-flash` / `thinking=disabled`，10 秒、零重试。已备份修改前 advisor 到 `backups/task-context-20260807-181500/`，花园前端到 `/home/conrad/services/focus-garden/backups/task-context-20260807-181500/`。==

==验证：Pi 上 `test_task_sync.py` 5/5、`test_recent_context.py` 23/23；`activitywatch-advisor-web.service` 和 `focus-garden.service` 均重启为 active，并经 loopback `/api/task-sync/state` 与 `/api/tasks` 返回成功确认。==

<!-- ai_provenance: source=codex; date=2026-08-07; verification=local-and-pi-tests-plus-live-endpoints; retrieved_notes="非笔记内容/工作流程与系统运维/PI_SERVER_HANDOFF.md" -->

## 2026-08-07：Next Action 两轮行动澄清

==advisor 修改：`src/next_action.py`（`clarify_next_action`、与初始建议相同的 V4 Pro 思考模型、完整有界 `dialogue_history`、action revision 与接受校验）、`src/web_app.py`（`POST /api/next-action/{suggestion_id}/clarify`）、`tests/test_next_action.py`。Garden 修改：`focus_garden/server.py` 固定白名单转发 `/clarify`，`static/{app.js,index.html,style.css}` 提供“说说哪里卡住”卡片、0/2 轮次、简短上下文与“接受最后更新的这一步”提示。==

==初版 UI/接口备份：`/home/conrad/workspace/activitywatch-advisor/backups/20260807-clarify-2rounds/` 与 `/home/conrad/services/focus-garden/backups/20260807-clarify-2rounds/`；随后模型策略改为复用 V4 Pro 思考模型前的 advisor 备份：`/home/conrad/workspace/activitywatch-advisor/backups/20260807-clarify-pro-model/`；加入完整两轮 dialogue history 前的 advisor 备份：`/home/conrad/workspace/activitywatch-advisor/backups/20260807-clarify-dialogue-context/`。恢复时只还原所需同名源码/静态文件并重启 `activitywatch-advisor-web.service focus-garden.service`；保留 `data/next_action/`，它包含用户的 active suggestion、澄清和反馈审计。验证：新增两轮/version/accept/model/context 单测通过，两服务 active，loopback 的 advisor 与 Garden `/api/next-action/active` 均返回 200。==

<!-- ai_provenance: source=codex; date=2026-08-07; verification=targeted-unit-test-plus-pi-service-restart; retrieved_notes="Pi activitywatch-advisor and focus-garden deployment" -->

## 2026-08-07：Next Action 模型可用性误报修复

==症状：页面把最新建议显示为“模型暂时不可用”，但归档 `_generation.finish_reason=stop` 且包含 DeepSeek V4 Pro 的正常 token 用量，说明模型调用本身已成功。根因在 `src/next_action.py` 的番茄钟结果校验：它把不同字段中“还剩 1 个番茄（40 分钟预算）”与“25 分钟启动片段”拼接后误认为“一个番茄等于 25 分钟”，抛出 `ValueError` 并错误降级为 fallback。==

==修复：校验现只在同一句确实将番茄钟与 15/25/30 分钟相等、完成或耗时关联时拒绝；独立的剩余预算和短启动片段可以共存。保留真正“用 25 分钟完成这个番茄”的拒绝测试，并新增误报场景的允许测试。部署前备份：`/home/conrad/workspace/backups/next-action-20260807-2039/`。==

## 2026-08-07：Focus Bridge 1.2.1 介入页与真机闭环

==Windows 源码位于 `D:\MyFocusGarden\focus-bridge-android`，安装包为 `app\build\outputs\apk\debug\app-debug.apk`，当前手机版本 `1.2.1 (14)`。新增 `InterventionPromptActivity` 与纯 Java `OfferStateMachine`：锁屏等待总预算 120 秒；手机可用后显示 10 秒整数倒计时；接受、拒绝或超时忽略均交回前台服务持久化提交；选择页重新锁屏时关闭并恢复等待。说明文字若已损坏为连续问号或 `U+FFFD`，应用回退为内置中文。==

==前台服务继续独立承担 15 秒 pending 轮询和 5 分钟 heartbeat；公网 HTTPS 是主链路，Tailnet 仅为 IOException fallback。决定在本地持久化，网络失败每 15 秒重试；提交成功前，`no_pending` 或新 offer 不得清除旧决定。无障碍服务继续负责打开“不做手机控”和可见校准点击，Automate 不在关键链路。==

==验证：`verify.ps1` 的 13 项状态机检查与 offline clean assembleDebug 通过。用户确认介入页正文、10 秒整数倒计时显示正常。Pi 决定 `bridge-accept-test-20260807T220244-f94ce3=accepted`；Android 22:03:04 开始 5 分钟正式流程、22:03:05 完成 `quick_pomodoro_confirmed_calibrated`，Pi 22:03:06 保存 final response。另一次损坏消息测试在 10 秒后正确提交 `ignored`。未修改 Focus Garden 生产代码、数据库或“近期动态”。完整专题见 [[我的专注花园/专注花园桥接手机APP]]。==

<!-- ai_provenance: source=codex; date=2026-08-07; verification=user-confirmed-plus-device-and-pi-event; retrieved_notes="非笔记内容/工作流程与系统运维/我的专注花园/专注花园桥接手机APP.md" -->

## 2026-08-07：Focus Garden 使用频率卡片

==开始专注页右侧「最近奖励」下已新增「花园使用频率」。卡片逐日列出近三日的花园已完成专注分钟数、Next Action 完成／采纳／询问数，并另列本周；日行比较上周同日，本周比较上周同期。`完成` 是 accepted suggestion 后记录 completed outcome 的唯一建议数，不是 Garden 专注 session 数。来源只读 Pi SQLite 与 advisor Next Action 归档，不新增写入、端口或公开路由。==

==生产文件：`/home/conrad/services/focus-garden/focus_garden/{database.py,server.py}`、`static/{index.html,app.js,frequency.css}`，测试为 28/28，通过后 `focus-garden.service` 已重启 active，`https://pi.taild4d3f7.ts.net:8460/` 返回 200。备份：`/home/conrad/services/focus-garden/backups/focus-garden-frequency-20260807-2226/` 与逐日调整前的 `.../focus-garden-frequency-20260807-2231-before-daily-breakdown/`。==

<!-- ai_provenance: source=codex; date=2026-08-07; verification=local-and-pi-tests-plus-tailnet-ui; retrieved_notes="我的专注花园/00-交接总览.md,我的专注花园/02-游戏架构.md,我的专注花园/05-Pi迁移验收与恢复清单.md" -->

## 2026-08-07：Cold Turkey release backlog 隔离与保守归档

==事故：22:09 的 execute 回执为 accepted，但 6 秒后收到一条 2026-08-06 创建的 `manual_focus_pause` release。该旧请求没有 `lease_id`，旧 Agent 路径将它作为泛化 `-stop` 执行。随后确认共 2,761 条同类记录；它们产生于旧 Focus Garden 的无 lease release 路径，并被“所有 release durable”扫描重新派发。==

==修复：`D:\tools\computer-intervention-agent\agent.py` 对无 lease release 返回 final `legacy_release_ignored`，绝不调用 Cold Turkey；Advisor `src/computer_intervention.py` 拒绝创建无 lease release，超过 10 分钟宽限期的历史无 lease 文件归档到 `data/computer_interventions/archive/release/legacy-unleased/`。所有带 lease 的 release 一直待命，直到 Agent final 后移至 `archive/release/completed/`。原始 JSON 保留，不做不可恢复删除。==

==Focus Garden 生产端 `/home/conrad/services/focus-garden/focus_garden/server.py` 从 execute dispatcher receipt 读取 lease 并在结束/取消前请求 release；没有可验证 lease 的历史 session 不发泛化 stop，依赖 Agent 的 wall-clock expiry 作为安全兜底。备份：Advisor `/home/conrad/workspace/backups/cold-turkey-release-legacy-fix-20260807-223100/`，Garden `/home/conrad/workspace/backups/focus-garden-release-lease-fix-20260807-224000/`。验证：Windows Agent 7/7、Advisor 9/9、Garden 29/29；两个服务 active，`/api/health` 正常，派发队列 release 为 0。==

<!-- ai_provenance: source=codex; date=2026-08-07; verification=windows-and-pi-tests-plus-live-queue-check; retrieved_notes="非笔记内容/工作流程与系统运维/PI_SERVER_HANDOFF.md" -->

## 2026-08-07：闲鱼购物分类与介入触发隔离

==Advisor 修改：`config/tag_rules.json` 新增 `shopping.xianyu`，以标题、idlefish 域名、手机/平板应用名与 `com.taobao.idlefish` 包名锁定 `shopping`；`src/{fact_tagger.py,semantic_analysis.py,deepseek_client.py,run_half_hour.py,pushplus_client.py,daily_life_statistics.py}` 和 `prompts/semantic-segmenter.md` 已扩展购物分类。`shopping` 在报告、推送和每日汇总中单列，但不参与娱乐偏离、工作—娱乐转换或行为介入。==

==备份：`/home/conrad/backups/activitywatch-advisor/xianyu-shopping-20260807-231928/`。验证：JSON/语法检查通过；`test_cleaning`、`test_daily_life_statistics`、`test_computer_intervention` 共 45/45 通过；按 2026-08-07 22:45—22:49 闲鱼窗口回放为 shopping、deviation=0、qualified transitions=0。全量 discover 为 151/152，通过外的一项为 `test_next_action.test_build_state_uses_context_and_recent_reports` 的任务夹具上下文未产生 task_titles，未改动该模块。无需重启 timer；web service 保持 active。==

<!-- ai_provenance: source=codex; date=2026-08-07; verification=pi-targeted-tests-and-replay; retrieved_notes="非笔记内容/工作流程与系统运维/PI_SERVER_HANDOFF.md" -->

## 2026-08-07：Focus Bridge 1.3.1 真实锁机确认与时效降级

==手机已安装 `1.3.1 (16)`。新增 Android `GetawayNotificationListenerService`（系统通知使用权）确认 `com.pl.getaway.getaway` 的真实 `getaway_pomo` 子通知；group summary 不算成功。熄屏/锁定期间每秒轮询且不消耗 attempts；亮屏解锁后最多三次，每次间隔 20 秒。三次仍无真实通知则写手机日志、上传 final failed，并由花园“最近锁机执行”显示错误。final 结果先存本机，网络失败每 15 秒重传。==

==自动介入执行按 execute `created_at` 降级：`<8 分钟 → 30 分钟`、`8–<15 分钟 → 20 分钟`、`≥15 分钟 → expired 且不锁机`；手动专注与本地调试保持指定时长。Advisor `src/computer_intervention.py` 将接受后 execute TTL 从 180 秒延长到 960 秒，给手机留出 15 分钟判断与短暂 final 回传余量。备份：Android `D:\MyFocusGarden\backups\20260807-lock-confirm-before\focus-bridge-android`；Advisor `/home/conrad/workspace/activitywatch-advisor/backups/20260807-phone-lock-age/`；Garden `/home/conrad/services/focus-garden/backups/20260807-lock-confirm-before/`。==

==Focus Garden 生产端仅窄改 `focus_garden/server.py` 与 `bridge_monitor.py`：心跳白名单接收通知权限/连接、锁机状态/时长/次数/错误；系统状态新增“锁机结果确认”“最近锁机执行”，最低合格版本为 1.3.0。未替换 static 前端、SQLite 或“近期动态”。Garden monitor 5/5、Advisor intervention 10/10、Android 26 项纯 Java 检查与 Gradle build 均通过；`focus-garden.service`、`activitywatch-advisor-web.service` active，loopback `/api/health` 与 `/api/system-status` 正常。==

==真机实测：5 分钟第 1 次通知确认成功；新鲜 30 分钟按 20 秒间隔三次失败并同步到花园；9 分钟请求自动降为 20 分钟并成功确认；15 分钟请求直接 expired；确认 `mWakefulness=Asleep` 后投递时为 `waiting_screen / attempts=0`，手动解锁后才尝试并最终确认 30 分钟。熄屏测试中 Android 服务曾被系统重建，Pi 未 final 的请求重新下发后恢复成功。完整架构见 [[我的专注花园/专注花园桥接手机APP]]。==

<!-- ai_provenance: source=codex; date=2026-08-07; verification=device-plus-pi-multi-scenario-tested; retrieved_notes="非笔记内容/工作流程与系统运维/我的专注花园/专注花园桥接手机APP.md" -->

## 2026-08-07：可编辑源码迁移与私有素材隔离

==迁移控制仓库：`/home/conrad/workspace/pi-portable-system/`（tag `portable-system-v1`）；安全源码导出：`/home/conrad/workspace/pi-system-migration/current/`；Monaco 可编辑区：`/home/conrad/workspace/editable/`。生产服务路径未改变。安全导出由 `pi-portable-export.timer` 每 6 小时触发，Windows 接收端为 `D:\PiSystemMigration`；Pi 文件夹模式为 Send Only，Windows 为 Receive Only 并启用 staggered versioning。==

==仓库安全边界：Advisor、Focus Garden、phone receiver 和迁移控制仓库均无外部 remote，pre-push 默认拒绝发布；编辑副本的 `production-local` 只能指向 Pi 本机路径。Focus Garden 私有编辑副本含 51 个被忽略的 Minecraft 来源素材，生产仓库和安全导出均不跟踪/携带它们。素材校验清单仅保存在 `/home/conrad/.local/state/pi-portable-system/private-assets.sha256`，权限 0600。==

==私有恢复链路尚未激活：Restic 0.18.0 已安装，但 `/root/.config/pi-portable-system/restic.env` 不存在，`pi-portable-private-backup.timer` 为 disabled/inactive，脚本会以退出码 3 安全拒绝运行。配置外部私有仓库后，应依次运行 `backup-private-state.sh`、`check-private-backup.sh`、`restore-private-to-staging.sh`，先在 staging 验证，禁止直接覆盖生产。验证结果：基础设施脚本语法、YAML、systemd 单元、生产端口/路由和安全导出均通过；Garden 31/31、pi-editor 29/29、phone receiver 编译通过；Advisor 152/153，其中唯一失败仍是已知的 `test_build_state_uses_context_and_recent_reports` 任务夹具问题。==

<!-- ai_provenance: source=codex; date=2026-08-07; verification=pi-live-and-windows-manifest-verified; retrieved_notes="Pi live system, systemd units, Git repositories, Syncthing configuration" -->

## 2026-08-07：手机与电脑客户端迁移基线

==客户端版本指针为 `D:\PiClientMigration\CURRENT.json`，当前 `2026.08.07-r1`。Android Focus Bridge 源码 commit `17bd187`、tag `focus-bridge-v1.3.1-build16`，APK SHA-256 为 `9c9c53b4ff46a7d7fb73fbbcdc2089584538e3da013d4090982430e5ff039b9d`；Computer Agent commit `9c97cc7`；Behavior Context Exporter commit `35f6dbf`。三个仓库均无 remote，pre-push 拒绝发布。==

==release 另含 ActivityWatch 同步脚本、Pi Editor bypass 和当前 6 个计划任务 XML。XML 只作旧机证据，不能在新机直接无脑导入，因为用户名、SID 和绝对路径会变化。恢复应从 Git bundle clone 可编辑源码，复制 example 为真实配置，再运行各组件安装脚本。完整流程见 [[Pi系统手机端与电脑端迁移配置流程]]。==

==安全边界：Focus Bridge token 在新手机生成后通过 `pair-focus-bridge.ps1` 直接写入 Pi；脚本不打印 token。Automate 私有 flow 位于 Vault 的既有二进制文件，因内含上传 token，只记录哈希而未进入 release。私有配置仍等待外部 Restic 仓库；Minecraft 来源素材不属于任何客户端构建。==

==客户端 release 已通过 Syncthing folder `pi-client-migration` 形成第二份副本：Windows `D:\PiClientMigration` 为 Send Only，Pi `/home/conrad/workspace/pi-client-migration` 为 Receive Only并启用 staggered versioning。该目录无密钥，不能用来恢复 Automate token、SSH/Syncthing 身份或私有素材。==

<!-- ai_provenance: source=codex; date=2026-08-07; verification=local-source-tests-build-and-bundle-verified; retrieved_notes="local client sources, builds, Scheduled Tasks" -->
