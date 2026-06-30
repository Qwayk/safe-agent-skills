from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import dashboard_favorite_list
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestDashboardFavoriteListCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli dashboard-favorite-list",
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

    @staticmethod
    def _favorite_list(*, revision: str = "4") -> dict:
        return {
            "id": "favorite-list-1",
            "revision": revision,
            "favorites": [{"id": "favorite-1", "pageId": "page-1", "title": "Home"}],
        }

    def test_parser_recognizes_dashboard_favorite_list_subcommands_when_registered(self) -> None:
        parser = build_parser()
        root_subparsers = next(
            action for action in parser._actions if isinstance(action, __import__("argparse")._SubParsersAction)
        )
        if "dashboard-favorite-list" not in root_subparsers.choices:
            self.skipTest("dashboard-favorite-list parser is not registered yet")

        cases = [
            (
                ["dashboard-favorite-list", "get"],
                "get",
                False,
            ),
            (
                ["dashboard-favorite-list", "create", "--favorite-list-json", '{"favorites":[{"pageId":"page-1"}]}'],
                "create",
                True,
            ),
            (
                [
                    "dashboard-favorite-list",
                    "update",
                    "--favorite-list-json",
                    '{"id":"favorite-list-1","revision":"4","favorites":[{"pageId":"page-1"}]}',
                ],
                "update",
                True,
            ),
            (
                ["dashboard-favorite-list", "delete", "--favorite-list-id", "favorite-list-1"],
                "delete",
                True,
            ),
            (
                [
                    "dashboard-favorite-list",
                    "add-favorite",
                    "--favorite-json",
                    '{"pageId":"page-1","relativeUrl":"/dashboard/home","title":"Home"}',
                ],
                "add-favorite",
                True,
            ),
            (
                ["dashboard-favorite-list", "delete-favorite", "--favorite-id", "favorite-1"],
                "delete-favorite",
                True,
            ),
        ]
        for argv, command, write_capable in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertEqual(args.dashboard_favorite_list_cmd, command)
                self.assertEqual(args.write_capable, write_capable)

    @patch("wix_safe_agent_cli.commands.dashboard_favorite_list.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.dashboard_favorite_list.HttpClient")
    def test_read_command_uses_official_path(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"favoriteList": self._favorite_list()})

        args = SimpleNamespace()
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = dashboard_favorite_list.cmd_dashboard_favorite_list_get(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(payload["request"]["path"], "/dashboard/v1/user-favorite-list")
        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "dashboard-favorite-list")

    @patch("wix_safe_agent_cli.commands.dashboard_favorite_list.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.dashboard_favorite_list.HttpClient")
    def test_writes_build_plans_and_delete_requires_ack(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        cases = [
            (
                dashboard_favorite_list.cmd_dashboard_favorite_list_create,
                SimpleNamespace(favorite_list_json='{"favorites":[{"pageId":"page-1","title":"Home"}]}'),
                "POST",
                "/dashboard/v1/user-favorite-list",
                False,
                {"favoriteList": {"favorites": [{"pageId": "page-1", "title": "Home"}]}},
            ),
            (
                dashboard_favorite_list.cmd_dashboard_favorite_list_update,
                SimpleNamespace(
                    favorite_list_json='{"id":"favorite-list-1","revision":"4","favorites":[{"pageId":"page-1","title":"Home"}]}'
                ),
                "PATCH",
                "/dashboard/v1/user-favorite-list/favorite-list-1",
                False,
                {
                    "favoriteList": {
                        "id": "favorite-list-1",
                        "revision": "4",
                        "favorites": [{"pageId": "page-1", "title": "Home"}],
                    }
                },
            ),
            (
                dashboard_favorite_list.cmd_dashboard_favorite_list_add_favorite,
                SimpleNamespace(favorite_json='{"pageId":"page-1","relativeUrl":"/dashboard/home","title":"Home"}'),
                "POST",
                "/dashboard/v1/user-favorite-list/add-favorite",
                False,
                {
                    "favorite": {
                        "pageId": "page-1",
                        "relativeUrl": "/dashboard/home",
                        "title": "Home",
                    }
                },
            ),
            (
                dashboard_favorite_list.cmd_dashboard_favorite_list_delete,
                SimpleNamespace(favorite_list_id="favorite-list-1"),
                "DELETE",
                "/dashboard/v1/user-favorite-list/favorite-list-1",
                True,
                None,
            ),
            (
                dashboard_favorite_list.cmd_dashboard_favorite_list_delete_favorite,
                SimpleNamespace(favorite_id="favorite-1"),
                "DELETE",
                "/dashboard/v1/user-favorite-list/delete-favorite/favorite-1",
                True,
                None,
            ),
        ]
        for func, args, method, path, requires_ack, expected_body in cases:
            with self.subTest(path=path):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertTrue(payload["dry_run"])
                self.assertEqual(payload["plan"]["request"]["method"], method)
                self.assertEqual(payload["plan"]["request"]["path"], path)
                self.assertEqual(payload["plan"]["preconditions"][-1] == "apply also requires --ack-irreversible", requires_ack)
                if expected_body is not None:
                    self.assertEqual(payload["plan"]["request"]["body"], expected_body)

        mock_client.return_value.request.assert_not_called()

    def test_update_requires_favorite_list_id_and_revision(self) -> None:
        args = SimpleNamespace(favorite_list_json='{"id":"favorite-list-1","favorites":[{"pageId":"page-1"}]}')
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = dashboard_favorite_list.cmd_dashboard_favorite_list_update(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
