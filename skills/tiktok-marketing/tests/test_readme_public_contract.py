from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class TestReadmePublicContract(unittest.TestCase):
    def test_install_command_uses_published_slug(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("npx skills add Qwayk/safe-agent-skills@tiktok-marketing -g -y", readme)

    def test_public_skill_and_starting_guide_links_resolve(self) -> None:
        for name in ("README.md", "SKILL.md", "docs/quickstart.md"):
            page = ROOT / name
            for link in re.findall(r"\]\(([^)\s]+)\)", page.read_text(encoding="utf-8")):
                target = link.split("#", 1)[0]
                if target and "://" not in target:
                    with self.subTest(page=name, link=link):
                        self.assertTrue((page.parent / target).is_file())
