from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import crm_pipelines
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = action, payload


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestCrmPipelinesCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli crm-pipelines",
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

    def test_parser_exposes_crm_pipelines_commands(self) -> None:
        parser = build_parser()
        cases = [
            (["crm-pipelines", "create", "--pipeline-json", '{"pipeline":{"name":"Sales","stages":[{"name":"New"}],"doneStage":{"allowedOutcomes":["WON"]}}}'], "create", True),
            (["crm-pipelines", "get", "--pipeline-id", "pipe-1"], "get", False),
            (["crm-pipelines", "update", "--pipeline-json", '{"pipeline":{"id":"pipe-1","revision":"1","name":"Sales"}}'], "update", True),
            (["crm-pipelines", "delete", "--pipeline-id", "pipe-1"], "delete", True),
            (["crm-pipelines", "query"], "query", False),
            (["crm-pipelines", "bulk-update-tags", "--tags-json", '{"pipelineIds":["pipe-1"],"assignTags":["hot"]}'], "bulk-update-tags", True),
            (
                ["crm-pipelines", "bulk-update-tags-by-filter", "--tags-json", '{"filter":{"name":{"$startsWith":"Sales"}},"assignTags":["hot"]}'],
                "bulk-update-tags-by-filter",
                True,
            ),
        ]
        for argv, command, write_capable in cases:
            with self.subTest(command=command):
                args = parser.parse_args(argv)
                self.assertEqual(args.crm_pipelines_cmd, command)
                self.assertEqual(args.write_capable, write_capable)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_reads_use_official_paths(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"ok": True})

        cases = [
            (
                crm_pipelines.cmd_crm_pipelines_get,
                SimpleNamespace(pipeline_id="pipe-1"),
                "GET",
                "/crm/pipelines/v1/pipelines/pipe-1",
                None,
            ),
            (
                crm_pipelines.cmd_crm_pipelines_query,
                SimpleNamespace(query_json=None),
                "POST",
                "/crm/pipelines/v1/pipelines/query",
                {"query": {"sort": [{"fieldName": "updatedDate", "order": "DESC"}], "paging": {"limit": 50}}},
            ),
        ]
        for func, args, http_method, path, body in cases:
            with self.subTest(path=path):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertEqual(payload["request"]["method"], http_method)
                self.assertEqual(payload["request"]["path"], path)
                if body is not None:
                    self.assertEqual(payload["request"]["body"], body)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_plan_first_writes_use_official_paths(self, mock_client: unittest.mock.MagicMock) -> None:
        cases = [
            (
                crm_pipelines.cmd_crm_pipelines_create,
                SimpleNamespace(pipeline_json='{"pipeline":{"name":"Sales","stages":[{"name":"New"}],"doneStage":{"allowedOutcomes":["WON"]}}}'),
                "POST",
                "/crm/pipelines/v1/pipelines",
                False,
            ),
            (
                crm_pipelines.cmd_crm_pipelines_update,
                SimpleNamespace(pipeline_json='{"pipeline":{"id":"pipe-1","revision":"1","name":"Sales"}}'),
                "PATCH",
                "/crm/pipelines/v1/pipelines/pipe-1",
                False,
            ),
            (
                crm_pipelines.cmd_crm_pipelines_delete,
                SimpleNamespace(pipeline_id="pipe-1"),
                "DELETE",
                "/crm/pipelines/v1/pipelines/pipe-1",
                True,
            ),
            (
                crm_pipelines.cmd_crm_pipelines_bulk_update_tags,
                SimpleNamespace(tags_json='{"pipelineIds":["pipe-1"],"assignTags":["hot"]}'),
                "POST",
                "/crm/pipelines/v1/bulk/pipelines/update-tags",
                False,
            ),
            (
                crm_pipelines.cmd_crm_pipelines_bulk_update_tags_by_filter,
                SimpleNamespace(tags_json='{"filter":{"name":{"$startsWith":"Sales"}},"assignTags":["hot"]}'),
                "POST",
                "/crm/pipelines/v1/bulk/pipelines/update-tags-by-filter",
                True,
            ),
        ]
        for func, args, http_method, path, needs_ack in cases:
            with self.subTest(path=path):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertTrue(payload["dry_run"])
                self.assertEqual(payload["plan"]["request"]["method"], http_method)
                self.assertEqual(payload["plan"]["request"]["path"], path)
                if needs_ack:
                    self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
                else:
                    self.assertNotIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
                self.assertFalse(mock_client.return_value.request.called)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_validates_required_fields(self, mock_client: unittest.mock.MagicMock) -> None:
        cases = [
            (crm_pipelines.cmd_crm_pipelines_create, SimpleNamespace(pipeline_json='{"name":"Sales"}'), "pipeline"),
            (crm_pipelines.cmd_crm_pipelines_update, SimpleNamespace(pipeline_json='{"pipeline":{"revision":"1"}}'), "pipeline.id"),
            (crm_pipelines.cmd_crm_pipelines_update, SimpleNamespace(pipeline_json='{"pipeline":{"id":"pipe-1"}}'), "pipeline.revision"),
            (crm_pipelines.cmd_crm_pipelines_get, SimpleNamespace(pipeline_id=""), "--pipeline-id"),
            (crm_pipelines.cmd_crm_pipelines_delete, SimpleNamespace(pipeline_id=None), "--pipeline-id"),
            (crm_pipelines.cmd_crm_pipelines_bulk_update_tags, SimpleNamespace(tags_json='{"assignTags":["hot"]}'), "pipelineIds"),
            (crm_pipelines.cmd_crm_pipelines_bulk_update_tags, SimpleNamespace(tags_json='{"pipelineIds":["pipe-1"]}'), "assignTags or unassignTags"),
            (
                crm_pipelines.cmd_crm_pipelines_bulk_update_tags_by_filter,
                SimpleNamespace(tags_json='{"filter":{"name":{"$startsWith":"Sales"}}}'),
                "assignTags or unassignTags",
            ),
        ]
        for func, args, expected_error in cases:
            with self.subTest(expected_error=expected_error):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 1)
                self.assertEqual(payload["error_type"], "ValidationError")
                self.assertIn(expected_error, payload["error"])
                self.assertFalse(mock_client.return_value.request.called)
