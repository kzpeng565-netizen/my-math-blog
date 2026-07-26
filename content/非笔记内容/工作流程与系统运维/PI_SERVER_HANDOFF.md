<!-- ai_provenance: source=codex; date=2026-07-26; verification=server-verified; retrieved_notes="D:\mathblog\quartz\content\非笔记内容\工作流程与系统运维\手机使用记录系统——树莓派端操作与维护指南.md","D:\mathblog\quartz\content\非笔记内容\工作流程与系统运维\手机使用记录系统——手机端操作与维护指南.md","C:/Users/15345/.codex/skills/manage-pi-server/references/server-layout.md" -->

# 半小时行为解释系统——接管交接文档

> [!summary]
> 本文档供后续 AI Agent 接管此项目时使用。标记体系：**[已由旧对话确认]**、**[已由服务器核实]**、**[仅讨论过]**、**[当前无法确认]**。

## 1. 项目目标与总体架构

**[已由旧对话确认]**

用户（Conrad）建立一个**个人行为反馈中枢**，在树莓派上每半小时自动收集电脑与手机使用数据，清洗后交 AI 解释，通过 PushPlus 微信公众号发送短核验消息。当前阶段（第一至第三版）**只核验 AI 理解能力，不自动干预**。

总体数据流：

```text
电脑: ActivityWatch (Windows) ---> Syncthing ---> /home/conrad/workspace/activitywatch-sync/ (树莓派)
                                                           |
手机: Automate (Android) ---> HTTPS PUT ---> Tailscale Funnel ---> phone-usage-receiver.service (127.0.0.1:8765)
                                                           |
                                                    /home/conrad/phone_usage/archive/
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
           DeepSeek V4 Flash 第1次: semantic-segmenter (语义时间线)
                     |
           semantic_analysis.py (校验 + 计算工作-娱乐混杂指标)
                     |
           DeepSeek V4 Flash 第2次: half-hour-interpreter (解释与报告)
                     |
           ai_reports/ (JSON + Markdown)
                     |
           pushplus_client.py → 微信公众号
```

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
| PushPlus 回执 | `data/pushplus_receipts/YYYY-MM-DD/HH-MM.json` | pushplus_client.py | 微信推送状态 |
| 处理状态 | `data/state/processing-state.json` | run_half_hour.py | 最后一次成功处理的时段 |

## 4. 树莓派上相关目录、脚本、服务及运行状态

### 4.1 目录

**[已由服务器核实]**

| 路径 | 用途 |
|---|---|
| `/home/conrad/workspace/activitywatch-advisor/` | 行为解释系统主目录 |
| `.../src/` | Python 脚本（run_half_hour.py, computer_facts.py, phone_facts.py, tablet_facts.py, cross_device.py, deepseek_client.py, semantic_analysis.py, pushplus_client.py, common.py） |
| `.../prompts/` | half-hour-interpreter.md, semantic-segmenter.md |
| `.../config/settings.json` | 应用名映射、模型配置、阈值参数 |
| `.../data/` | 所有输出（见上表） |
| `.../tests/` | test_cleaning.py |
| `.../systemd/` | systemd unit 文件 |
| `/home/conrad/.config/activitywatch-advisor/env` | DeepSeek API 密钥（权限 600） |
| `/home/conrad/.config/activitywatch-advisor/pushplus.env` | PushPlus 用户令牌（权限 600） |
| `/home/conrad/phone_usage/` | 手机数据接收端（receiver.py, maintenance.py, token.txt） |

### 4.2 服务

**[已由服务器核实]**

| 服务 | 状态 | 说明 |
|---|---|---|
| `phone-usage-receiver.service` | active | 手机数据接收，监听 `127.0.0.1:8765` |
| `phone-usage-maintenance.timer` | active | 每日约 03:30 归档压缩/清理 |
| `activitywatch-advisor.timer` | active, enabled | 每半小时 08/38 分触发分析 |
| `activitywatch-advisor.service` | inactive (dead, triggered by timer) | 单次分析，完成后退出 |
| `syncthing@conrad.service` | active | 同步 ActivityWatch 数据 |
| `tailscaled.service` | active | Tailscale VPN + Funnel |
| `cockpit.socket` | active | Web 管理 9090 |
| `filebrowser.service` | active | 文件管理 8080 |

