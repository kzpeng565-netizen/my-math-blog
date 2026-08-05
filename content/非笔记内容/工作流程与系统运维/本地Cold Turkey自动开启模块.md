# 本地 Cold Turkey 自动开启模块

<!-- ai_provenance: source=codex; date=2026-07-31; verification=checked; retrieved_notes="非笔记内容/工作流程与系统运维/PROJECT_STATE.md, 非笔记内容/工作流程与系统运维/PI_SERVER_HANDOFF.md, 非笔记内容/工作流程与系统运维/树莓派行为数据与接口索引.md" -->

## 模块定位

==本模块用于把树莓派半小时行为系统的“需要介入”判断落到 Windows 本地 Cold Turkey 封锁上。Pi 端只负责判断、归档和提供登录后 API；Windows agent 负责拉取请求、弹窗询问、执行 Cold Turkey、回传执行结果。==

设计边界：

- ==Pi 端不远程执行任意 Windows 命令。==
- ==Windows agent 只允许执行本地 allowlist 中的 Cold Turkey block。==
- ==当前 allowlist 只有 `常刷网站` 与 `bilibili`。==
- ==不要直接修改 Cold Turkey 内部数据库；第一版只使用官方命令行。==

## 文件位置

Windows 本地：

```text
D:\tools\computer-intervention-agent\agent.py
D:\tools\computer-intervention-agent\status_ui.py
D:\tools\computer-intervention-agent\config.json
D:\tools\computer-intervention-agent\run-agent.ps1
D:\tools\computer-intervention-agent\run-status-ui.ps1
D:\tools\computer-intervention-agent\state.json
```

Pi 项目：

```text
/home/conrad/workspace/activitywatch-advisor/src/computer_intervention.py
/home/conrad/workspace/activitywatch-advisor/src/run_half_hour.py
/home/conrad/workspace/activitywatch-advisor/src/web_app.py
/home/conrad/workspace/activitywatch-advisor/config/settings.json
/home/conrad/workspace/activitywatch-advisor/tests/test_computer_intervention.py
```

Pi 数据：

```text
/home/conrad/workspace/activitywatch-advisor/data/computer_interventions/requests/YYYY-MM-DD/<request_id>.json
/home/conrad/workspace/activitywatch-advisor/data/computer_interventions/responses/YYYY-MM-DD/*.json
/home/conrad/workspace/activitywatch-advisor/data/computer_interventions/state/windows-main.json
```

## 运行方式

当前 agent 是普通 Windows 后台进程，不是计划任务或服务。

启动：

```powershell
Start-Process -FilePath 'D:\anaconda\python.exe' `
  -ArgumentList 'D:\tools\computer-intervention-agent\agent.py' `
  -WorkingDirectory 'D:\tools\computer-intervention-agent' `
  -WindowStyle Hidden
```

检查：

```powershell
Get-CimInstance Win32_Process |
  Where-Object { $_.Name -in @('python.exe','python3.exe') -and $_.CommandLine -like '*computer-intervention-agent*' } |
  Select-Object ProcessId,CreationDate,CommandLine
```

桌面状态面板：

```text
C:\Users\15345\Desktop\Cold Turkey 自动开启状态.lnk
```

==双击该快捷方式会运行 `D:\tools\computer-intervention-agent\run-status-ui.ps1`，打开本地状态 UI。状态 UI 与介入弹窗使用同一套模块化简约设计：顶部判断卡、三张状态卡、下方信息模块、固定底部按钮。==

状态 UI 显示：

- ==真正的 `agent.py` 是否在运行；==
- ==Pi API 是否可登录访问、当前是否有 pending request；==
- ==上一次 request 的 `decision`、时间和拒绝计数变化；==
- ==上一次 Cold Turkey 执行结果；==
- ==agent 本地估计的 active lock 状态。==

状态 UI 按钮：

- ==“启动 agent”：如果没有运行中的 `agent.py`，尝试启动后台 agent；==
- ==“刷新”：重新读取本地 `state.json`、进程和 Pi API；==
- ==“关闭”：只关闭状态 UI，不关闭后台 agent。==

停止：

```powershell
Get-CimInstance Win32_Process |
  Where-Object { $_.Name -in @('python.exe','python3.exe') -and $_.CommandLine -like '*computer-intervention-agent*' } |
  ForEach-Object { Stop-Process -Id $_.ProcessId }
