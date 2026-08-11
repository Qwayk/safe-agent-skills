from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from giantpanda_api_tool.config import GIANTPANDA_API_HOST, load_config
from giantpanda_api_tool.errors import ValidationError


class TestConfig(unittest.TestCase):
    def test_fixed_host_is_constant(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("", encoding="utf-8")
            cfg = load_config(str(env_path))
            self.assertEqual(cfg.host, GIANTPANDA_API_HOST)

    def test_timeout_from_env_variable(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("GIANTPANDA_TIMEOUT_S=12\n", encoding="utf-8")
            cfg = load_config(str(env_path))
            self.assertEqual(cfg.timeout_s, 12.0)

    def test_env_overrides_file_for_token(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("GIANTPANDA_API_TOKEN=file-token\n", encoding="utf-8")
            os.environ["GIANTPANDA_API_TOKEN"] = "process-token"
            try:
                cfg = load_config(str(env_path))
            finally:
                os.environ.pop("GIANTPANDA_API_TOKEN", None)
            self.assertEqual(cfg.token, "process-token")

    def test_invalid_timeout_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("GIANTPANDA_TIMEOUT_S=0\n", encoding="utf-8")
            with self.assertRaises(ValidationError):
                load_config(str(env_path))
