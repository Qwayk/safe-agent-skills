from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import loyalty_program
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = action, payload


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestLoyaltyProgramCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli loyalty-program",
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

    def test_parser_exposes_loyalty_program_commands(self) -> None:
        parser = build_parser()
        cases = [
            (["loyalty-program", "get"], "get", False),
            (["loyalty-program", "premium-features"], "premium-features", False),
            (
                ["loyalty-program", "update", "--program-json", '{"loyaltyProgram":{"name":"Stars"}}'],
                "update",
                True,
            ),
            (["loyalty-program", "activate"], "activate", True),
            (["loyalty-program", "pause"], "pause", True),
            (["loyalty-program", "enable-points-expiration"], "enable-points-expiration", True),
            (["loyalty-program", "disable-points-expiration"], "disable-points-expiration", True),
        ]
        for argv, command, write_capable in cases:
            with self.subTest(command=command):
                args = parser.parse_args(argv)
                self.assertEqual(args.loyalty_program_cmd, command)
                self.assertEqual(args.write_capable, write_capable)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_read_commands_use_official_paths(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"loyaltyProgram": {"status": "ACTIVE"}})
        cases = [
            (loyalty_program.cmd_loyalty_program_get, "GET", "/loyalty-programs/v1/program"),
            (
                loyalty_program.cmd_loyalty_program_premium_features,
                "GET",
                "/loyalty-programs/v1/program/premium-features",
            ),
        ]
        for func, method, path in cases:
            with self.subTest(path=path):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(SimpleNamespace(), self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertEqual(payload["request"]["method"], method)
                self.assertEqual(payload["request"]["path"], path)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_write_commands_are_plan_first_and_ack_gated(self, mock_client: unittest.mock.MagicMock) -> None:
        cases = [
            (
                loyalty_program.cmd_loyalty_program_update,
                SimpleNamespace(program_json='{"loyaltyProgram":{"name":"Stars"}}'),
                "PATCH",
                "/loyalty-programs/v1/program",
            ),
            (
                loyalty_program.cmd_loyalty_program_activate,
                SimpleNamespace(),
                "POST",
                "/loyalty-programs/v1/program/activate",
            ),
            (
                loyalty_program.cmd_loyalty_program_pause,
                SimpleNamespace(),
                "POST",
                "/loyalty-programs/v1/program/pause",
            ),
            (
                loyalty_program.cmd_loyalty_program_enable_points_expiration,
                SimpleNamespace(),
                "POST",
                "/loyalty-programs/v1/program/points-expiration/enable",
            ),
            (
                loyalty_program.cmd_loyalty_program_disable_points_expiration,
                SimpleNamespace(),
                "POST",
                "/loyalty-programs/v1/program/points-expiration/disable",
            ),
        ]
        for func, args, method, path in cases:
            with self.subTest(path=path):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertTrue(payload["dry_run"])
                self.assertEqual(payload["plan"]["request"]["method"], method)
                self.assertEqual(payload["plan"]["request"]["path"], path)
                self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
        self.assertFalse(mock_client.return_value.request.called)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_update_requires_loyalty_program_object(self, mock_client: unittest.mock.MagicMock) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = loyalty_program.cmd_loyalty_program_update(
                SimpleNamespace(program_json='{"name":"Stars"}'),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertFalse(mock_client.return_value.request.called)
