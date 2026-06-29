from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

import requests

from make_com_safe_agent_cli.cli import main
from make_com_safe_agent_cli.config import credential_fingerprint
from make_com_safe_agent_cli.inventory import find_operation, load_inventory


class _FakeResponse:
    status = 200

    def __init__(self, url: str):
        self.url = url

    def json(self) -> dict[str, object]:
        return {"ok": True}

    def text(self) -> str:
        return '{"ok": true}'


class _FakeRequestsResponse:
    headers: dict[str, str] = {}

    def __init__(self, *, status_code: int, url: str, body: dict[str, object]):
        self.status_code = status_code
        self.url = url
        self.content = json.dumps(body).encode("utf-8")

    @property
    def text(self) -> str:
        return self.content.decode("utf-8")


class TestMakeApiInventoryAndSafety(unittest.TestCase):
    def test_official_inventory_has_expected_make_surface(self) -> None:
        inventory = load_inventory()
        self.assertEqual(len(inventory["operations"]), 376)
        self.assertEqual(len(inventory["pages"]), 59)
        self.assertEqual(inventory["failures"], [])
        self.assertIsNotNone(find_operation(inventory, "scenarios", "list-scenarios"))
        self.assertIsNotNone(find_operation(inventory, "users-me", "current-user-data"))

    def test_api_list_is_local_and_explicit(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["api", "list"])
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["operation_count"], 376)
        family_names = {family["family"] for family in payload["families"]}
        self.assertIn("scenarios", family_names)

    def test_write_plan_redacts_blueprint_and_requires_no_snapshot_ack(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("MAKE_BASE_URL=https://eu1.make.com\nMAKE_TIMEOUT_S=30\n", encoding="utf-8")
            body = '{"blueprint":"{\\"token\\":\\"super-secret\\"}","teamId":123,"scheduling":"{\\"type\\":\\"indefinitely\\"}"}'

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "api", "scenarios", "create-scenario", "--body-json", body])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["plan"]["request_body"]["blueprint"], "<REDACTED>")
            self.assertIsInstance(payload["plan"]["request_body_sha256"], str)
            self.assertIn("no-snapshot", payload["plan"]["risk_reasons"])

            plan_path = Path(payload["plan_out"])
            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--yes",
                        "--plan-in",
                        str(plan_path),
                        "api",
                        "scenarios",
                        "create-scenario",
                        "--body-json",
                        body,
                    ]
                )
            self.assertEqual(rc2, 0)
            refused = json.loads(buf2.getvalue())
            self.assertTrue(refused["refused"])
            self.assertIn("--ack-no-snapshot", refused["reasons"][0])

    def test_apply_refuses_when_body_differs_from_reviewed_plan(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("MAKE_BASE_URL=https://eu1.make.com\nMAKE_TIMEOUT_S=30\n", encoding="utf-8")
            body = '{"blueprint":"{\\"token\\":\\"reviewed\\"}","teamId":123,"scheduling":"{\\"type\\":\\"indefinitely\\"}"}'
            changed_body = '{"blueprint":"{\\"token\\":\\"changed\\"}","teamId":123,"scheduling":"{\\"type\\":\\"indefinitely\\"}"}'

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "api", "scenarios", "create-scenario", "--body-json", body])
            self.assertEqual(rc, 0)
            plan_path = Path(json.loads(buf.getvalue())["plan_out"])

            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--yes",
                        "--ack-no-snapshot",
                        "--plan-in",
                        str(plan_path),
                        "api",
                        "scenarios",
                        "create-scenario",
                        "--body-json",
                        changed_body,
                    ]
                )
            self.assertEqual(rc2, 0)
            refused = json.loads(buf2.getvalue())
            self.assertTrue(refused["refused"])
            self.assertIn("request body", refused["reasons"][0])

    def test_write_plan_redacts_api_key_fields(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("MAKE_BASE_URL=https://eu1.make.com\nMAKE_TIMEOUT_S=30\n", encoding="utf-8")
            body = json.dumps(
                {
                    "blueprint": "{}",
                    "teamId": 123,
                    "scheduling": "{}",
                    "api_key": "short",
                    "nested": {"client_secret": "also-short"},
                }
            )

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "api", "scenarios", "create-scenario", "--body-json", body])
            self.assertEqual(rc, 0)
            plan = json.loads(buf.getvalue())["plan"]
            self.assertEqual(plan["request_body"]["api_key"], "<REDACTED>")
            self.assertEqual(plan["request_body"]["nested"]["client_secret"], "<REDACTED>")

    def test_write_plan_sanitizes_raw_body_command_everywhere(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            env_path = root / ".env"
            env_path.write_text(
                "MAKE_BASE_URL=https://eu1.make.com\nMAKE_API_TOKEN=review-token\nMAKE_TIMEOUT_S=30\n",
                encoding="utf-8",
            )
            log_path = root / "global-audit.jsonl"
            run_id = "2026-06-29T120000Z_bodyred"
            secret = "LEAK_BODY_JSON_TOKEN"
            body = json.dumps(
                {
                    "blueprint": json.dumps({"token": secret}),
                    "teamId": 123,
                    "scheduling": json.dumps({"type": "indefinitely"}),
                }
            )

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--log-file",
                        str(log_path),
                        "--run-id",
                        run_id,
                        "api",
                        "scenarios",
                        "create-scenario",
                        "--body-json",
                        body,
                    ]
                )

            self.assertEqual(rc, 0)
            stdout = buf.getvalue()
            payload = json.loads(stdout)
            artifacts_dir = Path(payload["artifacts_dir"])
            plan = payload["plan"]

            self.assertEqual(plan["command"].split("--body-json", 1)[1].strip(), "<redacted-json>")
            self.assertEqual(plan["request_body"]["blueprint"], "<REDACTED>")
            self.assertEqual(plan["credential_fingerprint"], credential_fingerprint("review-token"))
            self.assertNotIn(secret, stdout)

            checked_paths = [
                artifacts_dir / "plan.json",
                artifacts_dir / "summary.md",
                artifacts_dir / "audit.jsonl",
                Path(payload["runs_index"]),
                log_path,
            ]
            for path in checked_paths:
                text = path.read_text(encoding="utf-8")
                self.assertNotIn(secret, text, str(path))
                self.assertNotIn(body, text, str(path))
                self.assertIn("<redacted-json>", text, str(path))

    def test_body_file_path_is_sanitized_in_command_records(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            env_path = root / ".env"
            env_path.write_text(
                "MAKE_BASE_URL=https://eu1.make.com\nMAKE_API_TOKEN=review-token\nMAKE_TIMEOUT_S=30\n",
                encoding="utf-8",
            )
            body_path = root / "secret-body-file.json"
            body_path.write_text(
                json.dumps(
                    {
                        "blueprint": "{}",
                        "teamId": 123,
                        "scheduling": json.dumps({"type": "indefinitely"}),
                    }
                ),
                encoding="utf-8",
            )

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--run-id",
                        "2026-06-29T120100Z_file",
                        "api",
                        "scenarios",
                        "create-scenario",
                        "--body-file",
                        str(body_path),
                    ]
                )

            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            artifacts_dir = Path(payload["artifacts_dir"])
            self.assertIn("--body-file <redacted-path>", payload["plan"]["command"])

            for path in [artifacts_dir / "plan.json", artifacts_dir / "summary.md", Path(payload["runs_index"])]:
                text = path.read_text(encoding="utf-8")
                self.assertNotIn(str(body_path), text, str(path))
                self.assertIn("<redacted-path>", text, str(path))

    def test_apply_refuses_when_credential_fingerprint_differs(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            env_path = root / ".env"
            env_path.write_text(
                "MAKE_BASE_URL=https://eu1.make.com\nMAKE_API_TOKEN=review-token\nMAKE_TIMEOUT_S=30\n",
                encoding="utf-8",
            )
            body = json.dumps(
                {
                    "blueprint": "{}",
                    "teamId": 123,
                    "scheduling": json.dumps({"type": "indefinitely"}),
                }
            )

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "api", "scenarios", "create-scenario", "--body-json", body])
            self.assertEqual(rc, 0)
            plan_path = Path(json.loads(buf.getvalue())["plan_out"])

            env_path.write_text(
                "MAKE_BASE_URL=https://eu1.make.com\nMAKE_API_TOKEN=apply-token\nMAKE_TIMEOUT_S=30\n",
                encoding="utf-8",
            )
            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--yes",
                        "--ack-no-snapshot",
                        "--plan-in",
                        str(plan_path),
                        "api",
                        "scenarios",
                        "create-scenario",
                        "--body-json",
                        body,
                    ]
                )

            self.assertEqual(rc2, 0)
            refused = json.loads(buf2.getvalue())
            self.assertTrue(refused["refused"])
            self.assertIn("credential fingerprint", refused["reasons"][0])

    def test_apply_receipt_does_not_leak_raw_body_command(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            env_path = root / ".env"
            env_path.write_text(
                "MAKE_BASE_URL=https://eu1.make.com\nMAKE_API_TOKEN=review-token\nMAKE_TIMEOUT_S=30\n",
                encoding="utf-8",
            )
            secret = "LEAK_RECEIPT_BODY_TOKEN"
            body = json.dumps(
                {
                    "blueprint": json.dumps({"token": secret}),
                    "teamId": 123,
                    "scheduling": json.dumps({"type": "indefinitely"}),
                }
            )

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "api", "scenarios", "create-scenario", "--body-json", body])
            self.assertEqual(rc, 0)
            plan_path = Path(json.loads(buf.getvalue())["plan_out"])

            log_path = root / "apply-audit.jsonl"
            receipt_path = root / "receipt.json"
            buf2 = io.StringIO()
            with patch(
                "make_com_safe_agent_cli.commands.api._request",
                return_value={"status": 200, "url": "https://eu1.make.com/api/v2/scenarios", "body": {"ok": True}},
            ):
                with redirect_stdout(buf2):
                    rc2 = main(
                        [
                            "--env-file",
                            str(env_path),
                            "--log-file",
                            str(log_path),
                            "--run-id",
                            "2026-06-29T120200Z_apply",
                            "--apply",
                            "--yes",
                            "--ack-no-snapshot",
                            "--plan-in",
                            str(plan_path),
                            "--receipt-out",
                            str(receipt_path),
                            "api",
                            "scenarios",
                            "create-scenario",
                            "--body-json",
                            body,
                        ]
                    )

            self.assertEqual(rc2, 0)
            payload = json.loads(buf2.getvalue())
            self.assertFalse(payload["dry_run"])
            artifacts_dir = Path(payload["artifacts_dir"])
            for text in [
                buf2.getvalue(),
                receipt_path.read_text(encoding="utf-8"),
                (artifacts_dir / "summary.md").read_text(encoding="utf-8"),
                (artifacts_dir / "audit.jsonl").read_text(encoding="utf-8"),
                Path(payload["runs_index"]).read_text(encoding="utf-8"),
                log_path.read_text(encoding="utf-8"),
            ]:
                self.assertNotIn(secret, text)
                self.assertNotIn(body, text)

    def test_secret_path_param_is_redacted_but_still_validated_exactly(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            env_path = root / ".env"
            env_path.write_text(
                "MAKE_BASE_URL=https://eu1.make.com\nMAKE_API_TOKEN=review-token\nMAKE_TIMEOUT_S=30\n",
                encoding="utf-8",
            )
            log_path = root / "path-audit.jsonl"
            secret = "SDK_INVITE_TOKEN_SHOULD_NOT_PRINT"
            path_pair = f"SDK_appInviteToken={secret}"

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--log-file",
                        str(log_path),
                        "--run-id",
                        "2026-06-29T130000Z_pathplan",
                        "api",
                        "sdk-apps-invites",
                        "accept-app-invite",
                        "--path-param",
                        path_pair,
                    ]
                )
            self.assertEqual(rc, 0)
            stdout = buf.getvalue()
            payload = json.loads(stdout)
            plan = payload["plan"]
            plan_path = Path(payload["plan_out"])
            artifacts_dir = Path(payload["artifacts_dir"])

            self.assertEqual(plan["target"]["path_params"]["SDK_appInviteToken"], "<REDACTED>")
            self.assertIsInstance(plan["target_fingerprints"]["path_params_sha256"], str)
            self.assertIn("SDK_appInviteToken=<redacted>", plan["command"])
            self.assertNotIn(secret, stdout)

            for path in [
                plan_path,
                artifacts_dir / "summary.md",
                artifacts_dir / "audit.jsonl",
                Path(payload["runs_index"]),
                log_path,
            ]:
                text = path.read_text(encoding="utf-8")
                self.assertNotIn(secret, text, str(path))
                self.assertIn("SDK_appInviteToken=<redacted>", text, str(path))

            apply_log_path = root / "path-apply-audit.jsonl"
            buf2 = io.StringIO()
            with patch(
                "make_com_safe_agent_cli.commands.api.HttpClient.request",
                return_value=_FakeResponse(f"https://eu1.make.com/api/v2/sdk/apps/invites/{secret}"),
            ):
                with redirect_stdout(buf2):
                    rc2 = main(
                        [
                            "--env-file",
                            str(env_path),
                            "--log-file",
                            str(apply_log_path),
                            "--run-id",
                            "2026-06-29T130100Z_pathapply",
                            "--apply",
                            "--yes",
                            "--ack-no-snapshot",
                            "--plan-in",
                            str(plan_path),
                            "api",
                            "sdk-apps-invites",
                            "accept-app-invite",
                            "--path-param",
                            path_pair,
                        ]
                    )
            self.assertEqual(rc2, 0)
            apply_payload = json.loads(buf2.getvalue())
            apply_artifacts_dir = Path(apply_payload["artifacts_dir"])
            for text in [
                buf2.getvalue(),
                Path(apply_payload["receipt_out"]).read_text(encoding="utf-8"),
                (apply_artifacts_dir / "summary.md").read_text(encoding="utf-8"),
                (apply_artifacts_dir / "audit.jsonl").read_text(encoding="utf-8"),
                Path(apply_payload["runs_index"]).read_text(encoding="utf-8"),
                apply_log_path.read_text(encoding="utf-8"),
            ]:
                self.assertNotIn(secret, text)
                self.assertTrue("<REDACTED>" in text or "<redacted>" in text)

            buf3 = io.StringIO()
            with redirect_stdout(buf3):
                rc3 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--yes",
                        "--ack-no-snapshot",
                        "--plan-in",
                        str(plan_path),
                        "api",
                        "sdk-apps-invites",
                        "accept-app-invite",
                        "--path-param",
                        "SDK_appInviteToken=SDK_INVITE_TOKEN_CHANGED_VALUE",
                    ]
                )
            self.assertEqual(rc3, 0)
            refused = json.loads(buf3.getvalue())
            self.assertTrue(refused["refused"])
            self.assertIn("path parameters", refused["reasons"][0])

    def test_secret_query_value_is_redacted_in_command_and_receipt_url(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            env_path = root / ".env"
            env_path.write_text(
                "MAKE_BASE_URL=https://eu1.make.com\nMAKE_API_TOKEN=review-token\nMAKE_TIMEOUT_S=30\n",
                encoding="utf-8",
            )
            log_path = root / "query-audit.jsonl"
            secret = "query-secret-token-value"
            body = json.dumps(
                {
                    "blueprint": "{}",
                    "teamId": 123,
                    "scheduling": json.dumps({"type": "indefinitely"}),
                }
            )

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--log-file",
                        str(log_path),
                        "--run-id",
                        "2026-06-29T130200Z_queryplan",
                        "api",
                        "scenarios",
                        "create-scenario",
                        "--query",
                        f"token={secret}",
                        "--body-json",
                        body,
                    ]
                )
            self.assertEqual(rc, 0)
            stdout = buf.getvalue()
            payload = json.loads(stdout)
            plan = payload["plan"]
            plan_path = Path(payload["plan_out"])
            artifacts_dir = Path(payload["artifacts_dir"])

            self.assertEqual(plan["target"]["query"]["token"], "<REDACTED>")
            self.assertIsInstance(plan["target_fingerprints"]["query_sha256"], str)
            self.assertIn("token=<redacted>", plan["command"])
            self.assertNotIn(secret, stdout)

            for path in [
                plan_path,
                artifacts_dir / "summary.md",
                artifacts_dir / "audit.jsonl",
                Path(payload["runs_index"]),
                log_path,
            ]:
                text = path.read_text(encoding="utf-8")
                self.assertNotIn(secret, text, str(path))
                self.assertIn("token=<redacted>", text, str(path))

            apply_log_path = root / "query-apply-audit.jsonl"
            buf2 = io.StringIO()
            with patch(
                "make_com_safe_agent_cli.commands.api.HttpClient.request",
                return_value=_FakeResponse(f"https://eu1.make.com/api/v2/scenarios?token={secret}"),
            ):
                with redirect_stdout(buf2):
                    rc2 = main(
                        [
                            "--env-file",
                            str(env_path),
                            "--log-file",
                            str(apply_log_path),
                            "--run-id",
                            "2026-06-29T130300Z_queryapply",
                            "--apply",
                            "--yes",
                            "--ack-no-snapshot",
                            "--plan-in",
                            str(plan_path),
                            "api",
                            "scenarios",
                            "create-scenario",
                            "--query",
                            f"token={secret}",
                            "--body-json",
                            body,
                        ]
                    )
            self.assertEqual(rc2, 0)
            apply_payload = json.loads(buf2.getvalue())
            apply_artifacts_dir = Path(apply_payload["artifacts_dir"])
            for text in [
                buf2.getvalue(),
                Path(apply_payload["receipt_out"]).read_text(encoding="utf-8"),
                (apply_artifacts_dir / "summary.md").read_text(encoding="utf-8"),
                (apply_artifacts_dir / "audit.jsonl").read_text(encoding="utf-8"),
                Path(apply_payload["runs_index"]).read_text(encoding="utf-8"),
                apply_log_path.read_text(encoding="utf-8"),
            ]:
                self.assertNotIn(secret, text)
                self.assertTrue("<REDACTED>" in text or "<redacted>" in text)

    def test_verbose_read_redacts_http_url_and_provider_body(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            env_path = root / ".env"
            env_path.write_text(
                "MAKE_BASE_URL=https://eu1.make.com\nMAKE_API_TOKEN=review-token\nMAKE_TIMEOUT_S=30\n",
                encoding="utf-8",
            )
            log_path = root / "verbose-read-audit.jsonl"
            path_secret = "SDK_INVITE_TOKEN_VERBOSE_SHOULD_NOT_PRINT"
            query_secret = "query-secret-token-verbose"
            body_secret = "provider-client-secret-value"

            stdout = io.StringIO()
            stderr = io.StringIO()
            with patch(
                "requests.Session.request",
                return_value=_FakeRequestsResponse(
                    status_code=200,
                    url=f"https://eu1.make.com/api/v2/sdk/apps/invites/{path_secret}?token={query_secret}",
                    body={"client_secret": body_secret, "ok": True},
                ),
            ):
                with redirect_stdout(stdout), redirect_stderr(stderr):
                    rc = main(
                        [
                            "--env-file",
                            str(env_path),
                            "--log-file",
                            str(log_path),
                            "--verbose",
                            "api",
                            "sdk-apps-invites",
                            "get-app-invite",
                            "--path-param",
                            f"SDK_appInviteToken={path_secret}",
                            "--query",
                            f"token={query_secret}",
                        ]
                    )

            self.assertEqual(rc, 0)
            for text in [stdout.getvalue(), stderr.getvalue(), log_path.read_text(encoding="utf-8")]:
                self.assertNotIn(path_secret, text)
                self.assertNotIn(query_secret, text)
                self.assertNotIn(body_secret, text)
            payload = json.loads(stdout.getvalue())
            self.assertEqual(payload["response"]["body"]["client_secret"], "<REDACTED>")

    def test_http_error_redacts_url_and_provider_body_in_outputs_and_run_records(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            env_path = root / ".env"
            env_path.write_text(
                "MAKE_BASE_URL=https://eu1.make.com\nMAKE_API_TOKEN=review-token\nMAKE_TIMEOUT_S=30\n",
                encoding="utf-8",
            )
            path_secret = "SDK_INVITE_TOKEN_HTTP_ERROR_SHOULD_NOT_PRINT"
            query_secret = "query-secret-token-http-error"
            body_secret = "provider-refresh-token-value"
            api_key_secret = "provider-api-key-value"
            path_pair = f"SDK_appInviteToken={path_secret}"

            plan_stdout = io.StringIO()
            with redirect_stdout(plan_stdout):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--run-id",
                        "2026-06-29T140000Z_httpplan",
                        "api",
                        "sdk-apps-invites",
                        "accept-app-invite",
                        "--path-param",
                        path_pair,
                        "--query",
                        f"token={query_secret}",
                    ]
                )
            self.assertEqual(rc, 0)
            plan_payload = json.loads(plan_stdout.getvalue())
            plan_path = Path(plan_payload["plan_out"])

            log_path = root / "http-error-audit.jsonl"
            stdout = io.StringIO()
            stderr = io.StringIO()
            with patch(
                "requests.Session.request",
                return_value=_FakeRequestsResponse(
                    status_code=400,
                    url=f"https://eu1.make.com/api/v2/sdk/apps/invites/{path_secret}?token={query_secret}",
                    body={
                        "error": "bad request",
                        "refresh_token": body_secret,
                        "nested": {"api_key": api_key_secret},
                    },
                ),
            ):
                with redirect_stdout(stdout), redirect_stderr(stderr):
                    rc2 = main(
                        [
                            "--env-file",
                            str(env_path),
                            "--log-file",
                            str(log_path),
                            "--run-id",
                            "2026-06-29T140100Z_httperror",
                            "--verbose",
                            "--apply",
                            "--yes",
                            "--ack-no-snapshot",
                            "--plan-in",
                            str(plan_path),
                            "api",
                            "sdk-apps-invites",
                            "accept-app-invite",
                            "--path-param",
                            path_pair,
                            "--query",
                            f"token={query_secret}",
                        ]
                    )

            self.assertEqual(rc2, 1)
            payload = json.loads(stdout.getvalue())
            artifacts_dir = Path(payload["artifacts_dir"])
            checked_texts = [
                stdout.getvalue(),
                stderr.getvalue(),
                plan_path.read_text(encoding="utf-8"),
                (artifacts_dir / "summary.md").read_text(encoding="utf-8"),
                (artifacts_dir / "audit.jsonl").read_text(encoding="utf-8"),
                Path(payload["runs_index"]).read_text(encoding="utf-8"),
                log_path.read_text(encoding="utf-8"),
            ]
            for text in checked_texts:
                self.assertNotIn(path_secret, text)
                self.assertNotIn(query_secret, text)
                self.assertNotIn(body_secret, text)
                self.assertNotIn(api_key_secret, text)
            self.assertIn("<REDACTED>", stdout.getvalue())

    def test_request_exception_redacts_url_before_stdout_stderr_and_audit(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            env_path = root / ".env"
            env_path.write_text(
                "MAKE_BASE_URL=https://eu1.make.com\nMAKE_API_TOKEN=review-token\nMAKE_TIMEOUT_S=30\n",
                encoding="utf-8",
            )
            log_path = root / "exception-audit.jsonl"
            path_secret = "SDK_INVITE_TOKEN_EXCEPTION_SHOULD_NOT_PRINT"
            query_secret = "query-secret-token-exception"
            body_secret = "provider-client-secret-exception"
            raw_url = f"https://eu1.make.com/api/v2/sdk/apps/invites/{path_secret}?token={query_secret}"

            stdout = io.StringIO()
            stderr = io.StringIO()
            with patch(
                "requests.Session.request",
                side_effect=requests.RequestException(f"failed for {raw_url} client_secret={body_secret}"),
            ):
                with redirect_stdout(stdout), redirect_stderr(stderr):
                    rc = main(
                        [
                            "--env-file",
                            str(env_path),
                            "--log-file",
                            str(log_path),
                            "--verbose",
                            "api",
                            "sdk-apps-invites",
                            "get-app-invite",
                            "--path-param",
                            f"SDK_appInviteToken={path_secret}",
                            "--query",
                            f"token={query_secret}",
                        ]
                    )

            self.assertEqual(rc, 1)
            for text in [stdout.getvalue(), stderr.getvalue(), log_path.read_text(encoding="utf-8")]:
                self.assertNotIn(path_secret, text)
                self.assertNotIn(query_secret, text)
                self.assertNotIn(body_secret, text)
                self.assertIn("<REDACTED>", text)
