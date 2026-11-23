from __future__ import annotations

import re
import unittest
from pathlib import Path


class TestDocsFormatting(unittest.TestCase):
    def test_api_coverage_has_real_newlines(self) -> None:
        root = Path(__file__).resolve().parents[1]
        api_coverage = root / "docs" / "api_coverage.md"
        text = api_coverage.read_text(encoding="utf-8")

        self.assertIn("\n", text, "docs/api_coverage.md must contain real newline characters")
        self.assertNotIn("\\n", text, "docs/api_coverage.md must not contain literal \\n escapes")

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

    def test_guide_links_point_to_existing_files(self) -> None:
        root = Path(__file__).resolve().parents[1]
        for path in [root / "README.md", *(root / "docs").glob("*.md")]:
            for link in re.findall(r"\]\(([^()\s]+)\)", path.read_text(encoding="utf-8")):
                if "://" in link or link.startswith("#"):
                    continue
                with self.subTest(file=path.name, link=link):
                    self.assertTrue((path.parent / link.partition("#")[0]).exists())
