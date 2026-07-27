# 树莓派服务器 Web 管理指南

<!-- ai_provenance: source=codex; date=2026-07-27; verification=checked; retrieved_notes="" -->

树莓派提供三个 Web 管理入口：

| 需求                   | 使用工具         |
| -------------------- | ------------ |
| 查看系统状态、日志、服务和存储      | Cockpit      |
| 临时使用网页终端             | Cockpit      |
| 浏览、上传、下载、新建或删除工作区文件  | File Browser |
| 编辑代码（语法高亮、代码折叠、保存）   | Monaco Lite  |
| 批量修改、安装软件或故障恢复       | SSH          |

## 1. 访问与登录

电脑应与树莓派处于同一可信局域网。

- Cockpit：`https://pi.local:9090`
- File Browser：`https://pi.local:8080`
- 如果 `pi.local` 无法解析，把主机名换成触摸面板显示的当前 IP。

两个服务使用本地自签名 TLS 证书。浏览器首次访问时可能显示证书警告；先确认地址确实是 `pi.local` 或树莓派当前局域网 IP，再选择继续访问。不要把 8080 或 9090 端口直接暴露到公网。

两者使用不同的登录凭据：

- Cockpit 使用 Linux 账户 `conrad` 及其 Linux 密码。
- File Browser 使用账户 `conrad` 及 File Browser 自己的密码，不一定与 Linux 密码相同。
- 密码不记录在笔记、技能或脚本中。

## 2. Cockpit

Cockpit 适合查看和管理系统状态，不适合代替 File Browser 进行日常文件整理。

### 2.1 查看系统状态

登录后先查看概览页中的 CPU、内存、磁盘和运行时间。遇到异常负载时，再进入日志或服务页面定位原因。

### 2.2 查看日志

在日志页面中按时间、严重级别或服务筛选。优先查看故障发生前后的记录，不要为了排错清空日志。

### 2.3 管理服务

在服务页面搜索完整的 systemd 单元名，例如：

- `filebrowser.service`
- `syncthing@conrad.service`
- `cockpit.socket`

修改前先确认当前状态和最近日志。只重启受影响的服务；除非确有必要，不要重启整台服务器。

### 2.4 使用终端

网页终端适合少量交互检查。需要执行可重复维护、批量修改或恢复操作时，优先从本机运行：

```powershell
ssh pi.local
```

本机已经配置专用 SSH 密钥，正常情况下不需要输入密码。不要在网页终端中粘贴来源不明的命令。

## 3. File Browser

File Browser 中显示的根目录 `/` 对应服务器上的：

```text
/home/conrad/workspace
```

它可以用于：

- 新建文件或文件夹；
- 上传、下载、重命名和移动文件；
- 预览或编辑文本文件；
- 整理工作区中的资料。

保存文本前确认编码为 UTF-8。编辑重要文件前先下载副本，或在 `backups/` 下创建备份。删除、覆盖和批量移动可能难以恢复，应先核对目标。

File Browser 被刻意限制在工作区内：

- 不能访问 `/etc`、`/home/conrad/touchpanel` 等工作区外路径；
- 命令执行器未启用；
- 不允许通过外部符号链接绕过根目录；
- 不要修改 `.stfolder` 等 Syncthing 元数据；
- 不要通过 File Browser 处理其凭据数据库或 TLS 私钥。

### 5.1 页面无法打开

1. 查看触摸面板上的当前 IP。
2. 尝试用当前 IP 替换 `pi.local`。
3. 在本机终端检查服务和监听端口：

```powershell
ssh pi.local
systemctl status cockpit.socket --no-pager
systemctl status filebrowser.service --no-pager
ss -lntp | grep -E ':(8080|9090) '
```

### 5.2 登录失败

先确认使用了正确的密码类型：Cockpit 使用 Linux 密码，File Browser 使用独立密码。不要反复尝试不确定的密码，以免混淆故障原因。

### 5.3 File Browser 无法保存

确认目标位于 `/home/conrad/workspace` 内，并检查文件所有者和权限。不要通过扩大 File Browser 根目录或放宽系统保护来绕过权限问题。

### 5.4 服务异常

先查看状态和最近日志，再决定是否重启：

