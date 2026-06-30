from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import dns_propagation
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestDnsPropagationCommands(unittest.TestCase):
    def _ctx(self) -> dict:
        cfg = SimpleNamespace(
            base_url="https://www.wixapis.com",
            timeout_s=30.0,
            access_token=None,
            api_key="acct-api-key",
            account_id="acct-001",
            app_id=None,
            app_secret=None,
            instance_id=None,
            has_official_app_auth=False,
        )
        return {
            "cfg": cfg,
            "env_file": "/tmp/.env",
            "tool": "wix-safe-agent-cli",
            "tool_version": "0.0.0",
            "command_str": "wix-safe-agent-cli dns-propagation get",
            "apply": False,
            "yes": False,
            "verbose": False,
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
        }

    def test_parser_recognizes_dns_propagation_get(self) -> None:
        parser = build_parser()
        parsed = parser.parse_args(
            ["dns-propagation", "get", "--dns-propagation-id", "example.com"]
        )

        self.assertEqual(parsed.dns_propagation_cmd, "get")
        self.assertFalse(parsed.write_capable)
        self.assertEqual(parsed.func.__name__, "cmd_dns_propagation_get")

    @patch("wix_safe_agent_cli.commands.dns_propagation.HttpClient")
    def test_dns_propagation_get_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {"dnsPropagation": {"id": "example.com", "status": "IN_PROGRESS"}}
        )
        args = SimpleNamespace(dns_propagation_id="example.com")
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = dns_propagation.cmd_dns_propagation_get(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["method"], "dns-propagation.get")
        self.assertEqual(
            payload["request"],
            {"method": "GET", "path": "/premium/domains/v1/dns-propagations/example.com"},
        )

        call = mock_client.return_value.request.call_args
        headers = call.kwargs["headers"]
        self.assertEqual(headers["Authorization"], "acct-api-key")
        self.assertEqual(headers["wix-account-id"], "acct-001")

    @patch("wix_safe_agent_cli.commands.dns_propagation.HttpClient")
    def test_dns_propagation_get_rejects_missing_tld(self, mock_client: unittest.mock.MagicMock) -> None:
        _ = mock_client
        args = SimpleNamespace(dns_propagation_id="example")
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = dns_propagation.cmd_dns_propagation_get(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("must include a TLD", payload["error"])
