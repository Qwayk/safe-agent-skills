from __future__ import annotations

import unittest

from ._helpers import run_cli


class TestCliJsonParseErrors(unittest.TestCase):
    def test_missing_command_is_json_error(self) -> None:
        rc, payload = run_cli(["--output", "json"])
        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")

    def test_missing_required_subcommand_is_json_error(self) -> None:
        rc, payload = run_cli(["--output", "json", "auth"])
        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")
