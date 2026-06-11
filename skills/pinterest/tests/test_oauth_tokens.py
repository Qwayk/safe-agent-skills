from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from pinterest_api_tool.oauth_tokens import get_token_status, read_token_json, redact_token_dict, write_token_from_file
from pinterest_api_tool.commands.auth import _build_oauth_authorize_url


class TestOAuthTokens(unittest.TestCase):
    def test_token_status_missing(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / ".state" / "token.json"
            st = get_token_status(p)
            self.assertFalse(st.exists)

    def test_write_and_redact(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            src = Path(d) / "token_in.json"
            dest = Path(d) / ".state" / "token.json"
            src.write_text(
                json.dumps({"access_token": "A", "refresh_token": "R", "expires_at": 1, "scope": "x"}),
                encoding="utf-8",
            )
            st = write_token_from_file(src_file=src, dest_file=dest)
            self.assertTrue(st.exists)
            data = read_token_json(dest)
            assert data is not None
            safe = redact_token_dict(data)
            self.assertEqual(safe["access_token"], "***REDACTED***")
            self.assertEqual(safe["refresh_token"], "***REDACTED***")
            self.assertEqual(safe["scope"], "x")

    def test_build_oauth_authorize_url(self) -> None:
        url = _build_oauth_authorize_url(
            app_id="123",
            redirect_uri="http://localhost:8765/",
            scopes=["boards:read", "pins:read"],
            state="abc",
        )
        self.assertIn("https://www.pinterest.com/oauth/?", url)
        self.assertIn("client_id=123", url)
        self.assertIn("redirect_uri=http%3A%2F%2Flocalhost%3A8765%2F", url)
        self.assertIn("scope=boards%3Aread%2Cpins%3Aread", url)
        self.assertIn("state=abc", url)
