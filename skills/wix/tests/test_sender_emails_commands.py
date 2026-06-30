from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import sender_emails
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestSenderEmailsCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli sender-emails",
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

    def test_parser_recognizes_sender_emails_subcommands(self) -> None:
        parser = build_parser()

        list_args = parser.parse_args(["sender-emails", "list"])
        self.assertEqual(list_args.sender_emails_cmd, "list")
        self.assertFalse(list_args.write_capable)

        get_args = parser.parse_args(["sender-emails", "get", "--sender-email-id", "sender-1"])
        self.assertEqual(get_args.sender_emails_cmd, "get")
        self.assertFalse(get_args.write_capable)

        create_args = parser.parse_args(
            [
                "sender-emails",
                "create",
                "--sender-email-json",
                '{"senderEmail":{"emailAddress":"owner@example.com"}}',
            ]
        )
        self.assertEqual(create_args.sender_emails_cmd, "create")
        self.assertTrue(create_args.write_capable)

        delete_args = parser.parse_args(["sender-emails", "delete", "--sender-email-id", "sender-1"])
        self.assertEqual(delete_args.sender_emails_cmd, "delete")
        self.assertTrue(delete_args.write_capable)

        get_or_create_args = parser.parse_args(
            ["sender-emails", "get-or-create", "--email-address", "owner@example.com"]
        )
        self.assertEqual(get_or_create_args.sender_emails_cmd, "get-or-create")
        self.assertTrue(get_or_create_args.write_capable)

        send_code_args = parser.parse_args(
            ["sender-emails", "send-verification-code", "--sender-email-id", "sender-1"]
        )
        self.assertEqual(send_code_args.sender_emails_cmd, "send-verification-code")
        self.assertTrue(send_code_args.write_capable)

        verify_args = parser.parse_args(
            [
                "sender-emails",
                "verify",
                "--sender-email-id",
                "sender-1",
                "--verification-code",
                "ABC123",
            ]
        )
        self.assertEqual(verify_args.sender_emails_cmd, "verify")
        self.assertTrue(verify_args.write_capable)

    @patch("wix_safe_agent_cli.commands.sender_emails.HttpClient")
    def test_list_builds_expected_request(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {"senderEmails": [{"id": "sender-1", "emailAddress": "owner@example.com", "verified": True}]}
        )
        args = SimpleNamespace(email_address="owner@example.com", limit=25, cursor="next-cursor")

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = sender_emails.cmd_sender_emails_list(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["path"], "/sender-emails/v1/sender-emails")
        self.assertEqual(payload["request"]["params"]["emailAddress"], "owner@example.com")
        self.assertEqual(payload["request"]["params"]["paging.limit"], 25)
        self.assertEqual(payload["request"]["params"]["paging.cursor"], "next-cursor")

    @patch("wix_safe_agent_cli.commands.sender_emails.HttpClient")
    def test_create_dry_run_builds_plan(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"senderEmails": []})
        args = SimpleNamespace(sender_email_json='{"senderEmail":{"emailAddress":"owner@example.com"}}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = sender_emails.cmd_sender_emails_create(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["method"], "sender-emails.create")
        self.assertEqual(payload["plan"]["request"]["body"]["senderEmail"]["emailAddress"], "owner@example.com")

    @patch("wix_safe_agent_cli.commands.sender_emails.HttpClient")
    def test_create_apply_requires_reviewed_plan(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"senderEmails": []})
        args = SimpleNamespace(sender_email_json='{"senderEmail":{"emailAddress":"owner@example.com"}}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = sender_emails.cmd_sender_emails_create(args, self._ctx(apply=True, yes=True))
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("--plan-out", payload["reasons"][0])
        self.assertEqual(mock_client.return_value.request.call_count, 1)

    @patch("wix_safe_agent_cli.commands.sender_emails.HttpClient")
    def test_create_refuses_duplicate_email_address(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {"senderEmails": [{"id": "sender-1", "emailAddress": "owner@example.com"}]}
        )
        args = SimpleNamespace(sender_email_json='{"senderEmail":{"emailAddress":"owner@example.com"}}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = sender_emails.cmd_sender_emails_create(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("already exists", payload["reasons"][0])

    @patch("wix_safe_agent_cli.commands.sender_emails.HttpClient")
    def test_get_or_create_dry_run_builds_plan(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"senderEmails": []})
        args = SimpleNamespace(email_address="owner@example.com")

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = sender_emails.cmd_sender_emails_get_or_create(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["method"], "sender-emails.get-or-create")

    @patch("wix_safe_agent_cli.commands.sender_emails.HttpClient")
    def test_send_verification_code_apply_requires_reviewed_plan(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {"senderEmail": {"id": "sender-1", "emailAddress": "owner@example.com", "verified": False}}
        )
        args = SimpleNamespace(sender_email_id="sender-1")

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = sender_emails.cmd_sender_emails_send_verification_code(
                args,
                self._ctx(apply=True, yes=True),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("--plan-out", payload["reasons"][0])
        self.assertEqual(mock_client.return_value.request.call_count, 1)

    def test_delete_live_apply_requires_ack_irreversible(self) -> None:
        args = SimpleNamespace(sender_email_id="sender-1")
        current_sender_email = {
            "id": "sender-1",
            "emailAddress": "owner@example.com",
            "verified": True,
        }

        with patch.object(sender_emails, "_get_sender_email", return_value=current_sender_email), patch.object(
            sender_emails, "_request_json"
        ) as mock_request:
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = sender_emails.cmd_sender_emails_delete(
                    args,
                    self._ctx(apply=True, yes=True, ack_irreversible=False),
                )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["method"], "sender-emails.delete")
        self.assertFalse(mock_request.called)

    @patch("wix_safe_agent_cli.commands.sender_emails.HttpClient")
    def test_verify_apply_requires_reviewed_plan(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {"senderEmail": {"id": "sender-1", "emailAddress": "owner@example.com", "verified": False}}
        )
        args = SimpleNamespace(sender_email_id="sender-1", verification_code="ABC123")

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = sender_emails.cmd_sender_emails_verify(args, self._ctx(apply=True, yes=True))
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("--plan-out", payload["reasons"][0])
        self.assertEqual(mock_client.return_value.request.call_count, 1)

    def test_create_live_apply_verifies_by_reread(self) -> None:
        args = SimpleNamespace(sender_email_json='{"senderEmail":{"emailAddress":"owner@example.com"}}')
        plan = {
            "method": "sender-emails.create",
            "baseline": {
                "env_fingerprint": "https://www.wixapis.com",
                "selector": {
                    "kind": "wix-sender-email",
                    "operation": "create",
                    "email_address": "owner@example.com",
                },
                "before_state": {"senderEmails": []},
            },
            "proposed_changes": [{"operation": "create", "emailAddress": "owner@example.com"}],
        }
        plan_path = self._write_plan(plan)

        created_sender_email = {"id": "sender-1", "emailAddress": "owner@example.com", "verified": False}
        with patch.object(sender_emails, "_list_sender_emails", return_value=[]), patch.object(
            sender_emails, "_request_json", return_value={"senderEmail": created_sender_email}
        ) as mock_request, patch.object(
            sender_emails, "_get_sender_email", return_value=created_sender_email
        ):
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = sender_emails.cmd_sender_emails_create(
                    args,
                    self._ctx(apply=True, yes=True, plan_in=plan_path),
                )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertFalse(payload["dry_run"])
        self.assertEqual(payload["receipt"]["verification"]["after"]["id"], "sender-1")
        self.assertEqual(mock_request.call_count, 1)
