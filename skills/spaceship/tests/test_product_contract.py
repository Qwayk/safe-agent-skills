from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from spaceship_safe_agent_cli import operations
from spaceship_safe_agent_cli.cli import main
from spaceship_safe_agent_cli.config import OFFICIAL_BASE_URL


class TestProductContract(unittest.TestCase):
    @staticmethod
    def _root() -> Path:
        return Path(__file__).resolve().parents[1]

    def test_coverage_has_40_shipped_rows_with_38_and_2_statuses(self) -> None:
        coverage = (self._root() / "docs" / "api_coverage.md").read_text(encoding="utf-8")
        rows = [line for line in coverage.splitlines() if line.startswith("|")][2:]
        self.assertEqual(len(rows), 40)
        self.assertEqual(sum("Implemented / live-unverified" in row for row in rows), 38)
        self.assertEqual(sum("Developer preview — unavailable" in row for row in rows), 2)

        by_operation = {spec.operation_id: spec for spec in operations.OFFICIAL_OPERATIONS}
        self.assertEqual(set(by_operation), {row.split("|")[4].strip() for row in rows})
        for row in rows:
            cells = [cell.strip() for cell in row.split("|")[1:-1]]
            operation_id = cells[3]
            shipped_command = cells[4]
            expected = "qwayk-spaceship-safe-agent-cli " + " ".join(by_operation[operation_id].command)
            self.assertEqual(shipped_command, expected)

    def test_examples_match_runtime_plan_and_receipt_shapes(self) -> None:
        examples = self._root() / "docs" / "examples"
        plan = json.loads((examples / "plan.example.json").read_text(encoding="utf-8"))
        receipt = json.loads((examples / "receipt.example.json").read_text(encoding="utf-8"))

        self.assertEqual(plan["plan_kind"], "deterministic_only")
        self.assertEqual(len(plan["plan_integrity"]), 64)
        self.assertIn("critical_request_fields", plan)
        self.assertIn("financial_recheck", plan)
        self.assertIn("required_acknowledgements", plan)
        self.assertIn("snapshot", plan)

        self.assertFalse(receipt["dry_run"])
        self.assertFalse(receipt["refused"])
        self.assertEqual(receipt["transport"]["status_code"], 204)
        self.assertEqual(receipt["transport"]["status_label"], "completed")
        self.assertTrue(receipt["request_body"]["redacted"])
        self.assertIn("verification", receipt)

    def test_fixed_host_and_missing_auth_error_do_not_leak_values(self) -> None:
        self.assertEqual(OFFICIAL_BASE_URL, "https://spaceship.dev/api")
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            key_canary = "VISIBLE_" + "TEST_KEY"
            env_path.write_text("SPACESHIP_API_KEY=" + key_canary + "\n", encoding="utf-8")
            output = io.StringIO()
            with redirect_stdout(output):
                rc = main(["--env-file", str(env_path), "--no-artifacts", "domains", "list"])
            rendered = output.getvalue()
            payload = json.loads(rendered)
            self.assertEqual(rc, 1)
            self.assertEqual(payload["error_type"], "RuntimeError")
            self.assertNotIn(key_canary, rendered)
            self.assertNotIn("X-API-Key", rendered)
            _, end = json.JSONDecoder().raw_decode(rendered)
            self.assertEqual(rendered[end:].strip(), "")

    def test_wrapper_uses_public_slug_and_fixed_cli_boundary(self) -> None:
        wrapper_path = self._root() / "skills" / "spaceship-safe-cli" / "SKILL.md"
        if not wrapper_path.exists():
            wrapper_path = self._root() / "SKILL.md"
        wrapper = wrapper_path.read_text(encoding="utf-8")
        self.assertIn("name: spaceship", wrapper)
        self.assertIn("qwayk-spaceship-safe-agent-cli --output json", wrapper)
        self.assertIn("https://spaceship.dev/api", wrapper)
        self.assertIn("domains delete <domain>", wrapper)
        self.assertIn("domains personal-nameservers get-host", wrapper)
        self.assertIn("--ack-no-snapshot", wrapper)


if __name__ == "__main__":
    unittest.main()
