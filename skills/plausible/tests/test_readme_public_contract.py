from __future__ import annotations

import unittest
from pathlib import Path


class TestReadmePublicContract(unittest.TestCase):
    def test_public_readme_opening_stays_user_facing(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "README.md").read_text(encoding="utf-8")

        self.assertTrue(text.startswith("# Plausible\n"))
        self.assertNotIn("## Simplicity lock", text)
        self.assertNotIn("# plausible-api-tool", text)
        self.assertIn("Plausible is useful when you want privacy-friendly", text)
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
        self.assertIn("[Browse all Plausible docs](docs/README.md)", text)
        self.assertIn("[Command guide](docs/command_reference.md)", text)
        self.assertIn("[Proof and verification](docs/proof.md)", text)
        self.assertNotIn("- `docs/use_cases.md`", text)
        self.assertNotIn("- `docs/onboarding.md`", text)

    def test_start_here_section_stays_human_facing(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "README.md").read_text(encoding="utf-8")

        self.assertIn("## Start here first", text)
        self.assertIn("[What you can do with Plausible](docs/use_cases.md)", text)
        self.assertIn("[Connect your Plausible account](docs/onboarding.md)", text)
        self.assertIn("[How this skill stays safe](docs/safety_model.md)", text)
        self.assertIn("[Quickstart](docs/quickstart.md)", text)
        self.assertIn("[Command guide](docs/command_reference.md)", text)

    def test_quickstart_opens_with_human_links(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "docs" / "quickstart.md").read_text(encoding="utf-8")

        self.assertIn("[What you can do](use_cases.md)", text)
        self.assertIn("[Connect your account](onboarding.md)", text)
        self.assertNotIn("`docs/use_cases.md`", text)
        self.assertNotIn("`docs/onboarding.md`", text)

    def test_use_cases_stay_specific_and_human(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "docs" / "use_cases.md").read_text(encoding="utf-8")

        self.assertIn("Plausible work is usually about answering a simple business question", text)
        self.assertIn("## Good jobs to give the agent", text)
        self.assertIn("## What the agent should show you", text)
        self.assertNotIn("Why this is powerful", text)
        self.assertNotIn("Common use cases", text)
