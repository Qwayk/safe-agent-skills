from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch
from urllib.parse import urlsplit

import requests

from x_api_tool.cli import main


class XReplies:
    def __init__(self, directory: str) -> None:
        self.root = Path(directory)
        self.env = self.root / ".env"
        self.env.write_text("X_API_BASE_URL=https://api.x.com/2\n")
        (self.root / ".state").mkdir()
        (self.root / ".state/token.json").write_text('{"access_token":"fixture-token"}\n')
        self.calls: list[tuple[str, str]] = []
        self.sender = "42"
        self.dm_status = 201
        self.dm_results: list[int] = []
        self.post_status = 201
        self.post_read_ok = True

    def call(self, *args: str) -> tuple[int, dict]:
        output = io.StringIO()
        with redirect_stdout(output):
            code = main(["--no-artifacts", "--env-file", str(self.env), *args])
        return code, json.loads(output.getvalue())

    def reply(self, request: requests.PreparedRequest, **kwargs) -> requests.Response:
        path = urlsplit(str(request.url)).path
        method = str(request.method)
        self.calls.append((method, path))
        assert request.headers.get("Authorization") == "Bearer fixture-token"
        status = 200
        if path == "/2/users/me":
            data = {"data": {"id": self.sender, "username": "example_sender"}}
        elif path.startswith("/2/users/"):
            target = path.split("/")[-1]
            user_ids = {"example_first": "123", "example_second": "456"}
            user_id = user_ids.get(target, target)
            username = next((name for name, uid in user_ids.items() if uid == user_id), "example_user")
            data = {"data": {"id": user_id, "username": username}}
        elif method == "POST" and path.startswith("/2/dm_conversations/"):
            status = self.dm_results.pop(0) if self.dm_results else self.dm_status
            data = {"data": {"dm_event_id": "99"}} if status == 201 else {"detail": "Example refusal"}
        elif method == "POST" and path == "/2/tweets":
            status = self.post_status
            data = {"data": {"id": "89", "text": "Sample"}} if status == 201 else {"detail": "Example error"}
        elif path == "/2/tweets/89":
            data = {"data": {"id": "89", "author_id": self.sender}} if self.post_read_ok else {"data": {}}
        else:
            raise AssertionError((method, path))
        reply = requests.Response()
        reply.url = str(request.url)
        reply.status_code = status
        reply._content = json.dumps(data).encode()
        return reply


SEND = (
    "dm", "send", "--to-user-id", "123", "--message", "Sample",
    "--intent-evidence", "Asked for this on X", "--opt-out-line", "Reply STOP to opt out.",
)
APPLY = ("--apply", "--yes", "--ack-no-snapshot")


class TestDmSendApplyOffline(unittest.TestCase):
    def test_no_snapshot_refuses_before_provider_call(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            x = XReplies(directory)
            with patch.object(requests.Session, "send", side_effect=x.reply):
                code, data = x.call("--apply", "--yes", *SEND)
            self.assertEqual(code, 0)
            self.assertTrue(data["refused"])
            self.assertEqual(data["plan"]["before_state"]["status"], "no_snapshot_available")
            self.assertEqual(x.calls, [])

    def test_reviewed_single_dm_reports_acceptance_and_rejection(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            x = XReplies(directory)
            plan = str(x.root / "approved.json")
            with patch.object(requests.Session, "send", side_effect=x.reply):
                self.assertEqual(x.call("--live", "--plan-out", plan, *SEND)[0], 0)
                self.assertTrue(x.call(*APPLY, *SEND)[1]["refused"])
                x.sender = "other-account"
                self.assertTrue(x.call(*APPLY, "--plan-in", plan, *SEND)[1]["refused"])
                self.assertFalse(any(method == "POST" for method, _ in x.calls))
                x.sender = "42"
                x.dm_status = 403
                code, rejected = x.call(*APPLY, "--plan-in", plan, *SEND)
                self.assertEqual(code, 1)
                self.assertFalse(rejected["receipt"]["verification"]["ok"])
                self.assertEqual(rejected["receipt"]["results"][0]["status"], "rejected")
                x.dm_status = 200
                code, unconfirmed = x.call(*APPLY, "--plan-in", plan, *SEND)
                self.assertEqual(code, 1)
                self.assertEqual(unconfirmed["receipt"]["results"][0]["status"], "unconfirmed")
                x.dm_status = 201
                code, accepted = x.call(*APPLY, "--plan-in", plan, *SEND)
            self.assertEqual(code, 0)
            self.assertEqual(accepted["receipt"]["results"][0]["dm_event_id"], "99")
            self.assertTrue(accepted["receipt"]["no_snapshot_approval"]["acknowledged"])

    def test_single_dm_uses_consent_and_the_opt_out_ledger(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            x = XReplies(directory)
            with patch.object(requests.Session, "send", side_effect=x.reply):
                code, preview = x.call(*SEND[:6])
                self.assertEqual(code, 0)
                self.assertTrue(preview["refused"])
                plan = str(x.root / "approved.json")
                self.assertEqual(x.call("--live", "--plan-out", plan, *SEND)[0], 0)
                self.assertEqual(x.call("dm", "opt-out", "add", "--recipient", "example_first")[0], 0)
                code, result = x.call(*APPLY, "--plan-in", plan, *SEND)
            self.assertEqual(code, 0)
            self.assertTrue(result["refused"])
            self.assertFalse(any(method == "POST" for method, _ in x.calls))
