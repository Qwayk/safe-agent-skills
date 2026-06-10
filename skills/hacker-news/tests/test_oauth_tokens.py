from __future__ import annotations

import os
import tempfile
import unittest

from hacker_news_api_tool.config import load_config
from hacker_news_api_tool.errors import ValidationError


class TestTimeoutValidation(unittest.TestCase):
    def test_timeout_must_be_positive_number(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = os.path.join(d, ".env")
            with open(env_path, "w", encoding="utf-8") as f:
                f.write("HACKER_NEWS_API_ROOT=https://status.example.com/v0\n")
                f.write("HACKER_NEWS_TIMEOUT_S=0\n")
            with self.assertRaises(ValidationError):
                load_config(env_path)

    def test_timeout_must_be_numeric(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = os.path.join(d, ".env")
            with open(env_path, "w", encoding="utf-8") as f:
                f.write("HACKER_NEWS_API_ROOT=https://status.example.com/v0\n")
                f.write("HACKER_NEWS_TIMEOUT_S=abc\n")
            with self.assertRaises(ValidationError):
                load_config(env_path)
