---
title: Termux 远程 Codex CLI 办公方案
date: 2026-08-24
tags:
  - Codex
  - Termux
  - SSH
  - Tailscale
---

<!-- ai_provenance: source=codex; date=2026-08-24; verification=local-and-source-backed -->

# Termux 远程 Codex CLI 办公方案

这套方案让平板上的 Termux 通过 Tailscale 和 SSH 进入 Windows 电脑，并直接打开 Codex CLI。日常只需记住两个命令：

```bash
ssh codex   # 进入项目选择和 Codex 操作菜单
ssh pc      # 进入普通 Windows PowerShell，也用于 scp 传文件
```

## 1. 当前结构

```text
平板 Termux
  │
  ├─ Tailscale 私网
  │
  └─ SSH 公钥认证
       │
       ▼
Windows 电脑：15345@100.105.53.66
  │
  ├─ C:\Users\15345\bin\codex-project.ps1
  ├─ C:\Users\15345\CodexInbox
  └─ C:\Users\15345\AppData\Roaming\npm\codex.cmd
```

前提：电脑处于开机且未休眠状态，电脑和平板均已连接 Tailscale，Windows 的 OpenSSH Server 正在运行。

## 2. 配置 SSH 免密码登录

### 2.1 在 Termux 安装工具

```bash
pkg update
pkg install openssh nano
```

### 2.2 生成平板专用密钥

```bash
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_tablet -C tablet-termux
```

私钥 `~/.ssh/id_ed25519_tablet` 只能保留在平板中，不能发给任何人。需要复制到电脑的是公钥：

```bash
cat ~/.ssh/id_ed25519_tablet.pub
```

### 2.3 把公钥加入 Windows

在电脑的 PowerShell 中执行，把引号里的内容替换成上一步显示的完整公钥：

```powershell
$key = 'ssh-ed25519 AAAA... tablet-termux'
Add-Content -LiteralPath "$env:USERPROFILE\.ssh\authorized_keys" -Value $key -Encoding ascii
ssh-keygen -lf "$env:USERPROFILE\.ssh\authorized_keys"
```

本机当前实际使用的公钥文件是：

```text
C:\Users\15345\.ssh\authorized_keys
```

如果另一台 Windows 电脑的 `C:\ProgramData\ssh\sshd_config` 启用了 `Match Group administrators`，管理员账户也可能改用：

```text
C:\ProgramData\ssh\administrators_authorized_keys
```

不要凭经验猜路径，应以该电脑的 `sshd_config` 为准。

### 2.4 验证只使用公钥

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_ed25519_tablet

ssh \
  -o PasswordAuthentication=no \
  -o PreferredAuthentications=publickey \
  -i ~/.ssh/id_ed25519_tablet \
  15345@100.105.53.66
```

成功进入 PowerShell 后执行 `exit` 返回 Termux。若得到 `Permission denied (publickey)`，说明公钥仍未被 Windows 接受；这种测试不会再退回密码登录，定位问题更清楚。

## 3. 用 Nano 配置快捷 SSH 命令

在 Termux 中打开配置文件：

```bash
mkdir -p ~/.ssh
nano ~/.ssh/config
```

粘贴：

```sshconfig
Host pc codex
    HostName 100.105.53.66
    User 15345
    IdentityFile ~/.ssh/id_ed25519_tablet
    IdentitiesOnly yes
    ServerAliveInterval 30
    ServerAliveCountMax 3

Host codex
    RequestTTY force
    RemoteCommand powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File C:/Users/15345/bin/codex-project.ps1
```

Nano 的常用按键：

- `Ctrl+O`：保存，然后按回车确认文件名。
- `Ctrl+X`：退出。
- `Ctrl+K`：删除当前行。
- Termux 中可用“音量减”代替 `Ctrl`，例如“音量减 + O”。

保存后设置权限并测试：

```bash
chmod 600 ~/.ssh/config
ssh pc
ssh codex
```

`pc` 与 `codex` 共享同一套主机、用户名和密钥配置；只有 `codex` 额外配置了远程启动命令。

## 4. Windows 项目启动器

启动器位置：

```text
C:\Users\15345\bin\codex-project.ps1
```

当前完整脚本如下。以后增加项目时，只需修改 `$Projects`：

```powershell
[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [string]$Project,

    [ValidateSet('new', 'last', 'history', 'all', 'image')]
    [string]$Action,

    [switch]$Resume,

    [switch]$PrintPath
)

