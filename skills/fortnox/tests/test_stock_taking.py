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


class TestStockTaking(unittest.TestCase):
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

    def _write_json(self, path: Path, payload: Any) -> None:
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def test_stock_taking_list_is_wired(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            with patch("fortnox_api_tool.commands.stock_taking.request_data") as request_data:
                request_data.return_value = _api_response(
                    status=200,
                    path="/api/warehouse/stocktaking-v1",
                    body=[{"id": 7}],
                )
                rc, payload = self._run(env_path=env_path, args=["stock-taking", "list"])

        self.assertEqual(rc, 0)
        self.assertEqual(payload["path"], "/api/warehouse/stocktaking-v1")
        self.assertEqual(payload["data"], [{"id": 7}])
        self.assertEqual(request_data.call_args.kwargs["path"], "/api/warehouse/stocktaking-v1")

    def test_stock_taking_get_is_wired(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            with patch("fortnox_api_tool.commands.stock_taking.request_data") as request_data:
                request_data.return_value = _api_response(
                    status=200,
                    path="/api/warehouse/stocktaking-v1/7",
                    body={"id": 7, "state": "planning"},
                )
                rc, payload = self._run(env_path=env_path, args=["stock-taking", "get", "--id", "7"])

        self.assertEqual(rc, 0)
        self.assertEqual(payload["path"], "/api/warehouse/stocktaking-v1/7")
        self.assertEqual(payload["data"]["id"], 7)
        self.assertEqual(request_data.call_args.kwargs["path"], "/api/warehouse/stocktaking-v1/7")

    def test_stock_taking_get_candidate_rows_shapes_filters(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            with patch("fortnox_api_tool.commands.stock_taking.request_data") as request_data:
                request_data.return_value = _api_response(
                    status=200,
                    path="/api/warehouse/stocktaking-v1/7/candidates",
                    body=[{"stockTakingRowId": "row-1"}],
                )
                rc, payload = self._run(
                    env_path=env_path,
                    args=[
                        "stock-taking",
                        "get-candidate-rows",
                        "--id",
                        "7",
                        "--item-id",
                        "A-1",
                        "--item-id",
                        "A-2,A-3",
                        "--supplier-number",
                        "100",
                        "--stock-point-id",
                        "sp-1",
                        "--stock-location-id",
                        "sl-1",
                        "--transaction-date",
                        "2026-06-15",
                        "--item-id-search",
                        "A",
                        "--item-description-search",
                        "bolt",
                        "--exclude-zero-balance-items",
                        "--include-non-inbound-items",
                    ],
                )

        self.assertEqual(rc, 0)
        self.assertEqual(payload["path"], "/api/warehouse/stocktaking-v1/7/candidates")
        self.assertEqual(
            request_data.call_args.kwargs["query_params"],
            {
                "itemIds": ["A-1", "A-2", "A-3"],
                "supplierNumbers": ["100"],
                "stockPointIds": ["sp-1"],
                "stockLocationIds": ["sl-1"],
                "transactionDate": "2026-06-15",
                "itemIdSearch": "A",
                "itemDescriptionSearch": "bolt",
                "excludeZeroBalanceItems": True,
                "includeNonInboundItems": True,
            },
        )

    def test_stock_taking_get_rows_shapes_filters(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            with patch("fortnox_api_tool.commands.stock_taking.request_data") as request_data:
                request_data.return_value = _api_response(
                    status=200,
                    path="/api/warehouse/stocktaking-v1/7/rows",
                    body={"rows": [{"stockTakingRowId": "row-1"}]},
                )
                rc, payload = self._run(
                    env_path=env_path,
                    args=[
                        "stock-taking",
                        "get-rows",
                        "--id",
                        "7",
                        "--item-id",
                        "A-1",
                        "--supplier-number",
                        "100",
                        "--stock-point-id",
                        "sp-1",
                        "--stock-location-id",
                        "sl-1",
                        "--transaction-date",
                        "2026-06-15",
                        "--item-id-search",
                        "A",
                        "--item-description-search",
                        "bolt",
                        "--exclude-zero-balance-items",
                        "--secondary-sort-by",
                        "itemId",
                        "--secondary-order",
                        "ascending",
                        "--state-filter",
                        "stockTakenWithDeviation",
                        "--starting-row-no",
                        "12",
                        "--starting-item-id",
                        "A-2",
                    ],
                )

        self.assertEqual(rc, 0)
        self.assertEqual(payload["path"], "/api/warehouse/stocktaking-v1/7/rows")
        self.assertEqual(
            request_data.call_args.kwargs["query_params"],
            {
                "itemIds": ["A-1"],
                "supplierNumbers": ["100"],
                "stockPointIds": ["sp-1"],
                "stockLocationIds": ["sl-1"],
                "transactionDate": "2026-06-15",
                "itemIdSearch": "A",
                "itemDescriptionSearch": "bolt",
                "excludeZeroBalanceItems": True,
                "secondarysortby": "itemId",
                "secondaryorder": "ascending",
                "stateFilter": "stockTakenWithDeviation",
                "startingRowNo": 12,
                "startingItemId": "A-2",
            },
        )

    def test_stock_taking_create_dry_run_emits_plan(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            payload_path = Path(td) / "stock_taking.json"
            self._write_json(payload_path, {"name": "Quarter count", "responsible": "EMP-1", "state": "planning"})
            expected_hash = _sha256(payload_path)

            with patch("fortnox_api_tool.commands.stock_taking.request_data") as request_data:
                rc, payload = self._run(
                    env_path=env_path,
                    args=["stock-taking", "create", "--json-file", str(payload_path)],
                )

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["baseline"]["payload_sha256"], expected_hash)
        self.assertEqual(request_data.call_count, 0)

    def test_stock_taking_create_apply_uses_response_id_for_verification(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            payload_path = Path(td) / "stock_taking.json"
            self._write_json(payload_path, {"name": "Quarter count", "responsible": "EMP-1", "state": "planning"})

            with patch("fortnox_api_tool.commands.stock_taking.request_data") as request_data:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["stock-taking", "create", "--json-file", str(payload_path)],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_data.side_effect = [
                    _api_response(status=201, path="/api/warehouse/stocktaking-v1", body={"id": 7001}),
                    _api_response(status=200, path="/api/warehouse/stocktaking-v1/7001", body={"id": 7001}),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "stock-taking",
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
        self.assertEqual(request_data.call_args_list[0].kwargs["path"], "/api/warehouse/stocktaking-v1")
        self.assertEqual(request_data.call_args_list[1].kwargs["path"], "/api/warehouse/stocktaking-v1/7001")
        self.assertEqual(payload_apply["receipt"]["target_id"], "7001")

    def test_stock_taking_update_rejects_payload_id_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            payload_path = Path(td) / "stock_taking_update.json"
            self._write_json(payload_path, {"id": 8, "name": "Quarter count", "responsible": "EMP-1"})

            rc, payload = self._run(
                env_path=env_path,
                args=["stock-taking", "update", "--id", "7", "--json-file", str(payload_path)],
            )

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("must match --id", payload["error"])

    def test_stock_taking_update_apply_verifies_expected_state(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            payload_path = Path(td) / "stock_taking_update.json"
            self._write_json(payload_path, {"id": 7, "name": "Quarter count", "responsible": "EMP-1", "state": "started"})

            with patch("fortnox_api_tool.commands.stock_taking.request_data") as request_data:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["stock-taking", "update", "--id", "7", "--json-file", str(payload_path)],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_data.side_effect = [
                    _api_response(status=200, path="/api/warehouse/stocktaking-v1/7", body={"id": 7}),
                    _api_response(status=200, path="/api/warehouse/stocktaking-v1/7", body={"id": 7, "state": "started"}),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "stock-taking",
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
        self.assertTrue(payload_apply["receipt"]["verification"]["verification_state_matches"])

    def test_stock_taking_add_rows_rejects_wrapped_payload(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            payload_path = Path(td) / "rows_wrapped.json"
            self._write_json(payload_path, {"rows": [{"stockTakingRowId": "row-1"}]})

            rc, payload = self._run(
                env_path=env_path,
                args=["stock-taking", "add-rows", "--id", "7", "--json-file", str(payload_path)],
            )

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("raw top-level array", payload["error"])

    def test_stock_taking_add_rows_apply_posts_raw_array_and_verifies_rows(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            payload_path = Path(td) / "rows.json"
            payload_rows = [{"stockTakingRowId": "row-1", "itemId": "A-1", "stockPointId": "sp-1"}]
            self._write_json(payload_path, payload_rows)

            with patch("fortnox_api_tool.commands.stock_taking.request_data") as request_data:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["stock-taking", "add-rows", "--id", "7", "--json-file", str(payload_path)],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_data.side_effect = [
                    _api_response(status=204, path="/api/warehouse/stocktaking-v1/7/rows", body=None),
                    _api_response(
                        status=200,
                        path="/api/warehouse/stocktaking-v1/7/rows",
                        body={"rows": [{"stockTakingRowId": "row-1"}]},
                    ),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "stock-taking",
                        "add-rows",
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
        self.assertEqual(request_data.call_args_list[0].kwargs["json_body"], payload_rows)
        self.assertTrue(payload_apply["receipt"]["verification"]["verification_row_ids_present"])

    def test_stock_taking_add_rows_by_filter_apply_shapes_query_and_verifies_rows(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            with patch("fortnox_api_tool.commands.stock_taking.request_data") as request_data:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=[
                        "stock-taking",
                        "add-rows-by-filter",
                        "--id",
                        "7",
                        "--item-id",
                        "A-1",
                        "--supplier-number",
                        "100",
                        "--exclude-zero-balance-items",
                        "--exclude-non-inbound-items",
                    ],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_data.side_effect = [
                    _api_response(
                        status=201,
                        path="/api/warehouse/stocktaking-v1/7/addrows",
                        body=[{"stockTakingRowId": "row-2"}],
                    ),
                    _api_response(
                        status=200,
                        path="/api/warehouse/stocktaking-v1/7/rows",
                        body={"rows": [{"stockTakingRowId": "row-2"}]},
                    ),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "stock-taking",
                        "add-rows-by-filter",
                        "--id",
                        "7",
                        "--item-id",
                        "A-1",
                        "--supplier-number",
                        "100",
                        "--exclude-zero-balance-items",
                        "--exclude-non-inbound-items",
                        "--apply",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply["ok"])
        self.assertEqual(
            request_data.call_args_list[0].kwargs["query_params"],
            {
                "itemIds": ["A-1"],
                "supplierNumbers": ["100"],
                "excludeZeroBalanceItems": True,
                "excludeNonInboundItems": True,
            },
        )
        self.assertTrue(payload_apply["receipt"]["verification"]["verification_row_ids_present"])

    def test_stock_taking_delete_refuses_without_yes_and_ack(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            with patch("fortnox_api_tool.commands.stock_taking.request_data") as request_data:
                rc, plan_payload = self._run(env_path=env_path, args=["stock-taking", "delete", "--id", "7"])
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=["stock-taking", "delete", "--id", "7", "--apply", "--plan-in", str(plan_path)],
                )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply.get("refused", False))
        self.assertEqual(request_data.call_count, 0)
        self.assertIn("--apply --yes", " ".join(payload_apply["reasons"]))
        self.assertIn("ack-irreversible", " ".join(payload_apply["reasons"]).lower())

    def test_stock_taking_delete_apply_verifies_absence(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            with patch("fortnox_api_tool.commands.stock_taking.request_data") as request_data:
                rc, plan_payload = self._run(env_path=env_path, args=["stock-taking", "delete", "--id", "7"])
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_data.side_effect = [
                    _api_response(status=204, path="/api/warehouse/stocktaking-v1/7", body=None),
                    Exception("HTTP 404 for GET /api/warehouse/stocktaking-v1/7"),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "stock-taking",
                        "delete",
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
        self.assertEqual(request_data.call_args_list[0].kwargs["method"], "DELETE")
        self.assertTrue(payload_apply["receipt"]["verification"]["verification_absent"])

    def test_stock_taking_delete_row_apply_verifies_row_absence(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            with patch("fortnox_api_tool.commands.stock_taking.request_data") as request_data:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["stock-taking", "delete-row", "--id", "7", "--row-id", "row-1"],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_data.side_effect = [
                    _api_response(status=200, path="/api/warehouse/stocktaking-v1/7/rows/row-1", body={"removed": True}),
                    _api_response(
                        status=200,
                        path="/api/warehouse/stocktaking-v1/7/rows",
                        body={"rows": [{"stockTakingRowId": "row-2"}]},
                    ),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "stock-taking",
                        "delete-row",
                        "--id",
                        "7",
                        "--row-id",
                        "row-1",
                        "--apply",
                        "--yes",
                        "--ack-irreversible",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply["ok"])
        self.assertTrue(payload_apply["receipt"]["verification"]["verification_row_absent"])

    def test_stock_taking_delete_rows_refuses_without_ack(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            with patch("fortnox_api_tool.commands.stock_taking.request_data") as request_data:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["stock-taking", "delete-rows", "--id", "7", "--item-id", "A-1"],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "stock-taking",
                        "delete-rows",
                        "--id",
                        "7",
                        "--item-id",
                        "A-1",
                        "--apply",
                        "--yes",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply.get("refused", False))
        self.assertEqual(request_data.call_count, 0)
        self.assertIn("ack-irreversible", " ".join(payload_apply["reasons"]).lower())

    def test_stock_taking_delete_rows_apply_shapes_query_and_verifies_absence(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            with patch("fortnox_api_tool.commands.stock_taking.request_data") as request_data:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=[
                        "stock-taking",
                        "delete-rows",
                        "--id",
                        "7",
                        "--item-id",
                        "A-1",
                        "--stock-point-id",
                        "sp-1",
                        "--exclude-zero-balance-items",
                    ],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_data.side_effect = [
                    _api_response(
                        status=200,
                        path="/api/warehouse/stocktaking-v1/7/rows",
                        body=[{"stockTakingRowId": "row-1"}],
                    ),
                    _api_response(
                        status=200,
                        path="/api/warehouse/stocktaking-v1/7/rows",
                        body={"rows": [{"stockTakingRowId": "row-2"}]},
                    ),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "stock-taking",
                        "delete-rows",
                        "--id",
                        "7",
                        "--item-id",
                        "A-1",
                        "--stock-point-id",
                        "sp-1",
                        "--exclude-zero-balance-items",
                        "--apply",
                        "--yes",
                        "--ack-irreversible",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply["ok"])
        self.assertEqual(
            request_data.call_args_list[0].kwargs["query_params"],
            {
                "itemIds": ["A-1"],
                "stockPointIds": ["sp-1"],
                "excludeZeroBalanceItems": True,
            },
        )
        self.assertTrue(payload_apply["receipt"]["verification"]["verification_row_ids_absent"])

    def test_stock_taking_release_refuses_without_yes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            rc, plan_payload = self._run(env_path=env_path, args=["stock-taking", "release", "--id", "7"])
            self.assertEqual(rc, 0)
            plan = self._plan_from_output(plan_payload)
            plan_path = Path(td) / "plan.json"
            plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

            rc_apply, payload_apply = self._run(
                env_path=env_path,
                args=["stock-taking", "release", "--id", "7", "--apply", "--plan-in", str(plan_path)],
            )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply.get("refused", False))
        self.assertIn("--apply --yes", " ".join(payload_apply["reasons"]))

    def test_stock_taking_release_apply_verifies_completed_state(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            with patch("fortnox_api_tool.commands.stock_taking.request_data") as request_data:
                rc, plan_payload = self._run(env_path=env_path, args=["stock-taking", "release", "--id", "7"])
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_data.side_effect = [
                    _api_response(status=204, path="/api/warehouse/stocktaking-v1/7/release", body=None),
                    _api_response(
                        status=200,
                        path="/api/warehouse/stocktaking-v1/7",
                        body={"id": 7, "state": "completed"},
                    ),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "stock-taking",
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
        self.assertEqual(request_data.call_args_list[0].kwargs["expect_json"], False)
        self.assertTrue(payload_apply["receipt"]["verification"]["verification_completed_state"])

    def test_stock_taking_void_requires_ack(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            rc, plan_payload = self._run(env_path=env_path, args=["stock-taking", "void", "--id", "7"])
            self.assertEqual(rc, 0)
            plan = self._plan_from_output(plan_payload)
            plan_path = Path(td) / "plan.json"
            plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

            rc_apply, payload_apply = self._run(
                env_path=env_path,
                args=[
                    "stock-taking",
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
        self.assertTrue(payload_apply.get("refused", False))
        self.assertIn("ack-irreversible", " ".join(payload_apply["reasons"]).lower())

    def test_stock_taking_void_apply_verifies_voided_state(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            with patch("fortnox_api_tool.commands.stock_taking.request_data") as request_data:
                rc, plan_payload = self._run(env_path=env_path, args=["stock-taking", "void", "--id", "7"])
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_data.side_effect = [
                    _api_response(status=204, path="/api/warehouse/stocktaking-v1/7/void", body=None),
                    _api_response(
                        status=200,
                        path="/api/warehouse/stocktaking-v1/7",
                        body={"id": 7, "state": "voided"},
                    ),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "stock-taking",
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
        self.assertEqual(request_data.call_args_list[0].kwargs["expect_json"], False)
        self.assertTrue(payload_apply["receipt"]["verification"]["verification_voided_state"])
