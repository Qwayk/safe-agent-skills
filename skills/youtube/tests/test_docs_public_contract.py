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
            "docs/command_reference.md": "exact YouTube command",
            "docs/proof.md": "You do not need to run these commands yourself",
        }
        for relative, expected in checks.items():
            with self.subTest(relative=relative):
                self.assertIn(expected, self._read(relative))

    def test_use_cases_stays_non_technical(self) -> None:
        text = self._read("docs/use_cases.md")
        self.assertNotIn("youtube-api-tool", text)
        self.assertNotIn("--apply", text)
        self.assertNotIn("--live", text)

    def test_command_reference_shows_required_write_approval(self) -> None:
        text = self._read("docs/command_reference.md")
        self.assertIn("--apply --yes --ack-no-snapshot api <resource.method>", text)
        self.assertIn("--apply --yes --ack-no-snapshot --ack-irreversible api <resource.method>", text)
        self.assertNotIn("youtube-api-tool --apply --yes api <resource.method>", text)
        self.assertNotIn("youtube-api-tool --apply --yes --ack-irreversible api <resource.method>", text)

    def test_auth_and_jobs_docs_do_not_promise_writes_today(self) -> None:
        auth = self._read("docs/authentication.md")
        jobs = self._read("docs/jobs_and_batches.md")

        self.assertIn("this build does not write `.state/token.json`", auth)
        self.assertIn("Write rows are safety examples today", jobs)
