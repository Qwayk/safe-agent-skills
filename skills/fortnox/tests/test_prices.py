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


class TestPrices(unittest.TestCase):
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
        price_list: str = "PL-1000",
        article_number: str = "ART-1000",
        from_quantity: str = "1",
    ) -> None:
        payload = {
            "Price": {
                "PriceList": price_list,
                "ArticleNumber": article_number,
                "FromQuantity": from_quantity,
                "Price": 99.5,
            }
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def test_prices_create_dry_run_emits_plan(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "create.json"
            self._make_payload_file(payload_path)

            with patch("fortnox_api_tool.commands.prices.request_json") as request_json:
                rc, payload = self._run(env_path=env_path, args=["prices", "create", "--json-file", str(payload_path)])

            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["plan"].get("baseline", {}).get("payload_sha256"), _sha256(payload_path))
            self.assertEqual(request_json.call_count, 0)

    def test_prices_create_apply_rechecks_json_payload_hash(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "create.json"
            self._make_payload_file(payload_path)

            with patch("fortnox_api_tool.commands.prices.request_json") as request_json:
                rc, plan_payload = self._run(env_path=env_path, args=["prices", "create", "--json-file", str(payload_path)])
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                self.assertEqual(request_json.call_count, 0)

                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                payload_path.write_text(
                    json.dumps(
                        {
                            "Price": {
                                "PriceList": "PL-1000",
                                "ArticleNumber": "ART-1000",
                                "FromQuantity": "1",
                                "Price": 125,
                            }
                        },
                        indent=2,
                    ),
                    encoding="utf-8",
                )

                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=["prices", "create", "--json-file", str(payload_path), "--apply", "--plan-in", str(plan_path)],
                )

            self.assertEqual(rc_apply, 0)
            self.assertTrue(payload_apply.get("refused", False))
            self.assertIn("hash", " ".join(payload_apply["reasons"]).lower())
            self.assertEqual(request_json.call_count, 0)

    def test_prices_create_apply_uses_response_key_for_verification(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "create.json"
            payload_path.write_text(
                json.dumps({"Price": {"Price": 99.5}}, indent=2),
                encoding="utf-8",
            )

            with patch("fortnox_api_tool.commands.prices.request_json") as request_json:
                rc, plan_payload = self._run(env_path=env_path, args=["prices", "create", "--json-file", str(payload_path)])
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_json.side_effect = [
                    _api_response(
                        status=201,
                        path="/prices",
                        body={"Price": {"PriceList": "PL-2000", "ArticleNumber": "ART-2000", "FromQuantity": "5"}},
                    ),
                    _api_response(
                        status=200,
                        path="/prices/PL-2000/ART-2000/5",
                        body={"Price": {"PriceList": "PL-2000", "ArticleNumber": "ART-2000", "FromQuantity": "5"}},
                    ),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=["prices", "create", "--json-file", str(payload_path), "--apply", "--plan-in", str(plan_path)],
                )

            self.assertEqual(rc_apply, 0)
            self.assertTrue(payload_apply.get("ok", False))
            self.assertEqual(request_json.call_args_list[0].kwargs["method"], "POST")
            self.assertEqual(request_json.call_args_list[0].kwargs["path"], "/prices")
            self.assertEqual(request_json.call_args_list[1].kwargs["method"], "GET")
            self.assertEqual(request_json.call_args_list[1].kwargs["path"], "/prices/PL-2000/ART-2000/5")

    def test_prices_create_apply_uses_payload_fallback_for_verification(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "create.json"
            self._make_payload_file(payload_path, price_list="PL-1000", article_number="ART-1000", from_quantity="1")

            with patch("fortnox_api_tool.commands.prices.request_json") as request_json:
                rc, plan_payload = self._run(env_path=env_path, args=["prices", "create", "--json-file", str(payload_path)])
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_json.side_effect = [
                    _api_response(status=201, path="/prices", body={"Price": {}}),
                    _api_response(
                        status=200,
                        path="/prices/PL-1000/ART-1000/1",
                        body={"Price": {"PriceList": "PL-1000", "ArticleNumber": "ART-1000", "FromQuantity": "1"}},
                    ),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=["prices", "create", "--json-file", str(payload_path), "--apply", "--plan-in", str(plan_path)],
                )

            self.assertEqual(rc_apply, 0)
            self.assertTrue(payload_apply.get("ok", False))
            self.assertEqual(request_json.call_args_list[1].kwargs["path"], "/prices/PL-1000/ART-1000/1")

    def test_prices_create_apply_fails_without_full_key_for_verification(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "create.json"
            payload_path.write_text(
                json.dumps({"Price": {"Price": 99.5}}, indent=2),
                encoding="utf-8",
            )

            with patch("fortnox_api_tool.commands.prices.request_json") as request_json:
                rc, plan_payload = self._run(env_path=env_path, args=["prices", "create", "--json-file", str(payload_path)])
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_json.side_effect = [_api_response(status=201, path="/prices", body={"Price": {}})]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=["prices", "create", "--json-file", str(payload_path), "--apply", "--plan-in", str(plan_path)],
                )

            self.assertEqual(rc_apply, 1)
            self.assertFalse(payload_apply.get("ok", True))
            self.assertEqual(payload_apply.get("error_type"), "ValidationError")
            self.assertIn("Could not determine full price key", payload_apply.get("error", ""))

    def test_prices_create_rejects_missing_top_level_price(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "create.json"
            payload_path.write_text(json.dumps({"PriceList": "PL-1000"}, indent=2), encoding="utf-8")

            rc, payload = self._run(env_path=env_path, args=["prices", "create", "--json-file", str(payload_path)])

            self.assertEqual(rc, 1)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "ValidationError")
            self.assertIn("top-level Price object", payload["error"])

    def test_prices_update_dry_run_emits_plan(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "update.json"
            self._make_payload_file(payload_path)

            with patch("fortnox_api_tool.commands.prices.request_json") as request_json:
                rc, payload = self._run(
                    env_path=env_path,
                    args=["prices", "update", "--price-list", "PL-1000", "--article-number", "ART-1000", "--json-file", str(payload_path)],
                )

            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["plan"].get("selector", {}).get("price_list"), "PL-1000")
            self.assertEqual(request_json.call_count, 0)

    def test_prices_update_rejects_selector_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "update.json"
            self._make_payload_file(payload_path, price_list="PL-2000", article_number="ART-1000")

            rc, payload = self._run(
                env_path=env_path,
                args=["prices", "update", "--price-list", "PL-1000", "--article-number", "ART-1000", "--json-file", str(payload_path)],
            )

            self.assertEqual(rc, 1)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "ValidationError")
            self.assertIn("must match --price-list", payload["error"])

    def test_prices_update_apply_rechecks_json_payload_hash(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "update.json"
            self._make_payload_file(payload_path)

            with patch("fortnox_api_tool.commands.prices.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["prices", "update", "--price-list", "PL-1000", "--article-number", "ART-1000", "--json-file", str(payload_path)],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                self.assertEqual(request_json.call_count, 0)

                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                payload_path.write_text(
                    json.dumps(
                        {"Price": {"PriceList": "PL-1000", "ArticleNumber": "ART-1000", "FromQuantity": "1", "Price": 111}},
                        indent=2,
                    ),
                    encoding="utf-8",
                )

                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=["prices", "update", "--price-list", "PL-1000", "--article-number", "ART-1000", "--json-file", str(payload_path), "--apply", "--plan-in", str(plan_path)],
                )

            self.assertEqual(rc_apply, 0)
            self.assertTrue(payload_apply.get("refused", False))
            self.assertIn("hash", " ".join(payload_apply["reasons"]).lower())
            self.assertEqual(request_json.call_count, 0)

    def test_prices_update_apply_performs_put_get_verify(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "update.json"
            self._make_payload_file(payload_path)

            with patch("fortnox_api_tool.commands.prices.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["prices", "update", "--price-list", "PL-1000", "--article-number", "ART-1000", "--json-file", str(payload_path)],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_json.side_effect = [
                    _api_response(status=200, path="/prices/PL-1000/ART-1000", body={"Price": {"PriceList": "PL-1000", "ArticleNumber": "ART-1000"}}),
                    _api_response(status=200, path="/prices/PL-1000/ART-1000", body={"Price": {"PriceList": "PL-1000", "ArticleNumber": "ART-1000"}}),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=["prices", "update", "--price-list", "PL-1000", "--article-number", "ART-1000", "--json-file", str(payload_path), "--apply", "--plan-in", str(plan_path)],
                )

            self.assertEqual(rc_apply, 0)
            self.assertTrue(payload_apply.get("ok", False))
            self.assertEqual(request_json.call_args_list[0].kwargs["method"], "PUT")
            self.assertEqual(request_json.call_args_list[0].kwargs["path"], "/prices/PL-1000/ART-1000")
            self.assertEqual(request_json.call_args_list[1].kwargs["path"], "/prices/PL-1000/ART-1000")

    def test_prices_update_by_from_quantity_dry_run_emits_plan(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "update_by_from_quantity.json"
            self._make_payload_file(payload_path)

            with patch("fortnox_api_tool.commands.prices.request_json") as request_json:
                rc, payload = self._run(
                    env_path=env_path,
                    args=[
                        "prices",
                        "update-by-from-quantity",
                        "--price-list",
                        "PL-1000",
                        "--article-number",
                        "ART-1000",
                        "--from-quantity",
                        "1",
                        "--json-file",
                        str(payload_path),
                    ],
                )

            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["plan"].get("selector", {}).get("from_quantity"), "1")
            self.assertEqual(request_json.call_count, 0)

    def test_prices_update_by_from_quantity_rejects_selector_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "update_by_from_quantity.json"
            self._make_payload_file(payload_path, from_quantity="2")

            rc, payload = self._run(
                env_path=env_path,
                args=[
                    "prices",
                    "update-by-from-quantity",
                    "--price-list",
                    "PL-1000",
                    "--article-number",
                    "ART-1000",
                    "--from-quantity",
                    "1",
                    "--json-file",
                    str(payload_path),
                ],
            )

            self.assertEqual(rc, 1)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "ValidationError")
            self.assertIn("must match --from-quantity", payload["error"])

    def test_prices_update_by_from_quantity_apply_performs_put_get_verify(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )
            payload_path = Path(td) / "update_by_from_quantity.json"
            self._make_payload_file(payload_path)

            with patch("fortnox_api_tool.commands.prices.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=[
                        "prices",
                        "update-by-from-quantity",
                        "--price-list",
                        "PL-1000",
                        "--article-number",
                        "ART-1000",
                        "--from-quantity",
                        "1",
                        "--json-file",
                        str(payload_path),
                    ],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_json.side_effect = [
                    _api_response(status=200, path="/prices/PL-1000/ART-1000/1", body={"Price": {"PriceList": "PL-1000", "ArticleNumber": "ART-1000", "FromQuantity": "1"}}),
                    _api_response(status=200, path="/prices/PL-1000/ART-1000/1", body={"Price": {"PriceList": "PL-1000", "ArticleNumber": "ART-1000", "FromQuantity": "1"}}),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "prices",
                        "update-by-from-quantity",
                        "--price-list",
                        "PL-1000",
                        "--article-number",
                        "ART-1000",
                        "--from-quantity",
                        "1",
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
            self.assertEqual(request_json.call_args_list[0].kwargs["path"], "/prices/PL-1000/ART-1000/1")
            self.assertEqual(request_json.call_args_list[1].kwargs["path"], "/prices/PL-1000/ART-1000/1")

    def test_prices_delete_dry_run_emits_plan(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )

            with patch("fortnox_api_tool.commands.prices.request_json") as request_json:
                rc, payload = self._run(
                    env_path=env_path,
                    args=["prices", "delete", "--price-list", "PL-1000", "--article-number", "ART-1000", "--from-quantity", "1"],
                )

            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["plan"].get("selector", {}).get("from_quantity"), "1")
            self.assertEqual(request_json.call_count, 0)

    def test_prices_delete_apply_refuses_without_ack(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )

            with patch("fortnox_api_tool.commands.prices.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["prices", "delete", "--price-list", "PL-1000", "--article-number", "ART-1000", "--from-quantity", "1"],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "prices",
                        "delete",
                        "--price-list",
                        "PL-1000",
                        "--article-number",
                        "ART-1000",
                        "--from-quantity",
                        "1",
                        "--apply",
                        "--yes",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

            self.assertEqual(rc_apply, 0)
            self.assertTrue(payload_apply.get("refused", False))
            self.assertIn("ack-irreversible", " ".join(payload_apply.get("reasons", [])))
            self.assertEqual(request_json.call_count, 0)

    def test_prices_delete_apply_refuses_without_yes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )

            with patch("fortnox_api_tool.commands.prices.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["prices", "delete", "--price-list", "PL-1000", "--article-number", "ART-1000", "--from-quantity", "1"],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "prices",
                        "delete",
                        "--price-list",
                        "PL-1000",
                        "--article-number",
                        "ART-1000",
                        "--from-quantity",
                        "1",
                        "--apply",
                        "--ack-irreversible",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

            self.assertEqual(rc_apply, 0)
            self.assertTrue(payload_apply.get("refused", False))
            self.assertIn("--apply --yes", " ".join(payload_apply.get("reasons", [])))
            self.assertEqual(request_json.call_count, 0)

    def test_prices_delete_apply_performs_delete_and_404_verify(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text(
                "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
                encoding="utf-8",
            )

            with patch("fortnox_api_tool.commands.prices.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["prices", "delete", "--price-list", "PL-1000", "--article-number", "ART-1000", "--from-quantity", "1"],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_json.side_effect = [
                    _api_response(status=204, path="/prices/PL-1000/ART-1000/1", body={}),
                    RuntimeError("HTTP 404 for GET https://api.fortnox.se/3/prices/PL-1000/ART-1000/1"),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "prices",
                        "delete",
                        "--price-list",
                        "PL-1000",
                        "--article-number",
                        "ART-1000",
                        "--from-quantity",
                        "1",
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
            self.assertEqual(request_json.call_args_list[0].kwargs["path"], "/prices/PL-1000/ART-1000/1")
            self.assertEqual(request_json.call_args_list[1].kwargs["method"], "GET")
            self.assertEqual(request_json.call_args_list[1].kwargs["path"], "/prices/PL-1000/ART-1000/1")
