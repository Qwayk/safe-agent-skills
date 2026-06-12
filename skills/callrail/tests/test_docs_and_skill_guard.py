from __future__ import annotations

import unittest
from pathlib import Path


class TestDocsAndSkillGuard(unittest.TestCase):
    def test_no_template_scaffold_text_in_shipped_docs_examples_or_skill(self) -> None:
        root = Path(__file__).resolve().parents[1]
        scan_paths = [
            root / "README.md",
            root / "docs" / "authentication.md",
            root / "docs" / "command_reference.md",
            root / "docs" / "configuration.md",
            root / "docs" / "onboarding.md",
            root / "docs" / "proof.md",
            root / "docs" / "quickstart.md",
            root / "docs" / "references.md",
            root / "docs" / "safety_model.md",
            root / "docs" / "skills_wrappers.md",
            root / "docs" / "troubleshooting.md",
            root / "docs" / "agent_extension.md",
            root / "docs" / "examples" / "outputs" / "version.json",
            root / "docs" / "examples" / "outputs" / "auth_check.json",
            root / "docs" / "examples" / "plan.example.json",
            root / "docs" / "examples" / "receipt.example.json",
            root / "skills" / "callrail-safe-agent-cli" / "SKILL.md",
        ]
        forbidden = [
            "<replace_me>",
            "<tool>",
            "<read_command>",
            "jobs run",
            "demo write",
            "demo read",
            "auth token set",
            "auth token status",
            "agent extension guide (template)",
        ]
        hits: list[str] = []
        for path in scan_paths:
            text = path.read_text(encoding="utf-8").lower()
            for token in forbidden:
                if token in text:
                    hits.append(f"{path}:{token}")
        if hits:
            self.fail("Template or removed-command text found:\n" + "\n".join(hits))

    def test_api_coverage_no_longer_marks_surface_as_planned(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "docs" / "api_coverage.md").read_text(encoding="utf-8")
        self.assertNotIn("Coverage mode: planned", text)
        self.assertNotIn("| planned |", text)
        self.assertIn("implemented, live-unverified", text)
        self.assertNotIn("Remaining audit slice before a 100/100 claim", text)
        self.assertNotIn("implemented, local-reference", text)

    def test_skill_wrapper_exists_and_points_to_safe_workflow(self) -> None:
        root = Path(__file__).resolve().parents[1]
        skill_path = root / "skills" / "callrail-safe-agent-cli" / "SKILL.md"
        self.assertTrue(skill_path.exists())
        text = skill_path.read_text(encoding="utf-8")
        required = [
            "qwayk-callrail-safe-agent-cli --output json auth check",
            "docs/api_coverage.md",
            "--plan-out",
            "--plan-in",
            "--apply --yes",
            "--ack-irreversible",
            "integrations create",
            "webhooks",
            "custom",
            "runs list",
            "runs show",
            "media_url",
            "--media-file",
        ]
        missing = [token for token in required if token not in text]
        if missing:
            self.fail("Skill wrapper missing required guidance: " + ", ".join(missing))

    def test_command_reference_mentions_global_safety_flags(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "docs" / "command_reference.md").read_text(encoding="utf-8")
        required = [
            "--output json",
            "--env-file",
            "--timeout-s",
            "--verbose",
            "--debug",
            "--apply",
            "--yes",
            "--ack-irreversible",
            "--plan-out",
            "--plan-in",
            "--receipt-out",
            "--run-id",
            "--artifacts-dir",
            "--no-artifacts",
        ]
        missing = [token for token in required if token not in text]
        if missing:
            self.fail("Command reference missing safety/global flags: " + ", ".join(missing))

    def test_removed_reference_helpers_are_absent_from_shipped_docs(self) -> None:
        root = Path(__file__).resolve().parents[1]
        scan_paths = [
            root / "README.md",
            root / "docs" / "api_coverage.md",
            root / "docs" / "command_reference.md",
            root / "docs" / "skills_wrappers.md",
            root / "skills" / "callrail-safe-agent-cli" / "SKILL.md",
        ]
        removed_tokens = [
            "tags available-colors",
            "integrations configure",
            "message-flows configure",
            "trackers request-number",
            "trackers configure-call-flows",
            "trackers session-call-sources",
            "trackers source-call-sources",
            "users roles",
        ]
        hits: list[str] = []
        for path in scan_paths:
            text = path.read_text(encoding="utf-8")
            for token in removed_tokens:
                if token in text:
                    hits.append(f"{path}:{token}")
        if hits:
            self.fail("Removed helper commands still appear in shipped docs:\n" + "\n".join(hits))

    def test_command_reference_and_skill_wrapper_explain_account_scoping_honestly(self) -> None:
        root = Path(__file__).resolve().parents[1]
        command_reference = (root / "docs" / "command_reference.md").read_text(encoding="utf-8")
        skill_wrapper = (root / "skills" / "callrail-safe-agent-cli" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("In normal use, include `--account-id`", command_reference)
        self.assertIn("unless `CALLRAIL_DEFAULT_ACCOUNT_ID` is already set", command_reference)
        self.assertIn("Most REST commands in this tool are account-scoped", skill_wrapper)

    def test_readme_has_nontechnical_example_requests_section(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "README.md").read_text(encoding="utf-8")
        required = [
            "**Capability:** Reads + careful changes",
            "CallRail is where calls, texts, forms",
            "## Start here first",
            "## What this skill helps with",
            "## What access this skill needs",
            "## Install and first run",
            "## How this skill stays safe",
            "## Helpful docs",
        ]
        missing = [token for token in required if token not in text]
        if missing:
            self.fail("README missing required public sections: " + ", ".join(missing))

        forbidden = [
            "Use this skill when",
            "For non-technical users",
            "For technical users",
            "with dry-run-first write paths",
            "without guessing from raw docs",
        ]
        hits = [token for token in forbidden if token in text]
        if hits:
            self.fail("README still has old public-page wording: " + ", ".join(hits))

    def test_tool_agents_has_customer_ready_contract_sections(self) -> None:
        root = Path(__file__).resolve().parents[1]
        rules_file = next(root.glob("AGENTS.*"), None)
        if not rules_file or not rules_file.is_file():
            return
        text = rules_file.read_text(encoding="utf-8")
        required = [
            "## Safe usage contract",
            "## Customer trust response shape",
            "## Where proof lives",
            "## Non-technical onboarding behavior",
            "## Live knowledge rule",
            "## Safe extension guidance",
        ]
        missing = [token for token in required if token not in text]
        if missing:
            self.fail("Tool rules file missing customer-ready contract sections: " + ", ".join(missing))
