from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC))

from notifications.ntfy import PRIORITY_BY_LEVEL, TAGS_BY_LEVEL, send_notification


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--level", type=int, choices=(1, 2), required=True)
    arguments = parser.parse_args()
    priority = PRIORITY_BY_LEVEL[arguments.level]
    title = f"ntfy 测试 level {arguments.level}"
    message = f"这是一条 {priority} 优先级测试通知。"
    result = send_notification(
        level=arguments.level,
        policy_id="bedtime_stop",
        title=title,
        message=message,
        priority=priority,
        tags=TAGS_BY_LEVEL[arguments.level],
    )
    print(json.dumps(result.as_dict(), ensure_ascii=False, sort_keys=True))
    return 0 if result.status == "accepted" else 1


if __name__ == "__main__":
    raise SystemExit(main())
