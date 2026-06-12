from __future__ import annotations

import io
import unittest
from contextlib import redirect_stdout

from jobber_safe_agent_cli.cli import main
from jobber_safe_agent_cli.schema_registry import mutation_fields, query_fields


class TestCliHelp(unittest.TestCase):
    def test_named_read_and_write_commands_are_exposed(self) -> None:
        read_query = query_fields()[0].name
        write_mutation = mutation_fields()[0].name

        read_buf = io.StringIO()
        with redirect_stdout(read_buf):
            rc_read = main(["read", "--help"])
        self.assertEqual(rc_read, 0)
        self.assertIn(read_query, read_buf.getvalue())

        write_buf = io.StringIO()
        with redirect_stdout(write_buf):
            rc_write = main(["write", "--help"])
        self.assertEqual(rc_write, 0)
        self.assertIn(write_mutation, write_buf.getvalue())

