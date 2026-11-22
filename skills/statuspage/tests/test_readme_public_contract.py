from __future__ import annotations

import contextlib
import io
import re
import shlex
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit

from statuspage_api_tool.cli import build_parser

ROOT = Path(__file__).resolve().parents[1]


class TestPublicInstallGuide(unittest.TestCase):
    def test_install_command_selects_statuspage(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        commands = [
            shlex.split(line)
            for line in readme.splitlines()
            if line.startswith("npx skills add ")
        ]
        self.assertEqual(len(commands), 1)
        self.assertEqual(commands[0][3], "Qwayk/safe-agent-skills@statuspage")

    def test_local_guide_links_resolve(self) -> None:
        guides = [ROOT / "README.md", ROOT / "SKILL.md", *(ROOT / "docs").rglob("*.md")]
        for guide in guides:
            for target in re.findall(r"\[[^\]\n]+\]\(([^)\s]+)\)", guide.read_text(encoding="utf-8")):
                link = urlsplit(target)
                if link.scheme or not link.path:
                    continue
                with self.subTest(guide=guide.relative_to(ROOT), target=target):
                    self.assertTrue((guide.parent / unquote(link.path)).is_file())

    def test_quickstart_command_checks_current_status(self) -> None:
        quickstart = (ROOT / "docs/quickstart.md").read_text(encoding="utf-8")
        command = next(
            line for line in quickstart.splitlines()
            if line.startswith(".venv/bin/statuspage-api-tool ")
        )
        with contextlib.redirect_stdout(io.StringIO()):
            args = build_parser().parse_args(shlex.split(command)[1:])
        self.assertEqual((args.cmd, args.summary_cmd), ("summary", "get"))
        self.assertEqual(args.base_url, "https://status.atlassian.com")
