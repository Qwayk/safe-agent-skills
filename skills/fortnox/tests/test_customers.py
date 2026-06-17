from __future__ import annotations

import hashlib
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any
from unittest.mock import patch

from fortnox_api_tool.cli import main


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _api_response(*, status: int, path: str, body: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": status,
        "url": f"https://api.fortnox.se/3{path}",
        "token_source": "env",
        "token_expired": None,
        "body": body,
    }


class TestCustomers(unittest.TestCase):
    def _run(self, *, env_path: Path, args: list[str]) -> tuple[int, dict[str, Any]]:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["--output", "json", "--env-file", str(env_path), *args])
        text = buf.getvalue().strip()
        self.assertTrue(text, "Command did not emit JSON output")
        return rc, json.loads(text)

    def _plan_from_output(self, payload: dict[str, Any]) -> dict[str, Any]:
        plan = payload.get("plan")
        if isinstance(plan, dict):
            return plan
        plan_out = payload.get("plan_out") or payload.get("plan_path")
        self.assertTrue(plan_out)
        self.assertIsInstance(plan_out, str)
        return json.loads(Path(plan_out).read_text(encoding="utf-8"))

    def _make_payload_file(self, path: Path, *, customer_number: str = "CUST-1000") -> None:
        payload = {
            "Customer": {
                "CustomerNumber": customer_number,
                "Name": "Sample customer",
            }
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def test_customers_create_dry_run_emits_plan(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "create.json"
            self._make_payload_file(payload_path, customer_number="CUST-1000")

            with patch("fortnox_api_tool.commands.customers.request_json") as request_json:
                rc, payload = self._run(
                    env_path=env_path,
                    args=[
                        "customers",
                        "create",
                        "--json-file",
                        str(payload_path),
                    ],
                )

            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["plan"].get("baseline", {}).get("payload_sha256"), _sha256(payload_path))
            self.assertEqual(request_json.call_count, 0)

    def test_customers_create_apply_rechecks_json_payload_hash(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "create.json"
            self._make_payload_file(payload_path, customer_number="CUST-1000")

            with patch("fortnox_api_tool.commands.customers.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=[
                        "customers",
                        "create",
                        "--json-file",
                        str(payload_path),
                    ],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                self.assertEqual(request_json.call_count, 0)

                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                payload_path.write_text(
                    json.dumps(
                        {
                            "Customer": {
                                "CustomerNumber": "CUST-1000",
                                "Name": "Updated sample customer",
                            }
                        },
                        indent=2,
                    ),
                    encoding="utf-8",
                )

                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "customers",
                        "create",
                        "--json-file",
                        str(payload_path),
                        "--apply",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply.get("refused", False))
        self.assertIn("hash", " ".join(payload_apply["reasons"]).lower())
        self.assertEqual(request_json.call_count, 0)

    def test_customers_create_apply_performs_post_get_verify(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "create.json"
            self._make_payload_file(payload_path, customer_number="CUST-1000")

            with patch("fortnox_api_tool.commands.customers.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=[
                        "customers",
                        "create",
                        "--json-file",
                        str(payload_path),
                    ],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_json.side_effect = [
                    _api_response(
                        status=201,
                        path="/customers",
                        body={"Customer": {"CustomerNumber": "CUST-1000"}},
                    ),
                    _api_response(
                        status=200,
                        path="/customers/CUST-1000",
                        body={"Customer": {"CustomerNumber": "CUST-1000"}},
                    ),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "customers",
                        "create",
                        "--json-file",
                        str(payload_path),
                        "--apply",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply.get("ok", False))
        self.assertEqual(request_json.call_args_list[0].kwargs["method"], "POST")
        self.assertEqual(request_json.call_args_list[0].kwargs["path"], "/customers")
        self.assertEqual(request_json.call_args_list[1].kwargs["method"], "GET")
        self.assertEqual(request_json.call_args_list[1].kwargs["path"], "/customers/CUST-1000")

    def test_customers_create_apply_uses_response_number_for_verification(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "create.json"
            payload = {
                "Customer": {
                    "Name": "Sample customer",
                }
            }
            payload_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

            with patch("fortnox_api_tool.commands.customers.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=[
                        "customers",
                        "create",
                        "--json-file",
                        str(payload_path),
                    ],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_json.side_effect = [
                    _api_response(
                        status=201,
                        path="/customers",
                        body={"Customer": {"CustomerNumber": "CUST-2000"}},
                    ),
                    _api_response(
                        status=200,
                        path="/customers/CUST-2000",
                        body={"Customer": {"CustomerNumber": "CUST-2000"}},
                    ),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "customers",
                        "create",
                        "--json-file",
                        str(payload_path),
                        "--apply",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply.get("ok", False))
        self.assertEqual(request_json.call_args_list[1].kwargs["path"], "/customers/CUST-2000")

    def test_customers_create_apply_fails_without_number_on_verification(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "create.json"
            payload = {
                "Customer": {
                    "Name": "No number in payload",
                }
            }
            payload_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

            with patch("fortnox_api_tool.commands.customers.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=[
                        "customers",
                        "create",
                        "--json-file",
                        str(payload_path),
                    ],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_json.side_effect = [
                    _api_response(
                        status=201,
                        path="/customers",
                        body={},
                    ),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "customers",
                        "create",
                        "--json-file",
                        str(payload_path),
                        "--apply",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

        self.assertEqual(rc_apply, 1)
        self.assertFalse(payload_apply.get("ok", True))
        self.assertEqual(payload_apply.get("error_type"), "ValidationError")
        self.assertIn("Could not determine CustomerNumber", payload_apply.get("error", ""))

    def test_customers_update_dry_run_emits_plan(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "update.json"
            self._make_payload_file(payload_path, customer_number="CUST-1000")

            with patch("fortnox_api_tool.commands.customers.request_json") as request_json:
                rc, payload = self._run(
                    env_path=env_path,
                    args=[
                        "customers",
                        "update",
                        "--customer-number",
                        "CUST-1000",
                        "--json-file",
                        str(payload_path),
                    ],
                )

            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["plan"].get("selector", {}).get("customer_number"), "CUST-1000")
            self.assertEqual(request_json.call_count, 0)

    def test_customers_update_apply_rechecks_json_payload_hash(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "update.json"
            self._make_payload_file(payload_path, customer_number="CUST-1000")

            with patch("fortnox_api_tool.commands.customers.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=[
                        "customers",
                        "update",
                        "--customer-number",
                        "CUST-1000",
                        "--json-file",
                        str(payload_path),
                    ],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)

                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                payload_path.write_text(
                    json.dumps(
                        {
                            "Customer": {
                                "CustomerNumber": "CUST-1000",
                                "Name": "Updated sample customer",
                            }
                        },
                        indent=2,
                    ),
                    encoding="utf-8",
                )

                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "customers",
                        "update",
                        "--customer-number",
                        "CUST-1000",
                        "--json-file",
                        str(payload_path),
                        "--apply",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply.get("refused", False))
        self.assertIn("hash", " ".join(payload_apply["reasons"]).lower())
        self.assertEqual(request_json.call_count, 0)

    def test_customers_update_apply_performs_put_get_verify(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "update.json"
            self._make_payload_file(payload_path, customer_number="CUST-1000")

            with patch("fortnox_api_tool.commands.customers.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=[
                        "customers",
                        "update",
                        "--customer-number",
                        "CUST-1000",
                        "--json-file",
                        str(payload_path),
                    ],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_json.side_effect = [
                    _api_response(
                        status=200,
                        path="/customers/CUST-1000",
                        body={"Customer": {"CustomerNumber": "CUST-1000"}},
                    ),
                    _api_response(
                        status=200,
                        path="/customers/CUST-1000",
                        body={"Customer": {"CustomerNumber": "CUST-1000"}},
                    ),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "customers",
                        "update",
                        "--customer-number",
                        "CUST-1000",
                        "--json-file",
                        str(payload_path),
                        "--apply",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply.get("ok", False))
        self.assertEqual(request_json.call_args_list[0].kwargs["method"], "PUT")
        self.assertEqual(request_json.call_args_list[0].kwargs["path"], "/customers/CUST-1000")
        self.assertEqual(request_json.call_args_list[1].kwargs["method"], "GET")
        self.assertEqual(request_json.call_args_list[1].kwargs["path"], "/customers/CUST-1000")

    def test_customers_update_rejects_number_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "update.json"
            self._make_payload_file(payload_path, customer_number="CUST-2002")

            rc, payload = self._run(
                env_path=env_path,
                args=[
                    "customers",
                    "update",
                    "--customer-number",
                    "CUST-1000",
                    "--json-file",
                    str(payload_path),
                ],
            )

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("must match --customer-number", payload["error"])

    def test_customers_delete_dry_run_emits_plan(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )

            with patch("fortnox_api_tool.commands.customers.request_json") as request_json:
                rc, payload = self._run(env_path=env_path, args=["customers", "delete", "--customer-number", "CUST-1000"])

            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["plan"].get("selector", {}).get("customer_number"), "CUST-1000")
            self.assertEqual(request_json.call_count, 0)

    def test_customers_delete_apply_refuses_without_ack(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )

            with patch("fortnox_api_tool.commands.customers.request_json") as request_json:
                rc, plan_payload = self._run(env_path=env_path, args=["customers", "delete", "--customer-number", "CUST-1000"])
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                rc_refused, payload_refused = self._run(
                    env_path=env_path,
                    args=[
                        "customers",
                        "delete",
                        "--customer-number",
                        "CUST-1000",
                        "--apply",
                        "--yes",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

        self.assertEqual(rc_refused, 0)
        self.assertTrue(payload_refused.get("refused", False))
        self.assertIn("ack-irreversible", " ".join(payload_refused["reasons"]).lower())
        self.assertEqual(request_json.call_count, 0)

    def test_customers_delete_apply_refuses_without_yes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )

            with patch("fortnox_api_tool.commands.customers.request_json") as request_json:
                rc, plan_payload = self._run(env_path=env_path, args=["customers", "delete", "--customer-number", "CUST-1000"])
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                rc_refused, payload_refused = self._run(
                    env_path=env_path,
                    args=[
                        "customers",
                        "delete",
                        "--customer-number",
                        "CUST-1000",
                        "--apply",
                        "--ack-irreversible",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

        self.assertEqual(rc_refused, 0)
        self.assertTrue(payload_refused.get("refused", False))
        self.assertIn("--apply --yes", " ".join(payload_refused["reasons"]))
        self.assertEqual(request_json.call_count, 0)

    def test_customers_delete_apply_performs_delete_and_404_verify(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )

            with patch("fortnox_api_tool.commands.customers.request_json") as request_json:
                rc, plan_payload = self._run(env_path=env_path, args=["customers", "delete", "--customer-number", "CUST-1000"])
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_json.side_effect = [
                    _api_response(status=204, path="/customers/CUST-1000", body={}),
                    RuntimeError("HTTP 404 for GET https://api.fortnox.se/3/customers/CUST-1000"),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "customers",
                        "delete",
                        "--customer-number",
                        "CUST-1000",
                        "--apply",
                        "--yes",
                        "--ack-irreversible",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply.get("ok", False))
        self.assertEqual(request_json.call_args_list[0].kwargs["method"], "DELETE")
        self.assertEqual(request_json.call_args_list[0].kwargs["path"], "/customers/CUST-1000")
        self.assertEqual(request_json.call_args_list[1].kwargs["method"], "GET")
        self.assertEqual(request_json.call_args_list[1].kwargs["path"], "/customers/CUST-1000")
