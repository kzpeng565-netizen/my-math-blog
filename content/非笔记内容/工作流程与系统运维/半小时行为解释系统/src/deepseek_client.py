from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def interpret_with_deepseek(
    settings: dict[str, Any],
    prompt_path: Path,
    computer_facts: dict[str, Any],
    phone_facts: dict[str, Any],
    cross_device_facts: dict[str, Any],
) -> dict[str, Any]:
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError("DEEPSEEK_API_KEY is not configured")

    model = settings["model"]
    system_prompt = prompt_path.read_text(encoding="utf-8")
    evidence = {
        "computer_facts": computer_facts,
        "phone_facts": phone_facts,
        "cross_device_facts": cross_device_facts,
    }
    payload = {
        "model": model["name"],
        "messages": [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": "请根据以下两个独立事实层输出 JSON 报告：\n"
                + json.dumps(evidence, ensure_ascii=False, separators=(",", ":")),
            },
        ],
        "thinking": {"type": model.get("thinking", "disabled")},
        "response_format": {"type": "json_object"},
        "max_tokens": int(model["max_tokens"]),
        "stream": False,
    }
    request_data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    retries = int(model.get("retries", 2))
    last_error: Exception | None = None

    for attempt in range(retries + 1):
        request = Request(
            model["endpoint"],
            data=request_data,
            method="POST",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )
        try:
            with urlopen(request, timeout=int(model["timeout_seconds"])) as response:
                response_body = json.loads(response.read().decode("utf-8"))
            content = response_body["choices"][0]["message"].get("content", "")
            if not content.strip():
                raise ValueError("DeepSeek returned empty content")
            report = json.loads(content)
            if not isinstance(report, dict):
                raise ValueError("DeepSeek output is not a JSON object")
            report["_generation"] = {
                "provider": "DeepSeek",
                "model": response_body.get("model", model["name"]),
                "finish_reason": response_body["choices"][0].get("finish_reason"),
                "usage": response_body.get("usage", {}),
            }
            return report
        except (HTTPError, URLError, TimeoutError, KeyError, ValueError, json.JSONDecodeError) as error:
            last_error = error
            if attempt < retries:
                time.sleep(2**attempt)
                continue
            break

    raise RuntimeError(f"DeepSeek request failed: {type(last_error).__name__}: {last_error}")
