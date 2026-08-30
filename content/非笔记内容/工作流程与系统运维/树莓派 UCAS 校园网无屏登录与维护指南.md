# 树莓派 UCAS 校园网无屏登录与维护指南

<!-- ai_provenance: source=codex; date=2026-08-30; verification=checked; retrieved_notes="none" -->

本文记录 2026 年 8 月 30 日树莓派迁移到学校后接入 UCAS 校园网的实际过程。目标是在没有显示器的情况下完成网页认证，同时保证 SEP 账号和密码不写入树莓派、命令行、日志或运维文档。

相关文档：[[树莓派服务器Web管理指南]]

## 1. 最终结论

- 校园 Wi-Fi 的 SSID 为 `UCAS`，无线层本身不需要密码，联网后通过网页认证。
- 认证入口为 `https://portal.ucas.ac.cn/index_11.html`，实际跳转至深澜 SRun 门户。
- 树莓派没有显示器时，可以在树莓派上运行无界面 Chromium，通过 ChromeDriver 操作登录页。
- ChromeDriver 只监听树莓派的 `127.0.0.1:9515`，Windows 端通过 SSH 本地转发访问。
- 凭据只从 Windows 本地文件读入内存，经 SSH 隧道送入官方门户表单；树莓派上不创建凭据文件。
- 登录成功的可靠判据是：IPv4 连通性检查返回 `204`，外部 IPv4 HTTPS 返回 `200`。

本次认证成功后的实测结果：

```text
IPv4 connectivity check = 204
IPv4 external HTTPS     = 200
IPv6 external HTTPS     = 200
Tailscale               = active
```

## 2. UCAS 网络的实际特征

树莓派连接 `UCAS` 后，曾获得如下动态地址：

```text
IPv4: 10.207.252.167/16
Gateway: 10.207.255.254
```

该地址由 DHCP 分配，不能视为固定地址。

未认证时的网络表现并不是完全断网：

- 普通 IPv4 HTTP 请求会被门户接管。访问 `http://neverssl.com/` 时返回 `200`，响应正文再通过 JavaScript 跳转到 UCAS 门户，而不一定使用标准 HTTP 302。
- 外部 IPv4 HTTPS 会收到校园门户的自签名证书，因此 `curl` 会报告证书验证失败。不能使用 `curl -k` 后的状态码作为联网成功证据。
- 原生 IPv6 可以直接访问外网。Chromium 和 ChromeDriver 最初就是借助 IPv6 从 Debian／Raspberry Pi 软件源安装的。
- Tailscale 在未认证阶段仍可借 IPv6保持在线，因此 SSH 远程入口没有丢失。
- `nmcli networking connectivity check` 可能因为 IPv6 可用而报告 `full`，即使 IPv4 仍被门户拦截。因此不能只看 NetworkManager 的总体状态。

## 3. NetworkManager 配置

创建开放 Wi-Fi 配置时，不要显式写入旧式 WEP 安全字段。曾经执行 `key-mgmt none` 后，NetworkManager 将连接误判为需要 WEP 密钥，导致报错：

```text
Secrets were required, but not provided
```

可靠做法是删除错误配置后重新创建普通开放网络连接：

```bash
sudo nmcli connection delete UCAS
sudo nmcli connection add type wifi ifname wlan0 con-name UCAS ssid UCAS
sudo nmcli connection modify UCAS connection.autoconnect yes connection.autoconnect-priority 100
sudo nmcli connection up UCAS
```

原临时热点配置继续保留，优先级较低，用于恢复：

```bash
sudo nmcli connection modify "netplan-wlan0-XYH 0563" connection.autoconnect-priority 10
```

在删除备用热点前，应先验证 UCAS 能够跨重启自动连接，并确认认证过期后仍可通过 Tailscale 重新执行无屏认证。

## 4. 无屏认证方案

### 4.1 所需软件

树莓派安装以下包：

```bash
sudo apt-get -o Acquire::ForceIPv6=true --no-install-recommends --yes install \
  chromium chromium-driver chromium-sandbox chromium-l10n
```

Chromium 与 ChromeDriver 必须来自同一软件源并保持相同主版本。本次使用的版本均为 `151.0.7922.173`。

ChromeDriver 不作为常驻服务运行。每次认证只启动一个临时 systemd 单元，例如：

```bash
sudo systemd-run \
  --unit=ucas-chromedriver-<随机ID> \
  --collect \
  --uid=conrad \
  /usr/bin/chromedriver \
  --port=9515 \
  --allowed-ips=127.0.0.1
```

### 4.2 SSH 本地转发

Windows 端选择一个空闲本地端口，将其转发到树莓派回环端口：

