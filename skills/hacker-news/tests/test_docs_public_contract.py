from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestDocsPublicContract(unittest.TestCase):
    def _read(self, relative: str) -> str:
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_readme_opening_has_no_internal_setup_or_flag_talk(self) -> None:
        text = self._read("README.md")
        opening = text.split("## Start here first", 1)[0]

        forbidden = [
            "raw docs",
            "manifest",
            "before-state",
            "no-snapshot",
            "--live",
            "--apply",
            "--ack",
            "CLI",
            "bridge",
            "wrapper",
            "Simplicity lock",
            "read public Hacker News data safely",
            "safe by design",
            "stop after the read-only results",
        ]
        for phrase in forbidden:
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, opening)

    def test_front_door_docs_open_with_user_help(self) -> None:
        checks = {
            "docs/README.md": "Start with the first three pages",
            "docs/use_cases.md": "Use this page when you want ideas",
            "docs/onboarding.md": "You do not need to be technical",
            "docs/safety_model.md": "Use this page when you want to know",
            "docs/quickstart.md": "technical command path",
            "docs/command_reference.md": "exact Hacker News command",
            "docs/proof.md": "You do not need to run these commands yourself",
        }
        for relative, expected in checks.items():
            with self.subTest(relative=relative):
                self.assertIn(expected, self._read(relative))

    def test_use_cases_stays_non_technical(self) -> None:
        text = self._read("docs/use_cases.md")

        self.assertNotIn("hacker-news-api-tool", text)
        self.assertNotIn("--apply", text)
        self.assertNotIn("--live", text)
        self.assertIn("fetch item details", text)

    def test_read_only_docs_do_not_promise_account_actions(self) -> None:
        readme = self._read("README.md")
        safety = self._read("docs/safety_model.md")
        onboarding = self._read("docs/onboarding.md")

        for text in (readme, safety, onboarding):
            self.assertIn("cannot", text)
            self.assertNotIn("Connect your account", text)
            self.assertNotIn("API key", text.split("## What access this skill needs", 1)[0] if "## What access this skill needs" in text else "")
