import csv
import os
import tempfile
import unittest
from typing import Any
from unittest.mock import patch

from ghost_api_tool.commands.jobs import cmd_jobs_run


class _Out:
    def __init__(self):
        self.items = []

    def print(self, obj):
        self.items.append(obj)


class _Audit:
    def __init__(self):
        self.events = []

    def write(self, event, payload):
        self.events.append((event, payload))


class JobsOutputTests(unittest.TestCase):
    def test_jobs_emits_single_summary_object(self):
        with tempfile.TemporaryDirectory() as td:
            csv_path = os.path.join(td, "jobs.csv")
            with open(csv_path, "w", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(
                    f,
                    fieldnames=["action", "slug", "file", "to", "captions_file"],
                )
                w.writeheader()
                w.writerow({"action": "post.patch", "slug": "a", "file": "x.json"})
                w.writerow({"action": "post.set-status", "slug": "b", "to": "draft"})

            class Args:
                file = csv_path
                limit = None

            ctx: dict[str, Any] = {"apply": False, "yes": False, "out": _Out(), "audit": _Audit()}

            def fake_patch(args, ctx):
                ctx["out"].print({"ok": "patch"})
                return 0

            def fake_set_status(args, ctx):
                ctx["out"].print({"ok": "set-status"})
                return 0

            with patch("ghost_api_tool.commands.jobs.post_cmd.cmd_post_patch", fake_patch), patch(
                "ghost_api_tool.commands.jobs.post_cmd.cmd_post_set_status", fake_set_status
            ):
                rc = cmd_jobs_run(Args(), ctx)

            self.assertEqual(rc, 0)
            self.assertEqual(len(ctx["out"].items), 1)
            summary = ctx["out"].items[0]
            self.assertEqual(summary["count"], 2)
            self.assertEqual(summary["errors"], 0)
            self.assertEqual(len(summary["results"]), 2)
            self.assertEqual(ctx["audit"].events[0][0], "jobs.run")

    def test_jobs_stops_on_first_error_and_returns_nonzero(self):
        with tempfile.TemporaryDirectory() as td:
            csv_path = os.path.join(td, "jobs.csv")
            with open(csv_path, "w", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, fieldnames=["action", "slug", "to"])
                w.writeheader()
                w.writerow({"action": "post.set-status", "slug": "a", "to": "draft"})
                w.writerow({"action": "post.set-status", "slug": "b", "to": "draft"})

            class Args:
                file = csv_path
                limit = None

            ctx: dict[str, Any] = {"apply": False, "yes": False, "out": _Out(), "audit": _Audit()}

            def ok(args, ctx):
                ctx["out"].print({"ok": True})
                return 0

            calls = {"n": 0}

            def handler(args, ctx):
                calls["n"] += 1
                if calls["n"] == 1:
                    return ok(args, ctx)
                raise RuntimeError("boom")

            with patch("ghost_api_tool.commands.jobs.post_cmd.cmd_post_set_status", handler):
                rc = cmd_jobs_run(Args(), ctx)

            self.assertEqual(rc, 1)
            summary = ctx["out"].items[0]
            self.assertEqual(summary["count"], 2)
            self.assertEqual(summary["errors"], 1)
            self.assertEqual(len(summary["results"]), 2)
