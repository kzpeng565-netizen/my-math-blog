<!-- ai_provenance: source=codex; date=2026-07-29; verification=server-verified; retrieved_notes="非笔记内容/工作流程与系统运维/PROJECT_STATE.md,非笔记内容/工作流程与系统运维/PI_SERVER_HANDOFF.md,非笔记内容/工作流程与系统运维/DECISIONS.md,非笔记内容/工作流程与系统运维/NEXT_STEPS.md" -->

# ntfy提醒系统配置

> 本文档交接树莓派上的 ntfy 提醒模块。目前包括“深夜设备使用提醒”和“15:00 任务进度提醒”。它们都不修改 Obsidian，不启用 Automate 弹窗、锁屏、语音或手机端网页。

## 当前状态

**[已由服务器核实，2026-07-29 00:36 CST]**

- `bedtime-reminder.timer`：`enabled` / `active`
- `bedtime-reminder.service`：最近一次运行 `Result=success`，`ExecMainStatus=0`
- 当前状态文件：`data/state/bedtime-reminder-state.json`
- 当前结构化日志：`data/bedtime_reminder/events.jsonl`
- 当前事件 ID：`bedtime-stop-2026-07-29`
- 00:33 已经由真实夜间调度发送第一层 ntfy 提醒，状态为 `LEVEL_1_SENT`
- ntfy 主题已经配置在树莓派私有文件 `/home/conrad/.config/activitywatch-advisor/ntfy.env`
- 真实主题不得写入 Git、Markdown 交接文档、README 示例或聊天摘要

==**[已由服务器核实，2026-07-29 01:10 CST]** 新增 `afternoon-task-check.timer`：每天 15:00 检查当天 Obsidian 规划任务完成度。如果已完成任务数量和番茄钟综合进度不到全天一半，则通过 ntfy 向手机发送高优先级提醒。判断层会调用 DeepSeek V4 Flash 辅助裁决；模型失败时退回确定性规则。==

==当前安装状态：`afternoon-task-check.timer` 为 `enabled` / `active`；`afternoon-task-check.service` 是 oneshot，未到时间前显示 `inactive (dead)` 是正常状态。2026-07-29 09:20 CST 已手动正式发送一次，ntfy 返回 `accepted`，message_id 为 `Tbg4g2XHqlSh`；因此当天 15:00 定时器会因已有成功回执而跳过重复发送。==

## 目标

只解决一个具体问题：

```text
凌晨 00:30 以后仍持续使用手机或电脑。
```

策略只在 `00:30` 到 `04:30` 使用 `Asia/Shanghai` 时区启用。04:30 后必须回到 `DISABLED`，清理当晚状态，不补发旧提醒，不影响白天使用。

## 文件位置

项目目录：

```bash
/home/conrad/workspace/activitywatch-advisor
```

核心文件：

| 文件 | 作用 |
|---|---|
| `config/bedtime_reminder.json` | `bedtime_stop` 策略配置 |
| `src/bedtime_reminder.py` | 状态机、触发判断、文件锁、状态持久化、JSONL 日志 |
| `src/notifications/base.py` | 通知结果类型 |
| `src/notifications/ntfy.py` | ntfy HTTP POST 发送器 |
| `tools/test_ntfy.py` | 复用正式模块的 ntfy 测试命令 |
| `src/afternoon_task_check.py` | ==15:00 任务进度检查：读取 Obsidian 同步快照、任务 Markdown 和番茄钟日志，必要时调用 DeepSeek V4 Flash 裁决并发送 ntfy== |
| `tests/test_afternoon_task_check.py` | ==任务进度解析与番茄钟兜底测试== |
| `tests/test_bedtime_reminder.py` | 状态机测试 |
| `systemd/afternoon-task-check.service` | ==15:00 任务进度检查 oneshot 服务模板== |
| `systemd/afternoon-task-check.timer` | ==每天 15:00 调度模板== |
| `systemd/bedtime-reminder.service` | oneshot systemd 服务模板 |
| `systemd/bedtime-reminder.timer` | 每分钟夜间调度模板 |
| `/etc/systemd/system/afternoon-task-check.service` | ==已安装的正式 systemd service== |
| `/etc/systemd/system/afternoon-task-check.timer` | ==已安装的正式 systemd timer== |
| `/etc/systemd/system/bedtime-reminder.service` | 已安装的正式 systemd service |
| `/etc/systemd/system/bedtime-reminder.timer` | 已安装的正式 systemd timer |
| `/home/conrad/.config/activitywatch-advisor/ntfy.env` | 私有 ntfy 配置，权限 600 |

