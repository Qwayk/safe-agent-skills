from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import community_membership_questions
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = action, payload


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestCommunityMembershipQuestionsCommands(unittest.TestCase):
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
            "tool": "wix-safe-agent-cli",
            "tool_version": "0.0.0",
            "command_str": "wix-safe-agent-cli community-membership-questions",
            "apply": False,
            "yes": False,
            "verbose": False,
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
            "plan_in": None,
            "plan_out": None,
            "receipt_out": None,
            "ack_irreversible": False,
            "enforce_reviewed_plan": True,
        }
        ctx.update(overrides)
        return ctx

    def test_parser_exposes_community_membership_questions_commands(self) -> None:
        parser = build_parser()
        cases = [
            (["community-membership-questions", "list", "--group-id", "group-1"], "list", False),
            (
                [
                    "community-membership-questions",
                    "list-answers",
                    "--group-id",
                    "group-1",
                    "--member-ids-json",
                    '["member-1"]',
                ],
                "list-answers",
                False,
            ),
            (
                [
                    "community-membership-questions",
                    "create-or-replace",
                    "--group-id",
                    "group-1",
                    "--questions-json",
                    '{"questions":[{"text":"Why join?","required":true}]}',
                ],
                "create-or-replace",
                True,
            ),
        ]
        for argv, command, write_capable in cases:
            with self.subTest(command=command):
                args = parser.parse_args(argv)
                self.assertEqual(args.community_membership_questions_cmd, command)
                self.assertEqual(args.write_capable, write_capable)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_list_uses_official_path(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"membershipQuestions": []})
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = community_membership_questions.cmd_community_membership_questions_list(
                SimpleNamespace(group_id="group-1"),
                self._ctx(),
            )
        self.assertEqual(rc, 0)
        self.assertEqual(mock_client.return_value.request.call_args.kwargs["method"], "GET")
        self.assertTrue(
            mock_client.return_value.request.call_args.kwargs["url"].endswith(
                "/social-groups-proxy/questions/v2/membership-questions/group-1"
            )
        )

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_list_answers_uses_official_path_and_body(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"answers": []})
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = community_membership_questions.cmd_community_membership_questions_list_answers(
                SimpleNamespace(
                    group_id="group-1",
                    member_ids_json='["member-1"]',
                    paging_json='{"limit":20,"offset":0}',
                ),
                self._ctx(),
            )
        self.assertEqual(rc, 0)
        self.assertEqual(mock_client.return_value.request.call_args.kwargs["method"], "POST")
        self.assertTrue(
            mock_client.return_value.request.call_args.kwargs["url"].endswith(
                "/social-groups-proxy/questions/v2/membership-questions/group-1/answers"
            )
        )
        self.assertEqual(
            mock_client.return_value.request.call_args.kwargs["json_body"],
            {"memberIds": ["member-1"], "paging": {"limit": 20, "offset": 0}},
        )

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_create_or_replace_is_plan_first_and_allows_empty_questions_array(
        self, mock_client: unittest.mock.MagicMock
    ) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({})
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = community_membership_questions.cmd_community_membership_questions_create_or_replace(
                SimpleNamespace(group_id="group-1", questions_json='{"questions":[]}'),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["request"]["method"], "PUT")
        self.assertEqual(payload["plan"]["request"]["path"], "/social-groups-proxy/questions/v2/membership-questions/group-1")
        self.assertEqual(payload["plan"]["request"]["body"], {"questions": []})
        self.assertIn("replace-community-membership-questions", payload["plan"]["risk_reasons"])
        self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
        self.assertFalse(mock_client.return_value.request.called)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_create_or_replace_rejects_empty_object(self, mock_client: unittest.mock.MagicMock) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = community_membership_questions.cmd_community_membership_questions_create_or_replace(
                SimpleNamespace(group_id="group-1", questions_json="{}"),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertFalse(mock_client.return_value.request.called)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_create_or_replace_rejects_bare_array(self, mock_client: unittest.mock.MagicMock) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = community_membership_questions.cmd_community_membership_questions_create_or_replace(
                SimpleNamespace(group_id="group-1", questions_json="[]"),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertFalse(mock_client.return_value.request.called)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_list_answers_rejects_non_array_member_ids(self, mock_client: unittest.mock.MagicMock) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = community_membership_questions.cmd_community_membership_questions_list_answers(
                SimpleNamespace(group_id="group-1", member_ids_json='{"memberIds":["member-1"]}', paging_json=None),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertFalse(mock_client.return_value.request.called)
