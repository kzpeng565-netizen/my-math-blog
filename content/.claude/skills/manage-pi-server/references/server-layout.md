# Raspberry Pi server layout

## Identity and login

| Item | Current value |
|---|---|
| Hardware | Raspberry Pi 3 Model B, 1GB RAM |
| OS | Debian 13 Trixie, ARM64, Raspberry Pi OS Lite |
| Hostname | `Pi`; use `pi.local` on mDNS |
| Last known IPv4 | `192.168.0.229` (DHCP; may change) |
| Linux user | `conrad`, sudo-capable |
| SSH | Port 22; dedicated Ed25519 key authentication is the default, with password authentication retained for recovery |
| Local SSH config | `C:\Users\15345\.ssh\config`; `ssh pi.local` selects user `conrad` and the dedicated key |
| Dedicated SSH private key | `C:\Users\15345\.ssh\pi_server_ed25519`; unencrypted for automation and ACL-restricted to the local user, Administrators, and SYSTEM |
| Dedicated SSH public key | `C:\Users\15345\.ssh\pi_server_ed25519.pub`; fingerprint `SHA256:TWr8514O8YdCE7kYLrz9i6gqf4rWua06aYs9Sy/iTbc` |
| Web administration guide | `D:\mathblog\quartz\content\非笔记内容\工作流程与系统运维\树莓派服务器Web管理指南.md` |
| Cockpit | `https://pi.local:9090` or `https://192.168.0.229:9090`; log in with the Linux account |
| File Browser | `https://pi.local:8080` or `https://192.168.0.229:8080`; log in as `conrad` with its configured File Browser credential |

Passwords are intentionally not stored here. SSH normally uses the dedicated key; the Linux password remains a recovery method and is also used by Cockpit. File Browser has its own credential database.

## Services and important paths

