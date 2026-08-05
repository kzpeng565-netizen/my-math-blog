<!-- ai_provenance: updated=2026-07-27 -->
<!-- ai_provenance: source=codex; date=2026-07-26; verification=server-verified -->

# 半小时行为解释系统——NEXT_STEPS

> 本文档描述下一步工作计划，按优先级排列。状态：☐ 待开始 / ◐ 进行中 / ☑ 已完成。

<!-- ai_provenance: source=codex; date=2026-07-28; verification=server-verified; retrieved_notes="非笔记内容/工作流程与系统运维/PROJECT_STATE.md,非笔记内容/工作流程与系统运维/DECISIONS.md,非笔记内容/工作流程与系统运维/PI_SERVER_HANDOFF.md" -->

## 2026-07-28 当前接管清单

==本节取代下方早期条目中的过时状态；下方旧计划保留作为项目演进记录。==

### ☑ A1. Windows 只读上下文导出每 20 分钟更新

**[已由本机核实]**

==当前用户计划任务 `Behavior Context Exporter Timer` 已创建，使用 `D:\anaconda\pythonw.exe` 运行 `D:\mathblog\tools\behavior-context-exporter\behavior_context_exporter.py`，每 20 分钟更新 `C:\Users\15345\BehaviorContextSync`。手动启动测试返回 `LastTaskResult = 0`，下一次运行时间正常显示。==

原管理员安装脚本仍保留；若以后要重新安装原任务，以管理员身份打开 PowerShell，执行：

```powershell
& 'D:\mathblog\tools\behavior-context-exporter\scripts\install_exporter_task.ps1'
```

==注意：旧任务 `Behavior Context Exporter` 只靠 LogonTrigger 启动，曾出现安装后未进入重复链的问题；现在可靠周期由 `Behavior Context Exporter Timer` 承担。脚本自身带文件锁，重复运行不会破坏快照。==

### ☐ A2. 观察影子模式 3—7 天

**[系统已部署][需要用户核验]**

重点检查 PushPlus 半小时消息中的“影子判断”：

- 正常数学学习是否被误判为无主线或低效；
- 持续知乎/高刺激内容是否被识别；
- 合理休息是否保持静默；
- 推荐任务是否符合 Claudian 最近规划说明；
- 番茄钟缺失是否始终被视为不确定，而非负面证据；
- `last_known_good` 上下文是否避免产生强任务建议。

### ☐ A3. 检查日/周统计

**[定时器已部署][需要用户核验]**

- 日报：每天 09:00，统计前一天；
- 周报：每周一 09:05，统计上一自然周；
- 检查报告数、工作/娱乐/休息分钟、娱乐偏离和影子候选数量是否合理；
- 成功回执位于 `data/statistics/pushplus_receipts/`。

### ☑ A3.1 每日生活复盘 ntfy 推送

**[已由服务器核实]**

==`activitywatch-advisor-daily-life.timer` 已启用，每天 09:00 生成前一天每日生活复盘并通过 ntfy 推送。统计数字由脚本生成，DeepSeek V4 Pro 只负责建议层；成功回执位于 `data/statistics/ntfy_receipts/daily_life/`。2026-07-29 已对 2026-07-28 样例完成一次真实 ntfy 推送，并通过 systemd 手动启动验证防重复。==

### ☑ A3.2 15:00 任务进度 ntfy 提醒

**[已由服务器核实]**

==`afternoon-task-check.timer` 已启用，每天 15:00 读取 Obsidian 同步任务和番茄钟。若当天计划综合进度不到一半，则调用 DeepSeek V4 Flash 辅助判断是否发送提醒；模型失败时使用确定性规则兜底。回执位于 `data/statistics/ntfy_receipts/afternoon_task_check/`。2026-07-29 dry run 已验证：V4 Flash 返回 `should_send: true`，但因 `--no-push` 没有向手机发送。==

==2026-07-29 09:20 CST 已正式发送一次，ntfy 返回 `accepted`，message_id 为 `Tbg4g2XHqlSh`。当天 15:00 timer 会因已有成功回执而不重复发；后续自然日照常 15:00 检查。==

检查命令：

