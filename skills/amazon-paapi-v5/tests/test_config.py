from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from amazon_pa_api_tool.config import load_config


class TestConfig(unittest.TestCase):
    def test_load_config_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "AMAZON_PA_ACCESS_KEY_ID=AKIAEXAMPLE",
                        "AMAZON_PA_SECRET_ACCESS_KEY=secret",
                        "AMAZON_PA_PARTNER_TAG=mytag-20",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            cfg = load_config(str(env_path))
            self.assertEqual(cfg.partner_tag, "mytag-20")
            self.assertEqual(cfg.partner_type, "Associates")
            self.assertEqual(cfg.host, "webservices.amazon.com")
            self.assertEqual(cfg.region, "us-east-1")
            self.assertEqual(cfg.marketplace, "www.amazon.com")

    def test_missing_access_key(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "AMAZON_PA_SECRET_ACCESS_KEY=secret",
                        "AMAZON_PA_PARTNER_TAG=mytag-20",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(RuntimeError, "AMAZON_PA_ACCESS_KEY_ID"):
                load_config(str(env_path))

