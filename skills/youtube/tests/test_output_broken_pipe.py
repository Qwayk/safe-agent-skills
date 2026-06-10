import io
import unittest
from unittest import mock

from youtube_api_tool.output import Output


class _BrokenPipeStdout(io.TextIOBase):
    def write(self, s: str) -> int:
        raise BrokenPipeError()


class TestOutputBrokenPipe(unittest.TestCase):
    def test_emit_json_ignores_broken_pipe(self) -> None:
        out = Output(mode="json")
        with mock.patch("sys.stdout", _BrokenPipeStdout()):
            out.emit({"ok": True, "value": 123})
        self.assertEqual(out.last, {"ok": True, "value": 123})

    def test_emit_text_ignores_broken_pipe_for_strings(self) -> None:
        out = Output(mode="text")
        with mock.patch("sys.stdout", _BrokenPipeStdout()):
            out.emit("hello")
        self.assertEqual(out.last, "hello")

    def test_emit_text_ignores_broken_pipe_for_dicts(self) -> None:
        out = Output(mode="text")
        with mock.patch("sys.stdout", _BrokenPipeStdout()):
            out.emit({"ok": True})
        self.assertEqual(out.last, {"ok": True})

