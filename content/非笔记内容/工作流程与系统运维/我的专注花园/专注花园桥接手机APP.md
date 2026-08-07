# 专注花园桥接手机 APP

<!-- ai_provenance: source=codex; date=2026-08-07; verification=device-plus-pi-multi-scenario-tested; retrieved_notes="非笔记内容/工作流程与系统运维/PI_SERVER_HANDOFF.md,非笔记内容/工作流程与系统运维/我的专注花园/00-交接总览.md,非笔记内容/工作流程与系统运维/我的专注花园/04-运维与扩展手册.md" -->

## 当前状态

- Android 包名：`com.conrad.focusbridge`
- ==已部署版本：`1.3.1 (16)`==
- Windows 开发目录：`D:\MyFocusGarden\focus-bridge-android`
- APK：`app\build\outputs\apk\debug\app-debug.apk`
- 修改前备份：`D:\MyFocusGarden\backups\20260807-lock-confirm-before\focus-bridge-android`
- Pi 权威服务：`/home/conrad/services/focus-garden`
- Pi 介入调度代码与状态：`/home/conrad/workspace/activitywatch-advisor`

==手机桥接已经完成通知确认、三次失败、30/20 分钟降级、15 分钟过期、熄屏等待与解锁恢复的多场景真机验收。成功不再以“点击已发出”为准，只有“不做手机控”真实 `getaway_pomo` 子通知出现后才回传 success。==

## 主要架构

```text
Pi intervention dispatcher
  ├─ offer / decision / execute / event
  │
  ▼
公网 HTTPS 固定白名单接口（主链路）
  └─ Tailnet :8460（仅 IOException 后备用）
  │
  ▼
BridgeForegroundService
  ├─ 15 秒 pending 轮询
  ├─ 5 分钟 heartbeat，失败后 1 分钟重试
  ├─ offer 状态机与锁屏检测
  ├─ 决定持久化和 15 秒提交重试
  ├─ execute final 结果持久化和 15 秒提交重试
  └─ START_STICKY、常驻通知、开机/升级恢复
  │
  ├─ offer ──► InterventionPromptActivity
  │             ├─ 接受
  │             ├─ 拒绝
  │             └─ 10 秒超时 ignored
  │
  └─ execute ─► FocusBridgeAccessibilityService
                ├─ 熄屏/锁屏时每秒等待，不消耗尝试
                ├─ 亮屏解锁后最多 3 次，每次确认窗口 20 秒
                └─ GetawayNotificationListenerService 确认真实计时通知
```

### 组件分工

`BridgeForegroundService` 是后台生命线。它负责心跳、轮询、offer 生命周期和可靠决定提交，不把后台存活交给 Automate 或“不做手机控”。

`FocusBridgeAccessibilityService` 只负责 Android 界面能力：从后台打开应用内选择页、启动“不做手机控”、查找目标窗口和执行已经校准的可见点击。

`InterventionPromptActivity` 是介入选择面。它不对其他应用导出，不允许点击外部或返回键绕过决定；显示接受、拒绝和整数秒倒计时。

`OfferStateMachine` 是无 Android 依赖的纯 Java 时间策略，便于离线测试锁屏、解锁、重新锁屏、超时和决定等待。

==`ExecutionAttemptPolicy` 管理熄屏等待、20 秒尝试窗口和三次失败；`LockDurationPolicy` 管理自动介入请求的时效：不足 8 分钟锁 30 分钟，8–15 分钟锁 20 分钟，满 15 分钟直接过期。手动专注和本地调试仍使用明确指定的时长。==

==`GetawayNotificationListenerService` 只读取系统已授权的活跃通知，过滤 `com.pl.getaway.getaway` 的 `getaway_pomo` channel，并排除 group summary。它不读取“不做手机控”的私有数据库；ADB 只用于开发验收，不属于运行链路。==

`BridgeApi` 固定先访问公网 HTTPS 桥接路径。公网失败且属于 I/O 异常时，才尝试 Tailnet 地址；因此 Android 上 Clash 与 Tailscale 的单 VPN 冲突不会成为心跳和执行的必需条件。

## 介入状态机

