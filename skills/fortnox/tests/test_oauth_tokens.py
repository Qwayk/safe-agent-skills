from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from fortnox_api_tool.oauth_tokens import (
    get_token_status,
    read_token_json,
    redact_token_dict,
    token_is_expired,
    token_path_for_env_file,
    write_token_dict,
    write_token_from_file,
)


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
                json.dumps({"access_token": "A", "refresh_token": "R", "expires_in": 3600, "scope": "x"}),
                encoding="utf-8",
            )
            st = write_token_from_file(src_file=src, dest_file=dest)
            self.assertTrue(st.exists)
            self.assertTrue(st.has_access_token)
            self.assertTrue(st.has_refresh_token)
            data = read_token_json(dest)
            assert data is not None
            safe = redact_token_dict(data)
            self.assertEqual(safe["access_token"], "***REDACTED***")
            self.assertEqual(safe["refresh_token"], "***REDACTED***")
            self.assertEqual(safe["scope"], "x")
            self.assertIsNotNone(data.get("expires_at"))
            self.assertFalse(token_is_expired(data))

    def test_write_token_dict_can_preserve_refresh_token(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            dest = Path(d) / ".state" / "token.json"
            write_token_dict(
                data={"access_token": "OLD", "refresh_token": "KEEP", "expires_in": 60},
                dest_file=dest,
                token_source="authorization_code",
            )
            existing = read_token_json(dest)
            assert existing is not None
            st = write_token_dict(
                data={"access_token": "NEW", "expires_in": 120},
                dest_file=dest,
                existing=existing,
                token_source="refresh_token",
                preserve_refresh_token=True,
            )
            self.assertTrue(st.exists)
            saved = read_token_json(dest)
            assert saved is not None
            self.assertEqual(saved["refresh_token"], "KEEP")
            self.assertEqual(saved["token_source"], "refresh_token")

    def test_token_path_can_be_overridden_relative_to_env_file(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_file = str(Path(d) / ".env")
            token_path = token_path_for_env_file(env_file, ".custom/token.json")
            self.assertEqual(token_path, Path(d) / ".custom" / "token.json")
