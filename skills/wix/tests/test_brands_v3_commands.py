from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import brands_v3
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestBrandsV3Commands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli brands-v3",
            "apply": False,
            "yes": False,
            "verbose": False,
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
        }
        ctx.update(overrides)
        return ctx

    def test_parser_recognizes_brands_v3_subcommands(self) -> None:
        parser = build_parser()

        get_args = parser.parse_args(["brands-v3", "get", "--brand-id", "brand-1"])
        self.assertEqual(get_args.brands_v3_cmd, "get")
        self.assertFalse(get_args.write_capable)

        query_args = parser.parse_args(["brands-v3", "query"])
        self.assertEqual(query_args.brands_v3_cmd, "query")
        self.assertFalse(query_args.write_capable)

        for command, extra in [
            ("create", ["--brand-json", '{"name":"Acme"}']),
            ("update", ["--brand-id", "brand-1", "--brand-json", '{"name":"Acme","revision":"1"}']),
            ("delete", ["--brand-id", "brand-1"]),
            ("bulk-create", ["--brands-json", '[{"name":"Acme"}]']),
            ("bulk-delete", ["--brand-ids-json", '["brand-1"]']),
            ("bulk-update", ["--brands-json", '[{"id":"brand-1","name":"Acme","revision":"1"}]']),
            ("get-or-create", ["--brand-name", "Acme"]),
            ("bulk-get-or-create", ["--brand-names-json", '["Acme"]']),
        ]:
            args = parser.parse_args(["brands-v3", command, *extra])
            self.assertEqual(args.brands_v3_cmd, command)
            self.assertTrue(args.write_capable)

    @patch("wix_safe_agent_cli.commands.brands_v3.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.brands_v3.HttpClient")
    def test_get_uses_expected_request_and_auth_family(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "site-app-token"}, "mode": "app_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"brand": {"id": "brand-1"}})
        args = SimpleNamespace(brand_id="brand-1")
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = brands_v3.cmd_brands_v3_get(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["path"], "/stores/v3/brands/brand-1")
        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "brands-v3")

    @patch("wix_safe_agent_cli.commands.brands_v3.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.brands_v3.HttpClient")
    def test_query_wraps_query_body(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "site-app-token"}, "mode": "app_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"brands": []})
        args = SimpleNamespace(query_json='{"filter":{"name":{"$startsWith":"Ac"}}}')
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = brands_v3.cmd_brands_v3_query(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["path"], "/stores/v3/brands/query")
        self.assertEqual(payload["request"]["body"], {"query": {"filter": {"name": {"$startsWith": "Ac"}}}})

    @patch("wix_safe_agent_cli.commands.brands_v3.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.brands_v3.HttpClient")
    def test_create_dry_run_builds_reviewed_plan(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "site-app-token"}, "mode": "app_token"}
        args = SimpleNamespace(brand_json='{"name":"Acme"}')
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = brands_v3.cmd_brands_v3_create(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["method"], "brands-v3.create")
        self.assertEqual(payload["plan"]["request"]["path"], "/stores/v3/brands")
        self.assertEqual(payload["plan"]["request"]["body"], {"brand": {"name": "Acme"}})
        self.assertEqual(mock_client.return_value.request.call_count, 0)

    def test_update_requires_revision_and_matching_id(self) -> None:
        missing_revision_args = SimpleNamespace(brand_id="brand-1", brand_json='{"id":"brand-1","name":"Acme"}')
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc_missing = brands_v3.cmd_brands_v3_update(missing_revision_args, self._ctx())
        missing_payload = json.loads(buf.getvalue())
        self.assertEqual(rc_missing, 1)
        self.assertIn("revision is required", missing_payload["error"])

        mismatched_id_args = SimpleNamespace(brand_id="brand-1", brand_json='{"id":"brand-2","name":"Acme","revision":"1"}')
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc_mismatch = brands_v3.cmd_brands_v3_update(mismatched_id_args, self._ctx())
        mismatch_payload = json.loads(buf.getvalue())
        self.assertEqual(rc_mismatch, 0)
        self.assertTrue(mismatch_payload["refused"])
        self.assertIn("does not match --brand-id", mismatch_payload["reasons"][0])

    @patch("wix_safe_agent_cli.commands.brands_v3.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.brands_v3.HttpClient")
    def test_bulk_delete_dry_run_requires_irreversible_ack_in_plan(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "site-app-token"}, "mode": "app_token"}
        args = SimpleNamespace(brand_ids_json='["brand-1","brand-2"]')
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = brands_v3.cmd_brands_v3_bulk_delete(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["method"], "brands-v3.bulk-delete")
        self.assertEqual(payload["plan"]["request"]["path"], "/stores/v3/bulk/brands/delete")
        self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
        self.assertEqual(mock_client.return_value.request.call_count, 0)
