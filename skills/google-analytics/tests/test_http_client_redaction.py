from __future__ import annotations

import io
import unittest
from contextlib import redirect_stderr

import requests

from ga4_api_tool.http import HttpClient


class _FakeResponse:
    def __init__(self, *, url: str, status_code: int, headers: dict[str, str] | None, content: bytes):
        self.url = url
        self.status_code = status_code
        self.headers = headers or {}
        self.content = content

    @property
    def text(self) -> str:  # noqa: D401
        return self.content.decode("utf-8", errors="replace")


class TestHttpClientRedaction(unittest.TestCase):
    def test_http_errors_do_not_leak_secrets_in_exception_or_verbose_logs(self) -> None:
        client = HttpClient(timeout_s=1, verbose=True, user_agent="ga4-api-tool-test")

        leak = "LEAK"
        resp = _FakeResponse(
            url=f"https://example.invalid/path?access_token={leak}&client_secret={leak}",
            status_code=400,
            headers={"Content-Type": "application/json"},
            content=b'{ "error": { "message": "bad" }, "secretValue": "LEAK" }',
        )

        stderr = io.StringIO()
        with redirect_stderr(stderr):
            client._session.request = lambda **_: resp  # type: ignore[method-assign]
            with self.assertRaises(RuntimeError) as cm:
                client.request(
                    "GET",
                    "https://example.invalid/path",
                    params={"access_token": leak, "client_secret": leak},
                )

        self.assertNotIn(leak, str(cm.exception))
        self.assertNotIn(leak, stderr.getvalue())

    def test_request_exception_messages_are_sanitized(self) -> None:
        client = HttpClient(timeout_s=1, verbose=True, user_agent="ga4-api-tool-test")
        leak = "LEAK"
        stderr = io.StringIO()

        def _raise(**_kwargs):
            raise requests.RequestException(f"boom access_token={leak}")

        with redirect_stderr(stderr):
            client._session.request = _raise  # type: ignore[method-assign]
            with self.assertRaises(RuntimeError) as cm:
                client.request("GET", "https://example.invalid/path", params={"access_token": leak})

        self.assertNotIn(leak, str(cm.exception))
        self.assertNotIn(leak, stderr.getvalue())