## 私有环境配置

`ntfy.env` 格式如下。真实主题只保存在树莓派，不要复制进 Git：

```bash
NTFY_SERVER=https://ntfy.sh
NTFY_TOPIC=<手机订阅的随机长主题>
NTFY_ENABLED=true
NTFY_TIMEOUT_SECONDS=10
NOTIFICATION_PROVIDER=ntfy
NOTIFICATION_FALLBACK_PROVIDER=pushplus
NOTIFICATION_FALLBACK_ENABLED=false
```

权限检查：

```bash
stat -c '%a %U:%G %n' /home/conrad/.config/activitywatch-advisor/ntfy.env
```

预期：

```text
600 conrad:conrad /home/conrad/.config/activitywatch-advisor/ntfy.env
```

## 手机端设置

手机 ntfy 应用只需要订阅同一个私有主题。建议系统通知设置：

- 声音关闭
- 振动开启
- 顶部弹出开启
- 锁屏显示开启
- 高优先级通知通道设置为高重要程度
- 自启动开启
- 后台运行不限制

树莓派负责所有状态判断和升级逻辑；手机只显示通知。

## 状态机

```text
DISABLED
WAITING
LEVEL_1_SENT
LEVEL_2_ACTIVE
COOLDOWN
```

- `DISABLED`：不在 `00:30-04:30`，不发送提醒。
- `WAITING`：在有效窗口内，定期检查手机/电脑是否活跃。
- `LEVEL_1_SENT`：第一层已发送，等待 5 分钟后重新检查。
- `LEVEL_2_ACTIVE`：每次发送前重新检查；最多 3 次高优先级通知，每次间隔 1 分钟。
- `COOLDOWN`：第二层完成后冷却 25 分钟；冷却结束后重新检查，条件仍成立则从第一层重新开始。

04:30 到达时，任何状态都应转为 `DISABLED`。

## 触发判断

函数入口：

```python
should_trigger_bedtime_stop(settings, policy, now)
```

当前第一版没有可靠区分“工作/娱乐”，所以简化为：

```text
00:30-04:30 内，手机或电脑在最近窗口内仍有新鲜活跃证据。
```

复用现有事实层：

- 电脑：ActivityWatch `not-afk` 与前台窗口事实。
- 手机：`screen` / `foreground` / `heartbeat` 事实。
- 平板：暂不作为触发设备，避免平板长时间亮屏单独触发。

数据新鲜度：

```text
maximum_data_age_seconds = 120
```

如果电脑和手机数据都不新鲜，结果记为 `activity_data_stale`，不继续升级，只写日志。

## 通知内容和优先级

第一层：

```text
标题：已到停止使用时间
优先级：default
正文：
现在已经超过凌晨00:30，你仍在使用手机或电脑。
请在5分钟内完成收尾，准备休息。
```

第二层：

```text
标题：请停止当前使用
优先级：high
正文：
第一条提醒后你仍然在使用设备。
请立即结束当前工作或娱乐，准备休息。
```

注意：ntfy JSON API 内部使用数字优先级发送，模块对外仍保留 `default` / `high` 语义。

## 15:00 任务进度提醒

<!-- ai_provenance: source=codex; date=2026-07-29; verification=server-verified; retrieved_notes="非笔记内容/工作流程与系统运维/PROJECT_STATE.md,非笔记内容/工作流程与系统运维/PI_SERVER_HANDOFF.md,非笔记内容/工作流程与系统运维/DECISIONS.md,非笔记内容/工作流程与系统运维/NEXT_STEPS.md" -->

==目标：如果下午三点当天计划还没有完成一半，就向手机发一条克制的进度提醒。==

读取来源：

