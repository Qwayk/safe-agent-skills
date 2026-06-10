from __future__ import annotations

import os
import tempfile
import unittest

from statuspage_api_tool.config import load_config


class TestConfigLoading(unittest.TestCase):
    def test_env_file_loads_base_url(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = os.path.join(d, ".env")
            with open(env_path, "w", encoding="utf-8") as f:
                f.write("STATUSPAGE_BASE_URL=https://status.example.com\n")
                f.write("STATUSPAGE_TIMEOUT_S=12\n")
            cfg = load_config(env_path)
            self.assertEqual(cfg.base_url, "https://status.example.com")
            self.assertEqual(cfg.timeout_s, 12.0)

    def test_os_env_overrides_env_file(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = os.path.join(d, ".env")
            with open(env_path, "w", encoding="utf-8") as f:
                f.write("STATUSPAGE_BASE_URL=https://status.example.com\n")
            old = os.environ.get("STATUSPAGE_BASE_URL")
            os.environ["STATUSPAGE_BASE_URL"] = "https://override.example.com"
            try:
                cfg = load_config(env_path)
                self.assertEqual(cfg.base_url, "https://override.example.com")
            finally:
                if old is None:
                    os.environ.pop("STATUSPAGE_BASE_URL", None)
                else:
                    os.environ["STATUSPAGE_BASE_URL"] = old
