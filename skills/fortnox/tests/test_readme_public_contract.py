from __future__ import annotations

import unittest
from pathlib import Path

README_REQUIRED_SECTIONS = [
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

PUBLIC_FACING_FILES = [
    "README.md",
    "docs/README.md",
    "docs/use_cases.md",
    "docs/onboarding.md",
    "docs/quickstart.md",
    "docs/proof.md",
    "SKILL.md",
]


class TestReadmePublicContract(unittest.TestCase):
    def _read(self, relative: str) -> str:
        root = Path(__file__).resolve().parents[1]
        return (root / relative).read_text(encoding="utf-8")

    def test_readme_matches_required_public_contract(self) -> None:
        text = self._read("README.md")

        self.assertTrue(text.startswith("# Fortnox\n"))
        self.assertIn("A good first ask is:", text)
        self.assertIn("Install slug: `fortnox`", text)
        self.assertIn("npx skills add Qwayk/safe-agent-skills@fortnox -g -y", text)
        self.assertIn("[What you can ask the Fortnox skill to do](docs/use_cases.md)", text)
        self.assertIn("[Set up your Fortnox connection step by step](docs/onboarding.md)", text)
        self.assertIn("[Read the Fortnox safety guide](docs/safety_model.md)", text)
        self.assertIn("[Do the first Fortnox check](docs/quickstart.md)", text)
        self.assertIn("[Open the technical command guide](docs/command_reference.md)", text)
        self.assertIn("[Browse all Fortnox docs](docs/README.md)", text)
        self.assertIn("[See proof and verification](docs/proof.md)", text)
        self.assertIn("[Inspect the full API coverage ledger](docs/api_coverage.md)", text)
        self.assertNotIn("skills_wrappers", text)

        positions = []
        for section in README_REQUIRED_SECTIONS:
            self.assertIn(section, text)
            positions.append(text.index(section))
        self.assertEqual(positions, sorted(positions))

        banned = [
            "active build",
            "foundational slices",
            "shipped surface now includes",
            "template",
            "demo",
        ]
        lowered = text.lower()
        for phrase in banned:
            self.assertNotIn(phrase, lowered)

    def test_public_facing_files_do_not_link_source_only_wrapper_docs(self) -> None:
        for relative in PUBLIC_FACING_FILES:
            with self.subTest(relative=relative):
                self.assertNotIn("skills_wrappers", self._read(relative))

    def test_quickstart_stays_conservative(self) -> None:
        text = self._read("docs/quickstart.md")

        self.assertIn("[Set up your Fortnox connection step by step](onboarding.md)", text)
        self.assertIn("[What you can ask the Fortnox skill to do](use_cases.md)", text)
        self.assertIn("fortnox-api-tool company-information get", text)
        self.assertIn("fortnox-api-tool customers list", text)
        self.assertIn("fortnox-api-tool suppliers list", text)
        self.assertIn("fortnox-api-tool invoices list", text)
        self.assertIn("--plan-out invoice-accrual.plan.json", text)
        self.assertIn("jobs run", text)
        self.assertNotIn("--apply --yes", text)
        self.assertNotIn("--ack-no-snapshot", text)
        self.assertNotIn("--ack-irreversible", text)

    def test_safety_model_mentions_apply_flags(self) -> None:
        text = self._read("docs/safety_model.md")

        self.assertIn("`--apply --yes --plan-in`", text)
        self.assertIn("`--ack-no-snapshot`", text)
        self.assertIn("`--ack-irreversible`", text)
        self.assertIn("jobs run", text)

    def test_public_skill_wrapper_is_real(self) -> None:
        skill = self._read("SKILL.md")

        self.assertIn("name: fortnox", skill)
        self.assertTrue(skill.startswith("---\n"))
        self.assertIn("**Capability:** Reads + careful changes", skill)
        self.assertIn("`--apply --yes --plan-in`", skill)
        self.assertIn("`--ack-no-snapshot`", skill)
        self.assertIn("`--ack-irreversible`", skill)
        self.assertIn("jobs run", skill)
        self.assertNotIn("skills_wrappers", skill)
