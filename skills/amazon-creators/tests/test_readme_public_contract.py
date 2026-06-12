from __future__ import annotations

import unittest
from pathlib import Path


class TestReadmePublicContract(unittest.TestCase):
    def test_public_readme_opening_stays_user_facing(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "README.md").read_text(encoding="utf-8")

        self.assertTrue(text.startswith("# Amazon Creators\n"))
        self.assertIn("**Capability:** Reads + guarded local helpers", text)
        self.assertIn("Amazon Creators is useful when you need structured Amazon catalog details", text)

        stale_phrases = [
            "Use this skill when",
            "For non-technical users",
            "For technical users",
            "with dry-run-first catalog requests",
            "The shipped surface covers",
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
            "## What happens before live work",
            "## What proof it leaves behind",
            "## Limits",
            "## Helpful docs",
            "[What you can do with Amazon Creators](docs/use_cases.md)",
            "[Connect your Amazon Creators account](docs/onboarding.md)",
            "[How this skill stays safe](docs/safety_model.md)",
            "[Browse all Amazon Creators docs](docs/README.md)",
        ]
        for item in required:
            self.assertIn(item, text)

    def test_use_cases_stay_amazon_specific(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "docs" / "use_cases.md").read_text(encoding="utf-8")

        self.assertIn("ISBNs, ASINs, resource presets, and locales", text)
        self.assertIn("paperback, hardcover, and Kindle", text)
        self.assertIn("browse-node hierarchy", text)
        self.assertNotIn("Bulk research", text)
