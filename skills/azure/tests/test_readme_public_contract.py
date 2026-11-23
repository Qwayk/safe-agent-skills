from __future__ import annotations

import shlex
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestPublishedInstall(unittest.TestCase):
    def test_readme_install_uses_the_public_skill_slug(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        commands = (shlex.split(line) for line in readme.splitlines() if line.startswith("npx skills add "))
        command, = commands
        self.assertEqual(command[:4], ["npx", "skills", "add", "Qwayk/safe-agent-skills@azure"])
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        _, front_matter, _ = skill.split("---", 2)
        self.assertIn("name: azure", front_matter.splitlines())

    def test_cli_install_keeps_the_registered_binary(self) -> None:
        project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertEqual(
            project["project"]["scripts"]["qwayk-azure-safe-agent-cli"],
            "azure_safe_agent_cli.__main__:main",
        )