```

注意：

- ==`config.json` 里可能有 Next Action Web 登录密码，不要复制到文档、仓库或对话中。==
- ==重启 Windows 或注销用户后，当前进程不会自动恢复。后续应补 Windows 计划任务。==
- ==状态 UI 不会触发 Cold Turkey 封锁；只有后台 agent 收到介入 request 并经用户确认/强制逻辑后才会执行。==

## 工作流程

```text
半小时 timer
  -> run_half_hour.py 生成 intervention_candidate
  -> computer_intervention.py 生成 request
  -> web_app.py 暴露 pending API
  -> Windows agent 拉取 pending
  -> 先回传 ack
  -> 弹窗询问/或第三次强制
  -> 调 Cold Turkey
  -> 回传 final receipt
```

API：

```text
GET  /api/computer-interventions/pending?computer_id=windows-main
POST /api/computer-interventions/ack
POST /api/computer-interventions/response
```

这些 API 复用 Next Action Web 登录保护；未登录访问应返回 401。

## 规则

### 触发

==半小时影子候选 `would_intervene=true` 且本次运行不是 `--no-push` 时，Pi 会生成电脑端介入请求。==

电脑是否有 ActivityWatch 活动不阻止请求生成：如果是手机或平板沉迷，也可以触发电脑端 Cold Turkey 封锁。

### block

当前 Windows allowlist：

```json
{
  "常刷网站": {
    "cold_turkey_block": "常刷网站",
    "display_name": "常刷网站",
    "default_lock_minutes": 30
  },
  "bilibili": {
    "cold_turkey_block": "bilibili",
    "display_name": "bilibili",
    "default_lock_minutes": 30
  }
}
```

Cold Turkey 命令：

```powershell
& 'D:\Cold Turkey\Cold Turkey Blocker.exe' -start '<block>' -lock 30
```

### B 站例外

`bilibili` 在以下时间不执行封锁：

```text
周六全天
周日全天
周一 00:00-12:00 Asia/Shanghai
```

例外时目标会在 request 里保留，但 `enabled=false`，回执应显示 skipped/exempt，不计入拒绝。

### 拒绝与强制

- ==点击“暂不介入”：当前 request 完成，`decline_streak += 1`。==
- ==弹窗超时或无法显示：返回 `ignored`，当前 request 完成，但不累计拒绝。==
- ==连续两次“不介入”后，第三次仍触发时强制执行 30 分钟。==
- ==封锁成功、强制封锁成功、agent 判断已经处于本地估计封锁状态、或观察到恢复，会重置拒绝计数。==

恢复条件：

```text
meaningful_minutes >= 20
confirmed_rest_minutes >= 10
episode_reset_minutes >= 90
```

## 弹窗 UI

当前弹窗是 Tkinter 实现的模块化简约界面：

- 高 DPI aware；
- 顶部判断卡；
- 三张观察值卡；
- 触发原因模块；
- 将处理的 block 模块；
- 中间内容可滚动；
- 底部按钮固定可见；
- 倒计时提示“未响应将按暂不介入处理，但不累计拒绝”；
- 目标 block 名使用 `display_name` 兜底，避免中文显示为 `????`。

测试 UI 时不要通过真实 pending request 触发，可临时 import `agent.py` 调用 `ask_user()`；测试数据建议使用 Unicode escape，避免 PowerShell 管道造成中文编码污染。

状态面板也是 Tkinter 实现，但不复用 `ask_user()`。它只做只读状态展示和启动 agent，不执行 Cold Turkey。

## 回执解读

最终回执示例：

```json
{
  "computer_id": "windows-main",
  "request_id": "2026-07-31-13-00_13-30",
  "agent_version": "0.1",
  "status": "final",
  "final": true,
  "decision": "accepted",
  "decline_streak_before": 0,
  "decline_streak_after": 0,
  "executions": [
    {
      "block": "常刷网站",
      "cold_turkey_block": "常刷网站",
      "action": "cold_turkey_start_lock",
      "lock_minutes": 30,
      "exit_code": 0,
      "status": "success"
    }
  ]
}
```

`decision` 常见值：

```text
accepted
declined
ignored
forced
already_locked
skipped
```

`status=success` 表示命令被 agent 认为成功提交给 Cold Turkey。第一版不保证能从 Cold Turkey 官方接口反查“真实封锁状态”。

## 验证记录

2026-07-31 已验证：

- ==`python3 -m unittest tests.test_computer_intervention -v`：3 OK。==
- ==`python3 -m unittest discover -s tests -v`：93 OK。==
- ==`activitywatch-advisor-web.service`：active。==
- ==未登录访问新 API：401。==
- ==真实请求 `2026-07-31-13-00_13-30`：用户选择 `accepted`，`常刷网站` 与 `bilibili` 均返回 `status=success`，拒绝计数重置为 0。==
- ==本地 agent 当前可用进程形态：`D:\anaconda\python.exe D:\tools\computer-intervention-agent\agent.py`。==
- ==桌面快捷方式 `Cold Turkey 自动开启状态.lnk` 已创建，可打开状态 UI。==
- ==`status_ui.py` 语法检查通过，并能显示运行状态、Pi 连接、上次执行和当前估计封锁。==

## 常见排障

### 没弹窗

先查 agent 是否在跑：

```powershell
Get-CimInstance Win32_Process |
  Where-Object { $_.Name -in @('python.exe','python3.exe') -and $_.CommandLine -like '*computer-intervention-agent*' }
