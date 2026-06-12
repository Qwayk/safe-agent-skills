from __future__ import annotations

import unittest
from pathlib import Path


class TestReadmePublicContract(unittest.TestCase):
    def test_public_readme_opening_stays_user_facing(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "README.md").read_text(encoding="utf-8")

        self.assertTrue(text.startswith("# Awin Advertiser\n"))
        self.assertNotIn("## Simplicity lock", text)
        self.assertNotIn("# Awin advertiser safe agent CLI", text)
        self.assertIn("**Capability:** Reads + careful changes", text)

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

        self.assertIn("[What you can do with Awin Advertiser](docs/use_cases.md)", text)
        self.assertIn("[Connect your Awin advertiser account](docs/onboarding.md)", text)
        self.assertIn("[How this skill stays safe](docs/safety_model.md)", text)
        self.assertIn("[Quickstart](docs/quickstart.md)", text)
        self.assertIn("[Command guide](docs/command_reference.md)", text)

    def test_opening_rejects_template_voice(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "README.md").read_text(encoding="utf-8")
        opening = text.split("## Start here first", 1)[0]

        banned = [
            "Use this skill when",
            "You can hand your agent jobs like",
            "without guessing from raw docs",
            "Read work stays explicit",
            "Riskier advertiser actions slow down on purpose",
        ]
        for phrase in banned:
            self.assertNotIn(phrase, opening)

    def test_helpful_docs_stay_human_facing(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "README.md").read_text(encoding="utf-8")

        self.assertIn("[Browse all Awin advertiser docs](docs/README.md)", text)
        self.assertIn("[Authentication details](docs/authentication.md)", text)
        self.assertIn("[Configuration](docs/configuration.md)", text)
        self.assertIn("[Proof and verification](docs/proof.md)", text)
        self.assertIn("[API coverage](docs/api_coverage.md)", text)
        self.assertNotIn("- `docs/use_cases.md`", text)
        self.assertNotIn("- `docs/onboarding.md`", text)

    def test_quickstart_opens_with_human_links(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "docs" / "quickstart.md").read_text(encoding="utf-8")

        self.assertIn("[What you can do with Awin Advertiser](use_cases.md)", text)
        self.assertIn("[Connect your Awin advertiser account](onboarding.md)", text)
        self.assertIn("[How this skill stays safe](safety_model.md)", text)
        self.assertNotIn("`docs/use_cases.md`", text)
        self.assertNotIn("`docs/onboarding.md`", text)
