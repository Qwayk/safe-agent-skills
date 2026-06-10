import io
import unittest
from contextlib import redirect_stderr

from ghost_api_tool.http import HttpClient


class _FakeResponse:
    def __init__(self, *, status_code: int, url: str, text: str):
        self.status_code = status_code
        self.url = url
        self._text = text
        self.headers = {}
        self.content = text.encode("utf-8", errors="replace")

    @property
    def text(self) -> str:
        return self._text


class HttpRedactionTests(unittest.TestCase):
    def test_http_error_redacts_sensitive_query_params(self):
        client = HttpClient(timeout_s=1.0, verbose=False, user_agent="test")
        secret = "22444f78447824223cefc48062"

        def fake_request(*, method, url, headers=None, params=None, json=None, files=None, data=None, timeout=None):  # type: ignore[no-untyped-def]
            self.assertEqual(method, "GET")
            self.assertEqual(url, "https://example.com/ghost/api/content/posts/")
            return _FakeResponse(status_code=403, url=f"{url}?key={secret}&limit=1", text="forbidden")

        client._session.request = fake_request  # type: ignore[method-assign]

        with self.assertRaises(RuntimeError) as cm:
            client.request("GET", "https://example.com/ghost/api/content/posts/", params={"key": secret, "limit": 1})

        msg = str(cm.exception)
        self.assertNotIn(secret, msg)
        self.assertIn("key=%3Credacted%3E", msg)

    def test_verbose_logs_redact_sensitive_query_params(self):
        client = HttpClient(timeout_s=1.0, verbose=True, user_agent="test")
        secret = "supersecret"

        def fake_request(*, method, url, headers=None, params=None, json=None, files=None, data=None, timeout=None):  # type: ignore[no-untyped-def]
            return _FakeResponse(status_code=500, url=f"{url}?key={secret}", text="error")

        client._session.request = fake_request  # type: ignore[method-assign]

        err = io.StringIO()
        with redirect_stderr(err):
            with self.assertRaises(RuntimeError):
                client.request("GET", "https://example.com/ghost/api/content/posts/", params={"key": secret})

        logs = err.getvalue()
        self.assertNotIn(secret, logs)
        self.assertIn("key=%3Credacted%3E", logs)

