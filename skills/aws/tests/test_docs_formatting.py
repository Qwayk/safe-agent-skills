from __future__ import annotations

import re
import unittest
from pathlib import Path


class TestDocsFormatting(unittest.TestCase):
    def test_no_double_bullet_lines(self) -> None:
        root = Path(__file__).resolve().parents[1]
        patterns = [
            root / "README.md",
            root / "docs",
        ]
        bad_lines: list[str] = []
        for p in patterns:
            if p.is_file():
                files = [p]
            else:
                files = list(p.rglob("*.md"))
            for f in files:
                try:
                    text = f.read_text(encoding="utf-8")
                except Exception:
                    continue
                for i, line in enumerate(text.splitlines(), start=1):
                    if re.match(r"^\s*-\s+-\s", line):
                        rel = f.relative_to(root)
                        bad_lines.append(f"{rel}:{i}: {line}")
        if bad_lines:
            joined = "\n".join(bad_lines)
            self.fail("Double-bullet lines found:\n" + joined)

    def test_committed_json_examples_do_not_leak_local_machine_paths(self) -> None:
        root = Path(__file__).resolve().parents[1]
        targets = [
            root / "docs" / "_generated" / "aws_botocore_inventory.json",
            *sorted((root / "docs" / "examples").rglob("*.json")),
        ]
        banned = [
            "/home/",
            "/Users/",
            ".venv",
        ]

        leaks: list[str] = []
        for path in targets:
            text = path.read_text(encoding="utf-8")
            for snippet in banned:
                if snippet in text:
                    leaks.append(f"{path.relative_to(root)} contains {snippet}")

        if leaks:
            self.fail("Committed AWS JSON examples leak local paths:\n" + "\n".join(leaks))
