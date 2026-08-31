# Service map

## Public and private web entry points

```text
Phone usage public Funnel: https://pi.taild4d3f7.ts.net -> 127.0.0.1:8765
Next Action tailnet-only Serve: https://pi.taild4d3f7.ts.net:8450 -> 127.0.0.1:8767 (no separate password)
Focus Garden tailnet-only Serve: https://pi.taild4d3f7.ts.net:8460 -> 127.0.0.1:8838
Monaco Lite tailnet-only Serve: https://pi.taild4d3f7.ts.net:8443 -> 127.0.0.1:8766
```

Do not expose Cockpit, File Browser, Monaco Lite, SSH, Syncthing GUI, or raw data directories through public Funnel.

## Systemd services and timers

```text
activitywatch-advisor-web.service
focus-garden.service
focus-garden-backup.timer
phone-usage-receiver.service
activitywatch-advisor.timer
activitywatch-advisor.service
activitywatch-advisor-daily-life.timer
bedtime-reminder.timer
sysadmin-time-guard.timer
wifi-failover.service
wifi-failover.timer
syncthing@conrad.service
tailscaled.service
```

## Common verification commands

```bash
ssh -o BatchMode=yes pi.taild4d3f7.ts.net
systemctl status activitywatch-advisor-web.service --no-pager -l
systemctl status phone-usage-receiver.service --no-pager -l
systemctl list-timers 'activitywatch*' 'bedtime*' 'sysadmin*' --no-pager
systemctl status focus-garden.service focus-garden-backup.timer --no-pager -l
systemctl status wifi-failover.timer wifi-failover.service --no-pager -l
sudo cat /var/lib/wifi-failover/state.json
sudo tail -n 20 /var/lib/wifi-failover/events.jsonl
curl -fsS http://127.0.0.1:8838/api/health
ss -lntp | grep -E ':(8765|8766|8767|8838|443|8443|8450|8460) '
tailscale funnel status
tailscale serve status
```

Before mutations, collect the status snapshot required by `manage-pi-server`.
