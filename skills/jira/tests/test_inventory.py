from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import generate_inventory
from jira_safe_agent_cli.audit_log import AuditLogger
from jira_safe_agent_cli.config import Config
from jira_safe_agent_cli.operations import build_plan, load_inventory, redact

ROOT = Path(__file__).resolve().parents[1]


class InventoryTests(unittest.TestCase):
    def test_pinned_boundary_and_statuses(self) -> None:
        inventory = load_inventory()
        self.assertEqual(inventory["operation_count"], 721)
        self.assertEqual(inventory["unique_method_path_count"], 721)
        self.assertEqual([spec["operation_count"] for spec in inventory["specs"]], [616, 105])
        self.assertEqual(
            inventory["coverage_status_counts"],
            {
                "access-gated-connect": 17,
                "access-gated-forge": 4,
                "developer-preview": 3,
                "implemented-deprecated": 37,
                "implemented-live-unverified": 642,
                "implemented-oauth-only": 8,
                "intentionally-excluded": 10,
            },
        )
        self.assertEqual(inventory["kind_counts"], {"read": 361, "write": 360})
        self.assertEqual(inventory["high_risk_write_count"], 277)

    def test_every_write_matches_the_auditable_high_risk_rules(self) -> None:
        inventory = load_inventory()
        by_command = {operation["command"]: operation for operation in inventory["operations"]}
        for operation in inventory["operations"]:
            expected = generate_inventory.high_risk_reasons(
                kind=operation["kind"],
                method=operation["method"],
                path=operation["path"],
                command=operation["command"],
                operation_id=operation["operation_id"],
                summary=operation["summary"],
            )
            self.assertEqual(operation["high_risk_reasons"], expected)
            self.assertEqual(operation["high_risk"], bool(expected))
            if operation["kind"] == "write" and operation["method"] == "DELETE":
                self.assertIn("destructive", expected)
        for command in generate_inventory.HIGH_RISK_OPERATION_OVERRIDES:
            self.assertTrue(by_command[command]["high_risk"], command)

    def test_reviewed_project_administration_commands_require_stronger_approval(self) -> None:
        by_command = {
            operation["command"]: operation for operation in load_inventory()["operations"]
        }
        self.assertEqual(
            generate_inventory.PROJECT_ADMINISTRATION_COMMANDS,
            {
                "assign-projects-to-custom-field-context",
                "create-component",
                "create-related-work",
                "create-version",
                "update-component",
                "update-related-work",
                "update-version",
            },
        )
        for command in generate_inventory.PROJECT_ADMINISTRATION_COMMANDS:
            self.assertTrue(by_command[command]["high_risk"], command)
            self.assertIn("project-administration", by_command[command]["high_risk_reasons"])

    def test_generation_matches_packaged_inventory(self) -> None:
        self.assertEqual(generate_inventory.build_inventory(), load_inventory())

    def test_every_fixed_command_is_unique_and_covered(self) -> None:
        inventory = load_inventory()
        commands = [operation["full_command"] for operation in inventory["operations"]]
        self.assertEqual(len(commands), len(set(commands)))
        coverage = (ROOT / "docs/api_coverage.md").read_text(encoding="utf-8")
        for command in commands:
            self.assertIn(f"`{command}`", coverage)
        self.assertNotIn("raw-request", " ".join(commands))

    def test_examples_are_valid_json_and_contain_no_real_secret(self) -> None:
        for path in sorted((ROOT / "docs/examples").glob("*.json")) + sorted(
            (ROOT / "examples").glob("*.json")
        ):
            json.loads(path.read_text(encoding="utf-8"))
            text = path.read_text(encoding="utf-8").lower()
            self.assertNotIn("authorization: bearer", text)
            self.assertNotIn("test-secret-token", text)

    def test_camel_case_secret_keys_are_redacted(self) -> None:
        self.assertEqual(
            redact(
                {
                    "accessToken": "secret",
                    "refresh_token": "secret",
                    "apiToken": "secret",
                    "secretToken": "secret",
                    "csrfToken": "secret",
                    "clientToken": "secret",
                    "personalToken": "secret",
                    "unknownTokens": ["secret"],
                    "name": "visible",
                }
            ),
            {
                "accessToken": "***REDACTED***",
                "refresh_token": "***REDACTED***",
                "apiToken": "***REDACTED***",
                "secretToken": "***REDACTED***",
                "csrfToken": "***REDACTED***",
                "clientToken": "***REDACTED***",
                "personalToken": "***REDACTED***",
                "unknownTokens": "***REDACTED***",
                "name": "visible",
            },
        )

    def test_pagination_tokens_are_preserved(self) -> None:
        self.assertEqual(
            redact(
                {
                    "nextPageToken": "next-123",
                    "pageToken": "page-123",
                    "continuationToken": "continue-123",
                }
            ),
            {
                "nextPageToken": "next-123",
                "pageToken": "page-123",
                "continuationToken": "continue-123",
            },
        )

    def test_audit_redaction_uses_the_same_cursor_allowlist(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "audit.jsonl"
            audit = AuditLogger(path=str(path), enabled=True)
            audit.write(
                "test",
                {
                    "nextPageToken": "visible-cursor",
                    "pageToken": "visible-page",
                    "continuationToken": "visible-continuation",
                    "csrfToken": "secret",
                    "clientToken": "secret",
                    "personalToken": "secret",
                    "unknownTokens": ["secret"],
                },
            )
            audit.close()
            payload = json.loads(path.read_text(encoding="utf-8"))["payload"]
            self.assertEqual(payload["nextPageToken"], "visible-cursor")
            self.assertEqual(payload["pageToken"], "visible-page")
            self.assertEqual(payload["continuationToken"], "visible-continuation")
            for key in ("csrfToken", "clientToken", "personalToken", "unknownTokens"):
                self.assertEqual(payload[key], "***REDACTED***")

    def test_every_callable_operation_can_build_a_fixed_request_plan(self) -> None:
        config = Config(
            base_url="https://example.atlassian.net",
            email=None,
            api_token=None,
            oauth_access_token=None,
            timeout_s=30,
        )
        planned = 0
        with tempfile.TemporaryDirectory() as directory:
            body = Path(directory) / "body.json"
            body.write_text("{}", encoding="utf-8")
            upload = Path(directory) / "upload.txt"
            upload.write_text("test", encoding="utf-8")
            for operation in load_inventory()["operations"]:
                if not operation["callable_with_supported_auth"]:
                    continue
                values: dict[str, object] = {
                    "body_file": None,
                    "file": None,
                    "form": None,
                    "content_type": None,
                }
                for parameter in operation["parameters"]:
                    destination = parameter["cli_flag"][2:].replace("-", "_")
                    if parameter["required"]:
                        if parameter["free_form_object"]:
                            value = ["property=value"]
                        elif parameter["array"]:
                            value: object = ["x"]
                        elif parameter["schema_type"] == "integer":
                            value = 1
                        elif parameter["schema_type"] == "number":
                            value = 1.0
                        elif parameter["schema_type"] == "boolean":
                            value = True
                        else:
                            value = "x"
                        values[destination] = value
                    else:
                        values[destination] = None
                if operation["request_body_required"]:
                    if "multipart/form-data" in operation["request_content_types"] and (
                        "application/json" not in operation["request_content_types"]
                    ):
                        values["file"] = [f"file={upload}"]
                    else:
                        values["body_file"] = str(body)
                plan = build_plan(SimpleNamespace(**values), config, operation)
                self.assertEqual(plan["surface"], operation["surface"])
                self.assertNotIn("{", plan["path"])
                planned += 1
        self.assertEqual(planned, 687)


if __name__ == "__main__":
    unittest.main()
