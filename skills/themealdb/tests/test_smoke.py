from __future__ import annotations

import unittest

from qwayk_themealdb_safe_agent_cli.output import Output


class TestSmoke(unittest.TestCase):
    def test_output_constructs(self) -> None:
        output = Output(mode="json")
        self.assertIsNotNone(output)

    def test_output_provenance_merges_into_json_objects(self) -> None:
        output = Output(mode="json")
        output.set_provenance({"tool": "qwayk-themealdb-safe-agent-cli", "version": "0.1.0"})
        merged = output._with_provenance({"ok": True})
        self.assertEqual(merged["tool"], "qwayk-themealdb-safe-agent-cli")
        self.assertEqual(merged["version"], "0.1.0")
