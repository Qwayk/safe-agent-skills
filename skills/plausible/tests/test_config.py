from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from plausible_api_tool.config import load_config


class TestConfig(unittest.TestCase):
    def test_missing_required_vars(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text("PLAUSIBLE_BASE_URL=https://example.com\n", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "Missing PLAUSIBLE_API_KEY"):
                load_config(str(env_path))

    def test_missing_env_file_has_hint(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / "does_not_exist.env"
            with self.assertRaisesRegex(RuntimeError, "env file not found"):
                load_config(str(env_path))

    def test_loads_valid_env(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "PLAUSIBLE_BASE_URL=https://plausible.example.com/",
                        "PLAUSIBLE_API_KEY=abc123",
                        "PLAUSIBLE_SITE_ID=example.com",
                        "PLAUSIBLE_TIMEOUT_S=10",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            cfg = load_config(str(env_path))
            self.assertEqual(cfg.base_url, "https://plausible.example.com")
            self.assertEqual(cfg.api_key, "abc123")
            self.assertEqual(cfg.site_id, "example.com")
            self.assertEqual(cfg.timeout_s, 10.0)
            self.assertIsNone(cfg.cf_access_client_id)
            self.assertIsNone(cfg.cf_access_client_secret)

    def test_loads_optional_cloudflare_access_service_token(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "PLAUSIBLE_BASE_URL=https://plausible.example.com/",
                        "PLAUSIBLE_API_KEY=abc123",
                        "PLAUSIBLE_SITE_ID=example.com",
                        "CF_ACCESS_CLIENT_ID=cfid",
                        "CF_ACCESS_CLIENT_SECRET=cfsecret",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            cfg = load_config(str(env_path))
            self.assertEqual(cfg.cf_access_client_id, "cfid")
            self.assertEqual(cfg.cf_access_client_secret, "cfsecret")
