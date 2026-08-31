from __future__ import annotations

import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
NODE = Path(r"C:\Program Files\nodejs\node.exe")
ENTRY = PROJECT_ROOT / "src" / "main.mjs"


def main() -> int:
    creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
    completed = subprocess.run(
        [str(NODE), str(ENTRY)],
        cwd=PROJECT_ROOT,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=creation_flags,
        check=False,
    )
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
