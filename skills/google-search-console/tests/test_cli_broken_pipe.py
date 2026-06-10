from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

from gsc_api_tool.cli import main


class _BrokenStdout:
    encoding = "utf-8"

    def write(self, _s: str) -> int:  # pragma: no cover
        raise BrokenPipeError()

    def flush(self) -> None:  # pragma: no cover
        return


class TestCliBrokenPipe(unittest.TestCase):
    def test_broken_pipe_returns_zero(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text("", encoding="utf-8")

            old = sys.stdout
            try:
                sys.stdout = _BrokenStdout()  # type: ignore[assignment]
                rc = main(["--env-file", str(env_path), "--output", "json", "operations", "validate"])
            finally:
                sys.stdout = old

        self.assertEqual(rc, 0)

