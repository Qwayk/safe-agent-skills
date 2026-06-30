from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import files
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


class TestFilesCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli files",
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

    def test_parser_recognizes_new_files_subcommands(self) -> None:
        parser = build_parser()

        update_args = parser.parse_args(["files", "update", "--file-id", "file-1", "--file-json", '{"displayName":"New"}'])
        self.assertEqual(update_args.files_cmd, "update")
        self.assertTrue(update_args.write_capable)

        bulk_delete_args = parser.parse_args(["files", "bulk-delete", "--file-ids-json", '["f1","f2"]'])
        self.assertEqual(bulk_delete_args.files_cmd, "bulk-delete")
        self.assertTrue(bulk_delete_args.write_capable)

        bulk_restore_args = parser.parse_args(["files", "bulk-restore", "--file-ids-json", '["f1","f2"]'])
        self.assertEqual(bulk_restore_args.files_cmd, "bulk-restore")
        self.assertTrue(bulk_restore_args.write_capable)

        upload_args = parser.parse_args(["files", "generate-upload-url", "--upload-json", '{"mimeType":"image/png"}'])
        self.assertEqual(upload_args.files_cmd, "generate-upload-url")
        self.assertFalse(upload_args.write_capable)

        resumable_args = parser.parse_args(
            ["files", "generate-resumable-upload-url", "--upload-json", '{"mimeType":"image/png"}']
        )
        self.assertEqual(resumable_args.files_cmd, "generate-resumable-upload-url")
        self.assertFalse(resumable_args.write_capable)

        import_args = parser.parse_args(["files", "import", "--import-json", '{"url":"https://example.com/a.png"}'])
        self.assertEqual(import_args.files_cmd, "import")
        self.assertTrue(import_args.write_capable)

        download_args = parser.parse_args(
            ["files", "generate-download-url", "--download-json", '{"fileId":"file-1"}']
        )
        self.assertEqual(download_args.files_cmd, "generate-download-url")
        self.assertFalse(download_args.write_capable)

    @patch("wix_safe_agent_cli.commands.files.HttpClient")
    def test_files_list_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {"files": [], "pagingMetadata": {"nextCursor": "cursor-2"}}
        )
        args = SimpleNamespace(
            parent_folder_id="media-root",
            media_types_json='["IMAGE","VIDEO"]',
            private="true",
            sort_json='{"fieldName":"updatedDate","order":"DESC"}',
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = files.cmd_files_list(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(payload["request"]["path"], "/site-media/v1/files")
        request_params = payload["request"]["params"]
        self.assertEqual(request_params["parentFolderId"], "media-root")
        self.assertEqual(request_params["mediaTypes"], ["IMAGE", "VIDEO"])
        self.assertTrue(request_params["private"])
        self.assertEqual(request_params["sort.fieldName"], "updatedDate")
        self.assertEqual(request_params["sort.order"], "DESC")

    @patch("wix_safe_agent_cli.commands.files.HttpClient")
    def test_files_get_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"file": {"id": "4acbb8"}})
        args = SimpleNamespace(file_id="wix:image://v1/0abec0_.../leon.jpg#originWidth=3024&originHeight=4032")
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = files.cmd_files_get(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(payload["request"]["path"], "/site-media/v1/files/get-file-by-id")
        self.assertEqual(
            payload["request"]["params"]["fileId"],
            "wix:image://v1/0abec0_.../leon.jpg#originWidth=3024&originHeight=4032",
        )

    @patch("wix_safe_agent_cli.commands.files.HttpClient")
    def test_files_batch_get_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"files": []})
        args = SimpleNamespace(file_ids_json='["id-1","id-2","id-3"]')
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = files.cmd_files_batch_get(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["method"], "POST")
        self.assertEqual(payload["request"]["path"], "/site-media/v1/files/get-files")
        self.assertEqual(payload["request"]["body"]["fileIds"], ["id-1", "id-2", "id-3"])

    @patch("wix_safe_agent_cli.commands.files.HttpClient")
    def test_files_batch_get_rejects_more_than_100_ids(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"files": []})
        args = SimpleNamespace(file_ids_json='[' + ",".join([f'"id-{i}"' for i in range(101)]) + "]")
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = files.cmd_files_batch_get(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")

    @patch("wix_safe_agent_cli.commands.files.HttpClient")
    def test_files_search_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {"files": [], "pagingMetadata": {"nextCursor": "cursor-99"}}
        )
        args = SimpleNamespace(
            search="building",
            media_types_json='["IMAGE"]',
            private="false",
            root_folder="MEDIA_ROOT",
            sort_json='{"fieldName":"displayName","order":"ASC"}',
            cursor="cursor-1",
            limit=10,
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = files.cmd_files_search(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["method"], "POST")
        self.assertEqual(payload["request"]["path"], "/site-media/v1/files/search")
        request_body = payload["request"]["body"]
        self.assertEqual(request_body["search"], "building")
        self.assertEqual(request_body["mediaTypes"], ["IMAGE"])
        self.assertFalse(request_body["private"])
        self.assertEqual(request_body["rootFolder"], "MEDIA_ROOT")
        self.assertEqual(request_body["sort"]["fieldName"], "displayName")
        self.assertEqual(request_body["sort"]["order"], "ASC")
        self.assertEqual(request_body["paging"]["cursor"], "cursor-1")
        self.assertEqual(request_body["paging"]["limit"], 10)

    @patch("wix_safe_agent_cli.commands.files.HttpClient")
    def test_files_query_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"files": []})
        args = SimpleNamespace(query_json='{"filter":{"mediaType":{"$in":["IMAGE","VIDEO"]}}}')
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = files.cmd_files_query(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["method"], "POST")
        self.assertEqual(payload["request"]["path"], "/site-media/v1/files/query")
        self.assertEqual(payload["request"]["body"]["query"]["filter"]["mediaType"]["$in"], ["IMAGE", "VIDEO"])

    @patch("wix_safe_agent_cli.commands.files.HttpClient")
    def test_files_list_deleted_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"files": []})
        args = SimpleNamespace(
            parent_folder_id="media-root",
            media_types_json='["VIDEO"]',
            private="true",
            sort_json='{"fieldName":"sizeInBytes","order":"DESC"}',
            cursor="cursor-del",
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = files.cmd_files_list_deleted(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(payload["request"]["path"], "/site-media/v1/trash-bin/files")
        request_params = payload["request"]["params"]
        self.assertEqual(request_params["parentFolderId"], "media-root")
        self.assertEqual(request_params["mediaTypes"], ["VIDEO"])
        self.assertTrue(request_params["private"])
        self.assertEqual(request_params["sort.fieldName"], "sizeInBytes")
        self.assertEqual(request_params["sort.order"], "DESC")
        self.assertEqual(request_params["paging.cursor"], "cursor-del")

    @patch("wix_safe_agent_cli.commands.files.HttpClient")
    def test_files_update_dry_run_fetches_before_state(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"file": {"id": "file-1", "displayName": "Old"}})
        args = SimpleNamespace(file_id="file-1", file_json='{"displayName":"New"}')
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = files.cmd_files_update(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["method"], "files.update")
        self.assertEqual(payload["plan"]["request"]["method"], "PATCH")
        self.assertEqual(payload["plan"]["request"]["path"], "/site-media/v1/files/update-file-descriptor")
        self.assertEqual(mock_client.return_value.request.call_count, 1)
        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["method"], "GET")

    @patch("wix_safe_agent_cli.commands.files.HttpClient")
    def test_files_bulk_delete_dry_run_captures_snapshot_for_small_batch(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"files": [{"id": "f1"}, {"id": "f2"}]})
        args = SimpleNamespace(file_ids_json='["f1","f2"]', permanent="false")
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = files.cmd_files_bulk_delete(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertTrue(payload["plan"]["state_capture"]["before_state_available"])
        self.assertEqual(payload["plan"]["request"]["body"]["fileIds"], ["f1", "f2"])
        self.assertFalse(payload["plan"]["request"]["body"]["permanent"])

    @patch("wix_safe_agent_cli.commands.files.HttpClient")
    def test_files_bulk_delete_large_batch_keeps_no_snapshot_note(self, mock_client: unittest.mock.MagicMock) -> None:
        args = SimpleNamespace(file_ids_json=json.dumps([f"f{i}" for i in range(101)]), permanent="true")
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = files.cmd_files_bulk_delete(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertFalse(payload["plan"]["state_capture"]["before_state_available"])
        self.assertIn("more than 100 files", payload["plan"]["state_capture"]["notes"])
        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.files.HttpClient")
    def test_files_bulk_restore_dry_run_keeps_no_snapshot(self, mock_client: unittest.mock.MagicMock) -> None:
        args = SimpleNamespace(file_ids_json='["f1","f2"]')
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = files.cmd_files_bulk_restore(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertFalse(payload["plan"]["state_capture"]["before_state_available"])
        self.assertIn("deleted-file get-by-id", payload["plan"]["state_capture"]["notes"])
        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.files.HttpClient")
    def test_files_import_dry_run_builds_plan(self, mock_client: unittest.mock.MagicMock) -> None:
        args = SimpleNamespace(import_json='{"url":"https://example.com/file.png","mimeType":"image/png"}')
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = files.cmd_files_import(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["method"], "files.import")
        self.assertEqual(payload["plan"]["request"]["path"], "/site-media/v1/files/import")
        self.assertFalse(payload["plan"]["state_capture"]["before_state_available"])
        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.files.HttpClient")
    def test_files_generate_upload_url_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"uploadUrl": "https://upload.example.com"})
        args = SimpleNamespace(upload_json='{"mimeType":"image/png","fileName":"hero.png"}')
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = files.cmd_files_generate_upload_url(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["method"], "files.generate-upload-url")
        self.assertEqual(payload["request"]["path"], "/site-media/v1/files/generate-upload-url")

    @patch("wix_safe_agent_cli.commands.files.HttpClient")
    def test_files_generate_resumable_upload_url_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"uploadUrl": "https://upload.example.com/resume"})
        args = SimpleNamespace(upload_json='{"mimeType":"video/mp4","uploadProtocol":"TUS"}')
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = files.cmd_files_generate_resumable_upload_url(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["method"], "files.generate-resumable-upload-url")
        self.assertEqual(payload["request"]["path"], "/site-media/v1/files/generate-resumable-upload-url")

    @patch("wix_safe_agent_cli.commands.files.HttpClient")
    def test_files_generate_download_url_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"downloadUrls": [{"url": "https://cdn.example.com/file.png"}]})
        args = SimpleNamespace(download_json='{"fileId":"file-1","expirationInMinutes":30}')
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = files.cmd_files_generate_download_url(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["method"], "files.generate-download-url")
        self.assertEqual(payload["request"]["path"], "/site-media/v1/files/generate-file-download-url")

    @patch("wix_safe_agent_cli.commands.files.HttpClient")
    def test_files_update_apply_refuses_without_plan(self, mock_client: unittest.mock.MagicMock) -> None:
        args = SimpleNamespace(file_id="file-1", file_json='{"displayName":"New"}')
        ctx = self._ctx(apply=True, yes=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = files.cmd_files_update(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertEqual(payload["method"], "files.update")
        self.assertEqual(mock_client.return_value.request.call_count, 0)

    @patch("wix_safe_agent_cli.commands.files.HttpClient")
    def test_files_bulk_delete_apply_refuses_without_plan(self, mock_client: unittest.mock.MagicMock) -> None:
        args = SimpleNamespace(file_ids_json='["f1","f2"]', permanent="true")
        ctx = self._ctx(apply=True, yes=True, ack_irreversible=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = files.cmd_files_bulk_delete(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertEqual(payload["method"], "files.bulk-delete")
        self.assertEqual(mock_client.return_value.request.call_count, 0)

    @patch("wix_safe_agent_cli.commands.files.HttpClient")
    def test_files_bulk_restore_apply_refuses_without_plan(self, mock_client: unittest.mock.MagicMock) -> None:
        args = SimpleNamespace(file_ids_json='["f1","f2"]')
        ctx = self._ctx(apply=True, yes=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = files.cmd_files_bulk_restore(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertEqual(payload["method"], "files.bulk-restore")
        self.assertEqual(mock_client.return_value.request.call_count, 0)

    @patch("wix_safe_agent_cli.commands.files.HttpClient")
    def test_files_import_apply_refuses_without_plan(self, mock_client: unittest.mock.MagicMock) -> None:
        args = SimpleNamespace(import_json='{"url":"https://example.com/file.png"}')
        ctx = self._ctx(apply=True, yes=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = files.cmd_files_import(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertEqual(payload["method"], "files.import")
        self.assertEqual(mock_client.return_value.request.call_count, 0)

    @patch("wix_safe_agent_cli.commands.files.HttpClient")
    def test_files_bulk_restore_apply_uses_saved_plan(self, mock_client: unittest.mock.MagicMock) -> None:
        args = SimpleNamespace(file_ids_json='["f1","f2"]')
        plan = {
            "method": "files.bulk-restore",
            "baseline": {
                "env_fingerprint": "https://www.wixapis.com",
                "selector": {
                    "kind": "wix-media-file",
                    "operation": "bulk-restore",
                    "file_ids": ["f1", "f2"],
                },
                "before_state": [],
            },
            "proposed_changes": [{"operation": "bulk-restore", "file_ids": ["f1", "f2"]}],
            "state_capture": {
                "before_state_available": False,
                "notes": "No useful before-state snapshot is available for trash-bin restore because this tool does not ship a direct deleted-file get-by-id read path.",
            },
        }
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as handle:
            json.dump(plan, handle)
            plan_path = handle.name

        ctx = self._ctx(apply=True, yes=True, plan_in=plan_path)
        mock_client.return_value.request.return_value = _DummyResponse({"restoredFileIds": ["f1", "f2"]})

        try:
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = files.cmd_files_bulk_restore(args, ctx)
            payload = json.loads(buf.getvalue())
        finally:
            files.Path(plan_path).unlink(missing_ok=True)

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertFalse(payload["dry_run"])
        self.assertEqual(payload["method"], "files.bulk-restore")
        self.assertEqual(mock_client.return_value.request.call_count, 1)
        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["method"], "POST")
        self.assertEqual(call.kwargs["url"], "https://www.wixapis.com/site-media/v1/bulk/trash-bin/files/restore")
