---
name: pi-ops-system-context
description: "Use for Conrad's Raspberry Pi behavior advisor and ops system, including Next Action web UI, My Focus Garden, half-hour AI reports, phone/tablet/computer activity collection, Automate uploads, Tailscale Funnel/Serve, PushPlus/ntfy notifications, Obsidian behavior context, Pomodoro/task/sleep/feedback rules, issue-feedback backlog processing, and updates to PROJECT_STATE, DECISIONS, NEXT_STEPS, or PI_SERVER_HANDOFF."
---

# Pi Ops System Context

Use this skill to quickly enter the operating context of Conrad's Raspberry Pi behavior advisor system.

The goal is to route the request to the right documents, services, and data directories before acting, so Codex can understand terms like "Next Action", "我的专注花园", "半小时报告", "Funnel", "Automate", "番茄钟", "问题反馈", and "运维文档" without asking the user to restate the architecture.

## Start every task

1. Read `references/canonical-docs.md` to locate the authoritative local and Raspberry Pi documents.
2. Read `references/reading-routes.md` and choose the smallest route that matches the user's request.
3. If the task touches Raspberry Pi services, deployment, ports, Funnel/Serve, systemd, or files under `/home/conrad`, also use `manage-pi-server` and follow its safety checks.
4. If the task edits local Obsidian Markdown, also use `obsidian-vault-notes` and follow its edit protocol.
5. If the task changes behavior, interfaces, services, data paths, or rules, read `references/update-protocol.md` before finishing.
6. If the task involves UCAS Wi-Fi roaming, intermittent Tailnet, Windows Mobile Hotspot, loss of remote access, or the touch-panel recovery button, read `references/wifi-failover.md` before diagnosing or changing network behavior.

### Focus Garden authority rule

For My Focus Garden, the Raspberry Pi production tree is the authoritative latest
version: `/home/conrad/services/focus-garden` (code, templates, static UI, and
the Pi SQLite database). `D:\MyFocusGarden` is a Windows development/mirror
copy, not an authority. Before any Garden deployment, pull or compare the
current Pi files first, preserve Pi-only features such as `recent-context`, and
merge only the requested change. Never deploy the whole local tree over Pi
without an explicit file-by-file comparison and a dated rollback backup. After
deployment, test the Pi service and its actual Tailnet endpoint; then mirror the
validated result back to Windows and update the handoff documents.

## Safety boundaries

- Never print or store passwords, DeepSeek API keys, PushPlus tokens, ntfy topics, upload tokens, cookies, or private SSH keys.
- Do not expose Cockpit, File Browser, Monaco Lite, SSH, Syncthing GUI, raw data directories, or credential files to the public internet.
- Treat My Focus Garden as a private Tailnet application: its Pi service stays loopback-only on `127.0.0.1:8838`, and its `:8460` Tailscale Serve route must never use Funnel.
- Keep Focus Garden's authoritative SQLite database on the Pi. Its archive mirror is for recovery, not a second writer; do not turn the Syncthing relationship into two-way writes.
- Do not copy, publish, or place Focus Garden's copyrighted local game assets into a repository or its Syncthing archive.
- Do not modify Obsidian Tasks, task dates, completion status, or Pomodoro progress from the Raspberry Pi.
- Treat Pomodoro as medium-reliability positive evidence only. In this system, `1 🍅 = 40 minutes`, not 25.
- Treat AI reports as interpretations, not facts. Prefer raw facts, context snapshots, deterministic metrics, and user feedback when resolving conflicts.

## Windows-to-Pi connectivity rule

- Use Tailscale MagicDNS `pi.taild4d3f7.ts.net` for every Windows-to-Pi runtime connection: application settings, plugin defaults, SSH targets, scripts, scheduled tasks, and health checks.
- Do not pin `100.109.89.52` or a `192.168.*` DHCP address in runtime configuration. Keep an IP only as time-bound diagnostic evidence in handoff records.
- Treat `pi.local` as a LAN-management or backward-compatible SSH alias only. When preserving that alias in `C:\Users\15345\.ssh\config`, make it resolve to MagicDNS; an existing `HostKeyAlias=pi.local` may remain solely for known-host fingerprint matching.
- Before adding or changing a Windows-to-Pi connection, search the relevant runtime sources and settings for literal Pi IPs and replace applicable ones with MagicDNS. Verify with a non-mutating SSH command before relying on the new target.

## UCAS Wi-Fi and on-demand hotspot recovery

- Do not infer that the UCAS network is generally unstable from Pi failures. Compare the Windows and Pi band/BSSID first; the Pi 3 currently uses 2.4 GHz and has been observed roaming between UCAS access points while the computer uses a stable 5 GHz BSSID.
- `wifi-failover.timer` judges loss from the Pi's own default route plus IPv4 and IPv6 external probes. Windows peer availability must never trigger a switch because the computer may be away, asleep, or powered off.
- Windows Mobile Hotspot `XYH 0563` is user-controlled and on-demand. Do not install or enable an automatic hotspot startup/watchdog unless the user explicitly changes this policy. Keep the scripts under `D:\tools\pi-network-fallback` as optional manual tools.
- The Pi keeps `netplan-wlan0-XYH 0563` as a lower-priority saved profile. If hotspot activation fails, the shared failover backend must immediately restore UCAS and enter cooldown.
- Preserve the touch-panel `一键恢复热点连接` button. It uses the shared failover script rather than a separate raw `nmcli` path.
- Do not pin a UCAS BSSID until roaming evidence is collected and the hotspot connection plus safe UCAS return have both been physically verified.

## Issue-feedback backlog

When the user mentions problem feedback, issue backlog, bug backlog, 网页问题反馈, 统一处理问题, or asks Codex to process collected issues:

1. Read `references/issue-feedback.md`.
2. Start from the Raspberry Pi file `data/issue_feedback/UNREVIEWED.md`.
3. Classify each open issue before changing code: Next Action, half-hour report, data collection, notification, rules, UI, security, docs, or unknown.
4. Preserve raw issue JSON as audit history. Mark resolved only after the fix or decision is verified.

## Useful command entry points

Use the bundled health script for a quick document/path check:

```powershell
python C:\Users\15345\.codex\skills\pi-ops-system-context\scripts\check_ops_docs.py
```

This script only checks presence and modified times. It does not read secrets or modify files.
