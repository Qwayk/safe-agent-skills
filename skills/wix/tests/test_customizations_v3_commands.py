from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import customizations_v3
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestCustomizationsV3Commands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli customizations-v3",
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

    def test_parser_recognizes_customizations_v3_subcommands(self) -> None:
        parser = build_parser()

        get_args = parser.parse_args(["customizations-v3", "get", "--customization-id", "customization-1"])
        self.assertEqual(get_args.customizations_v3_cmd, "get")
        self.assertFalse(get_args.write_capable)

        query_args = parser.parse_args(["customizations-v3", "query"])
        self.assertEqual(query_args.customizations_v3_cmd, "query")
        self.assertFalse(query_args.write_capable)

        write_cases = [
            (["customizations-v3", "create", "--customization-json", '{"name":"Size"}'], "create"),
            (
                [
                    "customizations-v3",
                    "update",
                    "--customization-id",
                    "customization-1",
                    "--customization-json",
                    '{"revision":3,"name":"Size"}',
                ],
                "update",
            ),
            (["customizations-v3", "delete", "--customization-id", "customization-1"], "delete"),
            (
                ["customizations-v3", "bulk-create", "--customizations-json", '[{"name":"Size"}]'],
                "bulk-create",
            ),
            (
                [
                    "customizations-v3",
                    "bulk-update",
                    "--customizations-json",
                    '[{"id":"customization-1","revision":3,"name":"Size"}]',
                ],
                "bulk-update",
            ),
            (
                [
                    "customizations-v3",
                    "add-choices",
                    "--customization-id",
                    "customization-1",
                    "--choices-json",
                    '[{"name":"Small"}]',
                ],
                "add-choices",
            ),
            (
                [
                    "customizations-v3",
                    "bulk-add-choices",
                    "--customizations-json",
                    '[{"id":"customization-1","choices":[{"name":"Small"}]}]',
                ],
                "bulk-add-choices",
            ),
            (
                [
                    "customizations-v3",
                    "remove-choices",
                    "--customization-id",
                    "customization-1",
                    "--choices-json",
                    '[{"id":"choice-1"}]',
                ],
                "remove-choices",
            ),
            (
                [
                    "customizations-v3",
                    "set-choices",
                    "--customization-id",
                    "customization-1",
                    "--choices-json",
                    '[{"name":"Small"}]',
                ],
                "set-choices",
            ),
        ]
        for argv, command in write_cases:
            args = parser.parse_args(argv)
            self.assertEqual(args.customizations_v3_cmd, command)
            self.assertTrue(args.write_capable)

    @patch("wix_safe_agent_cli.commands.customizations_v3.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.customizations_v3.HttpClient")
    def test_get_uses_expected_request_and_auth_family(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "site-app-token"}, "mode": "app_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"customization": {"id": "customization-1"}})
        args = SimpleNamespace(customization_id="customization-1")
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = customizations_v3.cmd_customizations_v3_get(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["path"], "/stores/v3/customizations/customization-1")
        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "customizations-v3")

    @patch("wix_safe_agent_cli.commands.customizations_v3.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.customizations_v3.HttpClient")
    def test_query_wraps_query_body(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "site-app-token"}, "mode": "app_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"customizations": []})
        args = SimpleNamespace(query_json='{"filter":{"name":{"$startsWith":"Gift"}}}')
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = customizations_v3.cmd_customizations_v3_query(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["path"], "/stores/v3/customizations/query")
        self.assertEqual(payload["request"]["body"], {"query": {"filter": {"name": {"$startsWith": "Gift"}}}})

    @patch("wix_safe_agent_cli.commands.customizations_v3.resolve_auth_mode")
    def test_create_dry_run_builds_reviewed_plan(self, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "site-app-token"}, "mode": "app_token"}
        args = SimpleNamespace(customization_json='{"name":"Size","customizationType":"PRODUCT_OPTION"}')
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = customizations_v3.cmd_customizations_v3_create(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["method"], "customizations-v3.create")
        self.assertEqual(payload["plan"]["request"]["path"], "/stores/v3/customizations")

    def test_update_requires_revision(self) -> None:
        args = SimpleNamespace(customization_id="customization-1", customization_json='{"name":"Size"}')
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = customizations_v3.cmd_customizations_v3_update(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertIn("revision", payload["error"])

    @patch("wix_safe_agent_cli.commands.customizations_v3.resolve_auth_mode")
    def test_delete_dry_run_requires_irreversible_ack_in_plan(self, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "site-app-token"}, "mode": "app_token"}
        args = SimpleNamespace(customization_id="customization-1")
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = customizations_v3.cmd_customizations_v3_delete(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])

    @patch("wix_safe_agent_cli.commands.customizations_v3.resolve_auth_mode")
    def test_set_choices_dry_run_requires_irreversible_ack_in_plan(self, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "site-app-token"}, "mode": "app_token"}
        args = SimpleNamespace(customization_id="customization-1", choices_json='[{"name":"Small"}]')
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = customizations_v3.cmd_customizations_v3_set_choices(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertEqual(payload["plan"]["method"], "customizations-v3.set-choices")
        self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
