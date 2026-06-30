from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import crm_cards
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = action, payload


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestCrmCardsCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli crm-cards",
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

    def test_parser_exposes_crm_cards_commands(self) -> None:
        parser = build_parser()
        cases = [
            (["crm-cards", "create", "--card-json", '{"card":{"name":"Lead","pipelineId":"pipe-1","stageId":"stage-1"}}'], "create", True),
            (["crm-cards", "get", "--card-id", "card-1"], "get", False),
            (["crm-cards", "update", "--card-json", '{"card":{"id":"card-1","revision":"1","name":"Lead"}}'], "update", True),
            (["crm-cards", "delete", "--card-id", "card-1"], "delete", True),
            (["crm-cards", "query"], "query", False),
            (["crm-cards", "search"], "search", False),
            (["crm-cards", "bulk-update-tags", "--tags-json", '{"cardIds":["card-1"],"assignTags":["hot"]}'], "bulk-update-tags", True),
            (
                ["crm-cards", "bulk-update-tags-by-filter", "--tags-json", '{"pipelineId":"pipe-1","filter":{"name":{"$startsWith":"A"}},"assignTags":["hot"]}'],
                "bulk-update-tags-by-filter",
                True,
            ),
            (["crm-cards", "move", "--card-id", "card-1", "--move-json", '{"stageId":"stage-2"}'], "move", True),
            (
                ["crm-cards", "search-by-stage", "--search-json", '{"pipelineId":"pipe-1","stageId":"stage-1"}'],
                "search-by-stage",
                False,
            ),
        ]
        for argv, command, write_capable in cases:
            with self.subTest(command=command):
                args = parser.parse_args(argv)
                self.assertEqual(args.crm_cards_cmd, command)
                self.assertEqual(args.write_capable, write_capable)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_reads_use_official_paths(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"ok": True})

        cases = [
            (
                crm_cards.cmd_crm_cards_get,
                SimpleNamespace(card_id="card-1"),
                "GET",
                "/crm/pipelines/v1/cards/card-1",
                None,
            ),
            (
                crm_cards.cmd_crm_cards_query,
                SimpleNamespace(query_json=None),
                "POST",
                "/crm/pipelines/v1/cards/query",
                {"query": {"sort": [{"fieldName": "updatedDate", "order": "DESC"}], "paging": {"limit": 50}}},
            ),
            (
                crm_cards.cmd_crm_cards_search,
                SimpleNamespace(search_json=None),
                "POST",
                "/crm/pipelines/v1/cards/search",
                {"search": {"sort": [{"fieldName": "updatedDate", "order": "DESC"}], "paging": {"limit": 50}}},
            ),
            (
                crm_cards.cmd_crm_cards_search_by_stage,
                SimpleNamespace(search_json='{"pipelineId":"pipe-1","stageId":"stage-1"}'),
                "POST",
                "/crm/pipelines/v1/cards/search-by-stage",
                {"pipelineId": "pipe-1", "stageId": "stage-1"},
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
                crm_cards.cmd_crm_cards_create,
                SimpleNamespace(card_json='{"card":{"name":"Lead","pipelineId":"pipe-1","stageId":"stage-1"}}'),
                "POST",
                "/crm/pipelines/v1/cards",
                False,
            ),
            (
                crm_cards.cmd_crm_cards_update,
                SimpleNamespace(card_json='{"card":{"id":"card-1","revision":"1","name":"Lead"}}'),
                "PATCH",
                "/crm/pipelines/v1/cards/card-1",
                False,
            ),
            (
                crm_cards.cmd_crm_cards_delete,
                SimpleNamespace(card_id="card-1"),
                "DELETE",
                "/crm/pipelines/v1/cards/card-1",
                True,
            ),
            (
                crm_cards.cmd_crm_cards_bulk_update_tags,
                SimpleNamespace(tags_json='{"cardIds":["card-1"],"assignTags":["hot"]}'),
                "POST",
                "/crm/pipelines/v1/bulk/cards/update-tags",
                False,
            ),
            (
                crm_cards.cmd_crm_cards_bulk_update_tags_by_filter,
                SimpleNamespace(tags_json='{"pipelineId":"pipe-1","filter":{"name":{"$startsWith":"Lead"}},"assignTags":["hot"]}'),
                "POST",
                "/crm/pipelines/v1/bulk/cards/update-tags-by-filter",
                True,
            ),
            (
                crm_cards.cmd_crm_cards_move,
                SimpleNamespace(card_id="card-1", move_json='{"stageId":"stage-2"}'),
                "PATCH",
                "/crm/pipelines/v1/cards/move/card-1",
                False,
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
            (crm_cards.cmd_crm_cards_create, SimpleNamespace(card_json='{"name":"Lead"}'), "card"),
            (crm_cards.cmd_crm_cards_update, SimpleNamespace(card_json='{"card":{"revision":"1"}}'), "card.id"),
            (crm_cards.cmd_crm_cards_update, SimpleNamespace(card_json='{"card":{"id":"card-1"}}'), "card.revision"),
            (crm_cards.cmd_crm_cards_get, SimpleNamespace(card_id=""), "--card-id"),
            (crm_cards.cmd_crm_cards_delete, SimpleNamespace(card_id=None), "--card-id"),
            (crm_cards.cmd_crm_cards_bulk_update_tags, SimpleNamespace(tags_json='{"assignTags":["hot"]}'), "cardIds"),
            (crm_cards.cmd_crm_cards_bulk_update_tags, SimpleNamespace(tags_json='{"cardIds":["card-1"]}'), "assignTags or unassignTags"),
            (
                crm_cards.cmd_crm_cards_bulk_update_tags_by_filter,
                SimpleNamespace(tags_json='{"filter":{"name":{"$startsWith":"Lead"}},"assignTags":["hot"]}'),
                "pipelineId",
            ),
            (
                crm_cards.cmd_crm_cards_bulk_update_tags_by_filter,
                SimpleNamespace(tags_json='{"pipelineId":"pipe-1","filter":{"name":{"$startsWith":"Lead"}}}'),
                "assignTags or unassignTags",
            ),
            (crm_cards.cmd_crm_cards_move, SimpleNamespace(card_id="", move_json='{"stageId":"stage-2"}'), "--card-id"),
            (crm_cards.cmd_crm_cards_search_by_stage, SimpleNamespace(search_json="{}"), "--search-json"),
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
