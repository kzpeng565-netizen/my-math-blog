# New Pomodoro Timer：代码结构与交接

> 当前插件版本：`1.2.3-focus-garden.8`  
> 插件目录：`.obsidian/plugins/new-pomodoro-timer/`  
> 主要运行文件：`main.js`（esbuild 打包产物）、`styles.css`、`manifest.json`、`data.json`

## 1. 先记住的总原则

==Pi Focus Garden 的 SQLite 会话是云端专注状态的唯一权威；New Pomodoro Timer 只是 Obsidian 端的计时显示器和操作入口。插件可以启动、暂停、恢复并读取会话，但不能用本地旧状态覆盖 Pi。Obsidian Markdown 仍由 Obsidian/Context Sync 写回，Pi 不直接写 Markdown。==

## 2. 文件与模块分层

### `manifest.json`

插件身份、版本和 Obsidian 最低版本。修改插件代码后通常要递增版本号并重载插件，避免 Obsidian 继续使用旧的缓存产物。

### `data.json`

Obsidian 本机持久化设置，由 `PomodoroSettings` 读取并与 `DEFAULT_SETTINGS` 合并。它不是 Pi 会话数据库，也不是跨设备同步源。

当前观察到的持久化设置包括：Work `5`、Break `7`、Focus Garden 已启用、Pi 地址为 `https://pi.taild4d3f7.ts.net:8460`。Work/Break 的实际选择应以面板控件和当前插件设置为准；如果旧值不在新预设中，面板会显示安全默认值，用户可重新选择保存。

### `styles.css`

负责 Focus Garden 同款纸张、绿色边框、表盘、按钮、移动端布局，以及 Work/Break 时长选择控件的视觉样式。它不参与计时和云端状态判断。

### `main.js` 的主要模块

这是打包文件，顶部包含 Svelte/runtime 和第三方辅助代码；维护时重点看以下自定义模块：

| 模块 | 作用 |
| --- | --- |
| `PomodoroSettings` | 默认设置、`data.json` 读写、设置变更后调用 `timer.setupTimer()` |
| `Tasks` / `TaskTracker` | 解析 Tasks/Dataview 任务、当前任务、任务进度和 block ID |
| `TimerSettingsComponent` | 原有计时设置组件；Work/Break 输入的变更回调在这里处理 |
| `TimerViewComponent` | 原有 Svelte 表盘、按钮、任务列表和设置面板 |
| `TimerView` | 外层 Focus Garden 设计卡片、Work/Break 预设、锁定模式、刷新云端、暂停入口 |
| `Logger` | 将本地计时日志写入设置指定的 Obsidian 文件 |
| `Timer` | 本地计时状态机、表盘倒计时、暂停、结束、日志和 Pi 会话镜像 |
| `StatusBarComponent` | 状态栏计时显示及菜单 |
| `PomodoroTimerPlugin` | 插件生命周期、命令、Pi API 请求和 5 秒同步循环 |

## 3. 启动与同步时序

1. `PomodoroTimerPlugin.onload()` 读取设置，创建 `TaskTracker`、`Timer`、`Tasks`，注册计时视图和命令。
2. 插件加载后立即调用 `syncFocusGardenSession()`，随后每 5 秒调用一次。
3. 同步通过 Pi MagicDNS 地址访问 `GET /api/bootstrap`，把 `focus` 会话保存到 `plugin.focusGardenSession`，再派发 `focus-garden-session` 事件。
4. `Timer.hydrateFocusGardenSession()` 将 Pi 的 `running/paused/ends_at/paused_at/resume_at` 映射为本地表盘状态。暂停时以 `paused_at` 计算剩余时间，不能用当前时间继续扣减。
5. Pi 没有活动会话时，`clearFocusGardenSessionFromPi()` 停止本地表盘；插件销毁时只停止本地 renderer，不向 Pi 发送暂停或取消。

## 4. 启动、暂停、恢复和结束

### 启动 Work

`Timer.start()` 在 Work 且 Focus Garden 已启用时：

