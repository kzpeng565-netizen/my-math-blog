# 树莓派服务器 Web 管理指南

<!-- ai_provenance: source=codex; date=2026-07-24; verification=checked; retrieved_notes="" -->

树莓派提供两个局域网 Web 管理入口：

| 需求 | 使用工具 |
|---|---|
| 查看系统状态、日志、服务和存储 | Cockpit |
| 临时使用网页终端 | Cockpit |
| 浏览、上传、下载或编辑工作区文件 | File Browser |
| 批量修改、安装软件或故障恢复 | SSH |

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

## 4. 常见问题

### 4.1 页面无法打开

1. 查看触摸面板上的当前 IP。
2. 尝试用当前 IP 替换 `pi.local`。
3. 在本机终端检查服务和监听端口：

```powershell
ssh pi.local
systemctl status cockpit.socket --no-pager
systemctl status filebrowser.service --no-pager
ss -lntp | grep -E ':(8080|9090) '
```

### 4.2 登录失败

先确认使用了正确的密码类型：Cockpit 使用 Linux 密码，File Browser 使用独立密码。不要反复尝试不确定的密码，以免混淆故障原因。

### 4.3 File Browser 无法保存

确认目标位于 `/home/conrad/workspace` 内，并检查文件所有者和权限。不要通过扩大 File Browser 根目录或放宽系统保护来绕过权限问题。

### 4.4 服务异常

先查看状态和最近日志，再决定是否重启：

```bash
systemctl status filebrowser.service --no-pager -l
journalctl -u filebrowser.service --no-pager -n 100
```
