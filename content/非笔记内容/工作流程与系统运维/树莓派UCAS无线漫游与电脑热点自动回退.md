# 树莓派 UCAS 无线漫游与电脑热点自动回退

<!-- ai_provenance: source=codex; date=2026-08-31; verification=live-wifi-logs-real-hotspot-switch-tests-and-service-tests; retrieved_notes="PI_SERVER_HANDOFF.md,树莓派 UCAS 校园网无屏登录与维护指南.md" -->

## 1. 结论

2026-08-31 的间歇性 Tailnet 断线不是 UCAS 整体网络故障，也不是 Pi 负载、欠压或 Focus Garden 服务崩溃。

电脑与 Pi 虽连接同一 SSID，但实际无线链路不同：

| 设备 | 频段与接入 |
|---|---|
| Windows 电脑 | 5 GHz、信道 44、802.11ax、信号 82%、BSSID `A0:69:D9:4D:8A:A0` |
| Raspberry Pi 3 | 2.4 GHz，在 `A0:69:D9:4D:8A:B0`（信道 6）与 `A0:69:D9:4D:8E:F0`（信道 11）之间切换 |

Pi 的 `wpa_supplicant` 在 15:10、15:15、15:30、15:35 反复重新关联两个 UCAS BSSID，每次都会触发 DHCP 重启。日志同时出现：

```text
bgscan simple: Failed to enable signal strength monitoring
```

Tailscale 因此出现 DERP 重连、endpoint timeout、TLS EOF/reset。Pi 本身当时：

- `get_throttled=0x0`；
- 网关 8/8 无丢包；
- IPv4 `generate_204=204`；
- IPv6 HTTPS=200；
- 内存、负载和磁盘正常。

所以当前不锁定 UCAS BSSID，先由 failover 日志继续积累稳定性证据。

## 2. 备用热点真实验收

Windows 移动热点：

```text
SSID=XYH 0563
Band=2.4 GHz
State=On
虚拟网卡=Microsoft Wi-Fi Direct Virtual Adapter #2
地址=192.168.137.1/24
PeerlessTimeoutEnabled=0
```

Pi 已保存：

```text
profile=netplan-wlan0-XYH 0563
autoconnect=yes
priority=10
```

真实测试：

1. Pi 本地预设自动回切；
2. Pi 成功连接电脑热点，Windows 客户端数由 0 变为 1；
3. 热点连接期间 SSH、Garden 和 Tailscale 可用；
4. 自动回切成功恢复 UCAS，客户端数回到 0；
5. 部署后的 `--force-fallback` 后端再次通过相同测试。

Pi 在保持 UCAS 时的扫描列表可能看不到 `XYH 0563`，但保存的 profile 可以定向连接，因此自动切换不依赖扫描结果。

## 3. 自动切换规则

### 不使用 Windows peer 作为触发条件

电脑可能被带走、关机或休眠。Windows Tailnet peer 不可达只记录为诊断，不得解释为 Pi 断网。

### UCAS → 电脑热点

Pi 每 30 秒检查：

1. 是否存在默认路由；
2. IPv4 `https://www.gstatic.com/generate_204` 是否返回 204；
3. IPv6 HTTPS 是否返回 2xx/3xx。

只有满足以下条件才切换：

```text
有默认路由，但 IPv4 和 IPv6 均失败
或没有默认路由
连续 4 次，约 2 分钟
```

切换热点失败时：

1. 立即重新激活 UCAS；
2. 进入 10 分钟冷却；
3. 冷却期内不重复扰动连接。

### 电脑热点 → UCAS

- 热点外网正常时保持热点，不自动来回切换；
- 热点连续 2 次失去外网时尝试恢复 UCAS；
- UCAS 激活失败时重新连接热点；
- 手动连接其他 Wi-Fi 时，watchdog 不覆盖用户选择。

### 物理限制

如果电脑被带走，同时 UCAS 也真正中断，则不存在可用热点。系统只能：

- 尝试热点；
- 失败后恢复 UCAS profile；
- 等待 UCAS 恢复或电脑返回。

软件无法在电脑不在场时凭空提供第二条网络链路。

## 4. 组件与路径

### Raspberry Pi

```text
/home/conrad/workspace/activitywatch-advisor/scripts/wifi_failover.py
/home/conrad/workspace/activitywatch-advisor/config/wifi_failover.json
/etc/systemd/system/wifi-failover.service
/etc/systemd/system/wifi-failover.timer
/var/lib/wifi-failover/state.json
/var/lib/wifi-failover/events.jsonl
```

timer：

```text
OnBootSec=2min
OnUnitActiveSec=30s
```

### Windows

```text
D:\tools\pi-network-fallback\ensure-hotspot.ps1
D:\tools\pi-network-fallback\hotspot-watchdog.ps1
D:\tools\pi-network-fallback\install-hotspot-startup.ps1
D:\tools\pi-network-fallback\remove-hotspot-startup.ps1
```

当前用户启动项：

```text
%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\Pi Hotspot Fallback.vbs
```

日志：

```text
%LOCALAPPDATA%\PiNetworkFallback\hotspot-ensure.jsonl
%LOCALAPPDATA%\PiNetworkFallback\watchdog.jsonl
```

Windows watchdog 登录后隐藏启动，每 5 分钟确认热点仍为 On。它使用命名互斥锁，重复启动不会生成多个进程。

## 5. 触屏一键恢复

Pi 触屏按钮已从“连接备用热点”升级为：

```text
一键恢复热点连接
```

点击后：

1. 确认是否离开 UCAS；
2. 非阻塞调用 `wifi_failover.py --force-fallback`；
3. 成功时显示当前 IP；
4. 热点失败时立即恢复 UCAS并显示错误；
5. 按钮执行期间禁用，结束后恢复。

面板由 `.xinitrc` 的循环托管，更新时结束旧 `panel.py` 后会在 2 秒左右自动重启。

## 6. 常用检查

```bash
systemctl status wifi-failover.timer wifi-failover.service --no-pager
sudo cat /var/lib/wifi-failover/state.json
sudo tail -n 30 /var/lib/wifi-failover/events.jsonl
nmcli -t -f NAME,DEVICE connection show --active
journalctl -u wifi-failover.service --since '-30 min' --no-pager
```

Windows：

```powershell
Get-CimInstance Win32_Process |
  Where-Object CommandLine -Like '*hotspot-watchdog.ps1*'

Get-Content "$env:LOCALAPPDATA\PiNetworkFallback\watchdog.jsonl" -Tail 10
Get-Content "$env:LOCALAPPDATA\PiNetworkFallback\hotspot-ensure.jsonl" -Tail 10
```

## 7. 停用与恢复

Pi 暂停自动切换：

```bash
sudo systemctl disable --now wifi-failover.timer
```

Windows 移除登录 watchdog：

```powershell
& 'D:\tools\pi-network-fallback\remove-hotspot-startup.ps1'
```

备份：

```text
Pi: /home/conrad/workspace/backups/wifi-failover-20260831-1648/
Windows: D:\tools\pi-network-fallback-backups\20260831-162644/
```

恢复 Pi 时先停用 timer，只逐文件恢复脚本、配置、unit 或 `panel.py`。网络 profile 和 Wi-Fi 密码本次未修改，不需要恢复。
