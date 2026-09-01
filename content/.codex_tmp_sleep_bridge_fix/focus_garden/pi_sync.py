from __future__ import annotations

import base64
import json
import os
import subprocess
import sys
from typing import Any


REMOTE_SCRIPT = r'''
import json
from pathlib import Path

ROOT = Path("/home/conrad/workspace/activitywatch-advisor")
CUTOFF = "{cutoff}"

def read(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

def early(value):
    if not value or ":" not in value:
        return False
    h, m = [int(x) for x in value[:5].split(":")]
    ch, cm = [int(x) for x in CUTOFF.split(":")]
    minute = h * 60 + m
    if minute >= 18 * 60:
        minute -= 24 * 60
    return minute <= ch * 60 + cm

events = []

for path in sorted((ROOT / "data/computer_interventions/responses").rglob("*final.json")):
    data = read(path) or {{}}
    event = data.get("event", data)
    executions = event.get("executions") or []
    if event.get("decision") == "accepted" and any(x.get("status") == "success" for x in executions):
        request_id = event.get("request_id") or path.stem
        events.append({{
            "id": "pi:intervention:" + request_id,
            "type": "intervention_accepted",
            "occurred_at": event.get("decided_at") or data.get("received_at"),
            "reason": "主动接受系统介入，并成功启用网站封锁",
            "source": "pi",
            "payload": {{"request_id": request_id, "decision": "accepted"}}
        }})

accepted = {{}}
for path in (ROOT / "data/next_action/responses").rglob("*.json"):
    data = read(path) or {{}}
    if data.get("result") == "accepted":
        accepted[data.get("suggestion_id")] = data
for path in (ROOT / "data/next_action/outcomes").rglob("*.json"):
    data = read(path) or {{}}
    sid = data.get("suggestion_id")
    if data.get("result") == "completed" and sid in accepted:
        events.append({{
            "id": "pi:next-action:" + sid,
            "type": "ai_help_completed",
            "occurred_at": data.get("received_at"),
            "reason": "主动向 AI 寻求下一步建议，接受并完成了同一任务",
            "source": "pi",
            "payload": {{"suggestion_id": sid}}
        }})

for path in sorted((ROOT / "data/statistics/daily_life").glob("*.json")):
    data = read(path) or {{}}
    sleep = data.get("phone_sleep_boundary") or {{}}
    period = data.get("period") or path.stem
    last_use = sleep.get("last_phone_use_at_night")
    if sleep.get("status") == "resolved" and sleep.get("quality") == "high" and early(last_use):
        events.append({{
            "id": "pi:early-sleep:" + str(period),
            "type": "early_sleep",
            "occurred_at": str(period) + "T23:59:00+08:00",
            "reason": "早睡估计达标：最后手机活动为 " + str(last_use) + "（阈值 " + CUTOFF + "）",
            "source": "pi",
            "payload": {{"period": period, "last_phone_use": last_use, "cutoff": CUTOFF,
                         "sleep_estimate_minutes": sleep.get("sleep_estimate_minutes_minus_20")}}
        }})

print(json.dumps({{"events": events}}, ensure_ascii=False))
'''


class PiRewardSync:
    def __init__(self, settings: dict[str, Any]):
        self.settings = settings["pi_sync"]

    def fetch(self) -> list[dict[str, Any]]:
        if not self.settings.get("enabled", True):
            return []
        script = REMOTE_SCRIPT.format(cutoff=self.settings.get("early_sleep_cutoff", "00:30"))
        if os.environ.get("FOCUS_GARDEN_PI_LOCAL") == "1":
            proc = subprocess.run(
                [sys.executable, "-"], input=script, capture_output=True,
                text=True, encoding="utf-8", timeout=30,
            )
        else:
            encoded = base64.b64encode(script.encode("utf-8")).decode("ascii")
            command = f"echo {encoded} | base64 -d | python3 -"
            proc = subprocess.run(
                ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=6", self.settings.get("host", "pi.taild4d3f7.ts.net"), command],
                capture_output=True, text=True, encoding="utf-8", timeout=30,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        if proc.returncode != 0:
            raise RuntimeError((proc.stderr or "树莓派同步失败").strip()[:500])
        return json.loads(proc.stdout)["events"]
