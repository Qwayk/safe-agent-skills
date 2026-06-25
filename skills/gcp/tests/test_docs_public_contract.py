from __future__ import annotations

import unittest
from pathlib import Path


class TestDocsPublicContract(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(__file__).resolve().parents[1]
        self.docs = self.root / "docs"

    def _read(self, name: str) -> str:
        return (self.docs / name).read_text(encoding="utf-8")

    def test_docs_home_starts_with_user_work_and_honest_status(self) -> None:
        text = self._read("README.md")
        opening = text.split("## ", 1)[0]

        self.assertIn("confirm the Google Cloud target", opening)
        self.assertIn("Live Google Cloud account behavior", opening)
        self.assertIn("not live account proof", opening)
        self.assertIn("## Start with the work", text)
        self.assertIn("## Commands, setup, and fixes", text)
        self.assertIn("## Proof and details", text)
        self.assertIn("[See useful Google Cloud asks](use_cases.md)", text)
        self.assertIn("[Connect Google Cloud safely](onboarding.md)", text)
        self.assertNotIn("Start here first:\n- `docs/", text)

    def test_onboarding_reduces_fear_before_commands(self) -> None:
        text = self._read("onboarding.md")
        opening = text.split("## Before you start", 1)[0]

        self.assertIn("choose the Google identity", opening)
        self.assertIn("You do not need to learn every command first.", opening)
        self.assertIn("Do not paste `.env`, service account JSON, OAuth files, tokens, or keys into chat.", opening)
        self.assertIn("## What to ask your AI agent", text)
        self.assertIn("## What success looks like", text)
        self.assertNotIn("qwayk-gcp-safe-agent-cli", opening)
        self.assertNotIn("--", opening)

    def test_use_cases_stays_plain_english_and_useful(self) -> None:
        text = self._read("use_cases.md")

        required = [
            "## Good first asks",
            "## Common jobs this helps with",
            "## What the agent should show you",
            "projects",
            "IAM",
            "Compute Engine",
            "Cloud Storage",
            "Cloud Run",
            "Cloud SQL",
            "logs",
            "billing",
        ]
        for phrase in required:
            self.assertIn(phrase, text)

        self.assertNotIn("`qwayk-gcp-safe-agent-cli", text)
        self.assertNotIn("--apply", text)

    def test_safety_model_explains_meaning_before_flags(self) -> None:
        text = self._read("safety_model.md")
        opening = text.split("## What safe use looks like", 1)[0]

        self.assertIn("look first, plan second, change last", opening)
        self.assertIn("Secrets stay local", opening)
        self.assertNotIn("--apply", opening)
        self.assertNotIn("--yes", opening)
        self.assertNotIn(".state/runs", opening)

    def test_quickstart_and_command_reference_do_not_open_with_page_talk(self) -> None:
        quickstart = self._read("quickstart.md")
        command_reference = self._read("command_reference.md")
        opening = quickstart.split("## ", 1)[0].lower()

        self.assertIn("Start with a result you can recognize", quickstart)
        self.assertIn("inventory summary", quickstart)
        self.assertIn("Use the command reference when you already know the Google Cloud job", command_reference)
        self.assertIn("For the guided path, start with", command_reference)
        self.assertIn("[What this skill can help you do](use_cases.md)", command_reference)

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

    def test_command_reference_teaches_generated_operation_lookup(self) -> None:
        text = self._read("command_reference.md")

        required = [
            "## How to find the right generated operation",
            "qwayk-gcp-safe-agent-cli <service> <operation> --input-json input.json",
            "[API coverage](api_coverage.md)",
            "Run `qwayk-gcp-safe-agent-cli --help`",
            "`compute`",
            "`serviceusage`",
            "`storage`",
            "`run`",
            "`sqladmin`",
            "`logging`",
            "`cloudbilling`",
            "`instances-list`",
            "`services-list`",
            "`buckets-list`",
            "`entries-list`",
            "`billing-accounts-list`",
        ]
        for phrase in required:
            self.assertIn(phrase, text)

    def test_generated_architecture_and_extension_docs_match_gcp_runtime(self) -> None:
        architecture = self._read("architecture.md")
        extension_path = self.docs / "agent_extension.md"
        extension = extension_path.read_text(encoding="utf-8") if extension_path.exists() else ""
        combined = architecture + "\n" + extension

        required = [
            "scripts/generate_gcp_discovery_inventory.py",
            "docs/_generated/gcp_discovery_inventory.json",
            "src/gcp_safe_agent_cli/generated_registry.py",
            "src/gcp_safe_agent_cli/generated_runtime.py",
            "src/gcp_safe_agent_cli/google_auth.py",
            "src/gcp_safe_agent_cli/project_config.py",
            "src/gcp_safe_agent_cli/redaction.py",
            "src/gcp_safe_agent_cli/runs.py",
            "normal Google Cloud operations come from the official-source generator",
            "Do not hand-add a one-off command",
            "Manual command modules are only for local helper commands",
        ]
        for phrase in required:
            self.assertIn(phrase, combined)

        banned = [
            "src/<package>",
            "<package>",
            "Create `src/<package>/commands/<name>.py`",
            "Implement `cmd_<name>",
        ]
        for phrase in banned:
            self.assertNotIn(phrase, combined)

    def test_proof_separates_local_validation_from_live_account_proof(self) -> None:
        text = self._read("proof.md")

        self.assertIn("Most users will never need to run these commands themselves.", text)
        self.assertIn("local tests and generated coverage passed", text)
        self.assertIn("live Google Cloud account behavior has not been verified yet", text)
        self.assertIn("This page does not prove that a real Google Cloud project", text)
        self.assertIn("## What still needs live verification", text)
        self.assertIn(".venv/bin/python -m unittest -q` passed with 54 tests", text)

    def test_committed_examples_label_live_verification_limits(self) -> None:
        example_paths = [
            self.docs / "examples" / "outputs" / "version.json",
            self.docs / "examples" / "outputs" / "inventory_summary.json",
            self.docs / "examples" / "outputs" / "auth_check.redacted.json",
            self.docs / "examples" / "outputs" / "compute_instances_list.mocked.json",
            self.docs / "examples" / "plan.example.json",
            self.docs / "examples" / "receipt.example.json",
        ]

        for path in example_paths:
            text = path.read_text(encoding="utf-8")
            self.assertIn("example", text.lower(), msg=f"{path.name} should say it is an example")
            self.assertIn(
                '"live_google_cloud_account_verified": false',
                text,
                msg=f"{path.name} should not look like live proof",
            )

    def test_skills_wrapper_docs_state_source_and_live_limits(self) -> None:
        notes_path = self.docs / "skills_wrappers.md"
        source_skill = self.root / "skills" / "gcp-safe-cli" / "SKILL.md"
        public_skill = self.root / "SKILL.md"
        skill_path = source_skill if source_skill.exists() else public_skill
        skill = skill_path.read_text(encoding="utf-8")

        if notes_path.exists():
            notes = notes_path.read_text(encoding="utf-8")
            self.assertIn("live Google Cloud account behavior is not verified", notes)
            self.assertIn("Do not treat a public publish as live Google Cloud account proof", notes)
        self.assertIn("Live Google Cloud account behavior has not been verified", skill)
        self.assertIn("Do not promise rollback, backup, restore, or undo", skill)

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
            "fake api base url",
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
        receipt_path = self.docs / "receipt_review_prompt.md"

        self.assertIn("Authentication means", authentication)
        self.assertIn("Configuration means", configuration)
        self.assertIn("A CSV file is a simple spreadsheet-style file.", jobs)
        if receipt_path.exists():
            receipt = receipt_path.read_text(encoding="utf-8")
            self.assertIn("A receipt is the record of what the tool actually did.", receipt)

    def test_configuration_and_auth_match_adc_runtime(self) -> None:
        authentication = self._read("authentication.md")
        configuration = self._read("configuration.md")

        self.assertIn("Application Default Credentials", authentication)
        self.assertIn("GCP_QUOTA_PROJECT", authentication)
        self.assertIn("GCP_ALLOWED_PROJECTS", configuration)
        self.assertNotIn("GCP_API_BASE_URL", configuration)

    def test_public_docs_do_not_expose_template_commands(self) -> None:
        banned = [
            "qwayk-gcp-safe-agent-cli demo",
            "qwayk-gcp-safe-agent-cli jobs",
            "read.ping",
            "write.ping",
            "auth token",
            "oauth_tokens",
            "api.example.com",
        ]

        paths = [
            self.root / "README.md",
            self.root / "CHANGELOG.md",
            self.root / "skills" / "gcp-safe-cli" / "SKILL.md",
            *self.docs.glob("*.md"),
            *self.root.glob("examples/*"),
        ]

        for path in paths:
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8")
            for phrase in banned:
                self.assertNotIn(phrase, text, msg=f"{path.relative_to(self.root)} contains starter text: {phrase}")
