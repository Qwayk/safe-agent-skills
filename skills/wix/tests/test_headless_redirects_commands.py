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
from wix_safe_agent_cli.commands import headless_redirects
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestHeadlessRedirectsCommands(unittest.TestCase):
    def _ctx(self, **overrides) -> dict:
        cfg = SimpleNamespace(
            base_url="https://www.wixapis.com",
            timeout_s=30.0,
            access_token="token-abc",
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
            "command_str": "wix-safe-agent-cli headless-redirects create-redirect-session",
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

    def test_parser_exposes_headless_redirects_command(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "headless-redirects",
                "create-redirect-session",
                "--redirect-session-json",
                '{"ecomCheckout":{"checkoutId":"7d2b240c-5c60-4580-8bc3-948bca6b4e4e"},"callbacks":{"postFlowUrl":"https://example.com/order-confirmation"}}',
            ]
        )

        self.assertIs(args.func, headless_redirects.cmd_headless_redirects_create_redirect_session)
        self.assertTrue(args.write_capable)

    @patch("wix_safe_agent_cli.commands.headless_redirects.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.headless_redirects.HttpClient")
    def test_create_redirect_session_is_plan_first_and_uses_official_path(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = headless_redirects.cmd_headless_redirects_create_redirect_session(
                SimpleNamespace(
                    redirect_session_json='{"auth":{"authRequest":{"clientId":"11111111-1111-4111-8111-111111111111","responseType":"code","redirectUri":"https://example.com/callback","scope":"offline_access","sessionToken":"secret-session"}}}'
                ),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())
        rendered = json.dumps(payload)

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["method"], "headlessRedirects.createRedirectSession")
        self.assertEqual(payload["plan"]["request"]["method"], "POST")
        self.assertEqual(payload["plan"]["request"]["path"], "/_api/redirects-api/v1/redirect-session")
        self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
        self.assertIn("connected Wix site must be published", payload["plan"]["preconditions"])
        self.assertNotIn("secret-session", rendered)
        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "headless-redirects")
        mock_client.return_value.request.assert_not_called()

    def test_create_redirect_session_requires_exactly_one_intent(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = headless_redirects.cmd_headless_redirects_create_redirect_session(
                SimpleNamespace(
                    redirect_session_json='{"ecomCheckout":{"checkoutId":"7d2b240c-5c60-4580-8bc3-948bca6b4e4e"},"login":{}}'
                ),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("exactly one redirect intent", payload["error"])

    @patch("wix_safe_agent_cli.commands.headless_redirects.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.headless_redirects.HttpClient")
    def test_create_redirect_session_requires_ack_and_matching_plan(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse(
            {
                "redirectSession": {
                    "id": "redirect-1",
                    "fullUrl": "https://mysite.com/_api/redirect?state=ok",
                    "sessionToken": "secret-session",
                }
            }
        )

        with tempfile.TemporaryDirectory() as tmp:
            plan_path = Path(tmp) / "plan.json"
            plan = {
                "method": "headlessRedirects.createRedirectSession",
                "baseline": {
                    "env_fingerprint": "https://www.wixapis.com",
                    "selector": {"kind": "headless-redirects", "operation": "create-redirect-session"},
                },
                "proposed_changes": [{"operation": "create-redirect-session"}],
            }
            plan_path.write_text(json.dumps(plan), encoding="utf-8")

            refused_buf = io.StringIO()
            with redirect_stdout(refused_buf):
                refused_rc = headless_redirects.cmd_headless_redirects_create_redirect_session(
                    SimpleNamespace(redirect_session_json='{"login":{}}'),
                    self._ctx(apply=True, yes=True, plan_in=str(plan_path), ack_irreversible=False),
                )

            accepted_buf = io.StringIO()
            with redirect_stdout(accepted_buf):
                accepted_rc = headless_redirects.cmd_headless_redirects_create_redirect_session(
                    SimpleNamespace(redirect_session_json='{"login":{}}'),
                    self._ctx(apply=True, yes=True, plan_in=str(plan_path), ack_irreversible=True),
                )

        refused = json.loads(refused_buf.getvalue())
        accepted = json.loads(accepted_buf.getvalue())
        rendered = json.dumps(accepted)
        self.assertEqual(refused_rc, 0)
        self.assertTrue(refused["dry_run"])
        self.assertEqual(accepted_rc, 0)
        self.assertFalse(accepted["dry_run"])
        self.assertEqual(accepted["receipt"]["request"]["path"], "/_api/redirects-api/v1/redirect-session")
        self.assertEqual(accepted["receipt"]["response"]["redirectSession"]["sessionToken"], "[REDACTED]")
        self.assertIn("fullUrl", accepted["receipt"]["response"]["redirectSession"])
        self.assertNotIn("secret-session", rendered)
        mock_client.return_value.request.assert_called_once()
