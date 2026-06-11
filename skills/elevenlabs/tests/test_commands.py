from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from elevenlabs_api_tool.cli import build_parser, main
from elevenlabs_api_tool.commands.operation_runner import _operation_requires_apply
from elevenlabs_api_tool.errors import ValidationError
from elevenlabs_api_tool.http import HttpResponse
from elevenlabs_api_tool.operations import OPERATIONS


class TestElevenLabsCommands(unittest.TestCase):
    def _env_file(self, directory: Path, *, api_key: str | None = "secret-token") -> Path:
        env_path = directory / ".env"
        env_path.write_text(
            "\n".join(
                [
                    "ELEVENLABS_API_BASE_URL=http://example.invalid",
                    f"ELEVENLABS_API_KEY={api_key}" if api_key else "",
                    "ELEVENLABS_TIMEOUT_S=30",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        return env_path

    def _run(self, args: list[str], *, api_key: str | None = "secret-token") -> dict[str, object]:
        with tempfile.TemporaryDirectory() as tmp:
            env_path = self._env_file(Path(tmp), api_key=api_key)
            buf = io.StringIO()
            with redirect_stdout(buf):
                _ = main(["--env-file", str(env_path), "--output", "json"] + args)
            return json.loads(buf.getvalue())

    def _assert_no_recovery_contract(self, recovery: object) -> None:
        self.assertIsInstance(recovery, dict)
        self.assertIs(recovery["automatic_rollback"], False)
        self.assertEqual(recovery["end_state"], "irreversible_and_clearly_labeled")
        self.assertEqual(recovery["strategy"], "no_inverse")
        self.assertIs(recovery["rollback_ready"], False)
        self.assertEqual(recovery["backups"], [])
        self.assertEqual(recovery["snapshots"], [])
        self.assertIsNone(recovery["rollback_plan"])
        self.assertIn("automated rollback", str(recovery["restore_note"]))
        self.assertIn("irreversible", str(recovery["restore_note"]))
        self.assertIn("manual cleanup", str(recovery["restore_note"]))

    def _assert_blocked_before_state(self, plan: object) -> None:
        self.assertIsInstance(plan, dict)
        before_state = plan["before_state"]
        self.assertIsInstance(before_state, dict)
        self.assertIs(before_state["required"], True)
        self.assertIs(before_state["supported"], False)
        self.assertEqual(before_state["status"], "no_snapshot_available")
        self.assertIsNone(before_state["saved_path"])
        self.assertIsNone(before_state["provider_backup_id"])
        self.assertEqual(plan["verification_plan"]["type"], "best_effort_after_apply")

    def test_auth_check_plan_does_not_leak_token(self) -> None:
        payload = self._run(["auth", "check"])
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["dry_run"])
        self.assertIn("plan", payload)
        plan = payload["plan"]
        self.assertEqual(plan["endpoint"], "GET /v1/user")
        self.assertNotIn("secret-token", json.dumps(payload))
        self._assert_no_recovery_contract(plan["recovery"])

    def test_write_apply_refuses_without_before_state(self) -> None:
        with patch("elevenlabs_api_tool.http.HttpClient.request") as mock_request:
            mock_request.return_value = HttpResponse(
                status=200,
                headers={},
                body=b"audio-bytes",
                url="http://example.invalid/v1/text-to-speech/abc",
            )
            with tempfile.TemporaryDirectory() as tmp:
                env_path = self._env_file(Path(tmp))
                out_path = Path(tmp) / "out.mp3"
                buf = io.StringIO()
                with redirect_stdout(buf):
                    _ = main(
                        [
                            "--env-file",
                            str(env_path),
                            "--output",
                            "json",
                            "--live",
                            "--apply",
                            "--ack-spend-money",
                            "tts",
                            "synthesize",
                            "--voice-id",
                            "abc",
                            "--text",
                            "hello",
                            "--out",
                            str(out_path),
                        ]
                    )
                payload = json.loads(buf.getvalue())
                file_exists = out_path.exists()
        self.assertTrue(payload["ok"])
        self.assertFalse(payload["dry_run"])
        self.assertTrue(payload["refused"])
        self.assertEqual(payload["verification_plan"]["type"], "best_effort_after_apply")
        self.assertIn("before-state", payload["reasons"][0])
        self.assertIn("plan", payload)
        self._assert_blocked_before_state(payload["plan"])
        self.assertNotIn("receipt", payload)
        self.assertFalse(file_exists)
        mock_request.assert_not_called()

    def test_tts_plan_includes_no_recovery_contract(self) -> None:
        payload = self._run(
            [
                "tts",
                "synthesize",
                "--voice-id",
                "abc",
                "--text",
                "hello",
                "--out",
                "out.mp3",
            ]
        )
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["dry_run"])
        self.assertIn("plan", payload)
        self._assert_no_recovery_contract(payload["plan"]["recovery"])
        self._assert_blocked_before_state(payload["plan"])

    @patch("elevenlabs_api_tool.http.HttpClient.request")
    def test_plan_mode_never_calls_http(self, mock_request) -> None:
        payload = self._run(["auth", "check"])
        self.assertTrue(payload["dry_run"])
        mock_request.assert_not_called()

    def test_auth_live_requires_out(self) -> None:
        payload = self._run(["--live", "auth", "check"])
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("Missing --out", payload["error"])

    @patch("elevenlabs_api_tool.http.HttpClient.request")
    def test_auth_live_writes_json_file(self, mock_request) -> None:
        mock_request.return_value = HttpResponse(
            status=200,
            headers={},
            body=b'{"workspace":"zoom"}',
            url="http://example.invalid/user",
        )
        with tempfile.TemporaryDirectory() as tmp:
            env_path = self._env_file(Path(tmp))
            out_path = Path(tmp) / "auth.json"
            buf = io.StringIO()
            with redirect_stdout(buf):
                _ = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--output",
                        "json",
                        "--live",
                        "auth",
                        "check",
                        "--out",
                        str(out_path),
                    ]
                )
            payload = json.loads(buf.getvalue())
            file_contents = out_path.read_text(encoding="utf-8")
            file_exists = out_path.exists()
            expected_path = str(out_path)
        self.assertTrue(payload["ok"])
        self.assertFalse(payload["dry_run"])
        self.assertNotIn("response", payload)
        self.assertIn("file", payload)
        self.assertTrue(file_exists)
        self.assertEqual(json.loads(file_contents), {"workspace": "zoom"})
        self.assertEqual(payload["file"]["file_path"], expected_path)
        self.assertEqual(payload["receipt"]["outputs"]["file"]["file_path"], expected_path)
        self.assertNotIn("secret-token", buf.getvalue())
        self.assertTrue(mock_request.called)

    def test_tts_plan_includes_endpoint(self) -> None:
        payload = self._run(["tts", "synthesize", "--voice-id", "abc", "--text", "hello", "--out", "out.mp3"])
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["endpoint"], "POST /v1/text-to-speech/{voice_id}")

    def test_voices_list_plan_endpoint(self) -> None:
        payload = self._run(["voices", "list"])
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["endpoint"], "GET /v1/voices")

    def test_models_list_plan_endpoint(self) -> None:
        payload = self._run(["models", "list"])
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["endpoint"], "GET /v1/models")

    def test_usage_get_plan_endpoint(self) -> None:
        payload = self._run(["usage", "get"])
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["endpoint"], "GET /v1/usage/character-stats")

    @patch("elevenlabs_api_tool.http.HttpClient.request")
    def test_usage_get_live_uses_default_window_params(self, mock_request) -> None:
        mock_request.return_value = HttpResponse(
            status=200,
            headers={},
            body=b'{"time":[],"usage":{}}',
            url="http://example.invalid/usage/character-stats",
        )
        payload = self._run(["--live", "usage", "get"])
        self.assertTrue(payload["ok"])
        _, kwargs = mock_request.call_args
        self.assertIn("start_unix", kwargs["params"])
        self.assertIn("end_unix", kwargs["params"])

    def test_history_list_plan_endpoint(self) -> None:
        payload = self._run(["history", "list"])
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["endpoint"], "GET /v1/history")

    def test_history_live_requires_out(self) -> None:
        payload = self._run(["--live", "history", "list"])
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("Missing --out", payload["error"])

    @patch("elevenlabs_api_tool.http.HttpClient.request")
    def test_history_live_writes_json_file(self, mock_request) -> None:
        mock_request.return_value = HttpResponse(
            status=200,
            headers={},
            body=b'{"items":[1,2,3]}',
            url="http://example.invalid/history",
        )
        with tempfile.TemporaryDirectory() as tmp:
            env_path = self._env_file(Path(tmp))
            out_path = Path(tmp) / "history.json"
            buf = io.StringIO()
            with redirect_stdout(buf):
                _ = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--output",
                        "json",
                        "--live",
                        "history",
                        "list",
                        "--out",
                        str(out_path),
                    ]
                )
            payload = json.loads(buf.getvalue())
            file_contents = out_path.read_text(encoding="utf-8")
            file_exists = out_path.exists()
            expected_path = str(out_path)
        self.assertTrue(payload["ok"])
        self.assertFalse(payload["dry_run"])
        self.assertNotIn("response", payload)
        self.assertIn("file", payload)
        self.assertTrue(file_exists)
        self.assertEqual(json.loads(file_contents), {"items": [1, 2, 3]})
        self.assertEqual(payload["file"]["file_path"], expected_path)
        self.assertEqual(payload["receipt"]["outputs"]["file"]["file_path"], expected_path)
        self.assertNotIn("secret-token", buf.getvalue())
        self.assertTrue(mock_request.called)
    def test_history_download_plan_endpoint(self) -> None:
        payload = self._run(
            ["history", "download", "--history-item-id", "item-1", "--out", "history.mp3"]
        )
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["endpoint"], "POST /v1/history/download")

    def test_all_operations_plan_endpoint(self) -> None:
        for op in OPERATIONS:
            with self.subTest(operation=op.name):
                skip_commands = {
                    "auth check",
                    "voices list",
                    "models list",
                    "usage get",
                    "history list",
                    "history download",
                    "tts synthesize",
                }
                if op.cli_command.lower() in skip_commands:
                    continue
                tokens = op.cli_command.split()
                args = tokens + list(op.sample_args)
                if "binary_output" in op.safety and "--out" not in args:
                    args += ["--out", "sample.bin"]
                elif "sensitive_output" in op.safety and "--out" not in args:
                    args += ["--out", "sample.json"]
                payload = self._run(args)
                self.assertTrue(payload["ok"])
                self.assertTrue(payload["dry_run"])
                self.assertEqual(payload["plan"]["endpoint"], f"{op.method.upper()} {op.path}")
                self.assertNotIn("secret-token", json.dumps(payload))

    def test_tts_requires_output_path(self) -> None:
        parser = build_parser()
        with self.assertRaises(ValidationError):
            parser.parse_args(["tts", "synthesize", "--voice-id", "abc", "--text", "hello"])

    def test_history_download_requires_output_path(self) -> None:
        parser = build_parser()
        with self.assertRaises(ValidationError):
            parser.parse_args(["history", "download", "--history-item-id", "item-1"])

    @patch("elevenlabs_api_tool.http.HttpClient.request")
    def test_history_download_apply_refuses_without_before_state(self, mock_request) -> None:
        mock_request.return_value = HttpResponse(
            status=200,
            headers={},
            body=b"audio-bytes",
            url="http://example.invalid/history/download",
        )
        with tempfile.TemporaryDirectory() as tmp:
            env_path = self._env_file(Path(tmp))
            out_path = Path(tmp) / "history.mp3"
            buf = io.StringIO()
            with redirect_stdout(buf):
                _ = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--output",
                        "json",
                        "--live",
                        "--apply",
                        "history",
                        "download",
                        "--history-item-id",
                        "item-1",
                        "--out",
                        str(out_path),
                    ]
                )
            payload = json.loads(buf.getvalue())
            file_exists = out_path.exists()
        self.assertTrue(payload["ok"])
        self.assertFalse(payload["dry_run"])
        self.assertTrue(payload["refused"])
        self._assert_blocked_before_state(payload["plan"])
        self.assertFalse(file_exists)
        mock_request.assert_not_called()

    @patch("elevenlabs_api_tool.http.HttpClient.request")
    def test_file_upload_with_body_uses_multipart_form_fields(self, mock_request) -> None:
        mock_request.return_value = HttpResponse(
            status=200,
            headers={},
            body=b'{"text":"ok"}',
            url="http://example.invalid/speech-to-text",
        )
        with tempfile.TemporaryDirectory() as tmp:
            env_path = self._env_file(Path(tmp))
            audio_path = Path(tmp) / "sample.mp3"
            out_path = Path(tmp) / "stt.json"
            audio_path.write_bytes(b"fake-audio")
            buf = io.StringIO()
            with redirect_stdout(buf):
                _ = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--output",
                        "json",
                        "--live",
                        "--apply",
                        "--ack-spend-money",
                        "stt",
                        "transcribe",
                        "--body",
                        '{"model_id":"scribe_v1"}',
                        "--file",
                        f"audio=@{audio_path}",
                        "--out",
                        str(out_path),
                    ]
                )
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertFalse(payload["dry_run"])
        self.assertTrue(payload["refused"])
        self._assert_blocked_before_state(payload["plan"])
        mock_request.assert_not_called()

    def test_write_op_requires_apply_when_live(self) -> None:
        payload = self._run(
            [
                "--live",
                "sound-effects",
                "generate",
                "--out",
                "example.bin",
            ]
        )
        self.assertTrue(payload["ok"])
        self.assertTrue(payload.get("refused"))
        self.assertIn("--live requires --apply", payload["reasons"][0])

    @patch("elevenlabs_api_tool.http.HttpClient.request")
    def test_live_write_without_apply_never_calls_http(self, mock_request) -> None:
        payload = self._run(
            [
                "--live",
                "sound-effects",
                "generate",
                "--out",
                "example.bin",
            ]
        )
        self.assertTrue(payload.get("refused"))
        mock_request.assert_not_called()
    @patch("elevenlabs_api_tool.http.HttpClient.request")
    def test_apply_false_live_runs_never_call_http(self, mock_request) -> None:
        skip_commands = {
            "auth check",
            "voices list",
            "models list",
            "usage get",
            "history list",
            "history download",
            "tts synthesize",
        }
        for op in OPERATIONS:
            if not _operation_requires_apply(op):
                continue
            if op.cli_command.lower() in skip_commands:
                continue
            tokens = op.cli_command.split()
            args: list[str] = ["--live"] + tokens + list(op.sample_args)
            if "binary_output" in op.safety and "--out" not in args:
                args.extend(["--out", "sample.bin"])
            elif "sensitive_output" in op.safety and "--out" not in args:
                args.extend(["--out", "sample.json"])
            with self.subTest(operation=op.name):
                payload = self._run(args)
                self.assertTrue(payload["ok"])
                self.assertTrue(payload.get("refused"))
                self.assertNotIn("secret-token", json.dumps(payload))
                self.assertTrue(
                    any("--live requires --apply" in reason for reason in payload.get("reasons", [])),
                    f"{op.cli_command} should mention --live requires --apply when refused",
                )
                self.assertFalse(
                    mock_request.called,
                    f"{op.cli_command} should not make HTTP calls when --apply is False",
                )

    def test_music_plan_requires_apply_and_ack(self) -> None:
        base_args = [
            "--live",
            "music",
            "plan",
            "create",
            "--body",
            '{"name":"plan"}',
        ]
        payload = self._run(base_args)
        self.assertTrue(payload["ok"])
        self.assertTrue(payload.get("refused"))
        self.assertIn("--live requires --apply", payload["reasons"][0])

        verify_args = [
            "--live",
            "--apply",
            "music",
            "plan",
            "create",
            "--body",
            '{"name":"plan"}',
        ]
        payload_ack = self._run(verify_args)
        self.assertTrue(payload_ack.get("refused"))
        self.assertIn("--ack-spend-money", payload_ack["reasons"][0])

    def test_spend_money_requires_ack_spend_money(self) -> None:
        payload = self._run(
            [
                "--live",
                "--apply",
                "sound-effects",
                "generate",
                "--out",
                "example.bin",
            ]
        )
        self.assertTrue(payload.get("refused"))
        self.assertIn("--ack-spend-money", payload["reasons"][0])

    @patch("elevenlabs_api_tool.http.HttpClient.request")
    def test_all_spend_money_operations_require_ack_spend_money(self, mock_request) -> None:
        for op in OPERATIONS:
            if "spend_money" not in op.safety:
                continue
            tokens = op.cli_command.split()
            args = ["--live", "--apply"] + tokens + list(op.sample_args)
            if "binary_output" in op.safety and "--out" not in args:
                args += ["--out", "sample.bin"]
            elif "sensitive_output" in op.safety and "--out" not in args:
                args += ["--out", "sample.json"]
            payload = self._run(args)
            self.assertTrue(payload.get("refused"))
            reasons = payload.get("reasons", [])
            self.assertTrue(any("--ack-spend-money" in reason for reason in reasons))
        mock_request.assert_not_called()

    def test_irreversible_requires_ack_and_yes(self) -> None:
        base_args = [
            "--live",
            "--apply",
            "--ack-spend-money",
            "convai",
            "twilio",
            "register-call",
            "--param",
            "foo=bar",
        ]
        payload = self._run(base_args)
        self.assertTrue(payload.get("refused"))
        self.assertIn("--ack-irreversible", payload["reasons"][0])

        payload_yes = self._run(
            [
                "--live",
                "--apply",
                "--ack-spend-money",
                "--ack-irreversible",
                "convai",
                "twilio",
                "register-call",
                "--param",
                "foo=bar",
            ]
        )
        self.assertTrue(payload_yes.get("refused"))
        self.assertIn("--yes", payload_yes["reasons"][0])

    def test_workspace_webhooks_delete_requires_ack_and_yes(self) -> None:
        common_args = [
            "--live",
            "--apply",
            "workspace",
            "webhooks",
            "delete",
            "--webhook-id",
            "hook-1",
            "--out",
            "delete.json",
        ]
        payload = self._run(common_args)
        self.assertTrue(payload.get("refused"))
        self.assertIn("--ack-irreversible", payload["reasons"][0])

        payload_yes = self._run(
            [
                "--live",
                "--apply",
                "--ack-irreversible",
                "workspace",
                "webhooks",
                "delete",
                "--webhook-id",
                "hook-1",
                "--out",
                "delete.json",
            ]
        )
        self.assertTrue(payload_yes.get("refused"))
        self.assertIn("--yes", payload_yes["reasons"][0])

    def test_plan_does_not_require_body_or_file_membership(self) -> None:
        payload = self._run(
            [
                "tokens",
                "single-use",
                "create",
                "--token-type",
                "tts_websocket",
                "--body-file",
                "missing.json",
                "--file",
                "upload=@missing",
            ]
        )
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["dry_run"])

    def test_stt_realtime_plan_without_out(self) -> None:
        payload = self._run(["stt", "realtime"])
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["dry_run"])
        self.assertEqual(
            payload["plan"]["endpoint"],
            "WEBSOCKET wss://api.elevenlabs.io/v1/speech-to-text/realtime",
        )
        self.assertNotIn("secret-token", json.dumps(payload))

    @patch("elevenlabs_api_tool.http.HttpClient.request")
    def test_read_only_live_executes_without_apply(self, mock_request) -> None:
        mock_request.return_value = HttpResponse(
            status=200,
            headers={},
            body=b'{"items": []}',
            url="http://example.invalid/service-accounts",
        )
        payload = self._run(
            [
                "--live",
                "service-accounts",
                "list",
            ]
        )
        self.assertTrue(payload["ok"])
        self.assertFalse(payload["dry_run"])
        self.assertFalse(payload.get("refused"))
        self.assertNotIn("secret-token", json.dumps(payload))
        self.assertTrue(mock_request.called)