```bash
cd /home/conrad/workspace/activitywatch-advisor
systemctl status afternoon-task-check.timer --no-pager
systemctl list-timers afternoon-task-check.timer --no-pager
python3 src/afternoon_task_check.py --date 2026-07-29 --no-push --force
```

### ☑ A4. 完成无活动静默和 token 短路

**[已由服务器核实]**

==电脑没有非 AFK 活动且手机、平板均无当前亮屏证据时，不调用 DeepSeek、不发 PushPlus，但仍归档事实、上下文、本地报告、影子候选和统计。2026-07-28 已修复手机/平板旧亮屏状态跨时段外推：屏幕事件超过 2700 秒后转为 `unknown`；同一个前置静默结果同时控制 AI 和 PushPlus。凌晨 04:00—04:30 隔离回放已验证平板 `on_minutes: 0`、`unknown_minutes: 30`、`model: null`、`push_suppressed_for_inactivity: true`，全部归档存在。第五版完成后主项目现有49项测试通过。==

### ☐ A4.1 观察下一次真实夜间运行

**[代码与历史回放已完成][需要运行观察]**

==连续检查至少一个 02:00—08:00 夜间窗口，确认没有新的半小时 PushPlus 回执，同时日志返回 `push_suppressed_for_inactivity: true`。若平板产生新的真实亮屏事件，则该时段允许推送，不算误报。==

### ☑ A4.2 完成手机异常反馈接入

**[已由服务器核实][已由用户真实提交验收]**

==`phone-usage-receiver.service` 已增加 `POST /annotation`，手机 Automate 桌面快捷方式按表单协议提交 `category` 和 `message`。2026-07-28 19:40:45 与 19:40:58 两条真实手机反馈均返回 `201` 并保存到 raw JSON；`UNREVIEWED.md` 与当日 daily Markdown 已自动重建。==

核对位置：

```text
/home/conrad/workspace/activitywatch-advisor/data/user_annotations/raw/YYYY-MM-DD/*.json
/home/conrad/workspace/activitywatch-advisor/data/user_annotations/daily/YYYY-MM-DD.md
/home/conrad/workspace/activitywatch-advisor/data/user_annotations/UNREVIEWED.md
```

当前已知 Git 状态：

```text
6462485 feat: add phone annotation intake and review logs
```

==注意：该提交只包含手机异常反馈接入和当时的文档/测试。静默修复与第五版标签/成本改造仍是远端工作区未提交改动；当前为9个修改文件和2个新增文件，后续提交前必须逐项检查，不要混入无关改动。==

### ☐ A4.3 设计人工反馈处理流程

**[数据入口已完成][处理流程待设计]**

==第一版只记录人工标注，不提供网页处理界面，也不自动修改 `status`。后续若要处理反馈，应先设计显式流程：谁可以把记录从 `unreviewed` 改为 `reviewed`，是否写 review note，是否需要生成对 prompt/config 的候选修改，以及如何避免 AI 自动改 raw JSON。==

### ☐ A5. 完整版验收

进入正式有限提醒前必须确认：

1. `shadow_mode` 已连续运行至少 3 天；
2. 全设备无活动路径仍停止 AI 调用并继续归档；
3. 误报不会打断正常数学学习或合理休息；
4. 同类提醒冷却至少 60 分钟；
5. 每次只给一个可在 5—10 分钟内启动的动作；
6. 陈旧上下文和数据不足时不发强建议；
7. 正式提醒不得修改 Obsidian 任务。

### ☑ A6. 可配置事实标签与 DeepSeek 成本优化

**[已由服务器核实]**

==已部署统一40分钟标签事实层、程序锁定边界、候选单元压缩、第二次AI摘要输入和逐请求费用记录。49项测试通过；19:00与20:00两个隔离历史窗口完成真实DeepSeek回放。两窗平均约0.0095元，按48窗/日粗算约0.46元。==

后续只需观察和迭代规则：

```bash
cd /home/conrad/workspace/activitywatch-advisor
python3 src/fact_tagger.py --rules config/tag_rules.json
git diff -- config/tag_rules.json
```

