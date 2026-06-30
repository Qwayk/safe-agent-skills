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
from wix_safe_agent_cli.commands import site_actions
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


class TestSiteActionsCommands(unittest.TestCase):
    def _ctx(self, *, cfg_override: dict | None = None, **overrides) -> dict:
        cfg = SimpleNamespace(
            base_url="https://www.wixapis.com",
            timeout_s=30.0,
            access_token=None,
            api_key="acct-api-key",
            account_id="acct-001",
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
            "command_str": "wix-safe-agent-cli site-actions bulk-delete",
            "apply": False,
            "yes": False,
            "verbose": False,
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
            "plan_in": None,
            "plan_out": None,
            "receipt_out": None,
            "ack_irreversible": False,
        }
        ctx.update(overrides)
        return ctx

    def test_parser_recognizes_site_actions_bulk_delete(self) -> None:
        parser = build_parser()

        parsed = parser.parse_args(["site-actions", "bulk-delete", "--site-ids-json", '["s1", "s2"]'])
        self.assertEqual(parsed.site_actions_cmd, "bulk-delete")
        self.assertTrue(parsed.write_capable)
        self.assertEqual(parsed.site_ids_json, '["s1", "s2"]')
        self.assertEqual(parsed.func.__name__, "cmd_site_actions_bulk_delete")

    def test_parser_recognizes_site_actions_publish(self) -> None:
        parser = build_parser()

        parsed = parser.parse_args(["site-actions", "publish", "--site-id", "site-a"])
        self.assertEqual(parsed.site_actions_cmd, "publish")
        self.assertTrue(parsed.write_capable)
        self.assertEqual(parsed.site_id, "site-a")
        self.assertEqual(parsed.func.__name__, "cmd_site_actions_publish")

    @patch("wix_safe_agent_cli.commands.site_actions.HttpClient")
    def test_site_actions_publish_dry_run_builds_plan_and_request_shape(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {
                "sites": [
                    {"id": "site-a", "displayName": "Alpha", "published": False},
                ]
            }
        )

        args = SimpleNamespace(site_id="site-a")
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = site_actions.cmd_site_actions_publish(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["method"], "site-actions.publish")
        self.assertEqual(payload["plan"]["request"]["method"], "POST")
        self.assertEqual(payload["plan"]["request"]["path"], "/site-publisher/v1/site/publish")
        self.assertEqual(payload["plan"]["request"]["body"], {})
        self.assertEqual(payload["plan"]["baseline"]["before_state"], {"site-a": {"id": "site-a", "displayName": "Alpha", "published": False}})

        preflight_call = mock_client.return_value.request.call_args
        self.assertTrue(str(preflight_call.kwargs["url"]).endswith("/site-list/v2/sites/query"))
        preflight_body = preflight_call.kwargs["json_body"]
        self.assertEqual(preflight_body["query"]["filter"], {"id": {"$in": ["site-a"]}})
        self.assertEqual(preflight_body["query"]["cursorPaging"], {"limit": 1})

    @patch("wix_safe_agent_cli.commands.site_actions.HttpClient")
    def test_site_actions_publish_dry_run_plan_out(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {"sites": [{"id": "site-a", "published": False}]}
        )

        args = SimpleNamespace(site_id="site-a")
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as handle:
            plan_path = handle.name

        try:
            ctx = self._ctx(plan_out=plan_path)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = site_actions.cmd_site_actions_publish(args, ctx)
            payload = json.loads(buf.getvalue())

            self.assertEqual(rc, 0)
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["plan_out"], plan_path)

            stored_plan = json.loads(Path(plan_path).read_text(encoding="utf-8"))
            self.assertEqual(stored_plan["method"], "site-actions.publish")
        finally:
            Path(plan_path).unlink()

    def test_site_actions_publish_refuses_missing_site_in_preflight(self) -> None:
        args = SimpleNamespace(site_id="missing-site")
        with patch("wix_safe_agent_cli.commands.site_actions.HttpClient") as mock_client:
            mock_client.return_value.request.return_value = _DummyResponse({"sites": []})

            ctx = self._ctx()
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = site_actions.cmd_site_actions_publish(args, ctx)
            payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("not found", payload["reasons"][0])

    @patch("wix_safe_agent_cli.commands.site_actions.HttpClient")
    def test_site_actions_publish_apply_requires_apply_and_yes(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {"sites": [{"id": "site-a", "published": False}]}
        )

        args = SimpleNamespace(site_id="site-a")
        ctx = self._ctx(apply=True, yes=False)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = site_actions.cmd_site_actions_publish(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertNotIn("receipt", payload)
        self.assertEqual(mock_client.return_value.request.call_count, 1)

    @patch("wix_safe_agent_cli.commands.site_actions.HttpClient")
    def test_site_actions_publish_refuses_stale_plan(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"sites": [{"id": "site-a", "published": False}]}),
            _DummyResponse({"sites": [{"id": "site-a", "published": False}]}),
            _DummyResponse({"sites": [{"id": "site-a", "published": True}]}),
        ]

        args = SimpleNamespace(site_id="site-a")
        dry_ctx = self._ctx()
        dry_buf = io.StringIO()
        with redirect_stdout(dry_buf):
            dry_rc = site_actions.cmd_site_actions_publish(args, dry_ctx)
        self.assertEqual(dry_rc, 0)
        dry_payload = json.loads(dry_buf.getvalue())

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as handle:
            json.dump(dry_payload["plan"], handle)
            plan_path = handle.name

        try:
            apply_ctx = self._ctx(apply=True, yes=True, plan_in=plan_path)
            apply_buf = io.StringIO()
            with redirect_stdout(apply_buf):
                apply_rc = site_actions.cmd_site_actions_publish(args, apply_ctx)
            apply_payload = json.loads(apply_buf.getvalue())

            self.assertEqual(apply_rc, 0)
            self.assertTrue(apply_payload["refused"])
            self.assertIn("changed since plan", apply_payload["reasons"][0])
            self.assertEqual(mock_client.return_value.request.call_count, 3)
            self.assertFalse(
                any(
                    str(call.kwargs.get("url", "")).endswith("/site-publisher/v1/site/publish")
                    for call in mock_client.return_value.request.call_args_list
                )
            )
        finally:
            Path(plan_path).unlink()

    @patch("wix_safe_agent_cli.commands.site_actions.HttpClient")
    def test_site_actions_publish_apply_request_headers(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"sites": [{"id": "site-a", "published": False}]}),
            _DummyResponse({"sites": [{"id": "site-a", "published": False}]}),
            _DummyResponse({}),
            _DummyResponse({"sites": [{"id": "site-a", "published": True}]}),
        ]

        args = SimpleNamespace(site_id="site-a")
        ctx = self._ctx(apply=True, yes=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = site_actions.cmd_site_actions_publish(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertFalse(payload["dry_run"])
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["method"], "site-actions.publish")

        calls = mock_client.return_value.request.call_args_list
        publish_calls = [
            call
            for call in calls
            if str(call.kwargs.get("url", "")).endswith("/site-publisher/v1/site/publish")
        ]
        self.assertEqual(len(publish_calls), 1)
        publish_call = publish_calls[0]
        self.assertEqual(publish_call.kwargs["method"], "POST")
        self.assertEqual(publish_call.kwargs["json_body"], {})
        publish_headers = publish_call.kwargs["headers"]
        self.assertEqual(publish_headers["Authorization"], "acct-api-key")
        self.assertEqual(publish_headers["wix-site-id"], "site-a")
        self.assertEqual(publish_headers["Content-Type"], "application/json")
        self.assertNotIn("wix-account-id", publish_headers)

        verification = payload["receipt"]["verification"]
        self.assertTrue(verification["ok"])
        self.assertEqual(verification["site_id"], "site-a")
        self.assertTrue(verification["after"]["published"])

    @patch("wix_safe_agent_cli.commands.site_actions.HttpClient")
    def test_site_actions_publish_receipt_marks_changed_only_when_transition_from_unpublished(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"sites": [{"id": "site-a", "published": True}]}),
            _DummyResponse({"sites": [{"id": "site-a", "published": True}]}),
            _DummyResponse({}),
            _DummyResponse({"sites": [{"id": "site-a", "published": True}]}),
        ]

        args = SimpleNamespace(site_id="site-a")
        ctx = self._ctx(apply=True, yes=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = site_actions.cmd_site_actions_publish(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertFalse(payload["receipt"]["changed"])
        verification = payload["receipt"]["verification"]
        self.assertIn("already published", verification["notes"])

    @patch("wix_safe_agent_cli.commands.site_actions.HttpClient")
    def test_site_actions_publish_apply_writes_receipt_out(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"sites": [{"id": "site-a", "published": False}]}),
            _DummyResponse({"sites": [{"id": "site-a", "published": False}]}),
            _DummyResponse({}),
            _DummyResponse({"sites": [{"id": "site-a", "published": True}]}),
        ]

        args = SimpleNamespace(site_id="site-a")
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as handle:
            receipt_path = handle.name

        try:
            ctx = self._ctx(apply=True, yes=True, receipt_out=receipt_path)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = site_actions.cmd_site_actions_publish(args, ctx)
            payload = json.loads(buf.getvalue())

            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["receipt_out"], receipt_path)

            stored_receipt = json.loads(Path(receipt_path).read_text(encoding="utf-8"))
            self.assertEqual(stored_receipt["method"], "site-actions.publish")
        finally:
            Path(receipt_path).unlink()

    def test_site_actions_bulk_delete_rejects_duplicate_ids(self) -> None:
        args = SimpleNamespace(site_ids_json='["s1", "s1"]')
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = site_actions.cmd_site_actions_bulk_delete(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")

    def test_site_actions_bulk_delete_rejects_empty_ids(self) -> None:
        args = SimpleNamespace(site_ids_json="[]")
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = site_actions.cmd_site_actions_bulk_delete(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")

    def test_site_actions_bulk_delete_rejects_too_many_ids(self) -> None:
        args = SimpleNamespace(site_ids_json=json.dumps([f"site-{i}" for i in range(21)]))
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = site_actions.cmd_site_actions_bulk_delete(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")

    @patch("wix_safe_agent_cli.commands.site_actions.HttpClient")
    def test_site_actions_bulk_delete_dry_run_builds_plan_and_request_shape(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {
                "sites": [
                    {"id": "site-a", "displayName": "Alpha", "published": True},
                    {"id": "site-b", "displayName": "Beta", "published": False},
                ]
            }
        )

        args = SimpleNamespace(site_ids_json='["site-a", "site-b"]')
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = site_actions.cmd_site_actions_bulk_delete(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["method"], "site-actions.bulk-delete")
        plan = payload["plan"]
        self.assertEqual(plan["request"]["method"], "POST")
        self.assertEqual(plan["request"]["path"], "/site-actions/v1/bulk/sites/delete")
        self.assertEqual(plan["request"]["body"], {"ids": ["site-a", "site-b"]})

        preflight_call = mock_client.return_value.request.call_args_list[0]
        self.assertEqual(preflight_call.kwargs["method"], "POST")
        self.assertTrue(str(preflight_call.kwargs["url"]).endswith("/site-list/v2/sites/query"))
        preflight_body = preflight_call.kwargs["json_body"]
        self.assertEqual(preflight_body["query"]["filter"], {"id": {"$in": ["site-a", "site-b"]}})
        self.assertEqual(preflight_body["query"]["cursorPaging"], {"limit": 2})
        preflight_headers = preflight_call.kwargs["headers"]
        self.assertEqual(preflight_headers["Authorization"], "acct-api-key")
        self.assertEqual(preflight_headers["wix-account-id"], "acct-001")

    @patch("wix_safe_agent_cli.commands.site_actions.HttpClient")
    def test_site_actions_bulk_delete_apply_refuses_without_ack_irreversible(
        self, mock_client: unittest.mock.MagicMock
    ) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {
                "sites": [
                    {"id": "site-a"},
                    {"id": "site-b"},
                ]
            }
        )
        args = SimpleNamespace(site_ids_json='["site-a", "site-b"]')
        ctx = self._ctx(apply=True, yes=True, ack_irreversible=False)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = site_actions.cmd_site_actions_bulk_delete(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertTrue(payload["dry_run"])
        self.assertIn("--ack-irreversible", payload["reasons"][0])

        calls = [call.kwargs["method"] for call in mock_client.return_value.request.call_args_list]
        self.assertEqual(calls, ["POST"])

    @patch("wix_safe_agent_cli.commands.site_actions.HttpClient")
    def test_site_actions_bulk_delete_refuses_missing_site_in_preflight(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {
                "sites": [
                    {"id": "site-a"},
                ]
            }
        )

        args = SimpleNamespace(site_ids_json='["site-a", "missing"]')
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = site_actions.cmd_site_actions_bulk_delete(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("not found", payload["reasons"][0])

    @patch("wix_safe_agent_cli.commands.site_actions.HttpClient")
    def test_site_actions_bulk_delete_refuses_stale_plan(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"sites": [{"id": "site-a", "published": False}] }),
            _DummyResponse({"sites": [{"id": "site-a", "published": True}] }),
            _DummyResponse({"sites": [{"id": "site-a", "published": True}] }),
        ]

        args = SimpleNamespace(site_ids_json='["site-a"]')
        dry_ctx = self._ctx()
        dry_buf = io.StringIO()
        with redirect_stdout(dry_buf):
            dry_rc = site_actions.cmd_site_actions_bulk_delete(args, dry_ctx)
        self.assertEqual(dry_rc, 0)
        dry_payload = json.loads(dry_buf.getvalue())

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as handle:
            json.dump(dry_payload["plan"], handle)
            plan_path = handle.name

        try:
            apply_ctx = self._ctx(apply=True, yes=True, ack_irreversible=True, plan_in=plan_path)
            apply_buf = io.StringIO()
            with redirect_stdout(apply_buf):
                apply_rc = site_actions.cmd_site_actions_bulk_delete(args, apply_ctx)
            apply_payload = json.loads(apply_buf.getvalue())

            self.assertEqual(apply_rc, 0)
            self.assertTrue(apply_payload["refused"])
            self.assertIn("changed since plan", apply_payload["reasons"][0])
            self.assertEqual(mock_client.return_value.request.call_count, 3)
            self.assertFalse(
                any(
                    str(call.kwargs.get("url", "")).endswith("/site-actions/v1/bulk/sites/delete")
                    for call in mock_client.return_value.request.call_args_list
                )
            )
        finally:
            Path(plan_path).unlink()

    @patch("wix_safe_agent_cli.commands.site_actions.HttpClient")
    def test_site_actions_bulk_delete_apply_request_headers_response_verification(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse(
                {
                    "sites": [
                        {"id": "site-a", "displayName": "Alpha"},
                        {"id": "site-b", "displayName": "Beta"},
                    ]
                }
            ),
            _DummyResponse(
                {
                    "sites": [
                        {"id": "site-a", "displayName": "Alpha"},
                        {"id": "site-b", "displayName": "Beta"},
                    ]
                }
            ),
            _DummyResponse(
                {
                    "results": [
                        {"itemMetadata": {"id": "site-a", "originalIndex": 0, "success": True}},
                        {"itemMetadata": {"id": "site-b", "originalIndex": 1, "success": True}},
                    ],
                    "bulkActionMetadata": {"totalSuccesses": 2, "totalFailures": 0},
                }
            ),
        ]

        args = SimpleNamespace(site_ids_json='["site-a", "site-b"]')
        ctx = self._ctx(apply=True, yes=True, ack_irreversible=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = site_actions.cmd_site_actions_bulk_delete(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertFalse(payload["dry_run"])
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["method"], "site-actions.bulk-delete")

        calls = mock_client.return_value.request.call_args_list
        preflight_calls = [call.kwargs for call in calls if call.kwargs.get("method") == "POST" and str(call.kwargs.get("url", "")).endswith("/site-list/v2/sites/query")]
        self.assertEqual(len(preflight_calls), 2)

        delete_call = [call for call in calls if str(call.kwargs.get("url", "")).endswith("/site-actions/v1/bulk/sites/delete")][0]
        self.assertEqual(delete_call.kwargs["method"], "POST")
        self.assertEqual(delete_call.kwargs["json_body"], {"ids": ["site-a", "site-b"]})
        delete_headers = delete_call.kwargs["headers"]
        self.assertEqual(delete_headers["Authorization"], "acct-api-key")
        self.assertEqual(delete_headers["wix-account-id"], "acct-001")
        self.assertEqual(delete_headers["Content-Type"], "application/json")

        verification = payload["receipt"]["verification"]
        self.assertTrue(verification["ok"])
        self.assertEqual(verification["totalSuccesses"], 2)
        self.assertEqual(verification["totalFailures"], 0)

    def test_parser_recognizes_site_actions_duplicate(self) -> None:
        parser = build_parser()

        parsed = parser.parse_args(
            [
                "site-actions",
                "duplicate",
                "--source-site-id",
                "source-1",
                "--site-display-name",
                "Copy of Site",
            ]
        )
        self.assertEqual(parsed.site_actions_cmd, "duplicate")
        self.assertTrue(parsed.write_capable)
        self.assertEqual(parsed.source_site_id, "source-1")
        self.assertEqual(parsed.site_display_name, "Copy of Site")
        self.assertEqual(parsed.func.__name__, "cmd_site_actions_duplicate")

    @patch("wix_safe_agent_cli.commands.site_actions.HttpClient")
    def test_site_actions_duplicate_dry_run_builds_plan_and_request_shape(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {"sites": [{"id": "source-1", "displayName": "Original", "published": True}]}
        )

        args = SimpleNamespace(source_site_id="source-1", site_display_name="Site Copy")
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = site_actions.cmd_site_actions_duplicate(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["method"], "site-actions.duplicate")
        plan = payload["plan"]
        self.assertEqual(plan["request"]["method"], "POST")
        self.assertEqual(plan["request"]["path"], "/site-actions/v1/sites/duplicate")
        self.assertEqual(plan["request"]["body"], {"sourceSiteId": "source-1", "siteDisplayName": "Site Copy"})
        self.assertEqual(plan["baseline"]["before_state"], {"source-1": {"id": "source-1", "displayName": "Original", "published": True}})
        self.assertIn("site-duplicate-partial-copy", plan["risk_reasons"])
        self.assertIn("duplicate is incomplete", plan["preconditions"][3])

        preflight_call = mock_client.return_value.request.call_args
        self.assertTrue(str(preflight_call.kwargs["url"]).endswith("/site-list/v2/sites/query"))
        preflight_body = preflight_call.kwargs["json_body"]
        self.assertEqual(preflight_body["query"]["filter"], {"id": {"$in": ["source-1"]}})
        self.assertEqual(preflight_body["query"]["cursorPaging"], {"limit": 1})
        preflight_headers = preflight_call.kwargs["headers"]
        self.assertEqual(preflight_headers["Authorization"], "acct-api-key")
        self.assertEqual(preflight_headers["wix-account-id"], "acct-001")

    @patch("wix_safe_agent_cli.commands.site_actions.HttpClient")
    def test_site_actions_duplicate_refuses_when_source_site_missing(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"sites": []})

        args = SimpleNamespace(source_site_id="missing-site", site_display_name="Copy")
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = site_actions.cmd_site_actions_duplicate(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("not found", payload["reasons"][0])

    @patch("wix_safe_agent_cli.commands.site_actions.HttpClient")
    def test_site_actions_duplicate_apply_refuses_without_yes_confirmation(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {"sites": [{"id": "source-1", "displayName": "Original"}]}
        )

        args = SimpleNamespace(source_site_id="source-1", site_display_name="Copy")
        ctx = self._ctx(apply=True, yes=False)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = site_actions.cmd_site_actions_duplicate(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertNotIn("receipt", payload)
        calls = [call.kwargs["method"] for call in mock_client.return_value.request.call_args_list]
        self.assertEqual(calls, ["POST"])

    @patch("wix_safe_agent_cli.commands.site_actions.HttpClient")
    def test_site_actions_duplicate_refuses_stale_plan(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"sites": [{"id": "source-1", "displayName": "Original v1"}]}),
            _DummyResponse({"sites": [{"id": "source-1", "displayName": "Original v2"}]}),
            _DummyResponse({"sites": [{"id": "source-1", "displayName": "Original v2"}]}),
        ]

        args = SimpleNamespace(source_site_id="source-1", site_display_name="Copy")
        dry_ctx = self._ctx()
        dry_buf = io.StringIO()
        with redirect_stdout(dry_buf):
            dry_rc = site_actions.cmd_site_actions_duplicate(args, dry_ctx)
        self.assertEqual(dry_rc, 0)
        dry_payload = json.loads(dry_buf.getvalue())

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as handle:
            json.dump(dry_payload["plan"], handle)
            plan_path = handle.name

        try:
            apply_ctx = self._ctx(apply=True, yes=True, plan_in=plan_path)
            apply_buf = io.StringIO()
            with redirect_stdout(apply_buf):
                apply_rc = site_actions.cmd_site_actions_duplicate(args, apply_ctx)
            apply_payload = json.loads(apply_buf.getvalue())

            self.assertEqual(apply_rc, 0)
            self.assertTrue(apply_payload["refused"])
            self.assertIn("changed since plan", apply_payload["reasons"][0])
            self.assertEqual(mock_client.return_value.request.call_count, 3)
            calls = [str(call.kwargs.get("url", "")) for call in mock_client.return_value.request.call_args_list]
            self.assertFalse(any("/site-actions/v1/sites/duplicate" in url for url in calls))
        finally:
            Path(plan_path).unlink()

    @patch("wix_safe_agent_cli.commands.site_actions.HttpClient")
    def test_site_actions_duplicate_apply_request_payload_and_verification(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"sites": [{"id": "source-1", "displayName": "Original"}]}),
            _DummyResponse({"sites": [{"id": "source-1", "displayName": "Original"}]}),
            _DummyResponse({"newSiteId": "new-1"}),
            _DummyResponse({"sites": [{"id": "new-1", "displayName": "Copy"}]}),
        ]

        args = SimpleNamespace(source_site_id="source-1", site_display_name="Copy")
        ctx = self._ctx(apply=True, yes=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = site_actions.cmd_site_actions_duplicate(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertFalse(payload["dry_run"])
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["method"], "site-actions.duplicate")

        calls = mock_client.return_value.request.call_args_list
        duplicate_calls = [call for call in calls if str(call.kwargs.get("url", "")).endswith("/site-actions/v1/sites/duplicate")]
        self.assertEqual(len(duplicate_calls), 1)
        duplicate_call = duplicate_calls[0]
        self.assertEqual(duplicate_call.kwargs["method"], "POST")
        self.assertEqual(
            duplicate_call.kwargs["json_body"],
            {"sourceSiteId": "source-1", "siteDisplayName": "Copy"},
        )
        duplicate_headers = duplicate_call.kwargs["headers"]
        self.assertEqual(duplicate_headers["Authorization"], "acct-api-key")
        self.assertEqual(duplicate_headers["wix-account-id"], "acct-001")
        self.assertEqual(duplicate_headers["Content-Type"], "application/json")

        query_calls = [call for call in calls if str(call.kwargs.get("url", "")).endswith("/site-list/v2/sites/query")]
        self.assertEqual(len(query_calls), 3)
        self.assertEqual(query_calls[2].kwargs["json_body"]["query"]["filter"]["id"]["$in"], ["new-1"])

        verification = payload["receipt"]["verification"]
        self.assertTrue(verification["ok"])
        self.assertEqual(verification["newSiteId"], "new-1")
        self.assertEqual(verification["new_site"]["id"], "new-1")

    @patch("wix_safe_agent_cli.commands.site_actions.HttpClient")
    def test_site_actions_duplicate_apply_missing_new_site_id_is_validation_error(
        self, mock_client: unittest.mock.MagicMock
    ) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"sites": [{"id": "source-1", "displayName": "Original"}]}),
            _DummyResponse({"sites": [{"id": "source-1", "displayName": "Original"}]}),
            _DummyResponse({}),
        ]

        args = SimpleNamespace(source_site_id="source-1", site_display_name="Copy")
        ctx = self._ctx(apply=True, yes=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = site_actions.cmd_site_actions_duplicate(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("newSiteId", payload["error"])

    @patch("wix_safe_agent_cli.commands.site_actions.HttpClient")
    def test_site_actions_duplicate_apply_writes_receipt_out(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"sites": [{"id": "source-1", "displayName": "Original"}]}),
            _DummyResponse({"sites": [{"id": "source-1", "displayName": "Original"}]}),
            _DummyResponse({"newSiteId": "new-1"}),
            _DummyResponse({"sites": [{"id": "new-1", "displayName": "Copy"}]}),
        ]

        args = SimpleNamespace(source_site_id="source-1", site_display_name="Copy")
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as handle:
            receipt_path = handle.name

        try:
            ctx = self._ctx(apply=True, yes=True, receipt_out=receipt_path)

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = site_actions.cmd_site_actions_duplicate(args, ctx)
            payload = json.loads(buf.getvalue())

            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["receipt_out"], receipt_path)

            stored_receipt = json.loads(Path(receipt_path).read_text(encoding="utf-8"))
            self.assertEqual(stored_receipt["method"], "site-actions.duplicate")
            self.assertEqual(stored_receipt["verification"]["newSiteId"], "new-1")
        finally:
            Path(receipt_path).unlink()
