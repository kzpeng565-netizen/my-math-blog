from __future__ import annotations

import json
import subprocess
from pathlib import Path


LOCAL_DOCS = [
    Path(r"D:/mathblog/quartz/content/非笔记内容/工作流程与系统运维/PROJECT_STATE.md"),
    Path(r"D:/mathblog/quartz/content/非笔记内容/工作流程与系统运维/DECISIONS.md"),
    Path(r"D:/mathblog/quartz/content/非笔记内容/工作流程与系统运维/NEXT_STEPS.md"),
    Path(r"D:/mathblog/quartz/content/非笔记内容/工作流程与系统运维/PI_SERVER_HANDOFF.md"),
    Path(r"D:/mathblog/quartz/content/非笔记内容/工作流程与系统运维/树莓派行为数据与接口索引.md"),
    Path(r"D:/mathblog/quartz/content/非笔记内容/工作流程与系统运维/树莓派下一步行动助手架构.md"),
    Path(r"D:/mathblog/quartz/content/非笔记内容/工作流程与系统运维/树莓派行为系统总流程图.md"),
]

REMOTE_DOCS = [
    "/home/conrad/workspace/activitywatch-advisor/PROJECT_STATE.md",
    "/home/conrad/workspace/activitywatch-advisor/DECISIONS.md",
    "/home/conrad/workspace/activitywatch-advisor/NEXT_STEPS.md",
    "/home/conrad/workspace/activitywatch-advisor/PI_SERVER_HANDOFF.md",
    "/home/conrad/workspace/activitywatch-advisor/docs/behavior-data-and-interfaces.md",
    "/home/conrad/workspace/activitywatch-advisor/docs/next-action-web-architecture.md",
    "/home/conrad/workspace/activitywatch-advisor/docs/system-flowchart.md",
]


def local_status(path: Path) -> dict[str, object]:
    try:
        stat = path.stat()
        return {"path": str(path), "exists": True, "mtime": stat.st_mtime, "size": stat.st_size}
    except OSError:
        return {"path": str(path), "exists": False}


def remote_status() -> list[dict[str, object]]:
    script = "python3 - <<'PY'\nimport json, os\npaths = " + repr(REMOTE_DOCS) + "\nrows=[]\nfor p in paths:\n    try:\n        s=os.stat(p); rows.append({'path':p,'exists':True,'mtime':s.st_mtime,'size':s.st_size})\n    except OSError:\n        rows.append({'path':p,'exists':False})\nprint(json.dumps(rows, ensure_ascii=False))\nPY"
    try:
        result = subprocess.run(
            ["ssh", "-o", "BatchMode=yes", "pi.local", script],
            text=True,
            capture_output=True,
            check=True,
            timeout=20,
        )
        return json.loads(result.stdout)
    except Exception as error:
        return [{"error": type(error).__name__, "detail": str(error)}]


def main() -> int:
    print(json.dumps({"local": [local_status(p) for p in LOCAL_DOCS], "remote": remote_status()}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
