from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fortnox_api_tool import api_runtime
from fortnox_api_tool.config import load_config


class _FakeResponse:
    def __init__(self, *, status: int, url: str, body: object, headers: dict[str, str] | None = None):
        self.status = status
        self.url = url
        self.body = body
        self.headers = headers or {}

    def json(self) -> object:
        return self.body


class TestApiRuntime(unittest.TestCase):
    def test_request_json_uses_origin_for_time_reporting_paths(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n", encoding="utf-8")
            cfg = load_config(str(env_path))
            ctx = {
                "cfg": cfg,
                "env_file": str(env_path),
                "timeout_s": 30.0,
                "verbose": False,
                "tool": "fortnox-api-tool",
                "tool_version": "0.1.0",
            }
            with patch("fortnox_api_tool.api_runtime.resolve_access_token") as resolve_access_token:
                resolve_access_token.return_value.token = "token"
                resolve_access_token.return_value.expired = False
                resolve_access_token.return_value.source = "env"
                with patch("fortnox_api_tool.api_runtime.HttpClient") as http_client:
                    http_client.return_value.request.return_value = _FakeResponse(
                        status=200,
                        url="https://api.fortnox.se/api/time/registrations-v2",
                        body={"Registrations": []},
                    )
                    payload = api_runtime.request_json(
                        ctx=ctx,
                        method="GET",
                        path="/api/time/registrations-v2",
                        expect_json=True,
                    )
        self.assertEqual(payload["url"], "https://api.fortnox.se/api/time/registrations-v2")
        self.assertEqual(http_client.return_value.request.call_args.args[1], "https://api.fortnox.se/api/time/registrations-v2")

    def test_request_data_allows_non_object_json_when_enabled(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n", encoding="utf-8")
            cfg = load_config(str(env_path))
            ctx = {
                "cfg": cfg,
                "env_file": str(env_path),
                "timeout_s": 30.0,
                "verbose": False,
                "tool": "fortnox-api-tool",
                "tool_version": "0.1.0",
            }
            with patch("fortnox_api_tool.api_runtime.resolve_access_token") as resolve_access_token:
                resolve_access_token.return_value.token = "token"
                resolve_access_token.return_value.expired = False
                resolve_access_token.return_value.source = "env"
                with patch("fortnox_api_tool.api_runtime.HttpClient") as http_client:
                    http_client.return_value.request.return_value = _FakeResponse(
                        status=201,
                        url="https://api.fortnox.se/api/warehouse/documentdeliveries/custom/documenttypes-v1",
                        body=1,
                    )
                    payload = api_runtime.request_data(
                        ctx=ctx,
                        method="POST",
                        path="/api/warehouse/documentdeliveries/custom/documenttypes-v1",
                        json_body={"referenceType": "RETURNS", "category": "OUTBOUND"},
                        expect_json=True,
                        expect_json_object=False,
                    )
        self.assertEqual(payload["body"], 1)

    def test_request_multipart_file_passes_files_to_http_client(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n", encoding="utf-8")
            upload_path = Path(td) / "upload.txt"
            upload_path.write_text("hello", encoding="utf-8")
            cfg = load_config(str(env_path))
            ctx = {
                "cfg": cfg,
                "env_file": str(env_path),
                "timeout_s": 30.0,
                "verbose": False,
                "tool": "fortnox-api-tool",
                "tool_version": "0.1.0",
            }
            with patch("fortnox_api_tool.api_runtime.resolve_access_token") as resolve_access_token:
                resolve_access_token.return_value.token = "token"
                resolve_access_token.return_value.expired = False
                resolve_access_token.return_value.source = "env"
                with patch("fortnox_api_tool.api_runtime.HttpClient") as http_client:
                    http_client.return_value.request.return_value = _FakeResponse(
                        status=201,
                        url="https://api.fortnox.se/3/inbox?path=inbox_v",
                        body={"File": {"Id": "55", "Name": "upload.txt"}},
                    )
                    payload = api_runtime.request_multipart_file(
                        ctx=ctx,
                        method="POST",
                        path="/inbox",
                        file_path=str(upload_path),
                        query_params={"path": "inbox_v"},
                    )
        self.assertEqual(payload["body"]["File"]["Id"], "55")
        call = http_client.return_value.request.call_args
        self.assertEqual(call.kwargs["params"], {"path": "inbox_v"})
        self.assertIn("file", call.kwargs["files"])
        self.assertEqual(call.kwargs["files"]["file"][0], "upload.txt")

    def test_request_raw_returns_bytes_and_headers(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n", encoding="utf-8")
            cfg = load_config(str(env_path))
            ctx = {
                "cfg": cfg,
                "env_file": str(env_path),
                "timeout_s": 30.0,
                "verbose": False,
                "tool": "fortnox-api-tool",
                "tool_version": "0.1.0",
            }
            with patch("fortnox_api_tool.api_runtime.resolve_access_token") as resolve_access_token:
                resolve_access_token.return_value.token = "token"
                resolve_access_token.return_value.expired = False
                resolve_access_token.return_value.source = "env"
                with patch("fortnox_api_tool.api_runtime.HttpClient") as http_client:
                    http_client.return_value.request.return_value = _FakeResponse(
                        status=200,
                        url="https://api.fortnox.se/3/invoices/I-1001/preview",
                        body=b"%PDF-1.7",
                        headers={"content-type": "application/pdf"},
                    )
                    payload = api_runtime.request_raw(
                        ctx=ctx,
                        method="GET",
                        path="/invoices/I-1001/preview",
                        accept="application/pdf",
                    )
        self.assertEqual(payload["body_bytes"], b"%PDF-1.7")
        self.assertEqual(payload["content_type"], "application/pdf")
        call = http_client.return_value.request.call_args
        self.assertEqual(call.kwargs["headers"]["Accept"], "application/pdf")
