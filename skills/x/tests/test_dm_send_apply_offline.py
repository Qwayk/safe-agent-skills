from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from x_api_tool.cli import main


class _DummyResponse:
    def __init__(self, *, status_code: int = 200, url: str = "https://api.x.com/2/example") -> None:
        self.status_code = status_code
        self.url = url

    def json(self) -> dict:
        return {}


class TestDmSendApplyOffline(unittest.TestCase):
    def _write_env(self, d: str) -> Path:
        env = Path(d) / ".env"
        env.write_text("X_API_BASE_URL=https://api.x.com/2\nX_API_TIMEOUT_S=30\n", encoding="utf-8")
        return env

    def _write_user_token(self, d: str) -> None:
        state_dir = Path(d) / ".state"
        state_dir.mkdir(parents=True, exist_ok=True)
        (state_dir / "token.json").write_text('{"access_token":"TEST_TOKEN"}\n', encoding="utf-8")

    def test_dm_send_apply_refuses_before_provider_call(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env = self._write_env(d)
            self._write_user_token(d)

            buf = io.StringIO()
            with patch("x_api_tool.commands.dm._post_json_with_backoff", return_value=_DummyResponse(status_code=200)) as mock_post:
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            str(env),
                            "--apply",
                            "--yes",
                            "dm",
                            "send",
                            "--to-user-id",
                            "123",
                            "--message",
                            "Hello",
                        ]
                    )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertFalse(payload["dry_run"])
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["plan"]["before_state"]["status"], "no_snapshot_available")
            self.assertEqual(payload["verification_plan"]["status"], "best_effort_after_apply")
            self.assertIsNone(payload.get("receipt_out"))
            self.assertFalse(mock_post.called)

    def test_dm_send_apply_with_ack_no_snapshot_calls_provider(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env = self._write_env(d)
            self._write_user_token(d)

            buf = io.StringIO()
            with patch("x_api_tool.commands.dm._post_json_with_backoff", return_value=_DummyResponse(status_code=200)) as mock_post:
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            str(env),
                            "--apply",
                            "--yes",
                            "--ack-no-snapshot",
                            "dm",
                            "send",
                            "--to-user-id",
                            "123",
                            "--message",
                            "Hello",
                        ]
                    )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertFalse(payload.get("refused", False))
            self.assertEqual(payload["receipt"]["before_state"]["status"], "no_snapshot_available")
            self.assertTrue(payload["receipt"]["no_snapshot_approval"]["acknowledged"])
            self.assertTrue(mock_post.called)
