from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import loyalty_tiers
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = action, payload


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestLoyaltyTiersCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli loyalty-tiers",
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

    def test_parser_exposes_loyalty_tiers_commands(self) -> None:
        parser = build_parser()
        cases = [
            (["loyalty-tiers", "list"], "list", False),
            (["loyalty-tiers", "get", "--tier-id", "tier-1"], "get", False),
            (["loyalty-tiers", "create", "--tier-json", '{"tier":{"requiredPoints":200}}'], "create", True),
            (
                ["loyalty-tiers", "update", "--tier-id", "tier-1", "--tier-json", '{"tier":{"requiredPoints":400}}'],
                "update",
                True,
            ),
            (["loyalty-tiers", "delete", "--tier-id", "tier-1", "--revision", "1"], "delete", True),
            (["loyalty-tiers", "bulk-create", "--tiers-json", '{"tiers":[{"requiredPoints":200}]}'], "bulk-create", True),
            (["loyalty-tiers", "get-program"], "get-program", True),
            (
                [
                    "loyalty-tiers",
                    "create-program-settings",
                    "--program-settings-json",
                    '{"programSettings":{"status":"ACTIVE","rollingWindow":{"durationInMonths":12}}}',
                ],
                "create-program-settings",
                True,
            ),
            (["loyalty-tiers", "get-program-settings"], "get-program-settings", False),
            (
                [
                    "loyalty-tiers",
                    "update-program-settings",
                    "--program-settings-json",
                    '{"programSettings":{"status":"ACTIVE","revision":"1","rollingWindow":{"durationInMonths":12}}}',
                ],
                "update-program-settings",
                True,
            ),
        ]
        for argv, command, write_capable in cases:
            with self.subTest(command=command):
                args = parser.parse_args(argv)
                self.assertEqual(args.loyalty_tiers_cmd, command)
                self.assertEqual(args.write_capable, write_capable)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_read_commands_use_official_paths(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"tiers": []})
        cases = [
            (loyalty_tiers.cmd_loyalty_tiers_list, SimpleNamespace(), "GET", "/loyalty-tiers/v1/tiers"),
            (
                loyalty_tiers.cmd_loyalty_tiers_get,
                SimpleNamespace(tier_id="tier-1"),
                "GET",
                "/loyalty-tiers/v1/tiers/tier-1",
            ),
            (
                loyalty_tiers.cmd_loyalty_tiers_get_program_settings,
                SimpleNamespace(),
                "GET",
                "/loyalty-tiers/v1/tiers/program-settings",
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

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_write_commands_are_plan_first_and_ack_gated(self, mock_client: unittest.mock.MagicMock) -> None:
        cases = [
            (
                loyalty_tiers.cmd_loyalty_tiers_create,
                SimpleNamespace(tier_json='{"tier":{"requiredPoints":200}}'),
                "POST",
                "/loyalty-tiers/v1/tiers",
            ),
            (
                loyalty_tiers.cmd_loyalty_tiers_update,
                SimpleNamespace(tier_id="tier-1", tier_json='{"tier":{"requiredPoints":400}}'),
                "PATCH",
                "/loyalty-tiers/v1/tiers/tier-1",
            ),
            (
                loyalty_tiers.cmd_loyalty_tiers_delete,
                SimpleNamespace(tier_id="tier-1", revision="1"),
                "DELETE",
                "/loyalty-tiers/v1/tiers/tier-1?revision=1",
            ),
            (
                loyalty_tiers.cmd_loyalty_tiers_bulk_create,
                SimpleNamespace(tiers_json='{"tiers":[{"requiredPoints":200}]}'),
                "POST",
                "/loyalty-tiers/v1/bulk/tiers/create",
            ),
            (
                loyalty_tiers.cmd_loyalty_tiers_get_program,
                SimpleNamespace(),
                "GET",
                "/loyalty-tiers/v1/tiers/program",
            ),
            (
                loyalty_tiers.cmd_loyalty_tiers_create_program_settings,
                SimpleNamespace(
                    program_settings_json='{"programSettings":{"status":"ACTIVE","rollingWindow":{"durationInMonths":12}}}'
                ),
                "POST",
                "/loyalty-tiers/v1/tiers/program-settings",
            ),
            (
                loyalty_tiers.cmd_loyalty_tiers_update_program_settings,
                SimpleNamespace(
                    program_settings_json='{"programSettings":{"status":"ACTIVE","revision":"1","rollingWindow":{"durationInMonths":12}}}'
                ),
                "PATCH",
                "/loyalty-tiers/v1/tiers/program-settings",
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
    def test_rejects_missing_required_body_fields(self, mock_client: unittest.mock.MagicMock) -> None:
        cases = [
            (loyalty_tiers.cmd_loyalty_tiers_create, SimpleNamespace(tier_json="{}")),
            (loyalty_tiers.cmd_loyalty_tiers_bulk_create, SimpleNamespace(tiers_json='{"tiers":[]}')),
            (
                loyalty_tiers.cmd_loyalty_tiers_update_program_settings,
                SimpleNamespace(program_settings_json='{"programSettings":{"status":"ACTIVE","revision":"1"}}'),
            ),
        ]
        for func, args in cases:
            with self.subTest(func=func.__name__):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 1)
                self.assertEqual(payload["error_type"], "ValidationError")
        self.assertFalse(mock_client.return_value.request.called)
