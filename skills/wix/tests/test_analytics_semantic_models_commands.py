from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import analytics_semantic_models
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


class TestAnalyticsSemanticModelsParser(unittest.TestCase):
    def test_parser_recognizes_analytics_semantic_models_commands(self) -> None:
        parser = build_parser()

        list_args = parser.parse_args(["analytics-semantic-models", "list"])
        self.assertEqual(list_args.analytics_semantic_models_cmd, "list")
        self.assertFalse(list_args.write_capable)
        self.assertIs(list_args.func, analytics_semantic_models.cmd_analytics_semantic_models_list)

        get_args = parser.parse_args(["analytics-semantic-models", "get", "--semantic-model-id", "sm-1"])
        self.assertEqual(get_args.analytics_semantic_models_cmd, "get")
        self.assertFalse(get_args.write_capable)
        self.assertIs(get_args.func, analytics_semantic_models.cmd_analytics_semantic_models_get)

        query_args = parser.parse_args(
            ["analytics-semantic-models", "query", "--query-json", '{"interval":{"from":"2026-06-01","to":"2026-06-02"}}']
        )
        self.assertEqual(query_args.analytics_semantic_models_cmd, "query")
        self.assertFalse(query_args.write_capable)
        self.assertIs(query_args.func, analytics_semantic_models.cmd_analytics_semantic_models_query)


class TestAnalyticsSemanticModelsCommands(unittest.TestCase):
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

    @patch("wix_safe_agent_cli.commands.analytics_semantic_models.HttpClient")
    def test_list_builds_expected_request_and_headers(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"semanticModels": []})
        args = SimpleNamespace()
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = analytics_semantic_models.cmd_analytics_semantic_models_list(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["method"], "analytics-semantic-models.list")
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(payload["request"]["path"], "/analytics/semantic-model/v3/semantic-models")
        self.assertNotIn("params", payload["request"])
        self.assertEqual(payload["response"], {"semanticModels": []})
        self.assertEqual(payload["auth_mode"], "app_token")

        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["method"], "GET")
        self.assertTrue(str(call.kwargs["url"]).endswith("/analytics/semantic-model/v3/semantic-models"))
        self.assertEqual(call.kwargs["headers"]["Authorization"], "token-abc")
        self.assertNotIn("Content-Type", call.kwargs["headers"])

    @patch("wix_safe_agent_cli.commands.analytics_semantic_models.HttpClient")
    def test_get_rejects_empty_semantic_model_id(self, mock_client: unittest.mock.MagicMock) -> None:
        args = SimpleNamespace(semantic_model_id="  ")
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = analytics_semantic_models.cmd_analytics_semantic_models_get(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("semantic-model-id", payload["error"])
        self.assertEqual(mock_client.return_value.request.call_count, 0)

    @patch("wix_safe_agent_cli.commands.analytics_semantic_models.HttpClient")
    def test_query_rejects_empty_and_non_object_query_json(self, mock_client: unittest.mock.MagicMock) -> None:
        ctx = self._ctx()

        empty_args = SimpleNamespace(query_json="{}")
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc_empty = analytics_semantic_models.cmd_analytics_semantic_models_query(empty_args, ctx)
        empty_payload = json.loads(buf.getvalue())

        self.assertEqual(rc_empty, 1)
        self.assertFalse(empty_payload["ok"])
        self.assertIn("must be a JSON object", empty_payload["error"])

        array_args = SimpleNamespace(query_json="[]")
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc_array = analytics_semantic_models.cmd_analytics_semantic_models_query(array_args, ctx)
        array_payload = json.loads(buf.getvalue())

        self.assertEqual(rc_array, 1)
        self.assertFalse(array_payload["ok"])
        self.assertIn("must be a JSON object", array_payload["error"])
        self.assertEqual(mock_client.return_value.request.call_count, 0)

    @patch("wix_safe_agent_cli.commands.analytics_semantic_models.HttpClient")
    def test_query_rejects_missing_interval(self, mock_client: unittest.mock.MagicMock) -> None:
        args = SimpleNamespace(query_json='{"paging":{"limit":10}}')
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = analytics_semantic_models.cmd_analytics_semantic_models_query(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertIn("interval object", payload["error"])
        self.assertEqual(mock_client.return_value.request.call_count, 0)

    @patch("wix_safe_agent_cli.commands.analytics_semantic_models.HttpClient")
    def test_query_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"rows": []})
        args = SimpleNamespace(query_json='{"interval":{"from":"2026-06-01","to":"2026-06-02"},"formattingEnabled":true}')
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = analytics_semantic_models.cmd_analytics_semantic_models_query(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["method"], "analytics-semantic-models.query")
        self.assertEqual(payload["request"]["method"], "POST")
        self.assertEqual(payload["request"]["path"], "/analytics/semantic-model/v3/semantic-models/query-data")
        self.assertEqual(
            payload["request"]["body"],
            {"interval": {"from": "2026-06-01", "to": "2026-06-02"}, "formattingEnabled": True},
        )
        self.assertEqual(payload["response"], {"rows": []})

        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["method"], "POST")
        self.assertTrue(str(call.kwargs["url"]).endswith("/analytics/semantic-model/v3/semantic-models/query-data"))
        self.assertEqual(call.kwargs["json_body"], payload["request"]["body"])
        self.assertEqual(call.kwargs["headers"]["Authorization"], "token-abc")
        self.assertEqual(call.kwargs["headers"]["Content-Type"], "application/json")
