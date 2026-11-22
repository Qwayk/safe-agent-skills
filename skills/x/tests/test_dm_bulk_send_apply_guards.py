from __future__ import annotations

import tempfile
import unittest
from unittest.mock import patch

import requests

from .test_dm_send_apply_offline import APPLY, XReplies


class TestDmBulkSendApplyGuards(unittest.TestCase):
    def command(self, x: XReplies) -> tuple[str, ...]:
        csv = x.root / "recipients.csv"
        csv.write_text(
            "recipient,message,intent_evidence\n"
            "123,First reply,Asked for first information on X\n"
            "456,Second reply,Asked for another topic on X\n"
        )
        return ("dm", "bulk-send", "--csv", str(csv), "--opt-out-line", "Reply STOP.", "--min-delay-s", "0.1")

    def test_apply_revalidates_opt_out(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            x = XReplies(directory)
            command = self.command(x)
            plan = str(x.root / "reviewed.json")
            with patch.object(requests.Session, "send", side_effect=x.reply):
                self.assertEqual(x.call("--live", "--plan-out", plan, *command)[0], 0)
                self.assertEqual(x.call("dm", "opt-out", "add", "--recipient", "example_second")[0], 0)
                code, data = x.call(*APPLY, "--plan-in", plan, *command)
            self.assertEqual(code, 0)
            self.assertTrue(data["refused"])
            self.assertFalse(any(method == "POST" for method, _ in x.calls))

    def test_missing_approval_stops_before_sends_or_pacing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            x = XReplies(directory)
            command = self.command(x)
            with patch.object(requests.Session, "send", side_effect=x.reply), patch("x_api_tool.commands.dm.time.sleep") as sleep:
                code, data = x.call("--apply", "--yes", *command)
            self.assertEqual(code, 0)
            self.assertTrue(data["refused"])
            self.assertEqual(x.calls, [])
            sleep.assert_not_called()

    def test_apply_saves_partial_receipt_and_stops_on_rejection(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            x = XReplies(directory)
            command = self.command(x)
            plan = str(x.root / "reviewed.json")
            x.dm_results = [201, 403]
            with patch.object(requests.Session, "send", side_effect=x.reply), patch("x_api_tool.commands.dm.time.sleep") as sleep:
                self.assertEqual(x.call("--live", "--plan-out", plan, *command)[0], 0)
                code, data = x.call(*APPLY, "--plan-in", plan, *command)
            self.assertEqual(code, 1)
            self.assertFalse(data["ok"])
            self.assertEqual([row["status"] for row in data["receipt"]["results"]], ["accepted", "rejected"])
            sleep.assert_called_once_with(0.1)