**[已由服务器核实]** 最新一次 systemd timer 触发：`2026-07-27 01:38`（已完成）。平板已全链路接入。

### 4.3 配置要点

**[已由服务器核实]**

- 模型：DeepSeek V4 Flash (`https://api.deepseek.com/chat/completions`)
- 计时器偏移到 `08` 和 `38` 分，为手机约 15 分钟上传留时间
- 语义切段使用非思考模式（`semantic_model.thinking = "disabled"`）
- 休息规则：电脑 AFK >= 3 分钟 **且** 所有已连接移动设备均无活动
- 娱乐偏离：工作中被 AI 判为娱乐且持续 > 30 秒
- 当前已连接设备：`computer`, `phone`, `tablet`（平板为辅助数据源）

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

## 7. 当前中断位置

**[已由服务器核实]**

- 上半轮（ChatGPT 会话）：额度耗尽中断
- 中断时正在处理："生成 PROJECT_STATE.md / DECISIONS.md / NEXT_STEPS.md"
- 上一个实时生成的报告：`2026-07-25 23:00—23:30`（23:38 完成并推送）
- 当前状态：`activitywatch-advisor.timer` 正在运行 `2026-07-26 00:08` 触发的服务（处理 23:30—00:00）
- 手机数据：`incoming/` 有 2026-07-25 的最后一轮上传（132KB foreground），但 `archive/2026-07-26/` 尚未创建（新一天的数据还未开始上传）

## 8. 尚未完成或尚未验证的事项

**[仅讨论过]** 但未执行：

- PROJECT_STATE.md / DECISIONS.md / NEXT_STEPS.md -- 未生成
- 全天归因分析 -- 仅讨论，未实施
- 与任务计划（OP）的对照 -- 仅讨论
- 替代信息流平台（树莓派信息过滤）-- 仅讨论
- 自动管控（Cold Turkey / 不做手机控联动）-- 仅讨论
- AI 维护提示词和 Skills -- 仅讨论

**[当前无法确认]** 的事项：

- 手机端 Automate 流是否仍然正常运行（需查看今天上新数据确认）
- DeepSeek API 密钥是否需要轮换（架构文档建议在部署后轮换）
- PushPlus 每日推送量是否有上限（大量夜间无活动时段也推送了）

## 9. 下一步最合理的操作顺序

**[建议顺序]**

1. **确认手机数据流**：等待 2026-07-26 第一个 15 分钟上传周期（约 00:15），确认 `archive/2026-07-26/` 目录被创建且包含数据
2. **确认定时器完成**：检查 `journalctl` 确认 00:08 触发的任务是否成功完成（包括 PushPlus 推送）
3. **生成 PROJECT_STATE.md / DECISIONS.md / NEXT_STEPS.md**：已完成（2026-07-27 更新）
4. **平板数据接入**：已完成（2026-07-27），包括接收端白名单、事实提取、三设备融合、AI prompt 适配
4. **观察数据质量**：积累 3-7 天完整数据后再做下一步改动
5. **夜间静默**：考虑在 00:00-07:00 间跳过 PushPlus 推送（当前所有时段都推送，包括无活动的凌晨）
6. **数据增长监控**：运行一周后计算真实日增长量，与预估的 1.4 MB/天对比
7. **API 密钥轮换**：在 DeepSeek 控制台生成新密钥，更新 `/home/conrad/.config/activitywatch-advisor/env`
8. **计划对照**：积累足够数据后，接入 OP 的任务计划进行计划-实际对照
9. **信息过滤平台**：在行为数据可靠后，建设树莓派上的替代信息供给系统

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
9. **推送是单向的**：微信公众号回复不会写回系统
10. **不要修改 `server-layout.md` 未经过验证的部分**
11. **Obsidian vault 路径**：`D:\mathblog\quartz\content`，项目文档应放在 `非笔记内容/工作流程与系统运维/`
12. **此文件是交接文档**：后续 Agent 接手时应先阅读此文件，再阅读 `server-layout.md` 和 `半小时行为解释系统——架构与维护.md`