1. 收到 `mode=offer` 后记录 request ID、消息和首次发现时间。
2. 手机锁屏或屏幕不可交互时，不强行打开页面，继续每秒检查；总等待预算为 120 秒。
3. 手机可用时打开原生介入页，并给出完整 10 秒。
4. 页面期间重新锁屏，立即关闭页面并恢复等待；再次解锁时重新给出完整 10 秒。
5. 用户选择接受或拒绝后，先将决定持久化，再提交 Pi。
6. 页面 10 秒无操作或 120 秒仍无法展示时，提交 `ignored`。
7. 决定提交失败后每 15 秒重试。提交成功前，新的 `no_pending` 或新 offer 不得清除旧决定。
8. 接受后 Pi 生成 execute；该请求在服务端保留 16 分钟，使手机有机会在 15 分钟边界回传 expired。
9. 自动介入 execute 在首次实际尝试前按请求年龄选时长：`<8m → 30m`，`8m–<15m → 20m`，`≥15m → expired`。
10. 熄屏或锁定时每秒轮询且 attempts 保持 0；亮屏解锁后开始尝试，每次等待 20 秒真实通知，最多三次。
11. success、failed、expired 都先持久化，再向 Pi 提交 final event；提交失败每 15 秒重试，同一 request 在 final 前不会因重复轮询再次并行执行。

## 面对的难点与解决方案

### Android 后台被停止，心跳丢失

难点是无障碍服务不能单独被当成稳定调度器，厂商省电策略也可能结束普通后台任务。

解决方案是独立前台服务、持久通知、`START_STICKY`、开机和应用升级广播恢复。心跳与 pending 轮询都放在前台服务，无障碍服务连接变化只作为状态信号。

### Tailscale 与 Clash 不能同时占用 Android VPN

如果关键 API 只走 Tailnet，开启 Clash 后手机控制会中断。

解决方案是公网 HTTPS 固定白名单路径作为主链路，每台设备使用独立 Bearer token；`:8460` 只作网络异常备用。token 仅保存在应用私有目录与 Pi 私有配置，不进入文档或日志。

### 锁屏时不能可靠打开交互页面

Android 对后台 Activity 启动和锁屏界面有严格限制，短通知也来不及操作。

解决方案是用 `PowerManager.isInteractive()` 和 `KeyguardManager.isKeyguardLocked()` 判断可用性。锁屏时等待而不弹页；解锁后由已连接的无障碍服务打开应用内 Activity。总等待 2 分钟，避免请求永久悬挂。

### 选择时间太短

最初 5 秒实机使用仍偏短，并且 0.1 秒小数倒计时产生视觉噪声。

解决方案是延长为 10 秒，用向上取整的整数秒显示，例如 `10、9、8…`。选择页重新打开时获得新的完整窗口。

### 中文说明变成连续问号

实测中标题、按钮和日志中文都正常，只有测试请求正文变为问号，说明损坏发生在消息进入应用之前，而不是 Android 字体或 Activity 编码。

解决方案分两层：正常服务端请求继续按 UTF-8 JSON 传输；手机端检测说明中的高比例连续 `?` 或 `U+FFFD`，遇到已损坏文本时改用内置提示“是否让手机开始这次专注？”。

### 决定在网络失败时可能丢失

若用户已经点击，但 POST 暂时失败，后续 pending 返回空或出现新 offer，旧实现可能清除本地决定。

解决方案是将已选择决定设为最高优先级并持久化。提交成功前，轮询快照不能覆盖它；失败后继续重试，成功后才清理 offer。

### “接受”不能只停留在服务器记录

完整链路跨越 offer、decision、execute、Android UI 自动化和 final event，任意一段成功都不能代表整体成功。

解决方案是分段记录：Pi decision 文件证明接受；Android 私有日志证明尝试；通知监听证明真实计时；Pi response 文件证明 final event 已收妥。缺少真实计时通知时，即使点击手势完成也必须重试并最终报错。

### Android 进程可能在执行中重启

==真机熄屏测试中，前台服务曾在解锁后的尝试阶段被系统重建。当前执行对象不跨进程恢复，但 Pi 在收到 final 前持续保留请求；新实例重新轮询后会重新执行。final 结果在手机本地持久化，上传失败也不会丢失。因此恢复语义是“至少一次尝试、至多一次有效 final”，不是依赖单个 Android 进程一直存活。==

