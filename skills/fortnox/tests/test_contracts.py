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


def _api_response(*, status: int, path: str, body: dict[str, Any] | None) -> dict[str, Any]:
    return {
        "status": status,
        "url": f"https://api.fortnox.se/3{path}",
        "token_source": "env",
        "token_expired": None,
        "body": body,
    }


class TestContracts(unittest.TestCase):
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

    def _make_payload_file(self, path: Path, *, document_number: str = "1001") -> None:
        payload = {
            "Contract": {
                "DocumentNumber": document_number,
                "CustomerNumber": "C-1",
                "InvoiceRows": [{"ArticleNumber": "A-1", "DeliveredQuantity": "1"}],
                "PeriodEnd": "2026-06-30",
            }
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _make_optional_action_payload_file(self, path: Path, *, document_number: str = "1001") -> None:
        payload = {"Contract": {"DocumentNumber": document_number}}
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def test_contracts_list_wires_documented_query_params(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            with patch("fortnox_api_tool.commands.contracts.request_json") as request_json:
                request_json.return_value = _api_response(status=200, path="/contracts", body={"Contracts": []})
                rc, payload = self._run(
                    env_path=env_path,
                    args=[
                        "contracts",
                        "list",
                        "--period-start",
                        "2026-06-01",
                        "--period-end",
                        "2026-06-30",
                        "--filter",
                        "active",
                        "--document-number",
                        "1001",
                        "--customer-number",
                        "C-1",
                        "--template-number",
                        "2001",
                        "--invoices-remaining",
                        "3",
                        "--last-modified",
                        "2026-06-15",
                    ],
                )

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(request_json.call_args.kwargs["method"], "GET")
        self.assertEqual(request_json.call_args.kwargs["path"], "/contracts")
        self.assertEqual(
            request_json.call_args.kwargs["query_params"],
            {
                "periodstart": "2026-06-01",
                "periodend": "2026-06-30",
                "filter": "active",
                "documentnumber": "1001",
                "customernumber": "C-1",
                "templatenumber": "2001",
                "invoicesremaining": "3",
                "lastmodified": "2026-06-15",
            },
        )

    def test_contracts_get(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            with patch(
                "fortnox_api_tool.commands.contracts.request_json",
                return_value=_api_response(
                    status=200,
                    path="/contracts/1001",
                    body={"Contract": {"DocumentNumber": 1001}},
                ),
            ):
                rc, payload = self._run(
                    env_path=env_path,
                    args=["contracts", "get", "--document-number", "1001"],
                )

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["path"], "/contracts/1001")

    def test_contracts_create_dry_run_emits_plan(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "create.json"
            self._make_payload_file(payload_path)
            expected_hash = _sha256(payload_path)

            with patch("fortnox_api_tool.commands.contracts.request_json") as request_json:
                rc, payload = self._run(env_path=env_path, args=["contracts", "create", "--json-file", str(payload_path)])

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"].get("baseline", {}).get("payload_sha256"), expected_hash)
        self.assertEqual(request_json.call_count, 0)

    def test_contracts_create_apply_rechecks_json_payload_hash(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "create.json"
            self._make_payload_file(payload_path)

            with patch("fortnox_api_tool.commands.contracts.request_json") as request_json:
                rc, plan_payload = self._run(env_path=env_path, args=["contracts", "create", "--json-file", str(payload_path)])
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                changed = json.loads(payload_path.read_text(encoding="utf-8"))
                changed["Contract"]["PeriodEnd"] = "2026-07-31"
                payload_path.write_text(json.dumps(changed, indent=2), encoding="utf-8")

                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "contracts",
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

    def test_contracts_create_apply_performs_post_and_get_verify(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "create.json"
            self._make_payload_file(payload_path)

            with patch("fortnox_api_tool.commands.contracts.request_json") as request_json:
                rc, plan_payload = self._run(env_path=env_path, args=["contracts", "create", "--json-file", str(payload_path)])
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_json.side_effect = [
                    _api_response(status=201, path="/contracts", body={"Contract": {"DocumentNumber": 1001}}),
                    _api_response(status=200, path="/contracts/1001", body={"Contract": {"DocumentNumber": 1001}}),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "contracts",
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
        self.assertEqual(request_json.call_args_list[0].kwargs["path"], "/contracts")
        self.assertEqual(request_json.call_args_list[1].kwargs["method"], "GET")
        self.assertEqual(request_json.call_args_list[1].kwargs["path"], "/contracts/1001")

    def test_contracts_update_selector_mismatch_validation(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "update.json"
            self._make_payload_file(payload_path, document_number="1002")

            with patch("fortnox_api_tool.commands.contracts.request_json") as request_json:
                rc, payload = self._run(
                    env_path=env_path,
                    args=["contracts", "update", "--document-number", "1001", "--json-file", str(payload_path)],
                )

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertIn("must match", payload["error"])
        self.assertEqual(request_json.call_count, 0)

    def test_contracts_create_invoice_apply_wires_invoice_date_and_verifies_state(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "action.json"
            self._make_optional_action_payload_file(payload_path)

            with patch("fortnox_api_tool.commands.contracts.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=[
                        "contracts",
                        "create-invoice",
                        "--document-number",
                        "1001",
                        "--json-file",
                        str(payload_path),
                        "--invoice-date",
                        "2026-06-20",
                    ],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_json.side_effect = [
                    _api_response(
                        status=200,
                        path="/contracts/1001",
                        body={"Contract": {"DocumentNumber": 1001, "InvoicesRemaining": "2", "LastInvoiceDate": "2026-06-01"}},
                    ),
                    _api_response(
                        status=200,
                        path="/contracts/1001/createinvoice",
                        body={"Contract": {"DocumentNumber": 1001}},
                    ),
                    _api_response(
                        status=200,
                        path="/contracts/1001",
                        body={"Contract": {"DocumentNumber": 1001, "InvoicesRemaining": "1", "LastInvoiceDate": "2026-06-20"}},
                    ),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "contracts",
                        "create-invoice",
                        "--document-number",
                        "1001",
                        "--json-file",
                        str(payload_path),
                        "--invoice-date",
                        "2026-06-20",
                        "--apply",
                        "--yes",
                        "--ack-no-snapshot",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply.get("ok", False))
        self.assertEqual(request_json.call_args_list[1].kwargs["method"], "PUT")
        self.assertEqual(request_json.call_args_list[1].kwargs["path"], "/contracts/1001/createinvoice")
        self.assertEqual(request_json.call_args_list[1].kwargs["query_params"], {"invoicedate": "2026-06-20"})
        self.assertTrue(payload_apply["receipt"].get("verification_last_invoice_date_matches"))

    def test_contracts_create_invoice_without_ack_no_snapshot_refuses_before_any_http(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "action.json"
            self._make_optional_action_payload_file(payload_path)

            with patch("fortnox_api_tool.commands.contracts.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=[
                        "contracts",
                        "create-invoice",
                        "--document-number",
                        "1001",
                        "--json-file",
                        str(payload_path),
                        "--invoice-date",
                        "2026-06-20",
                    ],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "contracts",
                        "create-invoice",
                        "--document-number",
                        "1001",
                        "--json-file",
                        str(payload_path),
                        "--invoice-date",
                        "2026-06-20",
                        "--apply",
                        "--yes",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply.get("refused", False))
        self.assertIn("--ack-no-snapshot", " ".join(payload_apply["reasons"]))
        self.assertEqual(request_json.call_count, 0)

    def test_contracts_increase_invoice_count_apply_verifies_increase(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            with patch("fortnox_api_tool.commands.contracts.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["contracts", "increase-invoice-count", "--document-number", "1001"],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_json.side_effect = [
                    _api_response(status=200, path="/contracts/1001", body={"Contract": {"DocumentNumber": 1001, "InvoicesRemaining": "2"}}),
                    _api_response(status=200, path="/contracts/1001/increaseinvoicecount", body={"Contract": {"DocumentNumber": 1001}}),
                    _api_response(status=200, path="/contracts/1001", body={"Contract": {"DocumentNumber": 1001, "InvoicesRemaining": "3"}}),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "contracts",
                        "increase-invoice-count",
                        "--document-number",
                        "1001",
                        "--apply",
                        "--yes",
                        "--ack-no-snapshot",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply.get("ok", False))
        self.assertTrue(payload_apply["receipt"].get("verification_invoices_remaining_increased"))

    def test_contracts_finish_apply_fails_when_active_stays_true(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            with patch("fortnox_api_tool.commands.contracts.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["contracts", "finish", "--document-number", "1001"],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_json.side_effect = [
                    _api_response(status=200, path="/contracts/1001", body={"Contract": {"DocumentNumber": 1001, "Active": True}}),
                    _api_response(status=200, path="/contracts/1001/finish", body={"Contract": {"DocumentNumber": 1001}}),
                    _api_response(status=200, path="/contracts/1001", body={"Contract": {"DocumentNumber": 1001, "Active": True}}),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "contracts",
                        "finish",
                        "--document-number",
                        "1001",
                        "--apply",
                        "--yes",
                        "--ack-no-snapshot",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

        self.assertEqual(rc_apply, 1)
        self.assertFalse(payload_apply.get("ok", True))
        self.assertFalse(payload_apply["receipt"].get("verification_active_false", True))
