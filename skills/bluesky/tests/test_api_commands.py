from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from bluesky_safe_agent_cli.cli import main


class TestApiCommands(unittest.TestCase):
    def test_api_ops_list_returns_inventory_rows(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["--output", "json", "api", "ops", "list", "--namespace", "app.bsky", "--group", "feed"])
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertGreater(payload["count"], 0)
        for row in payload["ops"]:
            self.assertEqual(row["namespace"], "app.bsky")
            self.assertEqual(row["group"], "feed")

    def test_query_operation_builds_dry_run_plan(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(
                [
                    "--output",
                    "json",
                    "api",
                    "app-bsky-actor-get-profile",
                    "--query",
                    "actor=alice.bsky.social",
                ]
            )
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["operation"]["lexicon_id"], "app.bsky.actor.getProfile")

    def test_procedure_operation_builds_dry_run_plan(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(
                [
                    "--output",
                    "json",
                    "--no-artifacts",
                    "api",
                    "com-atproto-server-create-session",
                    "--body",
                    "identifier=alice.bsky.social",
                    "--body",
                    "password=app-password",
                ]
            )
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["operation"]["lexicon_id"], "com.atproto.server.createSession")
        self.assertEqual(payload["plan"]["inputs"]["body"]["password"], "<redacted>")
        self.assertEqual(payload["plan"]["before_state"]["status"], "no_snapshot_available")
        self.assertEqual(payload["plan"]["verification_plan"]["status"], "best_effort_after_apply")
        self.assertEqual(payload["plan"]["rollback"]["mode"], "irreversible_and_clearly_labeled")

    def test_write_apply_refuses_without_before_state_or_receipt(self) -> None:
        calls: list[dict[str, object]] = []

        class _FakeClient:
            def request(self, **kwargs):
                calls.append(kwargs)

                class _Response:
                    status = 200
                    headers = {"content-type": "application/json"}
                    url = str(kwargs.get("url") or "")
                    body = b'{"did":"did:plc:123","handle":"alice.bsky.social","accessJwt":"x","refreshJwt":"y"}'

                    @staticmethod
                    def json() -> dict[str, object]:
                        return {
                            "did": "did:plc:123",
                            "handle": "alice.bsky.social",
                            "accessJwt": "x",
                            "refreshJwt": "y",
                        }

                return _Response()

        with tempfile.TemporaryDirectory() as d:
            receipt_path = Path(d) / "receipt.json"
            buf = io.StringIO()
            with patch("bluesky_safe_agent_cli.commands.api._client", return_value=_FakeClient()):
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--live",
                            "--apply",
                            "--receipt-out",
                            str(receipt_path),
                            "api",
                            "com-atproto-server-create-session",
                            "--body",
                            "identifier=alice.bsky.social",
                            "--body",
                            "password=app-password",
                        ]
                    )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertFalse(payload["dry_run"])
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["plan"]["before_state"]["status"], "no_snapshot_available")
            self.assertEqual(payload["verification_plan"]["status"], "best_effort_after_apply")
            self.assertEqual(payload["rollback"]["mode"], "irreversible_and_clearly_labeled")
            self.assertFalse(payload["rollback"]["requires_ack_irreversible"])
            self.assertFalse(receipt_path.exists())
            self.assertFalse(calls)

    def test_subscription_operation_builds_dry_run_plan(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["--output", "json", "api", "com-atproto-sync-subscribe-repos"])
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["operation"]["kind"], "subscription")

    def test_unknown_plan_in_argument_is_rejected(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(
                [
                    "--output",
                    "json",
                    "--plan-in",
                    "plan.json",
                    "api",
                    "app-bsky-actor-get-profile",
                    "--query",
                    "actor=alice.bsky.social",
                ]
            )
            self.assertEqual(rc, 1)
        payload = json.loads(buf.getvalue())
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("invalid choice", payload["error"])
        self.assertIn("plan.json", payload["error"])
