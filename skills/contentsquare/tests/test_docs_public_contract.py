from __future__ import annotations

import re
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit


class TestDocsPublicContract(unittest.TestCase):
    def test_local_guide_links_resolve(self) -> None:
        root = Path(__file__).resolve().parents[1]
        for page in [root / "README.md", root / "SKILL.md", *sorted((root / "docs").glob("*.md"))]:
            guide = page.read_text(encoding="utf-8")
            for target in re.findall(r"\[[^\]\n]+\]\(([^)\s]+)\)", guide):
                link = urlsplit(target)
                if link.scheme or not link.path:
                    continue
                with self.subTest(page=page.relative_to(root), link=target):
                    destination = (page.parent / unquote(link.path)).resolve()
                    self.assertTrue(destination.is_relative_to(root))
                    self.assertTrue(destination.is_file())
