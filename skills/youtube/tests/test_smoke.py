from __future__ import annotations

import unittest

from youtube_api_tool.output import Output


class TestSmoke(unittest.TestCase):
    def test_output_constructs(self) -> None:
        out = Output(mode="json")
        self.assertIsNotNone(out)
