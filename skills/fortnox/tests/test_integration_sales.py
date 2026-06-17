from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any
from unittest.mock import patch

from fortnox_api_tool.cli import main


def _api_response(*, status: int, path: str, body: Any) -> dict[str, Any]:
    return {
        "status": status,
        "url": f"https://api.fortnox.se{path}",
        "token_source": "env",
        "token_expired": None,
        "body": body,
    }


class TestIntegrationSales(unittest.TestCase):
    def _run(self, *, env_path: Path, args: list[str]) -> tuple[int, dict[str, Any]]:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["--output", "json", "--env-file", str(env_path), *args])
        text = buf.getvalue().strip()
        self.assertTrue(text, "Command did not emit JSON output")
        return rc, json.loads(text)

    def _write_env(self, td: str) -> Path:
        env_path = Path(td) / ".env"
        env_path.write_text(
            "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
            encoding="utf-8",
        )
        return env_path

    def test_get_by_app_id_calls_expected_path(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            with patch("fortnox_api_tool.commands.integration_sales.request_json") as request_json:
                request_json.return_value = _api_response(
                    status=200,
                    path="/api/integration-partner/apps/sales-v1/app-42",
                    body={"appId": "app-42", "activeUsers": 9},
                )
                rc, payload = self._run(
                    env_path=env_path,
                    args=["integration-sales", "get-by-app-id", "--app-id", "app-42"],
                )

            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["path"], "/api/integration-partner/apps/sales-v1/app-42")
            self.assertEqual(request_json.call_args.kwargs["method"], "GET")
            self.assertEqual(request_json.call_args.kwargs["path"], "/api/integration-partner/apps/sales-v1/app-42")

    def test_get_by_app_id_and_tenant_calls_expected_path(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            with patch("fortnox_api_tool.commands.integration_sales.request_json") as request_json:
                request_json.return_value = _api_response(
                    status=200,
                    path="/api/integration-partner/apps/sales-v1/app-42/tenant-7",
                    body={"appId": "app-42", "tenantId": "tenant-7", "activeUsers": 1},
                )
                rc, payload = self._run(
                    env_path=env_path,
                    args=[
                        "integration-sales",
                        "get-by-app-id-and-tenant",
                        "--app-id",
                        "app-42",
                        "--tenant-id",
                        "tenant-7",
                    ],
                )

            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["path"], "/api/integration-partner/apps/sales-v1/app-42/tenant-7")
            self.assertEqual(request_json.call_args.kwargs["path"], "/api/integration-partner/apps/sales-v1/app-42/tenant-7")

    def test_resolves_sales_information_of_an_integration_calls_expected_path(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            with patch("fortnox_api_tool.commands.integration_sales.request_json") as request_json:
                request_json.return_value = _api_response(
                    status=200,
                    path="/api/integration-developer/sales-v1/int-11",
                    body={"integrationId": "int-11", "sales": 1200},
                )
                rc, payload = self._run(
                    env_path=env_path,
                    args=[
                        "integration-sales",
                        "resolves-sales-information-of-an-integration",
                        "--integration-id",
                        "int-11",
                    ],
                )

            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["path"], "/api/integration-developer/sales-v1/int-11")
            self.assertEqual(request_json.call_args.kwargs["path"], "/api/integration-developer/sales-v1/int-11")
