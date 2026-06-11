from __future__ import annotations

import unittest
from pathlib import Path


class TestReadmePublicContract(unittest.TestCase):
    def test_public_readme_opening_stays_user_facing(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "README.md").read_text(encoding="utf-8")

        self.assertTrue(text.startswith("# Skimlinks\n"))
        self.assertNotIn("## Simplicity lock", text)
        self.assertNotIn("# Skimlinks Safe CLI", text)
        self.assertIn("**Capability:** Read-only", text)

        required_sections = [
            "## Start here first",
            "## What this skill helps with",
            "## Install and first run",
            "## How this skill stays safe",
            "## Helpful docs",
        ]
        for section in required_sections:
            self.assertIn(section, text)

    def test_start_here_section_stays_human_facing(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "README.md").read_text(encoding="utf-8")

        self.assertIn("[What you can do with Skimlinks](docs/use_cases.md)", text)
        self.assertIn("[Connect your Skimlinks account](docs/onboarding.md)", text)
        self.assertIn("[How this skill stays safe](docs/safety_model.md)", text)
        self.assertIn("[Quickstart](docs/quickstart.md)", text)
        self.assertIn("[Command guide](docs/command_reference.md)", text)

    def test_helpful_docs_stay_human_facing(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "README.md").read_text(encoding="utf-8")

        self.assertIn("[Browse all Skimlinks docs](docs/README.md)", text)
        self.assertIn("[Authentication details](docs/authentication.md)", text)
        self.assertIn("[Configuration](docs/configuration.md)", text)
        self.assertIn("[Troubleshooting](docs/troubleshooting.md)", text)
        self.assertIn("[Proof and verification](docs/proof.md)", text)
        self.assertIn("[API coverage](docs/api_coverage.md)", text)
        self.assertNotIn("- `docs/use_cases.md`", text)
        self.assertNotIn("- `docs/onboarding.md`", text)

    def test_docs_index_stays_user_first(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "docs" / "README.md").read_text(encoding="utf-8")

        use_cases_idx = text.index("[What you can do with Skimlinks](use_cases.md)")
        onboarding_idx = text.index("[Connect your Skimlinks account](onboarding.md)")
        safety_idx = text.index("[How this skill stays safe](safety_model.md)")
        quickstart_idx = text.index("[Quickstart](quickstart.md)")
        command_idx = text.index("[Command reference](command_reference.md)")
        self.assertLess(use_cases_idx, onboarding_idx)
        self.assertLess(onboarding_idx, safety_idx)
        self.assertLess(safety_idx, quickstart_idx)
        self.assertLess(quickstart_idx, command_idx)

    def test_quickstart_opens_with_human_links(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "docs" / "quickstart.md").read_text(encoding="utf-8")

        self.assertIn("[What you can do with Skimlinks](use_cases.md)", text)
        self.assertIn("[Connect your Skimlinks account](onboarding.md)", text)
        self.assertIn("[How this skill stays safe](safety_model.md)", text)
        self.assertNotIn("`docs/use_cases.md`", text)
        self.assertNotIn("`docs/onboarding.md`", text)
