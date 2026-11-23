from __future__ import annotations

import base64
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace

from azure_safe_agent_cli.cli import main
from azure_safe_agent_cli.generated_runtime import _poll_azure_async_operation, _safe_response


class _FakeResponse:
    def __init__(self, payload: dict, headers: dict[str, str] | None = None) -> None:
        self._payload = payload
        self.headers = headers or {}
        self.status = 200
        self.url = "https://management.azure.com/poll"

    def json(self) -> dict:
        return self._payload


class _FakeClient:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def request(self, method: str, url: str, **kwargs: object) -> _FakeResponse:
        _ = kwargs
        self.calls.append(f"{method} {url}")
        return _FakeResponse({"status": "Succeeded"})


class TestGeneratedRuntime(unittest.TestCase):
    def _env(self, root: Path, extra: str = "") -> Path:
        env = root / ".env"
        env.write_text(
            "\n".join(
                [
                    "AZURE_MANAGEMENT_ENDPOINT=https://management.azure.com",
                    "AZURE_API_TOKEN=fake-token-for-tests",
                    extra,
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        return env

    def test_inventory_summary_command(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["inventory", "summary"])
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertGreaterEqual(payload["summary"]["selected_operations"], 25000)

    def test_generated_read_requires_input_json_and_emits_one_json_error(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["resources-management", "resourcegroups_list_2025-04-01_148560"])
        self.assertEqual(rc, 1)
        payload = json.loads(buf.getvalue())
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")

    def test_write_defaults_to_dry_run_plan(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env = self._env(root)
            input_json = root / "input.json"
            input_json.write_text(
                json.dumps({"subscriptionId": "sub-1", "resourceGroupName": "rg-1", "body": {"location": "eastus"}}),
                encoding="utf-8",
            )
            plan = root / "plan.json"
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env),
                        "--plan-out",
                        str(plan),
                        "resources-management",
                        "resourcegroups_createorupdate_2025-04-01_148562",
                        "--input-json",
                        str(input_json),
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertTrue(plan.exists())
            self.assertIn("no_snapshot", payload["risk_categories"])

    def test_allowlist_refusal_is_safe_noop(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env = self._env(root, "AZURE_ALLOWED_SUBSCRIPTIONS=sub-allowed")
            input_json = root / "input.json"
            input_json.write_text(json.dumps({"subscriptionId": "sub-denied"}), encoding="utf-8")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env),
                        "resources-management",
                        "resourcegroups_list_2025-04-01_148560",
                        "--input-json",
                        str(input_json),
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertIn("AZURE_ALLOWED_SUBSCRIPTIONS", payload["reasons"][0])

    def test_apply_without_plan_is_safe_noop_refusal(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env = self._env(root)
            input_json = root / "input.json"
            input_json.write_text(
                json.dumps({"subscriptionId": "sub-1", "resourceGroupName": "rg-1", "body": {"location": "eastus"}}),
                encoding="utf-8",
            )
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env),
                        "--apply",
                        "--yes",
                        "resources-management",
                        "resourcegroups_createorupdate_2025-04-01_148562",
                        "--input-json",
                        str(input_json),
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertIn("--plan-in", payload["reasons"][0])

    def test_azure_async_operation_header_is_polled(self) -> None:
        client = _FakeClient()
        result = _poll_azure_async_operation(
            client=client,  # type: ignore[arg-type]
            response=_FakeResponse({}, {"Azure-AsyncOperation": "https://management.azure.com/poll/1"}),
            headers={"Authorization": "Bearer fake-token"},
            redaction_values=["fake-token"],
        )
        self.assertTrue(result["polling_performed"])
        self.assertEqual(result["status"], "succeeded")
        self.assertEqual(client.calls, ["GET https://management.azure.com/poll/1"])

    def test_sensitive_read_response_redacts_generic_value_fields(self) -> None:
        response = _FakeResponse(
            {
                "value": "returned-secret",
                "items": [{"name": "credential-one", "value": "nested-secret"}],
                "plain": "also-hidden",
            }
        )
        payload = _safe_response(response, redaction_values=[], sensitive_read=True)
        self.assertEqual(payload["response"]["value"], "***REDACTED***")
        self.assertEqual(payload["response"]["items"][0]["name"], "***REDACTED***")
        self.assertEqual(payload["response"]["items"][0]["value"], "***REDACTED***")
        self.assertEqual(payload["response"]["plain"], "***REDACTED***")


class TestConnectedPlans(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.settings = self.root / "azure settings.env"
        self.settings.write_text("AZURE_API_TOKEN=fixture-one\n")
        self.input = self.root / "request.json"
        self.input.write_text(json.dumps({
            "subscriptionId": "test-sub", "resourceGroupName": "test-group", "vmName": "fixture",
        }))
        self.plan = self.root / "plan.json"
        self.receipt = self.root / "receipt.json"
        self.start = [
            "compute-management", "virtualmachines_start_2026-03-01_40109",
            "--input-json", str(self.input),
        ]
        self.flags = ["--apply", "--yes", "--plan-in", str(self.plan),
                      "--ack-no-snapshot", "--ack-spend-money", "--receipt-out", str(self.receipt)]
        mock = patch("azure_safe_agent_cli.generated_runtime.HttpClient")
        self.send = mock.start().return_value.request
        self.addCleanup(mock.stop)

    def run_cli(self, *args):
        output = io.StringIO()
        with redirect_stdout(output):
            code = main(["--no-artifacts", "--env-file", str(self.settings), *args])
        return code, json.loads(output.getvalue())

    def save(self, *, bind=True):
        flags = ["--bind-azure"] if bind else []
        code, result = self.run_cli(*self.start, *flags, "--plan-out", str(self.plan))
        self.assertEqual(0, code, result)
        self.assertIs(bind, result["approval_ready"])
        self.send.assert_not_called()
        return result

    def test_live_write_requires_a_plan_tied_to_azure(self):
        self.save(bind=False)
        _, refusal = self.run_cli(*self.flags, *self.start)
        self.assertIn("--bind-azure", refusal["reasons"][0])
        self.send.assert_not_called()

    def test_current_identity_endpoint_and_approval_rules_are_checked(self):
        self.save()
        original = self.settings.read_text()
        for settings in (
            "AZURE_API_TOKEN=fixture-two\n",
            original + "AZURE_MANAGEMENT_ENDPOINT=https://changed.example.invalid\n",
        ):
            self.settings.write_text(settings)
            _, refusal = self.run_cli(*self.flags, *self.start)
            self.assertIn("identity, subscription or endpoint", refusal["reasons"][0])
        self.settings.write_text(original)
        plan = json.loads(self.plan.read_text())
        plan["risk_categories"] = []
        self.plan.write_text(json.dumps(plan))
        _, refusal = self.run_cli(*self.flags, *self.start)
        self.assertIn("approval rules", refusal["reasons"][0])
        self.send.assert_not_called()

    def test_spending_approval_and_azure_wait_time(self):
        self.save()
        missing_approval = [flag for flag in self.flags if flag != "--ack-spend-money"]
        _, refusal = self.run_cli(*missing_approval, *self.start)
        self.assertIn("--ack-spend-money", refusal["reasons"][0])
        self.send.assert_not_called()
        response = _FakeResponse({}, {
            "Azure-AsyncOperation": "https://management.azure.com/operations/demo?api-version=1",
            "Retry-After": "30",
        })
        response.status = 202
        self.send.return_value = response
        code, result = self.run_cli(*self.flags, *self.start)
        self.assertEqual(0, code)
        self.send.assert_called_once()
        self.assertFalse(self.send.call_args.kwargs.get("retries"))
        self.assertIsNone(result["applied"])
        receipt = json.loads(self.receipt.read_text())
        self.assertEqual("pending", receipt["verification_status"])
        self.assertEqual(30, receipt["azure_async_polling"]["retry_after_seconds"])

    def test_failed_and_lost_status_replies_keep_receipts(self):
        self.save()
        accepted = _FakeResponse({}, {"Azure-AsyncOperation": "https://management.azure.com/operations/demo"})
        accepted.status = 202
        self.send.side_effect = [accepted, _FakeResponse({"status": "Failed"})]
        code, result = self.run_cli(*self.flags, *self.start)
        self.assertEqual(1, code)
        self.assertFalse(result["applied"])
        self.assertEqual("operation_failed", json.loads(self.receipt.read_text())["verification_status"])

        self.send.side_effect = [accepted, RuntimeError("lost reply")]
        code, result = self.run_cli(*self.flags, *self.start)
        self.assertEqual(1, code)
        self.assertIsNone(result["applied"])
        self.assertEqual("outcome_unknown", json.loads(self.receipt.read_text())["verification_status"])

    def test_status_credentials_stay_on_the_approved_host(self):
        self.save()
        reply = _FakeResponse({}, {"Azure-AsyncOperation": "https://other.example.invalid/task"})
        reply.status = 202
        self.send.return_value = reply
        _, result = self.run_cli(*self.flags, *self.start)
        self.send.assert_called_once()
        self.assertEqual("pending", result["receipt"]["verification_status"])
        self.assertFalse(result["receipt"]["azure_async_polling"]["polling_performed"])

    def test_location_and_full_azure_scope_must_match_lists(self):
        self.settings.write_text("AZURE_ALLOWED_LOCATIONS=eastus\nAZURE_ALLOWED_SUBSCRIPTIONS=test-sub\n")
        self.input.write_text(json.dumps({
            "subscriptionId": "test-sub", "resourceGroupName": "test-group",
            "body": {"location": "westus"},
        }))
        _, refused = self.run_cli("resources-management", "resourcegroups_createorupdate_2025-04-01_148562",
                                  "--input-json", str(self.input))
        self.assertIn("AZURE_ALLOWED_LOCATIONS", refused["reasons"][0])
        self.input.write_text(json.dumps({
            "scope": "/subscriptions/other-sub/resourceGroups/test-group", "roleAssignmentName": "fixture",
        }))
        _, refused = self.run_cli(
            "authorization-management", "roleassignments_create_2022-04-01_16927",
            "--input-json", str(self.input),
        )
        self.assertIn("AZURE_ALLOWED_SUBSCRIPTIONS", refused["reasons"][0])
        self.send.assert_not_called()

    def test_sign_in_uses_the_requested_subscription_and_token_resource(self):
        self.settings.write_text("AZURE_DATA_PLANE_ENDPOINT=https://example.vault.azure.net\nAZURE_SUBSCRIPTION_ID=test-sub\n")
        self.input.write_text(json.dumps({"secret-name": "fixture", "secret-version": "fixture-version"}))
        self.send.return_value = _FakeResponse({"value": "fixture-secret"})
        responses = [
            SimpleNamespace(returncode=0, stdout=json.dumps({"id": "test-sub", "tenantId": "test-tenant"})),
            SimpleNamespace(returncode=0, stdout=json.dumps({"accessToken": "fixture-cli-token", "tenant": "test-tenant"})),
        ]
        with patch("azure_safe_agent_cli.azure_auth.subprocess.run", side_effect=responses) as az:
            code, result = self.run_cli("keyvault-data-plane", "getsecret_2025-07-01_83451",
                                        "--input-json", str(self.input))
        self.assertEqual(0, code, result)
        self.assertIn("--subscription", az.call_args_list[0].args[0])
        self.assertIn("test-sub", az.call_args_list[0].args[0])
        self.assertIn("https://vault.azure.net", az.call_args_list[1].args[0])
        self.assertEqual("Bearer fixture-cli-token", self.send.call_args.kwargs["headers"]["Authorization"])
        self.assertEqual("***REDACTED***", result["response"]["value"])

    def test_read_can_use_the_imported_token_without_environment_token(self):
        self.settings.write_text("")
        source = self.root / "credential.json"
        source.write_text(json.dumps({"accessToken": "fixture-imported-token"}))
        code, result = self.run_cli("auth", "token", "set", "--file", str(source))
        self.assertEqual(0, code, result)
        self.send.return_value = _FakeResponse({"value": []})
        code, result = self.run_cli("resources-management", "resourcegroups_list_2025-04-01_148560",
                                   "--input-json", str(self.input))
        self.assertEqual(0, code, result)
        self.assertEqual("Bearer fixture-imported-token", self.send.call_args.kwargs["headers"]["Authorization"])

    def test_uses_verified_cli_selection_without_binding_to_a_short_lived_token(self):
        self.settings.write_text("AZURE_SUBSCRIPTION_ID=test-sub\n")
        self.input.write_text(json.dumps({"resourceGroupName": "test-group", "vmName": "fixture"}))

        def cli_outputs(suffix):
            claims = base64.urlsafe_b64encode(json.dumps({"oid": "test-object", "tid": "test-tenant"}).encode()).decode().rstrip("=")
            return [
                json.dumps("https://management.azure.com/"),
                json.dumps({"id": "test-sub", "tenantId": "test-tenant"}),
                json.dumps({"accessToken": f"fixture.{claims}.{suffix}", "tenant": "test-tenant", "subscription": "test-sub"}),
            ]

        replies = [SimpleNamespace(returncode=0, stdout=data) for data in (*cli_outputs("old"), *cli_outputs("new"))]
        with patch("azure_safe_agent_cli.azure_auth.subprocess.run", side_effect=replies) as az:
            preview = self.save()
            self.assertEqual("test-sub", preview["plan"]["connection"]["subscription"])
            self.assertEqual("test-object", preview["plan"]["connection"]["identity"])
            self.send.return_value = _FakeResponse({})
            code, result = self.run_cli(*self.flags, *self.start)
        self.assertEqual(0, code, result)
        self.assertTrue(result["applied"])
        self.assertIn("--resource-type", az.call_args.args[0])
        self.assertTrue(self.send.call_args.kwargs["headers"]["Authorization"].endswith(".new"))

    def test_lost_write_reply_records_uncertain_result(self):
        self.save()
        self.send.side_effect = RuntimeError("lost write reply")
        code, result = self.run_cli(*self.flags, *self.start)
        self.assertEqual(1, code)
        self.assertIsNone(result["applied"])
        self.assertEqual("outcome_unknown", json.loads(self.receipt.read_text())["verification_status"])
        self.send.assert_called_once()
