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
from wix_safe_agent_cli.commands import data_permissions
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestDataPermissionsCommands(unittest.TestCase):
    def _ctx(self, **overrides) -> dict:
        cfg = SimpleNamespace(
            base_url="https://www.wixapis.com",
            timeout_s=30.0,
            access_token="site-app-token",
            api_key=None,
            account_id=None,
            app_id=None,
            app_secret=None,
            instance_id=None,
            has_official_app_auth=False,
        )
        cfg_override = overrides.pop("cfg_override", None)
        if isinstance(cfg_override, dict):
            for field, value in cfg_override.items():
                setattr(cfg, field, value)
        ctx = {
            "cfg": cfg,
            "env_file": "/tmp/.env",
            "tool": "wix-safe-agent-cli",
            "tool_version": "0.0.0",
            "command_str": "wix-safe-agent-cli data-permissions",
            "verbose": False,
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
            "apply": False,
            "yes": False,
            "plan_out": None,
            "plan_in": None,
            "receipt_out": None,
            "ack_irreversible": False,
            "enforce_reviewed_plan": True,
        }
        ctx.update(overrides)
        return ctx

    def _write_plan(self, plan: dict) -> str:
        handle = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json")
        json.dump(plan, handle)
        handle.close()
        return handle.name

    def test_parser_recognizes_data_permissions_commands(self) -> None:
        parser = build_parser()

        get_args = parser.parse_args(["data-permissions", "get", "--data-collection-id", "collection-1"])
        self.assertEqual(get_args.data_permissions_cmd, "get")
        self.assertFalse(get_args.write_capable)

        get_my_args = parser.parse_args(["data-permissions", "get-my", "--data-collection-id", "collection-1"])
        self.assertEqual(get_my_args.data_permissions_cmd, "get-my")
        self.assertFalse(get_my_args.write_capable)

        update_args = parser.parse_args(
            [
                "data-permissions",
                "update",
                "--data-collection-id",
                "collection-1",
                "--item-read",
                "ANYONE",
                "--item-insert",
                "SITE_MEMBER",
                "--item-update",
                "CMS_EDITOR",
                "--item-remove",
                "PRIVILEGED",
            ]
        )
        self.assertEqual(update_args.data_permissions_cmd, "update")
        self.assertTrue(update_args.write_capable)

        remove_args = parser.parse_args(
            [
                "data-permissions",
                "remove-special",
                "--data-collection-id",
                "collection-1",
                "--special-permissions-id",
                "sp-1",
            ]
        )
        self.assertEqual(remove_args.data_permissions_cmd, "remove-special")
        self.assertTrue(remove_args.write_capable)

    @patch("wix_safe_agent_cli.commands.data_permissions.HttpClient")
    def test_get_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {"dataPermissions": {"id": "collection-1", "itemRead": "ANYONE"}}
        )
        args = SimpleNamespace(data_collection_id="collection-1")

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_permissions.cmd_data_permissions_get(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["method"], "data-permissions.get")
        self.assertEqual(payload["request"]["params"]["dataCollectionId"], "collection-1")
        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["method"], "GET")
        self.assertEqual(call.kwargs["url"], "https://www.wixapis.com/wix-data/v1/permissions")
        self.assertEqual(call.kwargs["headers"]["Authorization"], "site-app-token")

    @patch("wix_safe_agent_cli.commands.data_permissions.HttpClient")
    def test_get_my_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {"itemRead": True, "itemInsert": False, "itemUpdate": False, "itemRemove": False}
        )
        args = SimpleNamespace(data_collection_id="collection-1")

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_permissions.cmd_data_permissions_get_my(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["method"], "data-permissions.get-my")
        self.assertEqual(payload["request"]["path"], "/wix-data/v1/permissions/current")

    @patch("wix_safe_agent_cli.commands.data_permissions.HttpClient")
    def test_update_dry_run_builds_plan(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {
                "dataPermissions": {
                    "id": "collection-1",
                    "itemRead": "SITE_MEMBER",
                    "itemInsert": "SITE_MEMBER",
                    "itemUpdate": "CMS_EDITOR",
                    "itemRemove": "PRIVILEGED",
                    "specialPermissions": [],
                }
            }
        )
        args = SimpleNamespace(
            data_collection_id="collection-1",
            item_read="ANYONE",
            item_insert="SITE_MEMBER",
            item_update="CMS_EDITOR",
            item_remove="PRIVILEGED",
        )

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_permissions.cmd_data_permissions_update(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["request"]["path"], "/wix-data/v1/permissions")
        self.assertEqual(payload["plan"]["request"]["body"]["dataPermissions"]["id"], "collection-1")
        self.assertEqual(payload["plan"]["request"]["body"]["dataPermissions"]["itemRead"], "ANYONE")

    @patch("wix_safe_agent_cli.commands.data_permissions.HttpClient")
    def test_update_apply_without_plan_refuses_before_write(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {
                "dataPermissions": {
                    "id": "collection-1",
                    "itemRead": "SITE_MEMBER",
                    "itemInsert": "SITE_MEMBER",
                    "itemUpdate": "CMS_EDITOR",
                    "itemRemove": "PRIVILEGED",
                    "specialPermissions": [],
                }
            }
        )
        args = SimpleNamespace(
            data_collection_id="collection-1",
            item_read="ANYONE",
            item_insert="SITE_MEMBER",
            item_update="CMS_EDITOR",
            item_remove="PRIVILEGED",
        )

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_permissions.cmd_data_permissions_update(args, self._ctx(apply=True, yes=True))
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertEqual(mock_client.return_value.request.call_count, 1)

    @patch("wix_safe_agent_cli.commands.data_permissions.HttpClient")
    def test_add_special_apply_without_plan_refuses_before_write(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {
                "dataPermissions": {
                    "id": "collection-1",
                    "itemRead": "ANYONE",
                    "itemInsert": "SITE_MEMBER",
                    "itemUpdate": "CMS_EDITOR",
                    "itemRemove": "PRIVILEGED",
                    "specialPermissions": [],
                }
            }
        )
        args = SimpleNamespace(
            data_collection_id="collection-1",
            user_id="user-1",
            policy_id=None,
            item_read="ALLOWED",
            item_insert="UNSPECIFIED",
            item_update="ALLOWED",
            item_remove="UNSPECIFIED",
        )

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_permissions.cmd_data_permissions_add_special(args, self._ctx(apply=True, yes=True))
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertEqual(mock_client.return_value.request.call_count, 1)

    @patch("wix_safe_agent_cli.commands.data_permissions.HttpClient")
    def test_add_special_dry_run_refuses_if_identity_already_exists(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {
                "dataPermissions": {
                    "id": "collection-1",
                    "itemRead": "ANYONE",
                    "itemInsert": "SITE_MEMBER",
                    "itemUpdate": "CMS_EDITOR",
                    "itemRemove": "PRIVILEGED",
                    "specialPermissions": [{"id": "sp-1", "userId": "user-1"}],
                }
            }
        )
        args = SimpleNamespace(
            data_collection_id="collection-1",
            user_id="user-1",
            policy_id=None,
            item_read="ALLOWED",
            item_insert="UNSPECIFIED",
            item_update="ALLOWED",
            item_remove="UNSPECIFIED",
        )

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_permissions.cmd_data_permissions_add_special(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("already exist", payload["reasons"][0])

    @patch("wix_safe_agent_cli.commands.data_permissions.HttpClient")
    def test_add_special_apply_uses_plan_and_verifies(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse(
                {
                    "dataPermissions": {
                        "id": "collection-1",
                        "itemRead": "ANYONE",
                        "itemInsert": "SITE_MEMBER",
                        "itemUpdate": "CMS_EDITOR",
                        "itemRemove": "PRIVILEGED",
                        "specialPermissions": [],
                    }
                }
            ),
            _DummyResponse(
                {
                    "dataPermissions": {
                        "id": "collection-1",
                        "itemRead": "ANYONE",
                        "itemInsert": "SITE_MEMBER",
                        "itemUpdate": "CMS_EDITOR",
                        "itemRemove": "PRIVILEGED",
                        "specialPermissions": [],
                    }
                }
            ),
            _DummyResponse(
                {
                    "dataPermissions": {
                        "id": "collection-1",
                        "itemRead": "ANYONE",
                        "itemInsert": "SITE_MEMBER",
                        "itemUpdate": "CMS_EDITOR",
                        "itemRemove": "PRIVILEGED",
                        "specialPermissions": [],
                    }
                }
            ),
            _DummyResponse(
                {
                    "specialPermissions": {
                        "id": "sp-1",
                        "userId": "user-1",
                        "itemRead": "ALLOWED",
                        "itemInsert": "UNSPECIFIED",
                        "itemUpdate": "ALLOWED",
                        "itemRemove": "UNSPECIFIED",
                    }
                }
            ),
            _DummyResponse(
                {
                    "dataPermissions": {
                        "id": "collection-1",
                        "itemRead": "ANYONE",
                        "itemInsert": "SITE_MEMBER",
                        "itemUpdate": "CMS_EDITOR",
                        "itemRemove": "PRIVILEGED",
                        "specialPermissions": [
                            {
                                "id": "sp-1",
                                "userId": "user-1",
                                "itemRead": "ALLOWED",
                                "itemInsert": "UNSPECIFIED",
                                "itemUpdate": "ALLOWED",
                                "itemRemove": "UNSPECIFIED",
                            }
                        ],
                    }
                }
            ),
        ]
        args = SimpleNamespace(
            data_collection_id="collection-1",
            user_id="user-1",
            policy_id=None,
            item_read="ALLOWED",
            item_insert="UNSPECIFIED",
            item_update="ALLOWED",
            item_remove="UNSPECIFIED",
        )

        dry_buf = io.StringIO()
        with redirect_stdout(dry_buf):
            data_permissions.cmd_data_permissions_add_special(args, self._ctx())
        plan_path = self._write_plan(json.loads(dry_buf.getvalue())["plan"])

        try:
            apply_buf = io.StringIO()
            with redirect_stdout(apply_buf):
                rc = data_permissions.cmd_data_permissions_add_special(
                    args,
                    self._ctx(apply=True, yes=True, plan_in=plan_path),
                )
            payload = json.loads(apply_buf.getvalue())

            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertFalse(payload["dry_run"])
            self.assertEqual(payload["receipt"]["verification"]["checks"][0]["field"], "id")
        finally:
            Path(plan_path).unlink(missing_ok=True)

    @patch("wix_safe_agent_cli.commands.data_permissions.HttpClient")
    def test_update_special_apply_without_plan_refuses_before_write(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {
                "dataPermissions": {
                    "id": "collection-1",
                    "specialPermissions": [{"id": "sp-1", "userId": "user-1"}],
                }
            }
        )
        args = SimpleNamespace(
            data_collection_id="collection-1",
            special_permissions_id="sp-1",
            user_id="user-1",
            policy_id=None,
            item_read="ALLOWED",
            item_insert="UNSPECIFIED",
            item_update="ALLOWED",
            item_remove="UNSPECIFIED",
        )

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_permissions.cmd_data_permissions_update_special(args, self._ctx(apply=True, yes=True))
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertEqual(mock_client.return_value.request.call_count, 1)

    @patch("wix_safe_agent_cli.commands.data_permissions.HttpClient")
    def test_update_special_requires_collection_id_for_verification(self, mock_client: unittest.mock.MagicMock) -> None:
        args = SimpleNamespace(
            data_collection_id=None,
            special_permissions_id="sp-1",
            user_id="user-1",
            policy_id=None,
            item_read="ALLOWED",
            item_insert="UNSPECIFIED",
            item_update="ALLOWED",
            item_remove="UNSPECIFIED",
        )

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_permissions.cmd_data_permissions_update_special(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertIn("data-collection-id", payload["error"])
        self.assertEqual(mock_client.return_value.request.call_count, 0)

    @patch("wix_safe_agent_cli.commands.data_permissions.HttpClient")
    def test_remove_special_apply_without_plan_refuses_before_write(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {
                "dataPermissions": {
                    "id": "collection-1",
                    "specialPermissions": [{"id": "sp-1", "userId": "user-1"}],
                }
            }
        )
        args = SimpleNamespace(data_collection_id="collection-1", special_permissions_id="sp-1")

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_permissions.cmd_data_permissions_remove_special(args, self._ctx(apply=True, yes=True))
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertEqual(mock_client.return_value.request.call_count, 1)

    @patch("wix_safe_agent_cli.commands.data_permissions.HttpClient")
    def test_remove_special_apply_uses_plan_and_verifies_absence(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse(
                {
                    "dataPermissions": {
                        "id": "collection-1",
                        "specialPermissions": [{"id": "sp-1", "userId": "user-1"}],
                    }
                }
            ),
            _DummyResponse(
                {
                    "dataPermissions": {
                        "id": "collection-1",
                        "specialPermissions": [{"id": "sp-1", "userId": "user-1"}],
                    }
                }
            ),
            _DummyResponse(
                {
                    "dataPermissions": {
                        "id": "collection-1",
                        "specialPermissions": [{"id": "sp-1", "userId": "user-1"}],
                    }
                }
            ),
            _DummyResponse({}),
            _DummyResponse({"dataPermissions": {"id": "collection-1", "specialPermissions": []}}),
        ]
        args = SimpleNamespace(data_collection_id="collection-1", special_permissions_id="sp-1")

        dry_buf = io.StringIO()
        with redirect_stdout(dry_buf):
            data_permissions.cmd_data_permissions_remove_special(args, self._ctx())
        plan_path = self._write_plan(json.loads(dry_buf.getvalue())["plan"])

        try:
            apply_buf = io.StringIO()
            with redirect_stdout(apply_buf):
                rc = data_permissions.cmd_data_permissions_remove_special(
                    args,
                    self._ctx(apply=True, yes=True, plan_in=plan_path),
                )
            payload = json.loads(apply_buf.getvalue())

            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertFalse(payload["dry_run"])
            self.assertIsNone(payload["receipt"]["verification"]["checks"][0]["actual"])
        finally:
            Path(plan_path).unlink(missing_ok=True)
