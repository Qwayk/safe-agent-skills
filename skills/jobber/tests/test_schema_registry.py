from __future__ import annotations

import re
import unittest
from pathlib import Path

from jobber_safe_agent_cli.schema_registry import load_schema_registry


class TestSchemaRegistry(unittest.TestCase):
    def test_registry_counts_and_lists(self) -> None:
        schema = load_schema_registry()
        self.assertGreater(schema.get("query_count", 0), 0)
        self.assertGreater(schema.get("mutation_count", 0), 0)
        self.assertGreater(schema.get("webhook_topic_count", 0), 0)
        self.assertGreater(len(schema.get("query_fields", [])), 0)
        self.assertGreater(len(schema.get("mutation_fields", [])), 0)
        self.assertEqual(schema["query_count"], len(schema["query_fields"]))
        self.assertEqual(schema["mutation_count"], len(schema["mutation_fields"]))
        self.assertEqual(schema["webhook_topic_count"], len(schema["webhook_topics"]))

    def test_api_coverage_counts_and_statuses_match_registry(self) -> None:
        root = Path(__file__).resolve().parents[1]
        coverage = (root / "docs" / "api_coverage.md").read_text(encoding="utf-8")
        schema = load_schema_registry()

        self.assertNotIn("100/100", coverage)
        self.assertNotIn("fully implemented", coverage.lower())
        self.assertIn("registry-backed/live-unverified/scope-gated", coverage)
        self.assertIn("registry-backed/live-unverified/scaffold-limited", coverage)
        self.assertIn("topic-listed/live-unverified", coverage)

        source_counts = re.search(
            r"Source counts: (?P<queries>\d+) Query fields, (?P<mutations>\d+) Mutation fields, (?P<topics>\d+) webhook topics",
            coverage,
        )
        self.assertIsNotNone(source_counts)
        assert source_counts is not None
        self.assertEqual(int(source_counts.group("queries")), schema["query_count"])
        self.assertEqual(int(source_counts.group("mutations")), schema["mutation_count"])
        self.assertEqual(int(source_counts.group("topics")), schema["webhook_topic_count"])

        def section_rows(start: str, end: str) -> list[str]:
            body = coverage.split(start, 1)[1].split(end, 1)[0]
            return [line for line in body.splitlines() if re.match(r"^\|\s*\d+\s*\|", line)]

        query_rows = section_rows("## Query coverage ledger", "## Mutation coverage ledger")
        mutation_rows = section_rows("## Mutation coverage ledger", "## Webhook topic coverage")
        webhook_rows = section_rows("## Webhook topic coverage", "## API inventory source")

        self.assertEqual(len(query_rows), schema["query_count"])
        self.assertEqual(len(mutation_rows), schema["mutation_count"])
        self.assertEqual(len(webhook_rows), schema["webhook_topic_count"])
        self.assertTrue(all("registry-backed/live-unverified/scope-gated" in row for row in query_rows))
        self.assertTrue(all("registry-backed/live-unverified/scaffold-limited" in row for row in mutation_rows))
        self.assertTrue(all("topic-listed/live-unverified" in row for row in webhook_rows))
