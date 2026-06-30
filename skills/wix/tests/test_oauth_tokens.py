from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from wix_safe_agent_cli.oauth_tokens import (
    get_token_status,
    metadata_view,
    read_token_json,
    redact_token_dict,
    write_token_from_dict,
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

    def test_write_from_dict(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            dest = Path(d) / ".state" / "token.json"
            st = write_token_from_dict(
                token_payload={"access_token": "A", "token_type": "Bearer", "expires_in": 3600},
                dest_file=dest,
            )
            self.assertTrue(st.exists)
            data = read_token_json(dest)
            self.assertIsNotNone(data)
            assert data is not None
            self.assertEqual(data["token_type"], "Bearer")

    def test_metadata_view_masks_token(self) -> None:
        out = metadata_view(
            {
                "access_token": "A",
                "subject_id": "S",
                "active": True,
            }
        )
        self.assertEqual(out["access_token"], "***REDACTED***")
        self.assertEqual(out["subject_id"], "S")
        self.assertIn("received_at_utc", out)
