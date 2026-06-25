from __future__ import annotations

import unittest
from pathlib import Path


class TestDocsPublicContract(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(__file__).resolve().parents[1]
        self.docs = self.root / "docs"

    def _read(self, name: str) -> str:
        return (self.docs / name).read_text(encoding="utf-8")

    def test_docs_home_groups_the_user_path_clearly(self) -> None:
        text = self._read("README.md")

        self.assertIn("start with the real job", text)
        self.assertIn("These docs explain how to", text)
        self.assertIn("## Start with the work", text)
        self.assertIn("## Commands, setup, and fixes", text)
        self.assertIn("## Proof and details", text)
        self.assertIn("[Good first asks](use_cases.md)", text)
        self.assertIn("[Set up your account step by step](onboarding.md)", text)
        self.assertIn("[Official sources used](references.md)", text)
        self.assertNotIn("[Engineering notes]", text)
        self.assertNotIn("[Plan review prompt]", text)
        self.assertNotIn("Start here first:\n- `docs/", text)

    def test_onboarding_stays_non_technical_up_front(self) -> None:
        text = self._read("onboarding.md")
        opening = text.split("## Step 1:", 1)[0]

        self.assertTrue(text.startswith("# Connect your Contentsquare account\n"))
        self.assertIn("You do not need to learn every command first.", text)
        self.assertIn("Keep the setup files private.", text)
        self.assertIn("## What success looks like", text)
        self.assertIn("## Step 4: What to ask your AI agent", text)
        self.assertNotIn("contentsquare-safe-cli", opening)
        self.assertNotIn("--", opening)

    def test_use_cases_stays_plain_english(self) -> None:
        text = self._read("use_cases.md")

        self.assertIn("## Good first asks", text)
        self.assertIn("## What to expect back", text)
        self.assertNotIn("`contentsquare-safe-cli", text)
        self.assertNotIn("--apply", text)

    def test_safety_model_explains_meaning_before_mechanics(self) -> None:
        text = self._read("safety_model.md")
        opening = text.split("## Read-only work", 1)[0]

        self.assertIn("look first, review second, change last", opening)
        self.assertNotIn("--apply", opening)
        self.assertNotIn("--yes", opening)
        self.assertNotIn(".state/runs", opening)

    def test_quickstart_and_command_reference_label_themselves_without_meta_page_talk(self) -> None:
        quickstart = self._read("quickstart.md")
        command_reference = self._read("command_reference.md")
        opening = quickstart.split("## ", 1)[0].lower()

        self.assertIn("Start by checking the Contentsquare OAuth connection", quickstart)
        self.assertIn("[good first asks](use_cases.md)", quickstart)
        self.assertTrue(command_reference.startswith("# Command reference\n"))
        self.assertIn("For the guided path, start with", command_reference)

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

    def test_proof_opens_with_reassurance(self) -> None:
        text = self._read("proof.md")

        self.assertIn("what has actually been checked", text)
        self.assertIn("If you only check one thing,", text)
        self.assertIn("## What this page proves", text)
        self.assertIn("## Smoke checks", text)
        self.assertIn("## What still needs live credentials", text)
        self.assertIn("## What can go wrong", text)
        self.assertNotIn("build session", text)
        self.assertNotIn("request-shape repair", text)

    def test_front_door_openings_reject_stock_ai_phrases(self) -> None:
        banned = [
            "without guessing from raw docs",
            "without turning",
            "full command manual",
            "this page helps",
            "if you are still deciding",
            "run one safe read that proves",
            "stays simple",
            "slows down on purpose",
            "real product work",
            "vibe coders",
            "purpose:",
            "rules:",
            "this template supports",
        ]
        targets = [
            "README.md",
            "onboarding.md",
            "quickstart.md",
            "command_reference.md",
            "safety_model.md",
            "use_cases.md",
            "proof.md",
        ]

        for name in targets:
            text = self._read(name)
            opening = text.split("## ", 1)[0].lower()
            for phrase in banned:
                self.assertNotIn(phrase, opening, msg=f"{name} opening contains banned phrase: {phrase}")

    def test_all_docs_open_like_help_pages(self) -> None:
        banned_opening_bits = [
            "purpose:",
            "rules:",
            "goal:",
            "this template supports",
            "layers:",
        ]

        for path in sorted(self.docs.glob("*.md")):
            text = path.read_text(encoding="utf-8")
            opening = text.split("## ", 1)[0].lower()
            for phrase in banned_opening_bits:
                self.assertNotIn(phrase, opening, msg=f"{path.name} opens with cold builder phrasing: {phrase}")

    def test_support_docs_explain_technical_words_in_plain_language(self) -> None:
        authentication = self._read("authentication.md")
        configuration = self._read("configuration.md")
        troubleshooting = self._read("troubleshooting.md")

        self.assertIn("In plain English", authentication)
        self.assertIn(".env", configuration)
        self.assertIn("Nothing changed in Contentsquare when auth setup fails.", troubleshooting)
