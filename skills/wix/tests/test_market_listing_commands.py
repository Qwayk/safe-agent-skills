from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import market_listing
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestMarketListingCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli market-listing search",
            "apply": False,
            "yes": False,
            "verbose": False,
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
        }

    def test_parser_recognizes_market_listing_search(self) -> None:
        parser = build_parser()
        parsed = parser.parse_args(
            [
                "market-listing",
                "search",
                "--search-term",
                "booking",
                "--language-code",
                "de",
                "--limit",
                "25",
            ]
        )

        self.assertEqual(parsed.market_listing_cmd, "search")
        self.assertFalse(parsed.write_capable)
        self.assertEqual(parsed.func.__name__, "cmd_market_listing_search")

    @patch("wix_safe_agent_cli.commands.market_listing.HttpClient")
    def test_market_listing_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {"marketListings": [{"appId": "app-1"}]}
        )
        args = SimpleNamespace(search_term="booking", language_code="de", limit=25)
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = market_listing.cmd_market_listing_search(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["method"], "market-listing.search")
        self.assertEqual(payload["request"]["method"], "POST")
        self.assertEqual(payload["request"]["path"], "/devcenter/app-market-listing/v1/market-listings/search")
        self.assertEqual(payload["request"]["body"], {"searchTerm": "booking", "languageCode": "de", "paging": {"limit": 25}})

        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["headers"]["Authorization"], "token-abc")
        self.assertEqual(call.kwargs["json_body"]["searchTerm"], "booking")
        self.assertEqual(call.kwargs["json_body"]["languageCode"], "de")
        self.assertEqual(call.kwargs["json_body"]["paging"]["limit"], 25)

    @patch("wix_safe_agent_cli.commands.market_listing.HttpClient")
    def test_market_listing_omits_optional_fields_when_not_set(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"marketListings": []})
        args = SimpleNamespace(search_term="booking", language_code=None, limit=None)
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = market_listing.cmd_market_listing_search(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["body"], {"searchTerm": "booking"})

        call = mock_client.return_value.request.call_args
        self.assertNotIn("languageCode", call.kwargs["json_body"])
        self.assertNotIn("paging", call.kwargs["json_body"])

    @patch("wix_safe_agent_cli.commands.market_listing.HttpClient")
    def test_market_listing_rejects_missing_search_term(self, mock_client: unittest.mock.MagicMock) -> None:
        _ = mock_client
        args = SimpleNamespace(search_term="  ", language_code=None, limit=None)
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = market_listing.cmd_market_listing_search(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("Missing --search-term", payload["error"])

    @patch("wix_safe_agent_cli.commands.market_listing.HttpClient")
    def test_market_listing_rejects_limit_out_of_range(self, mock_client: unittest.mock.MagicMock) -> None:
        _ = mock_client
        args = SimpleNamespace(search_term="booking", language_code=None, limit=51)
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = market_listing.cmd_market_listing_search(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("--limit must be an integer between 1 and 50", payload["error"])