$ErrorActionPreference = 'Stop'

$Projects = [ordered]@{
    notes     = 'D:\mathblog\quartz\content'
    quartz    = 'D:\mathblog\quartz'
    ink       = 'D:\MathInk-Forge-Project'
    focus     = 'D:\MyFocusGarden'
    pi        = 'D:\PiSystemMigration'
    lean      = 'D:\lean_1'
    mathagent = 'D:\MathStudyAgent'
}

$ImageInbox = Join-Path $env:USERPROFILE 'CodexInbox'
if (-not (Test-Path -LiteralPath $ImageInbox -PathType Container)) {
    New-Item -ItemType Directory -Path $ImageInbox -Force | Out-Null
}

function Show-ProjectMenu {
    Write-Host ''
    Write-Host 'Choose a Codex project:' -ForegroundColor Cyan

    $index = 1
    foreach ($entry in $Projects.GetEnumerator()) {
        $state = if (Test-Path -LiteralPath $entry.Value -PathType Container) { '' } else { ' [missing]' }
        Write-Host ("  [{0}] {1,-10} {2}{3}" -f $index, $entry.Key, $entry.Value, $state)
        $index++
    }

    Write-Host '  [p] Enter a Windows directory'
    Write-Host '  [q] Quit'
    Write-Host ''
}

function Show-ActionMenu {
    Write-Host ''
    Write-Host 'Choose an action:' -ForegroundColor Cyan
    Write-Host '  [1] Start a new chat'
    Write-Host '  [2] Continue the latest project chat'
    Write-Host '  [3] Browse this project chat history'
    Write-Host '  [4] Browse all chat history'
    Write-Host '  [5] Start or continue with an uploaded image'
    Write-Host '  [q] Quit'
    Write-Host ''
}

function Select-InboxImage {
    $extensions = @('.png', '.jpg', '.jpeg', '.webp')
    $images = @(
        Get-ChildItem -LiteralPath $ImageInbox -File -ErrorAction SilentlyContinue |
            Where-Object { $extensions -contains $_.Extension.ToLowerInvariant() } |
            Sort-Object LastWriteTime -Descending |
            Select-Object -First 20
    )

    if ($images.Count -eq 0) {
        Write-Host ''
        Write-Host "No images found in $ImageInbox" -ForegroundColor Yellow
        Write-Host 'Upload one from Termux with:'
        Write-Host '  scp "/path/to/image.png" pc:CodexInbox/' -ForegroundColor Cyan
        Write-Host ''
        return $null
    }

    Write-Host ''
    Write-Host "Recent images in $ImageInbox" -ForegroundColor Cyan
    for ($i = 0; $i -lt $images.Count; $i++) {
        $size = if ($images[$i].Length -ge 1MB) {
            '{0:N1} MB' -f ($images[$i].Length / 1MB)
        }
        else {
            '{0:N0} KB' -f ($images[$i].Length / 1KB)
        }

        Write-Host ("  [{0}] {1}  {2}  {3}" -f ($i + 1), $images[$i].Name, $images[$i].LastWriteTime.ToString('yyyy-MM-dd HH:mm'), $size)
    }

    Write-Host '  [q] Cancel'
    Write-Host ''
    $choice = Read-Host 'Image [1]'

    if ([string]::IsNullOrWhiteSpace($choice)) {
        $choice = '1'
    }

    if ($choice -eq 'q') {
        return $null
    }

    if ($choice -notmatch '^\d+$') {
        throw "Unknown image choice: $choice"
    }

    $selectedIndex = [int]$choice - 1
    if ($selectedIndex -lt 0 -or $selectedIndex -ge $images.Count) {
        throw "Unknown image choice: $choice"
    }

    return $images[$selectedIndex]
}

$promptedForProject = [string]::IsNullOrWhiteSpace($Project)

if ($promptedForProject) {
    Show-ProjectMenu
    $choice = Read-Host 'Project [1]'

    if ([string]::IsNullOrWhiteSpace($choice)) {
        $choice = '1'
    }

    if ($choice -eq 'q') {
        return
    }

    if ($choice -eq 'p') {
        $Project = Read-Host 'Windows directory'
    }
    elseif ($choice -match '^\d+$') {
        $keys = @($Projects.Keys)
        $selectedIndex = [int]$choice - 1

        if ($selectedIndex -lt 0 -or $selectedIndex -ge $keys.Count) {
            throw "Unknown menu choice: $choice"
        }

        $Project = $keys[$selectedIndex]
    }
    else {
        $Project = $choice
    }
}