Monaco Lite 中编辑 `/home/conrad/workspace/activitywatch-advisor/config/tag_rules.json`。每次只改一类识别规则，先校验，再用隔离输出目录回放一个已知窗口；不要直接修改历史正式报告。

### ◐ A7. 观察深夜 ntfy 提醒系统

<!-- ai_provenance: source=codex; date=2026-07-29; verification=server-verified; retrieved_notes="非笔记内容/工作流程与系统运维/ntfy提醒系统配置.md" -->

==`bedtime-reminder.timer` 已部署并启用，详见 [[ntfy提醒系统配置]]。2026-07-29 00:33 真实夜间调度已发送第一层，状态进入 `LEVEL_1_SENT`。后续需要观察完整 00:30—04:30 夜间窗口：确认第一层、5分钟复查、第二层最多3次、25分钟冷却和04:30重置是否都符合预期。==

检查命令：

```bash
cd /home/conrad/workspace/activitywatch-advisor
systemctl status bedtime-reminder.timer --no-pager
systemctl status bedtime-reminder.service --no-pager
journalctl -u bedtime-reminder.service --no-pager -n 100
cat data/state/bedtime-reminder-state.json
tail -n 50 data/bedtime_reminder/events.jsonl
```

==注意：这不是通用 AI 正式干预。`shadow_mode` 仍应保持 `true`；深夜提醒只做确定性的 ntfy 通知，不修改 Obsidian，不控制手机，不启用 Automate 弹窗。==

## 立即要做

### ☐ 1. 确认今天手机数据流正常

检查 `/home/conrad/phone_usage/archive/2026-07-26/` 是否已有数据文件。如果今天上午仍无数据，排查 Automate 流是否被系统杀死。

```bash
ssh pi.local "ls -lh /home/conrad/phone_usage/archive/2026-07-26/"
```

### ☐ 2. 验证 00:08 生成的报告质量

读取 `/home/conrad/workspace/activitywatch-advisor/data/ai_reports/2026-07-25/23-30.md`，确认 23:30—00:00 的核验报告合理。

### ✅ 14. 平板数据接入
平板已通过相同 Funnel 入口上传数据。接收端白名单增加 tablet_foreground/screen/heartbeat。phone_facts.py 增加 device 过滤，新建 tablet_facts.py。cross_device.py 支持三设备融合（平板为辅助数据源）。AI prompt 适配平板上下文。

### ✅ 15. 设备语义修正
平板亮屏不加入 any_device_interaction 和 minimum_evidence_seconds。休息判定只要求电脑 AFK + 手机熄屏，平板亮屏降低置信度但不否决。平板作为辅助数据源，仅在电脑和手机均无证据时作为低置信度 fallback。

## 短期（本周）

### ☐ 3. 观察数据质量 3-7 天

不修改任何系统配置，纯粹观察：
- 手机数据是否有连续缺失（心跳断 > 30 分钟）
- AI 语义时间线是否稳定（不会对相同行为给出不同解释）
- 休息判断是否准确
- 娱乐偏离检测是否合理

### ☑ 4. 无活动静默推送

==已实现为比固定夜间时段更准确的设备状态规则：电脑无非 AFK 活动且手机、平板无亮屏时跳过 AI 和 PushPlus，但仍生成全部归档。日报和周报移到白天。==

**验证结果**：真实无活动窗口已返回 `push_suppressed_for_inactivity: true`。

### ☐ 5. 数据增长确认

运行一周后计算 `data/` 目录真实日增长量，与预估的 1.4 MB/天对比。如大幅超出，排查是否某层数据异常膨胀。

### ☐ 6. DeepSeek API 密钥轮换

架构文档建议在部署验证后轮换密钥。在 DeepSeek 控制台生成新密钥，更新 `/home/conrad/.config/activitywatch-advisor/env`，重启 advisor：

```bash
sudo systemctl restart activitywatch-advisor.service
```

## 中期（2-4 周）

### ◐ 7. 日/周统计脚本

==已基于 `ai_reports`、`mixing_metrics`、影子候选和 PushPlus 回执实现只读聚合：==
- 每日工作/娱乐/休息总时长
- 娱乐偏离高发时段
- 最长连续工作时间
- 手机与电脑使用的时段分布

