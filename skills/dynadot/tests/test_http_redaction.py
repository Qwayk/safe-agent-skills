from __future__ import annotations

import unittest

import requests

from dynadot_api_tool.http import HttpClient


class TestHttpRedaction(unittest.TestCase):
    def test_redacts_key_query_param(self) -> None:
        url = "https://api.dynadot.com/api3.json?key=SECRET&command=is_processing"
        redacted = HttpClient._redact_url(url)  # noqa: SLF001
        self.assertIn("key=%2A%2A%2AREDACTED%2A%2A%2A", redacted)
        self.assertNotIn("SECRET", redacted)

    def test_redacts_key_in_request_exception(self) -> None:
        hc = HttpClient(timeout_s=0.1, verbose=False, user_agent="dynadot-api-tool-test")

        def _raise(*_args, **_kwargs):
            raise requests.RequestException("boom: https://api.dynadot.com/api3.json?key=SECRET&command=account_info")

        hc._session.request = _raise  # type: ignore[method-assign]  # noqa: SLF001

        with self.assertRaises(RuntimeError) as cm:
            hc.request("GET", "https://api.dynadot.com/api3.json", params={"key": "SECRET", "command": "account_info"})

        msg = str(cm.exception)
        self.assertNotIn("SECRET", msg)
        self.assertIn("***REDACTED***", msg)

    def test_redacts_key_in_http_error_body(self) -> None:
        hc = HttpClient(timeout_s=0.1, verbose=False, user_agent="dynadot-api-tool-test")

        class _Resp:
            status_code = 500
            url = "https://api.dynadot.com/api3.json?key=SECRET&command=tld_price"
            text = "error calling https://api.dynadot.com/api3.json?key=SECRET&command=tld_price (key%3DSECRET)"

        def _return(*_args, **_kwargs):
            return _Resp()

        hc._session.request = _return  # type: ignore[method-assign]  # noqa: SLF001

        with self.assertRaises(RuntimeError) as cm:
            hc.request("GET", "https://api.dynadot.com/api3.json", params={"key": "SECRET", "command": "tld_price"})

        msg = str(cm.exception)
        self.assertNotIn("SECRET", msg)
        self.assertIn("***REDACTED***", msg)
