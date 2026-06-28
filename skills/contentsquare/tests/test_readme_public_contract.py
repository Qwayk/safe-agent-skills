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
            "use this skill when",
            "use this when you want your agent",
            "you can hand your agent jobs like",
            "read public data safely",
            "safe by design",
            "when the real tool supports them",
            "source tool",
            "public admission",
            "public-live",
        ]
        for snippet in banned_opening_snippets:
            self.assertNotIn(snippet, opening.lower())

        self.assertNotIn("`", opening)
        self.assertNotIn("--", opening)

    def test_public_readme_opening_stays_user_facing(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "README.md").read_text(encoding="utf-8")

        self.assertTrue(text.startswith("# Contentsquare\n"))
        self.assertNotIn("## Simplicity lock", text)
        self.assertNotIn("# contentsquare-safe-cli", text)

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
        self.assertIn("Contentsquare is where teams check", opening)
        self.assertNotIn("Best for ", opening)
        self.assertNotIn("Not for ", opening)
        self.assertNotIn("Live Contentsquare account behavior has not been verified", opening)

    def test_helpful_docs_stay_human_facing(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "README.md").read_text(encoding="utf-8")

        self.assertIn("## Helpful docs", text)
        self.assertIn("[Browse all Contentsquare docs](docs/README.md)", text)
        self.assertIn("[Run the quickstart](docs/quickstart.md)", text)
        self.assertIn("[Command guide](docs/command_reference.md)", text)
        self.assertIn("[Proof and verification](docs/proof.md)", text)
        self.assertNotIn("[Official sources used](docs/references.md)", text)
        self.assertNotIn("- `docs/use_cases.md`", text)
        self.assertNotIn("- `docs/onboarding.md`", text)

    def test_start_here_section_stays_human_facing(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "README.md").read_text(encoding="utf-8")

        self.assertIn("## Start here first", text)
        self.assertIn("[See good first asks](docs/use_cases.md)", text)
        self.assertIn("[Set up your account step by step](docs/onboarding.md)", text)
        self.assertIn("[Understand the safety checks](docs/safety_model.md)", text)
        self.assertIn("[Run the first command](docs/quickstart.md)", text)
        self.assertIn("[Command guide](docs/command_reference.md)", text)

    def test_quickstart_opens_with_human_links(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "docs" / "quickstart.md").read_text(encoding="utf-8")
        opening = text.split("## ", 1)[0].lower()

        self.assertIn("Start by checking the Contentsquare OAuth connection", text)
        self.assertIn("[good first asks](use_cases.md)", text)
        self.assertIn("## What you will do first", text)
        self.assertIn("## 3. Run one small first read", text)
        self.assertIn("## 4. Stop before anything risky", text)
        self.assertIn("## What a useful first result includes", text)
        self.assertIn("## Where to go next", text)
        self.assertNotIn("`docs/use_cases.md`", text)
        self.assertNotIn("`docs/onboarding.md`", text)

        banned_opening_bits = [
            "this page helps",
            "this page is for",
            "without turning",
            "full command manual",
            "if you are still deciding",
            "run one safe read that proves",
        ]
        for phrase in banned_opening_bits:
            self.assertNotIn(phrase, opening)
