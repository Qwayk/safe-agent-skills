from __future__ import annotations

import io
import json
import os
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from google_ads_api_tool.cli import main


class _FakeGoogleAdsService:
    def __init__(self, rows: list[object]):
        self._rows = rows

    def search(self, request=None, *, customer_id=None, query=None, **kwargs):  # noqa: ARG002
        _ = (request, customer_id, query, kwargs)
        for r in self._rows:
            yield r


class _FakeSearchGoogleAdsRequest:
    def __init__(self) -> None:
        self.customer_id = ""
        self.query = ""
        self.page_size = 0


class _FakeClient:
    def __init__(self, rows: list[object]):
        self._rows = rows

    def get_type(self, name: str):
        if name == "SearchGoogleAdsRequest":
            return _FakeSearchGoogleAdsRequest()
        raise KeyError(name)

    def get_service(self, name: str):
        if name == "GoogleAdsService":
            return _FakeGoogleAdsService(self._rows)
        raise KeyError(name)


class _FakeRow:
    def __init__(self, i: int):
        self._pb = {"row": i}


class TestGaqlLimit(unittest.TestCase):
    def test_gaql_limit_truncates(self) -> None:
        os.environ["GOOGLE_ADS_DEVELOPER_TOKEN"] = "DEV_TOKEN_123"
        os.environ["GOOGLE_ADS_CLIENT_ID"] = "CLIENT_ID_123"
        os.environ["GOOGLE_ADS_CLIENT_SECRET"] = "CLIENT_SECRET_123"
        os.environ["GOOGLE_ADS_REFRESH_TOKEN"] = "REFRESH_TOKEN_123"
        try:
            rows = [_FakeRow(i) for i in range(10)]
            with patch("google_ads_api_tool.google_ads_client.GoogleAdsClient.load_from_dict") as m:
                m.return_value = _FakeClient(rows)
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "gaql",
                            "--customer-id",
                            "123",
                            "--query",
                            "SELECT campaign.id FROM campaign",
                            "--limit",
                            "3",
                            "--page-size",
                            "1000",
                        ]
                    )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["meta"]["row_count"], 3)
            self.assertTrue(payload["meta"]["limited"])
        finally:
            for k in [
                "GOOGLE_ADS_DEVELOPER_TOKEN",
                "GOOGLE_ADS_CLIENT_ID",
                "GOOGLE_ADS_CLIENT_SECRET",
                "GOOGLE_ADS_REFRESH_TOKEN",
            ]:
                os.environ.pop(k, None)
