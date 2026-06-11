from __future__ import annotations

import json
import tempfile
import time
import unittest
from pathlib import Path
from types import SimpleNamespace

from qwayk_reddit_safe_agent_cli.commands.auth import ValidationError, ensure_access_token
from qwayk_reddit_safe_agent_cli.oauth_tokens import (
    get_token_status,
    read_token_json,
    redact_token_dict,
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

    def test_access_token_with_no_expiry_is_not_treated_as_fresh(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text("", encoding="utf-8")
            token_path = env_path.parent / ".state" / "token.json"
            token_path.parent.mkdir(parents=True, exist_ok=True)
            token_path.write_text(json.dumps({"access_token": "stale-token"}, indent=2), encoding="utf-8")

            cfg = SimpleNamespace(
                bearer_token=None,
                client_id="client-id",
                client_secret=None,
                token_url="https://example.com/token",
                user_agent="unit-test",
            )
            with self.assertRaises(ValidationError) as ctx:
                ensure_access_token(cfg=cfg, env_file=str(env_path), timeout_s=5, verbose=False)
            self.assertIn("Missing usable Reddit OAuth token", str(ctx.exception))

    def test_access_token_expires_in_is_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text("", encoding="utf-8")
            token_path = env_path.parent / ".state" / "token.json"
            token_path.parent.mkdir(parents=True, exist_ok=True)
            token_path.write_text(
                json.dumps({"access_token": "fresh-token", "expires_in": "3600"},
                           indent=2),
                encoding="utf-8",
            )

            cfg = SimpleNamespace(
                bearer_token=None,
                client_id="client-id",
                client_secret=None,
                token_url="https://example.com/token",
                user_agent="unit-test",
            )
            token, source = ensure_access_token(cfg=cfg, env_file=str(env_path), timeout_s=5, verbose=False)
            self.assertEqual(token, "fresh-token")
            self.assertEqual(source, "token_file")

    def test_token_status_parses_common_expiry_shapes(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            token_path = Path(d) / ".state" / "token.json"
            token_path.parent.mkdir(parents=True, exist_ok=True)
            now = time.time()
            token_path.write_text(json.dumps({"access_token": "x", "expires_in": 3600}, indent=2), encoding="utf-8")
            status_in = get_token_status(token_path)
            self.assertTrue(status_in.exists)
            self.assertIsNotNone(status_in.expires_at_utc)

            token_path.write_text(json.dumps({"access_token": "x", "expiry": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now + 3600))}, indent=2), encoding="utf-8")
            status_iso = get_token_status(token_path)
            self.assertTrue(status_iso.exists)
            self.assertIsNotNone(status_iso.expires_at_utc)
