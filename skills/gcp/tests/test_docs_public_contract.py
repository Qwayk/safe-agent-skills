from __future__ import annotations

import json
import re
import shlex
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit

from gcp_safe_agent_cli.cli import build_parser


class TestPublicGuides(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(__file__).resolve().parents[1]
        self.docs = self.root / "docs"

    def test_local_guide_links_resolve(self) -> None:
        guides = [self.root / "README.md", self.root / "SKILL.md", *self.docs.glob("*.md")]
        for guide in guides:
            for link in re.findall(r"\[[^\]\n]+\]\(([^)\s]+)\)", guide.read_text(encoding="utf-8")):
                parsed = urlsplit(link)
                if parsed.scheme or parsed.netloc or not parsed.path:
                    continue
                with self.subTest(guide=guide.name, link=link):
                    self.assertTrue((guide.parent / unquote(parsed.path)).exists())

    def test_quickstart_and_change_examples_use_supported_commands(self) -> None:
        parser = build_parser()
        for name in ("quickstart.md", "command_reference.md"):
            text = (self.docs / name).read_text(encoding="utf-8")
            commands = re.findall(r"^qwayk-gcp-safe-agent-cli (?!<)(.+)$", text, re.MULTILINE)
            self.assertTrue(commands, name)
            for command in commands:
                with self.subTest(guide=name, command=command):
                    args = parser.parse_args(shlex.split(command))
                    if args.apply:
                        self.assertTrue(args.yes and args.plan_in and args.input_json)
                    if args.plan_out:
                        self.assertTrue(args.bind_adc and args.input_json)

    def test_example_outputs_are_json_and_identify_their_source(self) -> None:
        examples = self.docs / "examples"
        paths = [*examples.glob("*.json"), *(examples / "outputs").glob("*.json")]
        self.assertEqual(6, len(paths))
        for path in paths:
            with self.subTest(example=path.name):
                example = json.loads(path.read_text(encoding="utf-8"))
                self.assertTrue(example["example_kind"])
                self.assertIs(example["live_google_cloud_account_verified"], False)
