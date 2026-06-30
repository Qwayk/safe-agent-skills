from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import member_custom_fields
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestMemberCustomFieldsCommands(unittest.TestCase):
    def _ctx(self, **overrides) -> dict:
        cfg = SimpleNamespace(base_url="https://www.wixapis.com", timeout_s=30.0, access_token="token-abc")
        ctx = {
            "cfg": cfg,
            "env_file": "/tmp/.env",
            "verbose": False,
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
            "tool": "wix-safe-agent-cli",
            "tool_version": "0.0.0",
            "command_str": "wix-safe-agent-cli member-custom-fields",
            "apply": False,
            "yes": False,
            "plan_in": None,
            "plan_out": None,
            "receipt_out": None,
            "ack_irreversible": False,
            "enforce_reviewed_plan": True,
        }
        ctx.update(overrides)
        return ctx

    @patch("wix_safe_agent_cli.commands.member_custom_fields.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.member_custom_fields.HttpClient")
    def test_read_commands_use_official_paths(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"field": {}})

        cases = [
            (
                member_custom_fields.cmd_member_custom_fields_get,
                SimpleNamespace(field_id="field-1"),
                "GET",
                "/members/v1/custom-fields/field-1",
            ),
            (
                member_custom_fields.cmd_member_custom_fields_list,
                SimpleNamespace(),
                "GET",
                "/members/v1/custom-fields",
            ),
        ]
        for func, args, method, path in cases:
            with self.subTest(path=path):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertEqual(payload["request"]["method"], method)
                self.assertEqual(payload["request"]["path"], path)

        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "member-custom-fields")

    @patch("wix_safe_agent_cli.commands.member_custom_fields.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.member_custom_fields.HttpClient")
    def test_writes_are_plan_first_and_delete_requires_ack(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        cases = [
            (
                member_custom_fields.cmd_member_custom_fields_create,
                SimpleNamespace(field_json='{"field":{"name":"Favorite color"}}'),
                "POST",
                "/members/v1/custom-fields",
                False,
            ),
            (
                member_custom_fields.cmd_member_custom_fields_update,
                SimpleNamespace(field_id="field-1", field_json='{"field":{"name":"Favorite food"}}'),
                "PATCH",
                "/members/v1/custom-fields/field-1",
                False,
            ),
            (
                member_custom_fields.cmd_member_custom_fields_delete,
                SimpleNamespace(field_id="field-1"),
                "DELETE",
                "/members/v1/custom-fields/field-1",
                True,
            ),
            (
                member_custom_fields.cmd_member_custom_fields_hide,
                SimpleNamespace(field_id="field-1"),
                "POST",
                "/members/v1/custom-fields/field-1/hide",
                False,
            ),
            (
                member_custom_fields.cmd_member_custom_fields_update_order,
                SimpleNamespace(order_json='{"section":"GENERAL","fieldIds":["field-1"]}'),
                "POST",
                "/members/v1/custom-fields/order",
                False,
            ),
        ]
        for func, args, method, path, requires_ack in cases:
            with self.subTest(path=path):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertTrue(payload["dry_run"])
                self.assertEqual(payload["plan"]["request"]["method"], method)
                self.assertEqual(payload["plan"]["request"]["path"], path)
                preconditions = payload["plan"]["preconditions"]
                self.assertEqual("apply also requires --ack-irreversible" in preconditions, requires_ack)

        mock_client.return_value.request.assert_not_called()

    def test_parser_exposes_member_custom_fields_commands(self) -> None:
        parser = build_parser()
        cases = [
            (["member-custom-fields", "create", "--field-json", "{}"], member_custom_fields.cmd_member_custom_fields_create, True),
            (
                ["member-custom-fields", "update", "--field-id", "field-1", "--field-json", "{}"],
                member_custom_fields.cmd_member_custom_fields_update,
                True,
            ),
            (
                ["member-custom-fields", "delete", "--field-id", "field-1"],
                member_custom_fields.cmd_member_custom_fields_delete,
                True,
            ),
            (
                ["member-custom-fields", "get", "--field-id", "field-1"],
                member_custom_fields.cmd_member_custom_fields_get,
                False,
            ),
            (
                ["member-custom-fields", "hide", "--field-id", "field-1"],
                member_custom_fields.cmd_member_custom_fields_hide,
                True,
            ),
            (["member-custom-fields", "list"], member_custom_fields.cmd_member_custom_fields_list, False),
            (
                ["member-custom-fields", "update-order", "--order-json", "{}"],
                member_custom_fields.cmd_member_custom_fields_update_order,
                True,
            ),
        ]
        for argv, func, write_capable in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertIs(args.func, func)
                self.assertEqual(args.write_capable, write_capable)
