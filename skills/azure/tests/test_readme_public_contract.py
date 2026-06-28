from __future__ import annotations

import unittest
from pathlib import Path


class TestReadmePublicContract(unittest.TestCase):
    def _root(self) -> Path:
        return Path(__file__).resolve().parents[1]

    def _readme(self) -> str:
        return (self._root() / "README.md").read_text(encoding="utf-8")

    def _opening(self) -> str:
        return self._readme().split("## Start here first", 1)[0]

    def _prose_paragraphs(self, opening: str) -> list[str]:
        paragraphs: list[str] = []
        for block in opening.split("\n\n"):
            block = block.strip()
            if not block or block.startswith("# ") or block.startswith("**Capability:**"):
                continue
            paragraphs.append(block)
        return paragraphs

    def test_readme_first_screen_gate_stays_short_and_useful(self) -> None:
        opening = self._opening()
        paragraphs = self._prose_paragraphs(opening)

        self.assertLessEqual(len(opening.split()), 290, "README first-screen gate: opening is too long")
        self.assertLessEqual(len(paragraphs), 4, "README first-screen gate: use at most 4 short prose paragraphs")
        self.assertIn("A good first ask is:", opening)
        self.assertIn("Azure", opening)

        first_ask = opening.split("A good first ask is:", 1)[1].splitlines()[0]
        self.assertLessEqual(len(first_ask.split()), 35, "first ask should be short enough to copy")

        comma_heavy_sentences = [
            sentence.strip()
            for sentence in opening.replace("\n", " ").split(".")
            if sentence.count(",") >= 5
        ]
        self.assertEqual([], comma_heavy_sentences, "opening should not read like an inventory dump")

    def test_public_readme_opening_avoids_jargon_and_flag_talk(self) -> None:
        opening = self._opening()

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
            "generated inventory",
            "coverage count",
            "operation count",
            "command surface",
            "api surface",
        ]
        for snippet in banned_opening_snippets:
            self.assertNotIn(snippet, opening.lower())

        self.assertNotIn("`", opening)
        self.assertNotIn("--", opening)

    def test_public_readme_opening_stays_user_facing(self) -> None:
        text = self._readme()

        self.assertTrue(text.startswith("# Azure\n"))
        self.assertNotIn("## Simplicity lock", text)
        self.assertNotIn("# qwayk-azure-safe-agent-cli", text)

        required_sections = [
            "## Start here first",
            "## What this skill helps with",
            "## Why this skill is different",
            "## What access this skill needs",
            "## Install and first run",
            "## How this skill stays safe",
            "## What it covers today",
            "## What happens before live changes",
            "## What proof it leaves behind",
            "## Limits",
        ]
        for section in required_sections:
            self.assertIn(section, text)

        opening = self._opening()
        self.assertIn("A good first ask is:", opening)
        self.assertIn("subscription", opening)

    def test_opening_says_what_user_can_do(self) -> None:
        opening = self._opening().lower()

        for phrase in [
            "map what is running",
            "find public exposure",
            "review broad role assignments",
            "check storage or network risk",
            "flag expensive resources",
            "prepare careful change plans",
        ]:
            self.assertIn(phrase, opening)

    def test_opening_explains_safe_skill_value(self) -> None:
        opening = self._opening().lower()

        self.assertIn("safe skill", opening)
        self.assertIn("generic agent", opening)
        self.assertIn("explicit commands", opening)
        self.assertIn("reads first", opening)
        self.assertIn("plans before writes", opening)
        self.assertIn("receipts", opening)

    def test_difference_section_explains_safe_skill_value(self) -> None:
        text = self._readme()
        section = text.split("## Why this skill is different", 1)[1].split("## What access this skill needs", 1)[0].lower()

        self.assertIn("generic api", section)
        self.assertIn("named commands", section)
        self.assertIn("starts with reads", section)
        self.assertIn("plans before writes", section)
        self.assertIn("receipts", section)

    def test_skill_wrapper_opening_stays_user_facing(self) -> None:
        text = (self._root() / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("# Skill: Azure", text)
        self.assertIn("tenant and subscription", text)
        self.assertIn("Start with a safe read", text)
        self.assertIn("does not improvise Azure API calls", text)
        self.assertIn("explicit commands", text)
        self.assertNotIn("# azure-safe-cli", text)
        self.assertNotIn("Safe Azure reads and controlled writes", text)

    def test_helpful_docs_stay_human_facing(self) -> None:
        text = self._readme()

        self.assertIn("## Helpful docs", text)
        self.assertIn("[Browse all docs](docs/README.md)", text)
        self.assertIn("[Command guide](docs/command_reference.md)", text)
        self.assertIn("[Proof and verification](docs/proof.md)", text)
        self.assertNotIn("- `docs/use_cases.md`", text)
        self.assertNotIn("- `docs/onboarding.md`", text)

    def test_start_here_section_stays_human_facing(self) -> None:
        text = self._readme()

        self.assertIn("## Start here first", text)
        self.assertIn("[What this skill can help you do](docs/use_cases.md)", text)
        self.assertIn("[Set up your account step by step](docs/onboarding.md)", text)
        self.assertIn("[See how this skill keeps changes safe](docs/safety_model.md)", text)
        self.assertIn("[Quickstart](docs/quickstart.md)", text)
        self.assertIn("[Command guide](docs/command_reference.md)", text)

    def test_quickstart_opens_with_human_links(self) -> None:
        text = (self._root() / "docs" / "quickstart.md").read_text(encoding="utf-8")
        opening = text.split("## ", 1)[0].lower()

        self.assertIn("Start by asking the agent to list Azure resource groups", text)
        self.assertIn("[What this skill can help you do](use_cases.md)", text)
        self.assertIn("[Set up your account step by step](onboarding.md)", text)
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
