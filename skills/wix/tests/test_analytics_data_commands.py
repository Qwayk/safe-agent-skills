from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from datetime import date, timedelta
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import analytics_data
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


class TestAnalyticsDataParser(unittest.TestCase):
    def test_parser_recognizes_analytics_data_get_and_is_read_only(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "analytics-data",
                "get",
                "--start-date",
                "2024-01-01",
                "--end-date",
                "2024-01-04",
                "--measurement-types-json",
                '["TOTAL_SESSIONS","TOTAL_ORDERS"]',
            ]
        )

        self.assertEqual(args.analytics_data_cmd, "get")
        self.assertFalse(args.write_capable)
        self.assertIs(args.func, analytics_data.cmd_analytics_data_get)


class TestAnalyticsDataCommands(unittest.TestCase):
    @staticmethod
    def _recent_dates() -> tuple[str, str]:
        end = date.today() - timedelta(days=1)
        start = end - timedelta(days=3)
        return start.isoformat(), end.isoformat()

    def _ctx(self, *, cfg_override: dict | None = None, verbose: bool = False) -> dict:
        cfg = SimpleNamespace(
            base_url="https://www.wixapis.com",
            timeout_s=30.0,
            app_id=None,
            app_secret=None,
            instance_id=None,
            access_token="token-abc",
            has_official_app_auth=False,
        )
        if cfg_override:
            for key, value in cfg_override.items():
                setattr(cfg, key, value)
        return {
            "cfg": cfg,
            "env_file": "/tmp/.env",
            "verbose": verbose,
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
        }

    @patch("wix_safe_agent_cli.commands.analytics_data.HttpClient")
    def test_analytics_data_get_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {"data": [{"type": "TOTAL_SESSIONS", "total": 12}]}
        )
        start_date, end_date = self._recent_dates()

        args = SimpleNamespace(
            start_date=start_date,
            end_date=end_date,
            measurement_types_json='["TOTAL_SESSIONS", "TOTAL_ORDERS"]',
            time_zone="America/New_York",
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = analytics_data.cmd_analytics_data_get(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["method"], "analytics-data.get")
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(payload["request"]["path"], "/analytics/v2/site-analytics/data")
        self.assertEqual(payload["request"]["params"]["dateRange.startDate"], start_date)
        self.assertEqual(payload["request"]["params"]["dateRange.endDate"], end_date)
        self.assertEqual(payload["request"]["params"]["measurementTypes"], ["TOTAL_SESSIONS", "TOTAL_ORDERS"])
        self.assertEqual(payload["request"]["params"]["timeZone"], "America/New_York")
        self.assertEqual(payload["response"]["data"][0]["type"], "TOTAL_SESSIONS")

        http_call = mock_client.return_value.request.call_args
        headers = http_call.kwargs["headers"]
        self.assertEqual(headers["Authorization"], "token-abc")

    def test_analytics_data_get_rejects_empty_measurement_types(self) -> None:
        start_date, end_date = self._recent_dates()
        args = SimpleNamespace(
            start_date=start_date,
            end_date=end_date,
            measurement_types_json="[]",
            time_zone=None,
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = analytics_data.cmd_analytics_data_get(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertIn("at least one measurement type", payload["error"])

    def test_analytics_data_get_rejects_invalid_dates(self) -> None:
        _, end_date = self._recent_dates()
        args = SimpleNamespace(
            start_date="2024-13-01",
            end_date=end_date,
            measurement_types_json='["TOTAL_SESSIONS"]',
            time_zone=None,
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = analytics_data.cmd_analytics_data_get(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertIn("YYYY-MM-DD", payload["error"])

    def test_analytics_data_get_rejects_end_before_start(self) -> None:
        start_date, _ = self._recent_dates()
        earlier_end_date = (date.fromisoformat(start_date) - timedelta(days=1)).isoformat()
        args = SimpleNamespace(
            start_date=start_date,
            end_date=earlier_end_date,
            measurement_types_json='["TOTAL_SESSIONS"]',
            time_zone=None,
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = analytics_data.cmd_analytics_data_get(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertIn("--end-date must be the same as or after --start-date", payload["error"])

    def test_analytics_data_get_rejects_invalid_measurement_type(self) -> None:
        start_date, end_date = self._recent_dates()
        args = SimpleNamespace(
            start_date=start_date,
            end_date=end_date,
            measurement_types_json='["TOTAL_SESSIONS", "NOT_A_MEASUREMENT"]',
            time_zone=None,
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = analytics_data.cmd_analytics_data_get(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertIn("Invalid measurement type", payload["error"])

    def test_analytics_data_get_reports_success_response(self) -> None:
        start_date, end_date = self._recent_dates()
        args = SimpleNamespace(
            start_date=start_date,
            end_date=end_date,
            measurement_types_json='["TOTAL_FORMS_SUBMITTED"]',
            time_zone=None,
        )
        expected_payload = {"data": [{"type": "TOTAL_FORMS_SUBMITTED", "total": 4}]}

        class _StubResponse:
            def json(self) -> dict:
                return expected_payload

        ctx = self._ctx()
        with patch("wix_safe_agent_cli.commands.analytics_data.HttpClient") as mock_client:
            mock_client.return_value.request.return_value = _StubResponse()
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = analytics_data.cmd_analytics_data_get(args, ctx)
            payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["response"], expected_payload)
        self.assertIn("measurementTypes", payload["request"]["params"])
