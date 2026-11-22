from __future__ import annotations

import re
import shlex
import unittest
from pathlib import Path

from plausible_api_tool.cli import build_parser

ROOT = Path(__file__).resolve().parents[1]


class TestReadmePublicContract(unittest.TestCase):
    def test_install_command_uses_public_slug(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        commands = re.findall(r"^npx skills add (\S+)", readme, re.MULTILINE)
        self.assertEqual(commands, ["Qwayk/safe-agent-skills@plausible"])

    def test_readme_guide_links_open(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        links = re.findall(r"\]\((docs/[^)]+)\)", readme)
        self.assertTrue(links)
        for link in links:
            with self.subTest(link=link):
                file, _, anchor = link.partition("#")
                guide = ROOT / file
                self.assertTrue(guide.is_file())
                if anchor:
                    headings = re.findall(r"^#{1,6} (.+)$", guide.read_text(encoding="utf-8"), re.MULTILINE)
                    anchors = {re.sub(r"[^\w -]", "", heading.lower()).replace(" ", "-") for heading in headings}
                    self.assertIn(anchor, anchors)

    def test_quickstart_invokes_real_read_commands(self) -> None:
        quickstart = (ROOT / "docs" / "quickstart.md").read_text(encoding="utf-8")
        examples = re.findall(r"^plausible-api-tool (.+)$", quickstart, re.MULTILINE)
        parser = build_parser()
        checked = set()
        for example in examples:
            args = shlex.split(example)
            if args == ["--version"]:
                continue
            with self.subTest(command=example):
                options = parser.parse_args(args)
                self.assertFalse(options.apply)
                self.assertIn(options.cmd, {"auth", "stats"})
                checked.add(options.cmd)
        self.assertEqual(checked, {"auth", "stats"})
