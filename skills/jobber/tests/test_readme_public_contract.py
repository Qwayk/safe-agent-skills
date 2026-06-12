from __future__ import annotations

import unittest
from pathlib import Path


class TestReadmePublicContract(unittest.TestCase):
    def test_public_readme_opening_avoids_jargon_and_flag_talk(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "README.md").read_text(encoding="utf-8")
        opening = text.split("## Start here first", 1)[0]

        banned_opening_snippets = [
            "raw docs",
            "raw vendor docs",
            "documentation",
            "docs",
            "--live",
            "--apply",
            "--yes",
            "--ack",
            "no-snapshot",
            "before-state",
            "raw request bridge",
            "pinned to the official manifest",
            "shipped api surface",
            "real product work",
            "stays simple",
            "slows down on purpose",
            "when the real tool supports them",
        ]
        for snippet in banned_opening_snippets:
            self.assertNotIn(snippet, opening.lower())

        self.assertNotIn("`", opening)
        self.assertNotIn("--", opening)

    def test_public_readme_opening_stays_user_facing(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "README.md").read_text(encoding="utf-8")

        self.assertTrue(text.startswith("# Jobber Safe CLI\n"))
        self.assertNotIn("## Simplicity lock", text)
        self.assertNotIn("# qwayk-jobber-safe-agent-cli", text)

        required_sections = [
            "## Start here first",
            "## What this skill helps with",
            "## Install and first run",
            "## How this skill stays safe",
            "## What happens before live changes",
        ]
        for section in required_sections:
            self.assertIn(section, text)

        opening = text.split("## Start here first", 1)[0]
        self.assertIn("A good first ask is:", opening)
        self.assertIn("You can ask for things like", opening)

    def test_helpful_docs_stay_human_facing(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "README.md").read_text(encoding="utf-8")

        self.assertIn("## Helpful docs", text)
        self.assertIn("[Browse all docs](docs/README.md)", text)
        self.assertIn("[Command guide](docs/command_reference.md)", text)
        self.assertIn("[Proof and verification](docs/proof.md)", text)
        self.assertNotIn("- `docs/use_cases.md`", text)
        self.assertNotIn("- `docs/onboarding.md`", text)

    def test_start_here_section_stays_human_facing(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "README.md").read_text(encoding="utf-8")

        self.assertIn("## Start here first", text)
        self.assertIn("[What this skill can help you do](docs/use_cases.md)", text)
        self.assertIn("[Set up your account step by step](docs/onboarding.md)", text)
        self.assertIn("[See how this skill keeps changes safe](docs/safety_model.md)", text)
        self.assertIn("[Quickstart](docs/quickstart.md)", text)
        self.assertIn("[Command guide](docs/command_reference.md)", text)

    def test_quickstart_opens_with_human_links(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "docs" / "quickstart.md").read_text(encoding="utf-8")

        self.assertIn("[What this skill can help you do](use_cases.md)", text)
        self.assertIn("[Set up your account step by step](onboarding.md)", text)
        self.assertNotIn("`docs/use_cases.md`", text)
        self.assertNotIn("`docs/onboarding.md`", text)
