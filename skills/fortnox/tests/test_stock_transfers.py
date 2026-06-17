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


def _api_response(*, status: int, path: str, body: Any) -> dict[str, Any]:
    return {
        "status": status,
        "url": f"https://api.fortnox.se{path}",
        "token_source": "env",
        "token_expired": None,
        "body": body,
    }


class TestStockTransfers(unittest.TestCase):
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
        self.assertIsInstance(plan_out, str)
        return json.loads(Path(plan_out).read_text(encoding="utf-8"))

    def _write_env(self, td: str) -> Path:
        env_path = Path(td) / ".env"
        env_path.write_text(
            "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
            encoding="utf-8",
        )
        return env_path

    def _write_json(self, path: Path, payload: dict[str, Any]) -> None:
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def test_stock_transfers_get_is_wired(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            with patch("fortnox_api_tool.commands.stock_transfers.request_data") as request_data:
                request_data.return_value = _api_response(
                    status=200,
                    path="/api/warehouse/stocktransfer-v1/7",
                    body={"id": 7, "released": False},
                )
                rc, payload = self._run(env_path=env_path, args=["stock-transfers", "get", "--id", "7"])

        self.assertEqual(rc, 0)
        self.assertEqual(payload["path"], "/api/warehouse/stocktransfer-v1/7")
        self.assertEqual(payload["data"]["id"], 7)
        self.assertEqual(request_data.call_args.kwargs["path"], "/api/warehouse/stocktransfer-v1/7")

    def test_stock_transfers_create_dry_run_emits_plan(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            payload_path = Path(td) / "stock_transfer.json"
            self._write_json(payload_path, {"deliveryNoteId": "DN-1", "fromStockPointId": "sp-1", "toStockPointId": "sp-2"})
            expected_hash = _sha256(payload_path)

            with patch("fortnox_api_tool.commands.stock_transfers.request_data") as request_data:
                rc, payload = self._run(
                    env_path=env_path,
                    args=["stock-transfers", "create", "--json-file", str(payload_path)],
                )

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["baseline"]["payload_sha256"], expected_hash)
        self.assertEqual(request_data.call_count, 0)

    def test_stock_transfers_create_rejects_stale_wrapper(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            payload_path = Path(td) / "stock_transfer_wrapped.json"
            self._write_json(payload_path, {"StockTransfer": {"deliveryNoteId": "DN-1"}})

            rc, payload = self._run(
                env_path=env_path,
                args=["stock-transfers", "create", "--json-file", str(payload_path)],
            )

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("raw top-level object", payload["error"])

    def test_stock_transfers_create_apply_uses_response_id_for_verification(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            payload_path = Path(td) / "stock_transfer.json"
            self._write_json(payload_path, {"deliveryNoteId": "DN-1", "fromStockPointId": "sp-1", "toStockPointId": "sp-2"})

            with patch("fortnox_api_tool.commands.stock_transfers.request_data") as request_data:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["stock-transfers", "create", "--json-file", str(payload_path)],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_data.side_effect = [
                    _api_response(status=201, path="/api/warehouse/stocktransfer-v1", body={"id": 7001}),
                    _api_response(status=200, path="/api/warehouse/stocktransfer-v1/7001", body={"id": 7001}),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "stock-transfers",
                        "create",
                        "--json-file",
                        str(payload_path),
                        "--apply",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply["ok"])
        self.assertEqual(request_data.call_args_list[0].kwargs["path"], "/api/warehouse/stocktransfer-v1")
        self.assertEqual(request_data.call_args_list[1].kwargs["path"], "/api/warehouse/stocktransfer-v1/7001")
        self.assertEqual(payload_apply["receipt"]["target_id"], "7001")

    def test_stock_transfers_update_rejects_selector_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            payload_path = Path(td) / "stock_transfer_update.json"
            self._write_json(payload_path, {"id": 8, "deliveryNoteId": "DN-1"})

            rc, payload = self._run(
                env_path=env_path,
                args=["stock-transfers", "update", "--id", "7", "--json-file", str(payload_path)],
            )

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("must match --id", payload["error"])

    def test_stock_transfers_update_apply_performs_put_and_get_verify(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            payload_path = Path(td) / "stock_transfer_update.json"
            self._write_json(payload_path, {"id": 7, "deliveryNoteId": "DN-1", "rows": []})

            with patch("fortnox_api_tool.commands.stock_transfers.request_data") as request_data:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["stock-transfers", "update", "--id", "7", "--json-file", str(payload_path)],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_data.side_effect = [
                    _api_response(status=200, path="/api/warehouse/stocktransfer-v1/7", body={"id": 7}),
                    _api_response(status=200, path="/api/warehouse/stocktransfer-v1/7", body={"id": 7, "rows": []}),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "stock-transfers",
                        "update",
                        "--id",
                        "7",
                        "--json-file",
                        str(payload_path),
                        "--apply",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply["ok"])
        self.assertEqual(request_data.call_args_list[0].kwargs["method"], "PUT")
        self.assertEqual(request_data.call_args_list[0].kwargs["path"], "/api/warehouse/stocktransfer-v1/7")
        self.assertEqual(request_data.call_args_list[1].kwargs["path"], "/api/warehouse/stocktransfer-v1/7")

    def test_stock_transfers_release_refuses_without_yes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            rc, plan_payload = self._run(env_path=env_path, args=["stock-transfers", "release", "--id", "7"])
            self.assertEqual(rc, 0)
            plan = self._plan_from_output(plan_payload)
            plan_path = Path(td) / "plan.json"
            plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

            rc_apply, payload_apply = self._run(
                env_path=env_path,
                args=[
                    "stock-transfers",
                    "release",
                    "--id",
                    "7",
                    "--apply",
                    "--plan-in",
                    str(plan_path),
                ],
            )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply["refused"])
        self.assertIn("--apply --yes", " ".join(payload_apply["reasons"]))

    def test_stock_transfers_release_apply_performs_put_and_get_verify(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            rc, plan_payload = self._run(env_path=env_path, args=["stock-transfers", "release", "--id", "7"])
            self.assertEqual(rc, 0)
            plan = self._plan_from_output(plan_payload)
            plan_path = Path(td) / "plan.json"
            plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

            with patch("fortnox_api_tool.commands.stock_transfers.request_data") as request_data:
                request_data.side_effect = [
                    _api_response(status=204, path="/api/warehouse/stocktransfer-v1/7/release", body=None),
                    _api_response(status=200, path="/api/warehouse/stocktransfer-v1/7", body={"id": 7, "released": True}),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "stock-transfers",
                        "release",
                        "--id",
                        "7",
                        "--apply",
                        "--yes",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply["ok"])
        self.assertEqual(request_data.call_args_list[0].kwargs["path"], "/api/warehouse/stocktransfer-v1/7/release")
        self.assertEqual(request_data.call_args_list[1].kwargs["path"], "/api/warehouse/stocktransfer-v1/7")

    def test_stock_transfers_void_refuses_without_ack(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            rc, plan_payload = self._run(env_path=env_path, args=["stock-transfers", "void", "--id", "7"])
            self.assertEqual(rc, 0)
            plan = self._plan_from_output(plan_payload)
            plan_path = Path(td) / "plan.json"
            plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

            rc_apply, payload_apply = self._run(
                env_path=env_path,
                args=[
                    "stock-transfers",
                    "void",
                    "--id",
                    "7",
                    "--apply",
                    "--yes",
                    "--plan-in",
                    str(plan_path),
                ],
            )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply["refused"])
        self.assertIn("ack-irreversible", " ".join(payload_apply["reasons"]).lower())

    def test_stock_transfers_void_apply_performs_put_and_get_verify(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            rc, plan_payload = self._run(env_path=env_path, args=["stock-transfers", "void", "--id", "7"])
            self.assertEqual(rc, 0)
            plan = self._plan_from_output(plan_payload)
            plan_path = Path(td) / "plan.json"
            plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

            with patch("fortnox_api_tool.commands.stock_transfers.request_data") as request_data:
                request_data.side_effect = [
                    _api_response(status=204, path="/api/warehouse/stocktransfer-v1/7/void", body=None),
                    _api_response(status=200, path="/api/warehouse/stocktransfer-v1/7", body={"id": 7, "voided": True}),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "stock-transfers",
                        "void",
                        "--id",
                        "7",
                        "--apply",
                        "--yes",
                        "--ack-irreversible",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply["ok"])
        self.assertEqual(request_data.call_args_list[0].kwargs["path"], "/api/warehouse/stocktransfer-v1/7/void")
        self.assertEqual(request_data.call_args_list[1].kwargs["path"], "/api/warehouse/stocktransfer-v1/7")


if __name__ == "__main__":
    unittest.main()
