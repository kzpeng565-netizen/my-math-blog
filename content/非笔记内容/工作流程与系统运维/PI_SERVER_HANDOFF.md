<!-- ai_provenance: source=codex; date=2026-07-26; verification=server-verified; retrieved_notes="D:\mathblog\quartz\content\非笔记内容\工作流程与系统运维\手机使用记录系统——树莓派端操作与维护指南.md","D:\mathblog\quartz\content\非笔记内容\工作流程与系统运维\手机使用记录系统——手机端操作与维护指南.md","C:/Users/15345/.codex/skills/manage-pi-server/references/server-layout.md" -->

# 半小时行为解释系统——接管交接文档

> [!summary]
> 本文档供后续 AI Agent 接管此项目时使用。标记体系：**[已由旧对话确认]**、**[已由服务器核实]**、**[仅讨论过]**、**[当前无法确认]**。

## 1. 项目目标与总体架构

**[已由旧对话确认]**

用户（Conrad）建立一个**个人行为反馈中枢**，在树莓派上每半小时自动收集电脑与手机使用数据，清洗后交 AI 解释，通过 PushPlus 微信公众号发送短核验消息。当前阶段（第一至第三版）**只核验 AI 理解能力，不自动干预**。

<!-- ai_provenance: source=codex; date=2026-07-28; verification=server-verified; retrieved_notes="非笔记内容/工作流程与系统运维/PROJECT_STATE.md,非笔记内容/工作流程与系统运维/DECISIONS.md,非笔记内容/工作流程与系统运维/NEXT_STEPS.md" -->

==**[已由用户确认][已由服务器核实] 2026-07-28 已进入第四版：增加只读 Obsidian 上下文、影子判断、日/周统计、PushPlus 人工核验和全设备无活动静默。正式干预仍未启用。**==

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
           pushplus_client.py → 微信公众号（AI解释 + 影子判断）
                     |
           statistics_notifier.py → 日报 09:00 / 周报周一 09:05
```

> [!important]
> ==**[已由用户确认][已由服务器核实] 当电脑没有非 AFK 活动（含无电脑消息/数据），且手机、平板均无亮屏证据时，不调用 DeepSeek、不发送 PushPlus；仍归档事实、上下文、本地报告、影子候选和统计。完整版必须保留该 token 节省短路。**==

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
| `D:\mathblog\tools\behavior-context-exporter\` | Windows 实际运行的只读导出器、配置、测试及安装/卸载脚本 |

### 4.2 服务

**[已由服务器核实]**

| 服务 | 状态 | 说明 |
|---|---|---|
| `phone-usage-receiver.service` | active | 手机/平板数据上传接收与手机异常反馈接收，监听 `127.0.0.1:8765` |
| `phone-usage-maintenance.timer` | active | 每日约 03:30 归档压缩/清理 |
| `activitywatch-advisor.timer` | active, enabled | 每半小时 08/38 分触发分析 |
| `activitywatch-advisor.service` | inactive (dead, triggered by timer) | 单次分析，完成后退出 |
| `activitywatch-advisor-daily-summary.timer` | active, enabled | 每天 09:00 发送前一天统计 |
| `activitywatch-advisor-weekly-summary.timer` | active, enabled | 周一 09:05 发送上一自然周统计 |
| `syncthing@conrad.service` | active | 同步 ActivityWatch 数据 |
| `tailscaled.service` | active | Tailscale VPN + Funnel |
| `cockpit.socket` | active | Web 管理 9090 |
| `filebrowser.service` | active | 文件管理 8080 |

**[已由服务器核实]** 最新一次修复后 systemd timer 触发：`2026-07-28 11:08`（已完成，service 最终为 inactive/dead 的正常 oneshot 状态）。该时段手机真实亮屏 1.2 分钟，故正常调用模型并推送；平板旧亮屏已转为 `unknown`，未再造成虚假活动。

**[已由服务器核实]** ==`phone-usage-receiver.service` 仍只监听 `127.0.0.1:8765`。Tailscale Funnel 当前仍将 `https://pi.taild4d3f7.ts.net` 代理到 `http://127.0.0.1:8765`；`/upload/` 使用原 `X-Upload-Token`，`/annotation` 使用 `Authorization: Bearer <token>`。systemd unit 的 `ReadWritePaths` 已包含 `/home/conrad/phone_usage` 和 `/home/conrad/workspace/activitywatch-advisor/data/user_annotations`。==

