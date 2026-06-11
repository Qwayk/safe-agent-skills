from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout

from amazon_creators_api_tool.cli import main


def _run_cmd(args: list[str]) -> tuple[int, dict[str, object]]:
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = main(["--output", "json"] + args)
    return rc, json.loads(buf.getvalue())


class TestLocalesCommands(unittest.TestCase):
    def test_locales_list_returns_known_marketplaces(self) -> None:
        rc, payload = _run_cmd(["locales", "list"])
        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        locales = payload["locales"]
        self.assertGreater(len(locales), 5)
        us = next(item for item in locales if item["locale"] == "en_US")
        self.assertEqual(us["marketplace"], "www.amazon.com")
        self.assertEqual(
            us["token_endpoint_v2"],
            "https://creatorsapi.auth.us-east-1.amazoncognito.com/oauth2/token",
        )
        self.assertEqual(
            us["token_endpoint_v3"],
            "https://api.amazon.com/auth/o2/token",
        )

    def test_locales_show_accepts_locale_aliases(self) -> None:
        rc, payload = _run_cmd(["locales", "show", "--locale", "uk"])
        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["locale"], "en_GB")
        mapping = payload["mapping"]
        self.assertEqual(mapping["marketplace"], "www.amazon.co.uk")
        self.assertEqual(
            mapping["token_endpoint_v3"],
            "https://api.amazon.co.uk/auth/o2/token",
        )
