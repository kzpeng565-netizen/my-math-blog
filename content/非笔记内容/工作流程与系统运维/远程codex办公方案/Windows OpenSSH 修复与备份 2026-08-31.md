<!-- ai_provenance: source=codex; date=2026-08-31; verification=checked -->

# Windows OpenSSH 修复与备份（2026-08-31）

## 1. 故障现象

vivo Pad5e 的 Termux 执行：

```bash
ssh codex
```

连续返回：

```text
ssh: connect to host 100.105.53.66 port 22: Software caused connection abort
```

## 2. 原因

检查确认：

- 平板的 Tailscale 路由正常，可以访问电脑 `100.105.53.66`。
- Termux 的 SSH 配置、私钥和 Windows 上的公钥均正常。
- Windows 没有程序监听 TCP 22 端口。
- `sc query sshd` 返回错误 `1060`，说明 `sshd` 服务注册项已经消失，而不只是服务停止。
- OpenSSH Server 程序、主机密钥和 `sshd_config` 仍然存在。

`sshd` 在 2026-08-28 配置时仍处于运行状态，到 2026-08-31 服务项已经丢失。现有日志不足以确定是 Windows 更新、组件维护还是其他操作删除了服务。

## 3. 修复结果

2026-08-31 已完成：

- 确认 Windows OpenSSH Server 组件状态为 `Installed`。
- 重新注册 `OpenSSH SSH Server` 服务。
- 将服务启动类型设为 `Automatic`。
- 启用 `OpenSSH-Server-In-TCP` 入站防火墙规则。
- 配置服务异常退出后每隔 5 秒自动重启，最多连续重启三次。
- 确认 `0.0.0.0:22` 和 `[::]:22` 均处于监听状态。
- 从 vivo Pad5e 验证 SSH 公钥免密登录成功。
- 从 vivo Pad5e 实际执行 `ssh codex`，项目选择菜单正常显示。

## 4. 实际备份

备份目录：

```text
C:\Users\15345\OpenSSH-Backup\2026-08-31_180524-before-repair
```

该目录权限仅授予：

- `xyh\15345`
- `BUILTIN\Administrators`
- `NT AUTHORITY\SYSTEM`

备份内容：

```text
ProgramData-ssh\             Windows SSH 服务配置和主机密钥
authorized_keys              用户 SSH 登录公钥
codex-project.ps1            远程 Codex 项目选择脚本
ProgramData-ssh-acl.txt      C:\ProgramData\ssh 的 ACL 记录
authorized_keys-acl.txt      authorized_keys 的 ACL 记录
backup-sha256.csv            备份文件 SHA-256 校验值
pre-repair-state.json        修复前状态
post-repair-state.json       修复后状态
```

> [!warning]
> `ProgramData-ssh` 中包含 Windows SSH 主机私钥。不要将整个备份目录复制到 Obsidian、Git 仓库、公开网盘或聊天窗口。

## 5. 日常检查

可复用的一键备份与修复脚本：

```text
D:\mathblog\quartz\content\非笔记内容\工作流程与系统运维\远程codex办公方案\scripts\repair-windows-openssh.ps1
```

需要从管理员 PowerShell 执行。

在管理员 PowerShell 中检查服务：

```powershell
Get-Service sshd
Get-NetTCPConnection -LocalPort 22 -State Listen
Get-NetFirewallRule -Name OpenSSH-Server-In-TCP
```

正常状态应当是：

```text
sshd：Running
StartType：Automatic
TCP 22：Listening
防火墙：Enabled / Allow
```

平板端检查：

```bash
ssh pc
ssh codex
```

## 6. 服务再次丢失时

如果 `Get-Service sshd` 显示服务存在但停止：

```powershell
Start-Service sshd
```

如果提示找不到 `sshd` 服务，不要只运行 `Restart-Service`。需要在管理员 PowerShell 中重新注册：

```powershell
$sshd = 'C:\Windows\System32\OpenSSH\sshd.exe'

& $sshd -t

New-Service `
  -Name sshd `
  -BinaryPathName $sshd `
  -DisplayName 'OpenSSH SSH Server' `
  -Description 'OpenSSH SSH Server' `
  -StartupType Automatic `
  -DependsOn Tcpip

Start-Service sshd
```

如果防火墙规则丢失：

```powershell
New-NetFirewallRule `
  -Name OpenSSH-Server-In-TCP `
  -DisplayName 'OpenSSH SSH Server (sshd)' `
  -Enabled True `
  -Direction Inbound `
  -Protocol TCP `
  -Action Allow `
  -LocalPort 22 `
  -Profile Any
```

## 7. 从备份恢复配置

恢复前先停止服务，并确认使用的是正确备份目录：

```powershell
$backup = 'C:\Users\15345\OpenSSH-Backup\2026-08-31_180524-before-repair'

Stop-Service sshd

Copy-Item `
  -Path "$backup\ProgramData-ssh\*" `
  -Destination 'C:\ProgramData\ssh' `
  -Recurse `
  -Force

Copy-Item `
  -LiteralPath "$backup\authorized_keys" `
  -Destination 'C:\Users\15345\.ssh\authorized_keys' `
  -Force

Start-Service sshd
```

恢复后重新执行第 5 节的检查，并从平板测试：

```bash
ssh codex
```

## 8. 非阻断警告

Termux 当前的 OpenSSH 客户端可能显示：

```text
WARNING: connection is not using a post-quantum key exchange algorithm.
```

这是新客户端对旧版 Windows OpenSSH Server 的安全提醒，不会阻止当前 SSH 连接，也不是本次故障原因。
