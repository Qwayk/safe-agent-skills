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
from wix_safe_agent_cli.commands import data_folders
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestDataFoldersCommands(unittest.TestCase):
    def _ctx(self, **overrides) -> dict:
        cfg = SimpleNamespace(
            base_url="https://www.wixapis.com",
            timeout_s=30.0,
            access_token="site-app-token",
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
            "command_str": "wix-safe-agent-cli data-folders",
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

    def _write_plan(self, plan: dict) -> str:
        handle = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json")
        json.dump(plan, handle)
        handle.close()
        return handle.name

    def test_parser_recognizes_data_folders_subcommands(self) -> None:
        parser = build_parser()

        get_args = parser.parse_args(["data-folders", "get"])
        self.assertEqual(get_args.data_folders_cmd, "get")
        self.assertFalse(get_args.write_capable)

        create_args = parser.parse_args(["data-folders", "create", "--name", "Favorites"])
        self.assertEqual(create_args.data_folders_cmd, "create")
        self.assertTrue(create_args.write_capable)

        update_args = parser.parse_args(["data-folders", "update", "--folder-id", "folder-1", "--name", "Saved"])
        self.assertEqual(update_args.data_folders_cmd, "update")
        self.assertTrue(update_args.write_capable)

        delete_args = parser.parse_args(["data-folders", "delete", "--folder-id", "folder-1"])
        self.assertEqual(delete_args.data_folders_cmd, "delete")
        self.assertTrue(delete_args.write_capable)

        create_ref_args = parser.parse_args(
            ["data-folders", "create-collection-reference", "--collection-name", "RestaurantMenu", "--folder-id", "folder-1"]
        )
        self.assertEqual(create_ref_args.data_folders_cmd, "create-collection-reference")
        self.assertTrue(create_ref_args.write_capable)

        get_refs_args = parser.parse_args(
            ["data-folders", "get-collection-references", "--collection-name", "RestaurantMenu"]
        )
        self.assertEqual(get_refs_args.data_folders_cmd, "get-collection-references")
        self.assertFalse(get_refs_args.write_capable)

        delete_ref_args = parser.parse_args(
            ["data-folders", "delete-collection-reference", "--collection-name", "RestaurantMenu"]
        )
        self.assertEqual(delete_ref_args.data_folders_cmd, "delete-collection-reference")
        self.assertTrue(delete_ref_args.write_capable)

    @patch("wix_safe_agent_cli.commands.data_folders.HttpClient")
    def test_data_folders_get_root_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"folder": {"name": "", "folders": []}})
        args = SimpleNamespace(folder_id=None)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_folders.cmd_data_folders_get(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["method"], "data-folders.get")
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(payload["request"]["path"], "/wix-data/v1/folders")
        self.assertNotIn("params", payload["request"])

    @patch("wix_safe_agent_cli.commands.data_folders.HttpClient")
    def test_data_folders_create_dry_run_builds_plan(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"folder": {"name": "", "folders": []}})
        args = SimpleNamespace(name="Favorites", description="Pinned collections")

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_folders.cmd_data_folders_create(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["request"]["body"]["folderDetails"]["name"], "Favorites")
        self.assertEqual(payload["plan"]["request"]["body"]["folderDetails"]["description"], "Pinned collections")
        self.assertEqual(mock_client.return_value.request.call_count, 1)

    @patch("wix_safe_agent_cli.commands.data_folders.HttpClient")
    def test_data_folders_update_requires_at_least_one_field(self, mock_client: unittest.mock.MagicMock) -> None:
        args = SimpleNamespace(folder_id="folder-1", name=None, description=None)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_folders.cmd_data_folders_update(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("at least one", payload["error"].lower())
        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.data_folders.HttpClient")
    def test_data_folders_delete_apply_without_plan_is_refused_before_http_write(
        self, mock_client: unittest.mock.MagicMock
    ) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"folder": {"id": "folder-1", "name": "Favorites"}})
        args = SimpleNamespace(folder_id="folder-1")

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_folders.cmd_data_folders_delete(args, self._ctx(apply=True, yes=True, ack_irreversible=True))
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("--plan-in", payload["reasons"][0])
        self.assertEqual(mock_client.return_value.request.call_count, 1)

    @patch("wix_safe_agent_cli.commands.data_folders.HttpClient")
    def test_data_folders_delete_apply_uses_plan_and_verifies_absence(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"folder": {"id": "folder-1", "name": "Favorites"}}),
            _DummyResponse({"folder": {"id": "folder-1", "name": "Favorites"}}),
            _DummyResponse({"deleted": True}),
            RuntimeError("HTTP 404 Not Found"),
        ]
        args = SimpleNamespace(folder_id="folder-1")

        dry_buf = io.StringIO()
        with redirect_stdout(dry_buf):
            dry_rc = data_folders.cmd_data_folders_delete(args, self._ctx())
        dry_payload = json.loads(dry_buf.getvalue())
        plan_path = self._write_plan(dry_payload["plan"])
        try:
            apply_ctx = self._ctx(apply=True, yes=True, ack_irreversible=True, plan_in=plan_path)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = data_folders.cmd_data_folders_delete(args, apply_ctx)
            payload = json.loads(buf.getvalue())

            self.assertEqual(dry_rc, 0)
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["receipt"]["verification"]["after"]["status"], "DELETED")
        finally:
            Path(plan_path).unlink()

    @patch("wix_safe_agent_cli.commands.data_folders.HttpClient")
    def test_data_folders_create_collection_reference_apply_verifies_readback(
        self, mock_client: unittest.mock.MagicMock
    ) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"collectionReferences": []}),
            _DummyResponse({"collectionReferences": []}),
            _DummyResponse({"collectionReference": {"collectionName": "RestaurantMenu", "folderId": "folder-1"}}),
            _DummyResponse({"collectionReferences": [{"collectionName": "RestaurantMenu", "folderId": "folder-1"}]}),
        ]
        args = SimpleNamespace(collection_name="RestaurantMenu", folder_id="folder-1")

        dry_buf = io.StringIO()
        with redirect_stdout(dry_buf):
            dry_rc = data_folders.cmd_data_folders_create_collection_reference(args, self._ctx())
        dry_payload = json.loads(dry_buf.getvalue())
        plan_path = self._write_plan(dry_payload["plan"])
        try:
            apply_ctx = self._ctx(apply=True, yes=True, plan_in=plan_path)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = data_folders.cmd_data_folders_create_collection_reference(args, apply_ctx)
            payload = json.loads(buf.getvalue())

            self.assertEqual(dry_rc, 0)
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["receipt"]["verification"]["after"]["folderId"], "folder-1")
        finally:
            Path(plan_path).unlink()

    @patch("wix_safe_agent_cli.commands.data_folders.HttpClient")
    def test_data_folders_delete_collection_reference_dry_run_refuses_missing_reference(
        self, mock_client: unittest.mock.MagicMock
    ) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"collectionReferences": []})
        args = SimpleNamespace(collection_name="RestaurantMenu", folder_id="folder-1")

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_folders.cmd_data_folders_delete_collection_reference(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("does not exist", payload["reasons"][0])
