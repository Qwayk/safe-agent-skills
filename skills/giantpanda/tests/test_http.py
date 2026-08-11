from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stderr
from types import SimpleNamespace
from unittest.mock import patch

from giantpanda_api_tool.http import HttpClient, HttpError


class TestHttpClient(unittest.TestCase):
    def test_request_redacts_auth_in_verbose_output(self) -> None:
        client = HttpClient(timeout_s=5, verbose=True)

        fake = SimpleNamespace(
            status_code=200,
            content=json.dumps({"ok": True}).encode("utf-8"),
            url="https://account.giantpanda.com/api/v1/domains/stats/",
            headers={"Content-Type": "application/json"},
            text="{}",
        )

        with patch("giantpanda_api_tool.http.requests.Session.request", return_value=fake):
            out = io.StringIO()
            with redirect_stderr(out):
                resp = client.request(
                    "GET",
                    "https://account.giantpanda.com/api/v1/domains/stats/",
                    headers={"Authorization": "Token secret"},
                )
            self.assertEqual(resp.status, 200)
            self.assertNotIn("Token secret", out.getvalue())
            self.assertIn("***REDACTED***", out.getvalue())

    def test_request_refuses_redirect_without_following_it(self) -> None:
        client = HttpClient(timeout_s=5, verbose=False)
        redirect = SimpleNamespace(
            status_code=302,
            content=b"",
            url="https://account.giantpanda.com/accounts/login/",
            headers={"Location": "https://other.example.invalid/collect"},
        )

        with patch(
            "giantpanda_api_tool.http.requests.Session.request",
            return_value=redirect,
        ) as request:
            with self.assertRaises(HttpError):
                client.request(
                    "GET",
                    "https://account.giantpanda.com/api/v1/domains/stats/",
                    headers={"Authorization": "Token secret"},
                )

        self.assertFalse(request.call_args.kwargs["allow_redirects"])