```text
/home/conrad/workspace/behavior-context-sync/context_snapshot.json
/home/conrad/workspace/behavior-context-sync/raw/ToDo-已经规划好的任务.md
/home/conrad/workspace/behavior-context-sync/raw/番茄钟log.md
```

判断口径：

- ==当天任务：`⏳ YYYY-MM-DD` 或 `📅 YYYY-MM-DD` 等于当天的 `#task`。==
- ==任务数量：`- [x]` 计为已完成，`- [ ]` 计为未完成。==
- ==番茄钟：优先使用任务行 `[🍅:: 已完成/总数]`；如果当天番茄钟日志更多，则用当天日志的 40 分钟等价量兜底。==
- ==综合进度：任务完成比例和番茄完成比例各占一半；可用证据不足时只使用可用比例。低于 0.5 时确定性规则认为应该提醒。==
- ==DeepSeek V4 Flash 会读取上述摘要并输出 JSON 裁决；如果 API 不可用、JSON 非法或超时，则使用确定性规则继续。==

发送内容：

```text
标题：下午任务进度提醒 YYYY-MM-DD
优先级：high
正文包含：综合进度百分比、已完成/未完成任务数、番茄钟进度、判断理由、下一步建议。
```

回执位置：

```text
data/statistics/ntfy_receipts/afternoon_task_check/YYYY-MM-DD.json
```

`--no-push` dry run 会写 `dry_run: true`，但不会阻止 15:00 正式检查；只有 `accepted` 或 `not_needed` 会被当作当天已完成检查。

## systemd 操作

查看：

```bash
systemctl status bedtime-reminder.timer --no-pager
systemctl status bedtime-reminder.service --no-pager
systemctl status afternoon-task-check.timer --no-pager
systemctl status afternoon-task-check.service --no-pager
systemctl list-timers bedtime-reminder.timer --no-pager
systemctl list-timers afternoon-task-check.timer --no-pager
journalctl -u bedtime-reminder.service --no-pager -n 100
journalctl -u afternoon-task-check.service --no-pager -n 100
```

启用或恢复：

```bash
cd /home/conrad/workspace/activitywatch-advisor
sudo cp systemd/bedtime-reminder.service /etc/systemd/system/
sudo cp systemd/bedtime-reminder.timer /etc/systemd/system/
sudo systemd-analyze verify /etc/systemd/system/bedtime-reminder.service /etc/systemd/system/bedtime-reminder.timer
sudo systemctl daemon-reload
sudo systemctl enable --now bedtime-reminder.timer
sudo cp systemd/afternoon-task-check.service /etc/systemd/system/
sudo cp systemd/afternoon-task-check.timer /etc/systemd/system/
sudo systemd-analyze verify /etc/systemd/system/afternoon-task-check.service /etc/systemd/system/afternoon-task-check.timer
sudo systemctl daemon-reload
sudo systemctl enable --now afternoon-task-check.timer
```

停止：

```bash
sudo systemctl disable --now bedtime-reminder.timer
sudo systemctl disable --now afternoon-task-check.timer
```

回滚 systemd：

```bash
sudo systemctl disable --now bedtime-reminder.timer
sudo systemctl disable --now afternoon-task-check.timer
sudo rm -f /etc/systemd/system/bedtime-reminder.service
sudo rm -f /etc/systemd/system/bedtime-reminder.timer
sudo rm -f /etc/systemd/system/afternoon-task-check.service
sudo rm -f /etc/systemd/system/afternoon-task-check.timer
sudo systemctl daemon-reload
```

清理运行状态：

```bash
cd /home/conrad/workspace/activitywatch-advisor
rm -f data/state/bedtime-reminder-state.json data/state/bedtime-reminder-state.lock
```

## 测试命令

单元测试：

```bash
cd /home/conrad/workspace/activitywatch-advisor
python3 -m unittest tests.test_bedtime_reminder -v
python3 -m unittest tests.test_afternoon_task_check -v
python3 -m unittest discover -s tests -v
```

ntfy 通道测试：

