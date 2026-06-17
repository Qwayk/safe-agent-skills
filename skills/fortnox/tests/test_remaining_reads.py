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


class TestRemainingReads(unittest.TestCase):
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

    def _write_env(self, td: str) -> Path:
        env_path = Path(td) / ".env"
        env_path.write_text(
            "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
            encoding="utf-8",
        )
        return env_path

    def _write_article_url_connection_payload(
        self,
        path: Path,
        *,
        article_number: str = "ART-100",
        url_connection: str = "https://example.com/article/ART-100",
    ) -> None:
        path.write_text(
            json.dumps(
                {
                    "ArticleUrlConnection": {
                        "ArticleNumber": article_number,
                        "URLConnection": url_connection,
                    }
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    def test_article_url_connections_list_wires_optional_article_number(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            with patch("fortnox_api_tool.commands.remaining_reads.request_data") as request_data:
                request_data.return_value = _api_response(
                    status=200,
                    path="/3/articleurlconnections?articlenumber=100",
                    body={"ItemUrlConnections": []},
                )
                rc, payload = self._run(
                    env_path=env_path,
                    args=["article-url-connections", "list", "--article-number", "100"],
                )

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["path"], "/articleurlconnections")
        self.assertEqual(request_data.call_args.kwargs["query_params"], {"articlenumber": "100"})

    def test_article_url_connections_create_dry_run_emits_plan(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            payload_path = Path(td) / "create.json"
            self._write_article_url_connection_payload(payload_path)

            with patch("fortnox_api_tool.commands.remaining_reads.request_json") as request_json:
                rc, payload = self._run(
                    env_path=env_path,
                    args=["article-url-connections", "create", "--json-file", str(payload_path)],
                )

            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["plan"].get("baseline", {}).get("payload_sha256"), _sha256(payload_path))
            self.assertEqual(request_json.call_count, 0)

    def test_article_url_connections_create_apply_rechecks_json_payload_hash(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            payload_path = Path(td) / "create.json"
            self._write_article_url_connection_payload(payload_path)

            with patch("fortnox_api_tool.commands.remaining_reads.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["article-url-connections", "create", "--json-file", str(payload_path)],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                self._write_article_url_connection_payload(
                    payload_path,
                    article_number="ART-100",
                    url_connection="https://example.com/article/changed",
                )
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "article-url-connections",
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
        self.assertIn("reasons", payload_apply)
        self.assertIn("hash", " ".join(payload_apply["reasons"]).lower())
        self.assertEqual(request_json.call_count, 0)

    def test_article_url_connections_create_apply_performs_post_and_list_verify(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            payload_path = Path(td) / "create.json"
            self._write_article_url_connection_payload(
                payload_path,
                article_number="ART-100",
                url_connection="https://example.com/article/ART-100",
            )

            with patch("fortnox_api_tool.commands.remaining_reads.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["article-url-connections", "create", "--json-file", str(payload_path)],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_json.side_effect = [
                    _api_response(
                        status=201,
                        path="/3/articleurlconnections",
                        body={
                            "ArticleUrlConnection": {
                                "Id": 42,
                                "ArticleNumber": "ART-100",
                                "URLConnection": "https://example.com/article/ART-100",
                            }
                        },
                    ),
                    _api_response(
                        status=200,
                        path="/3/articleurlconnections/42",
                        body={
                            "ArticleUrlConnection": {
                                "Id": 42,
                                "ArticleNumber": "ART-100",
                                "URLConnection": "https://example.com/article/ART-100",
                            }
                        },
                    ),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "article-url-connections",
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
        self.assertEqual(request_json.call_args_list[0].kwargs["path"], "/articleurlconnections")
        self.assertEqual(
            request_json.call_args_list[0].kwargs["json_body"],
            {
                "ArticleUrlConnection": {
                    "ArticleNumber": "ART-100",
                    "URLConnection": "https://example.com/article/ART-100",
                }
            },
        )
        self.assertEqual(request_json.call_args_list[1].kwargs["method"], "GET")
        self.assertEqual(request_json.call_args_list[1].kwargs["path"], "/articleurlconnections/42")

    def test_article_url_connections_get_is_wired(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            with patch("fortnox_api_tool.commands.remaining_reads.get_json") as get_json:
                get_json.return_value = _api_response(
                    status=200,
                    path="/3/articleurlconnections/42",
                    body={"ArticleUrlConnection": {"Id": 42}},
                )
                rc, payload = self._run(
                    env_path=env_path,
                    args=["article-url-connections", "get", "--id", "42"],
                )

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["path"], "/articleurlconnections/42")
        self.assertEqual(get_json.call_args.kwargs["path"], "/articleurlconnections/42")

    def test_article_url_connections_update_apply_performs_put_and_get_verify(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            payload_path = Path(td) / "update.json"
            self._write_article_url_connection_payload(
                payload_path,
                article_number="ART-100",
                url_connection="https://example.com/article/updated",
            )

            with patch("fortnox_api_tool.commands.remaining_reads.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["article-url-connections", "update", "--id", "42", "--json-file", str(payload_path)],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_json.side_effect = [
                    _api_response(
                        status=200,
                        path="/3/articleurlconnections/42",
                        body={
                            "ArticleUrlConnection": {
                                "Id": 42,
                                "ArticleNumber": "ART-100",
                                "URLConnection": "https://example.com/article/updated",
                            }
                        },
                    ),
                    _api_response(
                        status=200,
                        path="/3/articleurlconnections/42",
                        body={
                            "ArticleUrlConnection": {
                                "Id": 42,
                                "ArticleNumber": "ART-100",
                                "URLConnection": "https://example.com/article/updated",
                            }
                        },
                    ),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "article-url-connections",
                        "update",
                        "--id",
                        "42",
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
        self.assertEqual(request_json.call_args_list[0].kwargs["path"], "/articleurlconnections/42")
        self.assertEqual(request_json.call_args_list[1].kwargs["method"], "GET")
        self.assertEqual(request_json.call_args_list[1].kwargs["path"], "/articleurlconnections/42")

    def test_article_url_connections_delete_apply_requires_irreversible_ack_and_verifies_absence(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)

            with patch("fortnox_api_tool.commands.remaining_reads.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["article-url-connections", "delete", "--id", "42"],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_json.side_effect = [
                    _api_response(
                        status=204,
                        path="/3/articleurlconnections/42",
                        body=None,
                    ),
                    Exception("HTTP 404 Not Found"),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "article-url-connections",
                        "delete",
                        "--id",
                        "42",
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
        self.assertEqual(request_json.call_args_list[0].kwargs["path"], "/articleurlconnections/42")
        self.assertEqual(request_json.call_args_list[1].kwargs["method"], "GET")
        self.assertEqual(request_json.call_args_list[1].kwargs["path"], "/articleurlconnections/42")

    def test_eu_vat_limit_regulation_get_wires_optional_year(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            with patch("fortnox_api_tool.commands.remaining_reads.request_data") as request_data:
                request_data.return_value = _api_response(
                    status=200,
                    path="/3/euvatlimitregulation?year=2026",
                    body={"EUVatLimitRegulation": {"Year": 2026}},
                )
                rc, payload = self._run(
                    env_path=env_path,
                    args=["eu-vat-limit-regulation", "get", "--year", "2026"],
                )

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["path"], "/euvatlimitregulation")
        self.assertEqual(request_data.call_args.kwargs["query_params"], {"year": 2026})

    def test_integration_ratings_list_allows_array_response(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            with patch("fortnox_api_tool.commands.remaining_reads.request_data") as request_data:
                request_data.return_value = _api_response(
                    status=200,
                    path="/api/integration-developer/ratings-v1",
                    body=[{"score": 5}],
                )
                rc, payload = self._run(env_path=env_path, args=["integration-ratings", "list"])

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["path"], "/api/integration-developer/ratings-v1")
        self.assertFalse(request_data.call_args.kwargs["expect_json_object"])

    def test_sie_get_emits_stream_text_and_query_params(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            with patch("fortnox_api_tool.commands.remaining_reads._stream_request") as stream_request:
                stream_request.return_value = {
                    "status": 200,
                    "token_source": "env",
                    "token_expired": None,
                    "content_type": "application/octet-stream",
                    "body": "#FLAGGA 0\n",
                }
                rc, payload = self._run(
                    env_path=env_path,
                    args=[
                        "sie",
                        "get",
                        "--type",
                        "4",
                        "--financial-year",
                        "1",
                        "--selection",
                        "all",
                    ],
                )

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["path"], "/sie/4")
        self.assertEqual(payload["content_type"], "application/octet-stream")
        self.assertIn("#FLAGGA 0", payload["data"])
        self.assertEqual(
            stream_request.call_args.kwargs["query_params"],
            {"selection": "all", "financialYear": 1},
        )

    def test_stock_status_get_stock_balance_wires_repeatable_filters(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            with patch("fortnox_api_tool.commands.remaining_reads.request_data") as request_data:
                request_data.return_value = _api_response(
                    status=200,
                    path="/api/warehouse/status-v1/stockbalance",
                    body=[{"itemId": 10, "stockPointCode": "A1"}],
                )
                rc, payload = self._run(
                    env_path=env_path,
                    args=[
                        "stock-status",
                        "get-stock-balance",
                        "--item-id",
                        "10",
                        "--item-id",
                        "11",
                        "--stock-point-code",
                        "A1",
                    ],
                )

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["path"], "/api/warehouse/status-v1/stockbalance")
        self.assertEqual(
            request_data.call_args.kwargs["query_params"],
            {"itemIds": "10,11", "stockPointCodes": "A1"},
        )

    def test_tenant_get_is_wired(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            with patch("fortnox_api_tool.commands.remaining_reads.request_data") as request_data:
                request_data.return_value = _api_response(
                    status=200,
                    path="/api/warehouse/tenants-v4",
                    body={"active": True},
                )
                rc, payload = self._run(env_path=env_path, args=["tenant", "get"])

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["path"], "/api/warehouse/tenants-v4")
        self.assertEqual(request_data.call_args.kwargs["path"], "/api/warehouse/tenants-v4")

    def test_users_fetch_single_is_wired(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            with patch("fortnox_api_tool.commands.remaining_reads.request_data") as request_data:
                request_data.return_value = _api_response(
                    status=200,
                    path="/api/integration-developer/users/users-v1/7/55",
                    body=[{"userId": 1}],
                )
                rc, payload = self._run(
                    env_path=env_path,
                    args=[
                        "users",
                        "fetch-user-information-for-a-single-published-integration-and-tenant",
                        "--integration-id",
                        "7",
                        "--tenant-id",
                        "55",
                    ],
                )

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["path"], "/api/integration-developer/users/users-v1/7/55")
        self.assertEqual(
            request_data.call_args.kwargs["path"],
            "/api/integration-developer/users/users-v1/7/55",
        )
