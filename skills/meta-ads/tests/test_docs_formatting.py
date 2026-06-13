from __future__ import annotations

import re
import unittest
from pathlib import Path


class TestDocsFormatting(unittest.TestCase):
    def test_no_double_bullet_lines(self) -> None:
        root = Path(__file__).resolve().parents[1]
        patterns = [
            root / "README.md",
            root / "docs",
        ]
        bad_lines: list[str] = []
        for p in patterns:
            if p.is_file():
                files = [p]
            else:
                files = list(p.rglob("*.md"))
            for f in files:
                try:
                    text = f.read_text(encoding="utf-8")
                except Exception:
                    continue
                for i, line in enumerate(text.splitlines(), start=1):
                    if re.match(r"^\s*-\s+-\s", line):
                        rel = f.relative_to(root)
                        bad_lines.append(f"{rel}:{i}: {line}")
        if bad_lines:
            joined = "\n".join(bad_lines)
            self.fail("Double-bullet lines found:\n" + joined)

    def test_use_cases_stays_human_and_specific(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "docs" / "use_cases.md").read_text(encoding="utf-8")

        required = [
            "Meta Ads is useful when a media buyer wants to understand",
            "## Good questions to ask",
            "## Everyday work this helps with",
            "## What the agent should show you",
            "## Good first path",
            "Which campaigns changed performance in the last 7 days?",
        ]
        for phrase in required:
            self.assertIn(phrase, text)

        stale_phrases = [
            "Meta Ads work usually starts with performance questions",
            "Inventory and account checks",
            "Insights and reporting",
            "Analysis packs and creative review",
            "Because this tool is read-only",
        ]
        for phrase in stale_phrases:
            self.assertNotIn(phrase, text)
