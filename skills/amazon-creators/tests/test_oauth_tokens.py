from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from amazon_creators_api_tool.config import Config
from amazon_creators_api_tool.errors import ValidationError
from amazon_creators_api_tool.oauth_tokens import (
    authorization_header,
    fetch_and_cache_token,
    get_token_status,
    read_token_json,
    redact_token_dict,
    token_path_for_env_file,
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

    def _write_token(self, env_dir: Path, value: str) -> Path:
        env_file = env_dir / ".env"
        env_file.write_text("", encoding="utf-8")
        token_path = token_path_for_env_file(str(env_file))
        token_path.parent.mkdir(parents=True, exist_ok=True)
        token_path.write_text(json.dumps({"access_token": value}), encoding="utf-8")
        return env_file

    def _build_config(self, version: str) -> Config:
        return Config(
            base_url="https://creatorsapi.amazon/catalog/v1",
            credential_id="cid",
            credential_secret="secret",
            credential_version=version,
            locale="en_US",
            timeout_s=30,
            token_url=None,
            partner_tag="partner",
        )

    def test_authorization_header_refuses_expired_token(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_file = self._write_token(Path(td), "expired")
            path = token_path_for_env_file(str(env_file))
            path.write_text(
                json.dumps(
                    {"access_token": "expired", "expires_at": 0},
                ),
                encoding="utf-8",
            )
            cfg = self._build_config("2")
            with self.assertRaises(ValidationError):
                authorization_header(cfg, str(env_file))

    def test_fetch_and_cache_token_saves_expiry(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_file = Path(td) / ".env"
            env_file.write_text("", encoding="utf-8")
            cfg = Config(
                base_url="https://creatorsapi.amazon/catalog/v1",
                credential_id="cid",
                credential_secret="secret",
                credential_version="2.1",
                locale="en_US",
                timeout_s=30,
                token_url="https://example.test/token",
                partner_tag="partner",
            )
            token_file = token_path_for_env_file(str(env_file))
            token_file.parent.mkdir(parents=True, exist_ok=True)

            class FakeResp:
                status_code = 200

                def json(self_non):
                    return {"access_token": "new", "expires_in": 900}

            with patch("amazon_creators_api_tool.oauth_tokens.requests.post", return_value=FakeResp()) as mock_post:
                status = fetch_and_cache_token(cfg, str(env_file))

            args, kwargs = mock_post.call_args
            self.assertEqual(args[0], "https://example.test/token")
            self.assertIn("data", kwargs)
            self.assertNotIn("json", kwargs)
            self.assertEqual(kwargs["data"]["scope"], "creatorsapi/default")
            self.assertEqual(kwargs["headers"]["Content-Type"], "application/x-www-form-urlencoded")
            self.assertTrue(status.exists)
            data = read_token_json(token_file)
            self.assertIsNotNone(data)
            self.assertIn("expires_at", data)
            self.assertEqual(data["access_token"], "new")

    def test_fetch_and_cache_token_uses_json_for_v3(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_file = Path(td) / ".env"
            env_file.write_text("", encoding="utf-8")
            cfg = Config(
                base_url="https://creatorsapi.amazon/catalog/v1",
                credential_id="cid",
                credential_secret="secret",
                credential_version="3.1",
                locale="en_US",
                timeout_s=30,
                token_url="https://example.test/token-v3",
                partner_tag="partner",
            )
            token_file = token_path_for_env_file(str(env_file))
            token_file.parent.mkdir(parents=True, exist_ok=True)

            class FakeResp:
                status_code = 200

                def json(self_non):
                    return {"access_token": "new", "expires_in": 900}

            with patch("amazon_creators_api_tool.oauth_tokens.requests.post", return_value=FakeResp()) as mock_post:
                status = fetch_and_cache_token(cfg, str(env_file))

            args, kwargs = mock_post.call_args
            self.assertEqual(args[0], "https://example.test/token-v3")
            self.assertIn("json", kwargs)
            self.assertNotIn("data", kwargs)
            self.assertEqual(kwargs["json"]["scope"], "creatorsapi::default")
            self.assertEqual(kwargs["headers"]["Content-Type"], "application/json")
            self.assertTrue(status.exists)

    def test_authorization_header_attaches_version_for_v2(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_file = self._write_token(Path(td), "abc")
            cfg = self._build_config("2")
            header = authorization_header(cfg, str(env_file))
            self.assertTrue(header.startswith("Bearer "))
            self.assertIn(", Version 2", header)

    def test_authorization_header_accepts_v_prefix(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_file = self._write_token(Path(td), "abc")
            cfg = self._build_config("v2.1")
            header = authorization_header(cfg, str(env_file))
            self.assertTrue(header.startswith("Bearer "))
            self.assertIn(", Version 2.1", header)

    def test_authorization_header_skips_version_for_v3(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_file = self._write_token(Path(td), "xyz")
            cfg = self._build_config("3")
            header = authorization_header(cfg, str(env_file))
            self.assertEqual(header, "Bearer xyz")
