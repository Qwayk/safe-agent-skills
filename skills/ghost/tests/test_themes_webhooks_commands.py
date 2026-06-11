import json
import os
import tempfile
import unittest

from ghost_api_tool.commands.theme import cmd_theme_activate
from ghost_api_tool.commands.webhook import cmd_webhook_create, cmd_webhook_delete


class _Out:
    def __init__(self) -> None:
        self.items = []

    def print(self, obj):
        self.items.append(obj)


class ThemesWebhooksCommandTests(unittest.TestCase):
    def test_theme_activate_requires_ack(self) -> None:
        class FakeApi:
            def themes_activate(self, _name):
                raise AssertionError("themes_activate should not be called when ack is missing")

        class Args:
            name = "casper"

        out = _Out()
        ctx = {"apply": True, "out": out, "ack_theme_change": False, "_api": FakeApi()}
        rc = cmd_theme_activate(Args(), ctx)
        self.assertEqual(rc, 0)
        self.assertTrue(out.items[0]["refused"])

    def test_webhook_create_requires_ack_and_does_not_write_ledger(self) -> None:
        class Args:
            event = "post.added"
            target_url = "https://example.com/hook/"
            name = None
            api_version = None
            secret_file = None

        with tempfile.TemporaryDirectory() as td:
            env_file = os.path.join(td, ".env")
            with open(env_file, "w", encoding="utf-8") as f:
                f.write("x=y\n")

            out = _Out()
            ctx = {"apply": True, "out": out, "ack_no_verify": False, "env_file": env_file, "run_id": "r1"}
            rc = cmd_webhook_create(Args(), ctx)
            self.assertEqual(rc, 0)
            self.assertTrue(out.items[0]["refused"])
            self.assertEqual(out.items[0]["recovery"]["end_state"], "irreversible_and_clearly_labeled")
            self.assertEqual(out.items[0]["recovery"]["strategy"], "ledger_only_proof")
            self.assertFalse(out.items[0]["recovery"]["rollback_ready"])

            ledger = os.path.join(td, ".state", "webhooks", "index.jsonl")
            self.assertFalse(os.path.exists(ledger))

    def test_webhook_create_writes_ledger_and_redacts_secret(self) -> None:
        class FakeApi:
            def webhooks_create(self, payload):
                # Ensure secret is passed to the API (but never printed/persisted).
                wh = (payload.get("webhooks") or [{}])[0]
                assert wh.get("secret") == "SECRET"
                return {
                    "webhooks": [
                        {
                            "id": "w1",
                            "event": wh.get("event"),
                            "target_url": wh.get("target_url"),
                            "name": wh.get("name"),
                            "secret": "RESPONSE_SECRET",
                            "api_version": "v6",
                            "integration_id": "i1",
                        }
                    ]
                }

        class Args:
            event = "post.added"
            target_url = "https://example.com/hook/"
            name = "x"
            api_version = None
            secret_file = None

        with tempfile.TemporaryDirectory() as td:
            env_file = os.path.join(td, ".env")
            with open(env_file, "w", encoding="utf-8") as f:
                f.write("x=y\n")

            secret_path = os.path.join(td, "secret.txt")
            with open(secret_path, "w", encoding="utf-8") as f:
                f.write("SECRET\n")

            Args.secret_file = secret_path

            out = _Out()
            ctx = {
                "apply": True,
                "out": out,
                "ack_no_verify": True,
                "env_file": env_file,
                "run_id": "r1",
                "_api": FakeApi(),
                "audit": type("_Audit", (), {"write": lambda *a, **k: None})(),
            }
            rc = cmd_webhook_create(Args(), ctx)
            self.assertEqual(rc, 0)
            obj = out.items[0]
            self.assertTrue(obj["ok"])
            self.assertNotIn("secret", json.dumps(obj))
            self.assertEqual(obj["recovery"]["end_state"], "irreversible_and_clearly_labeled")
            self.assertEqual(obj["recovery"]["strategy"], "ledger_only_proof")
            self.assertFalse(obj["recovery"]["rollback_ready"])
            self.assertEqual(obj["rollback_plan"], None)
            self.assertEqual(obj["backups"], [])

            ledger = os.path.join(td, ".state", "webhooks", "index.jsonl")
            self.assertTrue(os.path.exists(ledger))
            with open(ledger, encoding="utf-8") as f:
                row = json.loads(f.readline())
            self.assertEqual(row["action"], "create")
            self.assertEqual(row["webhook_id"], "w1")
            self.assertNotIn("secret", json.dumps(row))
            self.assertEqual(os.path.realpath(obj["recovery"]["ledger_path"]), os.path.realpath(ledger))
            self.assertEqual(obj["recovery"]["ledger_rows"][0]["webhook_id"], "w1")

    def test_webhook_delete_writes_ledger(self) -> None:
        class _Resp:
            status = 204

        class FakeApi:
            def webhooks_delete(self, _id):
                return _Resp()

        class Args:
            id = "w1"

        with tempfile.TemporaryDirectory() as td:
            env_file = os.path.join(td, ".env")
            with open(env_file, "w", encoding="utf-8") as f:
                f.write("x=y\n")

            out = _Out()
            ctx = {
                "apply": True,
                "out": out,
                "ack_no_verify": True,
                "env_file": env_file,
                "run_id": "r1",
                "_api": FakeApi(),
                "audit": type("_Audit", (), {"write": lambda *a, **k: None})(),
            }
            rc = cmd_webhook_delete(Args(), ctx)
            self.assertEqual(rc, 0)
            obj = out.items[0]
            self.assertEqual(obj["recovery"]["end_state"], "irreversible_and_clearly_labeled")
            self.assertEqual(obj["recovery"]["strategy"], "ledger_only_proof")
            self.assertFalse(obj["recovery"]["rollback_ready"])
            self.assertEqual(obj["rollback_plan"], None)
            self.assertEqual(obj["backups"], [])

            ledger = os.path.join(td, ".state", "webhooks", "index.jsonl")
            self.assertTrue(os.path.exists(ledger))
            self.assertEqual(os.path.realpath(obj["recovery"]["ledger_path"]), os.path.realpath(ledger))