if ($Projects.Contains($Project)) {
    $target = $Projects[$Project]
}
else {
    $target = $Project
}

if (-not (Test-Path -LiteralPath $target -PathType Container)) {
    throw "Project directory does not exist: $target"
}

$target = (Resolve-Path -LiteralPath $target).Path

if ($PrintPath) {
    Write-Output $target
    return
}

$codex = Join-Path $env:APPDATA 'npm\codex.cmd'
if (-not (Test-Path -LiteralPath $codex -PathType Leaf)) {
    $codex = (Get-Command codex.cmd -ErrorAction Stop).Source
}

if ($Resume) {
    $Action = 'last'
}
elseif ([string]::IsNullOrWhiteSpace($Action)) {
    if ($promptedForProject) {
        Show-ActionMenu
        $actionChoice = Read-Host 'Action [1]'

        if ([string]::IsNullOrWhiteSpace($actionChoice)) {
            $actionChoice = '1'
        }

        $Action = switch ($actionChoice) {
            '1' { 'new' }
            '2' { 'last' }
            '3' { 'history' }
            '4' { 'all' }
            '5' { 'image' }
            'q' { return }
            default { throw "Unknown action choice: $actionChoice" }
        }
    }
    else {
        $Action = 'new'
    }
}

Write-Host ''
Write-Host "Project: $target" -ForegroundColor Green
Write-Host ''

switch ($Action) {
    'new' {
        & $codex -C $target
    }
    'last' {
        & $codex resume -C $target --last
    }
    'history' {
        & $codex resume -C $target
    }
    'all' {
        & $codex resume --all
    }
    'image' {
        $image = Select-InboxImage
        if ($null -eq $image) {
            return
        }

        Write-Host ''
        Write-Host 'Use the image with:' -ForegroundColor Cyan
        Write-Host '  [1] A new chat'
        Write-Host '  [2] The latest project chat'
        $imageMode = Read-Host 'Mode [1]'
        if ([string]::IsNullOrWhiteSpace($imageMode)) {
            $imageMode = '1'
        }

        if ($imageMode -notin @('1', '2')) {
            throw "Unknown image mode: $imageMode"
        }

        $imagePrompt = Read-Host 'Instruction for Codex'
        if ([string]::IsNullOrWhiteSpace($imagePrompt)) {
            $imagePrompt = 'Please inspect the attached image and describe the important details.'
        }

        if ($imageMode -eq '2') {
            & $codex resume -C $target --last -i $image.FullName -- $imagePrompt
        }
        else {
            & $codex -C $target -i $image.FullName -- $imagePrompt
        }
    }
}

exit $LASTEXITCODE
```

### 增加新项目

在 `$Projects` 中增加一行即可，例如：

```powershell
myproject = 'D:\MyProject'
```

重新运行 `ssh codex` 后，新项目会自动出现在菜单中。

## 5. 日常使用流程

### 5.1 新建或恢复对话

在 Termux 执行：

```bash
ssh codex
```

先选项目，再选操作：

1. 新建对话。
2. 直接恢复该项目最近一次对话。
3. 浏览该项目的历史对话。
4. 浏览全部项目的历史对话。
5. 使用已上传图片新建或继续对话。

菜单背后使用的是这些 Codex CLI 命令：

```powershell
# 在指定项目新建对话
codex.cmd -C 'D:\mathblog\quartz\content'

# 恢复当前项目最近一次对话
codex.cmd resume -C 'D:\mathblog\quartz\content' --last

# 打开当前项目的历史对话选择器
codex.cmd resume -C 'D:\mathblog\quartz\content'

# 浏览所有目录的历史对话
codex.cmd resume --all
```

`--last` 默认只在当前工作目录范围内寻找最近对话，`--all` 会扩大到所有目录；`-C` 会在 Codex 启动前指定工作目录。

### 5.2 从平板发送图片

首次使用先让 Termux 访问 Android 公共存储：

```bash
termux-setup-storage
```

常见图片目录：

```text
~/storage/dcim/Camera
~/storage/pictures/Screenshots
~/storage/downloads
```

把图片传入电脑的图片收件箱：

```bash
scp "$HOME/storage/pictures/Screenshots/图片.png" pc:CodexInbox/
```

然后执行：

```bash
ssh codex
```

选择项目和操作 `5`，再选择图片、对话模式并输入要求。由于 Codex CLI 实际运行在电脑上，`-i` 必须接收电脑能够读取的路径，所以要先通过 `scp` 上传，不能直接传入 Android 本地路径。

对应的底层命令为：

```powershell
# 带图片新建对话
codex.cmd -C 'D:\mathblog\quartz\content' -i "$HOME\image.png" -- '请分析图片'

