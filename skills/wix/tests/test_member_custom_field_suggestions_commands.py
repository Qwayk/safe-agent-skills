from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import member_custom_field_suggestions
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestMemberCustomFieldSuggestionsCommands(unittest.TestCase):
    def _ctx(self) -> dict:
        return {
            "cfg": SimpleNamespace(base_url="https://www.wixapis.com", timeout_s=30.0, access_token="token-abc"),
            "env_file": "/tmp/.env",
            "verbose": False,
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
        }

    @patch("wix_safe_agent_cli.commands.member_custom_field_suggestions.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.member_custom_field_suggestions.HttpClient")
    def test_read_commands_use_official_paths(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"suggestions": []})

        cases = [
            (
                member_custom_field_suggestions.cmd_member_custom_field_suggestions_query,
                SimpleNamespace(query_json='{"query":{"filter":{"fieldType":{"$eq":"TEXT"}}}}'),
                "POST",
                "/members/v1/custom-field-suggestions/query",
                {"query": {"filter": {"fieldType": {"$eq": "TEXT"}}}},
            ),
            (
                member_custom_field_suggestions.cmd_member_custom_field_suggestions_list,
                SimpleNamespace(),
                "GET",
                "/members/v1/custom-field-suggestions",
                None,
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

        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "member-custom-field-suggestions")

    def test_parser_exposes_member_custom_field_suggestions_commands(self) -> None:
        parser = build_parser()
        cases = [
            (
                ["member-custom-field-suggestions", "query"],
                member_custom_field_suggestions.cmd_member_custom_field_suggestions_query,
            ),
            (
                ["member-custom-field-suggestions", "list"],
                member_custom_field_suggestions.cmd_member_custom_field_suggestions_list,
            ),
        ]
        for argv, func in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertIs(args.func, func)
                self.assertFalse(args.write_capable)
