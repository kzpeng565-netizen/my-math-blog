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
