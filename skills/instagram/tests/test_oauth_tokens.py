from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from instagram_api_tool.oauth_tokens import (
    get_token_status,
    read_access_token,
    read_token_json,
    redact_token_dict,
    write_token_from_file,
)


class TestOAuthTokens(unittest.TestCase):
    def test_reads_token_from_an_existing_instagram_sign_in_reply(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            token = Path(d) / "token.json"
            token.write_text(json.dumps({"data": [{"access_token": "fixture-token", "user_id": "123"}]}))
            self.assertEqual(read_access_token(token), "fixture-token")

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