| Component | Service or path |
|---|---|
| Cockpit | `cockpit.socket`; listens on 9090 |
| File Browser | `filebrowser.service`; listens with HTTPS on 8080 |
| File Browser binary | `/usr/local/bin/filebrowser` |
| File Browser database | `/var/lib/filebrowser/filebrowser.db` |
| File Browser systemd unit | `/etc/systemd/system/filebrowser.service` |
| File Browser TLS certificate | `/etc/filebrowser/cert.pem` |
| File Browser TLS private key | `/etc/filebrowser/key.pem` |
| Browser-editable workspace | `/home/conrad/workspace` |
| Syncthing service | `syncthing@conrad.service`; encrypted device sync on TCP 22000 |
| Syncthing GUI | Loopback only on `127.0.0.1:8384`; do not expose directly |
| Tailscale | `tailscaled.service`; authenticated and enabled; fixed IPv4 `100.109.89.52`; MagicDNS `pi.taild4d3f7.ts.net` |
| Focus Garden private web UI | `https://pi.taild4d3f7.ts.net:8460/` (Tailscale Serve, tailnet only); proxies to `http://127.0.0.1:8838`; never enable Funnel because the UI serves copyrighted local assets |
| Focus Garden service | `focus-garden.service`; source `/home/conrad/services/focus-garden`; launcher `/home/conrad/services/focus-garden/app.py --port 8838`, HTTP routes in `focus_garden/server.py`; loopback-only on `127.0.0.1:8838` |
| Focus Garden database | `/home/conrad/services/focus-garden/data/focus-garden.sqlite3`; the Pi is the only active writer |
| Focus Garden save backup | `focus-garden-backup.timer` runs every minute and creates an atomic SQLite snapshot at `/home/conrad/workspace/focus-garden-archive/focus-garden.sqlite3` |
| Focus Garden Syncthing folder | Folder ID `focus-garden-archive`; Pi `/home/conrad/workspace/focus-garden-archive` is Send Only, Windows `D:\MyFocusGardenArchive` is Receive Only with staggered versioning; copyrighted assets are excluded |
| DNS resolution | NetworkManager connection `netplan-eth0` ignores DHCP DNS and uses `8.8.8.8 223.5.5.5`; Tailscale DNS accept is disabled (`tailscale set --accept-dns=false`) because the DHCP/router DNS `192.168.0.252` stopped responding on 2026-07-29 and broke DeepSeek/ntfy lookups |
| Phone usage HTTPS Funnel | Public `https://pi.taild4d3f7.ts.net` on TCP 443 proxies to `http://127.0.0.1:8765`; token authentication remains enforced by the receiver |
| Next Action web UI | `https://pi.taild4d3f7.ts.net:8450` is Tailscale Serve (tailnet only) to `http://127.0.0.1:8767`; authentication is disabled because the former public `:10000` Funnel was removed on 2026-08-04; half-hour report web access is limited to the latest 3 reports |
| ActivityWatch receive-only folder | `/home/conrad/workspace/activitywatch-sync` |
| Obsidian behavior-context receive-only folder | `/home/conrad/workspace/behavior-context-sync`; Syncthing folder ID `behavior-context`, Windows side is Send Only and Pi side is Receive Only |
| Phone usage receiver | `phone-usage-receiver.service`; authenticated JSONL upload API on loopback-only `127.0.0.1:8765`; archive updates merge and deduplicate events instead of replacing an existing day |
| Phone usage receiver files | `/home/conrad/phone_usage/receiver.py`, private token at `/home/conrad/phone_usage/token.txt`, latest uploaded mirrors under `/home/conrad/phone_usage/incoming/`, date-partitioned history under `/home/conrad/phone_usage/archive/YYYY-MM-DD/` |
| Phone usage archive maintenance | `phone-usage-maintenance.timer` runs daily around 03:30; `/home/conrad/phone_usage/maintenance.py` compresses JSONL archives once they are 30 days old and removes archive day directories older than 365 days |
| Half-hour behavior interpreter | `activitywatch-advisor.timer` runs at minute 08 and 38. `activitywatch-advisor.service` cleans computer, phone, and tablet data; builds one tagged 40-minute window; asks DeepSeek to classify compact unlocked candidates; restores exact times and calculates mixing deterministically; then archives the report under `data/ai_reports/`. Half-hour PushPlus sending was disabled on 2026-08-07 by `disable-half-hour-pushplus.conf` using `UnsetEnvironment=PUSHPLUS_TOKEN`; the base unit may still reference the optional env file. `would_intervene=true` candidates may still use the independent ntfy half-hour check. |
| Behavior summary notifications | `activitywatch-advisor-daily-summary.timer` is disabled to avoid duplicate 09:00 daily messages; `activitywatch-advisor-weekly-summary.timer` still sends the previous ISO week on Monday at 09:05 through PushPlus; receipts are under `data/statistics/pushplus_receipts/` |
| Daily life review notifications | `activitywatch-advisor-daily-life.timer` runs daily at 09:00, 10:00, and 11:00. `src/daily_life_notifier.py` generates the previous day's `src/daily_life_statistics.py` report, waits without pushing if the morning phone boundary is still pending before 11:00, asks DeepSeek V4 Pro for the advice layer through `settings.json` `report_model` once the boundary resolves or reaches possible-fault status, sends a plain-text emoji-formatted ntfy message, and writes receipts under `data/statistics/ntfy_receipts/daily_life/`. Private ntfy settings are read from `/home/conrad/.config/activitywatch-advisor/ntfy.env`. |
| Behavior interpreter files | `/home/conrad/workspace/activitywatch-advisor`; private DeepSeek environment at `/home/conrad/.config/activitywatch-advisor/env`; private PushPlus token at `/home/conrad/.config/activitywatch-advisor/pushplus.env`; private ntfy settings at `/home/conrad/.config/activitywatch-advisor/ntfy.env`; private half-hour shadow ntfy settings at `/home/conrad/.config/activitywatch-advisor/ntfy-halfhour.env`; generated device facts, tagged facts, semantic timelines, mixing metrics, reports, PushPlus receipts, and ntfy receipts under `/home/conrad/workspace/activitywatch-advisor/data/` |
| Late-night device reminder | `bedtime-reminder.timer` runs once per minute from 00:00 through 04:59; `src/bedtime_reminder.py` enforces the active 00:30-04:30 Asia/Shanghai window, reads private ntfy settings from `/home/conrad/.config/activitywatch-advisor/ntfy.env`, and writes state/logs under `/home/conrad/workspace/activitywatch-advisor/data/` |
| System maintenance time guard | `sysadmin-time-guard.timer` runs every 3 minutes; `src/sysadmin_time_guard.py` reads the latest 60 minutes of ActivityWatch computer facts, sends ntfy reminders after sustained system-maintenance work, repeats reminders every 3 minutes while recent maintenance is still detected, and writes state/logs under `/home/conrad/workspace/activitywatch-advisor/data/` |
| Behavior tag rules | `/home/conrad/workspace/activitywatch-advisor/config/tag_rules.json`; editable in Monaco Lite; validate with `python3 src/fact_tagger.py --rules config/tag_rules.json` from the project root |
| Tagged fact archives | `/home/conrad/workspace/activitywatch-advisor/data/tagged_facts/YYYY-MM-DD/HH-MM.json`; complete auditable facts remain here while DeepSeek receives a compact candidate view |
| Behavior-context derived data | Last-known-good at `data/context_cache/current.json`; per-run archives under `data/context_snapshots/`; shadow-only candidates under `data/intervention_candidates/`; daily and weekly summaries under `data/statistics/`; half-hour reports and shadow candidates remain locally archived while the former half-hour PushPlus channel is disabled; stale phone/tablet screen events become `unknown`; all-device inactivity skips DeepSeek while local archival continues |
| Touch-panel application | `/home/conrad/touchpanel/panel.py` |
| Touch-panel recent-files source | `/home/conrad/workspace` (shows the six most recently modified regular files) |
| Legacy touch-panel todo data | `/home/conrad/touchpanel/todos.json` (retained but no longer used by the panel) |
| Offline local terminal | `/usr/bin/xterm`, launched from the panel as `conrad` |
| X session | `/home/conrad/.xinitrc` |
| Local auto-start | `/home/conrad/.bash_profile` with `TOUCHPANEL_START` marker |
| Panel sudo policy | `/etc/sudoers.d/touchpanel` |
| Xorg log | `/home/conrad/.local/share/xorg/Xorg.0.log` |

