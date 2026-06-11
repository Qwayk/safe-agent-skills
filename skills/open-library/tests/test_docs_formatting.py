from __future__ import annotations

import re
import unittest
from pathlib import Path


class TestDocsFormatting(unittest.TestCase):
    def test_no_double_bullet_lines(self) -> None:
        root = Path(__file__).resolve().parents[1]
        targets = [
            root / "README.md",
            root / "docs",
        ]
        bad_lines: list[str] = []
        for p in targets:
            if p.is_file():
                files = [p]
            else:
                files = list(p.rglob("*.md"))
            for f in files:
                text = f.read_text(encoding="utf-8")
                for i, line in enumerate(text.splitlines(), start=1):
                    if re.match(r"^\s*-\s+-\s", line):
                        bad_lines.append(f"{f.relative_to(root)}:{i}: {line}")

        if bad_lines:
            self.fail("Double-bullet lines found:\n" + "\n".join(bad_lines))
