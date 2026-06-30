from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import contributors
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def __init__(self) -> None:
        self.writes: list[tuple[str, dict]] = []

    def write(self, action: str, payload: dict) -> None:
        self.writes.append((action, payload))


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestContributorsCommands(unittest.TestCase):
    def _ctx(self, *, cfg_override: dict | None = None, **overrides) -> dict:
        cfg = SimpleNamespace(
            base_url="https://www.wixapis.com",
            timeout_s=30.0,
            access_token="site-app-token",
            api_key=None,
            account_id=None,
            app_id=None,
            app_secret=None,
            instance_id=None,
            has_official_app_auth=False,
        )
        if cfg_override:
            for key, value in cfg_override.items():
                setattr(cfg, key, value)

        ctx = {
            "cfg": cfg,
            "env_file": "/tmp/.env",
            "tool": "wix-safe-agent-cli",
            "tool_version": "0.0.0",
            "command_str": "wix-safe-agent-cli contributors query",
            "verbose": False,
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
            "apply": False,
            "yes": False,
            "ack_irreversible": False,
            "plan_out": None,
            "plan_in": None,
            "receipt_out": None,
        }
        ctx.update(overrides)
        return ctx

    def test_parser_recognizes_contributors_query(self) -> None:
        parser = build_parser()
        parsed = parser.parse_args(["contributors", "query", "--policy-ids-json", '["6600344420111308827"]'])

        self.assertEqual(parsed.contributors_cmd, "query")
        self.assertFalse(parsed.write_capable)
        self.assertEqual(parsed.policy_ids_json, '["6600344420111308827"]')
        self.assertEqual(parsed.func.__name__, "cmd_contributors_query")

    def test_parser_recognizes_contributors_remove(self) -> None:
        parser = build_parser()
        parsed = parser.parse_args(["contributors", "remove", "--account-id", "acct-123", "--site-id", "site-456"])

        self.assertEqual(parsed.contributors_cmd, "remove")
        self.assertTrue(parsed.write_capable)
        self.assertEqual(parsed.account_id, "acct-123")
        self.assertEqual(parsed.site_id, "site-456")
        self.assertEqual(parsed.func.__name__, "cmd_contributors_remove")

    def test_parser_recognizes_contributors_change_role(self) -> None:
        parser = build_parser()
        parsed = parser.parse_args(
            [
                "contributors",
                "change-role",
                "--account-id",
                "acct-123",
                "--site-id",
                "site-456",
                "--role-ids-json",
                '["role-1","role-2"]',
            ]
        )

        self.assertEqual(parsed.contributors_cmd, "change-role")
        self.assertTrue(parsed.write_capable)
        self.assertEqual(parsed.account_id, "acct-123")
        self.assertEqual(parsed.site_id, "site-456")
        self.assertEqual(parsed.role_ids_json, '["role-1","role-2"]')
        self.assertEqual(parsed.func.__name__, "cmd_contributors_change_role")

    def test_parser_recognizes_contributors_change_contributor_location(self) -> None:
        parser = build_parser()
        parsed = parser.parse_args(
            [
                "contributors",
                "change-contributor-location",
                "--account-id",
                "acct-123",
                "--site-id",
                "site-456",
                "--location-ids-json",
                '["loc-1","loc-2"]',
            ]
        )

        self.assertEqual(parsed.contributors_cmd, "change-contributor-location")
        self.assertTrue(parsed.write_capable)
        self.assertEqual(parsed.account_id, "acct-123")
        self.assertEqual(parsed.site_id, "site-456")
        self.assertEqual(parsed.location_ids_json, '["loc-1","loc-2"]')
        self.assertEqual(parsed.func.__name__, "cmd_contributors_change_contributor_location")

    @patch("wix_safe_agent_cli.commands.contributors.HttpClient")
    def test_contributors_query_builds_expected_request_and_headers(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {
                "contributors": [
                    {
                        "accountId": "b1eb9bab-b71c-4a12-b84e-5b5b4c869e64",
                        "accountOwnerId": "b1eb9bab-b80c-4a12-b84e-5b5b4c869e00",
                    }
                ]
            }
        )
        args = SimpleNamespace(policy_ids_json='["6600344420111308827","6600344420111309999"]')
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = contributors.cmd_contributors_query(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["method"], "contributors.query")
        self.assertEqual(payload["auth_mode"], "app_token")
        self.assertEqual(
            payload["request"],
            {
                "method": "GET",
                "path": "/roles-management/v2/contributors/query",
                "params": {"filter.policyIds": ["6600344420111308827", "6600344420111309999"]},
            },
        )
        self.assertEqual(payload["response"]["contributors"][0]["accountId"], "b1eb9bab-b71c-4a12-b84e-5b5b4c869e64")
        self.assertEqual(ctx["audit"].writes[0][0], "contributors.query")

        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["method"], "GET")
        self.assertTrue(call.kwargs["url"].endswith("/roles-management/v2/contributors/query"))
        self.assertEqual(call.kwargs["headers"], {"Authorization": "site-app-token"})
        self.assertEqual(
            call.kwargs["params"],
            {"filter.policyIds": ["6600344420111308827", "6600344420111309999"]},
        )

    @patch("wix_safe_agent_cli.commands.contributors.HttpClient")
    def test_contributors_remove_dry_run_builds_plan(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {"contributors": [{"accountId": "acct-123", "accountOwnerId": "owner-1"}]}
        )
        args = SimpleNamespace(account_id="acct-123", site_id="site-456")
        ctx = self._ctx(command_str="wix-safe-agent-cli contributors remove --account-id acct-123 --site-id site-456")

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = contributors.cmd_contributors_remove(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["method"], "contributors.remove")
        self.assertEqual(
            payload["plan"]["selector"],
            {"kind": "wix-contributor", "operation": "remove", "account_id": "acct-123", "site_id": "site-456"},
        )
        self.assertEqual(payload["plan"]["request"]["body"], {"accountId": "acct-123"})
        self.assertEqual(payload["plan"]["baseline"]["before_state"]["matched_contributor"]["accountId"], "acct-123")
        self.assertEqual(mock_client.return_value.request.call_count, 1)
        self.assertEqual(mock_client.return_value.request.call_args.kwargs["method"], "GET")
        self.assertEqual(
            mock_client.return_value.request.call_args.kwargs["headers"],
            {"Authorization": "site-app-token", "wix-site-id": "site-456"},
        )

    @patch("wix_safe_agent_cli.commands.contributors.HttpClient")
    def test_contributors_remove_plan_out_writes_file(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"contributors": [{"accountId": "acct-123"}]})
        args = SimpleNamespace(account_id="acct-123", site_id="site-456")

        with tempfile.TemporaryDirectory() as tmpdir:
            plan_path = str(Path(tmpdir) / "plan.json")
            ctx = self._ctx(
                command_str="wix-safe-agent-cli contributors remove --account-id acct-123 --site-id site-456",
                plan_out=plan_path,
            )

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = contributors.cmd_contributors_remove(args, ctx)
            payload = json.loads(buf.getvalue())

            self.assertEqual(rc, 0)
            self.assertEqual(payload["plan_out"], plan_path)
            written = json.loads(Path(plan_path).read_text(encoding="utf-8"))
            self.assertEqual(written["method"], "contributors.remove")

    @patch("wix_safe_agent_cli.commands.contributors.HttpClient")
    def test_contributors_remove_apply_verifies_account_disappears(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"contributors": [{"accountId": "acct-123", "accountOwnerId": "owner-1"}]}),
            _DummyResponse({}),
            _DummyResponse({"contributors": [{"accountId": "acct-999"}]}),
        ]
        args = SimpleNamespace(account_id="acct-123", site_id="site-456")
        ctx = self._ctx(
            command_str="wix-safe-agent-cli contributors remove --account-id acct-123 --site-id site-456",
            apply=True,
            yes=True,
            ack_irreversible=True,
        )

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = contributors.cmd_contributors_remove(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertFalse(payload["dry_run"])
        self.assertEqual(payload["receipt"]["response"], {})
        self.assertTrue(payload["receipt"]["verification"]["ok"])
        self.assertFalse(payload["receipt"]["verification"]["after"]["account_present"])
        self.assertEqual(mock_client.return_value.request.call_args_list[0].kwargs["method"], "GET")
        self.assertEqual(mock_client.return_value.request.call_args_list[1].kwargs["method"], "POST")
        self.assertEqual(mock_client.return_value.request.call_args_list[1].kwargs["json_body"], {"accountId": "acct-123"})
        self.assertEqual(mock_client.return_value.request.call_args_list[1].kwargs["headers"]["wix-site-id"], "site-456")
        self.assertEqual(mock_client.return_value.request.call_args_list[2].kwargs["method"], "GET")
        self.assertEqual(ctx["audit"].writes[0][0], "contributors.remove.apply")

    @patch("wix_safe_agent_cli.commands.contributors.HttpClient")
    def test_contributors_remove_refuses_when_account_not_present(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"contributors": [{"accountId": "someone-else"}]})
        args = SimpleNamespace(account_id="acct-123", site_id="site-456")
        ctx = self._ctx(command_str="wix-safe-agent-cli contributors remove --account-id acct-123 --site-id site-456")

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = contributors.cmd_contributors_remove(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["refused"])
        self.assertTrue(payload["dry_run"])
        self.assertIn("not currently present", payload["reasons"][0])

    @patch("wix_safe_agent_cli.commands.contributors.HttpClient")
    def test_contributors_remove_refuses_live_apply_without_acknowledgement(
        self, mock_client: unittest.mock.MagicMock
    ) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"contributors": [{"accountId": "acct-123"}]})
        args = SimpleNamespace(account_id="acct-123", site_id="site-456")
        ctx = self._ctx(
            command_str="wix-safe-agent-cli contributors remove --account-id acct-123 --site-id site-456",
            apply=True,
            yes=True,
        )

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = contributors.cmd_contributors_remove(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["refused"])
        self.assertFalse(payload["dry_run"])
        self.assertIn("--ack-irreversible", payload["reasons"][0])
        self.assertEqual(mock_client.return_value.request.call_count, 1)

    @patch("wix_safe_agent_cli.commands.contributors.HttpClient")
    def test_contributors_remove_rejects_missing_site_id(self, mock_client: unittest.mock.MagicMock) -> None:
        _ = mock_client
        args = SimpleNamespace(account_id="acct-123", site_id="   ")
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = contributors.cmd_contributors_remove(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("Missing --site-id", payload["error"])

    @patch("wix_safe_agent_cli.commands.contributors.HttpClient")
    def test_contributors_change_role_dry_run_builds_plan(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {"contributors": [{"accountId": "acct-123", "accountOwnerId": "owner-1"}]}
        )
        args = SimpleNamespace(account_id="acct-123", site_id="site-456", role_ids_json='["role-1","role-2"]')
        ctx = self._ctx(
            command_str=(
                "wix-safe-agent-cli contributors change-role --account-id acct-123 "
                "--site-id site-456 --role-ids-json [\"role-1\",\"role-2\"]"
            )
        )

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = contributors.cmd_contributors_change_role(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["method"], "contributors.change-role")
        self.assertEqual(
            payload["plan"]["selector"],
            {
                "kind": "wix-contributor",
                "operation": "change-role",
                "account_id": "acct-123",
                "site_id": "site-456",
                "role_ids": ["role-1", "role-2"],
            },
        )
        self.assertEqual(
            payload["plan"]["request"]["body"],
            {
                "accountId": "acct-123",
                "newRoles": [{"roleId": "role-1"}, {"roleId": "role-2"}],
            },
        )
        self.assertEqual(payload["plan"]["baseline"]["before_state"]["matched_contributor"]["accountId"], "acct-123")
        self.assertIn("full-replace", " ".join(payload["plan"]["risk_reasons"]))
        self.assertEqual(mock_client.return_value.request.call_count, 1)
        self.assertEqual(mock_client.return_value.request.call_args.kwargs["method"], "GET")
        self.assertEqual(
            mock_client.return_value.request.call_args.kwargs["headers"],
            {"Authorization": "site-app-token", "wix-site-id": "site-456"},
        )

    @patch("wix_safe_agent_cli.commands.contributors.HttpClient")
    def test_contributors_change_role_apply_verifies_roles_and_presence(
        self, mock_client: unittest.mock.MagicMock
    ) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"contributors": [{"accountId": "acct-123", "accountOwnerId": "owner-1"}]}),
            _DummyResponse({"newAssignedRoles": [{"roleId": "role-2", "assignmentId": "assign-1"}, {"roleId": "role-1", "assignmentId": "assign-2"}]}),
            _DummyResponse({"contributors": [{"accountId": "acct-123", "accountOwnerId": "owner-1"}]}),
        ]
        args = SimpleNamespace(account_id="acct-123", site_id="site-456", role_ids_json='["role-1","role-2"]')
        ctx = self._ctx(
            command_str=(
                "wix-safe-agent-cli contributors change-role --account-id acct-123 "
                "--site-id site-456 --role-ids-json [\"role-1\",\"role-2\"]"
            ),
            apply=True,
            yes=True,
        )

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = contributors.cmd_contributors_change_role(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertFalse(payload["dry_run"])
        self.assertEqual(payload["receipt"]["response"]["newAssignedRoles"][0]["assignmentId"], "assign-1")
        self.assertEqual(
            sorted(role["roleId"] for role in payload["receipt"]["verification"]["provider_new_assigned_roles"]),
            ["role-1", "role-2"],
        )
        self.assertTrue(payload["receipt"]["verification"]["ok"])
        self.assertTrue(payload["receipt"]["verification"]["after"]["account_present"])
        self.assertEqual(mock_client.return_value.request.call_args_list[0].kwargs["method"], "GET")
        self.assertEqual(mock_client.return_value.request.call_args_list[1].kwargs["method"], "PUT")
        self.assertEqual(
            mock_client.return_value.request.call_args_list[1].kwargs["json_body"],
            {
                "accountId": "acct-123",
                "newRoles": [{"roleId": "role-1"}, {"roleId": "role-2"}],
            },
        )
        self.assertEqual(mock_client.return_value.request.call_args_list[1].kwargs["headers"]["wix-site-id"], "site-456")
        self.assertEqual(mock_client.return_value.request.call_args_list[2].kwargs["method"], "GET")

    @patch("wix_safe_agent_cli.commands.contributors.HttpClient")
    def test_contributors_change_role_rejects_invalid_role_lists(self, mock_client: unittest.mock.MagicMock) -> None:
        _ = mock_client
        ctx = self._ctx()
        cases = [
            ("[]", "--role-ids-json cannot be an empty array"),
            ('["role-1","role-1"]', "--role-ids-json cannot contain duplicate role IDs"),
            ('["role-1",""]', "--role-ids-json[1] cannot be empty"),
            ('["role-1",1]', "--role-ids-json[1] must be a string"),
        ]

        for raw_role_ids, expected_error in cases:
            with self.subTest(raw_role_ids=raw_role_ids):
                args = SimpleNamespace(account_id="acct-123", site_id="site-456", role_ids_json=raw_role_ids)
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = contributors.cmd_contributors_change_role(args, ctx)
                payload = json.loads(buf.getvalue())

                self.assertEqual(rc, 1)
                self.assertEqual(payload["error_type"], "ValidationError")
                self.assertIn(expected_error, payload["error"])

    @patch("wix_safe_agent_cli.commands.contributors.HttpClient")
    def test_contributors_change_contributor_location_dry_run_builds_plan(
        self, mock_client: unittest.mock.MagicMock
    ) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {"contributors": [{"accountId": "acct-123", "accountOwnerId": "owner-1"}]}
        )
        args = SimpleNamespace(account_id="acct-123", site_id="site-456", location_ids_json='["loc-1","loc-2"]')
        ctx = self._ctx(
            command_str=(
                "wix-safe-agent-cli contributors change-contributor-location --account-id acct-123 "
                "--site-id site-456 --location-ids-json [\"loc-1\",\"loc-2\"]"
            )
        )

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = contributors.cmd_contributors_change_contributor_location(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["method"], "contributors.change-contributor-location")
        self.assertEqual(
            payload["plan"]["selector"],
            {
                "kind": "wix-contributor",
                "operation": "change-contributor-location",
                "account_id": "acct-123",
                "site_id": "site-456",
                "location_ids": ["loc-1", "loc-2"],
            },
        )
        self.assertEqual(
            payload["plan"]["request"]["body"],
            {
                "accountId": "acct-123",
                "newLocations": ["loc-1", "loc-2"],
            },
        )
        self.assertEqual(payload["plan"]["baseline"]["before_state"]["matched_contributor"]["accountId"], "acct-123")
        self.assertIn("full-replace", " ".join(payload["plan"]["risk_reasons"]))
        self.assertEqual(mock_client.return_value.request.call_count, 1)
        self.assertEqual(mock_client.return_value.request.call_args.kwargs["method"], "GET")
        self.assertEqual(
            mock_client.return_value.request.call_args.kwargs["headers"],
            {"Authorization": "site-app-token", "wix-site-id": "site-456"},
        )

    @patch("wix_safe_agent_cli.commands.contributors.HttpClient")
    def test_contributors_change_contributor_location_apply_verifies_locations_and_presence(
        self, mock_client: unittest.mock.MagicMock
    ) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"contributors": [{"accountId": "acct-123", "accountOwnerId": "owner-1"}]}),
            _DummyResponse(
                {
                    "newAssignedLocations": [
                        {"locationIds": ["loc-2", "loc-1"], "assignmentIds": ["assign-1"]},
                        {"locationIds": ["loc-1", "loc-2"], "assignmentIds": ["assign-2"]},
                    ]
                }
            ),
            _DummyResponse({"contributors": [{"accountId": "acct-123", "accountOwnerId": "owner-1"}]}),
        ]
        args = SimpleNamespace(account_id="acct-123", site_id="site-456", location_ids_json='["loc-1","loc-2"]')
        ctx = self._ctx(
            command_str=(
                "wix-safe-agent-cli contributors change-contributor-location --account-id acct-123 "
                "--site-id site-456 --location-ids-json [\"loc-1\",\"loc-2\"]"
            ),
            apply=True,
            yes=True,
        )

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = contributors.cmd_contributors_change_contributor_location(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertFalse(payload["dry_run"])
        self.assertEqual(payload["receipt"]["response"]["newAssignedLocations"][0]["assignmentIds"][0], "assign-1")
        self.assertEqual(
            sorted(
                {
                    location_id
                    for item in payload["receipt"]["verification"]["provider_new_assigned_locations"]
                    for location_id in item["locationIds"]
                }
            ),
            ["loc-1", "loc-2"],
        )
        self.assertTrue(payload["receipt"]["verification"]["ok"])
        self.assertTrue(payload["receipt"]["verification"]["after"]["account_present"])
        self.assertEqual(mock_client.return_value.request.call_args_list[0].kwargs["method"], "GET")
        self.assertEqual(mock_client.return_value.request.call_args_list[1].kwargs["method"], "PUT")
        self.assertEqual(
            mock_client.return_value.request.call_args_list[1].kwargs["json_body"],
            {
                "accountId": "acct-123",
                "newLocations": ["loc-1", "loc-2"],
            },
        )
        self.assertEqual(mock_client.return_value.request.call_args_list[1].kwargs["headers"]["wix-site-id"], "site-456")
        self.assertEqual(mock_client.return_value.request.call_args_list[2].kwargs["method"], "GET")

    @patch("wix_safe_agent_cli.commands.contributors.HttpClient")
    def test_contributors_change_contributor_location_rejects_invalid_location_lists(
        self, mock_client: unittest.mock.MagicMock
    ) -> None:
        _ = mock_client
        ctx = self._ctx()
        cases = [
            ("[]", "--location-ids-json cannot be an empty array"),
            ('["loc-1","loc-1"]', "--location-ids-json cannot contain duplicate location IDs"),
            ('["loc-1",""]', "--location-ids-json[1] cannot be empty"),
            ('["loc-1",1]', "--location-ids-json[1] must be a string"),
            ('["loc-1","loc-2","loc-3","loc-4","loc-5","loc-6","loc-7","loc-8","loc-9","loc-10","loc-11","loc-12","loc-13","loc-14","loc-15","loc-16","loc-17","loc-18","loc-19","loc-20","loc-21"]', "--location-ids-json cannot contain more than 20 location IDs"),
        ]

        for raw_location_ids, expected_error in cases:
            with self.subTest(raw_location_ids=raw_location_ids):
                args = SimpleNamespace(
                    account_id="acct-123",
                    site_id="site-456",
                    location_ids_json=raw_location_ids,
                )
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = contributors.cmd_contributors_change_contributor_location(args, ctx)
                payload = json.loads(buf.getvalue())

                self.assertEqual(rc, 1)
                self.assertEqual(payload["error_type"], "ValidationError")
                self.assertIn(expected_error, payload["error"])

    @patch("wix_safe_agent_cli.commands.contributors.HttpClient")
    def test_contributors_query_allows_no_filter(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"contributors": []})
        args = SimpleNamespace(policy_ids_json=None)
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = contributors.cmd_contributors_query(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["params"], {})
        self.assertEqual(mock_client.return_value.request.call_args.kwargs["params"], None)

    @patch("wix_safe_agent_cli.commands.contributors.HttpClient")
    def test_contributors_query_rejects_empty_policy_array(self, mock_client: unittest.mock.MagicMock) -> None:
        _ = mock_client
        args = SimpleNamespace(policy_ids_json="[]")
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = contributors.cmd_contributors_query(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("--policy-ids-json cannot be an empty array", payload["error"])

    @patch("wix_safe_agent_cli.commands.contributors.HttpClient")
    def test_contributors_query_errors_when_no_token_source_exists(self, mock_client: unittest.mock.MagicMock) -> None:
        _ = mock_client
        args = SimpleNamespace(policy_ids_json=None)
        ctx = self._ctx(cfg_override={"access_token": None})

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = contributors.cmd_contributors_query(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("Missing official Wix credentials", payload["error"])
