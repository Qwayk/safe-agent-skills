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
    def run_query(self, count, limit=None, fail=False):
        env = {"GOOGLE_ADS_CLIENT_ID": "test", "GOOGLE_ADS_CLIENT_SECRET": "test",
               "GOOGLE_ADS_REFRESH_TOKEN": "test"}
        args = ["--output", "json", "gaql", "--customer-id", "123",
                "--query", "SELECT campaign.id FROM campaign"]
        if limit is not None:
            args += ["--limit", str(limit)]
        with patch.dict(os.environ, env), patch(
            "google_ads_api_tool.google_ads_client.GoogleAdsClient.load_from_dict"
        ) as factory:
            factory.return_value = _FakeClient([_FakeRow(i) for i in range(count)])
            buf = io.StringIO()
            with patch("google_ads_api_tool.commands.gaql.protobuf_to_dict", side_effect=lambda r: r._pb):
                with redirect_stdout(buf):
                    if fail:
                        with patch.object(_FakeGoogleAdsService, "search", side_effect=RuntimeError("read failed")):
                            rc = main(args)
                    else:
                        rc = main(args)
        return rc, json.loads(buf.getvalue())

    def test_completeness(self):
        for count, limit, returned, limited in [(10, None, 10, False), (3, 3, 3, False),
                                               (10, 3, 3, True), (0, None, 0, False),
                                               (2, 3, 2, False)]:
            with self.subTest(count=count, limit=limit):
                rc, payload = self.run_query(count, limit)
                self.assertEqual(rc, 0)
                self.assertTrue(payload["ok"])
                self.assertEqual(payload["meta"]["row_count"], returned)
                self.assertEqual(payload["meta"]["limited"], limited)
                self.assertTrue(payload["meta"]["page_size_ignored"])
                self.assertEqual(payload["rows"], [{"row": i} for i in range(returned)])

    def test_failure_is_not_an_empty_success(self):
        rc, payload = self.run_query(0, fail=True)
        self.assertNotEqual(rc, 0)
        self.assertFalse(payload["ok"])

    def test_failure_during_limit_lookahead_is_not_complete(self):
        def fail_after_rows(*args, **kwargs):
            yield _FakeRow(0)
            yield _FakeRow(1)
            raise RuntimeError("later page failed")
        with patch.object(_FakeGoogleAdsService, "search", side_effect=fail_after_rows):
            rc, payload = self.run_query(2, limit=2)
        self.assertNotEqual(rc, 0)
        self.assertFalse(payload["ok"])
