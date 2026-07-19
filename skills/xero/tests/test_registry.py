from __future__ import annotations

import json
import re
import tempfile
import unittest
from pathlib import Path

from xero_safe_agent_cli.registry import load_registry


class TestRegistry(unittest.TestCase):
    def test_packaged_catalog_has_the_pinned_fixed_surface(self) -> None:
        registry = load_registry()
        summary = registry.summary()
        self.assertEqual(summary["pinned_commit"], "e952d0bda3628facbf7afc5990ad6a0e7e77bd1e")
        self.assertEqual(summary["openapi_operations"], 477)
        self.assertEqual(summary["manual_operations"], 2)
        self.assertEqual(summary["commands"], 474)
        self.assertEqual(summary["superseded_compatibility"], 5)
        self.assertTrue(re.fullmatch(r"[0-9a-f]{64}", summary["inventory_hash"]))

    def test_describe_exposes_fixed_input_auth_and_safety_contract(self) -> None:
        registry = load_registry()
        description = registry.describe("accounting.create-invoices")
        self.assertEqual(description["method"], "PUT")
        self.assertEqual(description["path"], "/Invoices")
        self.assertEqual(description["minimum_scopes"], ["accounting.invoices"])
        self.assertTrue(description["tenant_required"])
        self.assertTrue(description["extra_approval"])
        self.assertIn("application/json", description["input"]["body"]["media_types"])

    def test_unknown_or_superseded_names_are_not_callable(self) -> None:
        registry = load_registry()
        self.assertIsNone(registry.get("payroll-au.get-timesheets"))
        with self.assertRaisesRegex(Exception, "Unknown fixed Xero command"):
            registry.describe("accounting.call-anything")

    def test_tampered_catalog_server_is_refused_before_registry_use(self) -> None:
        source = Path(__file__).resolve().parents[1] / "src/xero_safe_agent_cli/generated/operations.json"
        value = json.loads(source.read_text(encoding="utf-8"))
        command = next(row for row in value["operations"] if row.get("command"))
        command["server"] = "https://attacker.invalid"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "operations.json"
            path.write_text(json.dumps(value), encoding="utf-8")
            with self.assertRaisesRegex(Exception, "pinned SHA-256"):
                load_registry(path)


if __name__ == "__main__":
    unittest.main()