The File Browser root is deliberately limited to `/home/conrad/workspace`. Its command runner and external symlink traversal are disabled. Its certificate is self-signed for `pi.local` and the last known IP.

When networking is unavailable, connect a USB mouse and keyboard, choose `本地终端` on the panel, and run `sudo -i` to obtain a root shell. The current Raspberry Pi OS sudo policy grants `conrad` `NOPASSWD: ALL`; this predates the terminal button and was not added by the panel. Do not broaden privileges further, and change this existing policy only when the user explicitly requests hardening. Run `exit` to leave root, then `exit` again to close xterm and return to the panel.

## Common checks

```bash
systemctl status cockpit.socket --no-pager
systemctl status filebrowser.service --no-pager
systemctl is-enabled filebrowser.service
ss -lntp | grep -E ':(22|8080|9090|22000) '
journalctl -u filebrowser.service --no-pager -n 100
systemctl status syncthing@conrad.service --no-pager
journalctl -u syncthing@conrad.service --no-pager -n 100
nmcli device show eth0 | grep -E 'IP4.DNS|IP4.GATEWAY'
tailscale debug prefs | grep -E '"CorpDNS"'
getent hosts ntfy.sh api.deepseek.com
pgrep -af 'Xorg|matchbox-window-manager|touchpanel/panel.py'
DISPLAY=:0 XAUTHORITY=/home/conrad/.Xauthority xinput list
```

Check the web endpoints from another machine:

```text
https://pi.local:9090
https://pi.local:8080
```

## Backups and recovery

Before File Browser maintenance, copy its database and systemd unit to a dated backup under `/home/conrad/workspace/backups/`. The database contains credential hashes, so keep backups private.

If File Browser fails, inspect in this order:

```bash
systemctl status filebrowser.service --no-pager -l
journalctl -u filebrowser.service --no-pager -n 100
ss -lntp | grep ':8080 '
/usr/local/bin/filebrowser version
```

