from __future__ import annotations

import unittest
from pathlib import Path


class TestReadmePublicContract(unittest.TestCase):
    def test_public_readme_opening_stays_user_facing(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "README.md").read_text(encoding="utf-8")

        self.assertTrue(text.startswith("# WooCommerce\n"))
        self.assertIn("**Capability:** Reads + careful changes", text)
        self.assertIn("WooCommerce is where a WordPress store", text)

        stale_phrases = [
            "Use this skill when",
            "For non-technical users",
            "For technical users",
            "safe way to use",
            "without guessing from raw docs",
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

        self.assertIn("[What you can do with WooCommerce](docs/use_cases.md)", readme)
        self.assertIn("[Connect your WooCommerce store](docs/onboarding.md)", readme)
        self.assertIn("[How this skill stays safe](docs/safety_model.md)", readme)
        self.assertIn("[Browse all WooCommerce docs](docs/README.md)", readme)
        self.assertNotIn("- `docs/use_cases.md`", readme)
        self.assertNotIn("Why this beats a quick one-off script", use_cases)
        self.assertIn("WooCommerce work usually means checking a live store", use_cases)
        self.assertIn("payment gateways", use_cases)
