from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import app_permissions
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


class TestAppPermissionsParser(unittest.TestCase):
    def test_parser_recognizes_app_permissions_subcommands_and_write_capable(self) -> None:
        parser = build_parser()

        list_args = parser.parse_args(["app-permissions", "list", "--app-id", "app-1"])
        self.assertEqual(list_args.app_permissions_cmd, "list")
        self.assertFalse(list_args.write_capable)
        self.assertEqual(list_args.func.__name__, "cmd_app_permissions_list")

        create_args = parser.parse_args([
            "app-permissions",
            "create",
            "--app-id",
            "app-1",
            "--permission-id",
            "perm-1",
        ])
        self.assertEqual(create_args.app_permissions_cmd, "create")
        self.assertTrue(create_args.write_capable)
        self.assertEqual(create_args.func.__name__, "cmd_app_permissions_create")

        delete_args = parser.parse_args([
            "app-permissions",
            "delete",
            "--app-id",
            "app-1",
            "--permission-id",
            "perm-1",
        ])
        self.assertEqual(delete_args.app_permissions_cmd, "delete")
        self.assertTrue(delete_args.write_capable)
        self.assertEqual(delete_args.func.__name__, "cmd_app_permissions_delete")


class TestAppPermissionsCommands(unittest.TestCase):
    def _ctx(self, **overrides) -> dict:
        cfg = SimpleNamespace(
            base_url="https://www.wixapis.com",
            timeout_s=30.0,
            app_id=None,
            app_secret=None,
            instance_id=None,
            access_token="token-abc",
            api_key="acct-api-key",
            account_id="acct-123",
            has_official_app_auth=False,
        )
        ctx = {
            "cfg": cfg,
            "env_file": "/tmp/.env",
            "tool": "wix-safe-agent-cli",
            "tool_version": "0.0.0",
            "command_str": "wix-safe-agent-cli app-permissions",
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

    @patch("wix_safe_agent_cli.commands.app_permissions.HttpClient")
    def test_app_permissions_list_request_shape_and_auth_headers(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"appPermissions": []})

        args = SimpleNamespace(app_id="app-1", consistent="true", cursor="cursor-1", limit=25)
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = app_permissions.cmd_app_permissions_list(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(payload["request"]["path"], "/apps/v1/app-permissions/v1/app-permissions")
        self.assertEqual(payload["request"]["params"], {"appId": "app-1", "consistent": True, "cursor": "cursor-1", "limit": 25})

        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["method"], "GET")
        self.assertEqual(call.kwargs["url"], "https://www.wixapis.com/apps/v1/app-permissions/v1/app-permissions")
        self.assertEqual(call.kwargs["params"], {"appId": "app-1", "consistent": True, "cursor": "cursor-1", "limit": 25})
        self.assertEqual(call.kwargs["headers"]["Authorization"], "token-abc")
        self.assertNotIn("wix-account-id", call.kwargs["headers"])

    @patch("wix_safe_agent_cli.commands.app_permissions.HttpClient")
    def test_app_permissions_create_dry_run_builds_plan(self, mock_client: unittest.mock.MagicMock) -> None:
        args = SimpleNamespace(app_permission_json=None, app_id="app-1", permission_id="perm-1")
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = app_permissions.cmd_app_permissions_create(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["method"], "app-permissions.create")
        self.assertEqual(payload["plan"]["request"]["method"], "POST")
        self.assertEqual(payload["plan"]["request"]["path"], "/apps/v1/app-permissions/v1/app-permissions")
        self.assertEqual(
            payload["plan"]["request"]["body"],
            {"appPermission": {"appId": "app-1", "permission": {"permissionId": "perm-1"}}},
        )
        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.app_permissions.HttpClient")
    def test_app_permissions_create_apply_without_plan_is_refused_before_request(self, mock_client: unittest.mock.MagicMock) -> None:
        args = SimpleNamespace(app_permission_json=None, app_id="app-1", permission_id="perm-1")
        ctx = self._ctx(apply=True, yes=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = app_permissions.cmd_app_permissions_create(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertEqual(payload["method"], "app-permissions.create")
        self.assertEqual(mock_client.return_value.request.call_count, 0)

    @patch("wix_safe_agent_cli.commands.app_permissions.HttpClient")
    def test_app_permissions_create_apply_with_plan_executes_post_and_verifies(self, mock_client: unittest.mock.MagicMock) -> None:
        plan = {
            "method": "app-permissions.create",
            "baseline": {
                "env_fingerprint": "https://www.wixapis.com",
                "selector": {
                    "kind": "wix-app-permission",
                    "operation": "create",
                    "app_id": "app-1",
                    "permission_id": "perm-1",
                },
                "before_state": {},
            },
        }

        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False, suffix=".json") as handle:
            json.dump(plan, handle)
            plan_path = handle.name

        try:
            mock_client.return_value.request.side_effect = [
                _DummyResponse({"ok": True}),
                _DummyResponse({"appPermissions": [{"permission": {"permissionId": "perm-1"}}]}),
            ]

            args = SimpleNamespace(app_permission_json=None, app_id="app-1", permission_id="perm-1")
            ctx = self._ctx(apply=True, yes=True, plan_in=plan_path)

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = app_permissions.cmd_app_permissions_create(args, ctx)
            payload = json.loads(buf.getvalue())

            self.assertEqual(rc, 0)
            self.assertFalse(payload["dry_run"])
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["method"], "app-permissions.create")
            self.assertTrue(payload["receipt"]["verification"]["ok"])

            calls = mock_client.return_value.request.call_args_list
            self.assertEqual(len(calls), 2)

            post_call = calls[0]
            self.assertEqual(post_call.kwargs["method"], "POST")
            self.assertEqual(post_call.kwargs["url"], "https://www.wixapis.com/apps/v1/app-permissions/v1/app-permissions")
            self.assertEqual(
                post_call.kwargs["headers"]["Authorization"],
                "acct-api-key",
            )
            self.assertEqual(post_call.kwargs["headers"]["wix-account-id"], "acct-123")
            self.assertEqual(
                post_call.kwargs["json_body"],
                {"appPermission": {"appId": "app-1", "permission": {"permissionId": "perm-1"}}},
            )

            verify_call = calls[1]
            self.assertEqual(verify_call.kwargs["method"], "GET")
            self.assertEqual(verify_call.kwargs["params"]["appId"], "app-1")
            self.assertTrue(verify_call.kwargs["params"]["consistent"])
        finally:
            import os

            os.unlink(plan_path)

    @patch("wix_safe_agent_cli.commands.app_permissions.HttpClient")
    def test_app_permissions_delete_dry_run_builds_plan(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {"appPermissions": [{"permission": {"permissionId": "perm-1"}}]}
        )

        args = SimpleNamespace(app_id="app-1", permission_id="perm-1")
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = app_permissions.cmd_app_permissions_delete(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["method"], "app-permissions.delete")
        self.assertEqual(payload["plan"]["request"]["method"], "DELETE")
        self.assertEqual(payload["plan"]["request"]["path"], "/apps/v1/app-permissions/v1/app-permissions")
        self.assertEqual(
            payload["plan"]["request"]["params"],
            {"appId": "app-1", "permissionId": "perm-1"},
        )
        self.assertEqual(mock_client.return_value.request.call_count, 1)

    @patch("wix_safe_agent_cli.commands.app_permissions.HttpClient")
    def test_app_permissions_delete_apply_without_plan_is_refused_before_request(self, mock_client: unittest.mock.MagicMock) -> None:
        args = SimpleNamespace(app_id="app-1", permission_id="perm-1")
        ctx = self._ctx(apply=True, yes=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = app_permissions.cmd_app_permissions_delete(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertEqual(payload["method"], "app-permissions.delete")
        self.assertEqual(mock_client.return_value.request.call_count, 0)

    @patch("wix_safe_agent_cli.commands.app_permissions.HttpClient")
    def test_app_permissions_delete_apply_without_ack_is_refused_before_request(self, mock_client: unittest.mock.MagicMock) -> None:
        args = SimpleNamespace(app_id="app-1", permission_id="perm-1")
        ctx = self._ctx(apply=True, yes=True, ack_irreversible=False)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = app_permissions.cmd_app_permissions_delete(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertEqual(payload["method"], "app-permissions.delete")
        self.assertEqual(mock_client.return_value.request.call_count, 0)

    @patch("wix_safe_agent_cli.commands.app_permissions.HttpClient")
    def test_app_permissions_delete_apply_with_plan_executes_delete_and_verifies_absence(self, mock_client: unittest.mock.MagicMock) -> None:
        plan = {
            "method": "app-permissions.delete",
            "baseline": {
                "env_fingerprint": "https://www.wixapis.com",
                "selector": {
                    "kind": "wix-app-permission",
                    "operation": "delete",
                    "app_id": "app-1",
                    "permission_id": "perm-1",
                },
                "before_state": {},
            },
        }

        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False, suffix=".json") as handle:
            json.dump(plan, handle)
            plan_path = handle.name

        try:
            mock_client.return_value.request.side_effect = [
                _DummyResponse({"ok": True}),
                _DummyResponse({"appPermissions": [{"permission": {"permissionId": "perm-other"}}]}),
            ]

            args = SimpleNamespace(app_id="app-1", permission_id="perm-1")
            ctx = self._ctx(apply=True, yes=True, ack_irreversible=True, plan_in=plan_path)

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = app_permissions.cmd_app_permissions_delete(args, ctx)
            payload = json.loads(buf.getvalue())

            self.assertEqual(rc, 0)
            self.assertFalse(payload["dry_run"])
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["method"], "app-permissions.delete")
            self.assertTrue(payload["receipt"]["verification"]["ok"])

            calls = mock_client.return_value.request.call_args_list
            self.assertEqual(len(calls), 2)

            delete_call = calls[0]
            self.assertEqual(delete_call.kwargs["method"], "DELETE")
            self.assertEqual(
                delete_call.kwargs["url"],
                "https://www.wixapis.com/apps/v1/app-permissions/v1/app-permissions",
            )
            self.assertEqual(
                delete_call.kwargs["headers"]["Authorization"],
                "acct-api-key",
            )
            self.assertEqual(delete_call.kwargs["headers"]["wix-account-id"], "acct-123")
            self.assertEqual(delete_call.kwargs["params"], {"appId": "app-1", "permissionId": "perm-1"})

            verify_call = calls[1]
            self.assertEqual(verify_call.kwargs["method"], "GET")
            self.assertTrue(verify_call.kwargs["params"]["consistent"])
        finally:
            import os

            os.unlink(plan_path)

    @patch("wix_safe_agent_cli.commands.app_permissions.HttpClient")
    def test_app_permissions_create_with_app_permission_json_file(self, mock_client: unittest.mock.MagicMock) -> None:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False, suffix=".json") as handle:
            json.dump({"appId": "app-json", "permission": {"permissionId": "perm-json"}}, handle)
            json_path = handle.name

        try:
            args = SimpleNamespace(
                app_permission_json=f"@{json_path}",
                app_id=None,
                permission_id=None,
            )
            ctx = self._ctx()

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = app_permissions.cmd_app_permissions_create(args, ctx)
            payload = json.loads(buf.getvalue())

            self.assertEqual(rc, 0)
            self.assertTrue(payload["dry_run"])
            self.assertEqual(
                payload["plan"]["request"]["body"],
                {"appPermission": {"appId": "app-json", "permission": {"permissionId": "perm-json"}}},
            )
            mock_client.return_value.request.assert_not_called()
        finally:
            import os

            os.unlink(json_path)
