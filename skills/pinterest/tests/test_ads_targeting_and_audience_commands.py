from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace

from pinterest_api_tool.commands import ads as ads_cmd
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


class TestAdsTargetingAndAudienceCommands(unittest.TestCase):
    def _ctx(self, http: _FakeHttp) -> dict:
        return {
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

    def test_ads_targeting_analytics_endpoints_build_paths_and_params(self) -> None:
        cases = [
            (ads_cmd.cmd_ads_targeting_analytics_ad_account, "/ad_accounts/123/targeting_analytics"),
            (ads_cmd.cmd_ads_targeting_analytics_campaigns, "/ad_accounts/123/campaigns/targeting_analytics"),
            (ads_cmd.cmd_ads_targeting_analytics_ad_groups, "/ad_accounts/123/ad_groups/targeting_analytics"),
            (ads_cmd.cmd_ads_targeting_analytics_ads, "/ad_accounts/123/ads/targeting_analytics"),
        ]
        for fn, expected_path in cases:
            http = _FakeHttp([{"ok": True}])
            args = SimpleNamespace(
                ad_account_id="123",
                start_date="2026-01-01",
                end_date="2026-01-31",
                granularity="DAY",
                metric_type=["spend_in_micro_dollar", "impression"],
                param=["foo=bar"],
            )

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = fn(args, self._ctx(http))
            self.assertEqual(rc, 0)

            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["path"], expected_path)

            self.assertEqual(len(http.calls), 1)
            self.assertIn(expected_path, str(http.calls[0]["url"]))
            params = http.calls[0]["params"] or {}
            self.assertEqual(params["start_date"], "2026-01-01")
            self.assertEqual(params["end_date"], "2026-01-31")
            self.assertEqual(params["granularity"], "DAY")
            self.assertEqual(params["metric_types"], "SPEND_IN_MICRO_DOLLAR,IMPRESSION")
            self.assertEqual(params["foo"], "bar")

    def test_ads_audience_endpoints_build_paths_and_params(self) -> None:
        cases = [
            (ads_cmd.cmd_ads_audience_insights, "/ad_accounts/123/audience_insights"),
            (ads_cmd.cmd_ads_audiences, "/ad_accounts/123/insights/audiences"),
        ]
        for fn, expected_path in cases:
            http = _FakeHttp([{"ok": True}])
            args = SimpleNamespace(ad_account_id="123", param=["foo=bar"])

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = fn(args, self._ctx(http))
            self.assertEqual(rc, 0)

            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["path"], expected_path)

            self.assertEqual(len(http.calls), 1)
            self.assertIn(expected_path, str(http.calls[0]["url"]))
            params = http.calls[0]["params"] or {}
            self.assertEqual(params["foo"], "bar")

