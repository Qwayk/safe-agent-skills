from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import notifications
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def __init__(self) -> None:
        self.writes: list[tuple[str, dict]] = []

    def write(self, action: str, payload: dict) -> None:
        self.writes.append((action, payload))


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestNotificationsCommands(unittest.TestCase):
    def _ctx(self, *, cfg_override: dict | None = None, **overrides) -> dict:
        cfg = SimpleNamespace(
            base_url="https://www.wixapis.com",
            timeout_s=30.0,
            access_token="app-token",
            api_key="acct-api-key",
            account_id="acct-001",
            app_id=None,
            app_secret=None,
            instance_id=None,
            has_official_app_auth=True,
        )
        if cfg_override:
            for key, value in cfg_override.items():
                setattr(cfg, key, value)

        ctx = {
            "cfg": cfg,
            "env_file": "/tmp/.env",
            "tool": "wix-safe-agent-cli",
            "tool_version": "0.0.0",
            "command_str": "wix-safe-agent-cli notifications notify",
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

    def _args(self, **kwargs) -> SimpleNamespace:
        data = {
            "notification_template_id": "template-1",
            "dynamic_values_json": None,
            "notify_json": None,
        }
        data.update(kwargs)
        return SimpleNamespace(**data)

    def test_parser_recognizes_notifications_notify(self) -> None:
        parser = build_parser()

        parsed = parser.parse_args(["notifications", "notify", "--notification-template-id", "tpl-1"])
        self.assertEqual(parsed.notifications_cmd, "notify")
        self.assertTrue(parsed.write_capable)
        self.assertEqual(parsed.func.__name__, "cmd_notifications_notify")

    def test_notifications_notify_dry_run_builds_plan(self) -> None:
        args = self._args(dynamic_values_json='{"greeting":{"text":"Welcome"}}')
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = notifications.cmd_notifications_notify(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["method"], "notifications.notify")
        self.assertEqual(payload["plan"]["request"]["method"], "POST")
        self.assertEqual(payload["plan"]["request"]["path"], "/notifications/v3/notify")
        self.assertEqual(payload["plan"]["request"]["body"]["notificationTemplateId"], "template-1")
        self.assertEqual(
            payload["plan"]["request"]["body"].get("dynamicValues"),
            {"greeting": {"text": "Welcome"}},
        )

    @patch("wix_safe_agent_cli.commands.notifications.HttpClient")
    def test_notifications_notify_apply_without_plan_in_refuses_before_http(self, mock_client: unittest.mock.MagicMock) -> None:
        args = self._args()
        ctx = self._ctx(apply=True, yes=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = notifications.cmd_notifications_notify(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertTrue(payload["refused"])
        self.assertEqual(mock_client.return_value.request.call_count, 0)

    def _build_plan_file(self, args: SimpleNamespace) -> str:
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as handle:
            plan_path = handle.name

        try:
            ctx = self._ctx(plan_out=plan_path)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = notifications.cmd_notifications_notify(args, ctx)
            self.assertEqual(rc, 0)
            self.assertTrue(Path(plan_path).exists())
            return plan_path
        except Exception:
            Path(plan_path).unlink(missing_ok=True)
            raise

    @patch("wix_safe_agent_cli.commands.notifications.HttpClient")
    def test_notifications_notify_apply_with_plan_posts_notifications_endpoint(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"notificationBatchId": "batch-1"})

        args = self._args()
        plan_path = self._build_plan_file(args)

        try:
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = notifications.cmd_notifications_notify(args, self._ctx(apply=True, yes=True, plan_in=plan_path))
            payload = json.loads(buf.getvalue())

            self.assertEqual(rc, 0)
            self.assertFalse(payload["dry_run"])
            self.assertTrue(payload["ok"])
            self.assertEqual(mock_client.return_value.request.call_count, 1)
            call = mock_client.return_value.request.call_args_list[0]
            self.assertEqual(call.kwargs["method"], "POST")
            self.assertEqual(call.kwargs["json_body"], {"notificationTemplateId": "template-1"})
            self.assertTrue(str(call.kwargs["url"]).endswith("/notifications/v3/notify"))
        finally:
            Path(plan_path).unlink(missing_ok=True)

    @patch("wix_safe_agent_cli.commands.notifications.HttpClient")
    def test_notifications_notify_auth_uses_app_token_not_account_api_key(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"notificationBatchId": "batch-2"})

        args = self._args()
        plan_path = self._build_plan_file(args)

        try:
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = notifications.cmd_notifications_notify(
                    args,
                    self._ctx(
                        apply=True,
                        yes=True,
                        plan_in=plan_path,
                        cfg_override={
                            "access_token": "token-via-app",
                            "api_key": "acct-api-key-should-not-be-used",
                            "account_id": "acct-should-not-be-used",
                        },
                    ),
                )
            payload = json.loads(buf.getvalue())

            self.assertEqual(rc, 0)
            headers = mock_client.return_value.request.call_args.kwargs["headers"]
            self.assertEqual(headers["Authorization"], "token-via-app")
            self.assertNotIn("wix-account-id", headers)
            self.assertNotIn("x-wix-client-app-instance-id", headers)
        finally:
            Path(plan_path).unlink(missing_ok=True)

    @patch("wix_safe_agent_cli.commands.notifications.HttpClient")
    def test_notifications_notify_receipt_verification_is_provider_response_only(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"accepted": True})

        args = self._args()
        plan_path = self._build_plan_file(args)
        try:
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = notifications.cmd_notifications_notify(args, self._ctx(apply=True, yes=True, plan_in=plan_path))
            payload = json.loads(buf.getvalue())

            self.assertEqual(rc, 1)
            self.assertEqual(payload["receipt"]["verification"]["type"], "provider-response")
            self.assertFalse(payload["receipt"]["verification"]["ok"])
            self.assertIn("notificationBatchId", payload["receipt"]["verification"]["notes"])
        finally:
            Path(plan_path).unlink(missing_ok=True)

    def test_notifications_dynamic_values_json_file_and_validation(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as handle:
            handle.write('{"greeting": {"text": "Hello"}}')
            json_path = handle.name

        try:
            args = self._args(dynamic_values_json=f"@{json_path}")
            ctx = self._ctx()
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = notifications.cmd_notifications_notify(args, ctx)
            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(
                payload["plan"]["request"]["body"]["dynamicValues"],
                {"greeting": {"text": "Hello"}},
            )
        finally:
            Path(json_path).unlink(missing_ok=True)

        bad_args = self._args(dynamic_values_json='{"greeting": {"value": "Hello"}}')
        bad_ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = notifications.cmd_notifications_notify(bad_args, bad_ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertIn("text", payload["error"])
