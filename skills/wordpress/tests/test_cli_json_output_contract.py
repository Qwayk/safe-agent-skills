import io
import json
import unittest
from contextlib import redirect_stderr, redirect_stdout

from wordpress_api_tool.cli import main as cli_main


class CliJsonOutputContractTests(unittest.TestCase):
    def _run(self, argv):
        out = io.StringIO()
        err = io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            rc = int(cli_main(list(argv)))
        stdout = out.getvalue()
        stderr = err.getvalue()
        payload = json.loads(stdout)
        return rc, stdout, stderr, payload

    def test_json_help_is_single_object(self):
        rc, _out, err, payload = self._run(["--output", "json", "--help"])
        self.assertEqual(rc, 0)
        self.assertEqual(err, "")
        self.assertTrue(payload.get("ok"))
        self.assertEqual(payload.get("kind"), "help")
        self.assertIsInstance(payload.get("help"), str)
        self.assertIn("wordpress-api-tool", payload.get("help") or "")

    def test_json_version_is_machine_readable(self):
        rc, _out, err, payload = self._run(["--output", "json", "--version"])
        self.assertEqual(rc, 0)
        self.assertEqual(err, "")
        self.assertTrue(payload.get("ok"))
        self.assertEqual(payload.get("tool"), "wordpress-api-tool")
        self.assertIsInstance(payload.get("version"), str)

    def test_json_missing_command_is_error_object(self):
        rc, _out, err, payload = self._run(["--output", "json"])
        self.assertEqual(rc, 2)
        self.assertEqual(err, "")
        self.assertFalse(payload.get("ok"))
        self.assertEqual(payload.get("error_type"), "ValidationError")

    def test_json_usage_error_does_not_print_argparse_usage(self):
        rc, _out, err, payload = self._run(["--output", "json", "post", "find"])
        self.assertEqual(rc, 2)
        self.assertEqual(err, "")
        self.assertFalse(payload.get("ok"))
        self.assertEqual(payload.get("error_type"), "ValidationError")
        self.assertIsInstance(payload.get("error"), str)

