from __future__ import annotations

import unittest
from pathlib import Path


class TestReadmePublicContract(unittest.TestCase):
    def test_public_readme_opening_stays_user_facing(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "README.md").read_text(encoding="utf-8")

        self.assertTrue(text.startswith("# Cloudflare\n"))
        self.assertNotIn("# cloudflare-api-tool", text)
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

        self.assertIn("[What you can do with Cloudflare](docs/use_cases.md)", text)
        self.assertIn("[Connect your Cloudflare account](docs/onboarding.md)", text)
        self.assertIn("[How this skill stays safe](docs/safety_model.md)", text)
        self.assertIn("[Quickstart](docs/quickstart.md)", text)
        self.assertIn("[Command guide](docs/command_reference.md)", text)

    def test_helpful_docs_stay_human_facing(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "README.md").read_text(encoding="utf-8")

        self.assertIn("[Browse all Cloudflare docs](docs/README.md)", text)
        self.assertIn("[Proof and verification](docs/proof.md)", text)
        self.assertIn("[Live official coverage ledger](docs/api_coverage_live_official.md)", text)
        self.assertNotIn("- `docs/onboarding.md`", text)
        self.assertNotIn("- `docs/proof.md`", text)
