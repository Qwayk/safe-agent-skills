from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import site_search
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestSiteSearchCommands(unittest.TestCase):
    def _ctx(self) -> dict:
        cfg = SimpleNamespace(
            base_url="https://www.wixapis.com",
            timeout_s=30.0,
            access_token="token-abc",
            api_key=None,
            account_id=None,
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
            "command_str": "wix-safe-agent-cli site-search search",
            "apply": False,
            "yes": False,
            "verbose": False,
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
        }

    def test_parser_recognizes_site_search_search(self) -> None:
        parser = build_parser()
        parsed = parser.parse_args(
            [
                "site-search",
                "search",
                "--document-type",
                "STORES_PRODUCTS",
                "--search-json",
                '{"paging":{"limit":3},"search":{"expression":"game","fields":[]}}',
            ]
        )

        self.assertEqual(parsed.site_search_cmd, "search")
        self.assertFalse(parsed.write_capable)
        self.assertEqual(parsed.func.__name__, "cmd_site_search_search")

    @patch("wix_safe_agent_cli.commands.site_search.HttpClient")
    def test_site_search_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {"siteDocumentItems": [{"id": "doc-1"}]}
        )
        args = SimpleNamespace(
            document_type="STORES_PRODUCTS",
            search_json='{"paging":{"limit":3},"search":{"expression":"game","fields":[]}}',
            language="en",
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = site_search.cmd_site_search_search(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["method"], "site-search.search")
        self.assertEqual(payload["request"]["method"], "POST")
        self.assertEqual(payload["request"]["path"], "/_api/site-search/v1/search")
        self.assertEqual(payload["request"]["body"]["documentType"], "STORES_PRODUCTS")
        self.assertEqual(payload["request"]["body"]["language"], "en")

        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["headers"]["Authorization"], "token-abc")
        self.assertEqual(call.kwargs["json_body"]["search"]["paging"]["limit"], 3)

    @patch("wix_safe_agent_cli.commands.site_search.HttpClient")
    def test_site_search_rejects_unknown_document_type(self, mock_client: unittest.mock.MagicMock) -> None:
        _ = mock_client
        args = SimpleNamespace(
            document_type="SITE_PAGES",
            search_json='{"paging":{"limit":3}}',
            language=None,
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = site_search.cmd_site_search_search(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("--document-type must be one of", payload["error"])

    @patch("wix_safe_agent_cli.commands.site_search.HttpClient")
    def test_site_search_rejects_non_object_search_json(self, mock_client: unittest.mock.MagicMock) -> None:
        _ = mock_client
        args = SimpleNamespace(
            document_type="BLOG_POSTS",
            search_json='["not-an-object"]',
            language=None,
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = site_search.cmd_site_search_search(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("--search-json must be a JSON object", payload["error"])
