from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "generate_inventory.py"
OPERATIONS = ROOT / "src" / "sav_domain_api" / "operations_generated.py"
DOCS = ROOT / "docs" / "api_coverage.md"


def _load_generated_operations() -> list[dict[str, object]]:
    spec = importlib.util.spec_from_file_location("sav_domain_api_inventory", OPERATIONS)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load generated operations module.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    payload = module.OPERATIONS  # type: ignore[attr-defined]
    return payload["operations"]  # type: ignore[index]


def _resolve_wrapper_path(tool_root: Path) -> Path:
    source = tool_root / "skills" / "sav" / "SKILL.md"
    public = tool_root / "SKILL.md"
    source_exists = source.exists()
    public_exists = public.exists()
    if source_exists and public_exists:
        raise AssertionError(
            "expected exactly one wrapper file path, but both exist: "
            f"{source} and {public}"
        )
    if not source_exists and not public_exists:
        raise AssertionError(
            "expected exactly one wrapper file path, but neither exists: "
            f"{source} or {public}"
        )
    return source if source_exists else public


def _parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise AssertionError("SKILL wrapper is missing frontmatter start marker")
    try:
        end = lines[1:].index("---") + 1
    except ValueError as exc:
        raise AssertionError("SKILL wrapper is missing frontmatter end marker") from exc
    frontmatter_lines = lines[1:end]
    body = "\n".join(lines[end + 1 :])
    if not frontmatter_lines:
        raise AssertionError("SKILL wrapper frontmatter is empty")

    frontmatter: dict[str, str] = {}
    for line in frontmatter_lines:
        if ":" not in line:
            raise AssertionError(f"invalid frontmatter line in SKILL wrapper: {line}")
        key, value = line.split(":", 1)
        frontmatter[key.strip()] = value.strip()

    return frontmatter, body