- 若已有 Pi 会话，调用 `POST /api/focus/resume`；
- 否则调用 `POST /api/focus/start`，提交 Work 时长、profile、锁定目标、关联任务 ID 和 `source: "obsidian"`；
- 成功后启动本地 clock worker。

Work 只能使用 Pi 接受的 `5/20/30/40/45/60` 分钟。默认设置是 40 分钟，但本机 `data.json` 的历史选择可能不同。

### 暂停 Work

暂停按钮和表盘数字在运行时都会进入 `Timer.pause()`：

1. 先读取 Pi 当前会话，防止本地显示过期；
2. 通过 Obsidian 原生 Modal 输入暂停分钟数；
3. 调用 `POST /api/focus/pause`；
4. 立刻用 Pi 返回值 hydrate 本地表盘；
5. 根据 `resume_at` 安排自动恢复；
6. 暂停期间解除锁定，恢复时重新开始计时和锁定。

一轮 Work 最多暂停一次，暂停后的成长按半轮处理，这是 Pi 端的业务规则；插件只负责传递操作和显示状态。

### Break

Break 是本地轮次状态。点击 `Break` 标签可以结束休息并自动开始下一轮 Work；点击 `Work` 标签不会跳过工作阶段。Break 可选 `0/5/10/15/20/30` 分钟，其中 `0` 表示跳过休息。

### 结束

Work 到时后由 `Timer.timeup()` 写日志、清理 Pi 会话，再根据 `autostart` 决定是否进入下一轮。不要把本地 `reset()` 当作云端取消入口；Focus Garden 活跃会话禁止本地重置，以免与 Pi 冲突。

## 5. UI 入口对应关系

- 表盘数字：空闲时启动，运行时进入暂停流程。
- `Work` / `Break` 状态文字：只有 Break 可跳过。
- Work 下拉框：`5/20/30/40/45/60`，默认显示 40。
- Break 下拉框：`0/5/10/15/20/30`。
- 锁定模式按钮：电脑＋手机、仅电脑、仅手机、仅计时。
- 网站 profile 按钮：深度专注或轻度专注。
- “刷新云端进度”：手动触发一次 `/api/bootstrap`。
- 暂停按钮：启动一次性暂停 Modal。

进行中的会话会禁用 Work/Break 时长选择，避免修改本地设置后误认为已经修改了 Pi 的当前会话。

## 6. 维护和排障顺序

1. 先看 Pi：`GET /api/bootstrap`、Focus Garden 服务和 SQLite 会话；Pi 状态优先于插件表盘。
2. 再看插件同步：确认 `focusGardenBaseUrl` 使用 `https://pi.taild4d3f7.ts.net:8460`，不要写固定 IP。
3. 再看本地状态：`focusGardenSession`、`Timer.state`、`paused_at/resume_at` 是否一致。
4. 修改 `main.js` 后运行 `node --check .obsidian/plugins/new-pomodoro-timer/main.js`，再递增 `manifest.json` 版本并重载插件。
5. 修改交互后同时更新本文件、`PROJECT_STATE.md`、`PI_SERVER_HANDOFF.md` 和 `我的专注花园/00-交接总览.md`；需要时把根目录交接文件镜像到 Pi。

## 7. 已知注意事项

- `main.js` 是打包产物，不能按源码目录结构直接推断原始项目；修改时应围绕上表中的模块和明确的字符串/方法定位。
- `data.json` 是单机设置，不应被用来判断 Pi 是否正在专注、是否暂停或是否已经获得奖励。
- 手机端后台心跳、Windows 锁机 agent、Pi API 和插件同步是四条不同链路；一个链路正常不代表其他链路必然正常。
- 任何涉及锁机、暂停、恢复和奖励的修复，都必须先确认 Pi 的权威会话，避免重复启动、重复解锁或重复结算。

<!-- ai_provenance: source=codex; date=2026-08-06; verification=local-verified; retrieved_notes=".obsidian/plugins/new-pomodoro-timer/main.js, styles.css, manifest.json, data.json" -->
