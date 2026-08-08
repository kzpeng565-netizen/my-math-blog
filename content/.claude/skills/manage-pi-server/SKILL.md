---
name: manage-pi-server
description: Manage and continue configuring Conrad's Raspberry Pi 3 Model B personal server. Use for SSH access, Cockpit or File Browser administration, system/service diagnostics, touch-panel dashboard changes, package installation, backups, and locating the server's important configuration or data files.
---

# Manage Pi Server

Read `references/server-layout.md` before changing this server. It is the source of truth for current addresses, services, ports, and important paths.

Read `D:\mathblog\quartz\content\非笔记内容\工作流程与系统运维\树莓派服务器Web管理指南.md` when the user asks how to access, use, or troubleshoot Cockpit or File Browser.

## Connect safely

1. Try `pi.local` first; fall back to the last known IP in the reference.
2. Use the dedicated key configured in the local OpenSSH config: `ssh -o BatchMode=yes pi.local`.
3. When falling back to an IP not covered by the local SSH config, use `ssh -i ~/.ssh/pi_server_ed25519 -o IdentitiesOnly=yes -o BatchMode=yes conrad@<ip>`.
4. Never regenerate, replace, copy, or expose the dedicated private key unless the user explicitly requests key maintenance.
5. Password authentication remains available only for recovery. Never store or print passwords in this skill, workspace files, commands, logs, or final responses. If key authentication fails and recovery is required, ask the user to enter the credential ephemerally.

Before a mutation, collect the smallest relevant status snapshot:

```bash
hostname
hostname -I
systemctl is-system-running
free -h
df -h /
vcgencmd get_throttled
```

## Choose the management surface

- Use Cockpit for system status, logs, services, storage, and a browser terminal.
- Use File Browser for files under the restricted workspace root and basic text editing.
- Use SSH for installation, configuration, recovery, and verification.
- Use the local Xorg/Tkinter panel only for the on-device dashboard, recent-file view, and local controls.

Do not expose Cockpit or File Browser directly to the public internet. Treat their TLS certificates as locally generated self-signed certificates unless the reference says otherwise.

## Make changes

1. Inspect the existing file, unit, package, or process.
2. Preserve unrelated user changes.
3. Back up fragile configuration before editing it.
4. Prefer systemd units and Debian packages where appropriate.
5. Restart only the affected service when possible.
6. Verify active state, listening port, recent journal, resource use, and the actual HTTP endpoint when applicable.
7. Reboot only when required, then verify the service again after boot.

Keep File Browser restricted to its documented root. Do not add symlinks that escape the root and do not enable its command runner without explicit approval.

## Maintain the handoff

When an intentional change modifies a documented hostname, address, port, service, login method, or important path, update `references/server-layout.md` in the same task. Never add credentials to the reference.
