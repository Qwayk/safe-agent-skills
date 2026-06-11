from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from tiktok_marketing_safe_agent_cli.cli import main


class _NoNetworkHttpClient:
    def __init__(self, *args, **kwargs):
        pass

    def request(self, *args, **kwargs):  # noqa: ARG002
        raise AssertionError("HTTP request was not expected")


class _CaptureHttpClient:
    calls: list[dict] = []

    def __init__(self, *args, **kwargs):
        pass

    def request(self, **kwargs):
        _CaptureHttpClient.calls.append(kwargs)

        class _Response:
            status = 200
            headers = {"content-type": "application/json"}
            url = str(kwargs.get("url") or "")
            body = b'{"ok": true}'

            @staticmethod
            def json() -> dict:
                return {"ok": True}

        return _Response()


class TestApiRuntime(unittest.TestCase):
    def _run_main(self, argv: list[str]) -> tuple[int, dict[str, object]]:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(argv)
        payload = json.loads(buf.getvalue() or "{}")
        return rc, payload

    def _write_env(self, dir_path: Path, *, include_token: bool = True) -> Path:
        env_path = dir_path / ".env"
        lines = [
            "TIKTOK_MARKETING_API_BASE_URL=http://example.invalid",
            "TIKTOK_MARKETING_APP_ID=app-123",
            "TIKTOK_MARKETING_APP_SECRET=secret-123",
            "TIKTOK_MARKETING_TIMEOUT_S=30",
        ]
        if include_token:
            lines.append("TIKTOK_MARKETING_ACCESS_TOKEN=token-abc")
        env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return env_path

    def test_api_ops_list_and_show(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env = self._write_env(Path(d))

            rc, payload = self._run_main(["--env-file", str(env), "--output", "json", "api", "ops", "list"])
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(len(payload["ops"]), 240)
            self.assertEqual(payload["count"], 240)
            self.assertIn("oauth2-advertiser-get", {op["operation_command"] for op in payload["ops"]})

            rc2, payload2 = self._run_main(
                ["--env-file", str(env), "--output", "json", "api", "ops", "show", "--op", "oauth2-advertiser-get"]
            )
            self.assertEqual(rc2, 0)
            self.assertTrue(payload2["ok"])
            op = payload2["operation"]
            self.assertEqual(op["operation_command"], "oauth2-advertiser-get")
            self.assertEqual(op["method"], "GET")

    def test_legacy_client_env_names_do_not_work(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env = Path(d) / ".env"
            lines = [
                "TIKTOK_MARKETING_API_BASE_URL=http://example.invalid",
                "TIKTOK_MARKETING_ACCESS_TOKEN=token-abc",
                "TIKTOK_MARKETING_CLIENT_ID=legacy-id",
                "TIKTOK_MARKETING_CLIENT_SECRET=legacy-secret",
            ]
            env.write_text("\n".join(lines) + "\n", encoding="utf-8")

            with patch("tiktok_marketing_safe_agent_cli.commands.auth.HttpClient", _NoNetworkHttpClient):
                rc, payload = self._run_main(
                    [
                        "--env-file",
                        str(env),
                        "--output",
                        "json",
                        "auth",
                        "check",
                    ]
                )

            self.assertEqual(rc, 1)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "ValidationError")
            self.assertIn("Missing TIKTOK_MARKETING_APP_ID or TIKTOK_MARKETING_APP_SECRET", str(payload["error"]))

    def test_api_get_is_plan_only_without_live(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env = self._write_env(Path(d))
            query_json = Path(d) / "query.json"
            query_json.write_text('{"advertiser_id": "123"}', encoding="utf-8")

            with patch("tiktok_marketing_safe_agent_cli.commands.api.HttpClient", _NoNetworkHttpClient):
                rc, payload = self._run_main(
                    [
                        "--env-file",
                        str(env),
                        "--output",
                        "json",
                        "api",
                        "ad-get",
                        "--query-json",
                        str(query_json),
                    ]
                )

            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertNotIn("response", payload)

    def test_api_post_without_required_flags_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env = self._write_env(Path(d))

            with patch("tiktok_marketing_safe_agent_cli.commands.api.HttpClient", _NoNetworkHttpClient):
                rc, payload = self._run_main(
                    [
                        "--env-file",
                        str(env),
                        "--output",
                        "json",
                        "--apply",
                        "api",
                        "ad-aco-create",
                    ]
                )

            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["dry_run"], True)
            self.assertIn("--live is required", " ".join(payload["reasons"]))

    def test_api_write_apply_requires_ack_irreversible(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env = self._write_env(root, include_token=False)
            body_path = root / "body.json"
            body_path.write_text(
                '{"app_id": "app-123", "secret": "secret-123", "auth_code": "one-time-code"}',
                encoding="utf-8",
            )
            plan_out = root / "plan.json"

            rc_plan, payload_plan = self._run_main(
                [
                    "--env-file",
                    str(env),
                    "--output",
                    "json",
                    "--plan-out",
                    str(plan_out),
                    "api",
                    "oauth2-access-token",
                    "--body-json",
                    str(body_path),
                ]
            )
            self.assertEqual(rc_plan, 0)
            self.assertTrue(payload_plan["ok"])
            self.assertEqual(payload_plan["plan"]["rollback"]["mode"], "irreversible_and_clearly_labeled")
            self.assertEqual(payload_plan["plan"]["before_state"]["status"], "no_snapshot_available")
            self.assertEqual(payload_plan["plan"]["verification_plan"]["status"], "best_effort_after_apply")
            self.assertTrue(payload_plan["plan"]["rollback"]["requires_ack_irreversible"])

            with patch("tiktok_marketing_safe_agent_cli.commands.api.HttpClient", _NoNetworkHttpClient):
                rc_apply, payload_apply = self._run_main(
                    [
                        "--env-file",
                        str(env),
                        "--output",
                        "json",
                        "--live",
                        "--apply",
                        "--yes",
                        "--plan-in",
                        str(plan_out),
                        "api",
                        "oauth2-access-token",
                    ]
                )

            self.assertEqual(rc_apply, 0)
            self.assertTrue(payload_apply["ok"])
            self.assertTrue(payload_apply["refused"])
            self.assertIn("--ack-irreversible", " ".join(payload_apply["reasons"]))

    def test_api_query_json_body_json_and_multipart_upload_execute(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env = self._write_env(root)

            body_path = root / "body.json"
            body_path.write_text('{"name": "campaign-name"}', encoding="utf-8")
            query_path = root / "query.json"
            query_path.write_text('{"advertiser_id": "123"}', encoding="utf-8")

            rc, payload = self._run_main(
                [
                    "--env-file",
                    str(env),
                    "--output",
                    "json",
                    "api",
                    "ad-aco-create",
                    "--body-json",
                    str(body_path),
                    "--query-json",
                    str(query_path),
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["plan"]["inputs"]["body"], {"name": "campaign-name"})
            self.assertEqual(payload["plan"]["inputs"]["query"]["advertiser_id"], "123")

            upload = root / "logo.txt"
            upload.write_text("binary", encoding="utf-8")
            upload_body = root / "upload_body.json"
            upload_body.write_text('{"meta": "tiktok-marketing-body"}', encoding="utf-8")
            plan_out = root / "plan.json"
            receipt_out = root / "receipt.json"

            _CaptureHttpClient.calls = []
            rc_plan, payload_plan = self._run_main(
                [
                    "--env-file",
                    str(env),
                    "--output",
                    "json",
                    "--plan-out",
                    str(plan_out),
                    "api",
                    "bc-image-upload",
                    "--file",
                    f"image_file={upload}",
                    "--body-json",
                    str(upload_body),
                ]
            )
            self.assertEqual(rc_plan, 0)
            self.assertTrue(payload_plan["ok"])
            self.assertTrue(payload_plan["dry_run"])
            self.assertEqual(payload_plan["plan"]["inputs"]["files"]["image_file"], str(upload))
            self.assertEqual(payload_plan["plan"]["before_state"]["status"], "no_snapshot_available")
            self.assertEqual(payload_plan["plan"]["verification_plan"]["status"], "best_effort_after_apply")
            self.assertEqual(payload_plan["plan"]["rollback"]["mode"], "irreversible_and_clearly_labeled")
            self.assertTrue(payload_plan["plan"]["rollback"]["requires_ack_irreversible"])

            with patch("tiktok_marketing_safe_agent_cli.commands.api.HttpClient", _CaptureHttpClient):
                rc_apply, payload_apply = self._run_main(
                    [
                        "--env-file",
                        str(env),
                        "--output",
                        "json",
                        "--live",
                        "--apply",
                        "--yes",
                        "--plan-in",
                        str(plan_out),
                        "--ack-irreversible",
                        "--receipt-out",
                        str(receipt_out),
                        "api",
                        "bc-image-upload",
                    ]
                )

            self.assertEqual(rc_apply, 0)
            self.assertTrue(payload_apply["ok"])
            self.assertFalse(payload_apply["dry_run"])
            self.assertTrue(payload_apply["refused"])
            self.assertFalse(receipt_out.exists())
            self.assertEqual(payload_apply["plan"]["inputs"]["body"]["meta"], "tiktok-marketing-body")
            self.assertEqual(payload_apply["plan"]["inputs"]["files"]["image_file"], str(upload))
            self.assertEqual(payload_apply["plan"]["before_state"]["status"], "no_snapshot_available")
            self.assertEqual(payload_apply["verification_plan"]["status"], "best_effort_after_apply")
            self.assertEqual(payload_apply["rollback"]["mode"], "irreversible_and_clearly_labeled")
            self.assertFalse(_CaptureHttpClient.calls)

    def test_auth_check_uses_token_file_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env = self._write_env(root, include_token=False)
            token_dir = root / ".state"
            token_dir.mkdir(parents=True, exist_ok=True)
            (token_dir / "token.json").write_text('{"access_token": "stored-token"}\n', encoding="utf-8")

            _CaptureHttpClient.calls = []
            with patch("tiktok_marketing_safe_agent_cli.commands.auth.HttpClient", _CaptureHttpClient):
                rc, payload = self._run_main(["--env-file", str(env), "--output", "json", "auth", "check"])

            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["live_checked"])
            self.assertEqual(payload["token_source"], "token_file")
            self.assertTrue(_CaptureHttpClient.calls)
            self.assertEqual(_CaptureHttpClient.calls[0]["headers"]["Access-Token"], "stored-token")
            self.assertEqual(_CaptureHttpClient.calls[0]["params"]["app_id"], "app-123")
            self.assertEqual(_CaptureHttpClient.calls[0]["params"]["secret"], "secret-123")

    def test_auth_check_failure_does_not_leak_secret(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env = self._write_env(root)
            env.write_text(
                "\n".join(
                    [
                        "TIKTOK_MARKETING_API_BASE_URL=http://example.invalid",
                        "TIKTOK_MARKETING_APP_ID=app-for-auth-failure",
                        "TIKTOK_MARKETING_APP_SECRET=secret-for-auth-failure",
                        "TIKTOK_MARKETING_ACCESS_TOKEN=token-for-auth-failure",
                        "TIKTOK_MARKETING_TIMEOUT_S=30",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            def _failure_request(*_args, **_kwargs):
                class _Response:
                    status_code = 401
                    headers = {"content-type": "application/json"}
                    url = (
                        "https://business-api.tiktok.com/open_api/v1.3/oauth2/advertiser/get/"
                        "?app_id=app-for-auth-failure"
                        "&secret=secret-for-auth-failure"
                        "&advertiser_id=advertiser-id"
                    )
                    body = b'{"error":"invalid_secret","secret":"secret-for-auth-failure"}'
                    text = body.decode("utf-8")

                    @staticmethod
                    def json() -> dict[str, object]:
                        return {"code": "1", "message": "auth failure"}

                return _Response()

            with patch("tiktok_marketing_safe_agent_cli.http.requests.Session.request", _failure_request):
                rc, payload = self._run_main(
                    ["--env-file", str(env), "--output", "json", "auth", "check"]
                )

            self.assertEqual(rc, 1)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "RuntimeError")
            self.assertNotIn("secret-for-auth-failure", str(payload["error"]))
            self.assertIn("***REDACTED***", str(payload["error"]))

    def test_oauth2_access_token_apply_does_not_require_existing_access_token(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env = self._write_env(root, include_token=False)
            body_path = root / "body.json"
            body_path.write_text(
                '{"app_id": "app-123", "secret": "secret-123", "auth_code": "one-time-code"}',
                encoding="utf-8",
            )
            plan_out = root / "plan.json"
            receipt_out = root / "receipt.json"

            rc_plan, payload_plan = self._run_main(
                [
                    "--env-file",
                    str(env),
                    "--output",
                    "json",
                    "--plan-out",
                    str(plan_out),
                    "api",
                    "oauth2-access-token",
                    "--body-json",
                    str(body_path),
                ]
            )
            self.assertEqual(rc_plan, 0)
            self.assertTrue(payload_plan["ok"])
            self.assertTrue(payload_plan["dry_run"])
            self.assertEqual(payload_plan["plan"]["rollback"]["mode"], "irreversible_and_clearly_labeled")
            self.assertEqual(payload_plan["plan"]["before_state"]["status"], "no_snapshot_available")

            _CaptureHttpClient.calls = []
            with patch("tiktok_marketing_safe_agent_cli.commands.api.HttpClient", _CaptureHttpClient):
                rc_apply, payload_apply = self._run_main(
                    [
                        "--env-file",
                        str(env),
                        "--output",
                        "json",
                        "--live",
                        "--apply",
                        "--yes",
                        "--plan-in",
                        str(plan_out),
                        "--ack-irreversible",
                        "--receipt-out",
                        str(receipt_out),
                        "api",
                        "oauth2-access-token",
                    ]
                )

            self.assertEqual(rc_apply, 0)
            self.assertTrue(payload_apply["ok"])
            self.assertFalse(payload_apply["dry_run"])
            self.assertTrue(payload_apply["refused"])
            self.assertEqual(payload_apply["plan"]["before_state"]["status"], "no_snapshot_available")
            self.assertEqual(payload_apply["verification_plan"]["status"], "best_effort_after_apply")
            self.assertFalse(receipt_out.exists())
            self.assertFalse(_CaptureHttpClient.calls)
