from __future__ import annotations

import re
import unittest
from pathlib import Path


class TestInstallAndGuideLinks(unittest.TestCase):
    def test_install_name_and_local_links(self) -> None:
        root = Path(__file__).resolve().parents[1]
        readme = root / "README.md"
        skill = root / "SKILL.md"
        if not skill.exists():
            skill = root / "skills" / "amazon-creators-api-safe-cli" / "SKILL.md"
        self.assertIn("npx skills add Qwayk/safe-agent-skills@amazon-creators -g -y", readme.read_text())
        self.assertRegex(skill.read_text(), r"(?m)^name: amazon-creators$")

        for page in [readme, skill, *(root / "docs").glob("*.md")]:
            for target in re.findall(r"\]\(([^)]+)\)", page.read_text()):
                if "://" in target:
                    continue
                relative, _, fragment = target.partition("#")
                destination = page.parent / relative if relative else page
                with self.subTest(page=page.name, target=target):
                    self.assertTrue(destination.exists())
                    if fragment:
                        headings = re.findall(r"(?m)^#+ (.+)$", destination.read_text())
                        self.assertIn(fragment, [heading.lower().replace(" ", "-") for heading in headings])
