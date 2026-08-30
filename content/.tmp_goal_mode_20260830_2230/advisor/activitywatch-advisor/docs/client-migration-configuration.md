---
title: Pi系统手机端与电脑端迁移配置流程
date: 2026-08-07
updated: 2026-08-07
tags:
  - Raspberry Pi
  - Android
  - Windows
  - 迁移
  - 运维
---

# Pi系统手机端与电脑端迁移配置流程

> [!summary]
> 本文是更换手机、电脑或 Pi 时的客户端配置权威流程。源码保持可编辑，构建产物只用于快速恢复；密钥、用户数据和 Minecraft 来源素材不进入普通 Git 或公开发布链路。

## 1. 当前版本基线

| 组件 | 当前版本 | 可编辑源码 | 迁移备份 |
| --- | --- | --- | --- |
| Focus Bridge Android | `1.3.1 (16)` | `D:\MyFocusGarden\focus-bridge-android`，tag `focus-bridge-v1.3.1-build16` | `D:\PiClientMigration\releases\2026.08.07-r1\mobile\focus-bridge` |
| Windows Computer Intervention Agent | 2026-08-07 生产快照 | `D:\tools\computer-intervention-agent`，tag `computer-agent-production-2026-08-07` | 同一 release 的 `windows\computer-agent` |
| Behavior Context Exporter | 2026-08-07 生产快照 | `D:\mathblog\tools\behavior-context-exporter`，tag `behavior-context-exporter-production-2026-08-07` | 同一 release 的 `windows\behavior-context-exporter` |
| ActivityWatch → Pi | 当前 Vault 脚本 | `ActivityWatch树莓派同步/` | 同一 release 的 `windows\activitywatch-sync` |
| Windows 计划任务 | 6 个当前任务 | Windows Task Scheduler | 同一 release 的 `windows\scheduled-tasks`，仅作参考 |

==`D:\PiClientMigration\CURRENT.json` 是“新设备该用哪一版”的唯一指针。旧 release 不覆盖、不删除；创建新版时使用新的 release ID，并在验收通过后才更新 CURRENT。==

==该目录通过独立 Syncthing folder `pi-client-migration` 复制到 Pi：Windows 为 Send Only，Pi `/home/conrad/workspace/pi-client-migration` 为 Receive Only并保留 staggered 历史版本。这个副本仍是无密钥 release，不代替 Restic 私有备份。==

## 2. 三类配置必须分开

### 2.1 可以版本化的内容

- 源码、测试、Gradle wrapper、安装脚本；
- 不含真实密码的 `*.example.json` 与 `local.properties.example`；
- APK、Git bundle、计划任务 XML 参考副本；
- 版本号、Git commit、tag 和 SHA-256 清单。

### 2.2 只能进入加密私有备份的内容

- Pi 的上传 token、Focus Bridge 配对 token、通知/API 密钥；
- Windows SSH 私钥、Syncthing 配置和设备证书；
- `computer-intervention-agent/config.json`、ActivityWatch 数据库、Obsidian 内容；
- Automate 原始 flow：当前二进制内含实时上传 token；
- Focus Garden 的 Minecraft 来源素材和运行数据库。

### 2.3 在新设备重新生成更安全的内容

- Focus Bridge 安装后生成的设备 token；
- Tailscale 设备身份；
- Android 运行时状态、缓存、日志和 pending decision；
- Windows 计划任务中的用户 SID 与绝对路径。

==普通源码 release 不追求包含秘密。私有数据必须等 Restic 加密仓库配置完成后再纳入异机恢复链路；在此之前，不得用公开 Git、公开网站或普通共享目录代替。==

## 3. 更换手机的配置流程

### 3.1 安装基础应用

1. 登录同一 Tailnet 的 Tailscale；用于 `:8460` 私有备用链路和花园页面。
2. 安装 Automate，导入私有的 `Phone Usage Logger` flow。
3. 安装“不做手机控”，确认快速番茄页面仍可由无障碍服务打开。
4. 安装当前 Focus Bridge APK：`focus-bridge-1.3.1-build16-debug.apk`。

### 3.2 Focus Bridge 设置

1. 首次打开应用，使它创建 app-private token 和运行目录。
2. 允许通知、开机启动、前台服务，并把电池策略设为不限制。
3. 在系统设置中启用 Focus Bridge 无障碍服务和通知读取权限。
4. 地址保持 `https://pi.taild4d3f7.ts.net:8460`；公网 HTTPS 是主链路，`:8460` 是 Tailscale fallback。
5. 在应用内填写确认按钮 X/Y 和快速番茄网格 Y 偏移，先使用“校准点击”验证，不凭旧手机坐标硬套。
6. USB 调试连接后运行 release 内的 `pair-focus-bridge.ps1`。脚本用 `adb run-as` 读取 debug app 的私有 token，并直接通过 SSH 写入 Pi，不在终端打印 token。
7. 重开应用，确认常驻通知、15 秒轮询、5 分钟 heartbeat 和日志中的 `public_https` 或可解释的 `tailnet_fallback`。

