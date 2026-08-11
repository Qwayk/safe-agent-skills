from __future__ import annotations

import json
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


def _wrapper_path(root: Path) -> Path:
    return root / "SKILL.md"


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
        rows: list[str] = []
        in_table = False
        for line in text.splitlines():
            if line.startswith("| Endpoint |"):
                in_table = True
                continue
            if not in_table:
                continue
            if line.startswith("|---"):
                continue
            if not line.startswith("| `"):
                break
            rows.append(line.strip())

        self.assertEqual(len(rows), 2, "Expected exactly two coverage endpoint rows")
        for row in rows:
            cells = [cell.strip() for cell in row.strip("|").split("|")]
            self.assertGreaterEqual(len(cells), 6)
            endpoint = cells[0]
            command = cells[2]
            self.assertIn(endpoint, {f"`GET {DOMAINS_STATS_PATH}`", f"`POST {DOMAINS_ADD_PATH}`"})
            if endpoint == f"`GET {DOMAINS_STATS_PATH}`":
                self.assertIn("domains stats", command)
            if endpoint == f"`POST {DOMAINS_ADD_PATH}`":
                self.assertIn(DOMAINS_ADD_OPERATION, command)

        expected_rows = {f"`GET {DOMAINS_STATS_PATH}`", f"`POST {DOMAINS_ADD_PATH}`"}
        found_rows = {line.split("|", maxsplit=2)[1].strip() for line in rows}
        self.assertEqual(found_rows, expected_rows)

    def test_frontmatter_wrapper_is_present_and_well_formed(self) -> None:
        root = _project_root()
        wrapper = _wrapper_path(root)
        self.assertTrue(wrapper.is_file(), f"Missing wrapper: {wrapper}")
        text = _load(wrapper)
        self.assertTrue(text.startswith("---\n"), "Wrapper does not start with YAML frontmatter")
        end = text.find("\n---", 4)
        self.assertNotEqual(end, -1, "Wrapper is missing closing frontmatter marker")
        frontmatter = text[4:end]
        self.assertIn("name: giantpanda", frontmatter)
        self.assertIn("description:", frontmatter)

    def test_examples_and_coverage_contain_no_template_leftovers_and_proof_is_honest(self) -> None:
        root = _project_root()
        proof = _load(root / "docs" / "proof.md").lower()
        coverage = _load(root / "docs" / "api_coverage.md")
        wrapper = _load(_wrapper_path(root)).lower()
        stale_markers = (
            "<replace_me>",
            "example-api-tool",
            "<get /",
            "<post /",
            "<provider>",
            "path/to",
        )
        for marker in stale_markers:
            self.assertNotIn(marker, coverage.lower(), f"coverage still contains stale marker {marker!r}")
            self.assertNotIn(marker, proof, f"proof still contains stale marker {marker!r}")
        self.assertIn("provider-live verified", coverage.lower())
        self.assertIn("provider-live-unverified", coverage.lower())
        self.assertIn("one provider request", proof)
        self.assertIn("http `200`", proof)
        self.assertIn("end_date, pagination, start_date, stats", proof)
        self.assertNotIn("honest no-live", proof)
        self.assertNotIn("all provider-facing verification here is mocked", proof)
        self.assertIn("no live `domains add`", proof, "proof must state no live write was made")
        self.assertIn("stats authentication", wrapper)
        self.assertIn("provider-live verified", wrapper)
        self.assertIn("domains add", wrapper)
        self.assertIn("provider-live-unverified", wrapper)

        examples = [*root.glob("examples/*.json"), *root.glob("docs/examples/**/*.json")]
        stale_in_examples = ("<replace_me>", "template")
        for path in examples:
            text = _load(path).lower()
            for marker in stale_in_examples:
                self.assertNotIn(marker, text, f"{path} contains stale marker {marker!r}")
