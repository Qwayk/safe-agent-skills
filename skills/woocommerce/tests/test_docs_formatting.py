from __future__ import annotations

import re
import unittest
from pathlib import Path


class TestDocsFormatting(unittest.TestCase):
    def test_no_double_bullet_lines(self) -> None:
        root = Path(__file__).resolve().parents[1]
        bad_lines: list[str] = []
        for path in [root / "README.md", root / "docs"]:
            files = [path] if path.is_file() else list(path.rglob("*.md"))
            for file_path in files:
                text = file_path.read_text(encoding="utf-8")
                for idx, line in enumerate(text.splitlines(), start=1):
                    if re.match(r"^\s*-\s+-\s", line):
                        bad_lines.append(f"{file_path.relative_to(root)}:{idx}: {line}")
        if bad_lines:
            self.fail("Double-bullet lines found:\n" + "\n".join(bad_lines))

    def test_no_template_placeholders_left(self) -> None:
        root = Path(__file__).resolve().parents[1]
        bad_hits: list[str] = []
        files_to_scan = [root / "README.md", root / "docs", root / ".env.example"]
        rules_file = next(root.glob("AGENTS.*"), None)
        if rules_file and rules_file.is_file():
            files_to_scan.append(rules_file)
        for file_path in files_to_scan:
            files = [file_path] if file_path.is_file() else list(file_path.rglob("*"))
            for candidate in files:
                if not candidate.is_file():
                    continue
                text = candidate.read_text(encoding="utf-8")
                for marker in ["example-api-tool", "example_api_tool", "<REPLACE_ME>", "<YYYY-MM-DD>"]:
                    if marker in text:
                        bad_hits.append(f"{candidate.relative_to(root)} contains {marker}")
        if bad_hits:
            self.fail("Template markers still present:\n" + "\n".join(bad_hits))
