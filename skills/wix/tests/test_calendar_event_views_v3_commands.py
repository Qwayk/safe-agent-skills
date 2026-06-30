from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import calendar_event_views_v3
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = action, payload


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestCalendarEventViewsV3Commands(unittest.TestCase):
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

    @patch("wix_safe_agent_cli.commands.calendar_event_views_v3.HttpClient")
    @patch("wix_safe_agent_cli.commands.calendar_event_views_v3.resolve_auth_mode")
    def test_get_uses_official_events_view_endpoint(self, mock_auth: unittest.mock.MagicMock, mock_client: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"mode": "access_token", "headers": {"Authorization": "token-abc"}}
        mock_client.return_value.request.return_value = _DummyResponse({"eventsView": {"endDate": "2027-06-29T00:00:00.000Z", "futureDurationInDays": 365}})

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = calendar_event_views_v3.cmd_calendar_event_views_v3_get(SimpleNamespace(), self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["method"], "calendar-event-views-v3.get")
        self.assertEqual(payload["request"], {"method": "GET", "path": "/calendar/v3/events/view"})
        self.assertEqual(mock_client.return_value.request.call_args.kwargs["method"], "GET")
        self.assertEqual(mock_client.return_value.request.call_args.kwargs["params"], None)
        self.assertEqual(mock_client.return_value.request.call_args.kwargs["json_body"], None)

    def test_parser_exposes_get_as_read_only(self) -> None:
        args = build_parser().parse_args(["calendar-event-views-v3", "get"])

        self.assertEqual(args.calendar_event_views_v3_cmd, "get")
        self.assertFalse(args.write_capable)
        self.assertIs(args.func, calendar_event_views_v3.cmd_calendar_event_views_v3_get)


if __name__ == "__main__":
    unittest.main()
