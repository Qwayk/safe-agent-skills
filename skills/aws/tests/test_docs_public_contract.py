from __future__ import annotations

import io
import json
import re
import shlex
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from urllib.parse import unquote, urlsplit

from aws_safe_agent_cli.aws_runtime import build_parser


class TestPublicGuides(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(__file__).resolve().parents[1]
        self.docs = self.root / "docs"

    def test_local_guide_links_resolve(self) -> None:
        guides = [self.root / "README.md", self.root / "SKILL.md", *self.docs.glob("*.md")]
        for guide in guides:
            for href in re.findall(r"\[[^\]\n]+\]\(([^)\s]+)\)", guide.read_text(encoding="utf-8")):
                link = urlsplit(href)
                if not link.scheme and not link.netloc and link.path:
                    with self.subTest(guide=guide.name, link=href):
                        self.assertTrue((guide.parent / unquote(link.path)).exists())

    def test_quickstart_and_command_examples_use_supported_commands(self) -> None:
        for name in ("quickstart.md", "command_reference.md"):
            guide = (self.docs / name).read_text(encoding="utf-8")
            commands = re.findall(r"^qwayk-aws-safe-agent-cli (?!<)(.+)$", guide, re.MULTILINE)
            self.assertTrue(commands, name)
            for command in commands:
                with self.subTest(guide=name, command=command):
                    argv = shlex.split(command)
                    if "--help" in argv:
                        with redirect_stdout(io.StringIO()), self.assertRaises(SystemExit) as result:
                            build_parser().parse_args(argv)
                        self.assertEqual(0, result.exception.code)
                        continue
                    args = build_parser().parse_args(argv)
                    if args.plan_out:
                        self.assertTrue(args.bind_aws and args.input_json)
                    if args.apply:
                        self.assertTrue(args.plan_in and args.yes)

    def test_saved_examples_are_json_and_the_write_samples_are_marked(self) -> None:
        examples = self.docs / "examples"
        paths = sorted(examples.rglob("*.json"))
        self.assertEqual(5, len(paths))
        for path in paths:
            with self.subTest(example=path.name):
                payload = json.loads(path.read_text(encoding="utf-8"))
                self.assertIsInstance(payload, dict)
                if path.name.endswith(".example.json"):
                    self.assertIs(payload["example"], True)
