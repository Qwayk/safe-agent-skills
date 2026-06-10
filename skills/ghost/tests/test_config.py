import os
import tempfile
import unittest

from ghost_api_tool.config import load_config, load_content_config
from ghost_api_tool.errors import ValidationError


class ConfigTests(unittest.TestCase):
    def test_load_config_from_env_file(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, ".env")
            with open(p, "w", encoding="utf-8") as f:
                f.write("GHOST_ADMIN_API_URL=https://example.com/ghost/api/admin/\n")
                f.write("GHOST_ADMIN_API_KEY=abc:" + "00" * 32 + "\n")
                f.write("GHOST_ACCEPT_VERSION=v5.0\n")
                f.write("GHOST_TIMEOUT_S=12\n")
            cfg = load_config(p)
            self.assertEqual(cfg.accept_version, "v5.0")
            self.assertEqual(cfg.timeout_s, 12.0)

    def test_load_content_config_from_env_file(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, ".env")
            with open(p, "w", encoding="utf-8") as f:
                f.write("GHOST_CONTENT_API_URL=https://example.com/ghost/api/content\n")
                f.write("GHOST_CONTENT_API_KEY=deadbeef\n")
                f.write("GHOST_ACCEPT_VERSION=v5.0\n")
                f.write("GHOST_TIMEOUT_S=7\n")
            cfg = load_content_config(p)
            self.assertEqual(cfg.content_api_url, "https://example.com/ghost/api/content/")
            self.assertEqual(cfg.content_api_key, "deadbeef")
            self.assertEqual(cfg.accept_version, "v5.0")
            self.assertEqual(cfg.timeout_s, 7.0)

    def test_load_content_config_requires_key(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, ".env")
            with open(p, "w", encoding="utf-8") as f:
                f.write("GHOST_CONTENT_API_URL=https://example.com/ghost/api/content/\n")
                f.write("GHOST_ACCEPT_VERSION=v5.0\n")
            with self.assertRaises(ValidationError):
                _ = load_content_config(p)