**不需要重新读取原始事件**，复用已保存的事实摘要即可。日报/周报已通过 systemd timer 和 PushPlus 实际验证。

仍待扩展：娱乐偏离高发时段、跨日最长连续工作以及更长历史趋势。

### ☑ 8. 接入只读 Obsidian 任务上下文

==已改为不要求任务 ID 或额外标准 JSON：Windows 只读导出 Profile、已规划任务和番茄钟日志；树莓派校验、缓存、精简后只用于解释和影子建议。==

```text
计划：学习 Haar 测度 25 分钟
实际：Obsidian 12 分钟 + 浏览器 5 分钟 + 知乎 9 分钟
偏离：知乎浏览 9 分钟不在计划内
```

==Obsidian 仍是唯一任务权威源，树莓派不得回写或维护第二份任务状态。==

### ☐ 9. 报告查看页面

在 File Browser 可访问的 workspace 中生成静态 HTML 页面，显示最近几天的报告摘要和趋势图。或者用 Cockpit 的自定义页面。

==若实现报告查看页面，应一并显示 `data/user_annotations/UNREVIEWED.md` 或 raw JSON 列表，但第一版不要在网页里自动修改反馈状态。==

### ☐ 10. 手机应用名映射扩充

当前 `phone_app_names` 只映射了微信、QQ、哔哩哔哩等少量应用。在 `settings.json` 中增加更多常用应用（小红书、知乎、淘宝等）的包名到中文名的映射。

## 长期（1-3 月）

### ☐ 11. 信息过滤与替代内容平台

在树莓派上搭建一个低刺激信息供给系统，在被判断为"需要恢复但想获取刺激"时推送替代内容。这需要：
- 确定内容源（RSS、预选文章等）
- 设计输出格式（有限队列，非无限滚动）
- 与行为中枢的交互协议

### ☐ 12. 有限自动干预

在数据积累充分、AI 判断准确率足够高后，从"纯观察"升级为"有限干预"：
- 只启用少数干预动作（提醒当前任务、建议 5 分钟启动、建议开启屏蔽模式）
- 不直接控制 Cold Turkey 或不做手机控
- 每次干预记录结果，用于后续调整

### ☐ 13. AI 维护配置

让 AI 每周检查一次配置文件和提示词，提出修改建议。约束：
- 稳定原则（core_principles）不可自动修改
- 个人偏好（profile）可提议但需确认
- 每次修改需出 diff
- Git 管理所有配置变更

## 不做的事（明确排除）

- 让 AI 自由生成 Cold Turkey 阻止规则
- 读取聊天内容、通知正文、短信
- 记录屏幕截图或键盘输入
- 将数据上传到非树莓派的第三方服务
- 自动修改用户的任务计划
- 弹窗或强锁屏幕

## 维护检查清单

每周花 5 分钟检查：

1. `ssh pi.local` → `systemctl is-active phone-usage-receiver.service activitywatch-advisor.timer syncthing@conrad.service tailscaled.service`
2. `df -h /` → 磁盘是否低于 20%
3. `journalctl -u activitywatch-advisor.service --since "1 day ago" --no-pager | grep -c "completed"` → 应有 ~48 条
4. `journalctl -u phone-usage-receiver.service --since "1 hour ago" --no-pager | grep "PUT"` → 应有最近上传记录
5. `ls /home/conrad/phone_usage/archive/$(date +%F)/` → 当天三个 JSONL 文件存在且非空
6. 查看最近一条 PushPlus 微信消息 → 内容合理
7. ==`journalctl -u phone-usage-receiver.service --since "1 hour ago" --no-pager | grep "/annotation"` → 若刚用手机反馈，应看到 `201`；`401/403` 说明 Authorization 头或 token 错误。==
8. ==`ls /home/conrad/workspace/activitywatch-advisor/data/user_annotations/daily/$(date +%F).md` → 若刚反馈，应看到当日 Markdown 更新时间刷新。==
## 2026-07-29 后续检查清单

### 系统维护超时提醒

