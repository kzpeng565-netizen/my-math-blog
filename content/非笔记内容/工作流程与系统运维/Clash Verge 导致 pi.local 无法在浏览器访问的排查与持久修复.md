---
title: Clash Verge 导致 pi.local 无法在浏览器访问的排查与持久修复
date: 2026-07-28
tags:
  - Windows
  - Clash-Verge
  - 树莓派
  - 局域网
  - 故障排查
---

<!-- ai_provenance: source=codex; date=2026-07-28; verification=checked; retrieved_notes="" -->

# Clash Verge 导致 pi.local 无法在浏览器访问的排查与持久修复

## 1. 问题现象

树莓派 Web 管理入口：

- Cockpit：`https://pi.local:9090`
- File Browser：`https://pi.local:8080`

在终端中用 `curl` 或直接访问局域网 IP 时服务可达，但浏览器访问 `pi.local` 报错：

```text
嗯… 无法访问此页面
似乎 pi.local 关闭了连接。
```

这个错误容易误导人去检查树莓派服务本身。实际排查中，`https://pi.local:8080` 和 `https://pi.local:9090` 都能直连返回 `200`，解析到 `192.168.0.229`。所以问题不在 File Browser 或 Cockpit 服务，而在 Windows 浏览器流量经过 Clash Verge 系统代理时，`pi.local` 没有被稳定绕过。

## 2. 根因

根因有两层。

第一层是 Clash Verge / mihomo 对 `.local` 的处理不适合 mDNS 本地域名。即使 Clash 规则里写了：

```yaml
- DOMAIN,pi.local,DIRECT
- DOMAIN-SUFFIX,local,DIRECT
```

如果程序已经把请求送进 Clash 代理端口，mihomo 仍可能无法正确解析 `pi.local`，日志中会出现类似：

```text
dial DIRECT (match Domain/pi.local) ... --> pi.local:8080 error: dns resolve failed: couldn't find ip
```

因此，仅靠 Clash 规则中的 `DIRECT` 不够。对浏览器来说，更可靠的是在 Windows 系统代理层就把 `pi.local`、`*.local`、局域网 IP 段排除掉，让浏览器完全不要把这些请求交给 Clash。

第二层是 Clash Verge 会在启动或切换系统代理时重写 Windows 的代理绕过列表。之前手动写入注册表：

```text
pi.local;*.local
```

重启 Clash Verge 后会被覆盖回默认列表，导致问题复发。

## 3. 关键判断方法

先确认服务本身是否可达：

```powershell
curl.exe -k -s -o NUL -w 'pi.local:8080 %{http_code} %{remote_ip}\n' --connect-timeout 10 https://pi.local:8080
curl.exe -k -s -o NUL -w 'pi.local:9090 %{http_code} %{remote_ip}\n' --connect-timeout 10 https://pi.local:9090
```

正常结果类似：

```text
pi.local:8080 200 192.168.0.229
pi.local:9090 200 192.168.0.229
```

再看 Windows 系统代理绕过列表：

```powershell
Get-ItemProperty 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings' |
  Select-Object ProxyEnable, ProxyServer, ProxyOverride, AutoConfigURL |
  Format-List
```

如果 `ProxyOverride` 中没有 `pi.local` 和 `*.local`，浏览器就可能把 `pi.local` 交给 Clash。

再看 Clash Verge 当前源配置：

```powershell
Select-String -Path "$env:APPDATA\io.github.clash-verge-rev.clash-verge-rev\verge.yaml" `
  -Pattern 'use_default_bypass|system_proxy_bypass|proxy_auto_config'
