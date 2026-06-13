from __future__ import annotations

import unittest
from pathlib import Path


class TestReadmePublicContract(unittest.TestCase):
    def test_public_readme_opening_stays_user_facing(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "README.md").read_text(encoding="utf-8")

        self.assertTrue(text.startswith("# HubSpot\n"))
        self.assertIn("**Capability:** Reads + careful changes", text)
        self.assertIn("HubSpot is where CRM records become", text)

        stale_phrases = [
            "Use this skill when",
            "For non-technical users",
            "For technical users",
            "plan careful CRM changes with preview",
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
            "## What happens before live changes",
            "## Limits",
            "## Helpful docs",
        ]
        for section in required_sections:
            self.assertIn(section, text)

    def test_links_stay_human_facing(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "README.md").read_text(encoding="utf-8")

        self.assertIn("[What you can do with HubSpot](docs/use_cases.md)", text)
        self.assertIn("[Connect your HubSpot account](docs/onboarding.md)", text)
        self.assertIn("[How this skill stays safe](docs/safety_model.md)", text)
        self.assertIn("[Quickstart](docs/quickstart.md)", text)
        self.assertIn("[Command guide](docs/command_reference.md)", text)
        self.assertIn("[Browse all HubSpot docs](docs/README.md)", text)
        self.assertIn("[Authentication details](docs/authentication.md)", text)
        self.assertIn("[Proof pack](docs/proof.md)", text)
        self.assertIn("[API coverage](docs/api_coverage.md)", text)
        self.assertNotIn("- `docs/use_cases.md`", text)
        self.assertNotIn("- `docs/onboarding.md`", text)

    def test_use_cases_stay_hubspot_specific(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "docs" / "use_cases.md").read_text(encoding="utf-8")

        stale_phrases = [
            "Why this beats typical no-code work",
            "Most automation tools",
            "Less guessing",
            "Bulk work:",
        ]
        for phrase in stale_phrases:
            self.assertNotIn(phrase, text)

        self.assertIn("# What you can do with HubSpot", text)
        self.assertIn("CRM record review", text)
        self.assertIn("Properties, associations, and pipeline checks", text)
        self.assertIn("Imports, exports, and account readiness", text)
        self.assertIn("Good first HubSpot path", text)