class TestGenerateInventory(unittest.TestCase):
    def test_generate_and_check_are_clean(self) -> None:
        subprocess.run(
            [sys.executable, str(SCRIPT)], check=True, cwd=ROOT, capture_output=True, text=True
        )
        check = subprocess.run(
            [sys.executable, str(SCRIPT), "--check"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(check.returncode, 0, msg=check.stderr)

    def test_command_ledger_is_deterministic_and_complete(self) -> None:
        self.assertTrue(SCRIPT.exists())
        subprocess.run(
            [sys.executable, str(SCRIPT)], check=True, cwd=ROOT, capture_output=True, text=True
        )
        operations = _load_generated_operations()
        self.assertEqual(len(operations), 12)

        command_order = [
            "domains active",
            "sales recent-auction",
            "sales recent-premium",
            "pricing list",
            "domains remove-from-sale",
            "domains submit-transfer-code",
            "domains set-auto-renewal",
            "domains set-sale-price",
            "domains set-nameservers",
            "domains set-privacy",
            "domains set-whois-contacts",
            "domains list-external-sale",
        ]
        self.assertEqual([o["command_path"] for o in operations], command_order)
        reads = [o for o in operations if o["kind"] == "read"]
        writes = [o for o in operations if o["kind"] == "write"]
        self.assertEqual(len(reads), 4)
        self.assertEqual(len(writes), 8)

        pricing = next(o for o in operations if o["operation_id"] == "get_domain_pricing")
        self.assertEqual(pricing["required_params"], [])

    def test_docs_track_expected_rows(self) -> None:
        self.assertTrue(DOCS.exists())
        doc_text = DOCS.read_text(encoding="utf-8")
        for token in [
            "domains active",
            "sales recent-auction",
            "sales recent-premium",
            "pricing list",
            "domains remove-from-sale",
            "domains submit-transfer-code",
            "domains set-auto-renewal",
            "domains set-sale-price",
            "domains set-nameservers",
            "domains set-privacy",
            "domains set-whois-contacts",
            "domains list-external-sale",
        ]:
            self.assertIn(f"`sav {token}`", doc_text)

    def test_inventory_has_only_expected_command_paths(self) -> None:
        self.assertTrue(SCRIPT.exists())
        subprocess.run(
            [sys.executable, str(SCRIPT)], check=True, cwd=ROOT, capture_output=True, text=True
        )
        operations = _load_generated_operations()
        command_paths = [str(o["command_path"]) for o in operations]
        self.assertEqual(len(command_paths), 12)
        for command_path in command_paths:
            self.assertNotIn("raw", command_path)
            self.assertNotIn("request", command_path)
            self.assertNotIn("arbitrary", command_path)

        expected = [
            "domains active",
            "sales recent-auction",
            "sales recent-premium",
            "pricing list",
            "domains remove-from-sale",
            "domains submit-transfer-code",
            "domains set-auto-renewal",
            "domains set-sale-price",
            "domains set-nameservers",
            "domains set-privacy",
            "domains set-whois-contacts",
            "domains list-external-sale",
        ]
        self.assertEqual(command_paths, expected)
        command_ids = {
            str(op["command_path"]): str(op["operation_id"]) for op in operations
        }
        for command, operation in (
            ("domains set-sale-price", "update_domain_for_sale_price"),
            ("domains set-nameservers", "update_domain_nameservers"),
            ("pricing list", "get_domain_pricing"),
        ):
            self.assertEqual(command_ids[command], operation)

    def test_examples_match_runtime_command_contract(self) -> None:
        examples_dir = ROOT / "docs" / "examples"
        self.assertTrue(examples_dir.exists())
        examples = {
            "plan": examples_dir / "plan.example.json",
            "read": examples_dir / "read-active.example.json",
            "receipt": examples_dir / "receipt.example.json",
        }
        self.assertTrue(all(path.exists() for path in examples.values()))

        operations = _load_generated_operations()
        contract = {
            f"sav {op['command_path']!s}": str(op["operation_id"]) for op in operations
        }

        plan_payload = json.loads(examples["plan"].read_text(encoding="utf-8"))
        self.assertIn("command", plan_payload)
        self.assertIn("operation_id", plan_payload)
        self.assertEqual(plan_payload["command"], "sav domains set-whois-contacts")
        self.assertEqual(contract[plan_payload["command"]], plan_payload["operation_id"])
        self.assertIn("plan", plan_payload)
        self.assertEqual(plan_payload["plan"]["operation_id"], plan_payload["operation_id"])
        self.assertEqual(
            plan_payload["plan"]["required_acks"],
            ["--apply", "--yes", "--ack-no-snapshot", "--ack-high-risk"],
        )

        read_payload = json.loads(examples["read"].read_text(encoding="utf-8"))
        self.assertIn("command", read_payload)
        self.assertIn("operation_id", read_payload)
        self.assertEqual(read_payload["command"], "sav domains active")
        self.assertEqual(contract[read_payload["command"]], read_payload["operation_id"])
        self.assertIn("api_host", read_payload)

        receipt_payload = json.loads(examples["receipt"].read_text(encoding="utf-8"))
        self.assertIn("receipt", receipt_payload)
        self.assertIn("command", receipt_payload["receipt"])
        self.assertIn("operation_id", receipt_payload["receipt"])
        self.assertEqual(receipt_payload["receipt"]["command"], "sav domains set-whois-contacts")
        self.assertEqual(
            contract[receipt_payload["receipt"]["command"]],
            receipt_payload["receipt"]["operation_id"],
        )
        self.assertIn("receipt", receipt_payload)
        self.assertEqual(receipt_payload["receipt"]["provider_response_only"], True)
        self.assertEqual(receipt_payload["receipt"]["rollback_available"], False)

    def test_wrapper_contract_is_in_single_active_layout(self) -> None:
        wrapper_path = _resolve_wrapper_path(ROOT)
        text = wrapper_path.read_text(encoding="utf-8")
        required_contract_tokens = [
            "12 operations in the official SAV Domain APIs v1 collection",
            "domain registration",
            "Start with a read such as `sav domains active` or `sav pricing list`",
            "Changes always save a private plan",
            "--apply --yes --plan-in --ack-no-snapshot --ack-high-risk",
            "schema_version: 2",
            "HMAC-SHA256",
            "Transfer writes accept only `--auth-code-file` for dry-run",
            "The transfer authorization code has no environment or literal command-line fallback",
            "Never follow redirects. Treat every non-2xx provider response as a failure",
            "provider_accepted",
            "provider_response_only",
            "durable_state_verified",
            "Require finite positive timeouts",
            "strict domain and nameserver values",
            "Never print secret-like values",
            "Do not claim restore, rollback, or backup support for writes",
        ]

        def assert_complete_contract(path: Path) -> None:
            frontmatter, body = _parse_frontmatter(path.read_text(encoding="utf-8"))
            self.assertEqual(frontmatter.get("name"), "sav")
            self.assertIn("read SAV account domains", frontmatter.get("description", ""))
            for token in required_contract_tokens:
                self.assertIn(token, body)

        assert_complete_contract(wrapper_path)

        with TemporaryDirectory() as tmp:
            temp_root = Path(tmp)
            missing_root = temp_root / "missing"
            missing_root.mkdir()
            with self.assertRaisesRegex(AssertionError, "neither exists"):
                _resolve_wrapper_path(missing_root)

            both_root = temp_root / "both"
            both_root.mkdir()
            source_root = both_root / "skills" / "sav"
            source_root.mkdir(parents=True)
            (source_root / "SKILL.md").write_text("---\nname: test\n---\n", encoding="utf-8")
            (both_root / "SKILL.md").write_text("---\nname: test\n---\n", encoding="utf-8")
            with self.assertRaisesRegex(AssertionError, "both exist"):
                _resolve_wrapper_path(both_root)

            public_root = temp_root / "public"
            public_root.mkdir()
            public_wrapper = public_root / "SKILL.md"
            public_wrapper.write_text(text, encoding="utf-8")
            self.assertEqual(_resolve_wrapper_path(public_root), public_wrapper)
            assert_complete_contract(public_wrapper)
