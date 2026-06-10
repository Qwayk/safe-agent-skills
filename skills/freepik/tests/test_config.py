from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from freepik_api_tool.config import load_config


class TestConfig(unittest.TestCase):
    def test_load_config_ok(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / ".env"
            p.write_text(
                "\n".join(
                    [
                        "FREEPIK_API_BASE_URL=https://api.freepik.com/v1",
                        "FREEPIK_API_KEY=abc",
                        "FREEPIK_TIMEOUT_S=12",
                        "FREEPIK_ACCEPT_LANGUAGE=en-US",
                        "FREEPIK_IMAGE_SIZE=1000px",
                        "FREEPIK_AUTH_HEADER=X-Api-Key",
                        "FREEPIK_AUTH_PREFIX=",
                    ]
                ),
                encoding="utf-8",
            )
            cfg = load_config(str(p))
            self.assertEqual(cfg.base_url, "https://api.freepik.com/v1")
            self.assertEqual(cfg.api_key, "abc")
            self.assertEqual(cfg.timeout_s, 12.0)
            self.assertEqual(cfg.accept_language, "en-US")
            self.assertEqual(cfg.image_size, "1000px")
            self.assertEqual(cfg.auth_header, "X-Api-Key")
            self.assertEqual(cfg.auth_prefix, "")

    def test_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / ".env"
            p.write_text(
                "\n".join(
                    [
                        "FREEPIK_API_BASE_URL=https://api.freepik.com/v1",
                        "FREEPIK_API_KEY=abc",
                    ]
                ),
                encoding="utf-8",
            )
            cfg = load_config(str(p))
            self.assertEqual(cfg.timeout_s, 30.0)
            self.assertIsNone(cfg.accept_language)
            self.assertIsNone(cfg.image_size)
            self.assertEqual(cfg.auth_header, "x-freepik-api-key")
            self.assertEqual(cfg.auth_prefix, "")

    def test_load_config_accepts_freepik_base_url_alias(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / ".env"
            p.write_text(
                "\n".join(["FREEPIK_BASE_URL=https://api.freepik.com/v1", "FREEPIK_API_KEY=abc"]),
                encoding="utf-8",
            )
            cfg = load_config(str(p))
            self.assertEqual(cfg.base_url, "https://api.freepik.com/v1")

    def test_missing_key_raises(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / ".env"
            p.write_text("FREEPIK_API_BASE_URL=https://api.freepik.com/v1\n", encoding="utf-8")
            with self.assertRaises(RuntimeError):
                load_config(str(p))
