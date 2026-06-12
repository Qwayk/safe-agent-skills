from __future__ import annotations

import re
import unittest
from pathlib import Path

from figma_safe_agent_cli.operation_specs import OPERATION_SPECS


def _build_rows():
    root = Path(__file__).resolve().parents[1]
    path = root / "docs" / "api_coverage.md"
    text = path.read_text(encoding="utf-8")
    rows = []
    for line in text.splitlines():
        if not line.startswith("| "):
            continue
        if line.startswith("| In-scope area") or line.startswith("|---"):
            continue
        cols = [col.strip() for col in line.strip().strip("|").split("|")]
        if len(cols) != 7:
            continue
        area, endpoint, _capability, command_col = cols[:4]
        m = re.match(r"^(GET|POST|PUT|PATCH|DELETE)\s+(.+)$", endpoint.strip("`"))
        if not m:
            raise AssertionError(f"Invalid endpoint format in api_coverage: {endpoint}")
        method, path = m.groups()
        command_clean = command_col.strip().strip("`")
        match = re.search(r"figma-safe-agent-cli\s+operations\s+([^\s]+)\s+([^\s]+)", command_clean)
        if not match:
            raise AssertionError(f"Missing command mapping in api_coverage row: {endpoint}")
        area_arg, op_key = match.groups()
        if area_arg in {"list", "show"}:
            raise AssertionError(f"Invalid helper command in api_coverage row: {area_arg}: {endpoint}")
        rows.append((area, method, path, op_key))
    return rows


