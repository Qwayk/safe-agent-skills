from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.commands import domains
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


class TestDomainsCommands(unittest.TestCase):
    def _ctx(self, *, cfg_override: dict | None = None, verbose: bool = False) -> dict:
        cfg = SimpleNamespace(
            base_url="https://www.wixapis.com",
            timeout_s=30.0,
            app_id=None,
            app_secret=None,
            instance_id=None,
            access_token="token-legacy",
            has_official_app_auth=False,
            api_key="acct-api-key",
            account_id="acct-001",
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

    @patch("wix_safe_agent_cli.commands.domains.HttpClient")
    def test_domains_check_availability_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"status": "AVAILABLE"})
        args = SimpleNamespace(domain="my-site.example.com")
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = domains.cmd_domains_check_availability(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["method"], "domains.check_availability")
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(payload["request"]["path"], "/domain-search/v2/check-domain-availability")
        self.assertEqual(payload["request"]["params"], {"domain": "my-site.example.com"})

        http_call = mock_client.return_value.request.call_args
        headers = http_call.kwargs["headers"]
        self.assertEqual(headers["Authorization"], "acct-api-key")
        self.assertEqual(headers["wix-account-id"], "acct-001")
        self.assertNotIn("Content-Type", headers)

    @patch("wix_safe_agent_cli.commands.domains.HttpClient")
    def test_domains_suggest_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"suggestions": []})
        args = SimpleNamespace(
            query="my shop",
            tlds_json='["com", "dev", "io"]',
            paging_limit=12,
            cursor="cursor-11",
            max_length=15,
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = domains.cmd_domains_suggest(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["method"], "domains.suggest")
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(payload["request"]["path"], "/domain-search/v2/suggest-domains")
        params = payload["request"]["params"]
        self.assertEqual(params["query"], "my shop")
        self.assertEqual(params["tlds"], ["com", "dev", "io"])
        self.assertEqual(params["paging.limit"], 12)
        self.assertEqual(params["paging.cursor"], "cursor-11")
        self.assertEqual(params["maxLength"], 15)

    @patch("wix_safe_agent_cli.commands.domains.HttpClient")
    def test_domains_check_availability_rejects_domain_without_tld(self, mock_client: unittest.mock.MagicMock) -> None:
        _ = mock_client
        args = SimpleNamespace(domain="my-site")
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = domains.cmd_domains_check_availability(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertIn("must include a TLD", payload["error"])

    @patch("wix_safe_agent_cli.commands.domains.HttpClient")
    def test_domains_suggest_rejects_leading_dot_tld(self, mock_client: unittest.mock.MagicMock) -> None:
        _ = mock_client
        args = SimpleNamespace(query="my", tlds_json='[".com", "com"]', paging_limit=None, cursor=None, max_length=None)
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = domains.cmd_domains_suggest(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertIn("leading dot", payload["error"])

    @patch("wix_safe_agent_cli.commands.domains.HttpClient")
    def test_domains_suggest_rejects_paging_limit_out_of_range(self, mock_client: unittest.mock.MagicMock) -> None:
        _ = mock_client
        args = SimpleNamespace(query="my", tlds_json=None, paging_limit=21, cursor=None, max_length=None)
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = domains.cmd_domains_suggest(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertIn("paging-limit must be between 1 and 20", payload["error"])

    @patch("wix_safe_agent_cli.commands.domains.HttpClient")
    def test_domains_suggest_rejects_max_length_out_of_range(self, mock_client: unittest.mock.MagicMock) -> None:
        _ = mock_client
        args = SimpleNamespace(query="my", tlds_json=None, paging_limit=None, cursor=None, max_length=2)
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = domains.cmd_domains_suggest(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertIn("max-length must be between 3 and 63", payload["error"])
