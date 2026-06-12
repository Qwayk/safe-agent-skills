from __future__ import annotations

import unittest
from pathlib import Path


class TestReadmePublicContract(unittest.TestCase):
    def test_public_readme_opening_stays_user_facing(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "README.md").read_text(encoding="utf-8")

        self.assertTrue(text.startswith("# CallRail\n"))
        self.assertIn("**Capability:** Reads + careful changes", text)
        self.assertIn("CallRail is where calls, texts, forms", text)

        stale_phrases = [
            "Use this skill when",
            "For non-technical users",
            "For technical users",
            "with dry-run-first write paths",
            "without guessing from raw docs",
        ]
        for phrase in stale_phrases:
            self.assertNotIn(phrase, text)

    def test_required_sections_and_links_stay_public_ready(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "README.md").read_text(encoding="utf-8")

        required = [
            "## Start here first",
            "## What this skill helps with",
            "## What access this skill needs",
            "## Install and first run",
            "## How this skill stays safe",
            "## What it covers today",
            "## What happens before live changes",
            "## What proof it leaves behind",
            "## Limits",
            "## Helpful docs",
            "[What you can do with CallRail](docs/use_cases.md)",
            "[Connect your CallRail account](docs/onboarding.md)",
            "[How this skill stays safe](docs/safety_model.md)",
            "[Browse all CallRail docs](docs/README.md)",
        ]
        for item in required:
            self.assertIn(item, text)

    def test_use_cases_stay_callrail_specific(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "docs" / "use_cases.md").read_text(encoding="utf-8")

        self.assertIn("which leads came in", text)
        self.assertIn("outbound call", text)
        self.assertIn("MMS reply", text)
        self.assertNotIn("Common use cases (examples)", text)
        self.assertNotIn("What you'll see from the agent", text)
