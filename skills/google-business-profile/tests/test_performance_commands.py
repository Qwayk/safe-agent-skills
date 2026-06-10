from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from google_business_profile_safe_agent_cli.api_client import PERFORMANCE_HOST
from google_business_profile_safe_agent_cli.cli import main
from google_business_profile_safe_agent_cli.http import HttpResponse


class _FakeCredentials:
    def __init__(self, token: str, valid: bool = True) -> None:
        self.token = token
        self.valid = valid

    def refresh(self, request: object) -> None:  # noqa: ANN001
        self.valid = True


def _make_request_file(root: Path) -> None:
    root.joinpath(".state").mkdir(parents=True, exist_ok=True)
    token = root / ".state" / "oauth_credentials.json"
    token.write_text("{}", encoding="utf-8")


class TestPerformanceCommands(unittest.TestCase):
    def setUp(self) -> None:
        self._env_text = "GBP_TIMEOUT_S=30\n"

    def test_fetch_multi_daily_metrics_time_series_calls_api(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            def fake_request(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict[str, object] | None = None,
                json_body: dict[str, object] | None = None,
                data: dict[str, object] | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                return HttpResponse(
                    status=200,
                    headers={},
                    body=json.dumps(
                        {
                            "multiDailyMetricTimeSeries": [
                                {
                                    "dailyMetricTimeSeries": [
                                        {
                                            "dailyMetric": "DAILY_ORDERS",
                                            "timeSeries": {
                                                "datedValues": [
                                                    {
                                                        "date": {"year": 2025, "month": 1, "day": 1},
                                                        "value": "8",
                                                    }
                                                ]
                                            },
                                        }
                                    ],
                                }
                            ]
                        }
                    ).encode("utf-8"),
                    url=url,
                )

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request), redirect_stdout(
                buf
            ):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "performance",
                        "locations",
                        "fetch-multi-daily-metrics-time-series",
                        "--location",
                        "locations/123",
                        "--daily-metrics",
                        "DAILY_ORDERS",
                        "--daily-range-start-year",
                        "2025",
                        "--daily-range-start-month",
                        "1",
                        "--daily-range-start-day",
                        "1",
                        "--daily-range-end-year",
                        "2025",
                        "--daily-range-end-month",
                        "1",
                        "--daily-range-end-day",
                        "31"
                    ]
                )

                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertEqual(payload["operation"], "performance.locations.fetch-multi-daily-metrics-time-series")
                self.assertEqual(payload["request"]["method"], "GET")
                self.assertEqual(payload["request"]["path"], "v1/locations/123:fetchMultiDailyMetricsTimeSeries")
            self.assertEqual(payload["request"]["params"].get("dailyMetrics"), ["DAILY_ORDERS"])
            self.assertEqual(payload["request"]["params"].get("dailyRange.startDate.year"), 2025)
            self.assertEqual(payload["request"]["host"], PERFORMANCE_HOST)
            self.assertNotIn("pageSize", payload["request"]["params"])
            self.assertNotIn("pageToken", payload["request"]["params"])
            self.assertNotIn("TOKEN_SHOULD_NOT_LEAK", buf.getvalue())

    def test_get_daily_metrics_time_series_calls_api(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            def fake_request(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict[str, object] | None = None,
                json_body: dict[str, object] | None = None,
                data: dict[str, object] | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                return HttpResponse(
                    status=200,
                    headers={},
                    body=json.dumps(
                        {
                            "timeSeries": {
                                "datedValues": [
                                    {"date": {"year": 2025, "month": 1, "day": 1}, "value": "8"}
                                ]
                            },
                        }
                    ).encode("utf-8"),
                    url=url,
                )

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request), redirect_stdout(
                buf
            ):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "performance",
                        "locations",
                        "get-daily-metrics-time-series",
                        "--name",
                        "locations/123",
                        "--daily-metric",
                        "DAILY_ORDERS",
                        "--daily-range-start-year",
                        "2025",
                        "--daily-range-start-month",
                        "1",
                        "--daily-range-start-day",
                        "1",
                        "--daily-range-end-year",
                        "2025",
                        "--daily-range-end-month",
                        "1",
                        "--daily-range-end-day",
                        "31"
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["operation"], "performance.locations.get-daily-metrics-time-series")
            self.assertEqual(payload["request"]["path"], "v1/locations/123:getDailyMetricsTimeSeries")
            self.assertEqual(payload["request"]["params"].get("dailyMetric"), "DAILY_ORDERS")
            self.assertNotIn("dailySubEntityType", payload["request"]["params"])
            self.assertEqual(payload["request"]["host"], PERFORMANCE_HOST)

    def test_search_keywords_impressions_monthly_list_calls_api(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            def fake_request(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict[str, object] | None = None,
                json_body: dict[str, object] | None = None,
                data: dict[str, object] | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                return HttpResponse(
                    status=200,
                    headers={},
                    body=json.dumps(
                        {
                            "searchKeywordsCounts": [
                                {
                                    "searchKeyword": "coffee",
                                    "insightsValue": {"value": "123"},
                                }
                            ]
                        }
                    ).encode("utf-8"),
                    url=url,
                )

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request), redirect_stdout(
                buf
            ):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "performance",
                        "locations",
                        "search-keywords",
                        "impressions",
                        "monthly",
                        "list",
                        "--parent",
                        "locations/123",
                        "--monthly-range-start-year",
                        "2025",
                        "--monthly-range-start-month",
                        "1",
                        "--monthly-range-end-year",
                        "2025",
                        "--monthly-range-end-month",
                        "3",
                        "--page-size",
                        "20",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["operation"], "performance.locations.search-keywords.impressions.monthly.list")
            self.assertEqual(
                payload["request"]["path"],
                "v1/locations/123/searchkeywords/impressions/monthly",
            )
            self.assertNotIn("filter", payload["request"]["params"])
            self.assertEqual(payload["request"]["params"].get("pageSize"), 20)
            self.assertEqual(payload["request"]["host"], PERFORMANCE_HOST)