- 观察 `sysadmin-time-guard.timer` 在进入 `COOLDOWN` 后是否只在连续 1 小时没有系统维护证据时重置。
- 如后续出现误报，优先查看 `data/sysadmin_time_guard/events.jsonl` 中的 `maintenance_source_seconds` 和 `context_bridge_items`，确认是直接命中还是邻近继承造成。
- 不要把浏览器重新加入 `context_bridge_apps`；普通网页、知乎、数学资料必须自行命中维护关键词才算维护。
- 如数学学习中的 ChatGPT 被误计，先补充 `non_maintenance_title_keywords`，再跑 `tests.test_sysadmin_time_guard`。

### 半小时提醒检测系统

- 保持正式名称为“半小时提醒检测系统”，不要在对外文档中称为“影子提醒”。
- 确认 ntfy 只在 `would_intervene=true` 时发送；`would_intervene=false`、`--no-push`、全设备无活动静默都只能写 skipped 回执。
- 常用验证：

```bash
cd /home/conrad/workspace/activitywatch-advisor
python3 -m unittest tests.test_sysadmin_time_guard -v
python3 -m unittest tests.test_half_hour_reminder_check_ntfy -v
journalctl -u sysadmin-time-guard.service --since "1 hour ago" --no-pager
```
## 2026-07-29：Next Action Web 试用事项

1. 将 `https://pi.taild4d3f7.ts.net:8450` 添加到手机桌面。
2. 连续试用“下一步”建议，重点观察它是否真的能说服自己开始行动。
3. “换一个”和“现在不做”时尽量填写原因和一句具体描述，方便之后分析失败原因。
4. 暂时不要做自动执行观察；第一版只记录用户手动执行结果。
5. 一到两周后再评估是否加入弱执行观察，例如对下一份半小时报告做低置信关联。
6. 检查 09:00/10:00/11:00 睡眠边界重试是否符合真实起床情况。
7. 若网页反馈入口足够顺手，再考虑为 `UNREVIEWED.md` 做 review/status 更新界面。
8. 修改建议 prompt 时必须保留三条硬约束：只从当天任务中选工作行动、不回写 Obsidian、不自动干预。
## 2026-07-29：Next Action v1.1 试用事项

1. 午间 12:00-13:00 试一次“下一步”，确认系统推荐吃饭/午休而不是学习。
2. 观察建议是否更能让自己开始行动，而不是只讲正确道理。
3. 检查番茄钟措辞：应是“预估还剩”“记录显示接近收尾”，不能是“只剩一个番茄即可完成”；必须明确本系统 `1 🍅 = 40 分钟`，不能把 15/25/30 分钟启动片段说成一个番茄。
4. 暂时不解决大任务标题粒度问题；如果仍明显复读标题，后续再考虑给任务增加 `next_step`。
## 2026-07-30 后续事项：问题反馈与 skill 使用

### 待观察：从手机提交一条真实问题反馈

在手机打开 Next Action Web，登录后进入“问题反馈”，提交一条真实或半真实问题，确认：

- 页面提示提交成功；
- 最近问题列表能看到该条；
- 树莓派生成 `data/issue_feedback/raw/YYYY-MM-DD/*.json`；
- `data/issue_feedback/UNREVIEWED.md` 自动更新。

### 待处理：之后统一处理问题反馈 backlog

当积累了若干条问题后，可以直接对 Codex 说：

```text
使用 pi-ops-system-context，处理 Next Action 网页问题反馈 backlog
```

Codex 应从以下文件开始：

```text
/home/conrad/workspace/activitywatch-advisor/data/issue_feedback/UNREVIEWED.md
```

处理顺序建议：

1. 先按分类和严重程度聚合问题。
2. 区分数据错误、模型提示词问题、规则不匹配、网页交互问题和通知问题。
3. 对每一类提出最小修复方案。
4. 只修改必要代码/配置/文档。
5. 测试通过后再更新 `PROJECT_STATE`、`DECISIONS`、`NEXT_STEPS`、`PI_SERVER_HANDOFF`。

### 待观察：新 skill 是否足够“听得懂”

后续每次涉及树莓派行为顾问系统、Next Action、半小时报告、Automate 上传、Funnel、问题反馈、Obsidian context 或番茄钟规则时，优先让 Codex 使用：

```text
pi-ops-system-context
```

