from __future__ import annotations

import unittest
from pathlib import Path


class TestReadmePublicContract(unittest.TestCase):
    def test_public_readme_opening_stays_user_facing(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "README.md").read_text(encoding="utf-8")

        self.assertTrue(text.startswith("# Meta Ads\n"))
        self.assertNotIn("## Simplicity lock", text)
        self.assertNotIn("# Meta Ads API tool (read-only)", text)
        self.assertIn("**Capability:** Read-only", text)

        required_sections = [
            "## Start here first",
            "## What this skill helps with",
            "## Install and first run",
            "## How this skill stays safe",
            "## What happens before a real change",
            "## Helpful docs",
        ]
        for section in required_sections:
            self.assertIn(section, text)

    def test_start_here_section_stays_human_facing(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "README.md").read_text(encoding="utf-8")

        self.assertIn("[What you can do with Meta Ads](docs/use_cases.md)", text)
        self.assertIn("[Connect your Meta Ads account](docs/onboarding.md)", text)
        self.assertIn("[How this skill stays safe](docs/safety_model.md)", text)
        self.assertIn("[Quickstart](docs/quickstart.md)", text)
        self.assertIn("[Command guide](docs/command_reference.md)", text)

    def test_helpful_docs_stay_human_facing(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "README.md").read_text(encoding="utf-8")

        self.assertIn("[Browse all Meta Ads docs](docs/README.md)", text)
        self.assertIn("[Media buyer quickstart](docs/media_buyer_quickstart.md)", text)
        self.assertIn("[Winning ads workbook](docs/winning_ads_workbook.md)", text)
        self.assertIn("[Snapshot export guide](docs/snapshot_export.md)", text)
        self.assertIn("[Proof and verification](docs/proof.md)", text)
        self.assertIn("[API coverage](docs/api_coverage.md)", text)
        self.assertNotIn("- `docs/use_cases.md`", text)
        self.assertNotIn("- `docs/onboarding.md`", text)

    def test_quickstart_opens_with_human_links(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "docs" / "quickstart.md").read_text(encoding="utf-8")

        self.assertIn("[What you can do with Meta Ads](use_cases.md)", text)
        self.assertIn("[Connect your Meta Ads account](onboarding.md)", text)
        self.assertIn("[How this skill stays safe](safety_model.md)", text)
        self.assertNotIn("- `docs/use_cases.md`", text)
        self.assertNotIn("- `docs/onboarding.md`", text)
