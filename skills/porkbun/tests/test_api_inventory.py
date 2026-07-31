from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any


def _resolve_skill_wrapper(root: Path) -> Path:
    candidates = (
        root / "skills" / "porkbun" / "SKILL.md",
        root / "SKILL.md",
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    expected = " or ".join(str(candidate) for candidate in candidates)
    raise FileNotFoundError(f"Missing Porkbun skill wrapper; expected {expected}")


class TestPorkbunInventory(unittest.TestCase):
    EXPECTED_SHA = "f4788709c27e0365e8a502180e0427bbcf7bd7558f3d7032bf34cf0a25dedd77"
    EXPECTED_FAMILIES = [
        "utility",
        "pricing",
        "api-key",
        "domain",
        "dns",
        "ssl",
        "email-hosting",
        "marketplace",
        "account",
        "webhooks",
    ]
    EXPECTED_BILLABLE = {"domainCreate", "domainRenew", "transferDomain"}
    EXPECTED_TERMS = {"domainCreate"}
    EXPECTED_SECRET_RESULTS = {
        "apikeyRequest",
        "apikeyRetrieve",
        "sslRetrieve",
        "getSslRetrieve",
        "createAccountInvite",
        "webhookList",
        "webhookGet",
        "webhookUpdate",
        "webhookRotateSecret",
        "webhookCreate",
    }
    EXPECTED_NO_SNAPSHOT = {
        "apikeyRequest",
        "apikeyRetrieve",
        "emailSetPassword",
        "createAccountInvite",
        "webhookCreate",
    }

    def setUp(self) -> None:
        self.root = Path(__file__).resolve().parents[1]
        self.spec_path = self.root / "vendor" / "porkbun-openapi-v3.9.json"
        self.inventory_path = self.root / "docs" / "operation_inventory.json"
        self.coverage_path = self.root / "docs" / "api_coverage.md"
        self.policy_path = self.root / "scripts" / "porkbun_inventory_policy.json"
        self.spec = json.loads(self.spec_path.read_text(encoding="utf-8"))
        self.inventory = json.loads(self.inventory_path.read_text(encoding="utf-8"))
        self.policy = json.loads(self.policy_path.read_text(encoding="utf-8"))
        self.operations: list[dict[str, Any]] = self.inventory["operations"]
        self.by_id = {op["operation_id"]: op for op in self.operations}

    def test_pinned_spec_and_boundary_counts(self) -> None:
        self.assertEqual(hashlib.sha256(self.spec_path.read_bytes()).hexdigest(), self.EXPECTED_SHA)
        self.assertEqual(self.spec["openapi"], "3.0.0")
        self.assertEqual(self.spec["info"]["version"], "3.9")
        self.assertEqual(len(self.spec["paths"]), 53)
        method_counts: dict[str, int] = {"GET": 0, "POST": 0}
        for path_item in self.spec["paths"].values():
            for method in path_item:
                upper = method.upper()
                if upper in method_counts:
                    method_counts[upper] += 1
        self.assertEqual(method_counts, {"GET": 25, "POST": 41})
        totals = self.inventory["summary"]["totals"]
        self.assertEqual(
            (totals["path_count"], totals["operation_count"], totals["read_count"], totals["write_count"]),
            (53, 66, 39, 27),
        )
        self.assertEqual(self.inventory["summary"]["families"], self.EXPECTED_FAMILIES)

    def test_exact_policy_sets(self) -> None:
        self.assertEqual(set(self.policy["billable_operations"]), self.EXPECTED_BILLABLE)
        self.assertEqual(set(self.policy["terms_required_operations"]), self.EXPECTED_TERMS)
        self.assertEqual(set(self.policy["secret_bearing_results"]), self.EXPECTED_SECRET_RESULTS)
        self.assertEqual(
            {op_id for op_id, value in self.policy["write_snapshot_policy"].items() if value["requires_no_snapshot_ack"]},
            self.EXPECTED_NO_SNAPSHOT,
        )

    def test_effect_and_risk_classification_matches_policy(self) -> None:
        writes = set(self.policy["write_operations"])
        billable = set(self.policy["billable_operations"])
        terms = set(self.policy["terms_required_operations"])
        secret = set(self.policy["secret_bearing_results"])
        dry_run = set(self.policy["native_dry_run_operations"])
        destructive = set(self.policy["destructive_operations"])
        self.assertEqual({op["operation_id"] for op in self.operations if op["write"]}, writes)
        for op in self.operations:
            op_id = op["operation_id"]
            self.assertEqual(op["effect"], "write" if op_id in writes else "read")
            self.assertEqual(op["billable"], op_id in billable)
            self.assertEqual(op["terms_required"], op_id in terms)
            self.assertEqual(op["secret_bearing_result"], op_id in secret)
            self.assertEqual(op["native_dry_run"], op_id in dry_run)
            self.assertEqual(op["destructive"], op_id in destructive)
            self.assertEqual(op["risk_profile"]["high_risk"], op_id in writes)

    def test_snapshot_contract_is_complete(self) -> None:
        policy = self.policy["write_snapshot_policy"]
        self.assertEqual(set(policy), set(self.policy["write_operations"]))
        for op_id in self.policy["write_operations"]:
            self.assertEqual(self.by_id[op_id]["snapshot_plan"], policy[op_id])
        self.assertEqual(policy["domainRenew"]["before_state_operation_id"], "getDomain")
        self.assertEqual(policy["domainRenew"]["readback_operation_id"], "getDomain")
        self.assertEqual(policy["dnsDelete"]["before_state_operation_id"], "getDnsRecordById")
        self.assertEqual(policy["webhookDelete"]["readback_operation_id"], "webhookList")

    def test_fixed_command_surface_is_unique(self) -> None:
        pattern = re.compile(
            r"^porkbun (utility|pricing|api-key|domain|dns|ssl|email-hosting|marketplace|account|webhooks) [a-z0-9-]+$"
        )
        commands = [op["command"] for op in self.operations]
        self.assertEqual(len(commands), 66)
        self.assertEqual(len(set(commands)), 66)
        self.assertTrue(all(pattern.fullmatch(command) for command in commands))

    def test_coverage_document_matches_inventory(self) -> None:
        coverage = self.coverage_path.read_text(encoding="utf-8")
        rows = [line for line in coverage.splitlines() if line.startswith("| ")][1:]
        self.assertEqual(len(rows), 66)
        for op in self.operations:
            self.assertIn(f"`{op['command']}`", coverage)
            self.assertIn(f"| {op['operation_id']} |", coverage)
        self.assertIn("GET / POST: 25 / 41", coverage)
        self.assertIn(f"Spec SHA-256: `{self.EXPECTED_SHA}`", coverage)
        self.assertNotIn("Last generated (UTC)", coverage)

    def test_command_reference_and_wrapper_match_runtime_surface(self) -> None:
        command_reference = (self.root / "docs" / "command_reference.md").read_text(encoding="utf-8")
        wrapper = _resolve_skill_wrapper(self.root).read_text(encoding="utf-8")
        for op in self.operations:
            self.assertIn(f"`{op['command']}", command_reference)
        self.assertIn("porkbun --output json", wrapper)
        self.assertIn("--plan-out", wrapper)
        self.assertIn("--plan-in", wrapper)
        self.assertIn("--ack-spend", wrapper)
        self.assertIn("--ack-terms", wrapper)
        self.assertIn("--ack-secret", wrapper)
        self.assertIn("--secret-out", wrapper)

    def test_request_bodies_preserve_official_schemas(self) -> None:
        for path_item in self.spec["paths"].values():
            for method_obj in path_item.values():
                if not isinstance(method_obj, dict) or not method_obj.get("operationId"):
                    continue
                raw_body = method_obj.get("requestBody")
                if not isinstance(raw_body, dict):
                    continue
                op = self.by_id[method_obj["operationId"]]
                content = raw_body.get("content", {})
                self.assertEqual(op["request"]["required"], bool(raw_body.get("required")))
                self.assertEqual(op["request"]["media_types"], sorted(content))
                for media_type, media_obj in content.items():
                    self.assertEqual(op["request"]["schemas"][media_type]["full_schema"], media_obj["schema"])

    def test_generation_is_byte_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            tmp = Path(temporary)
            outputs: list[tuple[Path, Path]] = []
            for suffix in ("a", "b"):
                inventory = tmp / f"{suffix}.json"
                coverage = tmp / f"{suffix}.md"
                subprocess.run(
                    [
                        sys.executable,
                        str(self.root / "scripts" / "generate_inventory.py"),
                        "--spec",
                        str(self.spec_path),
                        "--policy",
                        str(self.policy_path),
                        "--inventory",
                        str(inventory),
                        "--coverage",
                        str(coverage),
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                outputs.append((inventory, coverage))
            self.assertEqual(outputs[0][0].read_bytes(), outputs[1][0].read_bytes())
            self.assertEqual(outputs[0][1].read_bytes(), outputs[1][1].read_bytes())
            self.assertEqual(outputs[0][0].read_bytes(), self.inventory_path.read_bytes())
            self.assertEqual(outputs[0][1].read_bytes(), self.coverage_path.read_bytes())

    def test_packaged_resources_match_sources(self) -> None:
        package = self.root / "src" / "qwayk_porkbun_safe_agent_cli" / "resources"
        self.assertEqual((package / "operation_inventory.json").read_bytes(), self.inventory_path.read_bytes())
        self.assertEqual((package / "porkbun-openapi-v3.9.json").read_bytes(), self.spec_path.read_bytes())


if __name__ == "__main__":
    unittest.main()
