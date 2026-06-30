from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import contact_notes
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestContactNotesCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli contact-notes",
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

    @patch("wix_safe_agent_cli.commands.contact_notes.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.contact_notes.HttpClient")
    def test_read_commands_use_official_paths(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"note": {}})

        cases = [
            (
                contact_notes.cmd_contact_notes_get,
                SimpleNamespace(note_id="note-123"),
                "GET",
                "/crm/notes/v2/notes/note-123",
                None,
            ),
            (
                contact_notes.cmd_contact_notes_query,
                SimpleNamespace(query_json='{"filter":{"contactId":"contact-1"}}'),
                "POST",
                "/crm/notes/v2/notes/query",
                {"query": {"filter": {"contactId": "contact-1"}}},
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

        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "contact-notes")

    @patch("wix_safe_agent_cli.commands.contact_notes.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.contact_notes.HttpClient")
    def test_writes_are_plan_first_and_delete_requires_ack(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        cases = [
            (
                contact_notes.cmd_contact_notes_create,
                SimpleNamespace(note_json='{"note":{"contactId":"contact-1","text":"Called about renewal"}}'),
                "POST",
                "/crm/notes/v2/notes",
                False,
            ),
            (
                contact_notes.cmd_contact_notes_update,
                SimpleNamespace(note_id="note-123", note_json='{"note":{"revision":"1","text":"Updated note"}}'),
                "PATCH",
                "/crm/notes/v2/notes/note-123",
                False,
            ),
            (
                contact_notes.cmd_contact_notes_delete,
                SimpleNamespace(note_id="note-123"),
                "DELETE",
                "/crm/notes/v2/notes/note-123",
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

    def test_parser_exposes_contact_notes_commands(self) -> None:
        parser = build_parser()
        cases = [
            (["contact-notes", "get", "--note-id", "note-123"], contact_notes.cmd_contact_notes_get, False),
            (
                ["contact-notes", "query", "--query-json", "{}"],
                contact_notes.cmd_contact_notes_query,
                False,
            ),
            (
                ["contact-notes", "create", "--note-json", "{}"],
                contact_notes.cmd_contact_notes_create,
                True,
            ),
            (
                ["contact-notes", "update", "--note-id", "note-123", "--note-json", "{}"],
                contact_notes.cmd_contact_notes_update,
                True,
            ),
            (
                ["contact-notes", "delete", "--note-id", "note-123"],
                contact_notes.cmd_contact_notes_delete,
                True,
            ),
        ]
        for argv, func, write_capable in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertIs(args.func, func)
                self.assertEqual(args.write_capable, write_capable)
