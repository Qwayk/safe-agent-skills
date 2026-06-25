from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any
from unittest import mock

from contentsquare_safe_agent_cli.cli import main


class _Response:
    def __init__(self, payload: dict[str, Any]):
        self._payload = payload
        self.status = 200
        self.headers = {}
        self.body = json.dumps(payload).encode("utf-8")
        self.url = "https://api.contentsquare.example"

    def json(self) -> dict[str, Any]:
        return self._payload


def run_cli(argv: list[str]) -> tuple[int, dict]:
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = main(argv)
    return rc, json.loads(buf.getvalue())


def _env(path: Path, *, project_id: str | None = None) -> Path:
    lines = [
        "CONTENTSQUARE_CLIENT_ID=client",
        "CONTENTSQUARE_CLIENT_SECRET=secret",
        "CONTENTSQUARE_AUTH_BASE_URL=https://api.contentsquare.com",
        "CONTENTSQUARE_API_BASE_URL=https://api.eu.contentsquare.example",
    ]
    if project_id:
        lines.append(f"CONTENTSQUARE_PROJECT_ID={project_id}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _http_response(method: str, url: str, **kwargs: Any) -> _Response:
    if url.endswith("/v1/oauth/token"):
        body = kwargs.get("json_body") or {}
        return _Response(
            {
                "access_token": "token",
                "expires_in": 3600,
                "scope": body.get("scope"),
                "endpoint": "https://api.eu.contentsquare.example",
            }
        )
    if url.endswith("/v1/oauth/me"):
        return _Response({"scopes": "data-export metrics", "permissions": {"projects": [{"id": 42}]}})
    return _Response({"payload": [], "success": True})


def _token_bodies(calls: list[mock._Call]) -> list[dict[str, Any]]:
    return [
        dict(call.kwargs.get("json_body") or {})
        for call in calls
        if call.args and str(call.args[1]).endswith("/v1/oauth/token")
    ]


class OAuthRequestBodyTests(unittest.TestCase):
    def test_auth_check_defaults_to_data_export_scope_and_project_id(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env = _env(Path(td) / ".env", project_id="42")
            with mock.patch(
                "contentsquare_safe_agent_cli.contentsquare_client.HttpClient.request",
                side_effect=_http_response,
            ) as request:
                rc, payload = run_cli(["--env-file", str(env), "auth", "check"])
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(
                _token_bodies(request.call_args_list)[0],
                {
                    "grant_type": "client_credentials",
                    "client_id": "client",
                    "client_secret": "secret",
                    "scope": "data-export",
                    "project_id": "42",
                },
            )

    def test_auth_check_allows_explicit_scope_and_project_override(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env = _env(Path(td) / ".env", project_id="42")
            with mock.patch(
                "contentsquare_safe_agent_cli.contentsquare_client.HttpClient.request",
                side_effect=_http_response,
            ) as request:
                rc, payload = run_cli(
                    [
                        "--env-file",
                        str(env),
                        "--oauth-project-id",
                        "99",
                        "auth",
                        "check",
                        "--scope",
                        "data-export metrics",
                    ]
                )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            body = _token_bodies(request.call_args_list)[0]
            self.assertEqual(body["scope"], "data-export metrics")
            self.assertEqual(body["project_id"], "99")

    def test_auth_check_refuses_combined_enrichment_scope(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env = _env(Path(td) / ".env")
            with mock.patch(
                "contentsquare_safe_agent_cli.contentsquare_client.HttpClient.request",
                side_effect=_http_response,
            ) as request:
                rc, payload = run_cli(
                    [
                        "--env-file",
                        str(env),
                        "auth",
                        "check",
                        "--scope",
                        "enrichment metrics",
                    ]
                )
            self.assertEqual(rc, 1)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "ValidationError")
            self.assertEqual(_token_bodies(request.call_args_list), [])

    def test_auth_me_sends_documented_credentials_body_without_token(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env = _env(Path(td) / ".env")
            with mock.patch(
                "contentsquare_safe_agent_cli.contentsquare_client.HttpClient.request",
                side_effect=_http_response,
            ) as request:
                rc, payload = run_cli(["--env-file", str(env), "auth", "me"])
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(_token_bodies(request.call_args_list), [])
            self.assertEqual(len(request.call_args_list), 1)
            call = request.call_args_list[0]
            self.assertTrue(str(call.args[1]).endswith("/v1/oauth/me"))
            self.assertEqual(
                call.kwargs["json_body"],
                {"client_id": "client", "client_secret": "secret"},
            )
            self.assertNotIn("Authorization", call.kwargs.get("headers") or {})

    def test_data_export_command_token_body_uses_data_export_scope(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env = _env(Path(td) / ".env")
            with mock.patch(
                "contentsquare_safe_agent_cli.contentsquare_client.HttpClient.request",
                side_effect=_http_response,
            ) as request:
                rc, payload = run_cli(["--env-file", str(env), "data-export", "list-jobs"])
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(_token_bodies(request.call_args_list)[0]["scope"], "data-export")

    def test_metrics_command_token_body_uses_metrics_scope(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env = _env(Path(td) / ".env")
            with mock.patch(
                "contentsquare_safe_agent_cli.contentsquare_client.HttpClient.request",
                side_effect=_http_response,
            ) as request:
                rc, payload = run_cli(["--env-file", str(env), "metrics", "segments"])
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(_token_bodies(request.call_args_list)[0]["scope"], "metrics")

    def test_enrichment_command_token_body_uses_enrichment_scope_and_integration_id(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env = _env(Path(td) / ".env", project_id="42")
            plan = Path(td) / "plan.json"
            plan.write_text('{"proposed_changes": {"items": []}}', encoding="utf-8")
            with mock.patch(
                "contentsquare_safe_agent_cli.contentsquare_client.HttpClient.request",
                side_effect=_http_response,
            ) as request:
                rc, payload = run_cli(
                    [
                        "--env-file",
                        str(env),
                        "--plan-in",
                        str(plan),
                        "--apply",
                        "--yes",
                        "--ack-no-snapshot",
                        "enrichment",
                        "send-batch",
                        "--integration-id",
                        "123",
                    ]
                )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            body = _token_bodies(request.call_args_list)[0]
            self.assertEqual(body["scope"], "enrichment")
            self.assertEqual(body["integration_id"], "123")
            self.assertEqual(body["project_id"], "42")

    def test_enrichment_command_refuses_combined_scope_override(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env = _env(Path(td) / ".env", project_id="42")
            plan = Path(td) / "plan.json"
            plan.write_text('{"proposed_changes": {"items": []}}', encoding="utf-8")
            with mock.patch(
                "contentsquare_safe_agent_cli.contentsquare_client.HttpClient.request",
                side_effect=_http_response,
            ) as request:
                rc, payload = run_cli(
                    [
                        "--env-file",
                        str(env),
                        "--plan-in",
                        str(plan),
                        "--apply",
                        "--yes",
                        "--ack-no-snapshot",
                        "enrichment",
                        "send-batch",
                        "--integration-id",
                        "123",
                        "--scope",
                        "data-export enrichment",
                    ]
                )
            self.assertEqual(rc, 1)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "ValidationError")
            self.assertEqual(_token_bodies(request.call_args_list), [])

    def test_speed_analysis_command_token_body_uses_speed_analysis_scope(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env = _env(Path(td) / ".env")
            body_file = Path(td) / "body.json"
            body_file.write_text("{}", encoding="utf-8")
            with mock.patch(
                "contentsquare_safe_agent_cli.contentsquare_client.HttpClient.request",
                side_effect=_http_response,
            ) as request:
                rc, payload = run_cli(
                    [
                        "--env-file",
                        str(env),
                        "speed-analysis",
                        "monitoring-list",
                        "--body-json",
                        str(body_file),
                    ]
                )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(_token_bodies(request.call_args_list)[0]["scope"], "speed-analysis")


if __name__ == "__main__":
    unittest.main()
