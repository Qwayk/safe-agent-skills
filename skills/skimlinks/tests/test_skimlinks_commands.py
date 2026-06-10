from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

from skimlinks_safe_agent_cli.cli import main
from skimlinks_safe_agent_cli.http import redact_url


class FakeResponse:
    def __init__(self, *, url: str, body: Any, status: int = 200):
        self.url = url
        self.status = status
        self.headers = {"content-type": "application/json"}
        if isinstance(body, bytes):
            self.body = body
        else:
            self.body = json.dumps(body).encode("utf-8")

    def json(self) -> Any:
        return json.loads(self.body.decode("utf-8"))

    def text(self) -> str:
        return self.body.decode("utf-8")


class FakeHttp:
    def __init__(self, *, fail_auth: bool = False):
        self.fail_auth = fail_auth
        self.calls: list[dict[str, Any]] = []

    def request(self, method: str, url: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"method": method, "url": url, **kwargs})
        if "authentication.skimapis.com" in url:
            if self.fail_auth:
                raise RuntimeError("HTTP 401 for auth")
            return FakeResponse(
                url=url,
                body={
                    "access_token": "TOKEN:SECRET",
                    "timestamp": 1,
                    "expiry_timestamp": 2,
                },
            )
        if "aggregation/v1/link-report" in url and not url.endswith(("dimensions", "metrics")):
            return FakeResponse(url=url, body=b'{"device_type":"mobile","clicks":3}\n')
        return FakeResponse(url=url, body={"result": "ok"})


def _env_file(root: Path, extra: str = "") -> str:
    path = root / ".env"
    path.write_text(
        "\n".join(
            [
                "SKIMLINKS_CLIENT_ID=client_123",
                "SKIMLINKS_CLIENT_SECRET=secret_abc",
                "SKIMLINKS_PRODUCT_CLIENT_ID=product_client",
                "SKIMLINKS_PRODUCT_CLIENT_SECRET=product_secret",
                "SKIMLINKS_PUBLISHER_ID=777",
                "SKIMLINKS_PUBLISHER_DOMAIN_ID=888",
                "SKIMLINKS_LINK_WRAPPER_ID=777X888",
                extra,
            ]
        ),
        encoding="utf-8",
    )
    return str(path)


def _run(argv: list[str]) -> tuple[int, dict[str, Any]]:
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = main(["--output", "json", *argv])
    return rc, json.loads(buf.getvalue())


