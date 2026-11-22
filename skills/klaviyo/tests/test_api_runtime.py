from __future__ import annotations

import io
import json
import shlex
import tempfile
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest import TestCase
from unittest.mock import patch

from klaviyo_safe_agent_cli.cli import main
from klaviyo_safe_agent_cli.http import HttpResponse


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

            self.assertEqual(rc, 1)
            text = json.dumps(payload)
            self.assertFalse("super-secret-klaviyo-key" in text)
            self.assertFalse(payload["ok"])
            self.assertFalse(payload["live_ok"])
            self.assertEqual(payload["error_type"], "HttpError")

    def test_account_check_needs_a_returned_account(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env = self._env_file(Path(directory))
            args = ["--env-file", str(env), "--live", "auth", "check"]
            for data, expected_exit in [
                ([], 1),
                ([{"type": "account", "id": "account-test", "attributes": {"public_api_key": "PUBLIC123"}}], 0),
            ]:
                response = HttpResponse(200, {}, json.dumps({"data": data}).encode(), "https://a.klaviyo.com/api/accounts")
                with patch("klaviyo_safe_agent_cli.commands.auth.HttpClient.request", return_value=response):
                    rc, result = self._run_main(args)
                self.assertEqual(rc, expected_exit)
                self.assertEqual(result["live_ok"], expected_exit == 0)

    def test_flow_status_change_requires_review_and_confirmation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env = self._env_file(Path(directory))
            args = ["--env-file", str(env), "--no-artifacts"]
            plan = Path(directory) / "flow-plan.json"
            change = ["api", "update_flow", "--path", "id=flow-test", "--body-json",
                      '{"data":{"type":"flow","id":"flow-test","attributes":{"status":"live"}}}']
            with patch("klaviyo_safe_agent_cli.commands.api.HttpClient.request") as request:
                _, refused = self._run_main(args + ["--live", "--apply", "--ack-no-snapshot"] + change)
                self.assertTrue(refused["refused"])
                self.assertTrue(any("--plan-in" in reason for reason in refused["reasons"]))
                self.assertTrue(any("--yes" in reason for reason in refused["reasons"]))
                self._run_main(args + ["--plan-out", str(plan)] + change)
                request.assert_not_called()
                request.return_value = HttpResponse(200, {}, b"", "https://a.klaviyo.com/api/flows/flow-test")
                _, result = self._run_main(args + [
                    "--live", "--apply", "--yes", "--ack-no-snapshot", "--plan-in", str(plan),
                ] + change)
                self.assertTrue(result["ok"])
                request.assert_called_once()

    def test_reviewed_upload_uses_the_same_file_contents(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            env = self._env_file(root)
            upload = root / "image.png"
            upload.write_bytes(b"image approved for the preview")
            plan = root / "image-plan.json"
            args = ["--env-file", str(env), "--no-artifacts"]
            operation = ["api", "upload_image_from_file", "--file", f"file={upload}", "--body-json", "{}"]
            self._run_main(args + ["--plan-out", str(plan)] + operation)
            apply = args + ["--live", "--apply", "--ack-no-snapshot", "--plan-in", str(plan)]
            response = HttpResponse(201, {}, b"", "https://a.klaviyo.com/api/image-upload")
            with patch("klaviyo_safe_agent_cli.commands.api.HttpClient.request", return_value=response) as request:
                self.assertTrue(self._run_main(apply + operation)[1]["ok"])
                request.assert_called_once()
                self.assertEqual(request.call_args.kwargs["files"]["file"][1], upload.read_bytes())
                request.reset_mock()
                upload.write_bytes(b"updated image")
                self.assertTrue(self._run_main(apply + operation)[1]["refused"])
                request.assert_not_called()

    def test_bulk_receipts_show_accepted_and_uncertain_results(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            env = self._env_file(root).rename(root / "my settings.env")
            plan = root / "import-plan.json"
            receipt = root / "import-receipt.json"
            args = ["--env-file", str(env), "--no-artifacts"]
            operation = ["api", "bulk_import_profiles", "--body-json", '{"data":{"type":"profile-bulk-import-job"}}']
            self._run_main(args + ["--plan-out", str(plan)] + operation)
            apply = args + [
                "--live", "--apply", "--yes", "--ack-no-snapshot", "--plan-in", str(plan),
                "--receipt-out", str(receipt),
            ]
            response = HttpResponse(
                202, {"content-type": "application/vnd.api+json"}, b'{"data":{"id":"job-123"}}',
                "https://a.klaviyo.com/api/profile-bulk-import-jobs",
            )
            with patch("klaviyo_safe_agent_cli.commands.api.HttpClient.request", return_value=response) as request:
                rc, result = self._run_main(apply + operation)
                request.assert_called_once()
                self.assertEqual(rc, 0)
                result = result["receipt"]["verification"]
                self.assertEqual(result["status"], "accepted")
                command = shlex.split(result["next_command"])
                self.assertEqual(command[1:3], ["--env-file", str(env)])
                self.assertEqual(command[-4:], ["api", "get_bulk_import_profiles_job", "--path", "job_id=job-123"])

                request.reset_mock()
                request.side_effect = RuntimeError("Simulated lost reply")
                rc, result = self._run_main(apply + operation)
                request.assert_called_once()
                self.assertEqual(rc, 1)
                self.assertEqual(result["receipt"], json.loads(receipt.read_text()))
                self.assertEqual(result["receipt"]["verification"]["status"], "uncertain")

    def test_raw_command_input_stays_out_of_run_history(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            env = self._env_file(root)
            sample = "dummy-private-command-argument"
            rc, result = self._run_main([
                "--env-file", str(env), "api", "create_list",
                "--body-json", json.dumps({"data": {"attributes": {"name": sample}}}),
            ])
            self.assertEqual(rc, 0)
            run = Path(result["artifacts_dir"])
            for path in (run / "summary.md", run / "audit.jsonl", Path(result["runs_index"])):
                self.assertNotIn(sample, path.read_text())
