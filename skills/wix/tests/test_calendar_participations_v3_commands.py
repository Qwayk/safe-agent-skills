from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import calendar_participations_v3
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = action, payload


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestCalendarParticipationsV3Commands(unittest.TestCase):
    def _ctx(self, **overrides) -> dict:
        cfg = SimpleNamespace(
            base_url="https://www.wixapis.com",
            timeout_s=30.0,
            app_id=None,
            app_secret=None,
            instance_id=None,
            access_token="token-abc",
            has_official_app_auth=False,
        )
        ctx = {
            "cfg": cfg,
            "env_file": "/tmp/.env",
            "verbose": False,
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
            "tool": "wix-safe-agent-cli",
            "tool_version": "0.0.0",
            "command_str": "wix-safe-agent-cli calendar-participations-v3",
            "apply": False,
            "yes": False,
            "plan_in": None,
            "plan_out": None,
            "receipt_out": None,
            "ack_irreversible": False,
        }
        ctx.update(overrides)
        return ctx

    @patch("wix_safe_agent_cli.commands.calendar_participations_v3.HttpClient")
    @patch("wix_safe_agent_cli.commands.calendar_participations_v3.resolve_auth_mode")
    def test_get_builds_official_participation_path(
        self,
        mock_auth: unittest.mock.MagicMock,
        mock_client: unittest.mock.MagicMock,
    ) -> None:
        mock_auth.return_value = {"mode": "access_token", "headers": {"Authorization": "token-abc"}}
        mock_client.return_value.request.return_value = _DummyResponse({"participation": {"id": "participation-1"}})

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = calendar_participations_v3.cmd_calendar_participations_v3_get(
                SimpleNamespace(participation_id="participation-1"),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["method"], "calendar-participations-v3.get")
        self.assertEqual(payload["request"], {"method": "GET", "path": "/calendar/v3/participations/participation-1"})
        self.assertEqual(mock_client.return_value.request.call_args.kwargs["method"], "GET")
        self.assertEqual(mock_client.return_value.request.call_args.kwargs["json_body"], None)

    @patch("wix_safe_agent_cli.commands.calendar_participations_v3.HttpClient")
    @patch("wix_safe_agent_cli.commands.calendar_participations_v3.resolve_auth_mode")
    def test_query_posts_official_query_body(
        self,
        mock_auth: unittest.mock.MagicMock,
        mock_client: unittest.mock.MagicMock,
    ) -> None:
        mock_auth.return_value = {"mode": "access_token", "headers": {"Authorization": "token-abc"}}
        mock_client.return_value.request.return_value = _DummyResponse({"participations": []})

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = calendar_participations_v3.cmd_calendar_participations_v3_query(
                SimpleNamespace(query_json='{"query":{"filter":{"eventId":{"$eq":"event-1"}}}}'),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["method"], "POST")
        self.assertEqual(payload["request"]["path"], "/calendar/v3/participations/query")
        self.assertEqual(payload["request"]["body"]["query"]["filter"]["eventId"]["$eq"], "event-1")
        self.assertEqual(mock_client.return_value.request.call_args.kwargs["json_body"], payload["request"]["body"])

    def test_create_dry_run_emits_reviewed_plan(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = calendar_participations_v3.cmd_calendar_participations_v3_create(
                SimpleNamespace(participation_json='{"eventId":"event-1","participant":{"name":"Ada"},"partySize":1}'),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        plan = payload["plan"]
        self.assertEqual(plan["method"], "calendar-participations-v3.create")
        self.assertEqual(plan["request"]["method"], "POST")
        self.assertEqual(plan["request"]["path"], "/calendar/v3/participations")
        self.assertEqual(plan["request"]["body"]["participation"]["eventId"], "event-1")
        self.assertIn("updates-event-participants-and-remaining-capacity", plan["risk_reasons"])

    def test_update_requires_matching_id_and_revision(self) -> None:
        missing_revision = io.StringIO()
        with redirect_stdout(missing_revision):
            rc_missing = calendar_participations_v3.cmd_calendar_participations_v3_update(
                SimpleNamespace(participation_id="participation-1", participation_json='{"id":"participation-1","partySize":2}'),
                self._ctx(),
            )
        missing_payload = json.loads(missing_revision.getvalue())

        mismatched_id = io.StringIO()
        with redirect_stdout(mismatched_id):
            rc_mismatch = calendar_participations_v3.cmd_calendar_participations_v3_update(
                SimpleNamespace(participation_id="participation-1", participation_json='{"id":"participation-2","revision":"1"}'),
                self._ctx(),
            )
        mismatch_payload = json.loads(mismatched_id.getvalue())

        self.assertEqual(rc_missing, 1)
        self.assertIn("participation.revision is required", missing_payload["error"])
        self.assertEqual(rc_mismatch, 0)
        self.assertTrue(mismatch_payload["refused"])
        self.assertIn("does not match --participation-id", mismatch_payload["reasons"][0])

    def test_delete_requires_irreversible_ack_to_apply(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = calendar_participations_v3.cmd_calendar_participations_v3_delete(
                SimpleNamespace(participation_id="participation-1"),
                self._ctx(apply=True, yes=True, plan_in="/tmp/plan.json", ack_irreversible=False),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["method"], "calendar-participations-v3.delete")
        self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])

    def test_parser_exposes_all_participation_commands(self) -> None:
        parser = build_parser()
        cases = [
            (
                ["calendar-participations-v3", "create", "--participation-json", "{}"],
                calendar_participations_v3.cmd_calendar_participations_v3_create,
                True,
            ),
            (
                ["calendar-participations-v3", "get", "--participation-id", "participation-1"],
                calendar_participations_v3.cmd_calendar_participations_v3_get,
                False,
            ),
            (
                ["calendar-participations-v3", "update", "--participation-id", "participation-1", "--participation-json", "{}"],
                calendar_participations_v3.cmd_calendar_participations_v3_update,
                True,
            ),
            (
                ["calendar-participations-v3", "delete", "--participation-id", "participation-1"],
                calendar_participations_v3.cmd_calendar_participations_v3_delete,
                True,
            ),
            (
                ["calendar-participations-v3", "query", "--query-json", "{}"],
                calendar_participations_v3.cmd_calendar_participations_v3_query,
                False,
            ),
        ]
        for argv, func, write_capable in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertIs(args.func, func)
                self.assertEqual(args.write_capable, write_capable)


if __name__ == "__main__":
    unittest.main()
