from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from namebright_safe_cli.config import (
    OFFICIAL_NAMEBRIGHT_REST_BASE_URL,
    OFFICIAL_NAMEBRIGHT_TOKEN_URL,
    load_config,
)


class TestConfig(unittest.TestCase):
    def setUp(self) -> None:
        self._orig_id = os.environ.get("NAMEBRIGHT_CLIENT_ID")
        self._orig_secret = os.environ.get("NAMEBRIGHT_CLIENT_SECRET")
        self._orig_timeout = os.environ.get("NAMEBRIGHT_TIMEOUT_S")
        for key in ("NAMEBRIGHT_CLIENT_ID", "NAMEBRIGHT_CLIENT_SECRET", "NAMEBRIGHT_TIMEOUT_S"):
            os.environ.pop(key, None)

    def tearDown(self) -> None:
        for key, value in (
            ("NAMEBRIGHT_CLIENT_ID", self._orig_id),
            ("NAMEBRIGHT_CLIENT_SECRET", self._orig_secret),
            ("NAMEBRIGHT_TIMEOUT_S", self._orig_timeout),
        ):
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def test_load_config_from_env_file(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env = Path(d) / ".env"
            env.write_text(
                "\n".join(
                    [
                        "NAMEBRIGHT_CLIENT_ID=file-id",
                        "NAMEBRIGHT_CLIENT_SECRET=file-secret",
                        "NAMEBRIGHT_TIMEOUT_S=45",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            cfg = load_config(str(env))
            self.assertEqual(cfg.base_url, OFFICIAL_NAMEBRIGHT_REST_BASE_URL)
            self.assertEqual(cfg.token_url, OFFICIAL_NAMEBRIGHT_TOKEN_URL)
            self.assertEqual(cfg.client_id, "file-id")
            self.assertEqual(cfg.client_secret, "file-secret")
            self.assertAlmostEqual(cfg.timeout_s, 45)

    def test_environment_overrides_env_file(self) -> None:
        os.environ["NAMEBRIGHT_CLIENT_ID"] = "env-id"
        os.environ["NAMEBRIGHT_CLIENT_SECRET"] = "env-secret"
        with tempfile.TemporaryDirectory() as d:
            env = Path(d) / ".env"
            env.write_text(
                "NAMEBRIGHT_CLIENT_ID=file-id\nNAMEBRIGHT_CLIENT_SECRET=file-secret\n",
                encoding="utf-8",
            )
            cfg = load_config(str(env))
            self.assertEqual(cfg.client_id, "env-id")
            self.assertEqual(cfg.client_secret, "env-secret")

    def test_invalid_timeout(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env = Path(d) / ".env"
            env.write_text(
                "NAMEBRIGHT_CLIENT_ID=id\nNAMEBRIGHT_CLIENT_SECRET=secret\nNAMEBRIGHT_TIMEOUT_S=bad\n",
                encoding="utf-8",
            )
            with self.assertRaises(RuntimeError):
                load_config(str(env))

    def test_missing_client_secret(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env = Path(d) / ".env"
            env.write_text("NAMEBRIGHT_CLIENT_ID=id\n", encoding="utf-8")
            with self.assertRaises(RuntimeError):
                load_config(str(env))
