from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

import requests

from n8n_safe_agent_cli.cli import main


class TestSecretLeakRegressions(unittest.TestCase):
    def _env(self, root: Path, *, api_key: str = "") -> Path:
        env_path = root / ".env"
        env_path.write_text(
            "N8N_BASE_URL=https://example.app.n8n.cloud/api/v1\n"
            f"N8N_API_KEY={api_key}\n"
            "N8N_TIMEOUT_S=30\n",
            encoding="utf-8",
        )
        return env_path

    def _assert_no_raw_secrets(self, text: str, secrets: list[str]) -> None:
        for secret in secrets:
            self.assertNotIn(secret, text)

    def test_write_plan_redacts_command_strings_everywhere(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = self._env(root)
            body_path = root / "customer-secret-body-file.json"
            body_path.write_text(
                json.dumps({"name": "workflow-secret-name", "nodes": [], "connections": {}}),
                encoding="utf-8",
            )
            audit_path = root / "audit.jsonl"
            plan_path = root / "plan.json"
            run_id = "2026-06-29T120000Z_redact"
            secrets = [
                "customer-secret-body-file.json",
                "workflow-secret-name",
                "secret-workflow-id-123",
                "raw-token-query-456",
            ]

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--run-id",
                        run_id,
                        "--log-file",
                        str(audit_path),
                        "--plan-out",
                        str(plan_path),
                        "api",
                        "workflow",
                        "update-workflow",
                        "--path-param",
                        "id=secret-workflow-id-123",
                        "--query",
                        "api_key=raw-token-query-456",
                        "--body-file",
                        str(body_path),
                    ]
                )

            self.assertEqual(rc, 0)
            surfaces = [
                buf.getvalue(),
                plan_path.read_text(encoding="utf-8"),
                audit_path.read_text(encoding="utf-8"),
                (root / ".state" / "runs" / run_id / "summary.md").read_text(encoding="utf-8"),
                (root / ".state" / "runs" / "index.jsonl").read_text(encoding="utf-8"),
            ]
            for surface in surfaces:
                self._assert_no_raw_secrets(surface, secrets)
            self.assertIn("[REDACTED", buf.getvalue())

    def test_http_error_text_is_redacted_before_output_audit_and_run_files(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = self._env(root, api_key="safe-test-key")
            audit_path = root / "audit.jsonl"
            plan_path = root / "plan.json"
            body_path = root / "workflow.json"
            body_path.write_text(
                json.dumps({"name": "Visible workflow", "nodes": [], "connections": {}}),
                encoding="utf-8",
            )
            run_id = "2026-06-29T121000Z_httpredact"
            secrets = ["provider-secret-body-789", "request-secret-token-abc"]

            class FakeSuccessResponse:
                status = 200
                status_code = 200
                url = "https://example.app.n8n.cloud/api/v1/workflows/safe-id"
                content = b"{}"
                headers = {}
                text = "{}"

                def json(self):
                    return {"id": "safe-id"}

            class FakeResponse:
                status_code = 400
                url = "https://example.app.n8n.cloud/api/v1/workflows?token=request-secret-token-abc"
                content = b""
                headers = {}
                text = '{"error":"provider-secret-body-789"}'

            with patch("n8n_safe_agent_cli.http.HttpClient.request", return_value=FakeSuccessResponse()):
                with redirect_stdout(io.StringIO()):
                    self.assertEqual(
                        main(
                            [
                                "--env-file",
                                str(env_path),
                                "--plan-out",
                                str(plan_path),
                                "api",
                                "workflow",
                                "update-workflow",
                                "--path-param",
                                "id=safe-id",
                                "--query",
                                "token=request-secret-token-abc",
                                "--body-file",
                                str(body_path),
                            ]
                        ),
                        0,
                    )

            with patch("requests.Session.request", return_value=FakeResponse()):
                out = io.StringIO()
                err = io.StringIO()
                with redirect_stdout(out), redirect_stderr(err):
                    rc = main(
                        [
                            "--env-file",
                            str(env_path),
                            "--run-id",
                            run_id,
                            "--log-file",
                            str(audit_path),
                            "--apply",
                            "--yes",
                            "--plan-in",
                            str(plan_path),
                            "--verbose",
                            "api",
                            "workflow",
                            "update-workflow",
                            "--path-param",
                            "id=safe-id",
                            "--query",
                            "token=request-secret-token-abc",
                            "--body-file",
                            str(body_path),
                        ]
                    )

            self.assertEqual(rc, 1)
            surfaces = [
                out.getvalue(),
                err.getvalue(),
                audit_path.read_text(encoding="utf-8"),
                (root / ".state" / "runs" / run_id / "summary.md").read_text(encoding="utf-8"),
                (root / ".state" / "runs" / "index.jsonl").read_text(encoding="utf-8"),
            ]
            for surface in surfaces:
                self._assert_no_raw_secrets(surface, secrets)

            def boom(*args, **kwargs):
                raise requests.RequestException("request-secret-token-abc provider-secret-body-789")

            with patch("requests.Session.request", side_effect=boom):
                out2 = io.StringIO()
                err2 = io.StringIO()
                with redirect_stdout(out2), redirect_stderr(err2):
                    rc2 = main(
                        [
                            "--env-file",
                            str(env_path),
                            "--verbose",
                            "api",
                            "workflow",
                            "get-workflows",
                            "--query",
                            "token=request-secret-token-abc",
                        ]
                    )
            self.assertEqual(rc2, 1)
            self._assert_no_raw_secrets(out2.getvalue(), secrets)
            self._assert_no_raw_secrets(err2.getvalue(), secrets)

    def test_http_error_body_redacts_secret_key_values_even_when_value_looks_plain(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = self._env(root, api_key="safe-test-key")
            audit_path = root / "audit.jsonl"
            plan_path = root / "plan.json"
            body_path = root / "workflow.json"
            body_path.write_text(
                json.dumps({"name": "Visible workflow", "nodes": [], "connections": {}}),
                encoding="utf-8",
            )
            run_id = "2026-06-29T122000Z_httpkeyredact"
            secrets = ["CREDLEAK456"]

            class FakeSuccessResponse:
                status = 200
                status_code = 200
                url = "https://example.app.n8n.cloud/api/v1/workflows/safe-id"
                content = b"{}"
                headers = {}
                text = "{}"

                def json(self):
                    return {"id": "safe-id"}

            class FakeCredentialErrorResponse:
                status_code = 400
                url = "https://example.app.n8n.cloud/api/v1/workflows/safe-id"
                content = b""
                headers = {}
                text = '{"credential":"CREDLEAK456"}'

            with patch("n8n_safe_agent_cli.http.HttpClient.request", return_value=FakeSuccessResponse()):
                with redirect_stdout(io.StringIO()):
                    self.assertEqual(
                        main(
                            [
                                "--env-file",
                                str(env_path),
                                "--plan-out",
                                str(plan_path),
                                "api",
                                "workflow",
                                "update-workflow",
                                "--path-param",
                                "id=safe-id",
                                "--body-file",
                                str(body_path),
                            ]
                        ),
                        0,
                    )

            with patch("requests.Session.request", return_value=FakeCredentialErrorResponse()):
                out = io.StringIO()
                err = io.StringIO()
                with redirect_stdout(out), redirect_stderr(err):
                    rc = main(
                        [
                            "--env-file",
                            str(env_path),
                            "--run-id",
                            run_id,
                            "--log-file",
                            str(audit_path),
                            "--apply",
                            "--yes",
                            "--plan-in",
                            str(plan_path),
                            "--verbose",
                            "api",
                            "workflow",
                            "update-workflow",
                            "--path-param",
                            "id=safe-id",
                            "--body-file",
                            str(body_path),
                        ]
                    )

            self.assertEqual(rc, 1)
            run_dir = root / ".state" / "runs" / run_id
            surfaces = [
                out.getvalue(),
                err.getvalue(),
                audit_path.read_text(encoding="utf-8"),
                (run_dir / "audit.jsonl").read_text(encoding="utf-8"),
                (run_dir / "summary.md").read_text(encoding="utf-8"),
                (root / ".state" / "runs" / "index.jsonl").read_text(encoding="utf-8"),
            ]
            receipt_path = run_dir / "receipt.json"
            self.assertFalse(receipt_path.exists())
            for surface in surfaces:
                self._assert_no_raw_secrets(surface, secrets)
