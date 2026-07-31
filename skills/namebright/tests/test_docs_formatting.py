from __future__ import annotations

import json
import unittest
from pathlib import Path

from namebright_safe_cli.operations import OPERATIONS, get_operation


class TestDocsAlignment(unittest.TestCase):
    def test_examples_json_is_valid(self) -> None:
        root = Path(__file__).resolve().parents[1]
        json_files = sorted((root / "docs" / "examples").rglob("*.json")) + sorted(
            (root / "examples").glob("*.json"),
        )
        self.assertTrue(json_files, "No JSON example files found")

        for path in json_files:
            with self.subTest(path=path):
                payload = json.loads(path.read_text(encoding="utf-8"))
                self.assertIsInstance(payload, (dict, list))

    def test_example_plan_and_receipt_shapes(self) -> None:
        root = Path(__file__).resolve().parents[1]
        plan = json.loads((root / "docs" / "examples" / "plan.example.json").read_text(encoding="utf-8"))
        receipt = json.loads((root / "docs" / "examples" / "receipt.example.json").read_text(encoding="utf-8"))

        self.assertEqual(plan["tool"], "namebright-safe-cli")
        self.assertEqual(plan["schema_version"], "1.0")
        self.assertIn("operation", plan)
        self.assertIn("snapshots", plan)

        self.assertEqual(receipt["tool"], "namebright-safe-cli")
        self.assertEqual(receipt["schema_version"], "1.0")
        self.assertIn("operation", receipt)
        self.assertIn("write", receipt)
        self.assertIn("verification", receipt)
        self.assertIn("rollback_supported", receipt)

        spec = get_operation("domains", "domains update")
        self.assertIsNotNone(spec)
        assert spec is not None
        self.assertEqual(plan["operation"]["command"], spec.command)
        self.assertEqual(plan["operation"]["method"], spec.method)
        self.assertEqual(plan["operation"]["path"], spec.path)
        self.assertEqual(plan["required_acknowledgements"], list(spec.required_acks))
        self.assertEqual(receipt["operation"], plan["operation"])

    def test_api_coverage_matches_registry(self) -> None:
        text = (Path(__file__).resolve().parents[1] / "docs" / "api_coverage.md").read_text(encoding="utf-8")
        rows: list[tuple[str, str, str, str]] = []
        for line in text.splitlines():
            columns = [part.strip() for part in line.strip().strip("|").split("|")]
            if not columns or not columns[0].isdigit():
                continue
            self.assertGreaterEqual(len(columns), 10)
            rows.append((columns[1], columns[2], columns[5], columns[8]))

        expected = {
            (spec.family, spec.method, spec.command, "implemented; live-unverified")
            for spec in OPERATIONS
        }
        self.assertEqual(set(rows), expected)
        self.assertEqual(len(rows), len(OPERATIONS))

    def test_json_examples_have_no_secret_keys(self) -> None:
        root = Path(__file__).resolve().parents[1]
        forbidden = {
            "accesstoken",
            "authorization",
            "clientsecret",
            "linkauthcode",
            "password",
            "verificationcode",
        }

        def walk(value: object) -> None:
            if isinstance(value, dict):
                for key, item in value.items():
                    normalized = str(key).lower().replace("-", "").replace("_", "")
                    self.assertNotIn(normalized, forbidden)
                    walk(item)
            elif isinstance(value, list):
                for item in value:
                    walk(item)

        files = sorted((root / "docs" / "examples").rglob("*.json")) + sorted(
            (root / "examples").glob("*.json"),
        )
        for path in files:
            with self.subTest(path=path):
                walk(json.loads(path.read_text(encoding="utf-8")))