```

如果是：

```yaml
use_default_bypass: true
system_proxy_bypass: null
```

说明 Clash Verge 仍可能用默认 bypass 覆盖 Windows 注册表。

## 4. 本次持久修复

### 4.1 修改 Clash Verge 源配置

文件：

```text
C:\Users\15345\AppData\Roaming\io.github.clash-verge-rev.clash-verge-rev\verge.yaml
```

关键改动：

```yaml
use_default_bypass: false
system_proxy_bypass: 10.*;100.*;127.*;172.16.*;172.17.*;172.18.*;172.19.*;172.20.*;172.21.*;172.22.*;172.23.*;172.24.*;172.25.*;172.26.*;172.27.*;172.28.*;172.29.*;172.30.*;172.31.*;192.168.*;localhost;pi.local;*.local;*.lan;pi.taild4d3f7.ts.net;<local>
```

PAC 模板中也加入本地地址直连判断，避免以后切到 PAC 模式时复发：

```javascript
if (
  isPlainHostName(host) ||
  dnsDomainIs(host, ".local") ||
  shExpMatch(host, "*.local") ||
  dnsDomainIs(host, ".lan") ||
  shExpMatch(host, "*.lan") ||
  shExpMatch(host, "192.168.*") ||
  shExpMatch(host, "10.*") ||
  shExpMatch(host, "172.16.*") ||
  shExpMatch(host, "172.17.*") ||
  shExpMatch(host, "172.18.*") ||
  shExpMatch(host, "172.19.*") ||
  shExpMatch(host, "172.20.*") ||
  shExpMatch(host, "172.21.*") ||
  shExpMatch(host, "172.22.*") ||
  shExpMatch(host, "172.23.*") ||
  shExpMatch(host, "172.24.*") ||
  shExpMatch(host, "172.25.*") ||
  shExpMatch(host, "172.26.*") ||
  shExpMatch(host, "172.27.*") ||
  shExpMatch(host, "172.28.*") ||
  shExpMatch(host, "172.29.*") ||
  shExpMatch(host, "172.30.*") ||
  shExpMatch(host, "172.31.*") ||
  shExpMatch(host, "127.*")
) {
  return "DIRECT";
}
```

### 4.2 修改 Clash Verge 订阅增强规则

因为使用网络订阅，不能直接改订阅文件本体。应改 Clash Verge 的 profile enhancement 文件，让订阅更新后仍自动叠加本地规则。

规则增强文件中加入：

```yaml
prepend:
- DOMAIN,pi.local,DIRECT
- DOMAIN-SUFFIX,local,DIRECT
- IP-CIDR,192.168.0.0/16,DIRECT,no-resolve
- IP-CIDR,169.254.0.0/16,DIRECT,no-resolve

append: []

delete: []
```

本次涉及的 rules 增强文件包括：

```text
C:\Users\15345\AppData\Roaming\io.github.clash-verge-rev.clash-verge-rev\profiles\rtBnKLhVDpsv.yaml
C:\Users\15345\AppData\Roaming\io.github.clash-verge-rev.clash-verge-rev\profiles\rG2bjd1ZQkYE.yaml
C:\Users\15345\AppData\Roaming\io.github.clash-verge-rev.clash-verge-rev\profiles\rMPsmeLAmV6w.yaml
C:\Users\15345\AppData\Roaming\io.github.clash-verge-rev.clash-verge-rev\profiles\rxEC7ulYLE07.yaml
```

merge 增强文件中加入：

```yaml
hosts:
  pi.local: 192.168.0.229
```

本次涉及的 merge 增强文件包括：

```text
C:\Users\15345\AppData\Roaming\io.github.clash-verge-rev.clash-verge-rev\profiles\mnYmjKf3p6dg.yaml
C:\Users\15345\AppData\Roaming\io.github.clash-verge-rev.clash-verge-rev\profiles\m6HmoQNelSPn.yaml
C:\Users\15345\AppData\Roaming\io.github.clash-verge-rev.clash-verge-rev\profiles\m97igqW3LVQ2.yaml
C:\Users\15345\AppData\Roaming\io.github.clash-verge-rev.clash-verge-rev\profiles\mwHEecSNK4dl.yaml
```

`hosts` 这里是给 Clash 内核兜底。浏览器正常情况下应在系统代理层绕过，不进入 Clash；但若某些程序显式使用 Clash 代理端口，这个 hosts 映射可以减少 `pi.local` 解析失败。

### 4.3 修改已有 PowerShell 守护脚本

之前已经有一个用于修复代理绕过列表的方案：

```text
C:\Users\15345\AppData\Roaming\pi-editor\fix-bypass.ps1
C:\Users\15345\AppData\Roaming\pi-editor\run-bypass-hidden.vbs
```

计划任务：

```text
PiEditorTailscaleBypass
```

原脚本只补：

```powershell
$needed = @("pi.taild4d3f7.ts.net", "100.")
```

这能解决 Tailscale MagicDNS / tailnet 地址被代理的问题，但不能解决 `pi.local` 被代理的问题。

本次将脚本扩展为：

```powershell
$regPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings"
$current = (Get-ItemProperty -Path $regPath -Name ProxyOverride -EA 0).ProxyOverride

