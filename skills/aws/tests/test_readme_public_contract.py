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
            "example skill",
            "example-skill",
            "<replace_me>",
            "<yyyy-mm-dd>",
        ]
        for snippet in banned_opening_snippets:
            self.assertNotIn(snippet, opening.lower())
        self.assertNotIn("--", opening)

    def test_public_readme_opening_stays_user_facing(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "README.md").read_text(encoding="utf-8")

        self.assertTrue(text.startswith("# AWS Safe Agent CLI\n"))
        self.assertNotIn("## Simplicity lock", text)
        self.assertNotIn("# qwayk-aws-safe-agent-cli", text)
        self.assertIn("Install slug: `aws`", text)
        self.assertNotIn("Public admission is not live", text)
        self.assertNotIn("Sh" + "ai", text)
        self.assertNotIn("source tree is the working copy", text)

        required_sections = [
            "## Start here first",
            "## What this skill helps with",
            "## Example requests",
            "## Install and first run",
            "## How this skill stays safe",
            "## What happens before live changes",
        ]
        for section in required_sections:
            self.assertIn(section, text)

        opening = text.split("## Start here first", 1)[0]
        self.assertIn("A good first ask is:", opening)
        self.assertIn("AWS is where teams keep the servers, buckets, roles, keys, logs, queues, databases, and billing settings", opening)
        self.assertIn("Which account am I in?", opening)
        self.assertIn("Check my AWS account, role, and region.", opening)
        self.assertIn("IAM users, S3 buckets, and EC2 instances", opening)

    def test_helpful_docs_stay_human_facing(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "README.md").read_text(encoding="utf-8")

        self.assertIn("## Helpful docs", text)
        self.assertIn("[Browse the AWS docs hub](docs/README.md)", text)
        self.assertIn("[Run the first safe AWS checks](docs/quickstart.md)", text)
        self.assertIn("[Use the command guide](docs/command_reference.md)", text)
        self.assertIn("[Check the pinned coverage boundary](docs/api_coverage.md)", text)
        self.assertIn("[Review proof and examples](docs/proof.md)", text)
        self.assertNotIn("- `docs/use_cases.md`", text)
        self.assertNotIn("- `docs/onboarding.md`", text)

    def test_start_here_section_stays_human_facing(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "README.md").read_text(encoding="utf-8")

        self.assertIn("## Start here first", text)
        self.assertIn("[See real AWS jobs this skill helps with](docs/use_cases.md)", text)
        self.assertIn("[Set up AWS access locally](docs/onboarding.md)", text)
        self.assertIn("[Understand the AWS safety rules](docs/safety_model.md)", text)
        self.assertIn("[Run the first safe AWS checks](docs/quickstart.md)", text)
        self.assertIn("[Use the exact command guide](docs/command_reference.md)", text)
        self.assertIn("[Install and first run](#install-and-first-run)", text)
        self.assertIn("[Helpful docs](#helpful-docs)", text)

    def test_quickstart_opens_with_human_links(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "docs" / "quickstart.md").read_text(encoding="utf-8")
        opening = text.split("## ", 1)[0].lower()

        self.assertIn("A good first ask is:", text)
        self.assertIn("Start with a result you can recognize", text)
        self.assertIn("## What you will do first", text)
        self.assertIn("## 3. Run one small first read", text)
        self.assertIn("## Good next reads", text)
        self.assertIn("[Choose useful AWS tasks](use_cases.md)", text)
        self.assertIn("[Set up AWS access locally](onboarding.md)", text)
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
