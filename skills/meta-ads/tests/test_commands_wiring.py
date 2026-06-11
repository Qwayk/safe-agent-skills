from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest import mock

from meta_ads_api_tool.cli import build_parser, main
from meta_ads_api_tool.commands import snapshot as snapshot_cmd
from meta_ads_api_tool.output import Output


class TestCommandsWiring(unittest.TestCase):
    def _ctx(self):
        return {
            "cfg": SimpleNamespace(ad_account_id=None),
            "out": Output(mode="json"),
            "audit": mock.Mock(),
            "graph": mock.Mock(),
        }

    def test_ad_accounts_list_calls_graph(self) -> None:
        p = build_parser()
        args = p.parse_args(["ad-accounts", "list", "--fields", "id,name", "--max-pages", "2"])

        ctx = self._ctx()
        ctx["graph"].list_me_adaccounts.return_value = SimpleNamespace(data=[{"id": "1"}], paging=None, raw_pages=1)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = args.func(args, ctx)
        self.assertEqual(rc, 0)
        ctx["graph"].list_me_adaccounts.assert_called_once()
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertIn("ad_accounts_list", payload)

    def test_campaigns_list_calls_list_edge(self) -> None:
        p = build_parser()
        args = p.parse_args(["campaigns", "list", "--ad-account-id", "123", "--fields", "id,name", "--max-items", "10"])

        ctx = self._ctx()
        ctx["graph"].list_edge.return_value = SimpleNamespace(data=[], paging=None, raw_pages=1)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = args.func(args, ctx)
        self.assertEqual(rc, 0)
        ctx["graph"].list_edge.assert_called_once()
        call = ctx["graph"].list_edge.call_args.kwargs
        self.assertEqual(call["object_id"], "act_123")
        self.assertEqual(call["edge"], "campaigns")
        self.assertIn("fields", call["params"])
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertIn("campaigns_list", payload)

    def test_graph_command_is_removed_is_json_validation_error(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["--output", "json", "graph", "get", "--object-id", "me"])
        self.assertEqual(rc, 1)
        payload = json.loads(buf.getvalue())
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")

    def test_insights_get_calls_list_edge(self) -> None:
        p = build_parser()
        args = p.parse_args(
            [
                "insights",
                "get",
                "--ad-account-id",
                "act_55",
                "--level",
                "campaign",
                "--fields",
                "impressions,clicks",
                "--since",
                "2026-01-01",
                "--until",
                "2026-01-31",
                "--breakdown",
                "age",
            ]
        )

        ctx = self._ctx()
        ctx["graph"].list_edge.return_value = SimpleNamespace(data=[], paging=None, raw_pages=1)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = args.func(args, ctx)
        self.assertEqual(rc, 0)

        ctx["graph"].list_edge.assert_called_once()
        call = ctx["graph"].list_edge.call_args.kwargs
        self.assertEqual(call["object_id"], "act_55")
        self.assertEqual(call["edge"], "insights")
        self.assertEqual(call["params"]["level"], "campaign")
        self.assertIn("time_range", call["params"])
        self.assertEqual(call["params"]["breakdowns"], "age")
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertIn("insights_get", payload)

    def test_insights_compare_calls_list_edge_twice(self) -> None:
        p = build_parser()
        args = p.parse_args(
            [
                "insights",
                "compare",
                "--ad-account-id",
                "act_55",
                "--level",
                "campaign",
                "--fields",
                "campaign_id,impressions,spend",
                "--since-a",
                "2026-01-01",
                "--until-a",
                "2026-01-07",
                "--since-b",
                "2026-01-08",
                "--until-b",
                "2026-01-14",
                "--time-increment",
                "1",
                "--action-breakdown",
                "action_type",
                "--action-attribution-window",
                "7d_click",
            ]
        )

        ctx = self._ctx()
        ctx["graph"].list_edge.side_effect = [
            SimpleNamespace(data=[{"id": "a"}], paging=None, raw_pages=1),
            SimpleNamespace(data=[{"id": "b"}], paging=None, raw_pages=1),
        ]
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = args.func(args, ctx)
        self.assertEqual(rc, 0)

        self.assertEqual(ctx["graph"].list_edge.call_count, 2)
        first_call = ctx["graph"].list_edge.call_args_list[0].kwargs
        second_call = ctx["graph"].list_edge.call_args_list[1].kwargs
        self.assertEqual(first_call["object_id"], "act_55")
        self.assertEqual(first_call["edge"], "insights")
        self.assertEqual(second_call["object_id"], "act_55")
        self.assertEqual(second_call["edge"], "insights")
        self.assertEqual(first_call["params"]["level"], "campaign")
        self.assertIn("time_range", first_call["params"])
        self.assertIn("time_range", second_call["params"])
        self.assertEqual(first_call["params"]["time_increment"], "1")
        self.assertEqual(first_call["params"]["action_breakdowns"], "action_type")
        self.assertEqual(first_call["params"]["action_attribution_windows"], "7d_click")

        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertIn("insights_compare", payload)
        self.assertEqual(payload["count"]["a"], 1)
        self.assertEqual(payload["count"]["b"], 1)

    def test_creatives_anatomy_calls_graph_get(self) -> None:
        p = build_parser()
        args = p.parse_args(["creatives", "anatomy", "--creative-id", "cr_1", "--fields", "id,object_story_spec"])
        ctx = self._ctx()
        ctx["graph"].get.return_value = {
            "id": "cr_1",
            "object_story_spec": {
                "page_id": "p_1",
                "link_data": {
                    "message": "Hello",
                    "name": "Headline",
                    "description": "Desc",
                    "link": "https://example.com/?access_token=SECRET",
                    "picture": "https://cdn.example.com/a.jpg",
                },
            },
        }
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = args.func(args, ctx)
        self.assertEqual(rc, 0)
        ctx["graph"].get.assert_called_once()
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertIn("creatives_anatomy", payload)
        self.assertEqual(payload["anatomy"]["creative_id"], "cr_1")
        self.assertIn("***REDACTED***", payload["anatomy"]["urls"][0])

    def test_previews_get_calls_list_edge_and_redacts_urls(self) -> None:
        p = build_parser()
        args = p.parse_args(
            [
                "previews",
                "get",
                "--creative-id",
                "cr_9",
                "--ad-format",
                "DESKTOP_FEED_STANDARD",
            ]
        )
        ctx = self._ctx()
        ctx["graph"].list_edge.return_value = SimpleNamespace(
            data=[{"body": "https://example.com/?access_token=SECRET"}],
            paging={"next": "https://graph.example.com/?access_token=SECRET"},
            raw_pages=1,
        )
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = args.func(args, ctx)
        self.assertEqual(rc, 0)
        ctx["graph"].list_edge.assert_called_once()
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertIn("***REDACTED***", payload["data"][0]["body"])

    def test_presets_list_emits_json(self) -> None:
        p = build_parser()
        args = p.parse_args(["presets", "list"])

        ctx = self._ctx()
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = args.func(args, ctx)
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertIn("presets_list", payload)
        self.assertIn("presets", payload)

    def test_presets_show_emits_json(self) -> None:
        p = build_parser()
        args = p.parse_args(["presets", "show", "--preset", "ecom_core"])

        ctx = self._ctx()
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = args.func(args, ctx)
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertIn("presets_show", payload)
        self.assertEqual(payload["preset"]["id"], "ecom_core")

    def test_snapshot_export_is_wired(self) -> None:
        p = build_parser()
        args = p.parse_args(["snapshot", "export", "--ad-account-id", "act_1", "--preset", "ecom_core", "--out-dir", "/tmp"])
        self.assertIs(args.func, snapshot_cmd.cmd_snapshot_export)
