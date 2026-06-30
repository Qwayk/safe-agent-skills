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
from wix_safe_agent_cli.commands import site_folders
from wix_safe_agent_cli.errors import ValidationError
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


class TestSiteFoldersCommands(unittest.TestCase):
    def _ctx(self, *, cfg_override: dict | None = None, **overrides) -> dict:
        cfg = SimpleNamespace(
            base_url="https://www.wixapis.com",
            timeout_s=30.0,
            access_token=None,
            api_key="acct-api-key",
            account_id="acct-001",
            app_id=None,
            app_secret=None,
            instance_id=None,
            has_official_app_auth=False,
        )
        if cfg_override:
            for key, value in cfg_override.items():
                setattr(cfg, key, value)

        ctx = {
            "cfg": cfg,
            "env_file": "/tmp/.env",
            "tool": "wix-safe-agent-cli",
            "tool_version": "0.0.0",
            "command_str": "wix-safe-agent-cli site-folders",
            "apply": False,
            "yes": False,
            "verbose": False,
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
            "plan_in": None,
            "plan_out": None,
            "receipt_out": None,
            "ack_irreversible": False,
        }
        ctx.update(overrides)
        return ctx

    @patch("wix_safe_agent_cli.commands.site_folders.HttpClient")
    def test_site_folders_query_builds_expected_request_with_account_auth_and_defaults(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"folders": [], "metadata": {"count": 0}})

        args = SimpleNamespace(
            query_json=None,
            filter_json='{"parentId":"parent-1"}',
            sort_json='[{"fieldName":"name","order":"ASC"}]',
            limit=None,
            offset=4,
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = site_folders.cmd_site_folders_query(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["method"], "site-folders.query")
        self.assertEqual(payload["auth_mode"], "account_api_key")
        request = payload["request"]
        self.assertEqual(request["method"], "POST")
        self.assertEqual(request["path"], "/site-folders/v2/folders/query")
        body = request["body"]
        self.assertEqual(body["query"]["filter"]["parentId"], "parent-1")
        self.assertEqual(body["query"]["sort"], [{"fieldName": "name", "order": "ASC"}])
        self.assertEqual(body["query"]["paging"], {"limit": 1000, "offset": 4})

        call = mock_client.return_value.request.call_args
        headers = call.kwargs["headers"]
        self.assertEqual(headers["Authorization"], "acct-api-key")
        self.assertEqual(headers["wix-account-id"], "acct-001")
        self.assertEqual(headers["Content-Type"], "application/json")

    @patch("wix_safe_agent_cli.commands.site_folders.HttpClient")
    def test_site_folders_query_rejects_oversize_limit(self, mock_client: unittest.mock.MagicMock) -> None:
        _ = mock_client
        args = SimpleNamespace(query_json=None, filter_json=None, sort_json=None, limit=1001, offset=None)
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = site_folders.cmd_site_folders_query(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")

    @patch("wix_safe_agent_cli.commands.site_folders.HttpClient")
    def test_site_folders_get_folder_by_site_includes_auth_headers(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"folder": {"id": "f1"}})

        args = SimpleNamespace(site_id="site-123")
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = site_folders.cmd_site_folders_get_folder_by_site(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["method"], "site-folders.get-folder-by-site")
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(payload["request"]["path"], "/site-folders/v2/folders/sites/site-123")

        call = mock_client.return_value.request.call_args
        headers = call.kwargs["headers"]
        self.assertEqual(headers["Authorization"], "acct-api-key")
        self.assertEqual(headers["wix-account-id"], "acct-001")

    def test_site_folders_create_requires_name(self) -> None:
        args = SimpleNamespace(name="   ", parent_id=None)
        ctx = self._ctx()
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = site_folders.cmd_site_folders_create(args, ctx)
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")

    @patch("wix_safe_agent_cli.commands.site_folders.HttpClient")
    def test_site_folders_create_returns_dry_run_without_apply_confirmation(self, mock_client: unittest.mock.MagicMock) -> None:
        _ = mock_client
        args = SimpleNamespace(name="New folder", parent_id=None)
        ctx = self._ctx(apply=True, yes=False)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = site_folders.cmd_site_folders_create(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertNotIn("receipt", payload)
        self.assertIn("plan", payload)
        self.assertEqual(payload["method"], "site-folders.create")
        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.site_folders.HttpClient")
    def test_site_folders_delete_requires_ack_for_apply(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"folders": [{"id": "f9", "name": "Old"}]})

        args = SimpleNamespace(folder_id="f9")
        ctx = self._ctx(apply=True, yes=True, ack_irreversible=False)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = site_folders.cmd_site_folders_delete(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertEqual(payload["method"], "site-folders.delete")
        calls = [call.kwargs["method"] for call in mock_client.return_value.request.call_args_list]
        self.assertNotIn("DELETE", calls)
        self.assertIn("POST", calls)

    @patch("wix_safe_agent_cli.commands.site_folders.HttpClient")
    def test_site_folders_update_refuses_stale_plan(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"folders": [{"id": "f1", "name": "Changed", "parentId": "p1"}]})
        args = SimpleNamespace(folder_id="f1", name="New")

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as handle:
            json.dump(
                {
                    "method": "site-folders.update",
                    "env_fingerprint": "https://www.wixapis.com",
                    "command": "wix-safe-agent-cli site-folders update",
                    "baseline": {
                        "env_fingerprint": "https://www.wixapis.com",
                        "selector": {"kind": "site-folder", "operation": "update", "folder_id": "f1"},
                        "before_state": {"id": "f1", "name": "Old"},
                    },
                    "selector": {"kind": "site-folder", "operation": "update", "folder_id": "f1"},
                    "request": {"method": "PATCH"},
                },
                handle,
            )
            plan_path = handle.name

        ctx = self._ctx(apply=True, yes=True, plan_in=plan_path)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = site_folders.cmd_site_folders_update(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("changed since plan", payload["reasons"][0])
        self.assertEqual(mock_client.return_value.request.call_count, 1)
        Path(plan_path).unlink()

    def test_site_folders_move_sites_requires_target_form(self) -> None:
        parser = build_parser()
        with self.assertRaises(ValidationError):
            parser.parse_args(["site-folders", "move-sites", "--site-ids-json", '["s1", "s2"]'])

        with self.assertRaises(ValidationError):
            parser.parse_args(
                [
                    "site-folders",
                    "move-sites",
                    "--site-ids-json",
                    '["s1", "s2"]',
                    "--target-folder-id",
                    "f1",
                    "--to-root",
                ]
            )

    def test_site_folders_move_folders_requires_target_form(self) -> None:
        parser = build_parser()
        with self.assertRaises(ValidationError):
            parser.parse_args(["site-folders", "move-folders", "--folder-ids-json", '["f1", "f2"]'])

        with self.assertRaises(ValidationError):
            parser.parse_args(
                [
                    "site-folders",
                    "move-folders",
                    "--folder-ids-json",
                    '["f1", "f2"]',
                    "--target-folder-id",
                    "f1",
                    "--to-root",
                ]
            )

    def test_site_folders_move_folders_rejects_too_many_folder_ids(self) -> None:
        args = SimpleNamespace(folder_ids_json=json.dumps([f"f{i}" for i in range(1001)]), target_folder_id="f-parent", to_root=False)
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = site_folders.cmd_site_folders_move_folders(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")

    def test_site_folders_move_folders_rejects_duplicate_folder_ids(self) -> None:
        args = SimpleNamespace(folder_ids_json='["f1", "f1"]', target_folder_id="f-parent", to_root=False)
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = site_folders.cmd_site_folders_move_folders(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")

    def test_site_folders_move_folders_rejects_empty_folder_id(self) -> None:
        args = SimpleNamespace(folder_ids_json='["f1", ""]', target_folder_id="f-parent", to_root=False)
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = site_folders.cmd_site_folders_move_folders(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")

    @patch("wix_safe_agent_cli.commands.site_folders.HttpClient")
    def test_site_folders_move_folders_dry_run_plans_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"folders": [{"id": "f1", "parentId": "root"}]})

        args = SimpleNamespace(folder_ids_json='["f1"]', target_folder_id="f2", to_root=False)
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = site_folders.cmd_site_folders_move_folders(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["method"], "site-folders.move-folders")
        plan = payload["plan"]
        self.assertEqual(plan["method"], "site-folders.move-folders")
        self.assertEqual(plan["request"]["method"], "PATCH")
        self.assertEqual(plan["request"]["path"], "/site-folders/v2/folders/bulk/move")
        self.assertEqual(plan["request"]["body"], {"folderIds": ["f1"], "targetFolderId": "f2"})
        mock_client.return_value.request.assert_called()

    @patch("wix_safe_agent_cli.commands.site_folders.HttpClient")
    def test_site_folders_move_folders_refuses_missing_folder_before_apply(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"folders": []})

        args = SimpleNamespace(folder_ids_json='["f-missing"]', target_folder_id="f-parent", to_root=False)
        ctx = self._ctx(apply=True, yes=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = site_folders.cmd_site_folders_move_folders(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertEqual(payload["method"], "site-folders.move-folders")
        self.assertIn("does not exist", payload["reasons"][0])

    @patch("wix_safe_agent_cli.commands.site_folders.HttpClient")
    def test_site_folders_move_folders_apply_sends_expected_request_and_headers(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"folders": [{"id": "f1", "parentId": "root"}]}),
            _DummyResponse({"folders": [{"id": "f2", "parentId": "root"}]}),
            _DummyResponse({"folders": [{"id": "f1", "parentId": "f3"}, {"id": "f2", "parentId": "f3"}]}),
            _DummyResponse({"folders": [{"id": "f1", "parentId": "f3"}]}),
            _DummyResponse({"folders": [{"id": "f2", "parentId": "f3"}]}),
        ]

        args = SimpleNamespace(folder_ids_json='["f1", "f2"]', target_folder_id="f3", to_root=False)
        ctx = self._ctx(apply=True, yes=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = site_folders.cmd_site_folders_move_folders(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertFalse(payload["dry_run"])
        self.assertEqual(payload["method"], "site-folders.move-folders")

        patch_calls = [
            call
            for call in mock_client.return_value.request.call_args_list
            if call.kwargs.get("method") == "PATCH"
            and str(call.kwargs.get("url", "")).endswith("/site-folders/v2/folders/bulk/move")
        ]
        self.assertEqual(len(patch_calls), 1)
        patch_call = patch_calls[0]
        self.assertEqual(patch_call.kwargs["json_body"], {"folderIds": ["f1", "f2"], "targetFolderId": "f3"})
        patch_headers = patch_call.kwargs["headers"]
        self.assertEqual(patch_headers["Authorization"], "acct-api-key")
        self.assertEqual(patch_headers["wix-account-id"], "acct-001")
        self.assertEqual(patch_headers["Content-Type"], "application/json")
