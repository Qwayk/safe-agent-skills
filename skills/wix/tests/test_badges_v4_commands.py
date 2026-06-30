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
from wix_safe_agent_cli.commands import badges_v4
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestBadgesV4Commands(unittest.TestCase):
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
            "verbose": False,
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
            "tool": "wix-safe-agent-cli",
            "tool_version": "0.0.0",
            "command_str": "wix-safe-agent-cli badges-v4",
            "apply": False,
            "yes": False,
            "plan_in": None,
            "plan_out": None,
            "receipt_out": None,
            "ack_irreversible": False,
            "enforce_reviewed_plan": True,
        }
        ctx.update(overrides)
        return ctx

    @patch("wix_safe_agent_cli.commands.badges_v4.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.badges_v4.HttpClient")
    def test_read_commands_use_official_paths(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"badges": []})

        cases = [
            (badges_v4.cmd_badges_v4_get, SimpleNamespace(badge_id="badge-1"), "GET", "/badges/v4/badges/badge-1", None),
            (
                badges_v4.cmd_badges_v4_query,
                SimpleNamespace(query_json='{"query":{"filter":{"title":{"$eq":"VIP"}}}}'),
                "POST",
                "/badges/v4/badges/query",
                {"query": {"filter": {"title": {"$eq": "VIP"}}}},
            ),
        ]
        for func, args, method, path, body in cases:
            with self.subTest(path=path):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertEqual(payload["request"]["method"], method)
                self.assertEqual(payload["request"]["path"], path)
                if body is not None:
                    self.assertEqual(payload["request"]["body"], body)

        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "badges-v4")

    @patch("wix_safe_agent_cli.commands.badges_v4.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.badges_v4.HttpClient")
    def test_write_commands_are_plan_first(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        cases = [
            (
                badges_v4.cmd_badges_v4_create,
                SimpleNamespace(badge_json='{"badge":{"title":"VIP"}}'),
                "POST",
                "/badges/v4/badges",
                {"kind": "badges-v4", "operation": "create"},
            ),
            (
                badges_v4.cmd_badges_v4_update,
                SimpleNamespace(badge_id="badge-1", badge_json='{"badge":{"title":"VIP+"}}'),
                "PATCH",
                "/badges/v4/badges/badge-1",
                {"kind": "badges-v4", "badge_id": "badge-1", "operation": "update"},
            ),
            (
                badges_v4.cmd_badges_v4_move,
                SimpleNamespace(badge_id="badge-1", move_json='{"afterBadgeId":"badge-0"}'),
                "POST",
                "/badges/v4/badges/badge-1/move",
                {"kind": "badges-v4", "badge_id": "badge-1", "operation": "move"},
            ),
        ]
        for func, args, method, path, selector in cases:
            with self.subTest(path=path):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertTrue(payload["dry_run"])
                self.assertEqual(payload["plan"]["request"]["method"], method)
                self.assertEqual(payload["plan"]["request"]["path"], path)
                self.assertEqual(payload["plan"]["selector"], selector)

        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.badges_v4.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.badges_v4.HttpClient")
    def test_delete_plan_requires_irreversible_ack(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = badges_v4.cmd_badges_v4_delete(SimpleNamespace(badge_id="badge-1"), self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["request"]["method"], "DELETE")
        self.assertEqual(payload["plan"]["request"]["path"], "/badges/v4/badges/badge-1")
        self.assertEqual(payload["plan"]["selector"], {"kind": "badges-v4", "badge_id": "badge-1", "operation": "delete"})
        self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.badges_v4.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.badges_v4.HttpClient")
    def test_reviewed_plan_apply_sends_request_and_emits_receipt(
        self,
        mock_client: unittest.mock.MagicMock,
        mock_auth: unittest.mock.MagicMock,
    ) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"badge": {"id": "badge-1", "title": "VIP"}})

        with tempfile.TemporaryDirectory() as tmp:
            plan_path = str(Path(tmp) / "plan.json")
            args = SimpleNamespace(badge_json='{"badge":{"title":"VIP"}}')
            dry_buf = io.StringIO()
            with redirect_stdout(dry_buf):
                dry_rc = badges_v4.cmd_badges_v4_create(args, self._ctx(plan_out=plan_path))
            self.assertEqual(dry_rc, 0)
            self.assertTrue(Path(plan_path).exists())
            mock_client.return_value.request.assert_not_called()

            apply_buf = io.StringIO()
            with redirect_stdout(apply_buf):
                apply_rc = badges_v4.cmd_badges_v4_create(args, self._ctx(apply=True, yes=True, plan_in=plan_path))
            payload = json.loads(apply_buf.getvalue())

        self.assertEqual(apply_rc, 0)
        self.assertFalse(payload["dry_run"])
        self.assertEqual(payload["receipt"]["request"]["path"], "/badges/v4/badges")
        self.assertEqual(payload["receipt"]["response"], {"badge": {"id": "badge-1", "title": "VIP"}})
        call = mock_client.return_value.request.call_args.kwargs
        self.assertEqual(call["method"], "POST")
        self.assertTrue(str(call["url"]).endswith("/badges/v4/badges"))

    def test_parser_exposes_badges_v4_commands_and_write_flags(self) -> None:
        parser = build_parser()
        cases = [
            (["badges-v4", "get", "--badge-id", "badge-1"], badges_v4.cmd_badges_v4_get, False),
            (["badges-v4", "query"], badges_v4.cmd_badges_v4_query, False),
            (["badges-v4", "create", "--badge-json", "{}"], badges_v4.cmd_badges_v4_create, True),
            (["badges-v4", "update", "--badge-id", "badge-1", "--badge-json", "{}"], badges_v4.cmd_badges_v4_update, True),
            (["badges-v4", "delete", "--badge-id", "badge-1"], badges_v4.cmd_badges_v4_delete, True),
            (["badges-v4", "move", "--badge-id", "badge-1", "--move-json", "{}"], badges_v4.cmd_badges_v4_move, True),
        ]
        for argv, func, write_capable in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertIs(args.func, func)
                self.assertEqual(args.write_capable, write_capable)