```bash
cd /home/conrad/workspace/activitywatch-advisor
set -a
. /home/conrad/.config/activitywatch-advisor/ntfy.env
set +a
python3 -m tools.test_ntfy --level 1
python3 -m tools.test_ntfy --level 2
```

15:00 任务进度 dry run：

```bash
cd /home/conrad/workspace/activitywatch-advisor
python3 src/afternoon_task_check.py --date 2026-07-29 --no-push --force
python3 src/afternoon_task_check.py --date 2026-07-29 --no-ai --no-push --force
```

加速状态机测试：

```bash
cd /home/conrad/workspace/activitywatch-advisor
BEDTIME_REMINDER_TEST_MODE=true python3 src/bedtime_reminder.py \
  --state /tmp/bedtime-test-state.json \
  --log /tmp/bedtime-test-events.jsonl \
  --now 2026-07-29T00:31:00+08:00 \
  --simulate-trigger active
```

## 已完成验证

**[已由服务器核实]**

- `python3 -m py_compile src/bedtime_reminder.py src/notifications/base.py src/notifications/ntfy.py tools/test_ntfy.py` 通过。
- `python3 -m unittest tests.test_bedtime_reminder -v`：6 项通过。
- `python3 -m unittest discover -s tests -v`：61 项通过。
- `python3 -m tools.test_ntfy --level 1`：返回 `accepted`，优先级 `default`。
- `python3 -m tools.test_ntfy --level 2`：返回 `accepted`，优先级 `high`。
- `bedtime-reminder.timer` 已启用并处于 active。
- 2026-07-29 00:33 真实夜间调度已发送第一层，状态进入 `LEVEL_1_SENT`。
- ==`afternoon-task-check.timer` 已启用并处于 active；`systemd-analyze verify` 通过，下一次触发为 `2026-07-29 15:00:00 CST`。==
- ==`python3 -m unittest tests.test_afternoon_task_check -v`：2 项通过。==
- ==`python3 src/afternoon_task_check.py --date 2026-07-29 --no-push --force`：DeepSeek V4 Flash 返回 `should_send: true`，估算费用约 0.000701 元；未发送手机通知。==
- ==`python3 src/afternoon_task_check.py --date 2026-07-29 --force`：2026-07-29 09:20 CST 正式发送成功，ntfy 返回 `accepted`，message_id 为 `Tbg4g2XHqlSh`。==

## DNS 修复记录

==2026-07-29 09:13 CST 首次正式发送失败：DeepSeek 与 ntfy 均报 `Temporary failure in name resolution`。原因是 Tailscale 接管 `/etc/resolv.conf` 后把 DNS 查询转给 DHCP/router DNS `192.168.0.252`，而该上游无响应。==

已执行修复：

```bash
sudo tailscale set --accept-dns=false
sudo nmcli connection modify 'netplan-eth0' ipv4.ignore-auto-dns yes ipv4.dns '8.8.8.8 223.5.5.5'
sudo nmcli connection up 'netplan-eth0'
```

当前预期：

```text
/etc/resolv.conf 由 NetworkManager 生成
nameserver 8.8.8.8
nameserver 223.5.5.5
```

验证：

```bash
getent hosts ntfy.sh
getent hosts api.deepseek.com
tailscale status --peers=false
```

Tailscale Funnel 仍显示 `https://pi.taild4d3f7.ts.net` 开启；该 DNS 修复不应影响手机上传入口。

定位 ntfy 400 时曾发过少量 ASCII 最小测试消息，不属于策略提醒。

## 日志与状态查看

```bash
cd /home/conrad/workspace/activitywatch-advisor
cat data/state/bedtime-reminder-state.json
tail -n 50 data/bedtime_reminder/events.jsonl
```

结构化日志字段包括：

```text
timestamp
policy_id
event_id
previous_state
new_state
reason
device_activity_summary
data_age
notification_level
notification_attempt
send_success
error
```

## 注意事项

