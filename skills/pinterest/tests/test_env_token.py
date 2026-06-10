from __future__ import annotations

import unittest

from pinterest_api_tool.api import resolve_access_token


class TestEnvToken(unittest.TestCase):
    def test_env_access_token_wins(self) -> None:
        tok = resolve_access_token(
            env_file="/does/not/matter",
            env_access_token=" X ",
            env_refresh_token=None,
            app_id=None,
            app_secret=None,
            base_url="https://api.pinterest.com/v5",
            http=None,  # type: ignore[arg-type]
        )
        self.assertEqual(tok, "X")