如果 Codex 仍然需要反复问系统架构，说明 skill 的 reading routes 或 service map 还需要继续补。

## 2026-07-31 后续事项：本地 Cold Turkey 自动开启模块

### ☑ 已完成：第一版介入链路

==Pi 端已经能在半小时影子候选 `would_intervene=true` 时生成 `data/computer_interventions/requests/YYYY-MM-DD/<request_id>.json`；Windows agent 能拉取 pending request、回传 ack、弹窗询问、调用 Cold Turkey，并写回 final receipt。==

==当前已实测一条真实请求：`2026-07-31-13-00_13-30`。用户选择 `accepted` 后，agent 对 `常刷网站` 和 `bilibili` 执行 `-start <block> -lock 30`，返回 `status=success`，并把 `decline_streak` 重置为 0。==

### ◐ 待完成：持久化启动

==当前 agent 是普通后台进程，不是 Windows 计划任务或服务。后续应建立一个用户登录后启动的计划任务，命令建议为：==

```powershell
D:\anaconda\python.exe D:\tools\computer-intervention-agent\agent.py
```

==计划任务不要在文档中写入 Next Action Web 密码。密码应继续保存在本地 agent 的私有配置或用户环境变量中。==

### ☐ 待完成：健康检查与心跳

==Pi 端 `data/computer_interventions/state/windows-main.json` 目前只在 agent ack/final 时更新；没有 pending request 时不会刷新 `last_seen_at`。后续可以新增 `/api/computer-interventions/heartbeat`，让 agent 每 5 分钟回报在线、版本、当前 active lock 估计和最近错误。==

### ☐ 待观察：误触发与 B 站例外

==连续观察 3-7 天：确认“手机沉迷但电脑无活动”时仍能按预期封锁电脑；确认周六、周日、周一上午 B 站备课窗口不会执行 `bilibili` block；确认 `ignored` 不累计拒绝，但会完成当前请求。==

### ☐ 待评估：Cold Turkey 当前状态可验证性

==第一版只能根据命令返回值和 agent 本地 `active_locks` 估计封锁状态。若后续发现手动开启 block、重复启动 block 或 Cold Turkey 异常时状态不准，再研究是否存在安全可靠的官方状态读取方式；不要直接写 Cold Turkey 内部 SQLite。==

<!-- ai_provenance: source=codex; date=2026-07-31; verification=checked; retrieved_notes="非笔记内容/工作流程与系统运维/NEXT_STEPS.md" -->

## 2026-08-02 后续事项：我的专注花园

### ☑ 已完成：第一版本地游戏

==已完成本地 SQLite 奖励账本、树莓派只读同步、Cold Turkey 专注入口、40 分钟累计奖励、20 种植物注册、随机种植、`5×5` 自动扩园、日/周/月/年筛选、奖励原因记录和桌面快捷方式。==

### ☐ 待用户验收：第一次真实专注

==在确定可以接受网站被锁定时，从正式桌面快捷方式启动游戏，先选择 10 分钟，确认 `常刷网站` 与 `bilibili` block 按预期执行；开发期间不要使用正式入口测试。==

### ☐ 第二版：替换原创素材

==保持 `config/plants.json` 的植物 ID 稳定，逐步用原创透明 PNG 替换 `static/assets/plants/` 中的本地贴图，并在全部替换后移除本地素材限制说明。==

### ☐ 后续观察：早睡规则与 AI 闭环

==观察手机最后活动能否代表真实早睡；如误差明显，再加入电脑最后活动作为交叉条件。继续检查 Next Action response/outcome 是否能稳定通过同一 `suggestion_id` 形成闭环。==

<!-- ai_provenance: source=codex; date=2026-08-02; verification=checked; retrieved_notes="非笔记内容/工作流程与系统运维/NEXT_STEPS.md" -->

## 2026-08-03 后续事项：我的专注花园交接后

### ☑ 已完成：专题交接与当前版本核验

==已新建 [[我的专注花园/00-交接总览]] 及数据、架构、优化、运维四份专题文档；已核验 35 种目录、5 株存档、0 份待种、服务健康、6 项测试通过和前端语法检查通过。==

### ☐ P0：建立代码与存档备份