```

再查 Pi 是否有 pending request：

```bash
cd /home/conrad/workspace/activitywatch-advisor
find data/computer_interventions/requests -type f | sort | tail
find data/computer_interventions/responses -type f | sort | tail
```

### agent 启动后立刻退出

常见原因：

- `config.json` 没有登录密码；
- `NEXT_ACTION_WEB_PASSWORD` 未设置；
- Next Action Web 不可达；
- Python/Tkinter 异常。

### Pi 上 `last_seen_at` 很旧

当前没有独立心跳。只有 agent 提交 ack/final 时，Pi 端状态才会更新。判断实时在线应以 Windows 本机进程为准。

### 中文显示异常

优先检查：

- `agent.py` 是否仍是 UTF-8；
- `config.json` 中 `display_name` 是否正确；
- 测试脚本是否通过 PowerShell 管道传递了中文字符串。

### Cold Turkey 没有封锁

检查：

- block 名是否与 Cold Turkey GUI 中完全一致；
- `D:\Cold Turkey\Cold Turkey Blocker.exe` 是否存在；
- 回执中的 `exit_code` 和 `output_excerpt`；
- 当前是否处在 B 站例外时段。

## 后续改进

1. ==做 Windows 计划任务或服务，用户登录后自动启动 agent。==
2. ==新增 heartbeat API，让 Pi 能判断 agent 在线，而不是只靠 ack/final。==
3. ==给 agent 增加本地日志文件，便于排查登录失败、网络失败、Tk 弹窗异常。==
4. ==研究 Cold Turkey 是否有官方状态读取方式；没有则继续只使用命令返回值和本地估计状态。==
5. ==观察 3-7 天误触发，尤其是 B 站备课例外、手机沉迷触发电脑封锁、忽略不累计拒绝这三类边界。==
