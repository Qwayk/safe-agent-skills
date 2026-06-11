from __future__ import annotations

import tempfile
import unittest
import os

from hacker_news_api_tool.config import load_config


class TestConfigLoading(unittest.TestCase):
    def test_env_file_loads_api_root(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = os.path.join(d, ".env")
            with open(env_path, "w", encoding="utf-8") as f:
                f.write("HACKER_NEWS_API_ROOT=https://status.example.com/v0\n")
                f.write("HACKER_NEWS_TIMEOUT_S=12\n")
            cfg = load_config(env_path)
            self.assertEqual(cfg.api_root, "https://status.example.com/v0")
            self.assertEqual(cfg.timeout_s, 12.0)

    def test_os_env_overrides_env_file(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = os.path.join(d, ".env")
            with open(env_path, "w", encoding="utf-8") as f:
                f.write("HACKER_NEWS_API_ROOT=https://status.example.com/v0\n")
            old = os.environ.get("HACKER_NEWS_API_ROOT")
            os.environ["HACKER_NEWS_API_ROOT"] = "https://override.example.com/v0"
            try:
                cfg = load_config(env_path)
                self.assertEqual(cfg.api_root, "https://override.example.com/v0")
            finally:
                if old is None:
                    os.environ.pop("HACKER_NEWS_API_ROOT", None)
                else:
                    os.environ["HACKER_NEWS_API_ROOT"] = old

    def test_default_api_root_is_hn_api(self) -> None:
        cfg = load_config(None)
        self.assertTrue(cfg.api_root.startswith("https://hacker-news.firebaseio.com/v0"))
