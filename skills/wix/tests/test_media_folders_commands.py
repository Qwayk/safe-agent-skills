from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import media_folders
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestMediaFoldersCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli media-folders",
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

    def test_parser_recognizes_media_folders_subcommands(self) -> None:
        parser = build_parser()

        list_args = parser.parse_args(["media-folders", "list"])
        self.assertEqual(list_args.media_folders_cmd, "list")
        self.assertFalse(list_args.write_capable)

        get_args = parser.parse_args(["media-folders", "get", "--folder-id", "folder-1"])
        self.assertEqual(get_args.media_folders_cmd, "get")
        self.assertFalse(get_args.write_capable)

        search_args = parser.parse_args(["media-folders", "search", "--search", "logo"])
        self.assertEqual(search_args.media_folders_cmd, "search")
        self.assertFalse(search_args.write_capable)

        search_root_folder = parser.parse_args(
            ["media-folders", "search", "--root-folder", "MEDIA_ROOT"]
        )
        self.assertEqual(search_root_folder.root_folder, "MEDIA_ROOT")

        query_args = parser.parse_args(["media-folders", "query", '--query-json', '{"filter":{}}'])
        self.assertEqual(query_args.media_folders_cmd, "query")
        self.assertFalse(query_args.write_capable)

        list_deleted_args = parser.parse_args(["media-folders", "list-deleted"])
        self.assertEqual(list_deleted_args.media_folders_cmd, "list-deleted")
        self.assertFalse(list_deleted_args.write_capable)

        create_args = parser.parse_args(["media-folders", "create", "--display-name", "Marketing"])
        self.assertEqual(create_args.media_folders_cmd, "create")
        self.assertTrue(create_args.write_capable)

        update_args = parser.parse_args(["media-folders", "update", "--folder-id", "folder-1", "--display-name", "New"])
        self.assertEqual(update_args.media_folders_cmd, "update")
        self.assertTrue(update_args.write_capable)

        bulk_delete_args = parser.parse_args(["media-folders", "bulk-delete", "--folder-ids-json", '["f1", "f2"]'])
        self.assertEqual(bulk_delete_args.media_folders_cmd, "bulk-delete")
        self.assertTrue(bulk_delete_args.write_capable)

        bulk_restore_args = parser.parse_args(["media-folders", "bulk-restore", "--folder-ids-json", '["f1", "f2"]'])
        self.assertEqual(bulk_restore_args.media_folders_cmd, "bulk-restore")
        self.assertTrue(bulk_restore_args.write_capable)

        generate_download_url_args = parser.parse_args(["media-folders", "generate-download-url", "--folder-id", "folder-1"])
        self.assertEqual(generate_download_url_args.media_folders_cmd, "generate-download-url")
        self.assertFalse(generate_download_url_args.write_capable)

    @patch("wix_safe_agent_cli.commands.media_folders.HttpClient")
    def test_media_folders_list_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"folders": []})
        args = SimpleNamespace(parent_folder_id="parent-1", cursor="c1", limit=25, sort_json='{"fieldName":"displayName","order":"ASC"}')
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = media_folders.cmd_media_folders_list(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["method"], "media-folders.list")
        request = payload["request"]
        self.assertEqual(request["method"], "GET")
        self.assertEqual(request["path"], "/site-media/v1/folders")
        self.assertEqual(request["params"]["parentFolderId"], "parent-1")
        self.assertEqual(request["params"]["paging.cursor"], "c1")
        self.assertEqual(request["params"]["paging.limit"], 25)
        self.assertEqual(request["params"]["sort.fieldName"], "displayName")
        self.assertEqual(request["params"]["sort.order"], "ASC")

    @patch("wix_safe_agent_cli.commands.media_folders.HttpClient")
    def test_media_folders_get_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"id": "folder-1"})
        args = SimpleNamespace(folder_id="folder-1")
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = media_folders.cmd_media_folders_get(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["method"], "media-folders.get")
        request = payload["request"]
        self.assertEqual(request["method"], "GET")
        self.assertEqual(request["path"], "/site-media/v1/folders/folder-1")

    @patch("wix_safe_agent_cli.commands.media_folders.HttpClient")
    def test_media_folders_search_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"folders": []})
        args = SimpleNamespace(search="logo", root_folder="MEDIA_ROOT", cursor="cursor-1", limit=20, sort_json='{"fieldName":"createdDate","order":"DESC"}')
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = media_folders.cmd_media_folders_search(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["method"], "media-folders.search")
        request = payload["request"]
        body = request["body"]
        self.assertEqual(request["method"], "POST")
        self.assertEqual(request["path"], "/site-media/v1/folders/search")
        self.assertEqual(body["search"], "logo")
        self.assertEqual(body["rootFolder"], "MEDIA_ROOT")
        self.assertEqual(body["paging"]["cursor"], "cursor-1")
        self.assertEqual(body["paging"]["limit"], 20)
        self.assertEqual(body["sort"]["fieldName"], "createdDate")
        self.assertEqual(body["sort"]["order"], "DESC")

    @patch("wix_safe_agent_cli.commands.media_folders.HttpClient")
    def test_media_folders_query_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"folders": []})
        args = SimpleNamespace(
            query_json='{"filter":{"name":"promo"}}',
            sort_json='[{"fieldName":"displayName","order":"ASC"}]',
            limit=10,
            offset=0,
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = media_folders.cmd_media_folders_query(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        request = payload["request"]
        self.assertEqual(request["method"], "POST")
        self.assertEqual(request["path"], "/site-media/v1/folders/query")
        query = request["body"]["query"]
        self.assertEqual(query["filter"]["name"], "promo")
        self.assertEqual(query["sort"][0]["fieldName"], "displayName")
        self.assertEqual(query["paging"]["limit"], 10)
        self.assertEqual(query["paging"]["offset"], 0)

    def test_media_folders_query_rejects_limit_above_two_hundred(self) -> None:
        args = SimpleNamespace(
            query_json='{"filter":{"name":"promo"}}',
            sort_json=None,
            limit=201,
            offset=0,
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = media_folders.cmd_media_folders_query(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("at most 200", payload["error"])

    @patch("wix_safe_agent_cli.commands.media_folders.HttpClient")
    def test_media_folders_list_deleted_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"folders": []})
        args = SimpleNamespace(parent_folder_id="deleted-parent", cursor="cursor-2", limit=15, sort_json='{"fieldName":"updatedDate","order":"ASC"}')
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = media_folders.cmd_media_folders_list_deleted(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        request = payload["request"]
        self.assertEqual(request["method"], "GET")
        self.assertEqual(request["path"], "/site-media/v1/trash-bin/folders")
        self.assertEqual(request["params"]["parentFolderId"], "deleted-parent")
        self.assertEqual(request["params"]["paging.cursor"], "cursor-2")
        self.assertEqual(request["params"]["sort.order"], "ASC")

    @patch("wix_safe_agent_cli.commands.media_folders.HttpClient")
    def test_media_folders_create_dry_run_builds_plan(self, mock_client: unittest.mock.MagicMock) -> None:
        args = SimpleNamespace(display_name="Campaign Assets", parent_folder_id=None)
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = media_folders.cmd_media_folders_create(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["method"], "media-folders.create")
        self.assertEqual(payload["plan"]["request"]["method"], "POST")
        self.assertEqual(payload["plan"]["request"]["path"], "/site-media/v1/folders")
        self.assertEqual(payload["plan"]["request"]["body"]["displayName"], "Campaign Assets")
        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.media_folders.HttpClient")
    def test_media_folders_update_dry_run_fetches_before_state(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"folder": {"id": "folder-1", "displayName": "Old"}})
        args = SimpleNamespace(folder_id="folder-1", display_name="New name", parent_folder_id=None)
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = media_folders.cmd_media_folders_update(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["method"], "media-folders.update")
        self.assertEqual(payload["plan"]["request"]["method"], "PATCH")
        self.assertEqual(payload["plan"]["request"]["path"], "/site-media/v1/folders/folder-1")
        self.assertEqual(mock_client.return_value.request.call_count, 1)
        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["method"], "GET")

    @patch("wix_safe_agent_cli.commands.media_folders.HttpClient")
    def test_media_folders_bulk_delete_requires_folder_id_limit(self, mock_client: unittest.mock.MagicMock) -> None:
        args = SimpleNamespace(folder_ids_json='["f1","f2","f3"]', permanent="false")
        ctx = self._ctx()

        mock_client.return_value.request.return_value = _DummyResponse({"folders": [{"id":"f1"}, {"id":"f2"}, {"id":"f3"}]})
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = media_folders.cmd_media_folders_bulk_delete(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["method"], "media-folders.bulk-delete")
        self.assertEqual(payload["plan"]["request"]["body"]["folderIds"], ["f1", "f2", "f3"])
        self.assertFalse(payload["plan"]["request"]["body"]["permanent"])

    @patch("wix_safe_agent_cli.commands.media_folders.HttpClient")
    def test_media_folders_bulk_delete_rejects_more_than_hundred_folder_ids(self, mock_client: unittest.mock.MagicMock) -> None:
        folder_ids = [f"f{i}" for i in range(101)]
        args = SimpleNamespace(folder_ids_json=json.dumps(folder_ids), permanent="false")
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = media_folders.cmd_media_folders_bulk_delete(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("at most 100", payload["error"])
        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.media_folders.HttpClient")
    def test_media_folders_bulk_restore_dry_run_keeps_no_before_snapshot(self, mock_client: unittest.mock.MagicMock) -> None:
        args = SimpleNamespace(folder_ids_json='["f1","f2"]')
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = media_folders.cmd_media_folders_bulk_restore(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertFalse(payload["plan"]["state_capture"]["before_state_available"])
        self.assertIn("No useful before-state snapshot", payload["plan"]["state_capture"]["notes"])
        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.media_folders.HttpClient")
    def test_media_folders_generate_download_url_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"url": "https://cdn.example.com/f.zip"})
        args = SimpleNamespace(folder_id="folder-1")
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = media_folders.cmd_media_folders_generate_download_url(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        request = payload["request"]
        self.assertEqual(request["method"], "POST")
        self.assertEqual(request["path"], "/site-media/v1/folders/folder-1/generate-download-url")

    @patch("wix_safe_agent_cli.commands.media_folders.HttpClient")
    def test_media_folders_create_apply_refuses_without_plan(self, mock_client: unittest.mock.MagicMock) -> None:
        args = SimpleNamespace(display_name="Campaign Assets", parent_folder_id=None)
        ctx = self._ctx(apply=True, yes=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = media_folders.cmd_media_folders_create(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertEqual(payload["method"], "media-folders.create")
        self.assertEqual(mock_client.return_value.request.call_count, 0)

    @patch("wix_safe_agent_cli.commands.media_folders.HttpClient")
    def test_media_folders_update_apply_refuses_without_plan(self, mock_client: unittest.mock.MagicMock) -> None:
        args = SimpleNamespace(folder_id="folder-1", display_name="New name", parent_folder_id=None)
        ctx = self._ctx(apply=True, yes=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = media_folders.cmd_media_folders_update(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertEqual(payload["method"], "media-folders.update")
        self.assertEqual(mock_client.return_value.request.call_count, 0)

    @patch("wix_safe_agent_cli.commands.media_folders.HttpClient")
    def test_media_folders_bulk_delete_apply_refuses_without_plan(self, mock_client: unittest.mock.MagicMock) -> None:
        args = SimpleNamespace(folder_ids_json='["f1","f2"]', permanent="true")
        ctx = self._ctx(apply=True, yes=True, ack_irreversible=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = media_folders.cmd_media_folders_bulk_delete(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertEqual(payload["method"], "media-folders.bulk-delete")
        self.assertEqual(mock_client.return_value.request.call_count, 0)

    @patch("wix_safe_agent_cli.commands.media_folders.HttpClient")
    def test_media_folders_bulk_restore_apply_refuses_without_plan(self, mock_client: unittest.mock.MagicMock) -> None:
        args = SimpleNamespace(folder_ids_json='["f1","f2"]')
        ctx = self._ctx(apply=True, yes=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = media_folders.cmd_media_folders_bulk_restore(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertEqual(payload["method"], "media-folders.bulk-restore")
        self.assertEqual(mock_client.return_value.request.call_count, 0)

    @patch("wix_safe_agent_cli.commands.media_folders.HttpClient")
    def test_media_folders_bulk_restore_apply_uses_saved_plan_without_active_folder_preflight(
        self,
        mock_client: unittest.mock.MagicMock,
    ) -> None:
        args = SimpleNamespace(folder_ids_json='["f1","f2"]')
        plan = {
            "method": "media-folders.bulk-restore",
            "baseline": {
                "env_fingerprint": "https://www.wixapis.com",
                "selector": {
                    "kind": "wix-media-folder",
                    "operation": "bulk-restore",
                    "folder_ids": ["f1", "f2"],
                },
                "before_state": {},
            },
            "proposed_changes": [{"operation": "bulk-restore", "folder_ids": ["f1", "f2"]}],
        }
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as handle:
            json.dump(plan, handle)
            plan_path = handle.name

        ctx = self._ctx(apply=True, yes=True, plan_in=plan_path)
        mock_client.return_value.request.return_value = _DummyResponse({"restoredFolderIds": ["f1", "f2"]})

        try:
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = media_folders.cmd_media_folders_bulk_restore(args, ctx)
            payload = json.loads(buf.getvalue())
        finally:
            media_folders.Path(plan_path).unlink(missing_ok=True)

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertFalse(payload["dry_run"])
        self.assertEqual(payload["method"], "media-folders.bulk-restore")
        self.assertEqual(mock_client.return_value.request.call_count, 1)
        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["method"], "POST")
        self.assertEqual(call.kwargs["url"], "https://www.wixapis.com/site-media/v1/bulk/trash-bin/folders/restore")

    def test_media_folders_update_rejects_noop(self) -> None:
        args = SimpleNamespace(folder_id="folder-1", display_name=None, parent_folder_id=None)
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = media_folders.cmd_media_folders_update(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")