If the hostname is unreachable, obtain the current IP from the local panel, router DHCP leases, or the `b8:27:eb:b7:b4:30` Ethernet MAC previously observed. Do not assume the last known IP is permanent.
| File Browser | `https://pi.local:8080` or `https://192.168.0.229:8080`; log in as `conrad` with its configured File Browser credential |
| Monaco Lite | `https://pi.taild4d3f7.ts.net:8443` (Tailscale Serve, tailnet only); HTTP Basic Auth with credentials from `/etc/pi-editor.env` |
| Monaco Lite (pi-editor) | `pi-editor.service`; FastAPI + Uvicorn, loopback-only on `127.0.0.1:8766` |
| Monaco Lite Tailscale Serve | `https://pi.taild4d3f7.ts.net:8443` → `http://127.0.0.1:8766` |
| Monaco Lite source | `/opt/pi-editor/backend/` (Python), `/opt/pi-editor/frontend/` (static HTML/JS/Monaco) |
| Monaco Lite environment | `/etc/pi-editor.env` (root:root, 600) |
| Monaco Lite systemd unit | `/etc/systemd/system/pi-editor.service` |
| Next Action private web UI | `https://pi.taild4d3f7.ts.net:8450` (Tailscale Serve, tailnet only); proxies to `http://127.0.0.1:8767` |
| Next Action web service | `activitywatch-advisor-web.service`; Python stdlib HTTP server on loopback-only `127.0.0.1:8767` |
| Next Action source and data | `/home/conrad/workspace/activitywatch-advisor/src/web_app.py`, `/home/conrad/workspace/activitywatch-advisor/src/next_action.py`; archives under `/home/conrad/workspace/activitywatch-advisor/data/next_action/` |
| Next Action issue feedback | Source `/home/conrad/workspace/activitywatch-advisor/src/issue_feedback.py`; tests `/home/conrad/workspace/activitywatch-advisor/tests/test_issue_feedback.py`; API `POST /api/issue-feedback` and `GET /api/issue-feedback/recent` behind the web login; backlog under `/home/conrad/workspace/activitywatch-advisor/data/issue_feedback/UNREVIEWED.md` with raw JSON under `data/issue_feedback/raw/` |
| Behavior data/interface index | `/home/conrad/workspace/activitywatch-advisor/docs/behavior-data-and-interfaces.md`; mirrored in the local Obsidian vault as `非笔记内容/工作流程与系统运维/树莓派行为数据与接口索引.md` |
| Behavior system flowchart | Current authority: `/home/conrad/workspace/activitywatch-advisor/docs/system-flowchart.md`, mirrored locally as `非笔记内容/工作流程与系统运维/树莓派行为系统总流程图.md`. Existing rendered JPG files are 2026-07 historical snapshots and must not be used for current port/exposure decisions until regenerated from the Markdown. |
ss -lntp | grep -E ':(22|8080|9090|22000|8443|8450|8460|8766|8767|8838) '
systemctl status pi-editor --no-pager
journalctl -u pi-editor.service --no-pager -n 100
https://pi.taild4d3f7.ts.net:8443

## Editable migration system (2026-08-07)

| Component | Location / state |
| --- | --- |
| Migration control repository | `/home/conrad/workspace/pi-portable-system/`; local-only Git, tag `portable-system-v1`, pre-push blocked |
| Monaco-friendly editable clones | `/home/conrad/workspace/editable/`; production services do not run from these clones |
| Safe source export | `/home/conrad/workspace/pi-system-migration/current/`; excludes data, credentials, environments, backups, and Focus Garden private assets |
| Windows safe-source replica | `D:\PiSystemMigration`; Syncthing Receive Only with staggered versioning |
| Safe export schedule | `pi-portable-export.timer`; enabled, every six hours |
| Private Restic schedule | `pi-portable-private-backup.timer`; intentionally disabled until an external encrypted repository and password are configured |
| Private Focus Garden asset checksum | `/home/conrad/.local/state/pi-portable-system/private-assets.sha256`; mode 0600, never include in public exports |
| Windows/Android client migration release | Windows `D:\PiClientMigration` is Syncthing Send Only; Pi `/home/conrad/workspace/pi-client-migration` is Receive Only with staggered versioning. `CURRENT.json` points to the verified release, with editable Git bundles, APK/build references, secret-free templates, Scheduled Task references, and SHA-256 manifests |

Minecraft-derived files under Focus Garden `static/assets/{plants,mushrooms,blocks}` are private-only. They must never enter a public repository, public website deployment, or the safe source export. Run `/home/conrad/workspace/pi-portable-system/scripts/public-export-guard.sh` before any export or remote operation.
