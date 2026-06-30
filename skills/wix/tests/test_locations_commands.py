from __future__ import annotations

import io
import json
import tempfile
from pathlib import Path
from types import SimpleNamespace
from contextlib import redirect_stdout
import unittest
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import locations
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


class TestLocationsCommands(unittest.TestCase):
    def _ctx(self, *, cfg_override: dict | None = None, **overrides) -> dict:
        cfg = SimpleNamespace(
            base_url="https://www.wixapis.com",
            timeout_s=30.0,
            access_token="app-token-123",
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
            "command_str": "wix-safe-agent-cli locations",
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

    def test_cli_parser_recognizes_locations_subcommands(self) -> None:
        parser = build_parser()

        list_args = parser.parse_args(["locations", "list"])
        self.assertEqual(list_args.locations_cmd, "list")
        self.assertFalse(list_args.write_capable)

        query_args = parser.parse_args(["locations", "query", "--query-json", '{"limit":1}'])
        self.assertEqual(query_args.locations_cmd, "query")
        self.assertFalse(query_args.write_capable)

        get_args = parser.parse_args(["locations", "get", "--location-id", "loc-1"])
        self.assertEqual(get_args.locations_cmd, "get")
        self.assertFalse(get_args.write_capable)

        create_args = parser.parse_args(["locations", "create", "--location-json", '{"name":"HQ"}'])
        self.assertEqual(create_args.locations_cmd, "create")
        self.assertTrue(create_args.write_capable)

        update_args = parser.parse_args(
            [
                "locations",
                "update",
                "--location-id",
                "loc-1",
                "--location-json",
                '{"name":"HQ"}',
            ]
        )
        self.assertEqual(update_args.locations_cmd, "update")
        self.assertTrue(update_args.write_capable)

        archive_args = parser.parse_args(["locations", "archive", "--location-id", "loc-1"])
        self.assertEqual(archive_args.locations_cmd, "archive")
        self.assertTrue(archive_args.write_capable)

        set_default_args = parser.parse_args(["locations", "set-default", "--location-id", "loc-1"])
        self.assertEqual(set_default_args.locations_cmd, "set-default")
        self.assertTrue(set_default_args.write_capable)

    @patch("wix_safe_agent_cli.commands.locations.HttpClient")
    def test_locations_list_builds_expected_request_and_headers(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"locations": []})

        args = SimpleNamespace(
            include_archived=True,
            authorized_only=True,
            limit=50,
            offset=4,
            sort_field="name",
            sort_order="ASC",
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = locations.cmd_locations_list(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["method"], "locations.list")
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(payload["request"]["path"], "/locations/v1/locations")
        self.assertEqual(
            payload["request"]["params"],
            {
                "includeArchived": True,
                "filterAuthorizedLocationEntities": True,
                "paging.limit": 50,
                "paging.offset": 4,
                "sort.fieldName": "name",
                "sort.order": "ASC",
            },
        )

        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["method"], "GET")
        self.assertTrue(str(call.kwargs["url"]).endswith("/locations/v1/locations"))
        self.assertEqual(call.kwargs["params"], payload["request"]["params"])
        self.assertEqual(call.kwargs["headers"]["Authorization"], "app-token-123")
        self.assertNotIn("Content-Type", call.kwargs["headers"])
        self.assertEqual(payload["auth_mode"], "app_token")

    @patch("wix_safe_agent_cli.commands.locations.HttpClient")
    def test_locations_query_builds_expected_request_and_headers(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"locations": []})

        args = SimpleNamespace(query_json='{"filter": {"status": "active"}}', authorized_only=True)
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = locations.cmd_locations_query(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["method"], "locations.query")
        self.assertEqual(payload["request"]["method"], "POST")
        self.assertEqual(payload["request"]["path"], "/locations/v1/locations/query")
        self.assertEqual(
            payload["request"]["body"],
            {"query": {"filter": {"status": "active"}}, "filterAuthorizedLocationEntities": True},
        )

        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["method"], "POST")
        self.assertTrue(str(call.kwargs["url"]).endswith("/locations/v1/locations/query"))
        self.assertEqual(
            call.kwargs["json_body"],
            {"query": {"filter": {"status": "active"}}, "filterAuthorizedLocationEntities": True},
        )
        self.assertEqual(call.kwargs["headers"]["Authorization"], "app-token-123")
        self.assertEqual(call.kwargs["headers"]["Content-Type"], "application/json")
        self.assertEqual(payload["auth_mode"], "app_token")

    @patch("wix_safe_agent_cli.commands.locations.HttpClient")
    def test_locations_get_builds_expected_request_and_headers(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"location": {"id": "loc-1"}})

        args = SimpleNamespace(location_id="loc-1")
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = locations.cmd_locations_get(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["method"], "locations.get")
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(payload["request"]["path"], "/locations/v1/locations/loc-1")
        self.assertNotIn("params", payload["request"])

        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["method"], "GET")
        self.assertTrue(str(call.kwargs["url"]).endswith("/locations/v1/locations/loc-1"))
        self.assertIsNone(call.kwargs["json_body"])
        self.assertEqual(call.kwargs["headers"]["Authorization"], "app-token-123")
        self.assertEqual(payload["auth_mode"], "app_token")

    @patch("wix_safe_agent_cli.commands.locations.HttpClient")
    def test_locations_create_dry_run_builds_plan(self, mock_client: unittest.mock.MagicMock) -> None:
        args = SimpleNamespace(location_json='{"name":"HQ","timezone":"UTC"}')
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = locations.cmd_locations_create(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["method"], "locations.create")
        self.assertIn("plan", payload)
        self.assertEqual(payload["plan"]["method"], "locations.create")
        self.assertEqual(payload["plan"]["request"]["method"], "POST")
        self.assertEqual(payload["plan"]["request"]["path"], "/locations/v1/locations")
        self.assertNotIn("receipt", payload)
        self.assertEqual(mock_client.return_value.request.call_count, 0)

    @patch("wix_safe_agent_cli.commands.locations.HttpClient")
    def test_locations_update_dry_run_builds_plan_and_preflight(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"location": {"id": "loc-1", "name": "Old HQ"}})

        args = SimpleNamespace(location_id="loc-1", location_json='{"name":"New HQ"}')
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = locations.cmd_locations_update(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["method"], "locations.update")
        self.assertEqual(payload["plan"]["request"]["method"], "PUT")
        self.assertEqual(payload["plan"]["request"]["path"], "/locations/v1/locations/loc-1")
        self.assertNotIn("receipt", payload)

        preflight = mock_client.return_value.request.call_args_list[0].kwargs
        self.assertEqual(preflight["method"], "GET")
        self.assertTrue(preflight["url"].endswith("/locations/v1/locations/loc-1"))
        self.assertEqual(mock_client.return_value.request.call_count, 1)

    @patch("wix_safe_agent_cli.commands.locations.HttpClient")
    def test_locations_archive_dry_run_builds_plan_and_preflight(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"location": {"id": "loc-1", "archived": False}})

        args = SimpleNamespace(location_id="loc-1")
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = locations.cmd_locations_archive(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["method"], "locations.archive")
        self.assertEqual(payload["plan"]["request"]["method"], "POST")
        self.assertEqual(payload["plan"]["request"]["path"], "/locations/v1/locations/loc-1/archive")
        preflight = mock_client.return_value.request.call_args_list[0].kwargs
        self.assertEqual(preflight["method"], "GET")
        self.assertTrue(preflight["url"].endswith("/locations/v1/locations/loc-1"))
        self.assertEqual(mock_client.return_value.request.call_count, 1)

    @patch("wix_safe_agent_cli.commands.locations.HttpClient")
    def test_locations_set_default_dry_run_builds_plan_and_preflight(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"location": {"id": "loc-1", "default": False}})

        args = SimpleNamespace(location_id="loc-1")
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = locations.cmd_locations_set_default(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["method"], "locations.set-default")
        self.assertEqual(payload["plan"]["request"]["method"], "POST")
        self.assertEqual(payload["plan"]["request"]["path"], "/locations/v1/locations/loc-1/set-default")
        preflight = mock_client.return_value.request.call_args_list[0].kwargs
        self.assertEqual(preflight["method"], "GET")
        self.assertTrue(preflight["url"].endswith("/locations/v1/locations/loc-1"))
        self.assertEqual(mock_client.return_value.request.call_count, 1)

    @patch("wix_safe_agent_cli.commands.locations.HttpClient")
    def test_locations_create_apply_uses_readback_for_verification(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"location": {"id": "loc-1", "name": "HQ", "timezone": "UTC"}}),
            _DummyResponse({"location": {"id": "loc-1", "name": "HQ", "timezone": "UTC"}}),
        ]
        args = SimpleNamespace(location_json='{"name":"HQ","timezone":"UTC"}')
        ctx = self._ctx(apply=True, yes=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = locations.cmd_locations_create(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertFalse(payload["dry_run"])
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["method"], "locations.create")
        self.assertTrue(payload["receipt"]["verification"]["ok"])
        calls = mock_client.return_value.request.call_args_list
        self.assertEqual(calls[0].kwargs["method"], "POST")
        self.assertEqual(calls[1].kwargs["method"], "GET")
        self.assertTrue(str(calls[0].kwargs["url"]).endswith("/locations/v1/locations"))
        self.assertTrue(str(calls[1].kwargs["url"]).endswith("/locations/v1/locations/loc-1"))

    @patch("wix_safe_agent_cli.commands.locations.HttpClient")
    def test_locations_update_apply_verifies_submitted_fields(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"location": {"id": "loc-1", "name": "Old HQ", "default": False, "phone": "111"}}),
            _DummyResponse({"location": {"id": "loc-1", "name": "Old HQ", "default": False}}),
            _DummyResponse({"location": {"id": "loc-1", "name": "New HQ", "default": False, "phone": "111"}}),
        ]
        args = SimpleNamespace(
            location_id="loc-1",
            location_json='{"name":"New HQ","phone":"111","default":false}',
        )
        ctx = self._ctx(apply=True, yes=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = locations.cmd_locations_update(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertFalse(payload["dry_run"])
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["method"], "locations.update")
        self.assertTrue(payload["receipt"]["verification"]["ok"])
        calls = mock_client.return_value.request.call_args_list
        self.assertEqual(calls[0].kwargs["method"], "GET")
        self.assertEqual(calls[1].kwargs["method"], "PUT")
        self.assertEqual(calls[2].kwargs["method"], "GET")
        self.assertEqual(calls[1].kwargs["json_body"]["location"]["phone"], "111")
        self.assertEqual(calls[1].kwargs["json_body"]["location"]["name"], "New HQ")
        self.assertTrue(calls[1].kwargs["url"].endswith("/locations/v1/locations/loc-1"))

    @patch("wix_safe_agent_cli.commands.locations.HttpClient")
    def test_locations_archive_apply_verifies_archived_flag(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"location": {"id": "loc-1", "archived": False}}),
            _DummyResponse({}),
            _DummyResponse({"location": {"id": "loc-1", "archived": True}}),
        ]
        args = SimpleNamespace(location_id="loc-1")
        ctx = self._ctx(apply=True, yes=True, ack_irreversible=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = locations.cmd_locations_archive(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertFalse(payload["dry_run"])
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["receipt"]["verification"]["ok"])
        calls = mock_client.return_value.request.call_args_list
        self.assertEqual(calls[0].kwargs["method"], "GET")
        self.assertEqual(calls[1].kwargs["method"], "POST")
        self.assertEqual(calls[2].kwargs["method"], "GET")
        self.assertTrue(calls[1].kwargs["url"].endswith("/locations/v1/locations/loc-1/archive"))
        self.assertEqual(payload["receipt"]["verification"]["checks"][0]["field"], "archived")

    @patch("wix_safe_agent_cli.commands.locations.HttpClient")
    def test_locations_archive_refuses_missing_ack_irreversible(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"location": {"id": "loc-1", "archived": False}})

        args = SimpleNamespace(location_id="loc-1")
        ctx = self._ctx(apply=True, yes=True, ack_irreversible=False)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = locations.cmd_locations_archive(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("--ack-irreversible", payload["reasons"][0])
        self.assertEqual(payload["method"], "locations.archive")
        self.assertEqual(mock_client.return_value.request.call_count, 1)

    @patch("wix_safe_agent_cli.commands.locations.HttpClient")
    def test_locations_set_default_apply_verifies_default_flag(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"location": {"id": "loc-1", "default": False}}),
            _DummyResponse({}),
            _DummyResponse({"location": {"id": "loc-1", "default": True}}),
        ]
        args = SimpleNamespace(location_id="loc-1")
        ctx = self._ctx(apply=True, yes=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = locations.cmd_locations_set_default(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertFalse(payload["dry_run"])
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["receipt"]["verification"]["ok"])
        calls = mock_client.return_value.request.call_args_list
        self.assertEqual(calls[0].kwargs["method"], "GET")
        self.assertEqual(calls[1].kwargs["method"], "POST")
        self.assertEqual(calls[2].kwargs["method"], "GET")
        self.assertTrue(calls[1].kwargs["url"].endswith("/locations/v1/locations/loc-1/set-default"))
        self.assertEqual(payload["receipt"]["verification"]["checks"][0]["field"], "default")

    @patch("wix_safe_agent_cli.commands.locations.HttpClient")
    def test_locations_update_refuses_stale_plan(self, mock_client: unittest.mock.MagicMock) -> None:
        dry_run_payload = _DummyResponse({"location": {"id": "loc-1", "name": "Old HQ"}})
        mock_client.return_value.request.return_value = dry_run_payload

        args = SimpleNamespace(location_id="loc-1", location_json='{"name":"New HQ"}')
        dry_ctx = self._ctx()
        dry_buf = io.StringIO()
        with redirect_stdout(dry_buf):
            dry_rc = locations.cmd_locations_update(args, dry_ctx)
        self.assertEqual(dry_rc, 0)
        dry_payload = json.loads(dry_buf.getvalue())

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as handle:
            json.dump(dry_payload["plan"], handle)
            plan_path = handle.name

        try:
            mock_client.return_value.request.reset_mock()
            mock_client.return_value.request.return_value = _DummyResponse({"location": {"id": "loc-1", "name": "Changed"}})
            apply_ctx = self._ctx(apply=True, yes=True, plan_in=plan_path)
            apply_buf = io.StringIO()
            with redirect_stdout(apply_buf):
                apply_rc = locations.cmd_locations_update(args, apply_ctx)
            apply_payload = json.loads(apply_buf.getvalue())

            self.assertEqual(apply_rc, 0)
            self.assertTrue(apply_payload["refused"])
            self.assertIn("changed since plan was created", apply_payload["reasons"][0])
            self.assertEqual(mock_client.return_value.request.call_count, 1)
        finally:
            Path(plan_path).unlink()

    @patch("wix_safe_agent_cli.commands.locations.HttpClient")
    def test_locations_update_refuses_location_id_mismatch(self, mock_client: unittest.mock.MagicMock) -> None:
        _ = mock_client
        args = SimpleNamespace(location_id="loc-1", location_json='{"id":"loc-2","name":"New HQ"}')
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = locations.cmd_locations_update(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("does not match", payload["error"])
