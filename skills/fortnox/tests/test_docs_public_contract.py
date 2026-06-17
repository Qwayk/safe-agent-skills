from __future__ import annotations

import unittest
from pathlib import Path

PUBLIC_FACING_FILES = [
    "README.md",
    "docs/README.md",
    "docs/use_cases.md",
    "docs/onboarding.md",
    "docs/quickstart.md",
    "docs/proof.md",
    "SKILL.md",
]


class TestDocsPublicContract(unittest.TestCase):
    def _read(self, relative: str) -> str:
        root = Path(__file__).resolve().parents[1]
        return (root / relative).read_text(encoding="utf-8")

    def test_docs_index_keeps_user_path_first(self) -> None:
        text = self._read("docs/README.md")
        self.assertIn("## Start with the work", text)
        self.assertIn("## Commands, setup, and fixes", text)
        self.assertIn("## Proof and details", text)
        self.assertIn("[What you can ask the Fortnox skill to do](use_cases.md)", text)
        self.assertIn("[Do the first safe Fortnox check](quickstart.md)", text)
        self.assertIn("[Set up your Fortnox connection step by step](onboarding.md)", text)
        self.assertIn("[Read the Fortnox safety guide](safety_model.md)", text)
        self.assertIn("[Open the technical command guide](command_reference.md)", text)
        self.assertIn("[See proof and verification](proof.md)", text)
        self.assertIn("[Inspect the full API coverage ledger](api_coverage.md)", text)
        self.assertNotIn("skills_wrappers", text)

    def test_quickstart_stays_first_run_safe(self) -> None:
        text = self._read("docs/quickstart.md")
        self.assertIn("fortnox-api-tool company-information get", text)
        self.assertIn("fortnox-api-tool customers list", text)
        self.assertIn("fortnox-api-tool suppliers list", text)
        self.assertIn("fortnox-api-tool invoices list", text)
        self.assertIn("--plan-out invoice-accrual.plan.json", text)
        self.assertIn("jobs run", text)
        self.assertIn("A good first ask is:", text)
        self.assertIn("## What you will do first", text)
        self.assertIn("## 3. Run one small first read", text)
        self.assertIn("## 4. Stop before anything risky", text)
        self.assertNotIn("--ack-no-snapshot", text)
        self.assertNotIn("--ack-irreversible", text)
        self.assertNotIn("--apply --yes", text)

    def test_onboarding_has_success_and_plain_english_examples(self) -> None:
        text = self._read("docs/onboarding.md")
        self.assertIn("## What success looks like", text)
        self.assertIn("## What to ask your AI agent (examples)", text)
        self.assertIn("FORTNOX_CLIENT_ID", text)
        self.assertIn("FORTNOX_CLIENT_SECRET", text)
        self.assertIn("FORTNOX_REDIRECT_URI", text)

    def test_use_cases_stay_non_technical(self) -> None:
        text = self._read("docs/use_cases.md")
        self.assertIn("## Good first asks", text)
        self.assertIn("## What you should expect back from the agent", text)
        self.assertIn("## Why this is better than a typical no-code automation", text)
        self.assertNotIn("fortnox-api-tool ", text)

    def test_public_facing_files_do_not_link_source_only_wrapper_docs(self) -> None:
        for relative in PUBLIC_FACING_FILES:
            with self.subTest(relative=relative):
                self.assertNotIn("skills_wrappers", self._read(relative))

    def test_proof_stays_honest_about_live_verification(self) -> None:
        text = self._read("docs/proof.md")
        self.assertTrue(text.startswith("# Proof and verification\n"))
        self.assertIn("live production checks remain honestly unverified here", text)

    def test_safety_docs_and_wrapper_align_on_core_flags(self) -> None:
        safety = self._read("docs/safety_model.md")
        skill = self._read("SKILL.md")

        for text in (safety, skill):
            self.assertIn("`--apply --yes --plan-in`", text)
            self.assertIn("`--ack-no-snapshot`", text)
            self.assertIn("`--ack-irreversible`", text)
            self.assertIn("jobs run", text)
