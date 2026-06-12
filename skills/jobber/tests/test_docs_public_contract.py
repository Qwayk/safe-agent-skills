from __future__ import annotations

import re
import unittest
from pathlib import Path

from jobber_safe_agent_cli.commands.common import mutation_requires_ack_irreversible, mutation_requires_no_snapshot


class TestDocsPublicContract(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(__file__).resolve().parents[1]
        self.docs = self.root / "docs"

    def _read(self, name: str) -> str:
        return (self.docs / name).read_text(encoding="utf-8")

    def test_docs_home_groups_the_user_path_clearly(self) -> None:
        text = self._read("README.md")

        self.assertIn("## Start here", text)
        self.assertIn("## If you want commands", text)
        self.assertIn("## If you want proof and deeper detail", text)
        self.assertIn("[What this skill can help you do](use_cases.md)", text)
        self.assertIn("[Set up your account step by step](onboarding.md)", text)
        self.assertNotIn("Start here first:\n- `docs/", text)

    def test_onboarding_stays_non_technical_up_front(self) -> None:
        text = self._read("onboarding.md")
        opening = text.split("## Step 1:", 1)[0]

        self.assertIn("This page helps you get the skill connected without learning the command list first.", text)
        self.assertIn("## What success looks like", text)
        self.assertIn("## Step 3: What to ask your AI agent (examples)", text)
        self.assertNotIn("qwayk-jobber-safe-agent-cli", opening)
        self.assertNotIn("--", opening)

    def test_use_cases_stays_plain_english(self) -> None:
        text = self._read("use_cases.md")

        self.assertIn("## Good first asks", text)
        self.assertIn("## What the agent should show you", text)
        self.assertNotIn("`qwayk-jobber-safe-agent-cli", text)
        self.assertNotIn("--apply", text)

    def test_safety_model_explains_meaning_before_mechanics(self) -> None:
        text = self._read("safety_model.md")
        opening = text.split("## What safe use looks like", 1)[0]

        self.assertIn("look first, think second, and change last", opening)
        self.assertNotIn("--apply", opening)
        self.assertNotIn("--yes", opening)
        self.assertNotIn(".state/runs", opening)

    def test_quickstart_and_command_reference_label_themselves_as_command_pages(self) -> None:
        quickstart = self._read("quickstart.md")
        command_reference = self._read("command_reference.md")

        self.assertIn("This page is for people who want the commands.", quickstart)
        self.assertIn("[What this skill can help you do](use_cases.md)", quickstart)
        self.assertIn("This is the full command list for people who want exact syntax.", command_reference)
        self.assertIn("[What this skill can help you do](use_cases.md)", command_reference)

    def test_proof_opens_with_reassurance(self) -> None:
        text = self._read("proof.md")

        self.assertIn("Most users will never need to run these commands themselves.", text)
        self.assertIn("You don’t need to run these commands yourself.", text)
        self.assertIn("## What this page proves", text)

    def test_front_door_openings_reject_stock_ai_phrases(self) -> None:
        banned = [
            "without guessing from raw docs",
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
        jobs = self._read("jobs_and_batches.md")

        self.assertIn("Authentication means", authentication)
        self.assertIn("Configuration means", configuration)
        self.assertIn("A CSV file is a simple spreadsheet-style file.", jobs)
        receipt_path = self.docs / "receipt_review_prompt.md"
        if receipt_path.exists():
            receipt = receipt_path.read_text(encoding="utf-8")
            self.assertIn("A receipt is the record of what the tool actually did.", receipt)

    def test_public_write_apply_examples_require_plan_in(self) -> None:
        roots = [
            self.root / "README.md",
            self.root / "docs",
            self.root / "examples",
            self.root / "skills",
        ]
        files: list[Path] = []
        for root in roots:
            if root.is_file():
                files.append(root)
            else:
                files.extend(path for path in root.rglob("*") if path.is_file() and path.suffix in {".md", ".json", ".csv"})

        bad_apply_lines: list[str] = []
        residue_lines: list[str] = []
        for path in files:
            text = path.read_text(encoding="utf-8")
            rel = path.relative_to(self.root)
            for line_no, line in enumerate(text.splitlines(), start=1):
                if "--apply --yes write" in line and "--plan-in" not in line:
                    bad_apply_lines.append(f"{rel}:{line_no}: {line}")
                if "read.ping" in line or "write.ping" in line:
                    residue_lines.append(f"{rel}:{line_no}: {line}")
        if bad_apply_lines:
            self.fail("Direct write apply examples found without --plan-in:\n" + "\n".join(bad_apply_lines))
        if residue_lines:
            self.fail("Local ping job residue found in public files:\n" + "\n".join(residue_lines))

    def test_public_docs_do_not_show_high_risk_apply_without_ack_no_snapshot(self) -> None:
        roots = [
            self.root / "README.md",
            self.root / "docs",
            self.root / "examples",
            self.root / "skills",
        ]
        files: list[Path] = []
        for root in roots:
            if root.is_file():
                files.append(root)
            else:
                files.extend(path for path in root.rglob("*") if path.is_file() and path.suffix in {".md", ".json", ".csv"})

        bad_apply_lines: list[str] = []
        for path in files:
            text = path.read_text(encoding="utf-8")
            rel = path.relative_to(self.root)
            for line_no, line in enumerate(text.splitlines(), start=1):
                if "--apply" not in line or "--yes" not in line:
                    continue
                if "--ack-no-snapshot" in line:
                    continue
                match = re.search(r"\bwrite\s+([A-Za-z_][A-Za-z0-9_]*)", line)
                if not match:
                    continue
                if mutation_requires_no_snapshot(match.group(1)):
                    bad_apply_lines.append(f"{rel}:{line_no}: {line}")
        if bad_apply_lines:
            self.fail("High-risk write apply examples are missing --ack-no-snapshot:\n" + "\n".join(bad_apply_lines))

    def test_public_docs_do_not_show_irreversible_apply_without_ack_irreversible(self) -> None:
        roots = [
            self.root / "README.md",
            self.root / "docs",
            self.root / "examples",
            self.root / "skills",
        ]
        files: list[Path] = []
        for root in roots:
            if root.is_file():
                files.append(root)
            else:
                files.extend(path for path in root.rglob("*") if path.is_file() and path.suffix in {".md", ".json", ".csv"})

        bad_apply_lines: list[str] = []
        for path in files:
            text = path.read_text(encoding="utf-8")
            rel = path.relative_to(self.root)
            for line_no, line in enumerate(text.splitlines(), start=1):
                if "--apply" not in line or "--yes" not in line:
                    continue
                if "--ack-irreversible" in line:
                    continue
                match = re.search(r"\bwrite\s+([A-Za-z_][A-Za-z0-9_]*)", line)
                if not match:
                    continue
                if mutation_requires_ack_irreversible(match.group(1)):
                    bad_apply_lines.append(f"{rel}:{line_no}: {line}")
        if bad_apply_lines:
            self.fail("Irreversible write apply examples are missing --ack-irreversible:\n" + "\n".join(bad_apply_lines))