$needed = @(
    "pi.local",
    "*.local",
    "*.lan",
    "pi.taild4d3f7.ts.net",
    "10.*",
    "100.*",
    "127.*",
    "172.16.*",
    "172.17.*",
    "172.18.*",
    "172.19.*",
    "172.20.*",
    "172.21.*",
    "172.22.*",
    "172.23.*",
    "172.24.*",
    "172.25.*",
    "172.26.*",
    "172.27.*",
    "172.28.*",
    "172.29.*",
    "172.30.*",
    "172.31.*",
    "192.168.*",
    "localhost"
)

$existing = if ($current) {
    $current -split ";" | Where-Object { $_ -and $_ -ne "<local>" }
} else {
    @()
}

$all = ($existing + $needed) | Sort-Object -Unique
Set-ItemProperty -Path $regPath -Name ProxyOverride -Value (($all -join ";") + ";<local>")
```

计划任务改为每 1 分钟运行一次，并允许电池模式运行。检查命令：

```powershell
schtasks /Query /TN 'PiEditorTailscaleBypass' /V /FO LIST
```

关键结果应包含：

```text
Repeat: Every: 0 Hour(s), 1 Minute(s)
Last Result: 0
```

手动运行：

```powershell
schtasks /Run /TN 'PiEditorTailscaleBypass'
```

## 5. 为什么这个守护脚本方案适用

Clash Verge 自身会写 Windows 系统代理设置。只改注册表是一次性的，重启 Clash Verge 后可能被覆盖。只改 Clash 规则也不够，因为 `.local` 最好不要进入 Clash 的 DNS/代理路径。

守护脚本方案的作用是：承认 Clash Verge 可能覆盖注册表，然后每分钟把关键绕过项补回去。它不是最优雅，但非常实用，尤其适合这种本机 GUI 程序会反复改系统代理设置的场景。

最终应同时保留三层：

1. Windows `ProxyOverride`：让浏览器不要代理 `pi.local`；
2. Clash Verge `verge.yaml`：减少 Clash Verge 自己覆盖成坏状态的概率；
3. Clash profile enhancement：给显式走 Clash 端口的程序兜底。

## 6. 验证清单

服务直连：

```powershell
curl.exe -k -s -o NUL -w 'pi.local:8080 %{http_code} %{remote_ip}\n' --connect-timeout 10 https://pi.local:8080
curl.exe -k -s -o NUL -w 'pi.local:9090 %{http_code} %{remote_ip}\n' --connect-timeout 10 https://pi.local:9090
```

期望：

```text
pi.local:8080 200 192.168.0.229
pi.local:9090 200 192.168.0.229
```

系统代理绕过：

```powershell
Get-ItemProperty 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings' |
  Select-Object ProxyEnable, ProxyServer, ProxyOverride |
  Format-List
```

`ProxyOverride` 中必须有：

```text
pi.local;*.local;192.168.*;<local>
```

计划任务：

```powershell
schtasks /Query /TN 'PiEditorTailscaleBypass' /V /FO LIST
```

Clash 规则：

```powershell
Select-String -Path "$env:APPDATA\io.github.clash-verge-rev.clash-verge-rev\clash-verge.yaml" `
  -Pattern 'DOMAIN,pi.local|DOMAIN-SUFFIX,local|IP-CIDR,192.168.0.0'
```

## 7. 后续经验

遇到“终端能访问、浏览器不能访问”的局域网域名问题，不要只检查服务端。应按下面顺序排查：

1. 直接访问局域网 IP，确认服务是否活着；
2. 用 `curl` 访问域名，确认本机解析和 TLS 是否基本可用；
3. 检查 Windows `ProxyOverride`；
4. 检查 Clash Verge 是否重写了 `verge.yaml` 或系统代理；
5. 检查是否已有守护脚本或计划任务在周期性修复代理绕过；
6. 若使用网络订阅，只改 enhancement，不改订阅本体；
7. 对 `.local`、`.lan`、局域网 IP 段，优先在系统代理层绕过，而不是依赖 Clash 的 `DIRECT` 规则。

本次曾尝试写 Windows hosts：

```text
192.168.0.229 pi.local
```

但普通权限无法写入 `C:\Windows\System32\drivers\etc\hosts`。这不是必要步骤；当前方案依赖系统代理绕过和 Clash 增强规则即可。
