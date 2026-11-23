from __future__ import annotations

import re
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit


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

    def test_guide_links_point_to_shipped_files(self) -> None:
        root = Path(__file__).resolve().parents[1]
        pages = [root / "README.md", root / "SKILL.md", *(root / "docs").rglob("*.md")]
        for page in pages:
            for link in re.findall(r"\]\(([^)\s]+)\)", page.read_text(encoding="utf-8")):
                parts = urlsplit(link)
                if parts.scheme or parts.netloc or not parts.path:
                    continue
                with self.subTest(page=page.name, link=link):
                    target = (page.parent / unquote(parts.path)).resolve()
                    self.assertTrue(target.is_relative_to(root))
                    self.assertTrue(target.is_file())
