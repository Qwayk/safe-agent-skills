from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from plausible_api_tool.commands.sites import (
    cmd_site_custom_props_list,
    cmd_site_custom_props_ensure,
    cmd_site_create,
    cmd_site_delete,
    cmd_site_get,
    cmd_site_goals_list,
    cmd_site_goals_ensure,
    cmd_site_guests_list,
    cmd_site_guests_ensure,
    cmd_site_guests_delete,
    cmd_site_shared_links_ensure,
    cmd_site_list,
    cmd_site_teams_list,
)
from plausible_api_tool.output import Output


class _Audit:
    def write(self, *_args, **_kwargs) -> None:
        return


class TestSitesCommands(unittest.TestCase):
    def _ctx(self, **overrides):
        base = {
            "cfg": SimpleNamespace(site_id="example.com", base_url="https://plausible.local"),
            "http": None,
            "out": Output(mode="json"),
            "audit": _Audit(),
            "apply": False,
            "yes": False,
            "ack_irreversible": False,
            "plan_out": None,
            "receipt_out": None,
        }
        base.update(overrides)
        return base

    def test_site_list_calls_client(self) -> None:
        args = SimpleNamespace(after=None, before=None, limit=100, team_id=None)
        ctx = self._ctx()

        captured = {}

        def fake_list(_self, **kwargs):
            captured.update(kwargs)
            return {"sites": []}

        with patch("plausible_api_tool.commands.sites.PlausibleClient.sites_list", new=fake_list):
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_site_list(args, ctx)
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertIn("response", payload)
        self.assertEqual(captured.get("limit"), 100)

    def test_site_get_defaults_site_id(self) -> None:
        args = SimpleNamespace(site_id=None)
        ctx = self._ctx()

        captured = {}

        def fake_get(_self, site_id):
            captured["site_id"] = site_id
            return {"domain": site_id}

        with patch("plausible_api_tool.commands.sites.PlausibleClient.site_get", new=fake_get):
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_site_get(args, ctx)
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertEqual(captured["site_id"], "example.com")
        self.assertEqual(payload["site_id"], "example.com")

    def test_site_teams_list_calls_client(self) -> None:
        ctx = self._ctx()

        with patch("plausible_api_tool.commands.sites.PlausibleClient.sites_teams_list", return_value={"teams": []}):
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_site_teams_list(SimpleNamespace(), ctx)
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])

    def test_site_goals_list_defaults_site_id(self) -> None:
        args = SimpleNamespace(site_id=None, after=None, before=None, limit=100)
        ctx = self._ctx()

        captured = {}

        def fake_goals_list(_self, *, site_id, after=None, before=None, limit=None):
            captured["site_id"] = site_id
            captured["limit"] = limit
            return {"goals": []}

        with patch("plausible_api_tool.commands.sites.PlausibleClient.site_goals_list", new=fake_goals_list):
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_site_goals_list(args, ctx)
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertEqual(captured["site_id"], "example.com")
        self.assertEqual(captured["limit"], 100)
        self.assertEqual(payload["site_id"], "example.com")

    def test_site_custom_props_list_defaults_site_id(self) -> None:
        args = SimpleNamespace(site_id=None)
        ctx = self._ctx()

        captured = {}

        def fake_list(_self, *, site_id):
            captured["site_id"] = site_id
            return {"custom_properties": []}

        with patch("plausible_api_tool.commands.sites.PlausibleClient.site_custom_props_list", new=fake_list):
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_site_custom_props_list(args, ctx)
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertEqual(captured["site_id"], "example.com")
        self.assertEqual(payload["site_id"], "example.com")

    def test_site_guests_list_defaults_site_id(self) -> None:
        args = SimpleNamespace(site_id=None, after=None, before=None, limit=100)
        ctx = self._ctx()

        captured = {}

        def fake_list(_self, *, site_id, after=None, before=None, limit=None):
            captured["site_id"] = site_id
            captured["limit"] = limit
            return {"guests": []}

        with patch("plausible_api_tool.commands.sites.PlausibleClient.site_guests_list", new=fake_list):
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_site_guests_list(args, ctx)
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertEqual(captured["site_id"], "example.com")
        self.assertEqual(captured["limit"], 100)
        self.assertEqual(payload["site_id"], "example.com")

    def test_site_create_dry_run_refuses_without_apply(self) -> None:
        args = SimpleNamespace(domain="test-domain.com", timezone=None, team_id=None, tracker_config=None, tracker_config_file=None)
        ctx = self._ctx(apply=False, yes=False)

        with patch("plausible_api_tool.commands.sites.PlausibleClient.site_create") as p_create:
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_site_create(args, ctx)
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["dry_run"])
        self.assertTrue(payload["refused"])
        self.assertIn("plan", payload)
        self.assertEqual(payload["plan"]["recovery"]["end_state"], "irreversible_and_clearly_labeled")
        p_create.assert_not_called()

    def test_site_create_apply_requires_yes(self) -> None:
        args = SimpleNamespace(domain="test-domain.com", timezone=None, team_id=None, tracker_config=None, tracker_config_file=None)
        ctx = self._ctx(apply=True, yes=False)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_site_create(args, ctx)
        self.assertEqual(rc, 1)
        payload = json.loads(buf.getvalue())
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "SafetyError")

    def test_site_delete_apply_requires_ack_irreversible(self) -> None:
        args = SimpleNamespace(site_id="test-domain.com")
        ctx = self._ctx(apply=True, yes=True, ack_irreversible=False)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_site_delete(args, ctx)
        self.assertEqual(rc, 1)
        payload = json.loads(buf.getvalue())
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "SafetyError")

    def test_site_shared_links_ensure_dry_run_refused_without_apply(self) -> None:
        args = SimpleNamespace(site_id="example.com", name="Wordpress")
        ctx = self._ctx(apply=False, yes=False)

        with patch("plausible_api_tool.commands.sites.PlausibleClient.site_shared_links_ensure") as p_shared:
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_site_shared_links_ensure(args, ctx)
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["dry_run"])
        self.assertTrue(payload["refused"])
        self.assertIn("plan", payload)
        p_shared.assert_not_called()

    def test_site_shared_links_ensure_apply_is_blocked(self) -> None:
        args = SimpleNamespace(site_id="example.com", name="Wordpress")
        ctx = self._ctx(apply=True, yes=True)

        with patch("plausible_api_tool.commands.sites.PlausibleClient.site_shared_links_ensure") as p_shared:
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_site_shared_links_ensure(args, ctx)
        self.assertEqual(rc, 1)
        payload = json.loads(buf.getvalue())
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "SafetyError")
        self.assertIn("before-state", payload["error"])
        p_shared.assert_not_called()

    def test_site_create_plan_and_receipt_out_write_files(self) -> None:
        args = SimpleNamespace(domain="test-domain.com", timezone=None, team_id=None, tracker_config=None, tracker_config_file=None)
        with tempfile.TemporaryDirectory() as d:
            plan_path = str(Path(d) / "plan.json")
            receipt_path = str(Path(d) / "receipt.json")
            env_file = str(Path(d) / ".env")
            Path(env_file).touch()
            ctx = self._ctx(
                apply=True,
                yes=True,
                ack_irreversible=False,
                plan_out=plan_path,
                receipt_out=receipt_path,
                env_file=env_file,
                http=object(),
            )

            with patch("plausible_api_tool.commands.sites.PlausibleClient.site_create", return_value={"domain": "test-domain.com"}):
                with patch("plausible_api_tool.commands.sites.PlausibleClient.site_get", return_value={"domain": "test-domain.com"}):
                    buf = io.StringIO()
                    with redirect_stdout(buf):
                        rc = cmd_site_create(args, ctx)
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(Path(plan_path).exists())
            self.assertTrue(Path(receipt_path).exists())
            plan_obj = json.loads(Path(plan_path).read_text(encoding="utf-8"))
            receipt_obj = json.loads(Path(receipt_path).read_text(encoding="utf-8"))
            self.assertEqual(plan_obj["tool"], "plausible-api-tool")
            self.assertEqual(receipt_obj["tool"], "plausible-api-tool")
            self.assertNotIn("api_key", json.dumps(plan_obj))
            self.assertNotIn("api_key", json.dumps(receipt_obj))
            self.assertEqual(plan_obj["recovery"]["end_state"], "irreversible_and_clearly_labeled")
            self.assertEqual(plan_obj["recovery"]["strategy"], "no_inverse")
            self.assertFalse(plan_obj["recovery"]["rollback_ready"])
            self.assertEqual(receipt_obj["recovery"]["end_state"], "irreversible_and_clearly_labeled")
            self.assertEqual(receipt_obj["recovery"]["strategy"], "no_inverse")
            self.assertFalse(receipt_obj["recovery"]["rollback_ready"])
            self.assertIn("before_state", plan_obj)
            self.assertIn("before_state", receipt_obj)
            self.assertIn("before_state_path", plan_obj)
            self.assertIn("before_state_path", receipt_obj)
            state_root = Path(env_file).resolve().parent / ".state" / "plausible"
            self.assertEqual(Path(plan_obj["before_state_path"]).parent, state_root)
            self.assertEqual(Path(receipt_obj["before_state_path"]).parent, state_root)
            self.assertTrue(Path(plan_obj["before_state_path"]).exists())
            self.assertTrue(Path(receipt_obj["before_state_path"]).exists())
            self.assertEqual(plan_obj["before_state"]["command"], "site.create")
            self.assertEqual(receipt_obj["before_state"]["command"], "site.create")

    def test_site_create_calls_read_back_get(self) -> None:
        args = SimpleNamespace(domain="test-domain.com", timezone=None, team_id=None, tracker_config=None, tracker_config_file=None)
        ctx = self._ctx(apply=True, yes=True)

        calls = {"get": 0}

        def fake_get(_self, site_id):
            calls["get"] += 1
            return {"domain": site_id}

        with patch("plausible_api_tool.commands.sites.PlausibleClient.site_create", return_value={"domain": "test-domain.com"}):
            with patch("plausible_api_tool.commands.sites.PlausibleClient.site_get", new=fake_get):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cmd_site_create(args, ctx)
        self.assertEqual(rc, 0)
        self.assertGreaterEqual(calls["get"], 1)

    def test_site_goals_ensure_dry_run_contract(self) -> None:
        args = SimpleNamespace(
            site_id=None,
            goal_type="event",
            event_name="purchase",
            page_path=None,
            display_name="Checkout",
        )
        with tempfile.TemporaryDirectory() as d:
            env_file = str(Path(d) / ".env")
            Path(env_file).touch()
            ctx = self._ctx(apply=False, yes=False, env_file=env_file, http=object())

            payload_out = {"id": "goal-1", "goal_type": "event", "event_name": "purchase"}

            with patch("plausible_api_tool.commands.sites.PlausibleClient.site_goal_ensure", return_value=payload_out), patch(
                "plausible_api_tool.commands.sites.PlausibleClient.site_goals_list", return_value={"goals": [{"id": "goal-1", "goal_type": "event", "event_name": "purchase"}]}
            ):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cmd_site_goals_ensure(args, ctx)
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            recovery = payload["plan"]["recovery"]
            self.assertEqual(recovery["end_state"], "rollback_by_inverse_action")
            self.assertFalse(recovery["rollback_ready"])
            self.assertIn("before_state", payload["plan"])
            self.assertIn("before_state_path", payload["plan"])
            self.assertEqual(payload["plan"]["before_state"]["command"], "site.goals.ensure")
            self.assertEqual(payload["plan"]["before_state"]["before_state"]["resource"], "goal")
            self.assertEqual(
                Path(payload["plan"]["before_state_path"]).parent,
                Path(env_file).resolve().parent / ".state" / "plausible",
            )

    def test_site_custom_props_ensure_dry_run_contract(self) -> None:
        args = SimpleNamespace(site_id=None, property="cohort")
        with tempfile.TemporaryDirectory() as d:
            env_file = str(Path(d) / ".env")
            Path(env_file).touch()
            ctx = self._ctx(apply=False, yes=False, env_file=env_file, http=object())

            payload_out = {"property": "cohort"}
            with patch("plausible_api_tool.commands.sites.PlausibleClient.site_custom_prop_ensure", return_value=payload_out), patch(
                "plausible_api_tool.commands.sites.PlausibleClient.site_custom_props_list",
                return_value={"custom_properties": [{"property": "cohort"}]},
            ):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cmd_site_custom_props_ensure(args, ctx)
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            recovery = payload["plan"]["recovery"]
            self.assertEqual(recovery["end_state"], "rollback_by_inverse_action")
            self.assertEqual(recovery["strategy"], "plausible.sites.custom_props.delete")
            self.assertTrue(recovery["rollback_ready"])
            self.assertIn("before_state", payload["plan"])
            self.assertIn("before_state_path", payload["plan"])
            self.assertEqual(payload["plan"]["before_state"]["command"], "site.custom-props.ensure")
            self.assertEqual(payload["plan"]["before_state"]["before_state"]["resource"], "custom_prop")
            self.assertEqual(
                Path(payload["plan"]["before_state_path"]).parent,
                Path(env_file).resolve().parent / ".state" / "plausible",
            )

    def test_site_guests_delete_is_marked_irreversible(self) -> None:
        args = SimpleNamespace(site_id=None, email="guest@example.com")
        with tempfile.TemporaryDirectory() as d:
            env_file = str(Path(d) / ".env")
            Path(env_file).touch()
            ctx = self._ctx(apply=False, yes=False, env_file=env_file, http=object())

            with patch(
                "plausible_api_tool.commands.sites.PlausibleClient.site_guests_list",
                return_value={"guests": [{"email": "guest@example.com"}]},
            ), patch("plausible_api_tool.commands.sites.PlausibleClient.site_guest_delete", return_value={"status": "ok"}):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cmd_site_guests_delete(args, ctx)
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            recovery = payload["plan"]["recovery"]
            self.assertEqual(recovery["end_state"], "irreversible_and_clearly_labeled")
            self.assertFalse(recovery["rollback_ready"])
            self.assertFalse(payload["plan"]["rollback"]["supported"])
            self.assertIn("before_state", payload["plan"])
            self.assertIn("before_state_path", payload["plan"])
            self.assertEqual(payload["plan"]["before_state"]["command"], "site.guests.delete")
            self.assertEqual(
                Path(payload["plan"]["before_state_path"]).parent,
                Path(env_file).resolve().parent / ".state" / "plausible",
            )

    def test_site_guests_delete_becomes_inverse_when_role_is_captured(self) -> None:
        args = SimpleNamespace(site_id=None, email="guest@example.com")
        with tempfile.TemporaryDirectory() as d:
            env_file = str(Path(d) / ".env")
            Path(env_file).touch()
            ctx = self._ctx(apply=False, yes=False, env_file=env_file, http=object())

            with patch(
                "plausible_api_tool.commands.sites.PlausibleClient.site_guests_list",
                return_value={"guests": [{"email": "guest@example.com", "role": "viewer"}]},
            ), patch("plausible_api_tool.commands.sites.PlausibleClient.site_guest_delete", return_value={"status": "ok"}):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cmd_site_guests_delete(args, ctx)
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            recovery = payload["plan"]["recovery"]
            self.assertEqual(recovery["end_state"], "rollback_by_inverse_action")
            self.assertEqual(recovery["strategy"], "plausible.sites.guests.ensure")
            self.assertTrue(recovery["rollback_ready"])
            self.assertTrue(payload["plan"]["rollback"]["supported"])
            self.assertEqual(payload["plan"]["before_state"]["before_state"]["entry"]["role"], "viewer")
            self.assertIn("before_state_path", payload["plan"])

    def test_site_guests_ensure_dry_run_contract(self) -> None:
        args = SimpleNamespace(site_id=None, email="guest@example.com", role="viewer")
        with tempfile.TemporaryDirectory() as d:
            env_file = str(Path(d) / ".env")
            Path(env_file).touch()
            ctx = self._ctx(apply=False, yes=False, env_file=env_file, http=object())

            with patch("plausible_api_tool.commands.sites.PlausibleClient.site_guest_ensure", return_value={"email": "guest@example.com"}), patch(
                "plausible_api_tool.commands.sites.PlausibleClient.site_guests_list",
                return_value={"guests": [{"email": "guest@example.com", "role": "viewer"}]},
            ):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cmd_site_guests_ensure(args, ctx)
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["plan"]["recovery"]["end_state"], "rollback_by_inverse_action")
            self.assertIn("before_state", payload["plan"])
            self.assertIn("before_state_path", payload["plan"])
            self.assertEqual(payload["plan"]["before_state"]["command"], "site.guests.ensure")
            self.assertEqual(payload["plan"]["before_state"]["before_state"]["resource"], "guest")

    def test_site_goals_ensure_plan_and_receipt_artifacts_include_recovery(self) -> None:
        args = SimpleNamespace(
            site_id="example.com",
            goal_type="event",
            event_name="download",
            page_path=None,
            display_name="Download Click",
        )
        with tempfile.TemporaryDirectory() as d:
            plan_path = str(Path(d) / "plan.json")
            receipt_path = str(Path(d) / "receipt.json")
            ctx = self._ctx(
                apply=True,
                yes=True,
                ack_irreversible=False,
                plan_out=plan_path,
                receipt_out=receipt_path,
            )

            with patch(
                "plausible_api_tool.commands.sites.PlausibleClient.site_goal_ensure",
                return_value={"id": "goal-9", "goal_type": "event"},
            ), patch(
                "plausible_api_tool.commands.sites.PlausibleClient.site_goals_list",
                return_value={"goals": [{"id": "goal-9", "display_name": "Download Click"}]},
            ):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cmd_site_goals_ensure(args, ctx)
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["plan"]["recovery"]["end_state"], "rollback_by_inverse_action")
            self.assertFalse(payload["plan"]["recovery"]["rollback_ready"])
            self.assertTrue(payload["receipt"]["recovery"]["rollback_ready"])
            self.assertEqual(payload["receipt"]["recovery"]["rollback_plan"]["target"]["goal_id"], "goal-9")

            plan_obj = json.loads(Path(plan_path).read_text(encoding="utf-8"))
            receipt_obj = json.loads(Path(receipt_path).read_text(encoding="utf-8"))
            self.assertEqual(plan_obj["recovery"]["end_state"], "rollback_by_inverse_action")
            self.assertFalse(plan_obj["recovery"]["rollback_ready"])
            self.assertEqual(receipt_obj["recovery"]["end_state"], "rollback_by_inverse_action")
            self.assertTrue(receipt_obj["recovery"]["rollback_ready"])
            self.assertEqual(receipt_obj["recovery"]["rollback_plan"]["target"]["goal_id"], "goal-9")

    def test_site_custom_props_ensure_plan_and_receipt_artifacts_include_recovery(self) -> None:
        args = SimpleNamespace(site_id="example.com", property="campaign")
        with tempfile.TemporaryDirectory() as d:
            plan_path = str(Path(d) / "plan.json")
            receipt_path = str(Path(d) / "receipt.json")
            ctx = self._ctx(
                apply=True,
                yes=True,
                ack_irreversible=False,
                plan_out=plan_path,
                receipt_out=receipt_path,
            )

            with patch(
                "plausible_api_tool.commands.sites.PlausibleClient.site_custom_prop_ensure",
                return_value={"property": "campaign"},
            ), patch(
                "plausible_api_tool.commands.sites.PlausibleClient.site_custom_props_list",
                return_value={"custom_properties": [{"property": "campaign"}]},
            ):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cmd_site_custom_props_ensure(args, ctx)
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["plan"]["recovery"]["end_state"], "rollback_by_inverse_action")
            self.assertTrue(payload["plan"]["recovery"]["rollback_ready"])

            plan_obj = json.loads(Path(plan_path).read_text(encoding="utf-8"))
            receipt_obj = json.loads(Path(receipt_path).read_text(encoding="utf-8"))
            self.assertEqual(plan_obj["recovery"]["strategy"], "plausible.sites.custom_props.delete")
            self.assertEqual(receipt_obj["recovery"]["strategy"], "plausible.sites.custom_props.delete")
