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
from wix_safe_agent_cli.commands import stores_info_sections_v3
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestStoresInfoSectionsV3Commands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli stores-info-sections-v3",
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
    def _current_info_section(*, revision: int = 3) -> dict:
        return {
            "id": "section-1",
            "revision": revision,
            "title": "Shipping Details",
        }

    def _write_plan(self, plan: dict) -> str:
        handle = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json")
        json.dump(plan, handle)
        handle.close()
        return handle.name

    def test_parser_recognizes_stores_info_sections_v3_subcommands(self) -> None:
        parser = build_parser()

        get_args = parser.parse_args(["stores-info-sections-v3", "get", "--info-section-id", "section-1"])
        self.assertEqual(get_args.stores_info_sections_v3_cmd, "get")
        self.assertFalse(get_args.write_capable)

        query_args = parser.parse_args(["stores-info-sections-v3", "query"])
        self.assertEqual(query_args.stores_info_sections_v3_cmd, "query")
        self.assertFalse(query_args.write_capable)

        create_args = parser.parse_args(
            ["stores-info-sections-v3", "create", "--info-section-json", '{"title":"Shipping Details"}']
        )
        self.assertEqual(create_args.stores_info_sections_v3_cmd, "create")
        self.assertTrue(create_args.write_capable)

        update_args = parser.parse_args(
            [
                "stores-info-sections-v3",
                "update",
                "--info-section-id",
                "section-1",
                "--info-section-json",
                '{"revision":3,"title":"Updated"}',
            ]
        )
        self.assertEqual(update_args.stores_info_sections_v3_cmd, "update")
        self.assertTrue(update_args.write_capable)

        delete_args = parser.parse_args(["stores-info-sections-v3", "delete", "--info-section-id", "section-1"])
        self.assertEqual(delete_args.stores_info_sections_v3_cmd, "delete")
        self.assertTrue(delete_args.write_capable)

        write_cases = [
            (
                ["stores-info-sections-v3", "bulk-create", "--info-sections-json", '[{"title":"Shipping Details"}]'],
                "bulk-create",
            ),
            (
                [
                    "stores-info-sections-v3",
                    "bulk-delete",
                    "--info-section-ids-json",
                    '["section-1"]',
                ],
                "bulk-delete",
            ),
            (
                [
                    "stores-info-sections-v3",
                    "bulk-update",
                    "--info-sections-json",
                    '[{"id":"section-1","revision":3,"title":"Updated"}]',
                ],
                "bulk-update",
            ),
            (
                [
                    "stores-info-sections-v3",
                    "get-or-create",
                    "--info-section-json",
                    '{"uniqueName":"shipping","title":"Shipping Details"}',
                ],
                "get-or-create",
            ),
            (
                [
                    "stores-info-sections-v3",
                    "bulk-get-or-create",
                    "--info-sections-json",
                    '[{"uniqueName":"shipping","title":"Shipping Details"}]',
                ],
                "bulk-get-or-create",
            ),
        ]
        for argv, command in write_cases:
            args = parser.parse_args(argv)
            self.assertEqual(args.stores_info_sections_v3_cmd, command)
            self.assertTrue(args.write_capable)

    @patch("wix_safe_agent_cli.commands.stores_info_sections_v3.HttpClient")
    def test_get_builds_expected_request(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"infoSection": self._current_info_section()})
        args = SimpleNamespace(info_section_id="section-1")
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = stores_info_sections_v3.cmd_stores_info_sections_v3_get(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["path"], "/stores/v3/info-sections/section-1")

    @patch("wix_safe_agent_cli.commands.stores_info_sections_v3.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.stores_info_sections_v3.HttpClient")
    def test_query_wraps_query_body_and_auth_family(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "site-app-token"}, "mode": "app_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"infoSections": []})
        args = SimpleNamespace(query_json='{"filter":{"title":{"$startsWith":"Ship"}}}')
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = stores_info_sections_v3.cmd_stores_info_sections_v3_query(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["path"], "/stores/v3/info-sections/query")
        self.assertEqual(payload["request"]["body"], {"query": {"filter": {"title": {"$startsWith": "Ship"}}}})
        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "stores-info-sections-v3")

    def test_create_dry_run_builds_plan(self) -> None:
        args = SimpleNamespace(info_section_json='{"title":"Shipping Details"}')
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = stores_info_sections_v3.cmd_stores_info_sections_v3_create(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["method"], "stores-info-sections-v3.create")
        self.assertFalse(payload["plan"]["state_capture"]["before_state_available"])

    def test_update_dry_run_builds_plan(self) -> None:
        args = SimpleNamespace(
            info_section_id="section-1",
            info_section_json='{"revision":3,"title":"Updated"}',
        )
        with patch("wix_safe_agent_cli.commands.stores_info_sections_v3.HttpClient") as mock_client:
            mock_client.return_value.request.return_value = _DummyResponse({"infoSection": self._current_info_section()})
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = stores_info_sections_v3.cmd_stores_info_sections_v3_update(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["method"], "stores-info-sections-v3.update")

    def test_delete_dry_run_builds_plan(self) -> None:
        args = SimpleNamespace(info_section_id="section-1")
        with patch("wix_safe_agent_cli.commands.stores_info_sections_v3.HttpClient") as mock_client:
            mock_client.return_value.request.return_value = _DummyResponse({"infoSection": self._current_info_section()})
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = stores_info_sections_v3.cmd_stores_info_sections_v3_delete(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["method"], "stores-info-sections-v3.delete")

    def test_bulk_create_dry_run_builds_plan(self) -> None:
        args = SimpleNamespace(info_sections_json='[{"title":"Shipping Details"}]')
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = stores_info_sections_v3.cmd_stores_info_sections_v3_bulk_create(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["method"], "stores-info-sections-v3.bulk-create")
        self.assertEqual(payload["plan"]["request"]["path"], "/stores/v3/bulk/info-sections/create")
        self.assertEqual(payload["plan"]["request"]["body"], {"infoSections": [{"title": "Shipping Details"}]})

    def test_bulk_update_requires_revision(self) -> None:
        args = SimpleNamespace(info_sections_json='[{"id":"section-1","title":"Updated"}]')
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = stores_info_sections_v3.cmd_stores_info_sections_v3_bulk_update(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertIn("revision is required", payload["error"])

    def test_bulk_delete_dry_run_requires_irreversible_ack_in_plan(self) -> None:
        args = SimpleNamespace(info_section_ids_json='["section-1","section-2"]')
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = stores_info_sections_v3.cmd_stores_info_sections_v3_bulk_delete(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["method"], "stores-info-sections-v3.bulk-delete")
        self.assertEqual(payload["plan"]["risk_level"], "high")
        self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
        self.assertEqual(payload["plan"]["request"]["path"], "/stores/v3/bulk/info-sections/delete")

    def test_get_or_create_dry_run_builds_plan(self) -> None:
        args = SimpleNamespace(info_section_json='{"uniqueName":"shipping","title":"Shipping Details"}')
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = stores_info_sections_v3.cmd_stores_info_sections_v3_get_or_create(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["method"], "stores-info-sections-v3.get-or-create")
        self.assertEqual(payload["plan"]["request"]["path"], "/stores/v3/info-sections/get-or-create")

    @patch("wix_safe_agent_cli.commands.stores_info_sections_v3.HttpClient")
    def test_create_apply_requires_reviewed_plan_before_http(self, mock_client) -> None:
        args = SimpleNamespace(info_section_json='{"title":"Shipping Details"}')
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = stores_info_sections_v3.cmd_stores_info_sections_v3_create(args, self._ctx(apply=True, yes=True))
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertEqual(payload["method"], "stores-info-sections-v3.create")
        mock_client.assert_not_called()

    @patch("wix_safe_agent_cli.commands.stores_info_sections_v3.HttpClient")
    def test_update_apply_requires_reviewed_plan_before_http(self, mock_client) -> None:
        args = SimpleNamespace(
            info_section_id="section-1",
            info_section_json='{"revision":3,"title":"Updated"}',
        )
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = stores_info_sections_v3.cmd_stores_info_sections_v3_update(args, self._ctx(apply=True, yes=True))
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertEqual(payload["method"], "stores-info-sections-v3.update")
        mock_client.assert_not_called()

    @patch("wix_safe_agent_cli.commands.stores_info_sections_v3.HttpClient")
    def test_delete_apply_requires_reviewed_plan_before_http(self, mock_client) -> None:
        args = SimpleNamespace(info_section_id="section-1")
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = stores_info_sections_v3.cmd_stores_info_sections_v3_delete(
                args,
                self._ctx(apply=True, yes=True, ack_irreversible=True),
            )
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertEqual(payload["method"], "stores-info-sections-v3.delete")
        mock_client.assert_not_called()

    def test_update_rejects_body_id_mismatch(self) -> None:
        args = SimpleNamespace(
            info_section_id="section-1",
            info_section_json='{"id":"section-2","revision":3}',
        )
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = stores_info_sections_v3.cmd_stores_info_sections_v3_update(args, self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("does not match --info-section-id", payload["reasons"][0])

    @patch("wix_safe_agent_cli.commands.stores_info_sections_v3.HttpClient")
    def test_create_apply_uses_plan_in_and_verifies(self, mock_client) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"infoSection": {"id": "section-1", "title": "Shipping Details"}}),
            _DummyResponse({"infoSection": self._current_info_section()}),
        ]
        args = SimpleNamespace(info_section_json='{"title":"Shipping Details"}')
        dry_buf = io.StringIO()
        with redirect_stdout(dry_buf):
            stores_info_sections_v3.cmd_stores_info_sections_v3_create(args, self._ctx())
        plan_path = self._write_plan(json.loads(dry_buf.getvalue())["plan"])
        try:
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = stores_info_sections_v3.cmd_stores_info_sections_v3_create(
                    args,
                    self._ctx(apply=True, yes=True, plan_in=plan_path),
                )
            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["receipt"]["verification"]["after"]["id"], "section-1")
        finally:
            Path(plan_path).unlink()

    @patch("wix_safe_agent_cli.commands.stores_info_sections_v3.HttpClient")
    def test_update_apply_uses_plan_in_and_verifies(self, mock_client) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"infoSection": self._current_info_section()}),
            _DummyResponse({"infoSection": self._current_info_section()}),
            _DummyResponse({"infoSection": self._current_info_section(revision=4)}),
            _DummyResponse({"infoSection": self._current_info_section(revision=4)}),
        ]
        args = SimpleNamespace(
            info_section_id="section-1",
            info_section_json='{"revision":3,"title":"Updated"}',
        )
        dry_buf = io.StringIO()
        with redirect_stdout(dry_buf):
            stores_info_sections_v3.cmd_stores_info_sections_v3_update(args, self._ctx())
        plan_path = self._write_plan(json.loads(dry_buf.getvalue())["plan"])
        try:
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = stores_info_sections_v3.cmd_stores_info_sections_v3_update(
                    args,
                    self._ctx(apply=True, yes=True, plan_in=plan_path),
                )
            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["receipt"]["verification"]["after"]["revision"], 4)
        finally:
            Path(plan_path).unlink()

    @patch("wix_safe_agent_cli.commands.stores_info_sections_v3.HttpClient")
    def test_delete_apply_uses_plan_in_and_verifies(self, mock_client) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"infoSection": self._current_info_section()}),
            _DummyResponse({"infoSection": self._current_info_section()}),
            _DummyResponse({}),
            RuntimeError("HTTP 404 for GET https://www.wixapis.com/stores/v3/info-sections/section-1\n{}"),
        ]
        args = SimpleNamespace(info_section_id="section-1")
        dry_buf = io.StringIO()
        with redirect_stdout(dry_buf):
            stores_info_sections_v3.cmd_stores_info_sections_v3_delete(args, self._ctx())
        plan_path = self._write_plan(json.loads(dry_buf.getvalue())["plan"])
        try:
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = stores_info_sections_v3.cmd_stores_info_sections_v3_delete(
                    args,
                    self._ctx(apply=True, yes=True, ack_irreversible=True, plan_in=plan_path),
                )
            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["receipt"]["verification"]["actual_http_status"], 404)
        finally:
            Path(plan_path).unlink()
