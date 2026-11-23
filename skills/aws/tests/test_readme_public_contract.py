from __future__ import annotations

import re
import unittest
from pathlib import Path


class TestPublicInstall(unittest.TestCase):
    def test_install_command_matches_skill_name(self) -> None:
        root = Path(__file__).resolve().parents[1]
        header = (root / "SKILL.md").read_text(encoding="utf-8").split("---", 2)[1]
        name = re.search(r"^name:\s*(\S+)\s*$", header, re.MULTILINE)
        self.assertIsNotNone(name)
        self.assertEqual("aws", name.group(1))
        readme = (root / "README.md").read_text(encoding="utf-8")
        self.assertIn(f"npx skills add Qwayk/safe-agent-skills@{name.group(1)} -g -y", readme)
