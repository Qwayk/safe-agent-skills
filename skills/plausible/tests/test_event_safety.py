from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace

from plausible_api_tool.commands.event import cmd_event_send
from plausible_api_tool.output import Output


class _Audit:
    def write(self, *_args, **_kwargs) -> None:
        return


class TestEventSafety(unittest.TestCase):
    def test_dry_run_refuses_without_apply(self) -> None:
        args = SimpleNamespace(
            name="test_event",
            url="https://example.com/",
            domain=None,
            referrer=None,
            revenue_currency=None,
            revenue_amount=None,
            allow_non_default_domain=False,
            allow_url_host_mismatch=False,
            prop=[],
            interactive=False,
        )
        ctx = {
            "cfg": SimpleNamespace(site_id="example.com"),
            "apply": False,
            "yes": False,
            "ack_irreversible": False,
            "plan_out": None,
            "receipt_out": None,
            "out": Output(mode="json"),
            "audit": _Audit(),
        }
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_event_send(args, ctx)
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["refused"])
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["risk_level"], "irreversible")
        self.assertIn("plan", payload)

    def test_dry_run_recovery_contract_for_event_send(self) -> None:
        args = SimpleNamespace(
            name="test_event",
            url="https://example.com/",
            domain=None,
            referrer=None,
            revenue_currency=None,
            revenue_amount=None,
            allow_non_default_domain=False,
            allow_url_host_mismatch=False,
            prop=[],
            interactive=False,
        )
        ctx = {
            "cfg": SimpleNamespace(site_id="example.com"),
            "apply": False,
            "yes": False,
            "ack_irreversible": False,
            "plan_out": None,
            "receipt_out": None,
            "out": Output(mode="json"),
            "audit": _Audit(),
        }
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_event_send(args, ctx)
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        recovery = payload["plan"]["recovery"]
        self.assertEqual(recovery["end_state"], "irreversible_and_clearly_labeled")
        self.assertEqual(recovery["strategy"], "no_inverse")
        self.assertFalse(recovery["rollback_ready"])
        self.assertEqual(payload["plan"]["before_state"]["status"], "no_snapshot_available")
        self.assertNotIn("before_state_path", payload["plan"])

    def test_apply_is_blocked_for_event_send(self) -> None:
        args = SimpleNamespace(
            name="test_event",
            url="https://example.com/",
            domain=None,
            referrer=None,
            revenue_currency=None,
            revenue_amount=None,
            allow_non_default_domain=False,
            allow_url_host_mismatch=False,
            prop=[],
            interactive=False,
        )
        ctx = {
            "cfg": SimpleNamespace(site_id="example.com"),
            "apply": True,
            "yes": False,
            "ack_irreversible": True,
            "plan_out": None,
            "receipt_out": None,
            "out": Output(mode="json"),
            "audit": _Audit(),
        }
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_event_send(args, ctx)
        self.assertEqual(rc, 1)
        payload = json.loads(buf.getvalue())
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "SafetyError")
        self.assertEqual(payload["risk_level"], "irreversible")
        self.assertIn("--yes", payload["error"])

    def test_apply_requires_ack_irreversible(self) -> None:
        args = SimpleNamespace(
            name="test_event",
            url="https://example.com/",
            domain=None,
            referrer=None,
            revenue_currency=None,
            revenue_amount=None,
            allow_non_default_domain=False,
            allow_url_host_mismatch=False,
            prop=[],
            interactive=False,
        )
        ctx = {
            "cfg": SimpleNamespace(site_id="example.com"),
            "apply": True,
            "yes": True,
            "ack_irreversible": False,
            "plan_out": None,
            "receipt_out": None,
            "out": Output(mode="json"),
            "audit": _Audit(),
            "http": None,
        }
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_event_send(args, ctx)
        self.assertEqual(rc, 1)
        payload = json.loads(buf.getvalue())
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "SafetyError")
        self.assertIn("ack-irreversible", payload["error"])

    def test_refuses_pii_props_in_dry_run_and_redacts(self) -> None:
        args = SimpleNamespace(
            name="test_event",
            url="https://example.com/",
            domain=None,
            referrer=None,
            revenue_currency=None,
            revenue_amount=None,
            allow_non_default_domain=False,
            allow_url_host_mismatch=False,
            prop=[["email", "user@example.com"]],
            interactive=False,
        )
        ctx = {
            "cfg": SimpleNamespace(site_id="example.com"),
            "apply": False,
            "yes": False,
            "ack_irreversible": False,
            "plan_out": None,
            "receipt_out": None,
            "out": Output(mode="json"),
            "audit": _Audit(),
        }
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_event_send(args, ctx)
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["refused"])
        self.assertTrue(payload["plan"]["proposed_changes"][0]["payload"]["props"]["redacted"])
        self.assertNotIn("user@example.com", buf.getvalue())

    def test_apply_refuses_domain_mismatch_without_allow_flag(self) -> None:
        args = SimpleNamespace(
            name="test_event",
            url="https://example.com/",
            domain="other.example",
            referrer=None,
            revenue_currency=None,
            revenue_amount=None,
            allow_non_default_domain=False,
            allow_url_host_mismatch=True,
            prop=[],
            interactive=False,
        )
        ctx = {
            "cfg": SimpleNamespace(site_id="example.com"),
            "apply": True,
            "yes": True,
            "ack_irreversible": True,
            "plan_out": None,
            "receipt_out": None,
            "out": Output(mode="json"),
            "audit": _Audit(),
            "http": None,
        }
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_event_send(args, ctx)
        self.assertEqual(rc, 1)
        payload = json.loads(buf.getvalue())
        self.assertFalse(payload["ok"])

    def test_plan_out_writes_plan_json(self) -> None:
        args = SimpleNamespace(
            name="test_event",
            url="https://example.com/",
            domain=None,
            referrer=None,
            revenue_currency=None,
            revenue_amount=None,
            allow_non_default_domain=False,
            allow_url_host_mismatch=False,
            prop=[],
            interactive=False,
        )
        with tempfile.TemporaryDirectory() as d:
            plan_path = str(Path(d) / "plan.json")
            ctx = {
                "cfg": SimpleNamespace(site_id="example.com", base_url="https://plausible.local"),
                "apply": False,
                "yes": False,
                "ack_irreversible": False,
                "plan_out": plan_path,
                "receipt_out": None,
                "out": Output(mode="json"),
                "audit": _Audit(),
            }
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_event_send(args, ctx)
            self.assertEqual(rc, 0)
            plan_obj = json.loads(Path(plan_path).read_text(encoding="utf-8"))
            self.assertEqual(plan_obj["tool"], "plausible-api-tool")
            self.assertNotIn("api_key", json.dumps(plan_obj))
            self.assertEqual(plan_obj["recovery"]["end_state"], "irreversible_and_clearly_labeled")
            self.assertEqual(plan_obj["recovery"]["strategy"], "no_inverse")
            self.assertFalse(plan_obj["recovery"]["rollback_ready"])
            self.assertEqual(plan_obj["before_state"]["status"], "no_snapshot_available")
            self.assertNotIn("before_state_path", plan_obj)

    def test_receipt_out_writes_receipt_json(self) -> None:
        args = SimpleNamespace(
            name="test_event",
            url="https://example.com/",
            domain=None,
            referrer=None,
            revenue_currency=None,
            revenue_amount=None,
            allow_non_default_domain=False,
            allow_url_host_mismatch=False,
            prop=[],
            interactive=False,
        )
        with tempfile.TemporaryDirectory() as d:
            receipt_path = str(Path(d) / "receipt.json")
            ctx = {
                "cfg": SimpleNamespace(site_id="example.com", base_url="https://plausible.local"),
                "apply": True,
                "yes": True,
                "ack_irreversible": True,
                "plan_out": None,
                "receipt_out": receipt_path,
                "out": Output(mode="json"),
                "audit": _Audit(),
                "http": None,
            }

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_event_send(args, ctx)
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "SafetyError")
            self.assertIn("before-state", payload["error"])
            self.assertFalse(Path(receipt_path).exists())

    def test_verify_path_supported_with_mocked_stats(self) -> None:
        args = SimpleNamespace(
            name="test_event",
            url="https://example.com/__plausible_api_tool_test/123",
            domain=None,
            referrer=None,
            revenue_currency=None,
            revenue_amount=None,
            allow_non_default_domain=False,
            allow_url_host_mismatch=False,
            prop=[],
            interactive=False,
            verify=True,
            verify_wait_s=0.0,
        )

        class _Cfg:
            site_id = "example.com"
            base_url = "https://plausible.local"
            api_key = "x"

        ctx = {
            "cfg": _Cfg(),
            "apply": True,
            "yes": True,
            "ack_irreversible": True,
            "plan_out": None,
            "receipt_out": None,
            "out": Output(mode="json"),
            "audit": _Audit(),
            "http": None,
        }

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_event_send(args, ctx)
        self.assertEqual(rc, 1)
        payload = json.loads(buf.getvalue())
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "SafetyError")
        self.assertIn("before-state", payload["error"])

    def test_dry_run_plan_includes_referrer_and_revenue(self) -> None:
        args = SimpleNamespace(
            name="test_event",
            url="https://example.com/",
            domain=None,
            referrer="https://example.com/from",
            revenue_currency="USD",
            revenue_amount="9.99",
            allow_non_default_domain=False,
            allow_url_host_mismatch=False,
            prop=[],
            interactive=False,
        )
        ctx = {
            "cfg": SimpleNamespace(site_id="example.com", base_url="https://plausible.local"),
            "apply": False,
            "yes": False,
            "ack_irreversible": False,
            "plan_out": None,
            "receipt_out": None,
            "out": Output(mode="json"),
            "audit": _Audit(),
        }
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_event_send(args, ctx)
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        planned = payload["plan"]["proposed_changes"][0]["payload"]
        self.assertEqual(planned["referrer"], "https://example.com/from")
        self.assertEqual(planned["revenue"]["currency"], "USD")
        self.assertEqual(planned["revenue"]["amount"], "9.99")

    def test_refuses_pii_referrer_and_redacts(self) -> None:
        args = SimpleNamespace(
            name="test_event",
            url="https://example.com/",
            domain=None,
            referrer="https://example.com/?email=user@example.com",
            revenue_currency=None,
            revenue_amount=None,
            allow_non_default_domain=False,
            allow_url_host_mismatch=False,
            prop=[],
            interactive=False,
        )
        ctx = {
            "cfg": SimpleNamespace(site_id="example.com", base_url="https://plausible.local"),
            "apply": False,
            "yes": False,
            "ack_irreversible": False,
            "plan_out": None,
            "receipt_out": None,
            "out": Output(mode="json"),
            "audit": _Audit(),
        }
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_event_send(args, ctx)
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["refused"])
        planned = payload["plan"]["proposed_changes"][0]["payload"]
        self.assertEqual(planned["referrer"]["redacted"], True)
        self.assertNotIn("user@example.com", buf.getvalue())

    def test_revenue_requires_both_fields(self) -> None:
        args = SimpleNamespace(
            name="test_event",
            url="https://example.com/",
            domain=None,
            referrer=None,
            revenue_currency="USD",
            revenue_amount=None,
            allow_non_default_domain=False,
            allow_url_host_mismatch=False,
            prop=[],
            interactive=False,
        )
        ctx = {
            "cfg": SimpleNamespace(site_id="example.com", base_url="https://plausible.local"),
            "apply": False,
            "yes": False,
            "ack_irreversible": False,
            "plan_out": None,
            "receipt_out": None,
            "out": Output(mode="json"),
            "audit": _Audit(),
        }
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_event_send(args, ctx)
        self.assertEqual(rc, 1)
        payload = json.loads(buf.getvalue())
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")
