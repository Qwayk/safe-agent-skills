from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import requests

from .test_dm_send_apply_offline import APPLY, XReplies
from x_api_tool.cli import _audit_command


class TestReviewedXPosts(unittest.TestCase):
    def test_account_and_reviewed_post_flow(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            x = XReplies(directory)
            plan = str(x.root / "reviewed.json")
            preview = ("api", "createPosts", "--body-json", '{"text":"Sample"}')
            with patch.object(requests.Session, "send", side_effect=x.reply):
                code, check = x.call("--live", "auth", "check")
                self.assertEqual(code, 0)
                self.assertEqual(check["account"], {"id": "42", "username": "example_sender"})
                self.assertEqual(x.call("--live", "--plan-out", plan, *preview)[0], 0)
                x.sender = "changed"
                self.assertTrue(x.call(*APPLY, "--plan-in", plan, "api", "createPosts")[1]["refused"])
                self.assertFalse(any(method == "POST" for method, _ in x.calls))
                x.sender = "42"
                saved = Path(plan).read_text()
                changed = json.loads(saved)
                changed["inputs"]["body"]["text"] = "Different post"
                Path(plan).write_text(json.dumps(changed))
                self.assertTrue(x.call(*APPLY, "--plan-in", plan, "api", "createPosts")[1]["refused"])
                self.assertFalse(any(method == "POST" for method, _ in x.calls))
                Path(plan).write_text(saved)
                code, receipt = x.call(*APPLY, "--plan-in", plan, "api", "createPosts")
                self.assertEqual(code, 0, receipt)
                self.assertTrue(receipt["receipt"]["verification"]["ok"])
                self.assertEqual(x.calls[-2:], [("POST", "/2/tweets"), ("GET", "/2/tweets/89")])
                x.post_read_ok = False
                code, unconfirmed = x.call(*APPLY, "--plan-in", plan, "api", "createPosts")
                self.assertEqual(code, 1)
                self.assertFalse(unconfirmed["receipt"]["verification"]["ok"])

    def test_other_message_command_cannot_send_without_the_dm_checks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            x = XReplies(directory)
            with patch.object(requests.Session, "send", side_effect=x.reply):
                code, output = x.call(*APPLY, "api", "createDirectMessagesByParticipantId")
            self.assertEqual(code, 0)
            self.assertTrue(output["refused"])
            self.assertIn("dm send", output["reasons"][0])
            self.assertEqual(x.calls, [])

    def test_oauth_codes_and_callbacks_stay_out_of_audit_commands(self) -> None:
        message = _audit_command(["auth", "pkce", "finish", "--code=fixture", "--redirect-url", "fixture-url"])
        self.assertNotIn("fixture", message)
