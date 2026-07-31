from __future__ import annotations

import unittest

from namebright_safe_cli.output import Output


class TestSmoke(unittest.TestCase):
    def test_output_constructs(self) -> None:
        out = Output(mode="json")
        self.assertIsNotNone(out)
