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


class TestWayOfDeliveries(unittest.TestCase):
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

    def _make_payload_file(
        self,
        path: Path,
        *,
        code: str = "ECO",
        description: str = "Economy delivery",
    ) -> None:
        payload = {
            "WayOfDelivery": {
                "Code": code,
                "Description": description,
            }
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def test_way_of_deliveries_list_is_wired(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\n", encoding="utf-8")
            buf = io.StringIO()
            with patch(
                "fortnox_api_tool.commands.accounting_reads.get_json",
                return_value={
                    "status": 200,
                    "url": "https://api.fortnox.se/3/wayofdeliveries",
                    "token_source": "env",
                    "token_expired": None,
                    "body": {"WayOfDeliveries": []},
                },
            ):
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            str(env_path),
                            "way-of-deliveries",
                            "list",
                        ]
                    )
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertEqual(payload["path"], "/wayofdeliveries")

    def test_way_of_deliveries_get_is_wired(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\n", encoding="utf-8")
            buf = io.StringIO()
            with patch(
                "fortnox_api_tool.commands.accounting_reads.get_json",
                return_value={
                    "status": 200,
                    "url": "https://api.fortnox.se/3/wayofdeliveries/ECO",
                    "token_source": "env",
                    "token_expired": None,
                    "body": {"WayOfDelivery": {"Code": "ECO"}},
                },
            ):
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            str(env_path),
                            "way-of-deliveries",
                            "get",
                            "--code",
                            "ECO",
                        ]
                    )
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertEqual(payload["path"], "/wayofdeliveries/ECO")

    def test_way_of_deliveries_create_dry_run_emits_plan(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "create.json"
            self._make_payload_file(payload_path, code="ECO")
            expected_hash = _sha256(payload_path)

            rc, payload = self._run(
                env_path=env_path,
                args=["way-of-deliveries", "create", "--json-file", str(payload_path)],
            )

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"].get("baseline", {}).get("payload_sha256"), expected_hash)

    def test_way_of_deliveries_create_rejects_missing_top_level_wrapper(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "create.json"
            payload_path.write_text(json.dumps({"Code": "ECO"}, indent=2), encoding="utf-8")

            rc, payload = self._run(
                env_path=env_path,
                args=["way-of-deliveries", "create", "--json-file", str(payload_path)],
            )

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("top-level WayOfDelivery object", payload["error"])

    def test_way_of_deliveries_create_apply_rechecks_json_payload_hash(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "create.json"
            self._make_payload_file(payload_path, code="ECO")

            with patch("fortnox_api_tool.commands.way_of_deliveries.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["way-of-deliveries", "create", "--json-file", str(payload_path)],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                self.assertEqual(request_json.call_count, 0)

                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                payload_path.write_text(json.dumps({"WayOfDelivery": {"Code": "ECO", "Description": "Updated"}}, indent=2), encoding="utf-8")
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "way-of-deliveries",
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

    def test_way_of_deliveries_create_apply_performs_post_get_verify(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "create.json"
            self._make_payload_file(payload_path, code="ECO")

            with patch("fortnox_api_tool.commands.way_of_deliveries.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["way-of-deliveries", "create", "--json-file", str(payload_path)],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_json.side_effect = [
                    _api_response(status=201, path="/wayofdeliveries", body={"WayOfDelivery": {"Code": "ECO"}}),
                    _api_response(status=200, path="/wayofdeliveries/ECO", body={"WayOfDelivery": {"Code": "ECO"}}),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "way-of-deliveries",
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
        self.assertEqual(request_json.call_args_list[0].kwargs["path"], "/wayofdeliveries")
        self.assertEqual(request_json.call_args_list[1].kwargs["method"], "GET")
        self.assertEqual(request_json.call_args_list[1].kwargs["path"], "/wayofdeliveries/ECO")

    def test_way_of_deliveries_create_apply_uses_response_code_for_verification(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "create.json"
            payload_path.write_text(json.dumps({"WayOfDelivery": {"Description": "Economy delivery"}}, indent=2), encoding="utf-8")

            with patch("fortnox_api_tool.commands.way_of_deliveries.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["way-of-deliveries", "create", "--json-file", str(payload_path)],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_json.side_effect = [
                    _api_response(status=201, path="/wayofdeliveries", body={"WayOfDelivery": {"Code": "ECO"}}),
                    _api_response(status=200, path="/wayofdeliveries/ECO", body={"WayOfDelivery": {"Code": "ECO"}}),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "way-of-deliveries",
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
        self.assertEqual(request_json.call_args_list[1].kwargs["path"], "/wayofdeliveries/ECO")

    def test_way_of_deliveries_create_apply_fails_without_code_on_verification(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "create.json"
            payload_path.write_text(json.dumps({"WayOfDelivery": {"Description": "Economy delivery"}}, indent=2), encoding="utf-8")

            with patch("fortnox_api_tool.commands.way_of_deliveries.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["way-of-deliveries", "create", "--json-file", str(payload_path)],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_json.side_effect = [
                    _api_response(status=201, path="/wayofdeliveries", body={"WayOfDelivery": {}}),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "way-of-deliveries",
                        "create",
                        "--json-file",
                        str(payload_path),
                        "--apply",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

        self.assertEqual(rc_apply, 1)
        self.assertFalse(payload_apply["ok"])
        self.assertEqual(payload_apply["error_type"], "ValidationError")
        self.assertIn("Code", payload_apply["error"])

    def test_way_of_deliveries_update_dry_run_emits_plan(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "update.json"
            self._make_payload_file(payload_path, code="ECO")
            expected_hash = _sha256(payload_path)

            rc, payload = self._run(
                env_path=env_path,
                args=["way-of-deliveries", "update", "--code", "ECO", "--json-file", str(payload_path)],
            )

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"].get("baseline", {}).get("payload_sha256"), expected_hash)

    def test_way_of_deliveries_update_rejects_selector_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "update.json"
            self._make_payload_file(payload_path, code="FAST")

            rc, payload = self._run(
                env_path=env_path,
                args=["way-of-deliveries", "update", "--code", "ECO", "--json-file", str(payload_path)],
            )

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("WayOfDelivery.Code", payload["error"])

    def test_way_of_deliveries_update_apply_rechecks_json_payload_hash(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "update.json"
            self._make_payload_file(payload_path, code="ECO")

            with patch("fortnox_api_tool.commands.way_of_deliveries.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["way-of-deliveries", "update", "--code", "ECO", "--json-file", str(payload_path)],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                self.assertEqual(request_json.call_count, 0)

                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                payload_path.write_text(json.dumps({"WayOfDelivery": {"Code": "ECO", "Description": "Updated"}}, indent=2), encoding="utf-8")
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "way-of-deliveries",
                        "update",
                        "--code",
                        "ECO",
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

    def test_way_of_deliveries_update_apply_performs_put_get_verify(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "update.json"
            self._make_payload_file(payload_path, code="ECO")

            with patch("fortnox_api_tool.commands.way_of_deliveries.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["way-of-deliveries", "update", "--code", "ECO", "--json-file", str(payload_path)],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_json.side_effect = [
                    _api_response(status=200, path="/wayofdeliveries/ECO", body={"WayOfDelivery": {"Code": "ECO"}}),
                    _api_response(status=200, path="/wayofdeliveries/ECO", body={"WayOfDelivery": {"Code": "ECO"}}),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "way-of-deliveries",
                        "update",
                        "--code",
                        "ECO",
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
        self.assertEqual(request_json.call_args_list[0].kwargs["path"], "/wayofdeliveries/ECO")
        self.assertEqual(request_json.call_args_list[1].kwargs["method"], "GET")
        self.assertEqual(request_json.call_args_list[1].kwargs["path"], "/wayofdeliveries/ECO")

    def test_way_of_deliveries_remove_dry_run_emits_plan(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )

            rc, payload = self._run(env_path=env_path, args=["way-of-deliveries", "remove", "--code", "ECO"])

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["dry_run"])

    def test_way_of_deliveries_remove_apply_refuses_without_yes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )

            rc, payload = self._run(
                env_path=env_path,
                args=["way-of-deliveries", "remove", "--code", "ECO", "--apply"],
            )

        self.assertEqual(rc, 0)
        self.assertTrue(payload.get("refused", False))
        self.assertIn("--apply --yes", " ".join(payload["reasons"]))

    def test_way_of_deliveries_remove_apply_refuses_without_ack_irreversible(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )

            rc, payload = self._run(
                env_path=env_path,
                args=["way-of-deliveries", "remove", "--code", "ECO", "--apply", "--yes"],
            )

        self.assertEqual(rc, 0)
        self.assertTrue(payload.get("refused", False))
        self.assertIn("ack-irreversible", " ".join(payload["reasons"]).lower())

    def test_way_of_deliveries_remove_apply_performs_delete_and_404_verify(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )

            with patch("fortnox_api_tool.commands.way_of_deliveries.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["way-of-deliveries", "remove", "--code", "ECO"],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_json.side_effect = [
                    _api_response(status=204, path="/wayofdeliveries/ECO", body={}),
                    RuntimeError("HTTP 404 for GET https://api.fortnox.se/3/wayofdeliveries/ECO"),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "way-of-deliveries",
                        "remove",
                        "--code",
                        "ECO",
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
        self.assertEqual(request_json.call_args_list[0].kwargs["path"], "/wayofdeliveries/ECO")
        self.assertEqual(request_json.call_args_list[1].kwargs["method"], "GET")
        self.assertEqual(request_json.call_args_list[1].kwargs["path"], "/wayofdeliveries/ECO")
