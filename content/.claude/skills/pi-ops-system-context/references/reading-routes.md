# Reading routes

Choose the narrowest route that answers the user's request.

## Next Action web UI

Read:

```text
PROJECT_STATE.md
PI_SERVER_HANDOFF.md
树莓派下一步行动助手架构.md
docs/next-action-web-architecture.md
src/web_app.py
src/next_action.py
```

Use for: current suggestion, DeepSeek V4 Pro thinking, password-free Tailnet access on `:8450`, suggestion display, feedback buttons, issue feedback, active suggestion, JSON validation, and prompt/rule changes. The former public `:10000` Funnel is removed and must not be restored without independent authentication.

## My Focus Garden

Read:

```text
PROJECT_STATE.md
PI_SERVER_HANDOFF.md
我的专注花园/00-交接总览.md
我的专注花园/01-数据来源与处理.md
我的专注花园/02-游戏架构.md
我的专注花园/04-运维与扩展手册.md
我的专注花园/05-Pi迁移验收与恢复清单.md
D:/MyFocusGarden/README.md
D:/MyFocusGarden/focus_garden/server.py
D:/MyFocusGarden/config/settings.json
```

Use for: garden UI or rewards, Pi deployment, SQLite authority and recovery, Syncthing archive, focus profiles, safe focus mode, the native Next Action menu, or Tailnet access on `:8460`. Read the corresponding Next Action route too when changing the integrated menu or its fixed loopback proxy.

## Half-hour reports

Read:

```text
PI_SERVER_HANDOFF.md
DECISIONS.md
树莓派行为数据与接口索引.md
docs/behavior-data-and-interfaces.md
src/semantic_analysis.py
src/behavior_advisor.py
```

Use for: AI state interpretation, PushPlus report text, latest 3 web reports, semantic timelines, mixing metrics, shadow interventions, and report feedback.

## Data collection

Read:

```text
树莓派行为数据与接口索引.md
树莓派行为系统总流程图.md
PI_SERVER_HANDOFF.md
```

Use for: phone/tablet Automate uploads, computer ActivityWatch, Syncthing, Obsidian context exporter, sleep boundary, Pomodoro/task/profile input, and stale context questions.

## Tailscale, Funnel, Serve, and login

Read:

```text
manage-pi-server/references/server-layout.md
PI_SERVER_HANDOFF.md
PROJECT_STATE.md
```

Use for: public Funnel, tailnet-only Serve, Android VPN conflicts, Clash Meta, ports, cookies, password-free Next Action access, Focus Garden `:8460`, and endpoint reachability.

## Issue feedback backlog

Read:

```text
references/issue-feedback.md
/home/conrad/workspace/activitywatch-advisor/data/issue_feedback/UNREVIEWED.md
```

Then route by category:

- Next Action or AI suggestion quality: `src/next_action.py`, `src/web_app.py`, `docs/next-action-web-architecture.md`
- Half-hour report quality: latest report JSON/MD plus half-hour processing docs
- Data issue: facts/context/upload docs and relevant data directory
- Notification issue: PushPlus/ntfy docs and receipt directories
- Rule issue: `DECISIONS.md`, `NEXT_STEPS.md`, architecture docs
- UI issue: `src/web_app.py`, browser-rendered behavior if available

## Documentation-only updates

Read:

```text
PROJECT_STATE.md
DECISIONS.md
NEXT_STEPS.md
PI_SERVER_HANDOFF.md
```

If a data path or API is involved, also read `树莓派行为数据与接口索引.md`.

If a flow changes, also read `树莓派行为系统总流程图.md`.
