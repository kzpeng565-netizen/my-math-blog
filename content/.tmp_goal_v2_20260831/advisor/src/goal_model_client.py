from __future__ import annotations

import json
import os
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


GOAL_RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["answer", "assessment", "plan_changes", "approval_request"],
    "properties": {
        "answer": {"type": "string"},
        "assessment": {"type": "object"},
        "plan_changes": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": True,
                "properties": {
                    "plan_item_id": {"type": "string"},
                    "recommended_date": {"type": ["string", "null"]},
                    "deep_minutes": {"type": ["integer", "null"]},
                    "status": {"type": ["string", "null"]},
                    "reason": {"type": ["string", "null"]},
                },
            },
        },
        "approval_request": {"type": ["object", "null"]},
    },
}


def _extract_output_text(response: dict[str, Any]) -> str:
    direct = response.get("output_text")
    if isinstance(direct, str) and direct.strip():
        return direct
    fragments: list[str] = []
    output = response.get("output")
    if isinstance(output, list):
        for item in output:
            if not isinstance(item, dict):
                continue
            content = item.get("content")
            if not isinstance(content, list):
                continue
            for part in content:
                if not isinstance(part, dict):
                    continue
                text = part.get("text")
                if isinstance(text, str) and text:
                    fragments.append(text)
    if fragments:
        return "".join(fragments)
    # Some OpenAI-compatible gateways expose a Responses endpoint but retain
    # a Chat-Completions-shaped response. Accept it without changing protocol.
    choices = response.get("choices")
    if isinstance(choices, list) and choices and isinstance(choices[0], dict):
        message = choices[0].get("message")
        if isinstance(message, dict) and isinstance(message.get("content"), str):
            return str(message["content"])
    return ""


def _safe_http_error(error: HTTPError) -> str:
    return f"HTTP {int(error.code)}"


def request_goal_json(
    model: dict[str, Any],
    messages: list[dict[str, str]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    env_name = str(model.get("api_key_env") or "GOAL_AGENT_API_KEY")
    api_key = os.environ.get(env_name)
    if not api_key:
        raise RuntimeError(f"{env_name} is not configured")

    endpoint = str(model.get("endpoint") or "").strip()
    parsed = urlparse(endpoint)
    if parsed.scheme != "https" or not parsed.netloc:
        raise RuntimeError("Goal Agent model endpoint must be an HTTPS URL")

    instructions = "\n\n".join(
        str(item.get("content") or "")
        for item in messages
        if item.get("role") == "system"
    ).strip()
    input_items = [
        {
            "role": str(item.get("role") or "user"),
            "content": str(item.get("content") or ""),
        }
        for item in messages
        if item.get("role") != "system"
    ]
    payload: dict[str, Any] = {
        "model": str(model.get("name") or "gpt-5.6-sol"),
        "instructions": instructions,
        "input": input_items,
        "reasoning": {"effort": str(model.get("reasoning_effort") or "medium")},
        "max_output_tokens": int(model.get("max_output_tokens") or 4500),
        "store": False,
    }
    use_schema = bool(model.get("structured_output", True))
    if use_schema:
        payload["text"] = {
            "format": {
                "type": "json_schema",
                "name": "goal_agent_response",
                "strict": True,
                "schema": GOAL_RESPONSE_SCHEMA,
            }
        }

    retries = max(0, int(model.get("retries") or 0))
    timeout = max(5, int(model.get("timeout_seconds") or 80))
    attempts: list[dict[str, Any]] = []
    last_error: Exception | None = None
    schema_fallback_used = False

    for attempt in range(retries + 2):
        record: dict[str, Any] = {
            "attempt": attempt + 1,
            "structured_output": "text" in payload,
        }
        request = Request(
            endpoint,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            method="POST",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )
        try:
            with urlopen(request, timeout=timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
            if not isinstance(body, dict):
                raise ValueError("model response is not an object")
            content = _extract_output_text(body)
            if not content.strip():
                raise ValueError("model response has no output text")
            report = json.loads(content)
            if not isinstance(report, dict):
                raise ValueError("Goal Agent output is not a JSON object")
            for required in ("answer", "assessment", "plan_changes", "approval_request"):
                if required not in report:
                    raise ValueError(f"Goal Agent output is missing {required}")
            record["usage"] = body.get("usage", {})
            record["status"] = body.get("status")
            attempts.append(record)
            return report, {
                "provider": str(model.get("provider") or "openai_compatible"),
                "protocol": "responses",
                "model": str(body.get("model") or model.get("name") or ""),
                "reasoning_effort": payload["reasoning"]["effort"],
                "usage": body.get("usage", {}),
                "request_count": len(attempts),
                "attempts": attempts,
                "structured_output": "text" in payload,
                "schema_fallback_used": schema_fallback_used,
            }
        except HTTPError as error:
            last_error = error
            record["error"] = _safe_http_error(error)
            attempts.append(record)
            # A compatible Responses gateway may not implement JSON Schema.
            # Retry once on the same model/protocol with the prompt-only JSON
            # contract; never fall back to DeepSeek or another provider.
            if error.code in {400, 404, 422} and "text" in payload:
                payload.pop("text", None)
                schema_fallback_used = True
                continue
        except (
            URLError,
            TimeoutError,
            UnicodeDecodeError,
            json.JSONDecodeError,
            KeyError,
            TypeError,
            ValueError,
        ) as error:
            last_error = error
            record["error"] = f"{type(error).__name__}: {error}"
            attempts.append(record)
        if len(attempts) <= retries + 1:
            time.sleep(min(2 ** max(0, len(attempts) - 1), 4))
            continue
        break

    detail = f"{type(last_error).__name__}: {last_error}" if last_error else "unknown error"
    if isinstance(last_error, HTTPError):
        detail = _safe_http_error(last_error)
    raise RuntimeError(f"GPT-5.6 Sol Responses request failed: {detail}")