```bash
systemctl status filebrowser.service --no-pager -l
journalctl -u filebrowser.service --no-pager -n 100
```
## 1. 访问与登录
+ Cockpit：`https://pi.local:9090`
+ File Browser：`https://pi.local:8080`
+ Monaco Lite：`https://pi.taild4d3f7.ts.net:8443`（需要 Tailscale）
三者使用不同的登录凭据：
+ File Browser 使用账户 `conrad` 及 File Browser 自己的密码，不一定与 Linux 密码相同。
+ Monaco Lite 使用 HTTP Basic Auth，用户名 `conrad`，密码存储在 `/etc/pi-editor.env`（`root:root`，权限 600）。
- 不要通过 File Browser 处理其凭据数据库或 TLS 私钥。

## 4. Monaco Lite

Monaco Lite 是一个轻量级 Web 代码编辑器，提供 VS Code 同款编辑器内核（Monaco），用于在浏览器中查看和修改 Python、JSON、YAML、Markdown 等代码文件。

**设计原则**：File Browser 负责文件管理（浏览、上传、新建、删除），Monaco Lite 只负责代码编辑。两者各司其职，不互相替代。

### 4.1 访问

Monaco Lite 通过 Tailscale Serve 提供，仅限 Tailnet 内访问：

```
https://pi.taild4d3f7.ts.net:8443
```

电脑需要安装并连接 Tailscale 客户端（`kzpeng565@` 账户）。浏览器打开后会显示 HTTP Basic Auth 登录窗口，凭据同第 1 节所述。

如果在 Windows 上使用 Clash Verge 系统代理，需要将 `pi.taild4d3f7.ts.net` 和 `100.` 加入代理绕过列表，否则浏览器会把 Tailscale 流量发给 Clash 导致连接失败。

Clash Verge 的 `verge.yaml` 中 `system_proxy_bypass` 字段在切换系统代理或重启时会被重置为 `null`，因此不能依赖它持久化绕过列表。当前通过两层自动修复机制保证 Windows 注册表中的绕过项始终存在：

| 机制 | 触发时机 | 作用 |
|---|---|---|
| 登录脚本 | Windows 用户登录时 | 启动后立即注入绕过项 |
| 计划任务 `PiEditorTailscaleBypass` | 每 5 分钟 | 持续修复（Clash 重置后最多 5 分钟内恢复） |

脚本位置：`%APPDATA%\pi-editor\fix-bypass.ps1`

脚本逻辑：读取当前注册表 `ProxyOverride`，如果缺少 `pi.taild4d3f7.ts.net` 或 `100.` 则补充。不会删除已有项，不会重复添加。

手动触发修复（排查时使用）：

```powershell
powershell.exe -ExecutionPolicy Bypass -File "$env:APPDATA\pi-editor\fix-bypass.ps1"
```

验证注册表是否包含必需项：

```powershell
Get-ItemProperty "HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings" -Name ProxyOverride
# 输出应包含 pi.taild4d3f7.ts.net 和 100.
```

### 4.2 使用方式

1. 在 File Browser 中找到要编辑的文件，复制其相对路径（相对于 `/home/conrad/workspace`）
2. 打开 Monaco Lite，将路径粘贴到顶部输入框
3. 点击 Open，编辑器自动加载文件内容并匹配语法高亮
4. Ctrl+S 保存

编辑器左侧会显示最近打开文件列表（存储在浏览器 localStorage 中，最多 10 个）。

如果保存时文件已被其他程序修改（如 SSH、Syncthing），编辑器会弹出冲突对话框，防止静默覆盖。可选择重新加载最新版本、复制当前修改、或取消保存。

### 4.3 后端架构

| 组件 | 详情 |
|---|---|
| 后端框架 | FastAPI + Uvicorn（单 worker） |
| 监听地址 | `127.0.0.1:8766`（仅本机） |
| 外部入口 | Tailscale Serve `:8443` → `127.0.0.1:8766` |
| 文件根目录 | `/home/conrad/workspace`（由 `EDITOR_ROOT` 环境变量指定） |
| API 端点 | `GET /api/health`、`GET /api/file`、`PUT /api/file` |
| 前端 | Monaco Editor（本地托管，`/opt/pi-editor/frontend/monaco/min/vs/`） |

