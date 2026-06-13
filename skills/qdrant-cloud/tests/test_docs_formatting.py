from __future__ import annotations

import re
import unittest
from pathlib import Path


class TestDocsFormatting(unittest.TestCase):
    def test_api_coverage_has_real_newlines_and_last_audited(self) -> None:
        root = Path(__file__).resolve().parents[1]
        api_coverage = root / "docs" / "api_coverage.md"
        text = api_coverage.read_text(encoding="utf-8")

        self.assertIn("\n", text, "docs/api_coverage.md must contain real newline characters")
        self.assertNotIn("\\n", text, "docs/api_coverage.md must not contain literal \\n escapes")
        self.assertRegex(text, r"Last audited \(UTC\): \d{4}-\d{2}-\d{2} \d{2}:\d{2} UTC")

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
            "Qdrant Cloud is useful when a team needs to understand",
            "## Good questions to ask",
            "## Everyday work this helps with",
            "## What the agent should show you",
            "## Good first path",
            "Which accounts, clusters, and releases exist right now?",
        ]
        for phrase in required:
            self.assertIn(phrase, text)

        stale_phrases = [
            "Qdrant Cloud work usually starts with infrastructure questions",
            "A good first ask",
            "Good jobs to give the agent",
            "What you should expect from the agent",
            "dry-run plan",
        ]
        for phrase in stale_phrases:
            self.assertNotIn(phrase, text)
