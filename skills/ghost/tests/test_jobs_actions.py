import csv
import json
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


class JobsActionsTests(unittest.TestCase):
    def test_jobs_routes_replace_many_actions(self):
        with tempfile.TemporaryDirectory() as td:
            bodylex_map = os.path.join(td, "bodylex.json")
            bodymob_map = os.path.join(td, "bodymob.json")
            with open(bodylex_map, "w", encoding="utf-8") as f:
                json.dump({"a": {"new_src": "a", "caption": "x"}}, f)
            with open(bodymob_map, "w", encoding="utf-8") as f:
                json.dump({"b": {"new_src": "b", "caption": "y"}}, f)

            csv_path = os.path.join(td, "jobs.csv")
            with open(csv_path, "w", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(
                    f,
                    fieldnames=["action", "id", "map", "diff", "allow_published", "require_current"],
                )
                w.writeheader()
                w.writerow(
                    {
                        "action": "post.bodylex.image.replace-many",
                        "id": "1",
                        "map": bodylex_map,
                        "diff": "1",
                        "allow_published": "1",
                        "require_current": "",
                    }
                )
                w.writerow(
                    {
                        "action": "post.bodymob.image.replace-many",
                        "id": "2",
                        "map": bodymob_map,
                        "diff": "",
                        "allow_published": "1",
                        "require_current": "",
                    }
                )

            class Args:
                file = csv_path
                limit = None

            ctx: dict[str, Any] = {"apply": False, "yes": False, "out": _Out(), "audit": _Audit()}
            seen = {"bodylex": None, "bodymob": None}

            def fake_bodylex(args, ctx):
                seen["bodylex"] = {"id": args.id, "map": args.map, "diff": args.diff, "allow_published": args.allow_published}
                ctx["out"].print({"ok": "bodylex"})
                return 0

            def fake_bodymob(args, ctx):
                seen["bodymob"] = {"id": args.id, "map": args.map, "diff": args.diff, "allow_published": args.allow_published}
                ctx["out"].print({"ok": "bodymob"})
                return 0

            with patch("ghost_api_tool.commands.jobs.bodylex_cmd.cmd_bodylex_image_replace_many", fake_bodylex), patch(
                "ghost_api_tool.commands.jobs.bodymob_cmd.cmd_bodymob_image_replace_many",
                fake_bodymob,
            ):
                rc = cmd_jobs_run(Args(), ctx)

            self.assertEqual(rc, 0)
            self.assertEqual(seen["bodylex"]["id"], "1")
            self.assertEqual(seen["bodylex"]["map"], bodylex_map)
            self.assertTrue(seen["bodylex"]["diff"])
            self.assertTrue(seen["bodylex"]["allow_published"])
            self.assertEqual(seen["bodymob"]["id"], "2")
            self.assertEqual(seen["bodymob"]["map"], bodymob_map)
            self.assertFalse(seen["bodymob"]["diff"])
            self.assertTrue(seen["bodymob"]["allow_published"])

