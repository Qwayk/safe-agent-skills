from __future__ import annotations

import io
import json
import tempfile
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from threads_api_tool.commands import auth as auth_cmd
from threads_api_tool.oauth_tokens import TokenStatus
from threads_api_tool.output import Output


class _NoopAudit:
    def write(self, *_args, **_kwargs) -> None:
        return None


class TestAuthCommandRedaction(unittest.TestCase):
    def _ctx(self, env_file: Path, **overrides) -> dict:
        cfg = SimpleNamespace(
            base_url="http://example.invalid",
            api_version="v1.0",
            token="user-token",
            app_id="app-id",
            app_secret="app-secret",
            redirect_uri="https://callback.local",
            default_user_id="threads-default",
            timeout_s=30.0,
        )
        ctx = {
            "cfg": cfg,
            "out": Output(mode="json"),
            "audit": _NoopAudit(),
            "tool": "threads-api-tool",
            "tool_version": "0.1.0",
            "command_str": "threads-api-tool auth code exchange",
            "env_file": str(env_file),
            "timeout_s": 30,
            "verbose": False,
            "apply": True,
            "yes": False,
            "plan_out": None,
            "plan_in": None,
            "receipt_out": None,
            "ack_irreversible": False,
            "run_id": None,
            "artifacts_dir": None,
            "runs_index_path": None,
        }
        ctx.update(overrides)
        return ctx

    def test_auth_code_exchange_redacts_tokens(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_file = Path(d) / ".env"
            env_file.write_text("", encoding="utf-8")
            fake = Mock()
            fake.exchange_auth_code.return_value = {
                "access_token": "secret-token",
                "refresh_token": "secret-refresh",
                "token_type": "bearer",
                "user_id": "user-1",
            }

            args = SimpleNamespace(code="auth-code")
            buf = io.StringIO()
            with patch("threads_api_tool.commands.auth._client", return_value=fake):
                with redirect_stdout(buf):
                    rc = auth_cmd.cmd_auth_code_exchange(args, self._ctx(env_file))

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["plan"]["before_state"]["status"], "no_snapshot_available")
            self.assertTrue(payload["plan"]["before_state"]["local_state"]["writes_token_file"])
            fake.exchange_auth_code.assert_not_called()
            self.assertFalse((Path(d) / ".state" / "token.json").exists())

    def test_auth_app_token_generate_redacts_tokens(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_file = Path(d) / ".env"
            env_file.write_text("", encoding="utf-8")
            fake = Mock()
            fake.generate_app_access_token.return_value = {
                "access_token": "app-secret-token",
                "token_type": "bearer",
            }

            args = SimpleNamespace()
            buf = io.StringIO()
            with patch("threads_api_tool.commands.auth._client", return_value=fake):
                with redirect_stdout(buf):
                    rc = auth_cmd.cmd_auth_app_token_generate(args, self._ctx(env_file))

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["result"]["access_token"], "***REDACTED***")

    def test_auth_debug_token_redacts_tokens_in_result(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_file = Path(d) / ".env"
            env_file.write_text("", encoding="utf-8")
            fake = Mock()
            fake.debug_token.return_value = {
                "is_valid": True,
                "input_token": "user-token",
                "token_type": "bearer",
                "expires_at": 9999,
            }

            args = SimpleNamespace(input_token=None)
            buf = io.StringIO()
            with patch("threads_api_tool.commands.auth._client", return_value=fake):
                with redirect_stdout(buf):
                    rc = auth_cmd.cmd_auth_debug_token(args, self._ctx(env_file))

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["result"]["is_valid"], True)
            self.assertEqual(payload["result"]["token_type"], "bearer")
            self.assertEqual(payload["result"]["input_token"], "***REDACTED***")

    def test_auth_check_calls_me_endpoint(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_file = Path(d) / ".env"
            env_file.write_text("", encoding="utf-8")
            fake = Mock()
            fake.get_me.return_value = {"id": "user-1", "username": "alice"}

            args = SimpleNamespace()
            buf = io.StringIO()
            with patch("threads_api_tool.commands.auth._client", return_value=fake):
                with redirect_stdout(buf):
                    rc = auth_cmd.cmd_auth_check(args, self._ctx(env_file))

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            fake.get_me.assert_called_once_with(fields="id,username")
            self.assertEqual(payload["command"], "auth.check")
            self.assertEqual(payload["result"]["username"], "alice")

    def test_auth_authorize_url_uses_scope_and_state(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_file = Path(d) / ".env"
            env_file.write_text("", encoding="utf-8")
            fake = Mock()
            fake.build_authorize_url.return_value = "https://threads.net/oauth/authorize?client_id=app-id"

            args = SimpleNamespace(scope="threads_basic,threads_content_publish", state="state-1")
            buf = io.StringIO()
            with patch("threads_api_tool.commands.auth._client", return_value=fake):
                with redirect_stdout(buf):
                    rc = auth_cmd.cmd_auth_authorize_url(args, self._ctx(env_file))

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            fake.build_authorize_url.assert_called_once_with(
                scope="threads_basic,threads_content_publish",
                state="state-1",
                response_type="code",
            )
            self.assertEqual(payload["command"], "auth.authorize_url")
            self.assertIn("threads.net/oauth/authorize", payload["authorize_url"])

    def test_auth_token_status_reports_store_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_file = Path(d) / ".env"
            env_file.write_text("", encoding="utf-8")
            args = SimpleNamespace()
            buf = io.StringIO()
            status = TokenStatus(
                exists=True,
                path=str(Path(d) / ".state" / "token.json"),
                updated_at_utc="2026-05-26T12:00:00Z",
                fields=["access_token", "expires_in", "refresh_token"],
                has_refresh_token=True,
                expires_at_utc="2026-06-25T12:00:00Z",
            )
            with patch("threads_api_tool.oauth_tokens.get_token_status", return_value=status):
                with redirect_stdout(buf):
                    rc = auth_cmd.cmd_auth_token_status(args, self._ctx(env_file))

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["command"], "auth.token_status")
            self.assertTrue(payload["env_token_present"])
            self.assertTrue(payload["token_store"]["exists"])
            self.assertTrue(payload["token_store"]["has_refresh_token"])
            self.assertEqual(payload["token_store"]["fields"], ["access_token", "expires_in", "refresh_token"])

    def test_auth_token_exchange_long_dry_run_does_not_call_api(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_file = Path(d) / ".env"
            env_file.write_text("", encoding="utf-8")
            fake = Mock()

            args = SimpleNamespace(short_token="short-token")
            buf = io.StringIO()
            with patch("threads_api_tool.commands.auth._client", return_value=fake):
                with redirect_stdout(buf):
                    rc = auth_cmd.cmd_auth_token_exchange_long(
                        args,
                        self._ctx(env_file, apply=False),
                    )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["dry_run"])
            fake.exchange_short_lived_token.assert_not_called()

    def test_auth_token_exchange_long_refuses_before_token_http(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_file = Path(d) / ".env"
            env_file.write_text("", encoding="utf-8")
            fake = Mock()
            fake.exchange_short_lived_token.return_value = {
                "access_token": "long-secret-token",
                "token_type": "bearer",
                "expires_in": 5184000,
            }

            args = SimpleNamespace(short_token="short-token")
            buf = io.StringIO()
            with patch("threads_api_tool.commands.auth._client", return_value=fake):
                with redirect_stdout(buf):
                    rc = auth_cmd.cmd_auth_token_exchange_long(
                        args,
                        self._ctx(env_file, apply=True),
                    )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["plan"]["before_state"]["status"], "no_snapshot_available")
            fake.exchange_short_lived_token.assert_not_called()
            self.assertFalse((Path(d) / ".state" / "token.json").exists())

    def test_auth_token_refresh_refuses_before_token_http(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_file = Path(d) / ".env"
            env_file.write_text("", encoding="utf-8")
            fake = Mock()
            fake.refresh_long_lived_token.return_value = {
                "access_token": "refreshed-secret-token",
                "token_type": "bearer",
                "expires_in": 5184000,
            }

            args = SimpleNamespace(long_token="long-token")
            buf = io.StringIO()
            with patch("threads_api_tool.commands.auth._client", return_value=fake):
                with redirect_stdout(buf):
                    rc = auth_cmd.cmd_auth_token_refresh(
                        args,
                        self._ctx(env_file, apply=True),
                    )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["plan"]["before_state"]["status"], "no_snapshot_available")
            fake.refresh_long_lived_token.assert_not_called()
            self.assertFalse((Path(d) / ".state" / "token.json").exists())
