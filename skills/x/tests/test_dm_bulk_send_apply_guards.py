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
        self.headers: dict[str, str] = {}

    def json(self) -> dict:
        return {}


class TestDmBulkSendApplyGuards(unittest.TestCase):
    def _write_env(self, d: str) -> Path:
        env = Path(d) / ".env"
        env.write_text("X_API_BASE_URL=https://api.x.com/2\nX_API_TIMEOUT_S=30\n", encoding="utf-8")
        return env

    def _write_user_token(self, d: str) -> None:
        state_dir = Path(d) / ".state"
        state_dir.mkdir(parents=True, exist_ok=True)
        (state_dir / "token.json").write_text('{"access_token":"TEST_TOKEN"}\n', encoding="utf-8")

    def _write_opt_out(self, d: str, recipients: list[str]) -> None:
        state_dir = Path(d) / ".state"
        state_dir.mkdir(parents=True, exist_ok=True)
        recs = [{"recipient": r, "recipient_norm": r.lower() if not r.isdigit() else r} for r in recipients]
        (state_dir / "dm_opt_out.json").write_text(
            json.dumps({"version": 1, "updated_at_utc": None, "recipients": recs}, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    def _write_csv(self, d: str, *, recipient: str = "999") -> Path:
        csv_path = Path(d) / "job.csv"
        csv_path.write_text(
            "recipient,message,intent_evidence\n" f"{recipient},Hi,Asked for info\n",
            encoding="utf-8",
        )
        return csv_path

    def _write_plan_in(self, d: str, plan_obj: dict) -> Path:
        p = Path(d) / "plan.json"
        p.write_text(json.dumps(plan_obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return p

    def test_plan_in_apply_revalidates_opt_out_and_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env = self._write_env(d)
            self._write_user_token(d)
            self._write_opt_out(d, ["123"])
            csv_path = self._write_csv(d, recipient="999")

            opt_out_line = "Reply STOP to opt out."
            plan_in = self._write_plan_in(
                d,
                {
                    "tool": "x-api-tool",
                    "version": "0.1.0",
                    "generated_at_utc": "2026-02-26T00:00:00Z",
                    "env_fingerprint": "https://api.x.com/2",
                    "kind": "dm.bulk_send",
                    "csv": str(csv_path),
                    "count": 1,
                    "opt_out_line": opt_out_line,
                    "items": [
                        {
                            "recipient": "123",
                            "recipient_norm": "123",
                            "recipient_is_id": True,
                            "message": "Hi\n\n" + opt_out_line,
                            "intent_evidence": "",
                        }
                    ],
                    "dry_run": True,
                },
            )

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env),
                        "--apply",
                        "--yes",
                        "--plan-in",
                        str(plan_in),
                        "dm",
                        "bulk-send",
                        "--csv",
                        str(csv_path),
                        "--opt-out-line",
                        opt_out_line,
                        "--min-delay-s",
                        "0",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload.get("refused"))
            self.assertIn("reasons", payload)

    def test_apply_refuses_before_sends_or_pacing(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env = self._write_env(d)
            self._write_user_token(d)
            self._write_opt_out(d, [])
            csv_path = self._write_csv(d, recipient="999")

            opt_out_line = "Reply STOP to opt out."
            plan_in = self._write_plan_in(
                d,
                {
                    "tool": "x-api-tool",
                    "version": "0.1.0",
                    "generated_at_utc": "2026-02-26T00:00:00Z",
                    "env_fingerprint": "https://api.x.com/2",
                    "kind": "dm.bulk_send",
                    "csv": str(csv_path),
                    "count": 2,
                    "opt_out_line": opt_out_line,
                    "items": [
                        {
                            "recipient": "123",
                            "recipient_norm": "123",
                            "recipient_is_id": True,
                            "message": "Hi\n\n" + opt_out_line,
                            "intent_evidence": "Asked for info",
                        },
                        {
                            "recipient": "456",
                            "recipient_norm": "456",
                            "recipient_is_id": True,
                            "message": "Hi again\n\n" + opt_out_line,
                            "intent_evidence": "Follow up requested",
                        },
                    ],
                    "dry_run": True,
                },
            )

            buf = io.StringIO()
            with patch("x_api_tool.commands.dm._post_json_with_backoff", return_value=_DummyResponse(status_code=200)) as mock_post:
                with patch("x_api_tool.commands.dm.time.monotonic", side_effect=[0.0, 0.0, 0.0, 0.0]):
                    with patch("x_api_tool.commands.dm.time.sleep") as mock_sleep:
                        with redirect_stdout(buf):
                            rc = main(
                                [
                                    "--output",
                                    "json",
                                    "--env-file",
                                    str(env),
                                    "--apply",
                                    "--yes",
                                    "--plan-in",
                                    str(plan_in),
                                    "dm",
                                    "bulk-send",
                                    "--csv",
                                    str(csv_path),
                                    "--opt-out-line",
                                    opt_out_line,
                                    "--min-delay-s",
                                    "0.1",
                                ]
                            )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertFalse(payload["dry_run"])
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["plan"]["before_state"]["status"], "no_snapshot_available")
            self.assertEqual(payload["verification_plan"]["status"], "best_effort_after_apply")
            self.assertFalse(mock_post.called)
            self.assertFalse(mock_sleep.called)

    def test_apply_with_ack_no_snapshot_sends_and_paces(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env = self._write_env(d)
            self._write_user_token(d)
            self._write_opt_out(d, [])
            csv_path = self._write_csv(d, recipient="999")

            opt_out_line = "Reply STOP to opt out."
            plan_in = self._write_plan_in(
                d,
                {
                    "tool": "x-api-tool",
                    "version": "0.1.0",
                    "generated_at_utc": "2026-02-26T00:00:00Z",
                    "env_fingerprint": "https://api.x.com/2",
                    "kind": "dm.bulk_send",
                    "csv": str(csv_path),
                    "count": 2,
                    "opt_out_line": opt_out_line,
                    "items": [
                        {
                            "recipient": "123",
                            "recipient_norm": "123",
                            "recipient_is_id": True,
                            "message": "Hi\n\n" + opt_out_line,
                            "intent_evidence": "Asked for info",
                        },
                        {
                            "recipient": "456",
                            "recipient_norm": "456",
                            "recipient_is_id": True,
                            "message": "Hi again\n\n" + opt_out_line,
                            "intent_evidence": "Follow up requested",
                        },
                    ],
                    "dry_run": True,
                },
            )

            buf = io.StringIO()
            with patch("x_api_tool.commands.dm._post_json_with_backoff", return_value=_DummyResponse(status_code=200)) as mock_post:
                with patch("x_api_tool.commands.dm.time.sleep") as mock_sleep:
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
                                "--plan-in",
                                str(plan_in),
                                "dm",
                                "bulk-send",
                                "--csv",
                                str(csv_path),
                                "--opt-out-line",
                                opt_out_line,
                                "--min-delay-s",
                                "0.1",
                            ]
                        )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertFalse(payload.get("refused", False))
            self.assertEqual(payload["receipt"]["before_state"]["status"], "no_snapshot_available")
            self.assertTrue(payload["receipt"]["no_snapshot_approval"]["acknowledged"])
            self.assertEqual(mock_post.call_count, 2)
            mock_sleep.assert_called_once_with(0.1)
