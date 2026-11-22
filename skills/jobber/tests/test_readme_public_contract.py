from __future__ import annotations

import tomllib
import unittest
from pathlib import Path


class TestReadmePublicContract(unittest.TestCase):
    def test_install_example_uses_the_jobber_skill_and_cli(self) -> None:
        root = Path(__file__).resolve().parents[1]
        readme = (root / "README.md").read_text(encoding="utf-8")
        wrapper = (root / "SKILL.md").read_text(encoding="utf-8")
        package = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))

        self.assertIn("npx skills add Qwayk/safe-agent-skills@jobber", readme)
        self.assertIn("\nname: jobber\n", wrapper.split("---", 2)[1])
        self.assertIn("qwayk-jobber-safe-agent-cli", wrapper)
        self.assertIn("qwayk-jobber-safe-agent-cli", package["project"]["scripts"])