class TestSkimlinksCommands(unittest.TestCase):
    def test_redact_url_removes_access_token(self) -> None:
        safe = redact_url("https://example.test/path?access_token=SECRET&search=ok")
        self.assertNotIn("SECRET", safe)
        self.assertIn("access_token=%3Credacted%3E", safe)
        self.assertIn("search=ok", safe)

    def test_auth_failure_does_not_leak_secret_env_values(self) -> None:
        fake = FakeHttp(fail_auth=True)
        with tempfile.TemporaryDirectory() as td:
            env_file = _env_file(Path(td))
            with patch("skimlinks_safe_agent_cli.commands.auth.make_http_client", return_value=fake):
                rc, payload = _run(["--env-file", env_file, "auth", "check"])
        self.assertEqual(rc, 1)
        text = json.dumps(payload)
        self.assertNotIn("secret_abc", text)
        self.assertNotIn("client_123", text)
        self.assertFalse(payload["ok"])

    def test_merchant_merchants_list_passes_filters_and_domain_default(self) -> None:
        fake = FakeHttp()
        with tempfile.TemporaryDirectory() as td:
            env_file = _env_file(Path(td))
            with patch("skimlinks_safe_agent_cli.commands.merchant.make_http_client", return_value=fake):
                rc, payload = _run(
                    [
                        "--env-file",
                        env_file,
                        "merchant",
                        "merchants",
                        "list",
                        "--search",
                        "laptop",
                        "--limit",
                        "5",
                    ]
                )
        self.assertEqual(rc, 0)
        self.assertEqual(payload["operation"], "merchants.list")
        api_call = fake.calls[-1]
        self.assertEqual(api_call["method"], "GET")
        self.assertIn("/v4/publisher/777/merchants", api_call["url"])
        self.assertEqual(api_call["params"]["search"], "laptop")
        self.assertEqual(api_call["params"]["limit"], 5)
        self.assertEqual(api_call["params"]["publisher_domain_id"], "888")
        self.assertIn("access_token", api_call["params"])

    def test_reporting_link_report_query_passes_repeated_dimensions_and_metrics(self) -> None:
        fake = FakeHttp()
        with tempfile.TemporaryDirectory() as td:
            env_file = _env_file(Path(td))
            with patch("skimlinks_safe_agent_cli.commands.reporting.make_http_client", return_value=fake):
                rc, payload = _run(
                    [
                        "--env-file",
                        env_file,
                        "reporting",
                        "link-report",
                        "query",
                        "--start-date",
                        "2026-01-01",
                        "--end-date",
                        "2026-01-31",
                        "--dim",
                        "device_type",
                        "--dim",
                        "merchant_id",
                        "--met",
                        "clicks",
                    ]
                )
        self.assertEqual(rc, 0)
        self.assertEqual(payload["operation"], "link_report.query")
        api_call = fake.calls[-1]
        self.assertEqual(api_call["params"]["dim"], ["device_type", "merchant_id"])
        self.assertEqual(api_call["params"]["met"], ["clicks"])
        self.assertEqual(payload["rows"][0]["device_type"], "mobile")

    def test_product_key_products_get_uses_product_credentials_and_body(self) -> None:
        fake = FakeHttp()
        with tempfile.TemporaryDirectory() as td:
            env_file = _env_file(Path(td))
            with patch("skimlinks_safe_agent_cli.commands.product_key.make_http_client", return_value=fake):
                rc, payload = _run(
                    [
                        "--env-file",
                        env_file,
                        "product-key",
                        "products",
                        "get",
                        "--product-url",
                        "https://merchant.example/item-1,https://merchant.example/item-2",
                        "--sort-desc",
                        "desc",
                    ]
                )
        self.assertEqual(rc, 0)
        self.assertEqual(payload["operation"], "products.get")
        auth_call = fake.calls[0]
        self.assertEqual(auth_call["json_body"]["client_id"], "product_client")
        api_call = fake.calls[-1]
        self.assertEqual(api_call["method"], "POST")
        self.assertIn("/v1/publisher/777/products", api_call["url"])
        self.assertEqual(
            api_call["json_body"]["product_urls"],
            ["https://merchant.example/item-1", "https://merchant.example/item-2"],
        )
        query = parse_qs(urlsplit(api_call["url"]).query)
        self.assertEqual(query["publisher_domain_id"], ["888"])
        self.assertEqual(query["sort_desc"], ["desc"])
        self.assertIn("access_token", query)

    def test_product_key_requires_publisher_domain_id_for_both_commands(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_file = _env_file(Path(td), "SKIMLINKS_PUBLISHER_DOMAIN_ID=")
            for argv in (
                [
                    "--env-file",
                    env_file,
                    "product-key",
                    "product",
                    "get",
                    "--product-url",
                    "https://merchant.example/item",
                ],
                [
                    "--env-file",
                    env_file,
                    "product-key",
                    "products",
                    "get",
                    "--product-url",
                    "https://merchant.example/item",
                ],
            ):
                with self.subTest(argv=argv):
                    rc, payload = _run(argv)
                    self.assertEqual(rc, 1)
                    self.assertFalse(payload["ok"])
                    self.assertIn("publisher domain ID", payload["error"])

    def test_product_key_product_get_passes_official_sort_desc_string(self) -> None:
        fake = FakeHttp()
        with tempfile.TemporaryDirectory() as td:
            env_file = _env_file(Path(td))
            with patch("skimlinks_safe_agent_cli.commands.product_key.make_http_client", return_value=fake):
                rc, payload = _run(
                    [
                        "--env-file",
                        env_file,
                        "product-key",
                        "product",
                        "get",
                        "--product-url",
                        "https://merchant.example/item",
                        "--sort-by",
                        "epc",
                        "--sort-desc",
                        "asc",
                    ]
                )
        self.assertEqual(rc, 0)
        self.assertEqual(payload["operation"], "product.get")
        api_call = fake.calls[-1]
        self.assertEqual(api_call["params"]["sort_by"], "epc")
        self.assertEqual(api_call["params"]["sort_desc"], "asc")
        self.assertIsInstance(api_call["params"]["sort_desc"], str)

    def test_link_wrapper_build_encodes_url_without_http(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_file = _env_file(Path(td))
            rc, payload = _run(
                [
                    "--env-file",
                    env_file,
                    "link-wrapper",
                    "build",
                    "--url",
                    "https://merchant.example/a product?x=1&y=2",
                    "--xcust",
                    "article-1",
                    "--sref",
                    "https://publisher.example/page",
                ]
            )
        self.assertEqual(rc, 0)
        self.assertEqual(payload["operation"], "build")
        self.assertFalse(payload["followed_redirect"])
        self.assertIn("https%3A%2F%2Fmerchant.example%2Fa+product%3Fx%3D1%26y%3D2", payload["wrapped_url"])
        self.assertIn("xcust=article-1", payload["wrapped_url"])
