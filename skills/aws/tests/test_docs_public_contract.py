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

        self.assertIn("## Start with the work", text)
        self.assertIn("## Commands, setup, and fixes", text)
        self.assertIn("## Proof and details", text)
        self.assertIn("[What you can do with AWS](use_cases.md)", text)
        self.assertIn("[Set up AWS access locally](onboarding.md)", text)
        self.assertIn("[Proof and verification](proof.md)", text)
        self.assertNotIn("Start here first:\n- `docs/", text)

    def test_onboarding_stays_non_technical_up_front(self) -> None:
        text = self._read("onboarding.md")
        opening = text.split("## Step 1:", 1)[0]

        self.assertIn("Set up the local AWS identity first, then ask for one safe read.", text)
        self.assertIn("You do not need to learn the command line first", text)
        self.assertIn("## What to ask your AI agent (examples)", text)
        self.assertIn("## What success looks like", text)
        self.assertNotIn("qwayk-aws-safe-agent-cli", opening)
        self.assertNotIn("--", opening)

    def test_use_cases_stays_plain_english(self) -> None:
        text = self._read("use_cases.md")

        self.assertIn("## Good first asks", text)
        self.assertIn("## Safe review jobs", text)
        self.assertIn("## Review-first change jobs", text)
        self.assertIn("## What you should get back", text)
        self.assertIn("## When not to use it", text)
        self.assertIn("which account will this touch", text)
        self.assertNotIn("`qwayk-aws-safe-agent-cli", text)
        self.assertNotIn("--apply", text)

    def test_safety_model_explains_meaning_before_mechanics(self) -> None:
        text = self._read("safety_model.md")
        opening = text.split("## What safe use looks like", 1)[0]

        self.assertIn(
            "AWS changes are safer when the tool checks identity first, writes a plan second, and keeps a receipt last.",
            opening,
        )
        self.assertNotIn("--apply", opening)
        self.assertNotIn("--yes", opening)
        self.assertNotIn(".state/runs", opening)

    def test_quickstart_and_command_reference_label_themselves_without_meta_page_talk(self) -> None:
        quickstart = self._read("quickstart.md")
        command_reference = self._read("command_reference.md")
        opening = quickstart.split("## ", 1)[0].lower()

        self.assertIn("The first useful result is to confirm which AWS identity the tool is actually using.", quickstart)
        self.assertIn("[What the tool helps you do](use_cases.md)", quickstart)
        self.assertIn("[Set up AWS access locally](onboarding.md)", quickstart)
        self.assertIn("This is the exact command list for the AWS tool.", command_reference)
        self.assertIn("[Read the safety model](safety_model.md)", command_reference)

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

        self.assertIn("Most users do not need to run these checks every day.", text)
        self.assertIn("No live AWS writes were run during local validation.", text)
        self.assertIn("## What this page proves", text)

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
            "example skill",
            "example-skill",
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
        jobs = self._read("jobs_and_batches.md")
        proof = self._read("proof.md")

        self.assertIn("Authentication means", authentication)
        self.assertIn("Configuration means", configuration)
        self.assertIn("This AWS tool does not ship a separate background worker.", jobs)
        self.assertIn("A receipt with `verification.status: limited`", proof)

    def test_docs_reject_template_placeholders(self) -> None:
        banned = [
            "Example Skill",
            "example-skill",
            "<REPLACE_ME>",
            "<YYYY-MM-DD>",
            "After copying this template",
            "This template",
            "api.example.com",
            "demo write",
            "demo read",
        ]
        for path in sorted(self.docs.glob("*.md")):
            text = path.read_text(encoding="utf-8")
            lower = text.lower()
            for phrase in banned:
                self.assertNotIn(phrase.lower(), lower, msg=f"{path.name} still contains placeholder text: {phrase}")
