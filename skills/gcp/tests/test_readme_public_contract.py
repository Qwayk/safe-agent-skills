from __future__ import annotations

import unittest
from pathlib import Path


class TestReadmePublicContract(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(__file__).resolve().parents[1]
        self.text = (self.root / "README.md").read_text(encoding="utf-8")
        self.opening = self.text.split("## Start here first", 1)[0]

    def _prose_paragraphs(self) -> list[str]:
        paragraphs: list[str] = []
        for block in self.opening.split("\n\n"):
            block = block.strip()
            if not block or block.startswith("# ") or block.startswith("**Capability:**"):
                continue
            paragraphs.append(block)
        return paragraphs

    def test_public_readme_opening_passes_first_screen_gate(self) -> None:
        paragraphs = self._prose_paragraphs()

        self.assertLessEqual(len(self.opening.split()), 220)
        self.assertLessEqual(len(paragraphs), 3)
        self.assertIn("Google Cloud work often starts with one risky question", self.opening)
        self.assertIn("are we looking at the right project", self.opening)
        self.assertIn("inspect running resources", self.opening)
        self.assertIn("review IAM access", self.opening)
        self.assertIn("spot cost or exposure risks", self.opening)
        self.assertIn("A good first ask is:", self.opening)

        first_ask = self.opening.split("A good first ask is:", 1)[1].splitlines()[0]
        self.assertLessEqual(len(first_ask.split()), 35)

        comma_heavy_sentences = [
            sentence.strip()
            for sentence in self.opening.replace("\n", " ").split(".")
            if sentence.count(",") >= 5
        ]
        self.assertEqual([], comma_heavy_sentences)

    def test_public_readme_opening_answers_first_time_customer_questions(self) -> None:
        required = [
            "running",
            "access",
            "cost",
            "cloud admin reviews",
            "cleanup planning",
            "exposure checks",
            "reviewed change plans",
            "A good first ask is:",
            "Change level: **Reads + careful changes**",
            "Live Google Cloud account behavior has not been verified",
        ]
        for phrase in required:
            self.assertIn(phrase, self.opening)

    def test_public_readme_opening_avoids_technical_proof_and_template_voice(self) -> None:
        banned_opening_snippets = [
            "raw docs",
            "raw vendor docs",
            "generated inventory",
            "discovery",
            "coverage count",
            "operation count",
            "adc",
            "application default credentials",
            "--apply",
            "--yes",
            "--ack",
            "no-snapshot",
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
            "fake api base url",
            "rollback",
            "backup",
            "restore",
            "undo",
        ]
        opening_lower = self.opening.lower()
        for snippet in banned_opening_snippets:
            self.assertNotIn(snippet, opening_lower)

        self.assertNotIn("docs/", opening_lower)
        self.assertNotIn("--", self.opening)

    def test_public_readme_required_sections_are_present(self) -> None:
        self.assertTrue(self.text.startswith("# Google Cloud Platform Safe CLI\n"))
        self.assertNotIn("## Simplicity lock", self.text)
        self.assertNotIn("# qwayk-gcp-safe-agent-cli", self.text)

        required_sections = [
            "## Start here first",
            "## What this skill helps with",
            "## Example requests",
            "## What access this skill needs",
            "## Install and first run",
            "## How this skill stays safe",
            "## What it covers today",
            "## What happens before live changes",
            "## What proof it leaves behind",
            "## Limits",
            "## Helpful docs",
        ]
        for section in required_sections:
            self.assertIn(section, self.text)

        self.assertIn("Install slug: `gcp`", self.text)
        self.assertIn("npx skills add Qwayk/safe-agent-skills@gcp -g -y", self.text)
        self.assertNotIn("not public-live", self.text)

    def test_helpful_docs_and_start_here_stay_human_facing(self) -> None:
        expected_links = [
            "[See useful Google Cloud asks](docs/use_cases.md)",
            "[Connect Google Cloud safely](docs/onboarding.md)",
            "[Understand review before changes](docs/safety_model.md)",
            "[Run the quickstart](docs/quickstart.md)",
            "[Use the command guide](docs/command_reference.md)",
            "[Browse all GCP docs](docs/README.md)",
            "[Proof and verification](docs/proof.md)",
            "[API coverage](docs/api_coverage.md)",
        ]
        for link in expected_links:
            self.assertIn(link, self.text)

        self.assertNotIn("- `docs/use_cases.md`", self.text)
        self.assertNotIn("- `docs/onboarding.md`", self.text)

    def test_quickstart_opens_with_real_gcp_first_result(self) -> None:
        text = (self.root / "docs" / "quickstart.md").read_text(encoding="utf-8")
        opening = text.split("## ", 1)[0].lower()

        self.assertIn("Start by listing Compute Engine instances", text)
        self.assertIn("Compute Engine instances", text)
        self.assertIn("enabled services", text)
        self.assertIn('"project": "my-gcp-project"', text)
        self.assertIn('"zone": "us-central1-a"', text)
        self.assertIn("does not prove that every live Google Cloud read will work", text)

        banned_opening_bits = [
            "this page helps",
            "this page is for",
            "without turning",
            "full command manual",
            "if you are still deciding",
            "run one safe read that proves",
            "generated discovery inventory",
        ]
        for phrase in banned_opening_bits:
            self.assertNotIn(phrase, opening)
