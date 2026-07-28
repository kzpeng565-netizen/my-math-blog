<!-- ai_provenance: source=codex; date=2026-07-29; verification=server-verified; retrieved_notes="非笔记内容/工作流程与系统运维/PROJECT_STATE.md,非笔记内容/工作流程与系统运维/PI_SERVER_HANDOFF.md,非笔记内容/工作流程与系统运维/DECISIONS.md,非笔记内容/工作流程与系统运维/NEXT_STEPS.md" -->

# ntfy提醒系统配置

> 本文档交接树莓派上的“深夜设备使用提醒”模块。它是 `activitywatch-advisor` 项目下的独立确定性提醒策略，不属于半小时 AI 影子干预，也不启用 Automate 弹窗、锁屏、语音或手机端网页。

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
| `tests/test_bedtime_reminder.py` | 状态机测试 |
| `systemd/bedtime-reminder.service` | oneshot systemd 服务模板 |
| `systemd/bedtime-reminder.timer` | 每分钟夜间调度模板 |
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

## systemd 操作

查看：

```bash
systemctl status bedtime-reminder.timer --no-pager
systemctl status bedtime-reminder.service --no-pager
systemctl list-timers bedtime-reminder.timer --no-pager
journalctl -u bedtime-reminder.service --no-pager -n 100
```

启用或恢复：

```bash
cd /home/conrad/workspace/activitywatch-advisor
sudo cp systemd/bedtime-reminder.service /etc/systemd/system/
sudo cp systemd/bedtime-reminder.timer /etc/systemd/system/
sudo systemd-analyze verify /etc/systemd/system/bedtime-reminder.service /etc/systemd/system/bedtime-reminder.timer
sudo systemctl daemon-reload
sudo systemctl enable --now bedtime-reminder.timer
```

停止：

```bash
sudo systemctl disable --now bedtime-reminder.timer
```

回滚 systemd：

```bash
sudo systemctl disable --now bedtime-reminder.timer
sudo rm -f /etc/systemd/system/bedtime-reminder.service
sudo rm -f /etc/systemd/system/bedtime-reminder.timer
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
- `bedtime-reminder.service` 是 oneshot，运行成功后显示 `inactive (dead)` 是正常状态。
- 半小时 AI 的 `shadow_mode` 仍然是另一套系统；通用行为建议干预仍未启用。