class TestDocsAndCoverageGuard(unittest.TestCase):
    def test_review_prompts_reflect_before_state_refusal_model(self) -> None:
        root = Path(__file__).resolve().parents[1]
        plan_path = root / "docs" / "plan_review_prompt.md"
        receipt_path = root / "docs" / "receipt_review_prompt.md"

        if not plan_path.exists() and not receipt_path.exists():
            return

        self.assertTrue(plan_path.exists())
        self.assertTrue(receipt_path.exists())

        plan_text = plan_path.read_text(encoding="utf-8").lower()
        receipt_text = receipt_path.read_text(encoding="utf-8").lower()

        self.assertIn("plan.before_state.status", plan_text)
        self.assertIn("approved write receipts record explicit no-snapshot approval", plan_text)
        self.assertIn("provider write receipt records explicit no-snapshot approval", receipt_text)
        self.assertNotIn("verification is mixed", plan_text)
        self.assertNotIn("verification is mixed", receipt_text)
        self.assertNotIn("best-effort readback for selected families", plan_text)
        self.assertNotIn("best-effort readback for selected families", receipt_text)
        self.assertNotIn("response-status-based", plan_text)
        self.assertNotIn("response-status-based", receipt_text)

    def test_api_coverage_matches_operation_inventory(self) -> None:
        spec_rows = {(s.area, s.method, s.path_template, s.op_key) for s in OPERATION_SPECS}
        coverage_rows = set(_build_rows())

        missing_from_coverage = sorted(spec_rows - coverage_rows)
        extra_in_coverage = sorted(coverage_rows - spec_rows)

        if missing_from_coverage:
            joined = ", ".join(
                f"{area}:{method}:{path}:{op}" for area, method, path, op in missing_from_coverage
            )
            self.fail(f"Missing in docs/api_coverage.md: {joined}")
        if extra_in_coverage:
            joined = ", ".join(
                f"{area}:{method}:{path}:{op}" for area, method, path, op in extra_in_coverage
            )
            self.fail(f"Extra in docs/api_coverage.md: {joined}")

    def test_no_template_scaffold_phrases_in_shipped_docs_examples_or_skills(self) -> None:
        root = Path(__file__).resolve().parents[1]
        scan_roots = [root / "docs", root / "skills"]
        patterns = [
            "template guide",
            "template docs",
            "template.md",
            "template_readme",
            "copy this starter",
            "<replace_me>",
            "demo mode",
            "stub surface",
            "scaffold",
            "todo:",
            "dummy",
        ]
        hits: list[str] = []
        for base in scan_roots:
            for path in base.rglob("*"):
                if not path.is_file() or path.suffix not in {".md", ".json", ".txt"}:
                    continue
                try:
                    text = path.read_text(encoding="utf-8").lower()
                except Exception:
                    continue
                for pattern in patterns:
                    if pattern in text:
                        hits.append(f"{path}:{pattern}")
        if hits:
            raise self.failureException("Template scaffold text found:\n" + "\n".join(hits))

    def test_command_reference_documents_shipped_global_flags(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "docs" / "command_reference.md").read_text(encoding="utf-8")
        required = [
            "--version",
            "--config",
            "--project-dir",
            "--env-file",
            "--timeout-s",
            "--verbose",
            "--debug",
            "--output",
            "--log-file",
            "--apply",
            "--yes",
            "--ack-irreversible",
            "--plan-out",
            "--plan-in",
            "--receipt-out",
            "--run-id",
            "--artifacts-dir",
            "--no-artifacts",
            "--skip-live",
        ]
        missing = [token for token in required if token not in text]
        if missing:
            self.fail("Missing command reference coverage for: " + ", ".join(missing))

    def test_command_reference_documents_explicit_execution_surface(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "docs" / "command_reference.md").read_text(encoding="utf-8")
        old_tokens = ["operations run", "--path-param", "--query "]
        hits: list[str] = [token for token in old_tokens if token in text]
        if hits:
            self.fail("Old bridge wording still present in command_reference.md: " + ", ".join(hits))

        self.assertIn("operations <area> <op_key>", text)
        self.assertIn("--version-id", text)
        self.assertIn("operations <area> <op_key> [--named-flags ...]", text)

    def test_start_pages_follow_non_technical_first_order(self) -> None:
        root = Path(__file__).resolve().parents[1]
        docs_text = (root / "docs" / "README.md").read_text(encoding="utf-8")
        docs_order = [
            "use_cases.md",
            "onboarding.md",
            "safety_model.md",
            "quickstart.md",
            "command_reference.md",
        ]
        positions = [docs_text.index(token) for token in docs_order]
        self.assertEqual(positions, sorted(positions))

        readme_text = (root / "README.md").read_text(encoding="utf-8")
        self.assertIn("## Start here first", readme_text)
        self.assertIn("[What you can do with Figma](docs/use_cases.md)", readme_text)
        self.assertIn("[Connect your Figma account](docs/onboarding.md)", readme_text)
        self.assertIn("[How this skill stays safe](docs/safety_model.md)", readme_text)
        self.assertIn("[Quickstart](docs/quickstart.md)", readme_text)
        self.assertIn("[Command guide](docs/command_reference.md)", readme_text)

    def test_technical_pages_point_back_to_non_technical_start(self) -> None:
        root = Path(__file__).resolve().parents[1]
        for rel in ("docs/quickstart.md", "docs/command_reference.md"):
            text = (root / rel).read_text(encoding="utf-8").lower()
            self.assertIn("technical", text, msg=rel)
            self.assertIn("use_cases.md", text, msg=rel)
            self.assertIn("onboarding.md", text, msg=rel)

    def test_use_cases_stays_plain_english_and_proof_has_reassurance_line(self) -> None:
        root = Path(__file__).resolve().parents[1]
        use_cases = (root / "docs" / "use_cases.md").read_text(encoding="utf-8")
        self.assertNotIn("figma-safe-agent-cli", use_cases)
        self.assertIn("Figma work is usually about understanding a file", use_cases)
        self.assertIn("## What the agent should show you", use_cases)

        proof = (root / "docs" / "proof.md").read_text(encoding="utf-8")
        self.assertIn("You don't need to run these commands yourself", proof)

    def test_no_bridge_surface_terms_in_shipped_docs_and_skills(self) -> None:
        root = Path(__file__).resolve().parents[1]
        check_files = [
            root / "docs" / "command_reference.md",
            root / "docs" / "quickstart.md",
            root / "docs" / "skills_wrappers.md",
            root / "skills" / "figma-safe-cli" / "SKILL.md",
            root / "README.md",
            root / "CHANGELOG.md",
            root / "docs" / "agent_extension.md",
            root / "docs" / "troubleshooting.md",
            root / "docs" / "safety_model.md",
        ]
        forbidden = [
            "operations run",
            "--path-param",
            "operations list/show/run",
        ]
        hits: list[str] = []
        for path in check_files:
            if not path.exists():
                continue
            text = path.read_text(encoding="utf-8").lower()
            for token in forbidden:
                if token in text:
                    hits.append(f"{path}:{token}")
        if hits:
            raise self.failureException("Found deprecated bridge wording: " + "; ".join(hits))
