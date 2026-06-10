from __future__ import annotations

import sys
import unittest
from unittest.mock import patch

from amazon_creators_api_tool.cli import main


class TestBrokenPipeHandling(unittest.TestCase):
    def test_cli_exits_cleanly_when_stdout_pipe_breaks(self) -> None:
        class BrokenPipeStdout:
            def write(self, _content: object) -> int:
                raise BrokenPipeError

            def flush(self) -> None:
                pass

        with patch("sys.stdout", new=BrokenPipeStdout()):
            with self.assertRaises(SystemExit) as cm:
                main(["--output", "json", "locales", "list"])
        self.assertEqual(cm.exception.code, 0)
