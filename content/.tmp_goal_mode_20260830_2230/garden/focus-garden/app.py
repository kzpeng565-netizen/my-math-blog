from __future__ import annotations

import argparse
import os
import threading
import webbrowser
from pathlib import Path

from focus_garden.server import GardenHTTPServer, GardenService, start_reconciler


def main() -> None:
    parser = argparse.ArgumentParser(description="我的专注花园")
    parser.add_argument("--port", type=int, default=8838)
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--dry-run", action="store_true", help="不真正调用 Cold Turkey")
    args = parser.parse_args()
    if args.dry_run:
        os.environ["FOCUS_GARDEN_DRY_RUN"] = "1"
    root = Path(__file__).resolve().parent
    url = f"http://127.0.0.1:{args.port}"
    service = GardenService(root)
    try:
        server = GardenHTTPServer(("127.0.0.1", args.port), service)
    except OSError as exc:
        if getattr(exc, "winerror", None) == 10048 or getattr(exc, "errno", None) == 98:
            if not args.no_browser:
                webbrowser.open(url)
            return
        raise
    start_reconciler(service)
    if not args.no_browser:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    print(f"我的专注花园已启动：{url}")
    print("按 Ctrl+C 停止本地服务。")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()

