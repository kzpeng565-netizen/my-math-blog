# UCAS Wi-Fi roaming and Windows hotspot recovery

Use this reference when the Pi alone has intermittent Tailnet/SSH/Serve loss, when changing `wifi-failover.timer`, or when validating the touch-panel recovery path.

## Current diagnosis

- The Windows computer uses UCAS on 5 GHz, while the Raspberry Pi 3 uses 2.4 GHz.
- The Pi was observed reassociating between UCAS BSSIDs `A0:69:D9:4D:8A:B0` and `A0:69:D9:4D:8E:F0`, restarting DHCP and interrupting Tailnet.
- Do not label UCAS generally unstable when the computer remains healthy. Check Pi-specific roaming, band, BSSID, signal, driver logs, power state, gateway, and dual-stack external access.
- Pi resource, disk, power and loopback service health must be checked separately from the network path.

## Production behavior

Pi files:

```text
/home/conrad/workspace/activitywatch-advisor/scripts/wifi_failover.py
/home/conrad/workspace/activitywatch-advisor/config/wifi_failover.json
/etc/systemd/system/wifi-failover.service
/etc/systemd/system/wifi-failover.timer
/var/lib/wifi-failover/state.json
/var/lib/wifi-failover/events.jsonl
```

The timer runs every 30 seconds and evaluates:

1. default route;
2. IPv4 `generate_204=204`;
3. IPv6 HTTPS success.

It switches from UCAS only after four consecutive samples where both IPv4 and IPv6 fail, or the default route is absent. It does not use Windows peer reachability as a trigger.

If Windows hotspot activation fails:

1. restore UCAS immediately;
2. record the result;
3. wait 10 minutes before another automatic attempt.

When connected to the hotspot, keep it while Internet access is healthy. After two failed fallback samples, try UCAS; if UCAS activation fails, restore the hotspot.

Never override an unrelated manually selected Wi-Fi profile.

## Windows hotspot policy

- SSID: `XYH 0563`.
- The user enables the hotspot on demand.
- Do not automatically install or enable the Startup watchdog unless the user explicitly requests always-on hotspot behavior.
- Retain the optional scripts under:

```text
D:\tools\pi-network-fallback\ensure-hotspot.ps1
D:\tools\pi-network-fallback\hotspot-watchdog.ps1
D:\tools\pi-network-fallback\install-hotspot-startup.ps1
D:\tools\pi-network-fallback\remove-hotspot-startup.ps1
```

The active Startup launcher and watchdog should be absent under the on-demand policy.

## Touch-panel recovery

`/home/conrad/touchpanel/panel.py` contains `一键恢复热点连接`.

The button:

1. asks for confirmation;
2. invokes the shared failover script with `--force-fallback` in a background thread;
3. reports the resulting IP on success;
4. restores UCAS and reports the error if hotspot activation fails.

Do not replace it with a second direct `nmcli` implementation.

## Safe checks

```bash
systemctl status wifi-failover.timer wifi-failover.service --no-pager
sudo cat /var/lib/wifi-failover/state.json
sudo tail -n 30 /var/lib/wifi-failover/events.jsonl
nmcli -t -f NAME,DEVICE connection show --active
journalctl -u NetworkManager -u wpa_supplicant -u tailscaled --since '-30 min' --no-pager
```

Windows:

```powershell
Get-CimInstance Win32_Process |
  Where-Object CommandLine -Like '*hotspot-watchdog.ps1*'

Test-Path "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\Pi Hotspot Fallback.vbs"
```

Under the on-demand policy, both checks should show no active watchdog/launcher.

## BSSID pinning gate

Do not pin a UCAS BSSID until:

- roaming and failure correlation has been observed long enough to choose a stable AP;
- a real Pi → hotspot → UCAS round trip passes;
- hotspot failure is proven to restore UCAS;
- the local touch-panel button is available.

Pinning removes roaming flexibility if the selected AP disappears. Keep the fallback profile even after pinning.

## Recovery

Disable automatic Pi switching:

```bash
sudo systemctl disable --now wifi-failover.timer
```

Backups:

```text
Pi: /home/conrad/workspace/backups/wifi-failover-20260831-1648/
Windows: D:\tools\pi-network-fallback-backups\20260831-162644/
```

Do not copy or print the saved hotspot password. Network profiles were not modified by the implementation.
