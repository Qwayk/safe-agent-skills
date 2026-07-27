from __future__ import annotations

import contextlib
import io
import json
import unittest

from asana_safe_agent_cli.cli import main


class TestCliVersion(unittest.TestCase):
    def test_version_is_one_json_object_without_auth(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            rc = main(["--version"])
        payload = json.loads(stdout.getvalue())
        self.assertEqual(rc, 0)
        self.assertEqual(payload["tool"], "asana-safe")
        self.assertEqual(stdout.getvalue().count("\n}"), 1)


if __name__ == "__main__":
    unittest.main()
