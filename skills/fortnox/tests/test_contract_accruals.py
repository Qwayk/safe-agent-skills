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


class TestContractAccruals(unittest.TestCase):
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
            "ContractAccrual": {
                "DocumentNumber": document_number,
                "AccrualAccount": 1570,
                "AccrualRows": [{"Amount": 100}, {"Amount": 100}],
                "CostAccount": 4010,
                "Description": "seed",
                "Total": 200,
            }
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def test_contract_accruals_list(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            with patch(
                "fortnox_api_tool.commands.contract_accruals.get_json",
                return_value=_api_response(
                    status=200,
                    path="/contractaccruals",
                    body={"ContractAccruals": []},
                ),
            ):
                rc, payload = self._run(env_path=env_path, args=["contract-accruals", "list"])

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["path"], "/contractaccruals")

    def test_contract_accruals_get(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            with patch(
                "fortnox_api_tool.commands.contract_accruals.get_json",
                return_value=_api_response(
                    status=200,
                    path="/contractaccruals/1001",
                    body={"ContractAccrual": {"DocumentNumber": 1001}},
                ),
            ):
                rc, payload = self._run(
                    env_path=env_path,
                    args=["contract-accruals", "get", "--document-number", "1001"],
                )

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["path"], "/contractaccruals/1001")

    def test_contract_accruals_create_dry_run_emits_plan(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "create.json"
            self._make_payload_file(payload_path)
            expected_hash = _sha256(payload_path)

            with patch("fortnox_api_tool.commands.contract_accruals.request_json") as request_json:
                rc, payload = self._run(
                    env_path=env_path,
                    args=["contract-accruals", "create", "--json-file", str(payload_path)],
                )

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"].get("baseline", {}).get("payload_sha256"), expected_hash)
        self.assertEqual(request_json.call_count, 0)

    def test_contract_accruals_create_apply_rechecks_json_payload_hash(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "create.json"
            self._make_payload_file(payload_path)

            with patch("fortnox_api_tool.commands.contract_accruals.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["contract-accruals", "create", "--json-file", str(payload_path)],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                self._make_payload_file(payload_path, document_number="1001")
                changed = json.loads(payload_path.read_text(encoding="utf-8"))
                changed["ContractAccrual"]["Description"] = "changed"
                payload_path.write_text(json.dumps(changed, indent=2), encoding="utf-8")

                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "contract-accruals",
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

    def test_contract_accruals_create_apply_performs_post_and_get_verify(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "create.json"
            self._make_payload_file(payload_path)

            with patch("fortnox_api_tool.commands.contract_accruals.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["contract-accruals", "create", "--json-file", str(payload_path)],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_json.side_effect = [
                    _api_response(
                        status=201,
                        path="/contractaccruals",
                        body={"ContractAccrual": {"DocumentNumber": 1001}},
                    ),
                    _api_response(
                        status=200,
                        path="/contractaccruals/1001",
                        body={"ContractAccrual": {"DocumentNumber": 1001}},
                    ),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "contract-accruals",
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
        self.assertEqual(request_json.call_args_list[0].kwargs["path"], "/contractaccruals")
        self.assertEqual(request_json.call_args_list[1].kwargs["method"], "GET")
        self.assertEqual(request_json.call_args_list[1].kwargs["path"], "/contractaccruals/1001")

    def test_contract_accruals_update_selector_mismatch_validation(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "update.json"
            self._make_payload_file(payload_path, document_number="1002")

            with patch("fortnox_api_tool.commands.contract_accruals.request_json") as request_json:
                rc, payload = self._run(
                    env_path=env_path,
                    args=[
                        "contract-accruals",
                        "update",
                        "--document-number",
                        "1001",
                        "--json-file",
                        str(payload_path),
                    ],
                )

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertIn("must match", payload["error"])
        self.assertEqual(request_json.call_count, 0)

    def test_contract_accruals_update_apply_performs_put_and_get_verify(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "update.json"
            self._make_payload_file(payload_path)

            with patch("fortnox_api_tool.commands.contract_accruals.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=[
                        "contract-accruals",
                        "update",
                        "--document-number",
                        "1001",
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
                        path="/contractaccruals/1001",
                        body={"ContractAccrual": {"DocumentNumber": 1001}},
                    ),
                    _api_response(
                        status=200,
                        path="/contractaccruals/1001",
                        body={"ContractAccrual": {"DocumentNumber": 1001}},
                    ),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "contract-accruals",
                        "update",
                        "--document-number",
                        "1001",
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
        self.assertEqual(request_json.call_args_list[0].kwargs["path"], "/contractaccruals/1001")
        self.assertEqual(request_json.call_args_list[1].kwargs["method"], "GET")
        self.assertEqual(request_json.call_args_list[1].kwargs["path"], "/contractaccruals/1001")

    def test_contract_accruals_remove_refusal_and_success_path(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )

            with patch("fortnox_api_tool.commands.contract_accruals.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["contract-accruals", "remove", "--document-number", "1001"],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                rc_refused, payload_refused = self._run(
                    env_path=env_path,
                    args=[
                        "contract-accruals",
                        "remove",
                        "--document-number",
                        "1001",
                        "--apply",
                        "--plan-in",
                        str(plan_path),
                    ],
                )
                self.assertEqual(rc_refused, 0)
                self.assertTrue(payload_refused.get("refused", False))
                self.assertIn("yes", " ".join(payload_refused["reasons"]).lower())

                rc_refused_ack, payload_refused_ack = self._run(
                    env_path=env_path,
                    args=[
                        "contract-accruals",
                        "remove",
                        "--document-number",
                        "1001",
                        "--apply",
                        "--yes",
                        "--plan-in",
                        str(plan_path),
                    ],
                )
                self.assertEqual(rc_refused_ack, 0)
                self.assertTrue(payload_refused_ack.get("refused", False))
                self.assertIn("ack-irreversible", " ".join(payload_refused_ack["reasons"]).lower())

                request_json.side_effect = [
                    _api_response(status=204, path="/contractaccruals/1001", body=None),
                    RuntimeError("HTTP 404 for GET https://api.fortnox.se/3/contractaccruals/1001"),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "contract-accruals",
                        "remove",
                        "--document-number",
                        "1001",
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
        self.assertEqual(request_json.call_args_list[0].kwargs["path"], "/contractaccruals/1001")
        self.assertEqual(request_json.call_args_list[1].kwargs["method"], "GET")
        self.assertEqual(request_json.call_args_list[1].kwargs["path"], "/contractaccruals/1001")
