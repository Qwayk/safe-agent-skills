from __future__ import annotations

import datetime as dt
import unittest

from amazon_pa_api_tool.paapi import sign_paapi_request


class TestPaApiSigning(unittest.TestCase):
    def test_signing_headers_shape(self) -> None:
        now = dt.datetime(2026, 1, 12, 12, 0, 0, tzinfo=dt.timezone.utc)
        headers = sign_paapi_request(
            access_key_id="AKIAEXAMPLE",
            secret_access_key="secret",
            region="us-east-1",
            host="webservices.amazon.com",
            target="com.amazon.paapi5.v1.ProductAdvertisingAPIv1.GetItems",
            canonical_uri="/paapi5/getitems",
            body=b"{\"x\":1}\n",
            now_utc=now,
        )
        self.assertIn("authorization", headers)
        self.assertIn("x-amz-date", headers)
        self.assertIn("x-amz-target", headers)
        self.assertTrue(headers["authorization"].startswith("AWS4-HMAC-SHA256 Credential=AKIAEXAMPLE/"))
        self.assertIn("Signature=", headers["authorization"])

