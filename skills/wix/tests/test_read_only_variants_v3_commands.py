from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import read_only_variants_v3
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestReadOnlyVariantsV3Commands(unittest.TestCase):
    def _ctx(self, **overrides) -> dict:
        cfg = SimpleNamespace(
            base_url="https://www.wixapis.com",
            timeout_s=30.0,
            access_token="site-app-token",
            app_id=None,
            app_secret=None,
            instance_id=None,
            has_official_app_auth=False,
        )
        ctx = {
            "cfg": cfg,
            "env_file": "/tmp/.env",
            "tool": "wix-safe-agent-cli",
            "tool_version": "0.0.0",
            "command_str": "wix-safe-agent-cli read-only-variants-v3",
            "apply": False,
            "yes": False,
            "verbose": False,
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
            "plan_in": None,
            "plan_out": None,
            "receipt_out": None,
            "ack_irreversible": False,
            "enforce_reviewed_plan": True,
        }
        ctx.update(overrides)
        return ctx

    def _write_plan(self, plan: dict) -> str:
        handle = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json")
        json.dump(plan, handle)
        handle.close()
        return handle.name

    def test_parser_recognizes_read_only_variants_v3_subcommands(self) -> None:
        parser = build_parser()

        query_args = parser.parse_args(["read-only-variants-v3", "query"])
        self.assertEqual(query_args.read_only_variants_v3_cmd, "query")
        self.assertFalse(query_args.write_capable)

        search_args = parser.parse_args(["read-only-variants-v3", "search"])
        self.assertEqual(search_args.read_only_variants_v3_cmd, "search")
        self.assertFalse(search_args.write_capable)

    @patch("wix_safe_agent_cli.commands.read_only_variants_v3.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.read_only_variants_v3.HttpClient")
    def test_query_wraps_query_body_and_uses_read_only_variants_auth_path(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "site-app-token"}, "mode": "app_token"}
        mock_client.return_value.request.return_value = _DummyResponse(
            {"variants": [], "pagingMetadata": {"count": 0}}
        )
        args = SimpleNamespace(
            query_json='{"filter":{"productData.productId":{"$eq":"product-1"},"variantId":{"$eq":"variant-1"}}}'
        )
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = read_only_variants_v3.cmd_read_only_variants_v3_query(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["path"], "/stores/v3/products/query-variants")
        self.assertEqual(
            payload["request"]["body"],
            {"query": {"filter": {"productData.productId": {"$eq": "product-1"}, "variantId": {"$eq": "variant-1"}}}},
        )
        mock_auth.assert_called_once()
        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "read-only-variants-v3")

    @patch("wix_safe_agent_cli.commands.read_only_variants_v3.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.read_only_variants_v3.HttpClient")
    def test_search_wraps_search_body(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "site-app-token"}, "mode": "app_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"variants": []})
        args = SimpleNamespace(search_json='{"expression":"red shirt"}')
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = read_only_variants_v3.cmd_read_only_variants_v3_search(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["path"], "/stores/v3/products/search-variants")
        self.assertEqual(payload["request"]["body"], {"search": {"expression": "red shirt"}})
