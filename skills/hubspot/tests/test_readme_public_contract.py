from __future__ import annotations

import re
import unittest
from pathlib import Path


class TestReadmePublicContract(unittest.TestCase):
    def test_install_slug_matches_catalog_and_skill(self) -> None:
        root = Path(__file__).resolve().parents[1]
        readme = (root / "README.md").read_text(encoding="utf-8")
        wrapper = (root / "SKILL.md").read_text(encoding="utf-8")
        self.assertRegex(wrapper, r"(?m)^name: hubspot$")
        self.assertIn("npx skills add Qwayk/safe-agent-skills@hubspot -g -y", readme)
        catalog = root.parent / "README.md"
        if catalog.is_file():
            row = next(
                line for line in catalog.read_text(encoding="utf-8").splitlines()
                if "(hubspot/README.md)" in line
            )
            self.assertIn("<code>hubspot</code>", row)

    def test_setup_and_write_review_are_linked_from_readme(self) -> None:
        root = Path(__file__).resolve().parents[1]
        readme = (root / "README.md").read_text(encoding="utf-8")
        links = re.findall(r"\]\((docs/[^)]+)\)", readme)
        for target in ("docs/onboarding.md", "docs/safety_model.md"):
            with self.subTest(target=target):
                self.assertIn(target, links)
                self.assertTrue((root / target).is_file())