## 已完成验证

- `verify.ps1`：13 项介入状态机、8 项执行尝试策略、5 项时长策略检查通过。
- Gradle：离线 `clean assembleDebug` 通过。
- 安装：`1.3.1 (16)` 覆盖安装成功。
- 服务：前台服务、无障碍与通知使用权监听升级后均重新连接。
- 心跳：Pi 收到 `app_version=1.3.1`，公网 HTTPS、两项权限与两项连接状态全部通过。
- ignored：损坏说明测试显示正常中文，10 秒后提交 `ignored / prompt_timeout_10s`，Pi 队列清空。
- accepted：`bridge-accept-test-20260807T220244-f94ce3` 于 22:02:52 被 Pi 记录为 accepted。
- execute：22:03:04 手机开始 5 分钟正式流程；22:03:05 完成 `quick_pomodoro_confirmed_calibrated`；22:03:06 Pi 收到 final event。
- 用户确认“不做手机控”正确运行。
- 本地 5 分钟：第 1 次尝试约 2 秒出现真实通知并确认成功。
- 新鲜 30 分钟失败：三次尝试间隔均为 20 秒；随后手机日志、Pi final response 与花园红色错误卡同步出现。
- 9 分钟请求：自动降为 20 分钟，第 2 次尝试确认，花园恢复为“已确认 20 分钟”。
- 15 分钟请求：不启动“不做手机控”，回传 `expired / lock_request_expired_after_15_minutes`。
- 熄屏请求：花园显示 `waiting_screen / attempts=0`；解锁后才启动 30 分钟，并在 Android 服务重建后通过 Pi 重下发恢复、最终确认成功。

## 构建、安装与检查

```powershell
cd D:\MyFocusGarden\focus-bridge-android
.\verify.ps1
```

验证脚本只构建，不安装，也不修改 Pi。APK 生成后可用 Android SDK 的 `adb install -r` 覆盖安装。

手机端运行日志在应用私有目录 `files/focus-bridge.log`，界面中的“刷新运行日志”也能查看最近记录。正常接受流程应依次出现：

```text
收到介入选择
介入选择页面已弹出，等待 10 秒决定
介入决定待提交：accepted / prompt_accept
介入决定已提交
手机熄屏或锁定，持续等待亮屏解锁后启动锁机
开始 N 分钟正式流程，第 1/3 次尝试
流程完成：success / getaway_pomodoro_notification_confirmed
锁机执行结果已上传
```

## 运维边界

- Pi 上的 Focus Garden 生产树与 SQLite 才是权威最新版；Windows 花园目录不是部署权威。
- Android 源码目前保存在 Windows 开发目录，修改前先做日期备份。
- 不要让 Automate 或“不做手机控”承担桥接心跳、轮询或唤醒职责。
- 不要把 Focus Garden `:8460` 改为 Funnel；手机桥接公网只使用既有固定白名单路径。
- 不要在文档、日志或仓库中写入设备 token。
- 不要为了验收反复创建真实专注；锁屏等待场景后续在自然介入中观察即可。

## 仍需自然观察

- ==继续累计花园要求的 30 分钟连续后台观察证据；即时检查已经通过。==
- 日常开启 Clash 时继续观察公网主链路的心跳和自然执行回执。

## 2026-08-07：版本化迁移基线

==当前源码与构建已更新为 `1.3.1 (16)`，本地 Git tag 为 `focus-bridge-v1.3.1-build16`；可编辑源码 bundle 和经验证 APK 位于 `D:\PiClientMigration\releases\2026.08.07-r1\mobile\focus-bridge`。`verify.ps1` 已修正为从任意当前目录运行，依次完成 13 + 8 + 5 项策略检查和离线 Android 构建。==

==应用私有 token 与 SharedPreferences 不进入 Git 或 APK 旁的配置文件。换手机时安装后重新生成 token，再用 release 中的 `pair-focus-bridge.ps1` 经 ADB + SSH 直接更新 Pi；坐标与网格偏移必须在新屏幕上重新校准。完整步骤见 [[Pi系统手机端与电脑端迁移配置流程]]。==

<!-- ai_provenance: source=codex; date=2026-08-07; verification=local-build-and-bundle-verified; retrieved_notes="Focus Bridge Android source and release" -->
