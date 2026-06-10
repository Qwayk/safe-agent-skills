from __future__ import annotations

import io
import json
import tempfile
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest import TestCase
from unittest.mock import patch

from klaviyo_safe_agent_cli.cli import main


class _CaptureHttpClient:
    calls: list[dict[str, Any]]
    calls = []

    def __init__(self, *, timeout_s: float, verbose: bool, user_agent: str) -> None:  # noqa: ARG002
        pass

    def request(
        self,
        *,
        method: str,
        url: str,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        files: dict[str, Any] | None = None,
        retries: int = 0,
        retry_on: tuple[int, ...] = (429, 500, 502, 503, 504),  # noqa: ARG002
    ) -> SimpleNamespace:
        self.__class__.calls.append(
            {
                "method": method,
                "url": url,
                "headers": headers or {},
                "params": params or {},
                "json_body": json_body,
                "data": data,
                "files": files or {},
            }
        )
        return SimpleNamespace(
            status=201,
            headers={"content-type": "application/json"},
            body=b'{"ok":true}',
            url=url,
        )


class _FailingAuthHttpClient:
    def __init__(self, *, timeout_s: float, verbose: bool, user_agent: str) -> None:  # noqa: ARG002
        pass

    def request(
        self,
        *,
        method: str,
        url: str,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        files: dict[str, Any] | None = None,
        retries: int = 0,
        retry_on: tuple[int, ...] = (429, 500, 502, 503, 504),  # noqa: ARG002
    ) -> None:
        _ = method, url, headers, params, json_body, data, files, retries, retry_on
        raise RuntimeError("HTTP 401 Unauthorized for key=super-secret-klaviyo-key")