> [!warning]
> 更换正式签名或安装不可调试 release APK 后，`adb run-as` 可能不可用。那时应增加应用内的一次性配对流程，不能把 token 固化进源码或文档。

### 3.3 Automate 设置

权威 flow 名为 `Phone Usage Logger`。当前私有二进制位于 `automate手机日志收集发送Flow`，其哈希已记录在客户端 release，但由于包含上传 token，没有复制到安全 release。

> [!danger]
> 截至 `2026.08.07-r1`，该 flow 没有可恢复的异机副本：哈希只能证明文件身份，不能恢复文件。旧手机和当前 Vault 同时损坏时，只能按本指南手工重建。必须在 Restic 加密仓库启用后补入带版本号的私有 `.flo` 导出。

导入后逐项核对：

- 本地目录为 `Documents/PhoneUsage/`；
- device 字段为 `phone`；
- 记录 foreground、screen 和 heartbeat 三类 JSONL；
- 上传目标使用 `https://pi.taild4d3f7.ts.net/upload/...`；
- 每 15 分钟上传，并携带与 Pi `/home/conrad/phone_usage/token.txt` 匹配的私有 token；
- 授予前台应用观察、文件、网络、通知和忽略电池限制权限；
- 不增加屏幕文字、截图、通知正文、位置或触摸轨迹采集。

==每次修改 flow 后，从 Automate 私下导出一个带日期/版本号的新副本，例如 `phone-usage-logger-2026.08.07-r2.flo`，放入加密私有备份；不得把含 token 的 flow 提交到普通 Git。==

### 3.4 手机端验收

- Pi `/health` 正常，phone incoming/archive 出现新日期数据；
- Focus Bridge heartbeat 显示新设备在线；
- 做一次 10 秒 `ignored` 测试和一次最短可接受流程；
- 日志出现 pending → decision → execution → final；
- 旧手机停用上传和 Bridge 后，再把新手机视为唯一手机写入端。

## 4. 更换电脑的配置流程

### 4.1 安装顺序

1. 安装 Git、Python、Tailscale、Syncthing、ActivityWatch 和 Cold Turkey。
2. 登录同一 Tailnet，验证 `ssh conrad@pi.taild4d3f7.ts.net true`。
3. 从加密私有备份恢复原 SSH 私钥，或生成新密钥并将新公钥加入 Pi；不要复制文档中的密码。
4. 运行 `D:\PiClientMigration\restore-current-release.ps1`，从 Git bundle 恢复三套可编辑源码。
5. 从 example 文件创建真实配置，确认后再安装计划任务。

### 4.2 必要配置文件

