from __future__ import annotations

import argparse
import re
import shlex
import tomllib
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit

from awin_publisher_safe_agent_cli.cli import build_parser


class TestDocsStandard(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(__file__).resolve().parents[1]
        self.docs = self.root / "docs"

    def test_install_command_matches_the_skill_name(self) -> None:
        wrapper = self.root / "SKILL.md"
        if not wrapper.is_file():
            wrapper = self.root / "skills/awin-publisher-safe-cli/SKILL.md"
        _, fields, _ = wrapper.read_text(encoding="utf-8").split("---", 2)
        name, = (line.partition(":")[2].strip() for line in fields.splitlines() if line.startswith("name:"))
        readme = (self.root / "README.md").read_text(encoding="utf-8")
        command, = (shlex.split(line) for line in readme.splitlines() if line.startswith("npx skills add "))
        self.assertEqual(name, "awin-publisher-safe-cli")
        self.assertEqual(command[:4], ["npx", "skills", "add", f"Qwayk/safe-agent-skills@{name}"])
        project = tomllib.loads((self.root / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertEqual(project["project"]["scripts"][name], "awin_publisher_safe_agent_cli.__main__:main")

    def test_local_guide_links_work(self) -> None:
        for page in self.root.rglob("*.md"):
            if any(part.startswith(".") for part in page.relative_to(self.root).parts):
                continue
            for link in re.findall(r"\]\(([^)\s]+)\)", page.read_text(encoding="utf-8")):
                destination = urlsplit(link)
                if destination.scheme or destination.netloc or not destination.path:
                    continue
                with self.subTest(page=page.name, link=link):
                    self.assertTrue((page.parent / unquote(destination.path)).exists())

    def test_api_coverage_lists_all_provider_backed_commands(self) -> None:
        parser = build_parser()
        coverage = self._coverage_table_text()
        support_only = {"onboarding", "auth check", "runs list", "runs show"}
        live_commands = sorted(
            command
            for command in self._leaf_commands(parser)
            if command not in support_only
        )
        missing = [command for command in live_commands if f"`{command}`" not in coverage]
        self.assertEqual(
            [],
            missing,
            "docs/api_coverage.md is missing shipped provider-backed command(s): "
            + ", ".join(missing),
        )

    def _coverage_table_text(self) -> str:
        text = (self.docs / "api_coverage.md").read_text(encoding="utf-8")
        return text.split("## Endpoint shape notes", 1)[0]

    def _leaf_commands(self, parser: argparse.ArgumentParser, prefix: tuple[str, ...] = ()) -> list[str]:
        commands: list[str] = []
        for action in parser._actions:
            if not isinstance(action, argparse._SubParsersAction):
                continue
            for name, subparser in action.choices.items():
                command = prefix + (name,)
                nested = self._leaf_commands(subparser, command)
                if nested:
                    commands.extend(nested)
                    continue
                if subparser._defaults.get("func") is not None:
                    commands.append(" ".join(command))
        return commands