class TestApiRuntime(TestCase):

    def _env_file(self, root: Path, with_key: bool = True) -> Path:
        env_path = root / ".env"
        lines = [
            "KLAVIYO_API_BASE_URL=http://example.invalid",
            "KLAVIYO_TIMEOUT_S=30",
        ]
        if with_key:
            lines.append("KLAVIYO_API_KEY=super-secret-klaviyo-key")
        env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return env_path

    def _run_main(self, args: list[str]) -> tuple[int, dict[str, Any]]:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(args)
        payload = json.loads(buf.getvalue())
        return rc, payload

    def test_api_ops_list_and_show(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            env = self._env_file(Path(temp_dir), with_key=False)

            rc, payload = self._run_main(["--env-file", str(env), "--output", "json", "api", "ops", "list", "--method", "GET"])
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertGreater(payload["count"], 0)
            self.assertTrue(any(item["method"] == "GET" for item in payload["ops"]))

            rc2, show_payload = self._run_main(["--env-file", str(env), "--output", "json", "api", "ops", "show", "--op", "get_accounts"])
            self.assertEqual(rc2, 0)
            self.assertTrue(show_payload["ok"])
            self.assertEqual(show_payload["operation"]["operation_command"], "get_accounts")

    def test_api_read_operation_is_plan_only_without_live(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            env = self._env_file(Path(temp_dir), with_key=False)

            rc, payload = self._run_main(["--env-file", str(env), "--output", "json", "api", "get_accounts"])
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertFalse(payload.get("refused", False))
            self.assertEqual(payload["plan"]["operation"]["operation_command"], "get_accounts")
            self.assertFalse(payload["plan"]["before_state"]["required"])

    def test_api_query_json_list_values_are_joined_for_query_params(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            env = self._env_file(root, with_key=False)
            query_path = root / "query.json"
            query_path.write_text('{"fields[account]": ["id", "public_api_key"]}', encoding="utf-8")

            rc, payload = self._run_main(
                ["--env-file", str(env), "--output", "json", "api", "get_accounts", "--query-json", str(query_path)]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["plan"]["inputs"]["query"]["fields[account]"], "id,public_api_key")

    def test_api_apply_requires_live(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            env = self._env_file(Path(temp_dir), with_key=False)

            rc, payload = self._run_main(
                ["--env-file", str(env), "--output", "json", "--apply", "api", "delete_campaign", "--path", "id=cmp-1"]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertTrue(payload["dry_run"])
            self.assertTrue(any("--live is required" in reason for reason in payload["reasons"]))

    def test_high_impact_delete_requires_yes_and_plan_in(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            env = self._env_file(root, with_key=False)
            plan_path = root / "plan.json"

            rc_plan, plan_payload = self._run_main(
                [
                    "--env-file",
                    str(env),
                    "--output",
                    "json",
                    "--plan-out",
                    str(plan_path),
                    "api",
                    "delete_campaign",
                    "--path",
                    "id=cmp-1",
                ]
            )
            self.assertEqual(rc_plan, 0)
            self.assertTrue(plan_path.exists())
            self.assertTrue(plan_payload["plan"]["before_state"]["required"])
            self.assertFalse(plan_payload["plan"]["before_state"]["supported"])
            self.assertFalse(plan_payload["plan"]["no_recovery"]["automatic_rollback_available"])
            self.assertFalse(plan_payload["plan"]["no_recovery"]["snapshots_created"])
            self.assertEqual(plan_payload["plan"]["no_recovery"]["provider_backups"], [])
            self.assertIn("No automatic rollback is available", plan_payload["plan"]["no_recovery"]["note"])

            rc, payload = self._run_main(
                [
                    "--env-file",
                    str(env),
                    "--output",
                    "json",
                    "--live",
                    "--apply",
                    "--plan-in",
                    str(plan_path),
                    "api",
                    "delete_campaign",
                    "--path",
                    "id=cmp-1",
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertTrue(any("--yes" in reason for reason in payload["reasons"]))

    def test_upload_image_from_file_apply_refuses_before_http(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            env = self._env_file(root)

            body_path = root / "body.json"
            body_path.write_text('{"meta": "test"}', encoding="utf-8")
            image_path = root / "logo.bin"
            image_path.write_text("binary", encoding="utf-8")
            plan_path = root / "plan.json"
            receipt_path = root / "receipt.json"

            rc_plan, plan_payload = self._run_main(
                [
                    "--env-file",
                    str(env),
                    "--output",
                    "json",
                    "--plan-out",
                    str(plan_path),
                    "api",
                    "upload_image_from_file",
                    "--file",
                    f"file={image_path}",
                    "--body-json",
                    str(body_path),
                ]
            )
            self.assertEqual(rc_plan, 0)
            self.assertTrue(plan_payload["ok"])
            self.assertEqual(plan_payload["plan"]["inputs"]["files"].get("file"), str(image_path))
            self.assertTrue(plan_payload["plan"]["before_state"]["required"])
            self.assertFalse(plan_payload["plan"]["before_state"]["supported"])

            _CaptureHttpClient.calls = []
            with patch("klaviyo_safe_agent_cli.commands.api.HttpClient", _CaptureHttpClient):
                rc_apply, apply_payload = self._run_main(
                    [
                        "--env-file",
                        str(env),
                        "--output",
                        "json",
                        "--live",
                        "--apply",
                        "--plan-in",
                        str(plan_path),
                        "--receipt-out",
                        str(receipt_path),
                        "api",
                        "upload_image_from_file",
                        "--file",
                        f"file={image_path}",
                        "--body-json",
                        str(body_path),
                    ]
                )

            self.assertEqual(rc_apply, 0)
            self.assertTrue(apply_payload["refused"])
            self.assertFalse(_CaptureHttpClient.calls)
            self.assertFalse(receipt_path.exists())
            self.assertNotIn("receipt", apply_payload)
            joined = " ".join(apply_payload["reasons"])
            self.assertIn("before-state snapshot", joined)
            self.assertIn("ack-no-snapshot", joined)

    def test_client_operation_can_run_live_with_company_id_only(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            env_path = root / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "KLAVIYO_API_BASE_URL=http://example.invalid",
                        "KLAVIYO_COMPANY_ID=PUBLIC123",
                        "KLAVIYO_TIMEOUT_S=30",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            _CaptureHttpClient.calls = []
            with patch("klaviyo_safe_agent_cli.commands.api.HttpClient", _CaptureHttpClient):
                rc, payload = self._run_main(
                    [
                        "--env-file",
                        str(env_path),
                        "--output",
                        "json",
                        "--live",
                        "api",
                        "get_client_geofences",
                    ]
                )

            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertFalse(payload["dry_run"])
            self.assertTrue(_CaptureHttpClient.calls)
            self.assertEqual(_CaptureHttpClient.calls[0]["params"].get("company_id"), "PUBLIC123")
            self.assertNotIn("authorization", {k.lower() for k in _CaptureHttpClient.calls[0]["headers"].keys()})

    def test_auth_check_failure_does_not_leak_api_key(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            env = self._env_file(Path(temp_dir), with_key=True)

            with patch("klaviyo_safe_agent_cli.commands.auth.HttpClient", _FailingAuthHttpClient):
                rc, payload = self._run_main([
                    "--env-file",
                    str(env),
                    "--output",
                    "json",
                    "--live",
                    "auth",
                    "check",
                ])

            self.assertEqual(rc, 0)
            text = json.dumps(payload)
            self.assertFalse("super-secret-klaviyo-key" in text)
            self.assertFalse(payload["ok"])
            self.assertFalse(payload["live_ok"])
            self.assertEqual(payload["error_type"], "HttpError")
