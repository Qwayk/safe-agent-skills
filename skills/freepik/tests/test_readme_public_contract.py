from __future__ import annotations

import re
import shlex
import unittest
from pathlib import Path

from freepik_api_tool.cli import build_parser

ROOT = Path(__file__).resolve().parents[1]


class TestPublicGuides(unittest.TestCase):
    def test_readme_and_skill_link_to_shipped_guides(self) -> None:
        for name in ("README.md", "SKILL.md", "docs/README.md"):
            guide = ROOT / name
            for link in re.findall(r"\]\(([^)]+)\)", guide.read_text(encoding="utf-8")):
                if "://" not in link and not link.startswith("#"):
                    with self.subTest(guide=name, link=link):
                        self.assertTrue((guide.parent / link.split("#", 1)[0]).is_file())

    def test_quickstart_commands_match_the_download_parser(self) -> None:
        quickstart = (ROOT / "docs/quickstart.md").read_text(encoding="utf-8")
        parser = build_parser(json_mode=False)
        downloads = set()
        for line in quickstart.splitlines():
            if not line.startswith("freepik-api-tool "):
                continue
            with self.subTest(command=line):
                args = parser.parse_args(shlex.split(line)[1:])
                if args.cmd in {"download", "jobs"}:
                    downloads.add((args.cmd, args.apply))
                    if args.apply:
                        self.assertTrue(args.plan_in)
                        self.assertTrue(args.ack_no_snapshot)
                        if args.cmd == "jobs":
                            self.assertTrue(args.yes)
                    else:
                        self.assertTrue(args.plan_out)
        self.assertEqual(downloads, {("download", False), ("download", True), ("jobs", False), ("jobs", True)})
