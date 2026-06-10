from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from amazon_creators_api_tool.cli import main


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

    def _run_command(self, env_path: str, global_flags: list[str] | None = None, extra: list[str] | None = None) -> dict[str, object]:
        cmd = ["--output", "json", "--env-file", env_path]
        if global_flags:
            cmd += global_flags
        cmd += ["auth", "token", "fetch"]
        if extra:
            cmd += extra
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(cmd)
        self.assertEqual(rc, 0)
        return json.loads(buf.getvalue())

    def test_refuses_without_apply(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            payload = self._run_command(env_path)
            self.assertTrue(payload.get("ok"))
            self.assertTrue(payload.get("dry_run"))
            self.assertEqual(payload["plan"]["before_state"]["status"], "true_blocker")

    def test_fetch_with_apply_refuses_before_service_or_token_write(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            with patch(
                "amazon_creators_api_tool.oauth_tokens.requests.post",
                side_effect=AssertionError("token endpoint must not be called when before-state is blocked"),
            ):
                payload = self._run_command(env_path, global_flags=["--apply"])
            self.assertTrue(payload.get("ok"))
            self.assertTrue(payload.get("refused"))
            self.assertEqual(payload["plan"]["before_state"]["status"], "true_blocker")
            self.assertEqual(payload["verification_plan"]["status"], "true_blocker")
            self.assertFalse(os.path.exists(os.path.join(td, ".state", "token.json")))


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
