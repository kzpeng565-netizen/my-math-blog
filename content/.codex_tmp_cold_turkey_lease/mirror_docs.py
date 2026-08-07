from pathlib import Path


ROOT = Path("/home/conrad/workspace/activitywatch-advisor")
MARKER = "2026-08-07：Cold Turkey lease 休眠补偿部署"
TEXT = (
    "\n\n## 2026-08-07：Cold Turkey lease 休眠补偿部署\n\n"
    "==Windows agent 继续使用可暂停的 Cold Turkey `-start/-stop` lease，不使用 `-lock 30`。"
    "agent 持久化 `lease_id` 与绝对到期时间，在启动、轮询和唤醒后的第一次循环回收过期 lease；"
    "Pi release 改为 durable pending，旧 release 不会关闭新的 lease。==\n\n"
    "==本次修改已重启 `activitywatch-advisor-web.service` 与 `focus-garden.service`。"
    "Windows agent 测试 6/6、Advisor intervention 测试 6/6、Focus Garden 测试 23/23 通过；"
    "Advisor 全量测试有 2 项既有 task/Next Action fixture 失败，未修改相关模块。==\n\n"
    "<!-- ai_provenance: source=codex; date=2026-08-07; verification=local-tests-and-pi-service-restart -->\n"
)

for name in ("PROJECT_STATE.md", "DECISIONS.md", "NEXT_STEPS.md", "PI_SERVER_HANDOFF.md"):
    path = ROOT / name
    content = path.read_text(encoding="utf-8")
    if MARKER not in content:
        path.write_text(content.rstrip() + TEXT, encoding="utf-8")
        print(f"updated {name}")
    else:
        print(f"skipped {name}")
