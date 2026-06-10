from __future__ import annotations

import unittest

from ._helpers import run_cli


class TestCliVersion(unittest.TestCase):
    def test_version_json_no_env_needed(self) -> None:
        rc, payload = run_cli(["--output", "json", "--version"])
        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["tool"], "cloudinary-safe-agent-cli")
        self.assertIn("version", payload)
