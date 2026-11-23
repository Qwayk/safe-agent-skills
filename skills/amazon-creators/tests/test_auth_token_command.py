from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from amazon_creators_api_tool.cli import main
from amazon_creators_api_tool.oauth_tokens import token_path_for_env_file


class TestAuthTokenFetchCommand(unittest.TestCase):
    def _write_env(self, base: str) -> str:
        env_path = os.path.join(base, ".env")
        with open(env_path, "w", encoding="utf-8") as f:
            f.write("AMAZON_CREATORS_API_BASE_URL=https://creatorsapi.amazon/catalog/v1\n")
            f.write("AMAZON_CREATORS_CREDENTIAL_ID=cred-id\n")
            f.write("AMAZON_CREATORS_CREDENTIAL_SECRET=secret\n")
            f.write("AMAZON_CREATORS_CREDENTIAL_VERSION=2.1\n")
            f.write("AMAZON_CREATORS_LOCALE=en_US\n")
            f.write("AMAZON_CREATORS_TIMEOUT_S=30\n")
            f.write("AMAZON_CREATORS_PARTNER_TAG=partner-tag\n")
        return env_path

    def _run_command(self, env_path: str, global_flags: list[str] | None = None, extra: list[str] | None = None, expected_code: int = 0) -> dict[str, object]:
        cmd = ["--output", "json", "--env-file", env_path]
        if global_flags:
            cmd += global_flags
        cmd += ["auth", "token", "fetch"]
        if extra:
            cmd += extra
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(cmd)
        self.assertEqual(rc, expected_code)
        return json.loads(buf.getvalue())

    def test_previews_without_contacting_amazon_or_writing_a_token(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            with patch("amazon_creators_api_tool.oauth_tokens.requests.post") as send:
                payload = self._run_command(env_path)
            send.assert_not_called()
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["plan"]["selector"]["operation"], "auth.token_fetch")
            self.assertFalse(token_path_for_env_file(env_path).exists())

    def test_apply_fetches_for_the_selected_account_and_reuses_its_token(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(self._write_env(td))
            other = env_path.with_name("second.env")
            other.write_text(env_path.read_text().replace("cred-id", "second-id"))
            with (
                patch.dict(os.environ, {"AMAZON_CREATORS_CREDENTIAL_ID": "wrong-shell-id"}),
                patch("amazon_creators_api_tool.oauth_tokens.requests.post") as send,
            ):
                send.return_value.status_code = 200
                send.return_value.json.side_effect = [
                    {"access_token": "first-fixture-token", "expires_in": 3600},
                    {"access_token": "second-fixture-token", "expires_in": 3600},
                ]
                first = self._run_command(str(env_path), global_flags=["--apply"])
                self._run_command(str(env_path), global_flags=["--apply"])
                second = self._run_command(str(other), global_flags=["--apply"])
                self.assertEqual(send.call_count, 2)
                self.assertEqual(send.call_args_list[0].kwargs["data"]["client_id"], "cred-id")
                self.assertEqual(send.call_args_list[1].kwargs["data"]["client_id"], "second-id")
            for path, report in ((env_path, first), (other, second)):
                cache = token_path_for_env_file(str(path))
                self.assertEqual(cache.stat().st_mode & 0o777, 0o600)
                self.assertFalse(report["catalog_access_checked"])
                self.assertNotIn("fixture-token", json.dumps(report))
            self.assertNotEqual(first["token_status"]["path"], second["token_status"]["path"])

    def test_failed_refresh_preserves_the_previous_token(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            with patch("amazon_creators_api_tool.oauth_tokens.requests.post") as send:
                send.return_value.status_code = 200
                send.return_value.json.side_effect = [
                    {"access_token": "first-fixture-token", "expires_in": 3600},
                    {"error": "fixture rejection"},
                ]
                self._run_command(env_path, global_flags=["--apply"])
                cache = token_path_for_env_file(env_path)
                previous = cache.read_bytes()
                error = self._run_command(env_path, global_flags=["--apply"], extra=["--force"], expected_code=1)
            self.assertFalse(error["ok"])
            self.assertEqual(cache.read_bytes(), previous)


class TestAuthTokenSetCommand(unittest.TestCase):
    def _write_env(self, base: str) -> str:
        env_path = os.path.join(base, ".env")
        with open(env_path, "w", encoding="utf-8") as f:
            f.write("AMAZON_CREATORS_API_BASE_URL=https://creatorsapi.amazon/catalog/v1\n")
            f.write("AMAZON_CREATORS_CREDENTIAL_ID=cred-id-x\n")
            f.write("AMAZON_CREATORS_CREDENTIAL_SECRET=secret-x\n")
            f.write("AMAZON_CREATORS_CREDENTIAL_VERSION=2\n")
            f.write("AMAZON_CREATORS_LOCALE=en_US\n")
            f.write("AMAZON_CREATORS_TIMEOUT_S=30\n")
            f.write("AMAZON_CREATORS_PARTNER_TAG=partner-tag\n")
        return env_path

    def _write_token_input(self, base: str) -> str:
        token_path = os.path.join(base, "token-input.json")
        with open(token_path, "w", encoding="utf-8") as f:
            json.dump({"access_token": "A", "scope": "foo"}, f)
        return token_path

    def _run_command(self, env_path: str, token_file: str, flags: list[str], global_flags: list[str] | None = None) -> dict[str, object]:
        cmd = ["--output", "json", "--env-file", env_path]
        if global_flags:
            cmd += global_flags
        cmd += ["auth", "token", "set", "--file", token_file] + flags
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(cmd)
        self.assertEqual(rc, 0)
        return json.loads(buf.getvalue())

    def test_refuses_without_apply(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            token_input = self._write_token_input(td)
            payload = self._run_command(env_path, token_input, [])
            self.assertTrue(payload.get("ok"))
            self.assertTrue(payload.get("dry_run"))
            self.assertEqual(payload["plan"]["before_state"]["status"], "true_blocker")
            dest = os.path.join(td, ".state", "token.json")
            self.assertFalse(os.path.exists(dest))

    def test_apply_refuses_before_token_write(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            token_input = self._write_token_input(td)
            payload = self._run_command(env_path, token_input, [], global_flags=["--apply"])
            self.assertTrue(payload.get("ok"))
            self.assertTrue(payload.get("refused"))
            self.assertEqual(payload["plan"]["before_state"]["status"], "true_blocker")
            self.assertEqual(payload["verification_plan"]["status"], "true_blocker")
            dest = os.path.join(td, ".state", "token.json")
            self.assertFalse(os.path.exists(dest))
