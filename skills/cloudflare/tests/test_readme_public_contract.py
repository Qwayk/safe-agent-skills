from __future__ import annotations

import shlex
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestPublishedInstall(unittest.TestCase):
    def test_readme_installs_the_published_skill_name(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        command, = (shlex.split(line) for line in readme.splitlines() if line.startswith("npx skills add "))
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        _, front_matter, _ = skill.split("---", 2)
        name, = (line.partition(":")[2].strip() for line in front_matter.splitlines() if line.startswith("name:"))
        self.assertEqual(name, "cloudflare-api-safe-cli")
        self.assertEqual(command[:4], ["npx", "skills", "add", f"Qwayk/safe-agent-skills@{name}"])

    def test_quickstart_uses_the_installed_cli_and_ships_the_command_list(self) -> None:
        quickstart = (ROOT / "docs/quickstart.md").read_text(encoding="utf-8")
        command, = (shlex.split(line) for line in quickstart.splitlines() if line.startswith("cloudflare-api-tool --version"))
        project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertEqual(project["project"]["scripts"][command[0]], "cloudflare_api_tool.__main__:main")
        package = project["tool"]["setuptools"]["package-data"]["cloudflare_api_tool"]
        inventory = "_data/live_official_api_inventory.json"
        self.assertIn(inventory, package)
        self.assertTrue((ROOT / "src/cloudflare_api_tool" / inventory).is_file())
