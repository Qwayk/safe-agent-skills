from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from giantpanda_api_tool.commands.domains import (
    DOMAINS_ADD_OPERATION,
    DOMAINS_ADD_PATH,
    DOMAINS_STATS_PATH,
)


def _project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _load(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class TestCoverageExamplesWrapperAlignment(unittest.TestCase):
    def test_examples_parse_to_json_and_are_secret_or_path_safe(self) -> None:
        root = _project_root()
        paths = [*root.glob("examples/*.json"), *root.glob("docs/examples/**/*.json")]
        self.assertGreaterEqual(len(paths), 5)
        for path in paths:
            text = _load(path)
            payload = json.loads(text)
            self.assertIsInstance(payload, dict)
            lowered = text.lower()
            forbidden_tokens = ("your_token_here", "bearer", "authorization:", "sentinel_", "changeme")
            for token in forbidden_tokens:
                self.assertNotIn(token, lowered, f"{path} contains forbidden token marker {token!r}")
            private_path_patterns = (
                "/users/",
                "/home/",
                "/private/",
                "/tmp/",
                "/var/",
                "/opt/",
                "/root/",
            )
            for bad in private_path_patterns:
                self.assertNotIn(
                    bad,
                    lowered,
                    f"{path} appears to include a private absolute path marker {bad!r}",
                )

    def test_api_coverage_has_two_explicit_rows_and_command_match(self) -> None:
        root = _project_root()
        text = _load(root / "docs" / "api_coverage.md")
        rows = [line for line in text.splitlines() if re.match(r"^\| `(?:GET|POST) ", line)]
        self.assertEqual(len(rows), 2)
        for row in rows:
            cells = [cell.strip() for cell in row.strip("|").split("|")]
            command = "domains stats" if DOMAINS_STATS_PATH in cells[0] else DOMAINS_ADD_OPERATION
            self.assertTrue(any(command in cell for cell in cells))
        expected_rows = {f"`GET {DOMAINS_STATS_PATH}`", f"`POST {DOMAINS_ADD_PATH}`"}
        found_rows = {line.split("|", maxsplit=2)[1].strip() for line in rows}
        self.assertEqual(found_rows, expected_rows)

    def test_frontmatter_wrapper_is_present_and_well_formed(self) -> None:
        root = _project_root()
        wrapper = root / "SKILL.md"
        self.assertTrue(wrapper.is_file(), f"Missing wrapper: {wrapper}")
        text = _load(wrapper)
        self.assertTrue(text.startswith("---\n"), "Wrapper does not start with YAML frontmatter")
        end = text.find("\n---", 4)
        self.assertNotEqual(end, -1, "Wrapper is missing closing frontmatter marker")
        frontmatter = text[4:end]
        self.assertIn("name: giantpanda", frontmatter)
        self.assertIn("description:", frontmatter)

    def test_plan_and_receipt_examples_list_the_same_domains(self) -> None:
        examples = _project_root() / "docs" / "examples"
        plan = json.loads(_load(examples / "plan.example.json"))["plan"]
        receipt = json.loads(_load(examples / "receipt.example.json"))["receipt"]
        self.assertEqual(plan["plan_id"], receipt["plan_id"])
        self.assertEqual(plan["request_body"], receipt["request"])
        result = receipt["verification"]
        names = [row["name"] for row in plan["request_body"]["domains"]]
        self.assertCountEqual(names, result["created"] + result["existing"] + result["needs_check"])
