from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import stores_locations_v3
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


class TestStoresLocationsV3Parser(unittest.TestCase):
    def test_parser_recognizes_stores_locations_v3_commands(self) -> None:
        parser = build_parser()

        get_args = parser.parse_args(["stores-locations-v3", "get", "--stores-location-id", "location-1"])
        self.assertEqual(get_args.stores_locations_v3_cmd, "get")
        self.assertFalse(get_args.write_capable)
        self.assertIs(get_args.func, stores_locations_v3.cmd_stores_locations_v3_get)

        query_args = parser.parse_args(["stores-locations-v3", "query"])
        self.assertEqual(query_args.stores_locations_v3_cmd, "query")
        self.assertFalse(query_args.write_capable)
        self.assertIs(query_args.func, stores_locations_v3.cmd_stores_locations_v3_query)


class TestStoresLocationsV3Commands(unittest.TestCase):
    def _ctx(self) -> dict:
        cfg = SimpleNamespace(
            base_url="https://www.wixapis.com",
            timeout_s=30.0,
            app_id=None,
            app_secret=None,
            instance_id=None,
            access_token="token-abc",
            has_official_app_auth=False,
        )
        return {
            "cfg": cfg,
            "env_file": "/tmp/.env",
            "verbose": False,
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
        }

    @patch("wix_safe_agent_cli.commands.stores_locations_v3.HttpClient")
    def test_get_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"storesLocation": {"id": "location-1"}})
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = stores_locations_v3.cmd_stores_locations_v3_get(
                SimpleNamespace(stores_location_id="location-1"),
                ctx,
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["method"], "stores-locations-v3.get")
        self.assertEqual(payload["request"]["path"], "/stores/v3/locations/location-1")

    @patch("wix_safe_agent_cli.commands.stores_locations_v3.HttpClient")
    def test_query_wraps_query_body(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"storesLocations": []})
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = stores_locations_v3.cmd_stores_locations_v3_query(
                SimpleNamespace(query_json='{"filter":{"isDefault":{"$eq":true}}}'),
                ctx,
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["method"], "stores-locations-v3.query")
        self.assertEqual(payload["request"]["path"], "/stores/v3/locations/query")
        self.assertEqual(payload["request"]["body"], {"query": {"filter": {"isDefault": {"$eq": True}}}})

    @patch("wix_safe_agent_cli.commands.stores_locations_v3.HttpClient")
    def test_get_rejects_empty_id_and_query_rejects_non_object(self, mock_client: unittest.mock.MagicMock) -> None:
        ctx = self._ctx()

        get_buf = io.StringIO()
        with redirect_stdout(get_buf):
            get_rc = stores_locations_v3.cmd_stores_locations_v3_get(SimpleNamespace(stores_location_id=" "), ctx)
        get_payload = json.loads(get_buf.getvalue())
        self.assertEqual(get_rc, 1)
        self.assertFalse(get_payload["ok"])
        self.assertIn("stores-location-id", get_payload["error"])

        query_buf = io.StringIO()
        with redirect_stdout(query_buf):
            query_rc = stores_locations_v3.cmd_stores_locations_v3_query(SimpleNamespace(query_json="[]"), ctx)
        query_payload = json.loads(query_buf.getvalue())
        self.assertEqual(query_rc, 1)
        self.assertFalse(query_payload["ok"])
        self.assertIn("JSON object", query_payload["error"])

        self.assertEqual(mock_client.return_value.request.call_count, 0)
