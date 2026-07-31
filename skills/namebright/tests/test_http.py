from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stderr

import requests

from namebright_safe_cli.http import HttpClient


class _FakeResponse:
    def __init__(self, status_code: int, *, payload: dict | None = None, headers: dict[str, str] | None = None, url: str = "https://api.namebright.com/rest/test"):
        self.status_code = status_code
        self.headers = headers or {}
        self.url = url
        if payload is None:
            self.content = b""
        else:
            self.content = json.dumps(payload).encode("utf-8")

    def json(self):
        return json.loads(self.content.decode("utf-8")) if self.content else None


class _FailingSession:
    def request(self, **kwargs):  # noqa: ANN003
        raise requests.Timeout("timeout value")


class _FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = 0

    def request(self, **kwargs):  # noqa: ANN003
        self.calls += 1
        if not self.responses:
            raise RuntimeError("No responses left")
        return self.responses.pop(0)


class TestHttpClient(unittest.TestCase):
    def test_no_generic_retry_default(self) -> None:
        session = _FakeSession([_FakeResponse(500)])
        client = HttpClient(timeout_s=1.0, verbose=False, user_agent="u", transport=session)
        with self.assertRaises(RuntimeError):
            client.request("GET", "https://api.namebright.com/rest/test")
        self.assertEqual(session.calls, 1)

    def test_injected_transport_uses_fake_session(self) -> None:
        payload = {"ok": True}
        session = _FakeSession([_FakeResponse(200, payload=payload)])
        client = HttpClient(timeout_s=1.0, verbose=False, user_agent="u", transport=session)
        response = client.request("GET", "https://api.namebright.com/rest/test")
        self.assertEqual(session.calls, 1)
        self.assertEqual(response.status, 200)
        self.assertEqual(response.json(), {"ok": True})

    def test_verbose_logs_omit_query_string(self) -> None:
        session = _FakeSession([_FakeResponse(200, payload={"ok": True}, url="https://api.namebright.com/rest/test?token=abc")])
        client = HttpClient(timeout_s=1.0, verbose=True, user_agent="u", transport=session)

        stderr = io.StringIO()
        with redirect_stderr(stderr):
            client.request("GET", "https://api.namebright.com/rest/test?token=abc")

        log = stderr.getvalue()
        self.assertIn("/rest/test", log)
        self.assertNotIn("?token=abc", log)

    def test_verbose_request_exception_logs_type_only(self) -> None:
        client = HttpClient(timeout_s=1.0, verbose=True, user_agent="u", transport=_FailingSession())

        stderr = io.StringIO()
        with redirect_stderr(stderr):
            with self.assertRaises(RuntimeError) as caught:
                client.request("GET", "https://api.namebright.com/rest/test?token=abc")

        log = stderr.getvalue()
        self.assertIn("EXCEPTION", log)
        self.assertIn("Timeout", log)
        self.assertNotIn("timeout value", log)
        self.assertNotIn("?token=abc", log)
        self.assertIsNone(caught.exception.__cause__)
