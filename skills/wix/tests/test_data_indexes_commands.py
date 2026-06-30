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
from wix_safe_agent_cli.commands import data_indexes
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestDataIndexesCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli data-indexes",
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

    def test_parser_recognizes_data_indexes_subcommands(self) -> None:
        parser = build_parser()

        list_args = parser.parse_args(["data-indexes", "list", "--data-collection-id", "posts"])
        self.assertEqual(list_args.data_indexes_cmd, "list")
        self.assertFalse(list_args.write_capable)

        create_args = parser.parse_args(
            [
                "data-indexes",
                "create",
                "--data-collection-id",
                "posts",
                "--index-json",
                '{"name":"slug","fields":[{"path":"slug","order":"ASC"}]}',
            ]
        )
        self.assertEqual(create_args.data_indexes_cmd, "create")
        self.assertTrue(create_args.write_capable)

        drop_args = parser.parse_args(
            ["data-indexes", "drop", "--data-collection-id", "posts", "--index-name", "slug"]
        )
        self.assertEqual(drop_args.data_indexes_cmd, "drop")
        self.assertTrue(drop_args.write_capable)

    @patch("wix_safe_agent_cli.commands.data_indexes.HttpClient")
    def test_data_indexes_list_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {"indexes": [{"name": "slug", "status": "ACTIVE", "source": "USER"}]}
        )
        args = SimpleNamespace(data_collection_id="posts", limit=20, offset=4)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_indexes.cmd_data_indexes_list(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["method"], "data-indexes.list")
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(payload["request"]["path"], "/wix-data/v2/indexes")
        params = payload["request"]["params"]
        self.assertEqual(params["dataCollectionId"], "posts")
        self.assertEqual(params["paging.limit"], 20)
        self.assertEqual(params["paging.offset"], 4)
        self.assertEqual(payload["response"]["indexes"][0]["status"], "ACTIVE")

    @patch("wix_safe_agent_cli.commands.data_indexes.HttpClient")
    def test_data_indexes_create_dry_run_builds_plan_from_list_snapshot(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {"indexes": [{"name": "createdAt", "status": "ACTIVE", "source": "SYSTEM"}]}
        )
        args = SimpleNamespace(
            data_collection_id="posts",
            index_json='{"name":"slug","fields":[{"path":"slug","order":"ASC"}]}',
        )

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_indexes.cmd_data_indexes_create(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["method"], "data-indexes.create")
        self.assertTrue(payload["plan"]["state_capture"]["before_state_available"])
        self.assertEqual(payload["plan"]["request"]["body"]["dataCollectionId"], "posts")
        self.assertEqual(payload["plan"]["request"]["body"]["index"]["name"], "slug")
        self.assertEqual(mock_client.return_value.request.call_count, 1)

    @patch("wix_safe_agent_cli.commands.data_indexes.HttpClient")
    def test_data_indexes_create_apply_uses_plan_in_and_verifies_with_list(
        self, mock_client: unittest.mock.MagicMock
    ) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"indexes": [{"name": "slug", "status": "ACTIVE", "source": "USER"}]}),
            _DummyResponse({"indexes": [{"name": "slug", "status": "ACTIVE", "source": "USER"}]}),
            _DummyResponse({"index": {"name": "slug", "status": "BUILDING", "source": "USER"}}),
            _DummyResponse({"indexes": [{"name": "slug", "status": "BUILDING", "source": "USER"}]}),
        ]
        args = SimpleNamespace(
            data_collection_id="posts",
            index_json='{"name":"slug","fields":[{"path":"slug","order":"ASC"}]}',
        )

        dry_buf = io.StringIO()
        with redirect_stdout(dry_buf):
            dry_rc = data_indexes.cmd_data_indexes_create(args, self._ctx())
        dry_payload = json.loads(dry_buf.getvalue())
        plan_path = self._write_plan(dry_payload["plan"])
        try:
            apply_ctx = self._ctx(apply=True, yes=True, plan_in=plan_path)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = data_indexes.cmd_data_indexes_create(args, apply_ctx)
            payload = json.loads(buf.getvalue())

            self.assertEqual(dry_rc, 0)
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["receipt"]["verification"]["after"]["status"], "BUILDING")
            self.assertEqual(payload["receipt"]["verification"]["after"]["name"], "slug")
        finally:
            Path(plan_path).unlink()

    @patch("wix_safe_agent_cli.commands.data_indexes.HttpClient")
    def test_data_indexes_create_rejects_invalid_index_shapes(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"indexes": []})

        cases = [
            ("missing name", '{"fields":[{"path":"slug"}]}', "name"),
            ("empty fields", '{"name":"slug","fields":[]}', "fields"),
            (
                "unique with multiple fields",
                '{"name":"slug","unique":true,"fields":[{"path":"slug"},{"path":"locale"}]}',
                "unique",
            ),
            (
                "too many fields",
                '{"name":"slug","fields":[{"path":"a"},{"path":"b"},{"path":"c"},{"path":"d"}]}',
                "fields",
            ),
        ]

        for label, index_json, expected_text in cases:
            with self.subTest(label=label):
                args = SimpleNamespace(data_collection_id="posts", index_json=index_json)
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = data_indexes.cmd_data_indexes_create(args, self._ctx())
                payload = json.loads(buf.getvalue())

                self.assertEqual(rc, 1)
                self.assertFalse(payload["ok"])
                self.assertEqual(payload["error_type"], "ValidationError")
                self.assertIn(expected_text, payload["error"].lower())

    @patch("wix_safe_agent_cli.commands.data_indexes.HttpClient")
    def test_data_indexes_drop_refuses_system_generated_indexes(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {"indexes": [{"name": "createdAt", "status": "ACTIVE", "source": "SYSTEM"}]}
        )
        args = SimpleNamespace(data_collection_id="posts", index_name="createdAt")

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_indexes.cmd_data_indexes_drop(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("SYSTEM", payload["reasons"][0])

    @patch("wix_safe_agent_cli.commands.data_indexes.HttpClient")
    def test_data_indexes_drop_apply_uses_plan_in_and_verifies_with_list(
        self, mock_client: unittest.mock.MagicMock
    ) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"indexes": [{"name": "slug", "status": "ACTIVE", "source": "USER"}]}),
            _DummyResponse({"indexes": [{"name": "slug", "status": "ACTIVE", "source": "USER"}]}),
            _DummyResponse({"result": "accepted"}),
            _DummyResponse({"indexes": []}),
        ]
        args = SimpleNamespace(data_collection_id="posts", index_name="slug")

        dry_buf = io.StringIO()
        with redirect_stdout(dry_buf):
            dry_rc = data_indexes.cmd_data_indexes_drop(args, self._ctx())
        dry_payload = json.loads(dry_buf.getvalue())
        plan_path = self._write_plan(dry_payload["plan"])
        try:
            apply_ctx = self._ctx(apply=True, yes=True, plan_in=plan_path)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = data_indexes.cmd_data_indexes_drop(args, apply_ctx)
            payload = json.loads(buf.getvalue())

            self.assertEqual(dry_rc, 0)
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["receipt"]["verification"]["after"]["status"], "DROPPED")
            self.assertFalse(payload["receipt"]["verification"]["after"]["found"])
        finally:
            Path(plan_path).unlink()
