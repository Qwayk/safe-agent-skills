from __future__ import annotations

import unittest
from unittest.mock import patch

from qwayk_woocommerce_safe_agent_cli.client import WooCommerceClient
from qwayk_woocommerce_safe_agent_cli.config import Config


class _FakeResponse:
    def __init__(self) -> None:
        self.status_code = 401
        self.url = (
            "https://shop.example.com/wp-json/wc/v3/orders"
            "?consumer_key=ck_secret&consumer_secret=cs_secret"
        )
        self.text = "bad key ck_secret and secret cs_secret"
        self.content = self.text.encode("utf-8")
        self.headers: dict[str, str] = {}


class TestAuthRedaction(unittest.TestCase):
    def test_query_string_auth_error_redacts_secrets(self) -> None:
        cfg = Config(
            store_url="https://shop.example.com",
            api_base_url="https://shop.example.com/wp-json/wc/v3",
            consumer_key="ck_secret",
            consumer_secret="cs_secret",
            timeout_s=30.0,
            query_string_auth=True,
            verify_ssl=True,
        )
        client = WooCommerceClient(
            cfg=cfg,
            timeout_s=30.0,
            verbose=False,
            user_agent="test/0.0.0",
        )
        with patch("requests.Session.request", return_value=_FakeResponse()):
            with self.assertRaises(RuntimeError) as ctx:
                client.request_json("GET", "/orders", params={"per_page": 1}, auth_required=True)
        message = str(ctx.exception)
        self.assertNotIn("ck_secret", message)
        self.assertNotIn("cs_secret", message)
        self.assertIn("***REDACTED***", message)
