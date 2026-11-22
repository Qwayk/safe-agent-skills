from __future__ import annotations

import re
import shlex
import unittest
from pathlib import Path

from instantly_api_tool.cli import build_parser

ROOT = Path(__file__).resolve().parents[1]


class TestReadmePublicContract(unittest.TestCase):
    def test_install_command_uses_public_slug(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        install_commands = re.findall(r"^npx skills add (\S+)", readme, re.MULTILINE)
        self.assertEqual(install_commands, ["Qwayk/safe-agent-skills@instantly"])

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

    def test_quickstart_examples_are_read_only_and_parse(self) -> None:
        quickstart = (ROOT / "docs" / "quickstart.md").read_text(encoding="utf-8")
        examples = re.findall(r"^instantly-api-tool (.+)$", quickstart, re.MULTILINE)
        self.assertTrue(examples)
        parser = build_parser()
        for example in examples:
            arguments = shlex.split(example)
            if arguments == ["--version"]:
                continue
            with self.subTest(command=example):
                options = parser.parse_args(arguments)
                self.assertFalse(options.apply)
                self.assertFalse(options.write_capable)
