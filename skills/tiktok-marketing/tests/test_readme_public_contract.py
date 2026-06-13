from __future__ import annotations

import unittest
from pathlib import Path


class TestReadmePublicContract(unittest.TestCase):
    def test_public_readme_opening_stays_user_facing(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "README.md").read_text(encoding="utf-8")

        self.assertTrue(text.startswith("# TikTok Marketing\n"))
        self.assertNotIn("## Simplicity lock", text)
        self.assertNotIn("# tiktok-marketing-api-tool", text)
        self.assertIn("**Capability:** Reads + careful changes", text)
        self.assertIn("TikTok Marketing is where campaign setup", text)
        for stale_phrase in [
            "Use this skill when",
            "You can hand your agent jobs like",
            "without guessing from raw docs",
            "Read work stays explicit",
            "Riskier work slows down on purpose",
        ]:
            self.assertNotIn(stale_phrase, text)

        required_sections = [
            "## Start here first",
            "## What this skill helps with",
            "## Install and first run",
            "## How this skill stays safe",
            "## What happens before live changes",
            "## Helpful docs",
        ]
        for section in required_sections:
            self.assertIn(section, text)

    def test_start_here_section_stays_human_facing(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "README.md").read_text(encoding="utf-8")

        self.assertIn("[What you can do with TikTok Marketing](docs/use_cases.md)", text)
        self.assertIn("[Connect your TikTok Marketing account](docs/onboarding.md)", text)
        self.assertIn("[How this skill stays safe](docs/safety_model.md)", text)
        self.assertIn("[Quickstart](docs/quickstart.md)", text)
        self.assertIn("[Command guide](docs/command_reference.md)", text)

    def test_helpful_docs_stay_human_facing(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "README.md").read_text(encoding="utf-8")

        self.assertIn("[Browse all TikTok Marketing docs](docs/README.md)", text)
        self.assertIn("[Authentication details](docs/authentication.md)", text)
        self.assertIn("[Proof and verification](docs/proof.md)", text)
        self.assertIn("[API coverage](docs/api_coverage.md)", text)
        self.assertNotIn("- `docs/use_cases.md`", text)
        self.assertNotIn("- `docs/onboarding.md`", text)

    def test_quickstart_opens_with_human_links(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "docs" / "quickstart.md").read_text(encoding="utf-8")

        self.assertIn("[What you can do with TikTok Marketing](use_cases.md)", text)
        self.assertIn("[Connect your TikTok Marketing account](onboarding.md)", text)
        self.assertIn("[How this skill stays safe](safety_model.md)", text)
        self.assertNotIn("`use_cases.md`", text)
        self.assertNotIn("`onboarding.md`", text)

    def test_use_cases_stay_specific_and_human(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "docs" / "use_cases.md").read_text(encoding="utf-8")

        self.assertIn("# What you can do with TikTok Marketing", text)
        self.assertIn("Auth and advertiser access", text)
        self.assertIn("Campaign, ad, and creative review", text)
        self.assertIn("Reports, uploads, and pinned operations", text)
        self.assertIn("## What the agent should show you", text)
        self.assertIn("Good first TikTok Marketing path", text)
        self.assertNotIn("Why this skill is useful", text)
        self.assertNotIn("raw API guessing", text)
