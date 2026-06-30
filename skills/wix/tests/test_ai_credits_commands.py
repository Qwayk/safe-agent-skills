from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import ai_credits
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def __init__(self) -> None:
        self.writes: list[tuple[str, dict]] = []

    def write(self, action: str, payload: dict) -> None:
        self.writes.append((action, payload))


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestAiCreditsCommands(unittest.TestCase):
    def _ctx(self, *, cfg_override: dict | None = None, verbose: bool = False) -> dict:
        cfg = SimpleNamespace(
            base_url="https://www.wixapis.com",
            timeout_s=30.0,
            app_id=None,
            app_secret=None,
            instance_id=None,
            access_token="token-legacy",
            api_key="acct-api-key",
            account_id=None,
            has_official_app_auth=False,
        )
        if cfg_override:
            for key, value in cfg_override.items():
                setattr(cfg, key, value)
        return {
            "cfg": cfg,
            "env_file": "/tmp/.env",
            "verbose": verbose,
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
        }

    def test_parser_recognizes_ai_credits_get_balance(self) -> None:
        parser = build_parser()
        parsed = parser.parse_args(["ai-credits", "get-balance"])

        self.assertEqual(parsed.ai_credits_cmd, "get-balance")
        self.assertFalse(parsed.write_capable)
        self.assertEqual(parsed.func.__name__, "cmd_ai_credits_get_balance")

    @patch("wix_safe_agent_cli.commands.ai_credits.HttpClient")
    def test_ai_credits_get_balance_builds_expected_request_and_headers(
        self, mock_client: unittest.mock.MagicMock
    ) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {"periodicCredits": {"balance": 12}, "topUpCredits": {"balance": 3}}
        )
        args = SimpleNamespace()
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = ai_credits.cmd_ai_credits_get_balance(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["method"], "ai-credits.get-balance")
        self.assertEqual(
            payload["request"],
            {"method": "POST", "path": "/appmarket/credittransactions/v1/credit-transactions/balance", "body": {}},
        )
        self.assertEqual(payload["response"], {"periodicCredits": {"balance": 12}, "topUpCredits": {"balance": 3}})
        self.assertEqual(ctx["audit"].writes[0][0], "ai-credits.get-balance")

        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["method"], "POST")
        self.assertTrue(call.kwargs["url"].endswith("/appmarket/credittransactions/v1/credit-transactions/balance"))
        self.assertEqual(call.kwargs["json_body"], {})
        headers = call.kwargs["headers"]
        self.assertEqual(headers, {"Authorization": "acct-api-key"})

    @patch("wix_safe_agent_cli.commands.ai_credits.HttpClient")
    def test_ai_credits_get_balance_rejects_missing_api_key(self, mock_client: unittest.mock.MagicMock) -> None:
        _ = mock_client
        args = SimpleNamespace()
        ctx = self._ctx(cfg_override={"api_key": None})

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = ai_credits.cmd_ai_credits_get_balance(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("Missing required AI Credits API key", payload["error"])