==`D:\MyFocusGarden` 当前不是 Git 仓库。先建立本地可恢复备份；备份 SQLite 前停止游戏进程。若初始化 Git，先排除全部本机游戏贴图、草方块、数据库和日志。==

### ☐ P0：统一“封锁成功”的奖励口径

==Pi 主动介入规则当前是 `accepted` 且至少一个 execution 成功；本地专注则要求所有目标未失败。需决定主动介入是否也要求全部目标成功，并补回归测试。==

### ☐ P1：增量同步与规则配置化

==当前每次同步会经 SSH 扫描全部历史 JSON。后续增加同步游标或 Pi 侧摘要，并把奖励规则的启用状态、阈值和版本从代码提取到配置。==

### ☐ P1：清理前端和数据库演进机制

==删除 `static/app.js` 中已被覆盖的旧版渲染函数，为 SQLite 增加 schema version 与迁移；同时让缺失静态资源返回 404，而不是回退到首页 HTML。==

==其余视觉、统计、可访问性和原创素材事项见 [[我的专注花园/03-后续优化空间]]。==

<!-- ai_provenance: source=codex; date=2026-08-03; verification=checked; retrieved_notes="非笔记内容/工作流程与系统运维/我的专注花园/03-后续优化空间.md" -->

## 2026-08-03 后续事项：我的专注花园 Pi 迁移后

### ☑ 已完成：私有部署与单向存档同步

==已完成 Pi systemd 部署、tailnet-only Tailscale Serve、SQLite 一致性快照、Pi send-only → Windows receive-only Syncthing，以及桌面入口切换。==

### ☐ P0：做一次停服恢复演练

==在不覆盖唯一副本的前提下，从 `D:\MyFocusGardenArchive` 或 `.stversions` 恢复到临时数据库，验证完整性、奖励数和花园显示；确认步骤后再考虑真实故障恢复。==

### ☐ P1：决定是否需要 Windows Cold Turkey 远程桥接

==Pi 网页目前明确使用安全模拟，不锁定 Windows 网站。若以后需要手机启动真实封锁，应设计最小权限的 Windows agent API，不允许 Pi 下发任意命令，也不能把现有页面直接改成公网接口。==

<!-- ai_provenance: source=codex; date=2026-08-03; verification=checked; retrieved_notes="非笔记内容/工作流程与系统运维/我的专注花园/03-后续优化空间.md,非笔记内容/工作流程与系统运维/我的专注花园/04-运维与扩展手册.md" -->

### ☑ P1：验收花园内的 Next Action 菜单（免密码）

==已完成源码比对、7 文件备份、部署、8 项 Python 测试、`focus-garden.service` 重启与 loopback 健康检查。2026-08-04 已取消 Next Action 密码，花园代理接口返回 200；后续可直接从 `:8460` 验收当前建议、生成、反馈、结果、三条报告与问题反馈。全过程保持 8838 loopback、8460 tailnet-only，禁止 Funnel。==

### ☑ P1：Next Action 免密码访问验收（已完成）

==2026-08-04 已撤除 `NEXT_ACTION_WEB_PASSWORD` 与公网 `:10000` Funnel。`activitywatch-advisor-web.service` 和 `focus-garden.service` 均 active；`127.0.0.1:8767/api/next-action/active` 与花园代理接口均返回 200。后续从 `:8460` 可直接验收生成、反馈和结果，不需要登录步骤，且不得重新启用公网 Funnel。==

<!-- ai_provenance: source=codex; date=2026-08-04; verification=checked; retrieved_notes="非笔记内容/工作流程与系统运维/NEXT_STEPS.md" -->

### ☐ P1：用一次真实的短暂停闭环复核自动恢复

==在正常专注中选择一次 1—3 分钟暂停，确认 Windows agent 的 Cold Turkey 会话停止、网页显示倒计时、截止后无需点击就恢复计时和锁定；再确认 session 标记为曾暂停且结算仅按半额。不要为了此项测试使用手机的不可逆硬锁。==

<!-- ai_provenance: source=codex; date=2026-08-05; verification=local-tests-and-pi-service-restart; retrieved_notes="非笔记内容/工作流程与系统运维/PROJECT_STATE.md" -->

