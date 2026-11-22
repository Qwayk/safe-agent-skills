from __future__ import annotations

import re
import unittest
from pathlib import Path


class TestXPublicPackage(unittest.TestCase):
    def test_x_install_slug(self) -> None:
        root = Path(__file__).resolve().parents[1]
        self.assertIn("skills add Qwayk/safe-agent-skills@x ", (root / "README.md").read_text())
        self.assertIn("name: x", (root / "SKILL.md").read_text().split("---")[1])

    def test_local_guide_links(self) -> None:
        root = Path(__file__).resolve().parents[1]
        for guide in (root / "README.md", root / "SKILL.md", *(root / "docs").rglob("*.md")):
            for target in re.findall(r"\]\(([^)#]+)(?:#[^)]*)?\)", guide.read_text()):
                if "://" not in target:
                    with self.subTest(guide=guide.name, target=target):
                        self.assertTrue((guide.parent / target).exists())
