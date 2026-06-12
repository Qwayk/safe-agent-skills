from __future__ import annotations

import unittest
from pathlib import Path


class TestReadmePublicContract(unittest.TestCase):
    def test_public_readme_opening_stays_user_facing(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "README.md").read_text(encoding="utf-8")

        self.assertTrue(text.startswith("# Hacker News\n"))
        self.assertIn("**Capability:** Read-only", text)
        self.assertNotIn("## Simplicity lock", text)
        self.assertNotIn("# hacker-news-api-tool", text)

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
            with self.subTest(section=section):
                self.assertIn(section, text)

    def test_start_here_section_stays_human_facing(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "README.md").read_text(encoding="utf-8")

        self.assertIn("[What you can do with Hacker News](docs/use_cases.md)", text)
        self.assertIn("[Use Hacker News with no account](docs/onboarding.md)", text)
        self.assertIn("[How this skill stays safe](docs/safety_model.md)", text)
        self.assertIn("[Quickstart](docs/quickstart.md)", text)
        self.assertIn("[Command guide](docs/command_reference.md)", text)
        self.assertNotIn("- `docs/use_cases.md`", text)
        self.assertNotIn("- `docs/onboarding.md`", text)

    def test_helpful_docs_stay_human_facing(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "README.md").read_text(encoding="utf-8")

        self.assertIn("[Browse all Hacker News docs](docs/README.md)", text)
        self.assertIn("[Authentication details](docs/authentication.md)", text)
        self.assertIn("[Troubleshooting](docs/troubleshooting.md)", text)
        self.assertIn("[Proof and verification](docs/proof.md)", text)
        self.assertIn("[API coverage](docs/api_coverage.md)", text)

    def test_quickstart_opens_with_human_links(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "docs" / "quickstart.md").read_text(encoding="utf-8")

        self.assertIn("[What you can do with Hacker News](use_cases.md)", text)
        self.assertIn("[Use Hacker News with no account](onboarding.md)", text)
        self.assertIn("[How this skill stays safe](safety_model.md)", text)
        self.assertNotIn("`use_cases.md`", text)
        self.assertNotIn("`onboarding.md`", text)
