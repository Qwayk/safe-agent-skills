from __future__ import annotations

import re
import unittest
from pathlib import Path
from urllib.parse import urlsplit


class TestReadmePublicContract(unittest.TestCase):
    def test_public_skill_keeps_its_install_name(self) -> None:
        skill = Path(__file__).resolve().parents[1]
        _, metadata, _ = (skill / "SKILL.md").read_text(encoding="utf-8").split("---", 2)
        self.assertIn("name: reddit", metadata.splitlines())

    def test_public_guides_link_to_available_files(self) -> None:
        skill = Path(__file__).resolve().parents[1]
        readme = skill / "README.md"
        quickstart = skill / "docs" / "quickstart.md"
        for page in (readme, skill / "SKILL.md", quickstart):
            targets = [
                urlsplit(link)
                for link in re.findall(r"\]\(([^)]+)\)", page.read_text(encoding="utf-8"))
            ]
            local_paths = {target.path for target in targets if not target.scheme and target.path}
            if page == readme:
                self.assertIn("docs/quickstart.md", local_paths)
            for path in local_paths:
                self.assertTrue((page.parent / path).is_file(), f"{page.name}: {path}")