# 带图片恢复当前项目最近一次对话
codex.cmd resume -C 'D:\mathblog\quartz\content' --last -i "$HOME\image.png" -- '请查看图片'
```

## 6. 更新与诊断

### 更新 Codex CLI

```powershell
npm install -g @openai/codex@latest
codex.cmd --version
```

若当前版本支持自更新，也可执行：

```powershell
codex update
```

### 生成诊断摘要

```powershell
codex doctor --summary --no-color --ascii
```

`codex doctor` 会检查安装、配置、登录、运行时、Git、终端、App Server 和对话记录等状态，适合在恢复对话失败时先运行。

## 7. 已遇到问题与处理经验

### 7.1 SSH 一直询问密码

现象：

```text
15345@100.105.53.66's password:
```

原因通常不是密钥文件不存在，而是 Windows 没有接受平板公钥，于是 SSH 回退到了密码认证。本次问题的根因是新平板的公钥尚未加入 Windows，`authorized_keys` 中只有旧设备的密钥。

处理顺序：

1. 在 Termux 用 `cat ~/.ssh/id_ed25519_tablet.pub` 重新取得公钥。
2. 确认完整公钥已加入 Windows 当前生效的 `authorized_keys`。
3. 检查 `~/.ssh/config` 中的 `User`、`HostName` 和 `IdentityFile`。
4. 使用禁用密码回退的测试命令验证。

### 7.2 `invalid paginated history lineage ... cycle detected`

现象：Codex 在启动或恢复旧会话时报告历史记录 lineage 出现 cycle，然后 SSH 连接关闭。

本次排查发现旧版、预览版和新版 Codex 写入过同一批会话，诊断中还出现重复 thread ID 或索引缺失。安全处理顺序是：

1. 先升级到最新稳定版 Codex。
2. 完全退出正在运行的 Codex CLI 和 Codex 桌面端。
3. 重新启动 Codex，再尝试恢复。
4. 仍失败时运行 `codex doctor --summary --no-color --ascii` 收集诊断。

不要直接删除 `C:\Users\15345\.codex\sessions` 中的 `.jsonl` 会话文件。这些文件是历史对话的原始记录，升级与重启应优先于手工修改或删除。

### 7.3 `thread ... already has an active writer`

现象：

```text
thread ... already has an active writer
```

含义是该会话仍被另一个 Codex 进程占用，或者上一次异常退出留下了未释放的写入状态。本次问题最终通过**重启 Codex**解决。

推荐处理顺序：

1. 退出电脑和平板上仍连接该会话的 Codex CLI。
2. 完全关闭并重启 Codex 桌面端或相关 Codex 进程。
3. 再执行 `ssh codex` 并恢复会话。
4. 若仍无法释放，再重启电脑。

同样不要为了清理 writer 状态而直接删除会话文件。

### 7.4 Codex 报错后 SSH 显示连接关闭

```text
Connection to 100.105.53.66 closed.
```

`ssh codex` 使用 `RemoteCommand` 直接启动项目脚本。Codex 或脚本一旦异常退出，远程命令结束，SSH 会话也随之关闭。因此这条信息通常是上游 Codex 错误的结果，并不等于 Tailscale 或 SSH 本身断开。

需要单独检查连接时，使用：

```bash
ssh pc
```

## 8. 维护清单

- 电脑保持开机、不休眠，Tailscale 保持在线。
- 平板私钥只保存在平板，备份时注意加密。
- 新设备应生成自己的密钥，不要复制旧设备私钥。
- 项目路径变化时修改 `codex-project.ps1` 中的 `$Projects`。
- 图片统一上传到 `C:\Users\15345\CodexInbox`，用完后可定期手工整理。
- 恢复对话异常时依次采用：关闭重复会话 → 重启 Codex → 更新 Codex → 运行 `codex doctor`。
- 手工删除 `.codex\sessions` 或状态数据库应作为最后手段，并在操作前完整备份。

## 9. 官方参考

- [Codex Developer commands](https://learn.chatgpt.com/docs/developer-commands?surface=cli)：`-C`、`-i`、`resume`、`--last`、`--all`、`doctor`、`update` 的官方说明。

