from __future__ import annotations

import unittest
from pathlib import Path


class TestReadmePublicContract(unittest.TestCase):
    def test_public_readme_opening_stays_user_facing(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "README.md").read_text(encoding="utf-8")

        self.assertTrue(text.startswith("# Google Merchant Center\n"))
        self.assertNotIn("## Simplicity lock", text)
        self.assertNotIn("# Google Merchant API Safe Agent CLI", text)
        self.assertIn("Google Merchant Center is where product data", text)
        for stale_phrase in [
            "Use this skill when",
            "You can hand your agent jobs like",
            "without guessing from raw docs",
            "Read work stays simple",
            "Riskier work slows down on purpose",
        ]:
            self.assertNotIn(stale_phrase, text)

        required_sections = [
            "## Start here first",
            "## What this skill helps with",
            "## Install and first run",
            "## How this skill stays safe",
            "## What happens before live changes",
        ]
        for section in required_sections:
            self.assertIn(section, text)

    def test_helpful_docs_stay_human_facing(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "README.md").read_text(encoding="utf-8")

        self.assertIn("## Helpful docs", text)
        self.assertIn("[Browse all Google Merchant docs](docs/README.md)", text)
        self.assertIn("[Command guide](docs/command_reference.md)", text)
        self.assertIn("[Proof and verification](docs/proof.md)", text)
        self.assertNotIn("- `docs/use_cases.md`", text)
        self.assertNotIn("- `docs/onboarding.md`", text)

    def test_start_here_section_stays_human_facing(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "README.md").read_text(encoding="utf-8")

        self.assertIn("## Start here first", text)
        self.assertIn("[What you can do with Google Merchant Center](docs/use_cases.md)", text)
        self.assertIn("[Connect your Google Merchant Center account](docs/onboarding.md)", text)
        self.assertIn("[How this skill stays safe](docs/safety_model.md)", text)
        self.assertIn("[Quickstart](docs/quickstart.md)", text)
        self.assertIn("[Command guide](docs/command_reference.md)", text)

    def test_quickstart_opens_with_human_links(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "docs" / "quickstart.md").read_text(encoding="utf-8")

        self.assertIn("[What you can do](use_cases.md)", text)
        self.assertIn("[Connect your Google Merchant Center account](onboarding.md)", text)
        self.assertIn("[How this skill stays safe](safety_model.md)", text)
        self.assertIn("--plan-out plan.json", text)
        self.assertIn("--ack-no-snapshot", text)
        self.assertNotIn("`use_cases.md`", text)
        self.assertNotIn("`onboarding.md`", text)

    def test_use_cases_stay_specific_and_human(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "docs" / "use_cases.md").read_text(encoding="utf-8")

        self.assertIn("Merchant work is usually about finding catalog problems", text)
        self.assertIn("## Good jobs to give the agent", text)
        self.assertIn("## What the agent should show you", text)
        self.assertNotIn("Why this skill is more useful than raw docs", text)
        self.assertNotIn("What this skill intentionally does not promise", text)
