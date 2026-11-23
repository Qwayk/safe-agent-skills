from __future__ import annotations

import re
import shlex
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit

from meta_ads_api_tool.cli import build_parser

ROOT = Path(__file__).resolve().parents[1]


class TestPublicInstallGuide(unittest.TestCase):
    def test_install_uses_the_meta_ads_catalog_id(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        commands = [shlex.split(line) for line in readme.splitlines() if line.startswith("npx skills add ")]
        self.assertEqual(len(commands), 1)
        self.assertEqual(commands[0][3], "Qwayk/safe-agent-skills@meta-ads-api-safe-cli")

    def test_local_guide_links_resolve(self) -> None:
        guides = [ROOT / "README.md", ROOT / "SKILL.md", *(ROOT / "docs").rglob("*.md")]
        for guide in guides:
            for target in re.findall(r"\[[^\]\n]+\]\(([^)\s]+)\)", guide.read_text(encoding="utf-8")):
                link = urlsplit(target)
                if link.scheme or not link.path:
                    continue
                with self.subTest(guide=guide.relative_to(ROOT), target=target):
                    self.assertTrue((guide.parent / unquote(link.path)).is_file())

    def test_quickstart_first_report_has_an_account_and_dates(self) -> None:
        guide = (ROOT / "docs" / "quickstart.md").read_text(encoding="utf-8")
        report = next(line for line in guide.splitlines() if "insights get --ad-account-id" in line)
        args = build_parser().parse_args(shlex.split(report)[1:])
        self.assertEqual((args.cmd, args.insights_cmd, args.level), ("insights", "get", "campaign"))
        self.assertTrue(args.ad_account_id.startswith("act_"))
        self.assertLessEqual(args.since, args.until)
