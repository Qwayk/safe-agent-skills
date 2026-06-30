from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import sender_details
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestSenderDetailsCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli sender-details",
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

    def test_parser_recognizes_sender_details_subcommands(self) -> None:
        parser = build_parser()

        list_args = parser.parse_args(["sender-details", "list"])
        self.assertEqual(list_args.sender_details_cmd, "list")
        self.assertFalse(list_args.write_capable)

        get_args = parser.parse_args(["sender-details", "get", "--sender-details-id", "details-1"])
        self.assertEqual(get_args.sender_details_cmd, "get")
        self.assertFalse(get_args.write_capable)

        create_args = parser.parse_args(
            [
                "sender-details",
                "create",
                "--sender-details-json",
                '{"senderDetails":{"fromName":"Owner","fromEmailAddress":"owner@example.com"}}',
            ]
        )
        self.assertEqual(create_args.sender_details_cmd, "create")
        self.assertTrue(create_args.write_capable)

        update_args = parser.parse_args(
            [
                "sender-details",
                "update",
                "--sender-details-id",
                "details-1",
                "--sender-details-json",
                '{"senderDetails":{"fromName":"New Owner"}}',
            ]
        )
        self.assertEqual(update_args.sender_details_cmd, "update")
        self.assertTrue(update_args.write_capable)

        delete_args = parser.parse_args(["sender-details", "delete", "--sender-details-id", "details-1"])
        self.assertEqual(delete_args.sender_details_cmd, "delete")
        self.assertTrue(delete_args.write_capable)

        default_args = parser.parse_args(["sender-details", "get-default"])
        self.assertEqual(default_args.sender_details_cmd, "get-default")
        self.assertFalse(default_args.write_capable)

        mark_args = parser.parse_args(["sender-details", "mark-default", "--sender-details-id", "details-1"])
        self.assertEqual(mark_args.sender_details_cmd, "mark-default")
        self.assertTrue(mark_args.write_capable)

    @patch("wix_safe_agent_cli.commands.sender_details.HttpClient")
    def test_list_builds_expected_request(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {"senderDetails": [{"id": "details-1", "fromName": "Owner", "fromEmailAddress": "owner@example.com"}]}
        )
        args = SimpleNamespace(limit=20, cursor="next-cursor")

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = sender_details.cmd_sender_details_list(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["path"], "/sender-details/v1/sender-details")
        self.assertEqual(payload["request"]["params"]["paging.limit"], 20)
        self.assertEqual(payload["request"]["params"]["paging.cursor"], "next-cursor")

    def test_create_dry_run_builds_plan(self) -> None:
        args = SimpleNamespace(
            sender_details_json='{"senderDetails":{"fromName":"Owner","fromEmailAddress":"owner@example.com"}}'
        )

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = sender_details.cmd_sender_details_create(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["method"], "sender-details.create")

    def test_create_apply_requires_reviewed_plan(self) -> None:
        args = SimpleNamespace(
            sender_details_json='{"senderDetails":{"fromName":"Owner","fromEmailAddress":"owner@example.com"}}'
        )

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = sender_details.cmd_sender_details_create(args, self._ctx(apply=True, yes=True))
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("--plan-out", payload["reasons"][0])

    @patch("wix_safe_agent_cli.commands.sender_details.HttpClient")
    def test_get_default_builds_expected_request(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {"senderDetails": {"id": "details-1", "fromName": "Owner", "default": True}}
        )
        args = SimpleNamespace()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = sender_details.cmd_sender_details_get_default(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["path"], "/sender-details/v1/sender-details/default")

    @patch("wix_safe_agent_cli.commands.sender_details.HttpClient")
    def test_update_apply_requires_reviewed_plan(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {"senderDetails": {"id": "details-1", "fromName": "Owner", "fromEmailAddress": "owner@example.com"}}
        )
        args = SimpleNamespace(
            sender_details_id="details-1",
            sender_details_json='{"senderDetails":{"fromName":"New Owner"}}',
        )

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = sender_details.cmd_sender_details_update(args, self._ctx(apply=True, yes=True))
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("--plan-out", payload["reasons"][0])
        self.assertEqual(mock_client.return_value.request.call_count, 1)

    def test_delete_live_apply_requires_ack_irreversible(self) -> None:
        args = SimpleNamespace(sender_details_id="details-1")
        current = {"id": "details-1", "fromName": "Owner", "fromEmailAddress": "owner@example.com"}

        with patch.object(sender_details, "_get_sender_details", return_value=current), patch.object(
            sender_details, "_request_json"
        ) as mock_request:
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = sender_details.cmd_sender_details_delete(
                    args,
                    self._ctx(apply=True, yes=True, ack_irreversible=False),
                )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["method"], "sender-details.delete")
        self.assertFalse(mock_request.called)

    @patch("wix_safe_agent_cli.commands.sender_details.HttpClient")
    def test_mark_default_apply_requires_reviewed_plan(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {"senderDetails": {"id": "details-1", "fromName": "Owner", "fromEmailAddress": "owner@example.com"}}
        )
        args = SimpleNamespace(sender_details_id="details-1")

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = sender_details.cmd_sender_details_mark_default(args, self._ctx(apply=True, yes=True))
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("--plan-out", payload["reasons"][0])
        self.assertEqual(mock_client.return_value.request.call_count, 1)

    def test_create_live_apply_verifies_by_reread(self) -> None:
        args = SimpleNamespace(
            sender_details_json='{"senderDetails":{"fromName":"Owner","fromEmailAddress":"owner@example.com"}}'
        )
        plan = {
            "method": "sender-details.create",
            "baseline": {
                "env_fingerprint": "https://www.wixapis.com",
                "selector": {
                    "kind": "wix-sender-details",
                    "operation": "create",
                    "fromName": "Owner",
                    "fromEmailAddress": "owner@example.com",
                },
                "before_state": {},
            },
            "proposed_changes": [{"operation": "create", "fromName": "Owner", "fromEmailAddress": "owner@example.com"}],
        }
        plan_path = self._write_plan(plan)
        created = {"id": "details-1", "fromName": "Owner", "fromEmailAddress": "owner@example.com"}

        with patch.object(sender_details, "_request_json", return_value={"senderDetails": created}) as mock_request, patch.object(
            sender_details, "_get_sender_details", return_value=created
        ):
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = sender_details.cmd_sender_details_create(
                    args,
                    self._ctx(apply=True, yes=True, plan_in=plan_path),
                )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertFalse(payload["dry_run"])
        self.assertEqual(payload["receipt"]["verification"]["after"]["id"], "details-1")
        self.assertEqual(mock_request.call_count, 1)
