from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import member_custom_field_applications
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestMemberCustomFieldApplicationsCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli member-custom-field-applications",
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

    @patch("wix_safe_agent_cli.commands.member_custom_field_applications.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.member_custom_field_applications.HttpClient")
    def test_read_commands_use_official_paths(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"application": {}})

        cases = [
            (
                member_custom_field_applications.cmd_member_custom_field_applications_get,
                SimpleNamespace(custom_field_id="field-1"),
                "GET",
                "/members/v1/custom-fields-applications/field-1",
                None,
            ),
            (
                member_custom_field_applications.cmd_member_custom_field_applications_list,
                SimpleNamespace(applications_json='{"customFieldIds":["field-1"]}'),
                "POST",
                "/members/v1/custom-fields-applications/applications",
                {"customFieldIds": ["field-1"]},
            ),
            (
                member_custom_field_applications.cmd_member_custom_field_applications_get_members,
                SimpleNamespace(members_json='{"memberIds":["member-1"]}'),
                "POST",
                "/members/v1/custom-fields-applications/members",
                {"memberIds": ["member-1"]},
            ),
            (
                member_custom_field_applications.cmd_member_custom_field_applications_get_roles,
                SimpleNamespace(roles_json='{"roleIds":["role-1"]}'),
                "POST",
                "/members/v1/custom-fields-applications/roles",
                {"roleIds": ["role-1"]},
            ),
        ]
        for func, args, method, path, body in cases:
            with self.subTest(path=path):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertEqual(payload["request"]["method"], method)
                self.assertEqual(payload["request"]["path"], path)
                if body is not None:
                    self.assertEqual(payload["request"]["body"], body)

        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "member-custom-field-applications")

    @patch("wix_safe_agent_cli.commands.member_custom_field_applications.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.member_custom_field_applications.HttpClient")
    def test_writes_are_plan_first_and_delete_requires_ack(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        cases = [
            (
                member_custom_field_applications.cmd_member_custom_field_applications_create,
                SimpleNamespace(application_json='{"application":{"customFieldId":"field-1"}}'),
                "POST",
                "/members/v1/custom-fields-applications",
                False,
            ),
            (
                member_custom_field_applications.cmd_member_custom_field_applications_update,
                SimpleNamespace(custom_field_id="field-1", application_json='{"application":{"customFieldId":"field-1"}}'),
                "PATCH",
                "/members/v1/custom-fields-applications/field-1",
                False,
            ),
            (
                member_custom_field_applications.cmd_member_custom_field_applications_delete,
                SimpleNamespace(custom_field_id="field-1"),
                "DELETE",
                "/members/v1/custom-fields-applications/field-1",
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

    def test_parser_exposes_member_custom_field_applications_commands(self) -> None:
        parser = build_parser()
        cases = [
            (
                ["member-custom-field-applications", "create", "--application-json", "{}"],
                member_custom_field_applications.cmd_member_custom_field_applications_create,
                True,
            ),
            (
                ["member-custom-field-applications", "update", "--custom-field-id", "field-1", "--application-json", "{}"],
                member_custom_field_applications.cmd_member_custom_field_applications_update,
                True,
            ),
            (
                ["member-custom-field-applications", "delete", "--custom-field-id", "field-1"],
                member_custom_field_applications.cmd_member_custom_field_applications_delete,
                True,
            ),
            (
                ["member-custom-field-applications", "get", "--custom-field-id", "field-1"],
                member_custom_field_applications.cmd_member_custom_field_applications_get,
                False,
            ),
            (
                ["member-custom-field-applications", "list-applications"],
                member_custom_field_applications.cmd_member_custom_field_applications_list,
                False,
            ),
            (
                ["member-custom-field-applications", "get-members", "--members-json", "{}"],
                member_custom_field_applications.cmd_member_custom_field_applications_get_members,
                False,
            ),
            (
                ["member-custom-field-applications", "get-roles", "--roles-json", "{}"],
                member_custom_field_applications.cmd_member_custom_field_applications_get_roles,
                False,
            ),
        ]
        for argv, func, write_capable in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertIs(args.func, func)
                self.assertEqual(args.write_capable, write_capable)
