from __future__ import annotations

import json
import unittest
from pathlib import Path


class TestExamplesHonesty(unittest.TestCase):
    def _root(self) -> Path:
        return Path(__file__).resolve().parents[1]

    def _read(self, relative: str) -> str:
        return (self._root() / relative).read_text(encoding="utf-8")

    def _read_json(self, relative: str) -> dict:
        return json.loads(self._read(relative))

    def test_proof_declares_live_unverified_workspace(self) -> None:
        text = self._read("docs/proof.md")
        self.assertIn("live production checks remain honestly unverified here", text)
        self.assertIn("representative redacted docs examples only", text)

    def test_output_examples_are_marked_as_representative_not_live_proof(self) -> None:
        files = [
            "docs/examples/outputs/version.json",
            "docs/examples/outputs/auth_check.json",
            "docs/examples/outputs/ws_subscribe_start.json",
            "docs/examples/plan.example.json",
            "docs/examples/receipt.example.json",
        ]
        for relative in files:
            with self.subTest(relative=relative):
                payload = self._read_json(relative)
                self.assertEqual(payload["example_kind"], "representative-redacted-doc-example")
                self.assertIn("Representative redacted example only.", payload["example_note"])

    def test_live_looking_examples_do_not_claim_live_success_from_this_workspace(self) -> None:
        auth_check = self._read_json("docs/examples/outputs/auth_check.json")
        ws_subscribe = self._read_json("docs/examples/outputs/ws_subscribe_start.json")

        self.assertEqual(auth_check["proof_status"], "local-unit-tested-live-unverified")
        self.assertFalse(auth_check["live_probe"]["attempted"])
        self.assertIsNone(auth_check["live_probe"]["ok"])
        self.assertIn("No live Fortnox request was run from this workspace", auth_check["live_probe"]["reason"])

        self.assertEqual(ws_subscribe["proof_status"], "local-unit-tested-live-unverified")
        self.assertFalse(ws_subscribe["ok"])
        self.assertEqual(ws_subscribe["event_count"], 0)
        self.assertEqual(ws_subscribe["events"], [])
        self.assertEqual(ws_subscribe["stop_reason"], "representative_example_only_no_live_connection")

    def test_examples_are_fortnox_specific_and_have_no_generic_tool_placeholders(self) -> None:
        version = self._read_json("docs/examples/outputs/version.json")
        plan = self._read_json("docs/examples/plan.example.json")
        receipt = self._read_json("docs/examples/receipt.example.json")

        self.assertEqual(version["tool"], "fortnox-api-tool")
        self.assertEqual(plan["tool"], "fortnox-api-tool")
        self.assertEqual(receipt["tool"], "fortnox-api-tool")
        self.assertNotIn("<tool>", self._read("docs/examples/outputs/version.json"))
        self.assertNotIn("<tool>", self._read("docs/examples/plan.example.json"))
        self.assertNotIn("<tool>", self._read("docs/examples/receipt.example.json"))
        self.assertTrue(plan["command"].startswith("fortnox-api-tool "))
        self.assertTrue(receipt["command"].startswith("fortnox-api-tool "))

