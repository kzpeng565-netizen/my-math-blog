# Update protocol

After changing code, configuration, routes, prompts, data schemas, or operating rules, update the handoff layer.

## Always consider

```text
D:/mathblog/quartz/content/非笔记内容/工作流程与系统运维/PROJECT_STATE.md
D:/mathblog/quartz/content/非笔记内容/工作流程与系统运维/DECISIONS.md
D:/mathblog/quartz/content/非笔记内容/工作流程与系统运维/NEXT_STEPS.md
D:/mathblog/quartz/content/非笔记内容/工作流程与系统运维/PI_SERVER_HANDOFF.md
```

Mirror important project-level changes to:

```text
/home/conrad/workspace/activitywatch-advisor/PROJECT_STATE.md
/home/conrad/workspace/activitywatch-advisor/DECISIONS.md
/home/conrad/workspace/activitywatch-advisor/NEXT_STEPS.md
/home/conrad/workspace/activitywatch-advisor/PI_SERVER_HANDOFF.md
```

## Also update when relevant

- Data paths, APIs, JSON schemas: `树莓派行为数据与接口索引.md` and `docs/behavior-data-and-interfaces.md`
- Next Action behavior or UI: `树莓派下一步行动助手架构.md` and `docs/next-action-web-architecture.md`
- Focus Garden behavior, UI, rewards, deployment, backup, or Next Action integration: `我的专注花园/00-交接总览.md`, the matching numbered garden document, and `我的专注花园/05-Pi迁移验收与恢复清单.md`
- Large architecture changes: `树莓派行为系统总流程图.md` and rendered JPG if necessary
- Ports, services, public/private exposure: `manage-pi-server/references/server-layout.md`

## Verification notes

Record in the final answer:

- files changed;
- tests run;
- services restarted;
- unresolved follow-ups;
- whether handoff docs were updated.
