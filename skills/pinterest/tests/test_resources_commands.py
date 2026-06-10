from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace

from pinterest_api_tool.commands import resources as resources_cmd
from pinterest_api_tool.config import Config
from pinterest_api_tool.http import HttpResponse
from pinterest_api_tool.output import Output


class _FakeHttp:
    def __init__(self, responses: list[dict]) -> None:
        self._responses = list(responses)
        self.calls: list[dict[str, object]] = []

    def request(self, method: str, url: str, **kwargs):  # noqa: ANN001
        self.calls.append({"method": method, "url": url, "params": kwargs.get("params")})
        if not self._responses:
            raise AssertionError("No more fake responses available")
        data = self._responses.pop(0)
        return HttpResponse(status=200, headers={}, body=json.dumps(data).encode("utf-8"), url=url)


class _Audit:
    def write(self, event: str, payload):  # noqa: ANN001
        _ = event, payload


class TestResourcesCommands(unittest.TestCase):
    def test_resources_endpoints_build_paths_and_params(self) -> None:
        cases = [
            (resources_cmd.cmd_resources_ad_account_countries, "/resources/ad_account_countries", SimpleNamespace(param=["foo=bar"])),
            (resources_cmd.cmd_resources_delivery_metrics, "/resources/delivery_metrics", SimpleNamespace(param=None)),
            (resources_cmd.cmd_resources_metrics_ready_state, "/resources/metrics_ready_state", SimpleNamespace(param=None)),
            (
                resources_cmd.cmd_resources_targeting,
                "/resources/targeting/LOCATION",
                SimpleNamespace(targeting_type="LOCATION", param=["foo=bar"]),
            ),
            (
                resources_cmd.cmd_resources_targeting_interest,
                "/resources/targeting/interests/123",
                SimpleNamespace(interest_id="123", param=["foo=bar"]),
            ),
        ]

        for fn, expected_path, args in cases:
            http = _FakeHttp([{"ok": True}])
            ctx = {
                "cfg": Config(
                    base_url="https://api.pinterest.com/v5",
                    access_token="X",
                    app_id=None,
                    app_secret=None,
                    refresh_token=None,
                    timeout_s=30,
                ),
                "http": http,
                "env_file": "/tmp/.env",
                "out": Output(mode="json"),
                "audit": _Audit(),
            }

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = fn(args, ctx)
            self.assertEqual(rc, 0)

            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["path"], expected_path)

            self.assertEqual(len(http.calls), 1)
            self.assertEqual(http.calls[0]["method"], "GET")
            self.assertIn(expected_path, str(http.calls[0]["url"]))
            params = http.calls[0]["params"] or {}
            if expected_path.endswith("/delivery_metrics") or expected_path.endswith("/metrics_ready_state"):
                self.assertEqual(params, {})
            else:
                self.assertEqual(params["foo"], "bar")

