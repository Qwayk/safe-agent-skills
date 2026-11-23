from __future__ import annotations

import re
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "SKILL.md"
if not SKILL.is_file():
    SKILL = ROOT / "skills" / "themealdb-safe-reader" / "SKILL.md"


class TestDocsFormatting(unittest.TestCase):
    def test_install_command_matches_the_skill_name(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        front_matter = SKILL.read_text(encoding="utf-8").split("---", 2)[1]
        name = re.search(r"^name: (\S+)$", front_matter, re.MULTILINE)
        command = re.search(r"^npx skills add Qwayk/safe-agent-skills@(\S+) ", readme, re.MULTILINE)
        if name is None or command is None:
            self.fail("Could not find the install command or skill name.")
        self.assertEqual(name.group(1), command.group(1))

    def test_relative_links_point_to_existing_paths(self) -> None:
        paths = [ROOT / "README.md", SKILL, *(ROOT / "docs").rglob("*.md")]
        for path in paths:
            sections = path.read_text(encoding="utf-8").split("```")
            for section in sections[::2]:
                for target in re.findall(r"\[[^\]]+\]\(([^)\s]+)\)", section):
                    url = urlsplit(target)
                    if url.scheme or url.netloc or not url.path:
                        continue
                    with self.subTest(file=path.relative_to(ROOT), link=target):
                        self.assertTrue((path.parent / unquote(url.path)).exists())
