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
from wix_safe_agent_cli.commands import referral_program
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestReferralProgramCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli referral-program",
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

    def test_parser_recognizes_referral_program_commands(self) -> None:
        parser = build_parser()
        cases = [
            ["referral-program", "get"],
            ["referral-program", "get-premium-features"],
            ["referral-program", "get-ai-social-media-posts-suggestions"],
            ["referral-program", "activate"],
            ["referral-program", "pause"],
            ["referral-program", "generate-ai-social-media-posts-suggestions"],
            ["referral-program", "update", "--program-json", '{"program":{"revision":"1"}}'],
        ]
        for argv in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertTrue(callable(args.func))

    @patch("wix_safe_agent_cli.commands.referral_program.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.referral_program.HttpClient")
    def test_get_uses_official_path(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"program": {"status": "ACTIVE"}})

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = referral_program.cmd_referral_program_get(SimpleNamespace(), self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(payload["request"]["path"], "/_api/referral-programs/v1/program")
        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "referral-program")

    @patch("wix_safe_agent_cli.commands.referral_program.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.referral_program.HttpClient")
    def test_generate_ai_suggestions_is_plan_first(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = referral_program.cmd_referral_program_generate_ai_social_media_posts_suggestions(SimpleNamespace(), self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["method"], "referralProgram.generateAISocialMediaPostsSuggestions")
        self.assertEqual(payload["plan"]["request"]["method"], "POST")
        self.assertEqual(payload["plan"]["request"]["path"], "/_api/referral-programs/v1/program/ai-social-media-posts-suggestions")
        self.assertNotIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.referral_program.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.referral_program.HttpClient")
    def test_update_requires_revision_and_apply_uses_matching_plan(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"program": {"revision": "2"}})

        missing_buf = io.StringIO()
        with redirect_stdout(missing_buf):
            missing_rc = referral_program.cmd_referral_program_update(
                SimpleNamespace(program_json='{"program":{"status":"ACTIVE"}}'),
                self._ctx(),
            )

        with tempfile.TemporaryDirectory() as tmp:
            plan_path = Path(tmp) / "plan.json"
            plan = {
                "method": "referralProgram.updateReferralProgram",
                "baseline": {
                    "env_fingerprint": "https://www.wixapis.com",
                    "selector": {"kind": "referral-program", "operation": "update"},
                },
                "proposed_changes": [{"operation": "update"}],
            }
            plan_path.write_text(json.dumps(plan), encoding="utf-8")

            apply_buf = io.StringIO()
            with redirect_stdout(apply_buf):
                apply_rc = referral_program.cmd_referral_program_update(
                    SimpleNamespace(program_json='{"program":{"revision":"1","status":"ACTIVE"}}'),
                    self._ctx(apply=True, yes=True, plan_in=str(plan_path)),
                )

        missing = json.loads(missing_buf.getvalue())
        applied = json.loads(apply_buf.getvalue())
        self.assertEqual(missing_rc, 1)
        self.assertEqual(missing["error_type"], "ValidationError")
        self.assertIn("revision", missing["error"])
        self.assertEqual(apply_rc, 0)
        self.assertFalse(applied["dry_run"])
        self.assertEqual(applied["receipt"]["request"]["method"], "PATCH")
        self.assertEqual(applied["receipt"]["request"]["path"], "/_api/referral-programs/v1/program")
        mock_client.return_value.request.assert_called_once()
