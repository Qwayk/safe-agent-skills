from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import ribbons_v3
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestRibbonsV3Commands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli ribbons-v3",
            "apply": False,
            "yes": False,
            "verbose": False,
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
        }
        ctx.update(overrides)
        return ctx

    def test_parser_recognizes_ribbons_v3_subcommands(self) -> None:
        parser = build_parser()

        read_cases = [
            (["ribbons-v3", "get", "--ribbon-id", "ribbon-1"], "get"),
            (["ribbons-v3", "query"], "query"),
        ]
        write_cases = [
            (["ribbons-v3", "create", "--ribbon-json", '{"name":"Sale"}'], "create"),
            (["ribbons-v3", "update", "--ribbon-id", "ribbon-1", "--ribbon-json", '{"revision":"1"}'], "update"),
            (["ribbons-v3", "delete", "--ribbon-id", "ribbon-1"], "delete"),
            (["ribbons-v3", "bulk-create", "--ribbons-json", '[{"name":"Sale"}]'], "bulk-create"),
            (["ribbons-v3", "bulk-delete", "--ribbon-ids-json", '["ribbon-1"]'], "bulk-delete"),
            (["ribbons-v3", "bulk-update", "--ribbons-json", '[{"id":"ribbon-1","revision":"1"}]'], "bulk-update"),
            (["ribbons-v3", "get-or-create", "--ribbon-name", "Sale"], "get-or-create"),
            (["ribbons-v3", "bulk-get-or-create", "--ribbon-names-json", '["Sale"]'], "bulk-get-or-create"),
        ]
        for argv, command in read_cases:
            args = parser.parse_args(argv)
            self.assertEqual(args.ribbons_v3_cmd, command)
            self.assertFalse(args.write_capable)
        for argv, command in write_cases:
            args = parser.parse_args(argv)
            self.assertEqual(args.ribbons_v3_cmd, command)
            self.assertTrue(args.write_capable)

    @patch("wix_safe_agent_cli.commands.ribbons_v3.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.ribbons_v3.HttpClient")
    def test_get_uses_expected_request_and_auth_family(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "site-app-token"}, "mode": "app_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"ribbon": {"id": "ribbon-1"}})
        args = SimpleNamespace(ribbon_id="ribbon-1")
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = ribbons_v3.cmd_ribbons_v3_get(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["path"], "/stores/v3/ribbons/ribbon-1")
        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "ribbons-v3")

    @patch("wix_safe_agent_cli.commands.ribbons_v3.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.ribbons_v3.HttpClient")
    def test_query_wraps_query_body(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "site-app-token"}, "mode": "app_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"ribbons": []})
        args = SimpleNamespace(query_json='{"filter":{"name":{"$startsWith":"Sale"}}}')
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = ribbons_v3.cmd_ribbons_v3_query(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["path"], "/stores/v3/ribbons/query")
        self.assertEqual(payload["request"]["body"], {"query": {"filter": {"name": {"$startsWith": "Sale"}}}})

    @patch("wix_safe_agent_cli.commands.ribbons_v3.resolve_auth_mode")
    def test_create_dry_run_builds_reviewed_plan(self, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "site-app-token"}, "mode": "app_token"}
        args = SimpleNamespace(ribbon_json='{"name":"Sale"}')
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = ribbons_v3.cmd_ribbons_v3_create(args, self._ctx(command_str="wix-safe-agent-cli ribbons-v3 create"))
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["method"], "ribbons-v3.create")
        self.assertEqual(payload["plan"]["request"]["path"], "/stores/v3/ribbons")
        self.assertEqual(payload["plan"]["request"]["body"], {"ribbon": {"name": "Sale"}})

    def test_update_requires_revision_and_matching_id(self) -> None:
        args = SimpleNamespace(ribbon_id="ribbon-1", ribbon_json='{"id":"other","name":"Sale","revision":"1"}')
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = ribbons_v3.cmd_ribbons_v3_update(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("does not match --ribbon-id", payload["reasons"][0])

        args = SimpleNamespace(ribbon_id="ribbon-1", ribbon_json='{"id":"ribbon-1","name":"Sale"}')
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = ribbons_v3.cmd_ribbons_v3_update(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertIn("ribbon.revision is required", payload["error"])

    @patch("wix_safe_agent_cli.commands.ribbons_v3.resolve_auth_mode")
    def test_bulk_delete_dry_run_requires_irreversible_ack_in_plan(self, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "site-app-token"}, "mode": "app_token"}
        args = SimpleNamespace(ribbon_ids_json='["ribbon-1","ribbon-2"]')
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = ribbons_v3.cmd_ribbons_v3_bulk_delete(args, self._ctx(command_str="wix-safe-agent-cli ribbons-v3 bulk-delete"))
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["method"], "ribbons-v3.bulk-delete")
        self.assertEqual(payload["plan"]["risk_level"], "high")
        self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
        self.assertEqual(payload["plan"]["request"]["path"], "/stores/v3/bulk/ribbons/delete")