| 组件 | 真实配置 | 模板/备份 | 迁移处理 |
| --- | --- | --- | --- |
| Computer Agent | `D:\tools\computer-intervention-agent\config.json` | `config.example.json` | 保持 `api_base=https://pi.taild4d3f7.ts.net:8450`、`auth_required=false`、5 秒轮询；核对 Cold Turkey 路径和 allowlist |
| Behavior Context Exporter | `D:\mathblog\tools\behavior-context-exporter\behavior_context_exporter.json` | `behavior_context_exporter.example.json` | 按新 Vault 位置填写 6 个输入路径和 `export_dir` |
| Android 构建 | `focus-bridge-android\local.properties` | `local.properties.example` | 只填写新电脑 Android SDK 路径 |
| ActivityWatch | `%LOCALAPPDATA%\activitywatch\...\peewee-sqlite.v2.db` | 私有数据备份 | 停止 ActivityWatch 后恢复；不能提交 Git |
| Syncthing | `%LOCALAPPDATA%\Syncthing\config.xml` | 加密私有备份或重新配对 | 建议新设备重新配对并重建 folder type，不能复制到源码 release |
| SSH | `%USERPROFILE%\.ssh\config` 和私钥 | 加密私有备份 | 运行连接必须使用 MagicDNS；私钥 ACL 只允许当前用户、Administrators、SYSTEM |
| Pi Editor bypass | `%APPDATA%\pi-editor\` | release 的 `windows\pi-editor-bypass` | 核对新用户目录后恢复计划任务 |

### 4.3 计划任务

当前需要恢复并验收：

| 任务 | 触发方式 | 作用 |
| --- | --- | --- |
| `ActivityWatch Sync to Pi` | 每 5 分钟 | 生成 ActivityWatch 同步副本 |
| `Behavior Context Exporter` | 登录后，每 20 分钟 | 导出 Obsidian 行为上下文 |
| `Behavior Context Exporter Timer` | 每 20 分钟的旧兼容任务 | 与上一项重复时只保留经过验收的统一任务 |
| `ComputerInterventionAgent` | 用户登录 | 轮询并执行 Cold Turkey allowlist |
| `PiEditorTailscaleBypass` | 每 1 分钟 | 修复 Pi Editor 的 Tailscale bypass |
| `Syncthing for ActivityWatch` | 用户登录 | 启动 Windows Syncthing |

==release 中的 XML 是旧设备配置证据，不建议在新电脑直接无脑导入：其中含旧用户名、SID、Python 和程序路径。优先运行各源码仓库自带安装脚本，再用 XML 对照触发器、运行级别和电池策略。==

==也可以在核对路径后运行 release 的 `windows\scheduled-tasks\install-client-tasks.ps1`，一次建立 5 个规范任务。它有意不恢复重复的 `Behavior Context Exporter Timer`；脚本运行后仍需逐个检查 action、trigger 和最近结果。==

### 4.4 Syncthing 方向

- ActivityWatch：Windows Send Only，Pi Receive Only；
- Behavior Context：Windows Send Only，Pi Receive Only；
- Focus Garden archive：Pi Send Only，Windows Receive Only；
- Pi safe source：Pi Send Only，Windows `D:\PiSystemMigration` Receive Only；
- 任何数据库、任务 Markdown 或迁移源码都不能配置为双向多写。

## 5. 创建下一版客户端 release

### Android

1. 修改 `versionName`，并且每次安装包变化都递增 `versionCode`。
2. 运行 `verify.ps1`；它必须从任意工作目录都能完成 26 项策略检查和离线 `assembleDebug`。
3. 提交源码并创建 `focus-bridge-v<version>-build<code>` tag。
4. 新建 `D:\PiClientMigration\releases\<new-id>`，复制 APK，创建包含全部历史的 Git bundle。
5. 生成 `MANIFEST.sha256`，运行 `verify-release.ps1`，再更新 `CURRENT.json`。

### Windows

1. Agent 和 Exporter 分别提交到自己的本地 Git；真实配置、state、日志必须仍为 ignored。
2. 使用日期加修订号 tag，例如 `computer-agent-production-2026-08-08-r2`。
3. 创建新的 Git bundle、脱敏模板和计划任务参考，不覆盖旧 release。
4. 运行单元测试、bundle verify 和 SHA-256 验证后再切换 CURRENT。

## 6. 整体切换顺序

1. 保持旧 Pi、旧电脑、旧手机继续运行。
2. 恢复新电脑源码和只读同步，先不要启用介入写入。
3. 配置新手机，完成 token 配对和采集验收。
4. 停止旧客户端任务，确认 Pi 队列没有未完成命令。
5. 启用新电脑计划任务和新手机后台服务。
6. 观察至少一个完整半小时窗口，再移除旧设备的 Tailscale/Syncthing 身份。

## 7. 回滚

在新客户端连续稳定运行一个完整半小时窗口以前，不删除旧设备源码、应用、Tailscale/Syncthing 身份或计划任务。

如果新手机失败：

1. 停止新手机的 Focus Bridge 前台服务与 Automate flow；
2. 将 Pi 的 `focus_bridge_token.txt` 恢复为旧手机 token，或重新运行旧手机对应的安全配对流程；
3. 重新启用旧手机 flow/Bridge，确认 heartbeat 和上传恢复；
4. 保留失败新机日志，但不得让两个手机同时上传相同 device 身份。

如果新电脑失败：

1. 停止新电脑的 5 个客户端计划任务和 Syncthing；
2. 重新启用旧电脑任务，确认 ActivityWatch、行为上下文和 intervention heartbeat；
3. 不让新电脑继续消费 intervention 队列或写入同步目录；
4. 如果故障来自新版构建，将 `CURRENT.json` 改回上一个已验证 release，再从其 Git bundle 恢复；禁止覆盖或修改失败 release 本身。

如果新 Pi 失败，保持客户端仍指向旧 Pi 的 MagicDNS/路由，停用新 Pi 写入 timer，并按 [[我的专注花园/05-Pi迁移验收与恢复清单]] 回退。只有回滚链路验收成功后，才移除失败设备身份。

<!-- ai_provenance: source=codex; date=2026-08-07; verification=local-build-tests-and-live-config-inventory; retrieved_notes="手机使用记录系统——手机端操作与维护指南.md,ActivityWatch 树莓派同步运维手册.md,我的专注花园/专注花园桥接手机APP.md,PI_SERVER_HANDOFF.md" -->
