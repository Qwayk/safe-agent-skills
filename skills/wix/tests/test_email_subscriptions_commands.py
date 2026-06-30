from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import email_subscriptions
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = action, payload


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestEmailSubscriptionsCommands(unittest.TestCase):
    def _ctx(self, **overrides) -> dict:
        cfg = SimpleNamespace(
            base_url="https://www.wixapis.com",
            timeout_s=30.0,
            app_id=None,
            app_secret=None,
            instance_id=None,
            access_token="token-abc",
            has_official_app_auth=False,
        )
        ctx = {
            "cfg": cfg,
            "env_file": "/tmp/.env",
            "tool": "wix-safe-agent-cli",
            "tool_version": "0.0.0",
            "command_str": "wix-safe-agent-cli email-subscriptions",
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

    def test_parser_exposes_email_subscriptions_commands(self) -> None:
        parser = build_parser()
        cases = [
            (["email-subscriptions", "query"], "query", False),
            (
                ["email-subscriptions", "upsert", "--subscription-json", '{"emailSubscription":{"email":"a@example.com"}}'],
                "upsert",
                True,
            ),
            (
                [
                    "email-subscriptions",
                    "bulk-upsert",
                    "--subscriptions-json",
                    '{"emailSubscriptions":[{"email":"a@example.com"}]}',
                ],
                "bulk-upsert",
                True,
            ),
            (
                ["email-subscriptions", "generate-unsubscribe-link", "--email", "a@example.com"],
                "generate-unsubscribe-link",
                True,
            ),
        ]
        for argv, command, write_capable in cases:
            with self.subTest(command=command):
                args = parser.parse_args(argv)
                self.assertEqual(args.email_subscriptions_cmd, command)
                self.assertEqual(args.write_capable, write_capable)

    @patch("wix_safe_agent_cli.commands.email_subscriptions.HttpClient")
    def test_email_subscriptions_query_uses_official_path(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"ok": True})
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = email_subscriptions.cmd_email_subscriptions_query(
                SimpleNamespace(query_json='{"filter":{"email":{"$in":["a@example.com"]}}}'),
                self._ctx(),
            )
        self.assertEqual(rc, 0)
        self.assertEqual(mock_client.return_value.request.call_args.kwargs["method"], "POST")
        self.assertTrue(
            mock_client.return_value.request.call_args.kwargs["url"].endswith(
                "/email-marketing/v1/email-subscriptions/query"
            )
        )
        self.assertEqual(
            mock_client.return_value.request.call_args.kwargs["json_body"],
            {"query": {"filter": {"email": {"$in": ["a@example.com"]}}}},
        )

    @patch("wix_safe_agent_cli.commands.email_subscriptions.HttpClient")
    def test_email_subscriptions_writes_are_plan_first(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"ok": True})
        write_cases = [
            (
                email_subscriptions.cmd_email_subscriptions_upsert,
                SimpleNamespace(subscription_json='{"emailSubscription":{"email":"a@example.com","subscriptionStatus":"SUBSCRIBED"}}'),
                "/email-marketing/v1/email-subscriptions",
                {"email": "a@example.com"},
            ),
            (
                email_subscriptions.cmd_email_subscriptions_bulk_upsert,
                SimpleNamespace(subscriptions_json='{"emailSubscriptions":[{"email":"a@example.com"}]}'),
                "/email-marketing/v1/email-subscriptions/bulk",
                {"emails": ["a@example.com"]},
            ),
            (
                email_subscriptions.cmd_email_subscriptions_generate_unsubscribe_link,
                SimpleNamespace(email="a@example.com", request_json=None),
                "/email-marketing/v1/email-subscriptions/unsubscribe-link",
                {"email": "a@example.com"},
            ),
        ]
        for func, args, path, selector in write_cases:
            with self.subTest(path=path):
                mock_client.return_value.request.reset_mock()
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertTrue(payload["dry_run"])
                self.assertEqual(payload["plan"]["request"]["method"], "POST")
                self.assertEqual(payload["plan"]["request"]["path"], path)
                self.assertEqual(payload["plan"]["selector"], selector)
                self.assertFalse(mock_client.return_value.request.called)

    @patch("wix_safe_agent_cli.commands.email_subscriptions.HttpClient")
    def test_email_subscriptions_validate_email_inputs(self, mock_client: unittest.mock.MagicMock) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = email_subscriptions.cmd_email_subscriptions_upsert(
                SimpleNamespace(subscription_json='{"emailSubscription":{"email":"not-an-email"}}'),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertFalse(mock_client.return_value.request.called)