### 4.3 配置要点

**[已由服务器核实]**

- 模型：DeepSeek V4 Flash (`https://api.deepseek.com/chat/completions`)
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

## 5. 已验证成功的功能

**[已由旧对话确认][已由服务器核实]**

1. 手机 Automate 流采集并上传 foreground/screen/heartbeat -- 已验证
2. 手机数据通过 Tailscale Funnel HTTPS 到达树莓派 -- 已验证
3. `phone-usage-receiver` 接收、验证、去重、合并、归档 -- 已验证
4. ActivityWatch Windows 端采集并通过 Syncthing 同步到树莓派 -- 已验证
5. `computer_facts.py` 从 SQLite 提取并清洗电脑事实 -- 已验证
6. `phone_facts.py` 从 JSONL 提取并清洗手机事实 -- 已验证
7. `tablet_facts.py` 从 JSONL 提取并清洗平板事实 -- 已验证
7. DeepSeek 语义时间线生成（第1次调用）-- 已验证
8. 程序校验语义时间线并计算混杂指标 -- 已验证
9. DeepSeek 报告生成（第2次调用）-- 已验证
10. PushPlus 微信公众号推送 -- 已验证
11. 定时器每半小时自动触发全流程 -- 已验证（2026-07-25 全天 48 个时段均已产出报告）
12. 手机心率检测与休息规则 -- 已验证
13. 工作-娱乐混杂指标（>30s 偏离判定）-- 已验证
14. Obsidian 三文件只读导出、任务解析、中文路径及原子写入 -- 已验证（Windows 5 项测试）
15. Behavior Context Syncthing Send Only → Receive Only、中文文件名和 SHA-256 -- 已验证
16. 上下文 schema 校验、冲突文件忽略、last-known-good 回退和完全不可用降级 -- 已验证
17. 影子候选生成、归档并合并进半小时 PushPlus 消息 -- 已验证
18. 每日/每周统计定时生成、PushPlus 实际发送及回执去重 -- 已验证
19. DeepSeek 非法 JSON 降级为本地低置信度报告，不中断主流程 -- 已验证
20. 全设备无活动时 `model: null`、PushPlus `all_devices_inactive`、仍完整归档 -- 已验证
21. ==过期手机/平板亮屏状态不再跨时段外推，且同一个前置静默判断同时跳过 DeepSeek 和 PushPlus -- 已用 2026-07-28 04:00—04:30 历史窗口隔离回放验证；主项目 29 项测试通过==
22. ==手机异常反馈接入 -- 已验证。localhost 集成测试覆盖表单、JSON、中文 message、空说明、`category=4` 空说明、非法分类、超长 message、缺失/错误 token、报告不存在仍保存、Markdown 从 raw 重建和同秒不同 ID；接入后主项目 42 项测试通过。==
23. ==手机真实提交 -- 已验证。2026-07-28 19:40:45 与 19:40:58 两条真实反馈均返回 `201`，保存到 `data/user_annotations/raw/2026-07-28/`，并重建当日 Markdown 与 `UNREVIEWED.md`。==

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

## 7. 当前接管状态

==**[已由服务器核实] 本节旧中断信息已被 2026-07-28 状态取代。本次静默修复已经部署，系统状态 `running`，三个 advisor timer 均 active。手机异常反馈接入已提交为 `6462485 feat: add phone annotation intake and review logs`；当前仍有四个尚未提交但已部署的静默修复文件：`src/phone_facts.py`、`src/run_half_hour.py`、`src/tablet_facts.py`、`tests/test_cleaning.py`。**==

## 8. 尚未完成或尚未验证的事项

**[已由服务器核实]** 当前尚未完成：

- Windows Task Scheduler 尚需用户以管理员 PowerShell 运行一次安装脚本
- 影子模式尚未完成 3—7 天人工观察，不得启用正式提醒
- 120 分钟历史、正式 60 分钟冷却和有限提醒尚未实现
- 微信核验回复自动回写尚未实现
- ==手机异常反馈已有入口和 raw/Markdown 记录，但尚未实现人工处理界面、`status` 更新流程或基于反馈的 prompt/config 候选修改流程。==

**[仅讨论过]**：

