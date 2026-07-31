from __future__ import annotations

import importlib
import io
import json
import unittest
from contextlib import redirect_stdout

from namebright_safe_cli.cli import main


class TestCliVersion(unittest.TestCase):
    def test_package_imports(self) -> None:
        pkg = importlib.import_module("namebright_safe_cli")
        self.assertTrue(hasattr(pkg, "__path__"))

    def test_version_json_no_env_needed(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["--output", "json", "--version"])
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["tool"], "namebright-safe-cli")
        self.assertIn("version", payload)