```powershell
ssh -N -L 127.0.0.1:<本地临时端口>:127.0.0.1:9515 pi.local
```

这样 ChromeDriver 不会暴露在校园网、Tailscale 或局域网接口上。

### 4.3 临时浏览器会话

通过 WebDriver 创建无界面 Chromium 会话时，应满足以下条件：

- 使用 `--headless=new`；
- 使用唯一的临时目录 `/tmp/ucas-headless-<随机ID>`；
- 使用 `--incognito`；
- 禁止同步和密码保存提示；
- 认证结束后删除 WebDriver session、停止临时 systemd 单元并删除临时目录。

门户表单使用以下选择器：

```text
账号输入框：#username
密码输入框：#password
登录按钮：  #login-account
```

账号和密码应由本地程序直接从凭据文件读入内存，再通过加密的 SSH 隧道发送给 WebDriver。不要把凭据放入：

- PowerShell 或 Bash 命令参数；
- 环境变量；
- 树莓派上的临时文本文件；
- ChromeDriver 日志；
- Git 仓库或 Obsidian 文档。

### 4.4 登录按钮的特殊处理

ChromeDriver 的普通 element-click 操作曾在 `#login-account` 上返回 HTTP 400。直接重复点击可能造成不必要的多次认证请求。

最终可靠的做法是通过页面自身 JavaScript 触发按钮：

```javascript
const button = document.querySelector("#login-account");
button.click();
```

触发后不要立即再次提交，而应等待并轮询独立的 IPv4 连通性检查。

## 5. 成功验证

门户页面显示“登录成功”只能作为辅助信息。最终以网络层验证为准。

### 5.1 IPv4 连通性检查

```bash
curl -4 -sS --max-time 12 \
  -o /dev/null \
  -w '%{http_code}\n' \
  http://connectivitycheck.gstatic.com/generate_204
```

结果应为：

```text
204
```

若结果为 `200`，通常仍是门户拦截页。

### 5.2 外部 IPv4 HTTPS

```bash
curl -4 -sS --max-time 12 \
  -o /dev/null \
  -w '%{http_code}\n' \
  https://deb.debian.org/
```

结果应为：

```text
200
```

只有同时得到 `204` 和 `200`，才将本次认证视为成功。

## 6. 清理检查

认证结束后检查无界面浏览器、驱动、监听端口和临时目录：

```bash
pgrep -af 'chromedriver|ucas-headless|chromium.*headless'
ss -lntp | grep ':9515 '
find /tmp -maxdepth 1 -type d -name 'ucas-headless-*' -print
systemctl list-units --all 'ucas-chromedriver-*' --no-legend --no-pager
```

正常结果应为空。若 ChromeDriver 仍存在，不要只关闭承载它的 SSH 进程；远端子进程可能继续运行。应显式停止对应的临时 systemd 单元：

```bash
sudo systemctl stop ucas-chromedriver-<随机ID>.service
```

然后删除对应的临时 Chromium profile。

## 7. 认证过期后的处理

校园网会话可能在断线、重启或超时后失效。判断流程如下：

1. 确认 `wlan0` 仍连接 `UCAS`。
2. 运行 IPv4 `generate_204` 检查。
3. 若返回 `204`，无需重新认证。
4. 若返回 `200` 或外部 IPv4 HTTPS 出现校园门户证书，则重新执行一次无屏认证。
5. 认证完成后再次验证 `204 + 200`，并执行清理检查。

不要为了“自动登录”把 SEP 密码长期保存在树莓派。当前的一次性无屏认证方案虽然需要在会话失效时重新执行，但安全边界更清楚，也便于审计。

## 8. 本次踩坑摘要

- 开放 Wi-Fi 不应配置成 WEP；错误的安全字段会让 NetworkManager 索取不存在的无线密码。
- 本机浏览器登录不能替代树莓派登录，因为校园门户按树莓派的网络会话/IP/MAC 放行。
- 未认证时 IPv6 可用，既能安装依赖，也能维持 Tailscale 远程入口。
- NetworkManager 显示 `full` 不等于 IPv4 已认证，必须单独验证 IPv4。
- `HTTP 200` 不一定表示外网正常，可能只是门户拦截页；`generate_204=204` 才是可靠信号。
- HTTPS 证书错误是未认证状态的重要信号，不应通过忽略证书来掩盖。
- 普通 WebDriver 点击可能被页面层拦截，使用页面 JavaScript 触发后成功。
- 关闭 SSH 客户端不保证远端 ChromeDriver 同时退出；临时 systemd 单元更容易可靠回收。
- 凭据应始终留在本地内存和加密隧道中，任何调试输出都不得打印表单值。
