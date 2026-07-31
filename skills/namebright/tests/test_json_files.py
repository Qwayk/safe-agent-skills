from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from namebright_safe_cli.errors import ValidationError
from namebright_safe_cli.json_files import read_json_file, write_json_file


class TestJsonFiles(unittest.TestCase):
    def test_read_json_file(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "payload.json"
            p.write_text('{"a": 1, "b": "x"}', encoding="utf-8")
            self.assertEqual(read_json_file(p), {"a": 1, "b": "x"})

    def test_read_json_file_rejects_invalid_json(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "payload.json"
            p.write_text("{\n", encoding="utf-8")
            with self.assertRaises(ValidationError):
                read_json_file(p)

    def test_write_json_file_uses_private_modes(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "out" / "plan.json"
            path = write_json_file(p, {"ok": True})
            self.assertTrue(Path(path).exists())
            self.assertEqual(Path(path).stat().st_mode & 0o777, 0o600)
            self.assertEqual(p.parent.stat().st_mode & 0o777, 0o700)

    def test_write_json_file_creates_parent_directory(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "nested" / "deeper" / "plan.json"
            write_json_file(p, {"safe": True})
            self.assertTrue(p.parent.exists())
            self.assertEqual(p.parent.stat().st_mode & 0o777, 0o700)
