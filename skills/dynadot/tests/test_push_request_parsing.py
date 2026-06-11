from __future__ import annotations

import unittest

from dynadot_api_tool.commands.domains import _parse_push_request_domains  # noqa: SLF001


class TestPushRequestParsing(unittest.TestCase):
    def test_parses_bracketed_csv(self) -> None:
        self.assertEqual(_parse_push_request_domains("[a.com,b.com]"), ["a.com", "b.com"])

    def test_parses_semicolon_separated(self) -> None:
        self.assertEqual(_parse_push_request_domains("a.com;b.com"), ["a.com", "b.com"])

    def test_dedupes_and_normalizes(self) -> None:
        self.assertEqual(_parse_push_request_domains("[A.COM, a.com, b.com.]"), ["a.com", "b.com"])

