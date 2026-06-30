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
from wix_safe_agent_cli.commands import b2b_site_transfer
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = action, payload


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestB2BSiteTransferCommands(unittest.TestCase):
    def _ctx(self, **overrides) -> dict:
        cfg = SimpleNamespace(
            base_url="https://www.wixapis.com",
            timeout_s=30.0,
            access_token=None,
            api_key="api-key",
            account_id="target-account",
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
            "command_str": "wix-safe-agent-cli b2b-site-transfer transfer",
            "apply": False,
            "yes": False,
            "verbose": False,
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
            "plan_in": None,
            "plan_out": None,
            "receipt_out": None,
            "ack_irreversible": False,
            "enforce_reviewed_plan": False,
        }
        ctx.update(overrides)
        return ctx

    def test_parser_recognizes_transfer(self) -> None:
        parser = build_parser()
        body = '{"siteId":"site-1","sourceAccountId":"source-account"}'
        parsed = parser.parse_args(["b2b-site-transfer", "transfer", "--site-transfer-json", body])
        self.assertEqual(parsed.b2b_site_transfer_cmd, "transfer")
        self.assertTrue(parsed.write_capable)

    def test_transfer_dry_run_builds_irreversible_account_plan(self) -> None:
        args = SimpleNamespace(site_transfer_json='{"siteId":"site-1","sourceAccountId":"source-account","enableNotifications":false}')
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = b2b_site_transfer.cmd_b2b_site_transfer_transfer(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["auth_mode"], "account_api_key")
        self.assertEqual(payload["plan"]["request"]["path"], "/b2b-site-management/v1/transfer-site")
        self.assertEqual(payload["plan"]["request"]["body"]["siteTransfer"]["siteId"], "site-1")
        self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
        self.assertEqual(payload["plan"]["selector"]["targetAccountHeader"], "target-account")

    def test_transfer_requires_site_and_source_account(self) -> None:
        args = SimpleNamespace(site_transfer_json='{"siteId":"site-1"}')
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = b2b_site_transfer.cmd_b2b_site_transfer_transfer(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertIn("sourceAccountId", payload["error"])

    @patch("wix_safe_agent_cli.commands.b2b_site_transfer.HttpClient")
    def test_transfer_apply_uses_account_headers(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"siteTransfer": {"siteId": "site-1"}})
        plan = {
            "method": "b2b-site-transfer.transfer",
            "baseline": {
                "env_fingerprint": "https://www.wixapis.com",
                "selector": {"siteId": "site-1", "sourceAccountId": "source-account", "targetAccountHeader": "target-account"},
            },
            "proposed_changes": [{"operation": "transfer"}],
        }
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as handle:
            json.dump(plan, handle)
            plan_path = handle.name
        try:
            ctx = self._ctx(apply=True, yes=True, ack_irreversible=True, plan_in=plan_path)
            args = SimpleNamespace(site_transfer_json='{"siteId":"site-1","sourceAccountId":"source-account"}')
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = b2b_site_transfer.cmd_b2b_site_transfer_transfer(args, ctx)
            payload = json.loads(buf.getvalue())
        finally:
            Path(plan_path).unlink()

        self.assertEqual(rc, 0)
        self.assertFalse(payload["dry_run"])
        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["method"], "POST")
        self.assertTrue(str(call.kwargs["url"]).endswith("/b2b-site-management/v1/transfer-site"))
        self.assertEqual(call.kwargs["headers"]["Authorization"], "api-key")
        self.assertEqual(call.kwargs["headers"]["wix-account-id"], "target-account")


if __name__ == "__main__":
    unittest.main()