### 4.4 文件系统安全

后端只接受相对于 `EDITOR_ROOT` 的路径。以下请求会被拒绝：

- 绝对路径（如 `/etc/passwd`）
- `..` 路径穿越（如 `../../etc/passwd`）
- 指向 workspace 外部的符号链接
- 超过 2 MiB 的文件（`413`）
- 非 UTF-8 文本/二进制文件（`415`）
- 不存在的文件（V1 不允许创建新文件）

保存文件时使用同目录临时文件 + `fsync` + `os.replace` 保证原子性，保留原文件权限。每次保存携带 SHA-256 版本号，版本不匹配时返回 `409 Conflict`。

### 4.5 服务管理

```bash
# 查看状态
systemctl status pi-editor --no-pager

# 重启
sudo systemctl restart pi-editor

# 查看日志
journalctl -u pi-editor --no-pager -n 50
```

部署位置：

```text
/opt/pi-editor/
├── backend/           # FastAPI 应用（app.py, auth.py, filesystem.py, models.py）
├── frontend/          # 静态文件（index.html, editor.js, monaco/）
└── venv/              # Python 虚拟环境

/etc/pi-editor.env     # 环境变量（root:root, 600）
/etc/systemd/system/pi-editor.service
```

环境变量（`/etc/pi-editor.env`）：

| 变量 | 值 |
|---|---|
| `EDITOR_ROOT` | `/home/conrad/workspace` |
| `EDITOR_MAX_FILE_BYTES` | `2097152` |
| `EDITOR_ALLOW_CREATE` | `false` |
| `EDITOR_USERNAME` | `conrad` |
| `EDITOR_PASSWORD` | 生成时随机 |
| `EDITOR_LOG_LEVEL` | `info` |

systemd 资源限制：`MemoryHigh=160M`、`MemoryMax=256M`、`TasksMax=64`、`CPUQuota=100%`。

### 4.6 恢复与更新

部署和测试流程见原始教程。前端修改后无需重启服务（静态文件直接生效），后端 Python 代码修改后需要重启：

```bash
sudo systemctl restart pi-editor
```

回滚（停止并删除服务）：

```bash
sudo systemctl disable --now pi-editor
sudo tailscale serve --https=8443 off
sudo rm /etc/systemd/system/pi-editor.service
sudo systemctl daemon-reload
# 保留 /opt/pi-editor 和 /etc/pi-editor.env 以便排查
```

### 4.7 已知限制

- V1 不支持创建新文件（通过 File Browser 创建后再编辑）
- `verge.yaml` 中的 `system_proxy_bypass` 会被 Clash Verge 重置，依赖计划任务自动修复
- 编辑器无终端、无 Git 集成、无语言服务器（自动补全需后续版本接入 LSP）
- 仅限 Tailnet 访问，公网不可达（不使用 Funnel）

## 5. 常见问题
### 5.5 Monaco Lite 无法打开（系统代理环境下）

**症状**：浏览器显示"关闭了连接"或页面全黑。

排查顺序：

1. 确认 Tailscale 已连接：`tailscale status` 应显示 `pi` 在线
2. 确认服务运行：`ssh pi.local "systemctl is-active pi-editor"`
3. 检查监听端口：`ssh pi.local "ss -lntp | grep 8766"`
4. 确认 Tailscale Serve 配置：`ssh pi.local "sudo tailscale serve status"` 应显示 8443 端口
5. Windows 端检查代理绕过：`Get-ItemProperty "HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings" -Name ProxyOverride` 应包含 `pi.taild4d3f7.ts.net` 和 `100.`
6. 硬刷新浏览器（Ctrl+Shift+R）

如果注册表绕过项持续缺失，检查计划任务是否正常：

```powershell
schtasks /query /tn PiEditorTailscaleBypass
```

如果任务不存在，手动创建：

```powershell
schtasks /create /tn PiEditorTailscaleBypass /sc minute /mo 5 /tr "powershell.exe -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$env:APPDATA\pi-editor\fix-bypass.ps1`"" /rl limited /f
```
