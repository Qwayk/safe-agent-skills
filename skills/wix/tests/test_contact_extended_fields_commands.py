from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import contact_extended_fields
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestContactExtendedFieldsCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli contact-extended-fields",
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

    @patch("wix_safe_agent_cli.commands.contact_extended_fields.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.contact_extended_fields.HttpClient")
    def test_read_commands_use_official_paths(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"field": {}})

        cases = [
            (
                contact_extended_fields.cmd_contact_extended_fields_get,
                SimpleNamespace(key="custom.favorite"),
                "GET",
                "/contacts/v4/extended-fields/custom.favorite",
                None,
            ),
            (
                contact_extended_fields.cmd_contact_extended_fields_list,
                SimpleNamespace(),
                "GET",
                "/contacts/v4/extended-fields",
                None,
            ),
            (
                contact_extended_fields.cmd_contact_extended_fields_query,
                SimpleNamespace(query_json='{"filter":{"namespace":"custom"}}'),
                "POST",
                "/contacts/v4/extended-fields/query",
                {"query": {"filter": {"namespace": "custom"}}},
            ),
        ]
        for func, args, method, path, expected_body in cases:
            with self.subTest(path=path):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertEqual(payload["request"]["method"], method)
                self.assertEqual(payload["request"]["path"], path)
                if expected_body is not None:
                    self.assertEqual(payload["request"]["body"], expected_body)

        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "contact-extended-fields")

    @patch("wix_safe_agent_cli.commands.contact_extended_fields.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.contact_extended_fields.HttpClient")
    def test_writes_are_plan_first_and_delete_requires_ack(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        cases = [
            (
                contact_extended_fields.cmd_contact_extended_fields_find_or_create,
                SimpleNamespace(field_json='{"field":{"displayName":"Favorite color","dataType":"TEXT"}}'),
                "POST",
                "/contacts/v4/extended-fields",
                False,
            ),
            (
                contact_extended_fields.cmd_contact_extended_fields_update,
                SimpleNamespace(key="custom.favorite", field_json='{"field":{"displayName":"Favorite food"}}'),
                "PATCH",
                "/contacts/v4/extended-fields/custom.favorite",
                False,
            ),
            (
                contact_extended_fields.cmd_contact_extended_fields_delete,
                SimpleNamespace(key="custom.favorite"),
                "DELETE",
                "/contacts/v4/extended-fields/custom.favorite",
                True,
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

    def test_parser_exposes_contact_extended_fields_commands(self) -> None:
        parser = build_parser()
        cases = [
            (
                ["contact-extended-fields", "get", "--key", "custom.favorite"],
                contact_extended_fields.cmd_contact_extended_fields_get,
                False,
            ),
            (
                ["contact-extended-fields", "list"],
                contact_extended_fields.cmd_contact_extended_fields_list,
                False,
            ),
            (
                ["contact-extended-fields", "query", "--query-json", "{}"],
                contact_extended_fields.cmd_contact_extended_fields_query,
                False,
            ),
            (
                ["contact-extended-fields", "find-or-create", "--field-json", "{}"],
                contact_extended_fields.cmd_contact_extended_fields_find_or_create,
                True,
            ),
            (
                ["contact-extended-fields", "update", "--key", "custom.favorite", "--field-json", "{}"],
                contact_extended_fields.cmd_contact_extended_fields_update,
                True,
            ),
            (
                ["contact-extended-fields", "delete", "--key", "custom.favorite"],
                contact_extended_fields.cmd_contact_extended_fields_delete,
                True,
            ),
        ]
        for argv, func, write_capable in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertIs(args.func, func)
                self.assertEqual(args.write_capable, write_capable)
