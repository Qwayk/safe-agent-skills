from __future__ import annotations

import re
import shlex
import unittest
from pathlib import Path

from unsplash_api_tool.cli import build_parser

ROOT = Path(__file__).resolve().parents[1]


class TestPublicGuides(unittest.TestCase):
    def test_guide_links_resolve(self) -> None:
        for guide in [ROOT / "README.md", ROOT / "SKILL.md", *(ROOT / "docs").glob("*.md")]:
            for destination in re.findall(r"\]\(([^)]+)\)", guide.read_text(encoding="utf-8")):
                path, _, anchor = destination.partition("#")
                if "://" in path:
                    continue
                with self.subTest(guide=guide.name, link=destination):
                    target = guide.parent / path if path else guide
                    self.assertTrue(target.exists())
                    if anchor:
                        headings = re.findall(r"^#+ (.+)$", target.read_text(), re.MULTILINE)
                        slugs = {re.sub(r"[^a-z0-9 -]", "", title.lower()).replace(" ", "-") for title in headings}
                        self.assertIn(anchor, slugs)

    def test_setup_and_quickstart_commands_match_the_cli(self) -> None:
        parser = build_parser()
        download_examples = set()
        for name in ("onboarding.md", "quickstart.md"):
            for line in (ROOT / "docs" / name).read_text(encoding="utf-8").splitlines():
                if not line.startswith("unsplash-api-tool "):
                    continue
                with self.subTest(command=line):
                    args = parser.parse_args(shlex.split(line)[1:])
                    self.assertTrue(callable(args.func))
                    if args.cmd == "photos" and args.photos_cmd == "download":
                        download_examples.add(args.apply)
                        if args.apply:
                            self.assertTrue(args.plan_in)
                            self.assertTrue(args.ack_no_snapshot)
                        else:
                            self.assertTrue(args.plan_out)
        self.assertEqual(download_examples, {False, True})
