from __future__ import annotations

import re
import shlex
import unittest
from pathlib import Path

from contentsquare_safe_agent_cli.cli import build_parser


class TestReadmePublicContract(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(__file__).resolve().parents[1]

    def test_install_command_uses_the_public_slug(self) -> None:
        readme = (self.root / "README.md").read_text(encoding="utf-8")
        self.assertIn("npx skills add Qwayk/safe-agent-skills@contentsquare", readme)
        self.assertTrue((self.root / "SKILL.md").is_file())

    def test_quickstart_commands_are_available(self) -> None:
        text = (self.root / "docs" / "quickstart.md").read_text(encoding="utf-8")
        commands = re.findall(r"^contentsquare-safe-cli (.+)$", text, flags=re.MULTILINE)
        self.assertTrue(commands)
        parser = build_parser()
        for command in commands:
            with self.subTest(command=command):
                args = parser.parse_args(shlex.split(command))
                self.assertFalse(args.apply)
                self.assertTrue(callable(args.func))
