from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from mercury_api_tool.cli import main


class _FakeResponse:
    def __init__(self, *, url: str, status_code: int, body: bytes):
        self.url = url
        self.status_code = status_code
        self.content = body
        self.headers = {"content-type": "application/json;charset=utf-8"}

    @property
    def text(self) -> str:
        return self.content.decode("utf-8", errors="replace")


class TestNoTokenLeak(unittest.TestCase):
    def test_auth_check_does_not_print_token(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            token = "secret-token:TEST_TOKEN_DO_NOT_LEAK"
            env_path.write_text(
                "MERCURY_API_BASE_URL=https://api.mercury.com/api/v1\n"
                f"MERCURY_API_TOKEN={token}\n"
                "MERCURY_AUTH_SCHEME=bearer\n"
                "MERCURY_TIMEOUT_S=30\n",
                encoding="utf-8",
            )

            seen_headers: list[dict[str, str] | None] = []

            def _fake_request(self, method, url, headers=None, params=None, json=None, data=None, timeout=None):  # noqa: ANN001
                seen_headers.append(headers)
                return _FakeResponse(url=url, status_code=200, body=b'{"id":"org_1"}')

            out_buf = io.StringIO()
            err_buf = io.StringIO()
            with patch("mercury_api_tool.http.requests.Session.request", new=_fake_request):
                with redirect_stdout(out_buf), redirect_stderr(err_buf):
                    rc = main(["--output", "json", "--verbose", "--env-file", str(env_path), "auth", "check"])

            self.assertEqual(rc, 0)
            payload = json.loads(out_buf.getvalue())
            self.assertTrue(payload["ok"])

            self.assertTrue(seen_headers)
            auth = (seen_headers[0] or {}).get("Authorization") or ""
            self.assertIn(token, auth)

            combined = out_buf.getvalue() + err_buf.getvalue()
            self.assertNotIn(token, combined)
