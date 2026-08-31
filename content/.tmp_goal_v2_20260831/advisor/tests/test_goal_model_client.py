from __future__ import annotations

import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from goal_model_client import _extract_output_text, request_goal_json


class GoalModelClientTests(unittest.TestCase):
    def test_extracts_responses_output_text(self) -> None:
        self.assertEqual(
            _extract_output_text(
                {
                    "output": [
                        {
                            "type": "message",
                            "content": [
                                {
                                    "type": "output_text",
                                    "text": '{"answer":"ok"}',
                                }
                            ],
                        }
                    ]
                }
            ),
            '{"answer":"ok"}',
        )

    def test_uses_responses_reasoning_and_never_deepseek_fields(self) -> None:
        response = MagicMock()
        response.read.return_value = json.dumps(
            {
                "model": "gpt-5.6-sol",
                "status": "completed",
                "output": [
                    {
                        "type": "message",
                        "content": [
                            {
                                "type": "output_text",
                                "text": json.dumps(
                                    {
                                        "answer": "ok",
                                        "assessment": {},
                                        "plan_changes": [],
                                        "approval_request": None,
                                    }
                                ),
                            }
                        ],
                    }
                ],
                "usage": {"input_tokens": 10, "output_tokens": 5},
            }
        ).encode("utf-8")
        context = MagicMock()
        context.__enter__.return_value = response
        model = {
            "provider": "openai_compatible",
            "protocol": "responses",
            "endpoint": "https://example.invalid/v1/responses",
            "name": "gpt-5.6-sol",
            "api_key_env": "GOAL_AGENT_API_KEY",
            "reasoning_effort": "medium",
            "max_output_tokens": 4500,
            "timeout_seconds": 10,
            "retries": 0,
            "structured_output": True,
        }
        with patch.dict(os.environ, {"GOAL_AGENT_API_KEY": "test-secret"}):
            with patch("goal_model_client.urlopen", return_value=context) as open_url:
                report, generation = request_goal_json(
                    model,
                    [
                        {"role": "system", "content": "system"},
                        {"role": "user", "content": "user"},
                    ],
                )
        request = open_url.call_args.args[0]
        payload = json.loads(request.data.decode("utf-8"))
        self.assertEqual(payload["model"], "gpt-5.6-sol")
        self.assertEqual(payload["reasoning"], {"effort": "medium"})
        self.assertEqual(payload["max_output_tokens"], 4500)
        self.assertFalse(payload["store"])
        self.assertIn("text", payload)
        self.assertNotIn("thinking", payload)
        self.assertNotIn("messages", payload)
        self.assertEqual(report["answer"], "ok")
        self.assertEqual(generation["protocol"], "responses")
        self.assertEqual(generation["model"], "gpt-5.6-sol")

    def test_missing_key_fails_without_fallback_provider(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "GOAL_AGENT_API_KEY"):
                request_goal_json(
                    {
                        "endpoint": "https://example.invalid/v1/responses",
                        "name": "gpt-5.6-sol",
                    },
                    [{"role": "user", "content": "hello"}],
                )


if __name__ == "__main__":
    unittest.main()
