# Canonical ops documents

Use these documents as the source map for Conrad's Raspberry Pi behavior advisor.

## Local Obsidian documents

```text
D:/mathblog/quartz/content/非笔记内容/工作流程与系统运维/PROJECT_STATE.md
D:/mathblog/quartz/content/非笔记内容/工作流程与系统运维/DECISIONS.md
D:/mathblog/quartz/content/非笔记内容/工作流程与系统运维/NEXT_STEPS.md
D:/mathblog/quartz/content/非笔记内容/工作流程与系统运维/PI_SERVER_HANDOFF.md
D:/mathblog/quartz/content/非笔记内容/工作流程与系统运维/树莓派行为数据与接口索引.md
D:/mathblog/quartz/content/非笔记内容/工作流程与系统运维/树莓派下一步行动助手架构.md
D:/mathblog/quartz/content/非笔记内容/工作流程与系统运维/树莓派行为系统总流程图.md
D:/mathblog/quartz/content/非笔记内容/工作流程与系统运维/树莓派UCAS无线漫游与电脑热点自动回退.md
D:/mathblog/quartz/content/非笔记内容/工作流程与系统运维/我的专注花园/00-交接总览.md
D:/mathblog/quartz/content/非笔记内容/工作流程与系统运维/我的专注花园/01-数据来源与处理.md
D:/mathblog/quartz/content/非笔记内容/工作流程与系统运维/我的专注花园/02-游戏架构.md
D:/mathblog/quartz/content/非笔记内容/工作流程与系统运维/我的专注花园/04-运维与扩展手册.md
D:/mathblog/quartz/content/非笔记内容/工作流程与系统运维/我的专注花园/05-Pi迁移验收与恢复清单.md
```

## Raspberry Pi project documents

```text
/home/conrad/workspace/activitywatch-advisor/PROJECT_STATE.md
/home/conrad/workspace/activitywatch-advisor/DECISIONS.md
/home/conrad/workspace/activitywatch-advisor/NEXT_STEPS.md
/home/conrad/workspace/activitywatch-advisor/PI_SERVER_HANDOFF.md
/home/conrad/workspace/activitywatch-advisor/docs/behavior-data-and-interfaces.md
/home/conrad/workspace/activitywatch-advisor/docs/next-action-web-architecture.md
/home/conrad/workspace/activitywatch-advisor/docs/system-flowchart.md
```

## Wi-Fi failover implementation

```text
/home/conrad/workspace/activitywatch-advisor/scripts/wifi_failover.py
/home/conrad/workspace/activitywatch-advisor/config/wifi_failover.json
/etc/systemd/system/wifi-failover.service
/etc/systemd/system/wifi-failover.timer
/var/lib/wifi-failover/state.json
/var/lib/wifi-failover/events.jsonl
/home/conrad/touchpanel/panel.py
D:/tools/pi-network-fallback
```

## Focus Garden source and production paths

```text
D:/MyFocusGarden
D:/MyFocusGarden/focus_garden/server.py
D:/MyFocusGarden/config/settings.json
/home/conrad/services/focus-garden
/home/conrad/services/focus-garden/app.py
/home/conrad/services/focus-garden/focus_garden/server.py
/home/conrad/services/focus-garden/data/focus-garden.sqlite3
/home/conrad/workspace/focus-garden-archive/focus-garden.sqlite3
```

## Key source files

```text
/home/conrad/workspace/activitywatch-advisor/src/web_app.py
/home/conrad/workspace/activitywatch-advisor/src/next_action.py
/home/conrad/workspace/activitywatch-advisor/src/user_annotations.py
/home/conrad/workspace/activitywatch-advisor/src/issue_feedback.py
/home/conrad/workspace/activitywatch-advisor/src/obsidian_context.py
/home/conrad/workspace/activitywatch-advisor/src/daily_life_notifier.py
/home/conrad/workspace/activitywatch-advisor/src/bedtime_reminder.py
/home/conrad/workspace/activitywatch-advisor/src/sysadmin_time_guard.py
```

## Private configuration locations

Know these paths exist, but never print their contents:

```text
/home/conrad/.config/activitywatch-advisor/env
/home/conrad/.config/activitywatch-advisor/web.env
/home/conrad/.config/activitywatch-advisor/pushplus.env
/home/conrad/.config/activitywatch-advisor/ntfy.env
/home/conrad/.config/activitywatch-advisor/ntfy-halfhour.env
/home/conrad/phone_usage/token.txt
```
