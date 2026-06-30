from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.commands import sites
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


class TestSitesCommands(unittest.TestCase):
    def _ctx(self, *, cfg_override: dict | None = None, verbose: bool = False) -> dict:
        cfg = SimpleNamespace(
            base_url="https://www.wixapis.com",
            timeout_s=30.0,
            access_token="token-legacy",
            api_key="acct-api-key",
            account_id="acct-001",
            app_id=None,
            app_secret=None,
            instance_id=None,
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

    @patch("wix_safe_agent_cli.commands.sites.HttpClient")
    def test_sites_query_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"sites": [{"id": "s1"}], "pagingMetadata": {"count": 1}})

        args = SimpleNamespace(
            query_json='{"query":{}}',
            filter_json='{"published":{"$eq":true}}',
            sort_json='{ "displayName": "ASC"}',
            cursor="cursor-1",
            limit=80,
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = sites.cmd_sites_query(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        request = payload["request"]
        self.assertEqual(request["method"], "POST")
        self.assertEqual(request["path"], "/site-list/v2/sites/query")
        body = request["body"]
        self.assertIn("query", body)
        self.assertEqual(body["query"]["filter"], {"published": {"$eq": True}})
        self.assertEqual(body["query"]["sort"], {"displayName": "ASC"})
        self.assertEqual(body["query"]["cursorPaging"], {"cursor": "cursor-1", "limit": 80})

        http_call = mock_client.return_value.request.call_args
        headers = http_call.kwargs["headers"]
        self.assertEqual(headers["Authorization"], "acct-api-key")
        self.assertEqual(headers["wix-account-id"], "acct-001")
        self.assertEqual(headers["Content-Type"], "application/json")

    @patch("wix_safe_agent_cli.commands.sites.HttpClient")
    def test_sites_count_builds_expected_filter_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"count": 7})

        args = SimpleNamespace(
            query_json='{"query":{"filter":{"published":{"$eq":true},"name":{"$contains":"shop"}}}}',
            filter_json=None,
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = sites.cmd_sites_count(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["path"], "/site-list/v2/sites/count")
        self.assertEqual(payload["request"]["body"], {
            "filter": {
                "published": {"$eq": True},
                "name": {"$contains": "shop"},
            },
        })

    @patch("wix_safe_agent_cli.commands.sites.HttpClient")
    def test_sites_count_rejects_unsupported_filter_by_premium(self, mock_client: unittest.mock.MagicMock) -> None:
        _ = mock_client
        args = SimpleNamespace(query_json='{"query":{"filter":{"premium":{"$eq":true}}}}', filter_json=None)
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = sites.cmd_sites_count(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertIn("premium", payload["error"])

    @patch("wix_safe_agent_cli.commands.sites.HttpClient")
    def test_sites_count_rejects_conflicting_filter_sources(self, mock_client: unittest.mock.MagicMock) -> None:
        _ = mock_client
        args = SimpleNamespace(
            query_json='{"query":{"filter":{"published":{"$eq":true}}}}',
            filter_json='{ "name": {"$eq": "Main"} }',
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = sites.cmd_sites_count(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertIn("one filter source", payload["error"])

    def test_sites_query_rejects_limit_over_100(self) -> None:
        args = SimpleNamespace(
            query_json='{"query":{}}',
            filter_json=None,
            sort_json=None,
            cursor=None,
            limit=101,
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = sites.cmd_sites_query(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertIn("100 or less", payload["error"])