### ☐ P1：日常验证一次“暂停—恢复—半额结算”

==选择仅电脑的 40 分钟专注，确认系统状态页先显示 Cold Turkey active；暂停一次并输入分钟数，确认其变为 idle；恢复后回到 active，完成后确认本轮只累积 20 分钟有效成长。不要在验证时选择手机锁定，因为当前暂停 release 只保证 Windows Cold Turkey lease。==

<!-- ai_provenance: source=codex; date=2026-08-05; verification=implementation-verified; retrieved_notes="非笔记内容/工作流程与系统运维/NEXT_STEPS.md" -->

## 2026-08-05 后续事项：健康面板与运行状态

### ☑ 已完成：系统状态真实健康面板

==花园已显示 Pi 服务、任务 queue、Obsidian 快照、同步检查、Windows/Android bridge、上下文缓存、最近报告和 SQLite 备份的新鲜度。Windows agent 已切换为计划任务启动并已成功发送 heartbeat。==

### ☐ 待观察：日常心跳与陈旧状态语义

==连续日常使用 3—7 天，确认 Windows heartbeat 在登录、休眠、网络中断和恢复后的显示符合实际；Android 超过 20 分钟、Windows 超过 12 分钟应显示 stale，而不能伪装为在线。==

### ☐ 待设计：统一 current_state 输入契约

==先盘点 Next Action 与半小时语义/影子介入的既有输入和输出，明确哪些确定性摘要可复用；未经确认前不替换 AI prompt、不增加自动干预，也不让任何状态文件成为第二个任务写入端。==

<!-- ai_provenance: source=codex; date=2026-08-05; verification=server-verified; retrieved_notes="非笔记内容/工作流程与系统运维/PI_SERVER_HANDOFF.md" -->

### ☑ P2：任务网页写回桥与 Next Action 实时任务上下文

==已部署并验收：Windows Syncthing 已恢复与 Pi 连通；新快照中的任务 ID 缺失数为 0；Pi Next Action 状态实测含上海时区当前时间和带 ID 的有效任务。花园的任务界面与 Pi loopback bridge 已启用。==

### ☐ P2：首个真实网页改动的闭环观察

==日常从花园新建或推迟一个非循环任务后，打开 Obsidian，确认插件在下一次同步中写回相应 Markdown、导出快照抵达 Pi、queue 归零。不要用循环任务或批量任务作为首测。==

<!-- ai_provenance: source=codex; date=2026-08-05; verification=server-verified; retrieved_notes="非笔记内容/任务计划/ToDo-已经规划好的任务.md" -->

<!-- ai_provenance: source=codex; date=2026-08-04; verification=checked; retrieved_notes="非笔记内容/工作流程与系统运维/我的专注花园/04-运维与扩展手册.md,非笔记内容/工作流程与系统运维/树莓派 Next Action Web架构.md" -->

### ☑ P0：启用电脑＋手机正式专注闭环

==已完成：Focus Garden 正式锁定已启用；Windows agent 已从退役的 `:10000` 迁至 tailnet-only `:8450`，并以免密码私有访问轮询到 `no_pending`；手机桥接 v1.0.0 心跳为 online。后续只需在日常使用中观察实际回执，不要为验收额外发起真实锁机。==

### ☐ P1：在真实使用后复核连续专注的轮间体验

==连续专注已实现为每轮分别启动锁机、休息不解锁。待完成至少一次非测试的多轮使用后，根据实际锁机持续时间与休息体验决定是否需要调整默认休息选项或增加只计时模式。==

### ☐ P1：解锁后验收 Focus Bridge 1.0.1 重试包

==Android v1.0.1 新包已编译；本次 USB `adb install -r` 在设备端一直等待 Package Manager 返回，尚未确认安装完成。待手机解锁、没有安装确认或 USB 调试弹窗时，只安装该包一次，然后以日常真实专注观察“锁屏开始后 30 秒重试”和手机通知，不要额外制造锁机测试。==


<!-- ai_provenance: source=codex; date=2026-08-04; verification=checked; retrieved_notes="非笔记内容/工作流程与系统运维/NEXT_STEPS.md" -->
