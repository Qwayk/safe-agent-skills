from __future__ import annotations

import unittest
from pathlib import Path


class TestReadmePublicContract(unittest.TestCase):
    def test_public_readme_opening_stays_user_facing(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "README.md").read_text(encoding="utf-8")

        self.assertTrue(text.startswith("# Salesforce\n"))
        self.assertIn("**Capability:** Reads + careful changes", text)
        self.assertIn("Salesforce is where customer records", text)

        stale_phrases = [
            "Use this skill when",
            "For non-technical users",
            "For technical users",
            "without guessing from raw docs",
            "Safe CLI",
        ]
        for phrase in stale_phrases:
            self.assertNotIn(phrase, text)

    def test_required_sections_stay_public_ready(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "README.md").read_text(encoding="utf-8")

        required_sections = [
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
        ]
        for section in required_sections:
            self.assertIn(section, text)

    def test_links_and_use_cases_stay_human_facing(self) -> None:
        root = Path(__file__).resolve().parents[1]
        readme = (root / "README.md").read_text(encoding="utf-8")
        use_cases = (root / "docs" / "use_cases.md").read_text(encoding="utf-8")

        self.assertIn("[What you can do with Salesforce](docs/use_cases.md)", readme)
        self.assertIn("[Connect your Salesforce org](docs/onboarding.md)", readme)
        self.assertIn("[How this skill stays safe](docs/safety_model.md)", readme)
        self.assertIn("[Browse all Salesforce docs](docs/README.md)", readme)
        self.assertNotIn("- `docs/use_cases.md`", readme)
        self.assertNotIn("ad hoc API calls", use_cases)
        self.assertIn("Salesforce Platform work is usually about understanding the org", use_cases)
        self.assertIn("Bulk API job", use_cases)
