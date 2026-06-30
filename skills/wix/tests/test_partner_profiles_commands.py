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
from wix_safe_agent_cli.commands import partner_profiles
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = action, payload


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestPartnerProfilesCommands(unittest.TestCase):
    def _ctx(self, **overrides) -> dict:
        cfg = SimpleNamespace(
            base_url="https://www.wixapis.com",
            timeout_s=30.0,
            access_token=None,
            api_key="api-key",
            account_id="account-1",
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
            "command_str": "wix-safe-agent-cli partner-profiles create",
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

    def test_parser_recognizes_commands(self) -> None:
        parser = build_parser()
        create = parser.parse_args(["partner-profiles", "create", "--profile-json", '{"professionalInformation":{"businessName":"Agency"}}'])
        public = parser.parse_args(["partner-profiles", "find-public-by-slug", "--slug", "agency"])
        self.assertEqual(create.partner_profiles_cmd, "create")
        self.assertTrue(create.write_capable)
        self.assertEqual(public.partner_profiles_cmd, "find-public-by-slug")
        self.assertFalse(public.write_capable)

    def test_create_dry_run_uses_account_api_key_plan(self) -> None:
        args = SimpleNamespace(profile_json='{"professionalInformation":{"businessName":"Agency"}}')
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = partner_profiles.cmd_partner_profiles_create(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["auth_mode"], "account_api_key")
        self.assertEqual(payload["plan"]["request"]["method"], "POST")
        self.assertEqual(payload["plan"]["request"]["path"], "/partners/profile/v1/partner-profiles")
        self.assertEqual(payload["plan"]["request"]["body"]["partnerProfile"]["professionalInformation"]["businessName"], "Agency")

    def test_update_requires_revision(self) -> None:
        args = SimpleNamespace(profile_json='{"id":"partner-1","professionalInformation":{"businessName":"Agency"}}')
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = partner_profiles.cmd_partner_profiles_update(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertIn("revision", payload["error"])

    def test_delete_dry_run_requires_irreversible_ack(self) -> None:
        args = SimpleNamespace()
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = partner_profiles.cmd_partner_profiles_delete(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])

    @patch("wix_safe_agent_cli.commands.partner_profiles.HttpClient")
    def test_get_public_uses_no_auth_headers(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"publicPartnerProfile": {"id": "partner-1"}})
        args = SimpleNamespace(partner_id="partner-1")
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = partner_profiles.cmd_partner_profiles_get_public(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["auth_mode"], "none")
        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["headers"], {})
        self.assertTrue(str(call.kwargs["url"]).endswith("/partners/profile/v1/partner-profiles/partner-1/public"))

    @patch("wix_safe_agent_cli.commands.partner_profiles.HttpClient")
    def test_update_apply_uses_official_path_and_account_headers(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"partnerProfile": {"id": "partner-1", "revision": "2"}})
        plan = {
            "method": "partner-profiles.update",
            "baseline": {
                "env_fingerprint": "https://www.wixapis.com",
                "selector": {"operation": "update", "profileId": "partner-1", "revision": "1"},
            },
            "proposed_changes": [{"operation": "update"}],
        }
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as handle:
            json.dump(plan, handle)
            plan_path = handle.name
        try:
            ctx = self._ctx(apply=True, yes=True, plan_in=plan_path)
            args = SimpleNamespace(profile_json='{"id":"partner-1","revision":"1","professionalInformation":{"businessName":"Agency"}}')
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = partner_profiles.cmd_partner_profiles_update(args, ctx)
            payload = json.loads(buf.getvalue())
        finally:
            Path(plan_path).unlink()

        self.assertEqual(rc, 0)
        self.assertFalse(payload["dry_run"])
        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["method"], "PATCH")
        self.assertTrue(str(call.kwargs["url"]).endswith("/partners/profile/v1/partner-profiles"))
        self.assertEqual(call.kwargs["headers"]["Authorization"], "api-key")
        self.assertEqual(call.kwargs["headers"]["wix-account-id"], "account-1")


if __name__ == "__main__":
    unittest.main()
