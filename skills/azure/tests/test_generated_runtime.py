from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

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


if __name__ == "__main__":
    unittest.main()
