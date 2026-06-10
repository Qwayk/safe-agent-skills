from __future__ import annotations

import io
import unittest
from contextlib import redirect_stderr

import requests

from youtube_api_tool.http import HttpClient


class TestHttpRedaction(unittest.TestCase):
    def test_redact_url_query_key(self) -> None:
        url = "https://www.googleapis.com/youtube/v3/search?part=snippet&key=SECRET&maxResults=5"
        redacted = HttpClient.redact_url(url)
        self.assertIn("part=snippet", redacted)
        self.assertIn("maxResults=5", redacted)
        self.assertNotIn("SECRET", redacted)
        self.assertIn("key=%2A%2A%2AREDACTED%2A%2A%2A", redacted)

    def test_request_exception_never_leaks_query_or_auth(self) -> None:
        hc = HttpClient(timeout_s=1.0, verbose=True, user_agent="test")

        def _boom(*args, **kwargs):  # noqa: ANN001
            raise requests.RequestException(
                "boom https://www.googleapis.com/youtube/v3/search?key=SECRET",
            )

        hc._session.request = _boom  # type: ignore[method-assign]
        buf = io.StringIO()
        with redirect_stderr(buf):
            with self.assertRaises(RuntimeError) as ctx:
                hc.request(
                    "GET",
                    "https://www.googleapis.com/youtube/v3/search",
                    params={"key": "SECRET"},
                    headers={"Authorization": "Bearer SECRET"},
                )

        msg = str(ctx.exception)
        self.assertNotIn("SECRET", msg)
        stderr = buf.getvalue()
        self.assertNotIn("SECRET", stderr)

    def test_http_error_never_leaks_response_url_or_body(self) -> None:
        hc = HttpClient(timeout_s=1.0, verbose=True, user_agent="test")

        class _Resp:
            status_code = 400
            headers: dict[str, str] = {}
            content = b'{"error":"bad","key":"SECRET"}'
            text = '{"error":"bad","key":"SECRET"}'
            url = "https://www.googleapis.com/youtube/v3/search?key=SECRET"

        def _resp(*args, **kwargs):  # noqa: ANN001
            return _Resp()

        hc._session.request = _resp  # type: ignore[method-assign]
        buf = io.StringIO()
        with redirect_stderr(buf):
            with self.assertRaises(RuntimeError) as ctx:
                hc.request(
                    "GET",
                    "https://www.googleapis.com/youtube/v3/search",
                    params={"key": "SECRET"},
                    headers={"Authorization": "Bearer SECRET"},
                )

        msg = str(ctx.exception)
        self.assertIn("HTTP 400", msg)
        self.assertNotIn("SECRET", msg)
        stderr = buf.getvalue()
        self.assertNotIn("SECRET", stderr)