- 替代信息流平台（树莓派信息过滤）-- 仅讨论
- 自动管控（Cold Turkey / 不做手机控联动）-- 仅讨论
- AI 维护提示词和 Skills -- 仅讨论

**[当前无法确认]** 的事项：

- 手机端 Automate 流是否仍然正常运行（需查看今天上新数据确认）
- DeepSeek API 密钥是否需要轮换（架构文档建议在部署后轮换）
- 正式提醒启用前的影子误报率是否足够低

## 9. 下一步最合理的操作顺序

**[建议顺序]**

1. ==**安装 Windows 定时导出任务**：管理员 PowerShell 运行 `D:\mathblog\tools\behavior-context-exporter\scripts\install_exporter_task.ps1`。==
2. ==**观察影子判断 3—7 天**：核对数学学习、知乎、休息、陈旧上下文和候选任务。==
3. ==**检查日/周统计**：日报 09:00、周报周一 09:05；核对报告数与分钟数。==
4. **数据增长监控**：运行一周后计算真实日增长量。
5. **API 密钥轮换**：在 DeepSeek 控制台生成新密钥并更新私有环境文件。
6. **完整版验收**：确认无活动时仍停止 AI、继续归档；确认冷却期、单动作和数据不足不提醒。
7. **信息过滤平台**：在行为数据可靠后再建设替代信息供给系统。

## 10. 后续 Agent 接管时的注意事项

**[必须遵守]**

1. **SSH 连接**：使用 `ssh -o BatchMode=yes pi.local`；密钥在 `C:\Users\15345\.ssh\pi_server_ed25519`
2. **不要暴露密钥**：DeepSeek API 密钥在 `/home/conrad/.config/activitywatch-advisor/env`（600 权限）；PushPlus token 在 `.../pushplus.env`；上传 token 在 `/home/conrad/phone_usage/token.txt`
3. **服务只监听 localhost**：`phone-usage-receiver` 只在 `127.0.0.1:8765`，通过 Tailscale Funnel 对外暴露
4. **定时器是 enabled**：修改后需要 `systemctl daemon-reload`
5. **配置文件的位置**：`settings.json` 在 `activitywatch-advisor/config/`；不要与 `.config/activitywatch-advisor/env` 混淆
6. **输出数据结构**：computer_facts 和 phone_facts 设计为可复用层，全天分析时可直接读取而不重新处理原始事件
7. **手机数据可能有延迟**：约 15 分钟上传一次，timer 在 08/38 分运行就是为了等待最近一轮上传
8. **休息规则是用户确认的**：不要修改 AFK >= 3 分钟 + 手机熄屏的判断逻辑
9. **推送是单向的**：微信公众号回复不会写回系统；==手机桌面快捷 `/annotation` 是当前人工反馈入口==
10. **不要修改 `server-layout.md` 未经过验证的部分**
11. **Obsidian vault 路径**：`D:\mathblog\quartz\content`，项目文档应放在 `非笔记内容/工作流程与系统运维/`
12. **此文件是交接文档**：后续 Agent 接手时应先阅读此文件，再阅读 `server-layout.md` 和 `半小时行为解释系统——架构与维护.md`
13. ==**Obsidian 是唯一任务权威源**：不得从树莓派修改任务、日期、完成状态或番茄钟进度。==
14. ==**番茄钟只作弱参考**：使用声明 `duration`；无记录不是无学习，长墙钟跨度可来自暂停。==
15. ==**全设备无活动必须静默**：不调用 DeepSeek、不发 PushPlus，但所有本地归档必须继续。==
16. ==**正式提醒未启用**：`shadow_mode` 必须保持 `true`，除非用户在观察 3—7 天后明确授权。==
17. ==**AI 报告有存档**：`data/ai_reports/` 同时保留 JSON 和 Markdown，不要只依赖微信消息。==
18. ==**不要恢复旧的移动设备状态外推**：手机或平板超过 `heartbeat_stale_seconds` 的最后屏幕事件必须视为 `unknown`；`unknown` 不等于亮屏，也不应阻止无活动静默。==
19. ==**AI 和通知必须共用前置静默结果**：不得在调用 DeepSeek 后才单独判断是否推送。==
20. ==**不要把反馈当作自动修复指令**：`data/user_annotations/raw/` 是人工调试标注，AI 不得自动修改 raw JSON，不得在接收请求时调用 DeepSeek，也不得直接改任务或配置。==

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
