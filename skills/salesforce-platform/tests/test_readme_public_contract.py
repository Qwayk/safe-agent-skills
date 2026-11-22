from __future__ import annotations

import unittest
from pathlib import Path


class TestReadmePublicContract(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(__file__).resolve().parents[1]
        self.readme = (self.root / "README.md").read_text(encoding="utf-8")

    def test_install_command_matches_skill_name(self) -> None:
        slug = "salesforce-platform"
        skill = (self.root / "SKILL.md").read_text(encoding="utf-8")
        frontmatter = skill.split("---", 2)[1]
        self.assertIn(f"name: {slug}", frontmatter.splitlines())
        self.assertIn(f"npx skills add Qwayk/safe-agent-skills@{slug} -g -y", self.readme)

        index = self.root.parent / "README.md"
        if index.is_file():
            self.assertIn(f"]({slug}/README.md)", index.read_text(encoding="utf-8"))

    def test_setup_and_approval_links_have_targets(self) -> None:
        for link in ("docs/onboarding.md", "docs/safety_model.md"):
            with self.subTest(link=link):
                self.assertIn(f"]({link})", self.readme)
                self.assertTrue((self.root / link).is_file())
