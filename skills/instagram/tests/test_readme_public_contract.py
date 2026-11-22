from __future__ import annotations

import re
import unittest
from pathlib import Path


class TestReadmePublicContract(unittest.TestCase):
    def test_install_command_uses_the_catalog_slug(self) -> None:
        skill = Path(__file__).resolve().parents[1]
        readme = (skill / "README.md").read_text(encoding="utf-8")
        self.assertIn("npx skills add Qwayk/safe-agent-skills@instagram -g -y", readme.splitlines())

    def test_readme_and_quickstart_links_point_to_existing_files(self) -> None:
        skill = Path(__file__).resolve().parents[1]
        for file in (skill / "README.md", skill / "docs/quickstart.md"):
            for link in re.findall(r"\]\(([^)#]+)(?:#[^)]*)?\)", file.read_text(encoding="utf-8")):
                if "://" not in link:
                    self.assertTrue((file.parent / link).is_file(), f"{file.name}: {link}")
