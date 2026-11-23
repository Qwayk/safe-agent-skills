from __future__ import annotations

import importlib
import re
import shlex
import tomllib
import unittest
from pathlib import Path

from qdrant_cloud_api_tool.cli import build_parser


class TestPublicInstall(unittest.TestCase):
    root = Path(__file__).resolve().parents[1]

    def test_readme_install_command_matches_the_skill(self) -> None:
        readme = (self.root / "README.md").read_text(encoding="utf-8")
        skill = (self.root / "SKILL.md").read_text(encoding="utf-8")
        slug = re.search(r"^name: ([a-z0-9-]+)$", skill, re.MULTILINE)
        self.assertIsNotNone(slug)
        commands = [
            shlex.split(line) for line in readme.splitlines() if line.startswith("npx skills add ")
        ]
        self.assertEqual(len(commands), 1)
        self.assertEqual(commands[0][3], f"Qwayk/safe-agent-skills@{slug.group(1)}")

    def test_onboarding_uses_the_installed_entry_point(self) -> None:
        config = tomllib.loads((self.root / "pyproject.toml").read_text(encoding="utf-8"))
        onboarding = (self.root / "docs/onboarding.md").read_text(encoding="utf-8")
        commands = [
            shlex.split(line)
            for line in onboarding.splitlines()
            if line.startswith(".venv/bin/") and line.endswith(" onboarding")
        ]
        self.assertEqual(len(commands), 1)
        entry_point = Path(commands[0][0]).name
        module, function = config["project"]["scripts"][entry_point].split(":")
        self.assertTrue(callable(getattr(importlib.import_module(module), function)))
        self.assertIsNotNone(build_parser().parse_args(commands[0][1:]).func)

    def test_readme_and_setup_guide_links_work(self) -> None:
        for path in (self.root / "README.md", self.root / "docs/onboarding.md"):
            text = path.read_text(encoding="utf-8")
            for link in re.findall(r"\]\(([^()\s]+)\)", text):
                if "://" not in link and not link.startswith("#"):
                    with self.subTest(file=path.name, link=link):
                        self.assertTrue((path.parent / link.partition("#")[0]).exists())
