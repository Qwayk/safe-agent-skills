from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from typing import Any
from unittest.mock import patch

import requests

from awin_publisher_safe_agent_cli.cli import main


def _build_mock_response(method: str, url: str, params: dict[str, Any], payload: object) -> requests.Response:
    response = requests.Response()
    response.status_code = 200
    response._content = json.dumps(payload).encode("utf-8")
    response.headers["content-type"] = "application/json"
    response.url = requests.Request(method=method, url=url, params=params).prepare().url or url
    return response


class TestReadCommands(unittest.TestCase):
    def test_accounts_list_calls_accounts_endpoint_and_filters_publisher_only(self) -> None:
        captured: dict[str, Any] = {}
        token = "TOKEN_123"
        payload = {
            "accounts": [
                {"id": "100", "type": "publisher", "name": "Pub A", "status": "active"},
                {"id": "200", "type": "advertiser", "name": "Adv B", "status": "active"},
                {"id": "300", "accountType": "publisher_account", "accountName": "Pub C"},
            ]
        }

        @patch("awin_publisher_safe_agent_cli.http.requests.Session.request")
        def run(mocked_request) -> None:
            def fake_request(
                method: str,
                url: str,
                headers: dict[str, str] | None = None,
                params: dict[str, Any] | None = None,
                **kwargs: Any,
            ) -> requests.Response:
                captured["method"] = method
                captured["url"] = url
                captured["headers"] = headers or {}
                captured["params"] = params or {}
                return _build_mock_response(method, url, params or {}, payload)

            mocked_request.side_effect = fake_request

            with tempfile.TemporaryDirectory() as td:
                env_file = os.path.join(td, ".env")
                with open(env_file, "w", encoding="utf-8") as f:
                    f.write(f"AWIN_API_TOKEN={token}\n")

                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(["--output", "json", "--env-file", env_file, "accounts", "list"])

            out = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(out["ok"])
            self.assertEqual(out["operation"], "accounts.list")
            self.assertEqual(out["metadata"]["publisher_accounts_count"], 2)
            self.assertEqual([a["id"] for a in out["accounts"]], ["100", "300"])
            self.assertEqual(captured["method"], "GET")
            self.assertTrue(captured["url"].endswith("/accounts"))
            self.assertIn("accessToken", captured["params"])
            self.assertEqual(captured["params"]["accessToken"], token)
            self.assertIn("authorization", {k.lower() for k in captured["headers"].keys()})

        run()

    def test_programs_list_sends_expected_params(self) -> None:
        captured: dict[str, Any] = {}
        token = "TOKEN_456"
        payload = [{"id": "11", "advertiserName": "Example"}]

        @patch("awin_publisher_safe_agent_cli.http.requests.Session.request")
        def run(mocked_request) -> None:
            def fake_request(
                method: str,
                url: str,
                headers: dict[str, str] | None = None,
                params: dict[str, Any] | None = None,
                **kwargs: Any,
            ) -> requests.Response:
                captured["method"] = method
                captured["url"] = url
                captured["headers"] = headers or {}
                captured["params"] = params or {}
                return _build_mock_response(method, url, params or {}, payload)

            mocked_request.side_effect = fake_request

            with tempfile.TemporaryDirectory() as td:
                env_file = os.path.join(td, ".env")
                with open(env_file, "w", encoding="utf-8") as f:
                    f.write(f"AWIN_API_TOKEN={token}\n")

                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            env_file,
                            "programs",
                            "list",
                            "--publisher-id",
                            "777",
                            "--relationship",
                            "joined",
                            "--country-code",
                            "us",
                        ]
                    )

            out = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(out["ok"])
            self.assertEqual(out["operation"], "programs.list")
            self.assertEqual(out["publisher_id"], "777")
            self.assertEqual(out["metadata"]["country_code"], "US")
            self.assertEqual(captured["method"], "GET")
            self.assertTrue(captured["url"].endswith("/publishers/777/programmes"))
            self.assertEqual(captured["params"]["accessToken"], token)
            self.assertEqual(captured["params"]["relationship"], "joined")
            self.assertEqual(captured["params"]["countryCode"], "US")
            self.assertNotIn("includeHidden", captured["params"])

        run()

    def test_programs_details_sends_expected_params(self) -> None:
        captured: dict[str, Any] = {}
        token = "TOKEN_789"
        payload = {"id": "11", "advertiserName": "Example"}

        @patch("awin_publisher_safe_agent_cli.http.requests.Session.request")
        def run(mocked_request) -> None:
            def fake_request(
                method: str,
                url: str,
                headers: dict[str, str] | None = None,
                params: dict[str, Any] | None = None,
                **kwargs: Any,
            ) -> requests.Response:
                captured["method"] = method
                captured["url"] = url
                captured["params"] = params or {}
                return _build_mock_response(method, url, params or {}, payload)

            mocked_request.side_effect = fake_request

            with tempfile.TemporaryDirectory() as td:
                env_file = os.path.join(td, ".env")
                with open(env_file, "w", encoding="utf-8") as f:
                    f.write(f"AWIN_API_TOKEN={token}\n")

                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            env_file,
                            "programs",
                            "details",
                            "--publisher-id",
                            "777",
                            "--advertiser-id",
                            "55",
                            "--relationship",
                            "any",
                        ]
                    )

            out = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(out["ok"])
            self.assertEqual(out["operation"], "programs.details")
            self.assertEqual(out["publisher_id"], "777")
            self.assertEqual(out["advertiser_id"], "55")
            self.assertEqual(captured["method"], "GET")
            self.assertTrue(captured["url"].endswith("/publishers/777/programmedetails"))
            self.assertEqual(captured["params"]["accessToken"], token)
            self.assertEqual(captured["params"]["advertiserId"], "55")
            self.assertEqual(captured["params"]["relationship"], "any")

        run()

    def test_programs_details_requires_advertiser_id(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_file = os.path.join(td, ".env")
            with open(env_file, "w", encoding="utf-8") as f:
                f.write("AWIN_API_TOKEN=TOKEN_000\n")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        env_file,
                        "programs",
                        "details",
                        "--publisher-id",
                        "777",
                    ]
                )

        out = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertFalse(out["ok"])
        self.assertEqual(out["error_type"], "ValidationError")

    def test_programs_list_rejects_include_hidden_with_relationship(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_file = os.path.join(td, ".env")
            with open(env_file, "w", encoding="utf-8") as f:
                f.write("AWIN_API_TOKEN=TOKEN_111\n")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        env_file,
                        "programs",
                        "list",
                        "--publisher-id",
                        "777",
                        "--relationship",
                        "joined",
                        "--include-hidden",
                    ]
                )

        out = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertFalse(out["ok"])
        self.assertEqual(out["error_type"], "ValidationError")
        self.assertIn("include-hidden", out["error"])
