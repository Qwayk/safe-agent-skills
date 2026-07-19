from __future__ import annotations

import json
import unittest
from pathlib import Path

from xero_safe_agent_cli.registry import load_registry
from xero_safe_agent_cli.runtime import XeroRuntime


class TestExamples(unittest.TestCase):
    def test_command_inputs_match_the_fixed_catalog(self) -> None:
        root = Path(__file__).resolve().parents[1]
        registry = load_registry()
        examples = {
            "accounting.get-invoices": root / "examples/get-invoices.json",
            "accounting.create-invoices": root / "examples/create-draft-invoice.json",
            "projects.get-project": root / "examples/get-project.json",
        }
        for command, path in examples.items():
            with self.subTest(command=command):
                value = json.loads(path.read_text(encoding="utf-8"))
                operation = registry.get(command)
                assert operation is not None
                XeroRuntime._validate_input(operation, value)

    def test_committed_plan_receipt_and_output_examples_are_valid_json(self) -> None:
        root = Path(__file__).resolve().parents[1]
        for path in sorted((root / "docs/examples").rglob("*.json")):
            with self.subTest(path=path.name):
                self.assertIsInstance(json.loads(path.read_text(encoding="utf-8")), dict)

    def test_auth_status_example_matches_the_secret_free_missing_token_shape(self) -> None:
        root = Path(__file__).resolve().parents[1]
        value = json.loads(
            (root / "docs/examples/outputs/auth_check.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            value,
            {
                "ok": True,
                "profile": "pkce",
                "token": {
                    "exists": False,
                    "path": "/private/path/.state/oauth/token.json",
                    "has_refresh_token": None,
                    "expires_at": None,
                    "scopes": [],
                },
            },
        )


if __name__ == "__main__":
    unittest.main()
