from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import contact_attachments
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestContactAttachmentsCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli contact-attachments",
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

    @patch("wix_safe_agent_cli.commands.contact_attachments.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.contact_attachments.HttpClient")
    def test_read_commands_use_official_paths(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"attachment": {}})

        cases = [
            (
                contact_attachments.cmd_contact_attachments_get,
                SimpleNamespace(contact_id="contact-1", attachment_id="attachment-1"),
                "GET",
                "/contacts/v4/attachments/contact-1/attachment-1",
            ),
            (
                contact_attachments.cmd_contact_attachments_list,
                SimpleNamespace(contact_id="contact-1"),
                "GET",
                "/contacts/v4/attachments/contact-1",
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

        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "contact-attachments")

    @patch("wix_safe_agent_cli.commands.contact_attachments.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.contact_attachments.HttpClient")
    def test_writes_are_plan_first_and_delete_requires_ack(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        cases = [
            (
                contact_attachments.cmd_contact_attachments_generate_upload_url,
                SimpleNamespace(contact_id="contact-1", attachment_json='{"attachment":{"fileName":"proposal.pdf","mimeType":"application/pdf"}}'),
                "POST",
                "/contacts/v4/attachments/contact-1/upload-url",
                False,
            ),
            (
                contact_attachments.cmd_contact_attachments_delete,
                SimpleNamespace(contact_id="contact-1", attachment_id="attachment-1"),
                "DELETE",
                "/contacts/v4/attachments/contact-1/attachment-1",
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

    def test_parser_exposes_contact_attachments_commands(self) -> None:
        parser = build_parser()
        cases = [
            (
                ["contact-attachments", "get", "--contact-id", "contact-1", "--attachment-id", "attachment-1"],
                contact_attachments.cmd_contact_attachments_get,
                False,
            ),
            (
                ["contact-attachments", "list", "--contact-id", "contact-1"],
                contact_attachments.cmd_contact_attachments_list,
                False,
            ),
            (
                ["contact-attachments", "generate-upload-url", "--contact-id", "contact-1", "--attachment-json", "{}"],
                contact_attachments.cmd_contact_attachments_generate_upload_url,
                True,
            ),
            (
                ["contact-attachments", "delete", "--contact-id", "contact-1", "--attachment-id", "attachment-1"],
                contact_attachments.cmd_contact_attachments_delete,
                True,
            ),
        ]
        for argv, func, write_capable in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertIs(args.func, func)
                self.assertEqual(args.write_capable, write_capable)
