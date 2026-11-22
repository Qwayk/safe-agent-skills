from __future__ import annotations

import re
import shlex
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit

from klaviyo_safe_agent_cli.cli import build_parser


class TestReadmePublicContract(unittest.TestCase):
    def test_local_guide_links_resolve(self) -> None:
        root = Path(__file__).resolve().parents[1]
        for relative in ("README.md", "docs/README.md", "docs/quickstart.md", "docs/onboarding.md"):
            page = root / relative
            for url in re.findall(r"\[[^\]\n]+\]\(([^()\n]+)\)", page.read_text(encoding="utf-8")):
                link = urlsplit(url)
                if link.scheme or link.netloc:
                    continue
                target = page.parent / unquote(link.path) if link.path else page
                self.assertTrue(target.exists(), f"{relative} links to a missing path: {url}")

    def test_quickstart_commands_use_the_installed_cli(self) -> None:
        quickstart = Path(__file__).resolve().parents[1] / "docs" / "quickstart.md"
        parser = build_parser()
        commands = [
            parser.parse_args(shlex.split(line)[1:])
            for line in quickstart.read_text(encoding="utf-8").splitlines()
            if line.startswith("klaviyo-safe-agent-cli ")
        ]
        self.assertTrue(any(args.live and getattr(args, "op", None) == "get_lists" for args in commands))
