from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class DocsAndWrapperTests(unittest.TestCase):
    def wrapper_path(self) -> Path:
        for candidate in (ROOT / "skills/jira/SKILL.md", ROOT / "SKILL.md"):
            if candidate.is_file():
                return candidate
        self.fail("Jira wrapper not found in source or published layout")

    def test_required_public_and_technical_pages_exist(self) -> None:
        required = [
            "README.md",
            "docs/README.md",
            "docs/quickstart.md",
            "docs/use_cases.md",
            "docs/safety_model.md",
            "docs/onboarding.md",
            "docs/command_reference.md",
            "docs/api_coverage.md",
            "docs/references.md",
            "docs/proof.md",
            "docs/skills_wrappers.md",
        ]
        for relative in required:
            self.assertTrue((ROOT / relative).is_file(), relative)
        self.assertTrue(self.wrapper_path().is_file())

    def test_readme_links_resolve(self) -> None:
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        for target in re.findall(r"\[[^]]+\]\(([^)]+)\)", text):
            if "://" not in target:
                self.assertTrue((ROOT / target).exists(), target)

    def test_wrapper_matches_executable_boundary_and_safety(self) -> None:
        wrapper = self.wrapper_path().read_text(encoding="utf-8")
        for required in [
            "jira-safe",
            "Jira Cloud Platform",
            "Jira Software",
            "--apply --plan-in PLAN --yes",
            "--ack-no-snapshot",
            "--ack-high-risk",
            "721",
        ]:
            self.assertIn(required, wrapper)

    def test_no_starter_names_or_placeholders_remain(self) -> None:
        candidates = [ROOT / "README.md", ROOT / "pyproject.toml", ROOT / ".env.example"]
        candidates += list((ROOT / "docs").glob("*.md"))
        candidates.append(self.wrapper_path())
        text = "\n".join(path.read_text(encoding="utf-8") for path in candidates)
        for stale in ["example-api-tool", "example_api_tool", "EXAMPLE_API_", "<REPLACE_ME>"]:
            self.assertNotIn(stale, text)


if __name__ == "__main__":
    unittest.main()
