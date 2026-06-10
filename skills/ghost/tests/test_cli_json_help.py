import io
import json
import unittest
from contextlib import redirect_stdout

from ghost_api_tool.cli import main as cli_main


class CliJsonHelpTests(unittest.TestCase):
    def test_help_is_single_json_object_in_json_mode(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cli_main(["--output", "json", "--help"])
        self.assertEqual(rc, 0)
        obj = json.loads(buf.getvalue())
        self.assertTrue(obj["ok"])
        self.assertEqual(obj.get("kind"), "help")
        self.assertIn("usage: ghost-api-tool", obj.get("help") or "")

    def test_subcommand_help_is_single_json_object_in_json_mode(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cli_main(["--output", "json", "post", "--help"])
        self.assertEqual(rc, 0)
        obj = json.loads(buf.getvalue())
        self.assertTrue(obj["ok"])
        self.assertEqual(obj.get("kind"), "help")
        self.assertIn("usage: ghost-api-tool post", obj.get("help") or "")