- 不要把真实 `NTFY_TOPIC` 写入仓库。
- 不要让 PushPlus 和 ntfy 同时作为主通道发送同一条深夜提醒。
- 不要加入 Automate 覆盖弹窗、自动锁屏、语音播报或提示音。
- 不要把平板亮屏单独作为触发条件。
- 不要因为数据缺失或过期而补发大量通知。
- ==不要把 15:00 任务进度提醒做成修改 Obsidian 任务的自动化；它只读任务、番茄钟和快照，只发送通知和写 receipt。==
- ==不要把 `--no-push` dry run 的 `skipped` 回执当成当天已经检查完成；正式去重只认 `accepted` 或 `not_needed`。==
- `bedtime-reminder.service` 是 oneshot，运行成功后显示 `inactive (dead)` 是正常状态。
- ==`afternoon-task-check.service` 也是 oneshot；未到 15:00 前显示 `inactive (dead)` 是正常状态。==
- 半小时 AI 的 `shadow_mode` 仍然是另一套系统；通用行为建议干预仍未启用。

## 系统维护时间提醒

**[已由服务器核验，2026-07-29 09:54 CST]**

目标：当最近 30 分钟主要在做系统维护时，通过 ntfy 提醒切回数学学习或放松；当最近 60 分钟时间段里系统维护持续占据主要位置时，发送高优先级警告。提醒发送后，只有连续 1 小时没有系统维护证据，状态才会重置。

文件位置：

| 文件 | 作用 |
|---|---|
| `config/sysadmin_time_guard.json` | 系统维护判定关键词、30/60 分钟阈值、1 小时冷却、通知文案 |
| `src/sysadmin_time_guard.py` | 读取 ActivityWatch 最近 60 分钟电脑时间线，判定系统维护占比，维护状态机并发送 ntfy |
| `tests/test_sysadmin_time_guard.py` | 状态机、升级、冷却和关键词分类单元测试 |
| `systemd/sysadmin-time-guard.service` | oneshot 服务模板 |
| `systemd/sysadmin-time-guard.timer` | 每 5 分钟运行一次的 timer |
| `/etc/systemd/system/sysadmin-time-guard.service` | 已安装的正式 systemd service |
| `/etc/systemd/system/sysadmin-time-guard.timer` | 已安装的正式 systemd timer |
| `data/state/sysadmin-time-guard-state.json` | 正式状态文件 |
| `data/sysadmin_time_guard/events.jsonl` | 正式结构化日志 |
| `data/state/sysadmin-time-guard-dry-run-state.json` | `--no-push` dry run 状态文件 |
| `data/sysadmin_time_guard/dry-run-events.jsonl` | `--no-push` dry run 日志 |

当前安装状态：

- `sysadmin-time-guard.timer`：`enabled` / `active`
- `sysadmin-time-guard.service`：oneshot，手动运行成功后显示 `inactive (dead)` 是正常状态
- 2026-07-29 09:54 CST 手动正式运行一次，结果为 `no_action`，未发送 ntfy；当时最近 30 分钟系统维护占比约 25.5%，最近 60 分钟约 17.1%

判定口径：

- 直接读取 ActivityWatch 最近 60 分钟电脑前台时间线，不等待半小时行为解释归档。
- 系统维护证据包括终端、VS Code、树莓派/Cockpit/File Browser/Monaco Lite、systemd、journalctl、Tailscale、DNS、ntfy、activitywatch-advisor 等应用、域名或标题关键词。
- 标题中出现数学、作业、证明等关键词时，会优先排除为非系统维护。
- 数据过期时不补发提醒，只写日志。

阈值：

```text
30 分钟提醒：最近 30 分钟活跃时间中，系统维护占比 >= 75%
60 分钟警告：最近 60 分钟活跃时间中，系统维护占比 >= 65%，且首尾 10 分钟都有维护证据
冷却重置：连续 60 分钟没有系统维护证据
调度频率：每 5 分钟
```

常用命令：

```bash
cd /home/conrad/workspace/activitywatch-advisor
python3 -m unittest tests.test_sysadmin_time_guard -v
python3 -m py_compile src/sysadmin_time_guard.py
python3 src/sysadmin_time_guard.py --no-push
systemctl status sysadmin-time-guard.timer --no-pager
systemctl status sysadmin-time-guard.service --no-pager
systemctl list-timers sysadmin-time-guard.timer --no-pager
journalctl -u sysadmin-time-guard.service --no-pager -n 50
```