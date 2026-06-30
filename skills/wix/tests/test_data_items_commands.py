from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.commands import data_items
from wix_safe_agent_cli.cli import build_parser
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


class TestDataItemsCommands(unittest.TestCase):
    def _ctx(self, *, cfg_override: dict | None = None, verbose: bool = False, **overrides) -> dict:
        cfg = SimpleNamespace(
            base_url="https://www.wixapis.com",
            timeout_s=30.0,
            app_id=None,
            app_secret=None,
            instance_id=None,
            access_token="token-abc",
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
            "command_str": "wix-safe-agent-cli data-items",
            "apply": False,
            "yes": False,
            "verbose": verbose,
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
            "plan_in": None,
            "plan_out": None,
            "receipt_out": None,
            "ack_irreversible": False,
        }
        ctx.update(overrides)
        return ctx

    @patch("wix_safe_agent_cli.commands.data_items.HttpClient")
    def test_data_items_get_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"dataItem": {"id": "i1"}})
        args = SimpleNamespace(
            data_item_id="item-1",
            data_collection_id="cities",
            consistent_read=True,
            language="en-US",
            fields_json='["state","year"]',
            include_references_json='{"field":"author"}',
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_items.cmd_data_items_get(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(payload["request"]["path"], "/wix-data/v2/items/item-1")
        params = payload["request"]["params"]
        self.assertEqual(params["dataCollectionId"], "cities")
        self.assertTrue(params["consistentRead"])
        self.assertEqual(params["language"], "en-US")
        self.assertEqual(params["fields"], ["state", "year"])
        self.assertEqual(params["includeReferences"], [{"field": "author"}])

    @patch("wix_safe_agent_cli.commands.data_items.HttpClient")
    def test_data_items_query_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"dataItems": [], "pagingMetadata": {"count": 0}})
        args = SimpleNamespace(
            data_collection_id="posts",
            query_json=None,
            filter_json='{"state":"California"}',
            sort_json='{"fieldName":"createdDate","order":"DESC"}',
            fields_json='["title","body"]',
            include_references_json='[{"field":"author","limit":3}]',
            include_field_groups_json='["FULL"]',
            language="en-US",
            limit=5,
            offset=10,
            cursor=None,
            return_total_count=True,
            consistent_read=False,
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_items.cmd_data_items_query(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["method"], "POST")
        self.assertEqual(payload["request"]["path"], "/wix-data/v2/items/query")
        body = payload["request"]["body"]
        self.assertEqual(body["dataCollectionId"], "posts")
        self.assertEqual(body["query"]["filter"]["state"], "California")
        self.assertEqual(body["query"]["paging"], {"limit": 5, "offset": 10})
        self.assertEqual(body["query"]["fields"], ["title", "body"])
        self.assertEqual(body["query"]["includeFieldGroups"], ["FULL"])
        self.assertEqual(body["query"]["includeReferences"], [{"field": "author", "limit": 3}])
        self.assertTrue(body["query"]["returnTotalCount"])
        self.assertEqual(body["language"], "en-US")

    @patch("wix_safe_agent_cli.commands.data_items.HttpClient")
    def test_data_items_count_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"totalCount": 4})
        args = SimpleNamespace(
            data_collection_id="posts",
            query_json=None,
            filter_json='{"state":"California"}',
            language="en-US",
            consistent_read=True,
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_items.cmd_data_items_count(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["method"], "POST")
        self.assertEqual(payload["request"]["path"], "/wix-data/v2/items/count")
        body = payload["request"]["body"]
        self.assertEqual(body["dataCollectionId"], "posts")
        self.assertEqual(body["filter"]["state"], "California")
        self.assertTrue(body["consistentRead"])
        self.assertEqual(body["language"], "en-US")

    @patch("wix_safe_agent_cli.commands.data_items.HttpClient")
    def test_data_items_aggregate_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"results": []})
        args = SimpleNamespace(
            data_collection_id="cities",
            aggregation_json='{"operations":[{"sum":"population"}]}',
            initial_filter_json='{"state":"California"}',
            final_filter_json='{"totalPopulation":{"$gt":1000000}}',
            sort_json='{"fieldName":"state","order":"ASC"}',
            app_options_json='{"includeHiddenProducts": true}',
            language="en-US",
            limit=10,
            offset=None,
            cursor=None,
            return_total_count=True,
            consistent_read=True,
            include_draft_items=True,
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_items.cmd_data_items_aggregate(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["method"], "POST")
        self.assertEqual(payload["request"]["path"], "/wix-data/v2/items/aggregate")
        body = payload["request"]["body"]
        self.assertEqual(body["dataCollectionId"], "cities")
        self.assertEqual(body["aggregation"]["operations"], [{"sum": "population"}])
        self.assertEqual(body["initialFilter"]["state"], "California")
        self.assertEqual(body["finalFilter"]["totalPopulation"]["$gt"], 1000000)
        self.assertEqual(body["sort"]["fieldName"], "state")
        self.assertEqual(body["appOptions"], {"includeHiddenProducts": True})
        self.assertEqual(body["paging"]["limit"], 10)
        self.assertTrue(body["returnTotalCount"])
        self.assertTrue(body["consistentRead"])
        self.assertEqual(body["publishPluginOptions"], {"includeDraftItems": True})

    @patch("wix_safe_agent_cli.commands.data_items.HttpClient")
    def test_data_items_aggregate_rejects_non_object_aggregation(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({})
        args = SimpleNamespace(
            data_collection_id="cities",
            aggregation_json='["not-object"]',
            initial_filter_json=None,
            final_filter_json=None,
            sort_json=None,
            app_options_json=None,
            language=None,
            limit=None,
            offset=None,
            cursor=None,
            return_total_count=False,
            consistent_read=False,
            include_draft_items=False,
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_items.cmd_data_items_aggregate(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")

    @patch("wix_safe_agent_cli.commands.data_items.HttpClient")
    def test_data_items_aggregate_pipeline_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"results": []})
        args = SimpleNamespace(
            data_collection_id="cities",
            pipeline_json='{"stages":[{"filter":{"state":"CA"}}],"paging":{"limit":25}}',
            app_options_json='{"includeHiddenProducts": true}',
            language="en-US",
            return_total_count=True,
            consistent_read=True,
            include_draft_items=True,
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_items.cmd_data_items_aggregate_pipeline(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["method"], "POST")
        self.assertEqual(payload["request"]["path"], "/wix-data/v2/items/aggregate-pipeline")
        body = payload["request"]["body"]
        self.assertEqual(body["dataCollectionId"], "cities")
        self.assertEqual(body["pipeline"]["stages"][0]["filter"], {"state": "CA"})
        self.assertEqual(body["pipeline"]["paging"]["limit"], 25)
        self.assertEqual(body["language"], "en-US")
        self.assertEqual(body["appOptions"], {"includeHiddenProducts": True})
        self.assertTrue(body["returnTotalCount"])
        self.assertTrue(body["consistentRead"])
        self.assertEqual(body["publishPluginOptions"], {"includeDraftItems": True})

    @patch("wix_safe_agent_cli.commands.data_items.HttpClient")
    def test_data_items_distinct_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"distinctValues": ["CA", "NY"]})
        args = SimpleNamespace(
            data_collection_id="cities",
            field_name="state",
            filter_json='{"country":"US"}',
            order="ASC",
            language="en-US",
            limit=100,
            offset=0,
            cursor=None,
            return_total_count=True,
            consistent_read=True,
            include_draft_items=True,
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_items.cmd_data_items_distinct(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["method"], "POST")
        self.assertEqual(payload["request"]["path"], "/wix-data/v2/items/query-distinct-values")
        body = payload["request"]["body"]
        self.assertEqual(body["dataCollectionId"], "cities")
        self.assertEqual(body["fieldName"], "state")
        self.assertEqual(body["filter"]["country"], "US")
        self.assertEqual(body["order"], "ASC")
        self.assertEqual(body["paging"], {"limit": 100, "offset": 0})
        self.assertEqual(body["returnTotalCount"], True)
        self.assertEqual(body["consistentRead"], True)
        self.assertEqual(body["publishPluginOptions"], {"includeDraftItems": True})
        self.assertEqual(payload["response"]["distinctValues"], ["CA", "NY"])

    @patch("wix_safe_agent_cli.commands.data_items.HttpClient")
    def test_data_items_distinct_rejects_missing_field(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({})
        args = SimpleNamespace(
            data_collection_id="cities",
            field_name="",
            filter_json=None,
            order=None,
            language=None,
            limit=None,
            offset=None,
            cursor=None,
            return_total_count=False,
            consistent_read=False,
            include_draft_items=False,
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_items.cmd_data_items_distinct(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")

    @patch("wix_safe_agent_cli.commands.data_items.HttpClient")
    def test_data_items_search_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"dataItems": [{"id": "x1"}]})
        args = SimpleNamespace(
            data_collection_id="cities",
            search_json='{"filter":{"state":"CA"},"sort":[{"fieldName":"population","order":"DESC"}],"fields":["city","state"],"search":{"expression":"Francisco","mode":"AND"},"paging":{"limit":5}}',
            include_references_json='[{"field":"author"}]',
            referenced_item_options_json='[{"fieldName":"author","limit":3}]',
            include_draft_items=True,
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_items.cmd_data_items_search(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["method"], "POST")
        self.assertEqual(payload["request"]["path"], "/wix-data/v2/items/search")
        body = payload["request"]["body"]
        self.assertEqual(body["dataCollectionId"], "cities")
        self.assertEqual(body["search"]["search"]["expression"], "Francisco")
        self.assertEqual(body["search"]["filter"]["state"], "CA")
        self.assertEqual(body["search"]["sort"][0]["fieldName"], "population")
        self.assertEqual(body["search"]["fields"], ["city", "state"])
        self.assertEqual(body["search"]["paging"]["limit"], 5)
        self.assertEqual(body["includeReferences"], [{"field": "author"}])
        self.assertEqual(body["referencedItemOptions"], [{"fieldName": "author", "limit": 3}])
        self.assertEqual(body["publishPluginOptions"], {"includeDraftItems": True})

    @patch("wix_safe_agent_cli.commands.data_items.HttpClient")
    def test_data_items_search_rejects_non_object_search_json(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({})
        args = SimpleNamespace(
            data_collection_id="cities",
            search_json='[]',
            include_references_json=None,
            referenced_item_options_json=None,
            include_draft_items=False,
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_items.cmd_data_items_search(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")

    @patch("wix_safe_agent_cli.commands.data_items.HttpClient")
    def test_data_items_query_rejects_cursor_and_offset_together(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({})
        args = SimpleNamespace(
            data_collection_id="posts",
            query_json=None,
            filter_json=None,
            sort_json=None,
            fields_json=None,
            include_references_json=None,
            include_field_groups_json=None,
            language=None,
            limit=5,
            offset=10,
            cursor="cursor-1",
            return_total_count=False,
            consistent_read=False,
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_items.cmd_data_items_query(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")

    @patch("wix_safe_agent_cli.commands.data_items.HttpClient")
    def test_data_items_query_referenced_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"results": [], "pagingMetadata": {"count": 0}})
        args = SimpleNamespace(
            data_collection_id="posts",
            referring_item_field_name="author",
            referring_item_id="post-1",
            fields_json='["title","slug"]',
            language="en-US",
            order="ASC",
            limit=5,
            offset=None,
            cursor="cursor-1",
            return_total_count=True,
            consistent_read=True,
            include_draft_items=True,
            include_hidden_products=True,
            include_variants=False,
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_items.cmd_data_items_query_referenced(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["method"], "POST")
        self.assertEqual(payload["request"]["path"], "/wix-data/v2/items/query-referenced")
        body = payload["request"]["body"]
        self.assertEqual(body["dataCollectionId"], "posts")
        self.assertEqual(body["referringItemFieldName"], "author")
        self.assertEqual(body["referringItemId"], "post-1")
        self.assertEqual(body["fields"], ["title", "slug"])
        self.assertEqual(body["language"], "en-US")
        self.assertEqual(body["order"], "ASC")
        self.assertEqual(body["cursorPaging"], {"cursor": "cursor-1", "limit": 5})
        self.assertEqual(body["returnTotalCount"], True)
        self.assertEqual(body["publishPluginOptions"]["includeDraftItems"], True)
        self.assertEqual(body["appOptions"]["includeHiddenProducts"], True)
        self.assertTrue(payload["response"].get("results") == [])

    @patch("wix_safe_agent_cli.commands.data_items.HttpClient")
    def test_data_items_query_referenced_rejects_cursor_and_offset_together(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({})
        args = SimpleNamespace(
            data_collection_id="posts",
            referring_item_field_name="author",
            referring_item_id="post-1",
            fields_json=None,
            language=None,
            order=None,
            limit=5,
            offset=2,
            cursor="cursor-1",
            return_total_count=False,
            consistent_read=False,
            include_draft_items=False,
            include_hidden_products=False,
            include_variants=False,
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_items.cmd_data_items_query_referenced(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")

    @patch("wix_safe_agent_cli.commands.data_items.HttpClient")
    def test_data_items_is_referenced_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"isReferenced": True})
        args = SimpleNamespace(
            data_collection_id="posts",
            referring_item_field_name="author",
            referring_item_id="post-1",
            referenced_item_id="author-1",
            consistent_read=True,
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_items.cmd_data_items_is_referenced(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["method"], "POST")
        self.assertEqual(payload["request"]["path"], "/wix-data/v2/items/is-referenced")
        body = payload["request"]["body"]
        self.assertEqual(body["dataCollectionId"], "posts")
        self.assertEqual(body["referringItemFieldName"], "author")
        self.assertEqual(body["referringItemId"], "post-1")
        self.assertEqual(body["referencedItemId"], "author-1")
        self.assertTrue(body["consistentRead"])

    @patch("wix_safe_agent_cli.commands.data_items.HttpClient")
    def test_data_items_insert_dry_run_emits_plan(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"dataItem": {"id": "i9"}})
        args = SimpleNamespace(
            data_collection_id="posts",
            data_item_json='{"id":"i9","name":"Alice"}',
            language="en-US",
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_items.cmd_data_items_insert(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["method"], "data-items.insert")
        self.assertTrue(payload["dry_run"])
        self.assertIn("plan", payload)
        self.assertNotIn("receipt", payload)
        self.assertEqual(payload["plan"]["method"], "data-items.insert")
        self.assertEqual(payload["plan"]["request"]["method"], "POST")
        self.assertEqual(payload["plan"]["request"]["path"], "/wix-data/v2/items")
        self.assertEqual(payload["plan"]["request"]["body"]["dataCollectionId"], "posts")
        self.assertEqual(payload["plan"]["selector"]["operation"], "insert")
        self.assertNotIn("language", payload["plan"]["request"]["body"])

    @patch("wix_safe_agent_cli.commands.data_items.HttpClient")
    def test_data_items_save_dry_run_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"dataItem": {"id": "i9"}})
        args = SimpleNamespace(
            data_collection_id="posts",
            data_item_json='{"id":"i9","name":"Alice"}',
            app_options_json='{"includeHiddenProducts":true}',
            include_draft_items=True,
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_items.cmd_data_items_save(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["method"], "data-items.save")
        self.assertTrue(payload["dry_run"])
        request = payload["plan"]["request"]
        self.assertEqual(request["method"], "POST")
        self.assertEqual(request["path"], "/wix-data/v2/items/save")
        self.assertEqual(request["body"]["dataCollectionId"], "posts")
        self.assertEqual(request["body"]["dataItem"]["id"], "i9")
        self.assertEqual(request["body"]["appOptions"], {"includeHiddenProducts": True})
        self.assertEqual(request["body"]["publishPluginOptions"], {"includeDraftItems": True})

    @patch("wix_safe_agent_cli.commands.data_items.HttpClient")
    def test_data_items_truncate_dry_run_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"totalCount": 5})
        args = SimpleNamespace(
            data_collection_id="posts",
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_items.cmd_data_items_truncate(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["method"], "data-items.truncate")
        self.assertTrue(payload["dry_run"])
        request = payload["plan"]["request"]
        self.assertEqual(request["method"], "POST")
        self.assertEqual(request["path"], "/wix-data/v2/items/truncate")
        self.assertEqual(request["body"], {"dataCollectionId": "posts"})
        self.assertEqual(payload["plan"]["baseline"]["before_state"], {"count": 5})

    @patch("wix_safe_agent_cli.commands.data_items.HttpClient")
    def test_data_items_bulk_save_dry_run_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.side_effect = [
            RuntimeError("HTTP 404 for https://www.wixapis.com/wix-data/v2/items/i1"),
            RuntimeError("HTTP 404 for https://www.wixapis.com/wix-data/v2/items/i2"),
        ]
        args = SimpleNamespace(
            data_collection_id="posts",
            data_items_json='[{"id":"i1","name":"Alice"},{"id":"i2","name":"Bob"}]',
            app_options_json='{"includeHiddenProducts":true}',
            include_draft_items=True,
            return_entity=True,
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_items.cmd_data_items_bulk_save(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["method"], "data-items.bulk-save")
        self.assertTrue(payload["dry_run"])
        request = payload["plan"]["request"]
        self.assertEqual(request["method"], "POST")
        self.assertEqual(request["path"], "/wix-data/v2/bulk/items/save")
        self.assertEqual(request["body"]["dataCollectionId"], "posts")
        self.assertEqual(request["body"]["returnEntity"], True)
        self.assertEqual(request["body"]["appOptions"], {"includeHiddenProducts": True})
        self.assertEqual(request["body"]["publishPluginOptions"], {"includeDraftItems": True})
        self.assertEqual(len(request["body"]["dataItems"]), 2)

    @patch("wix_safe_agent_cli.commands.data_items.HttpClient")
    def test_data_items_bulk_update_dry_run_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"dataItem": {"id": "i1", "count": 1}}),
            _DummyResponse({"dataItem": {"id": "i2", "count": 2}}),
        ]
        args = SimpleNamespace(
            data_collection_id="posts",
            data_items_json='[{"id":"i1","count":10},{"id":"i2","count":20}]',
            condition_json='{"filter":{"state":"published"}}',
            app_options_json='{"includeHiddenProducts":true}',
            include_draft_items=True,
            return_entity=True,
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_items.cmd_data_items_bulk_update(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["method"], "data-items.bulk-update")
        self.assertTrue(payload["dry_run"])
        request = payload["plan"]["request"]
        self.assertEqual(request["method"], "POST")
        self.assertEqual(request["path"], "/wix-data/v2/bulk/items/update")
        self.assertEqual(request["body"]["dataCollectionId"], "posts")
        self.assertEqual(request["body"]["condition"], {"filter": {"state": "published"}})
        self.assertEqual(request["body"]["appOptions"], {"includeHiddenProducts": True})
        self.assertEqual(request["body"]["publishPluginOptions"], {"includeDraftItems": True})
        self.assertEqual(request["body"]["returnEntity"], True)
        self.assertEqual(len(request["body"]["dataItems"]), 2)

    @patch("wix_safe_agent_cli.commands.data_items.HttpClient")
    def test_data_items_bulk_remove_dry_run_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"dataItem": {"id": "i1", "name": "Alice"}}),
            _DummyResponse({"dataItem": {"id": "i2", "name": "Bob"}}),
        ]
        args = SimpleNamespace(
            data_collection_id="posts",
            data_item_ids_json='["i1","i2"]',
            condition_json='{"filter":{"state":"archived"}}',
            app_options_json='{"includeHiddenProducts":true}',
            include_draft_items=True,
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_items.cmd_data_items_bulk_remove(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["method"], "data-items.bulk-remove")
        self.assertTrue(payload["dry_run"])
        request = payload["plan"]["request"]
        self.assertEqual(request["method"], "POST")
        self.assertEqual(request["path"], "/wix-data/v2/bulk/items/remove")
        self.assertEqual(request["body"]["dataCollectionId"], "posts")
        self.assertEqual(request["body"]["dataItemIds"], ["i1", "i2"])
        self.assertEqual(request["body"]["condition"], {"filter": {"state": "archived"}})
        self.assertEqual(request["body"]["appOptions"], {"includeHiddenProducts": True})
        self.assertEqual(request["body"]["publishPluginOptions"], {"includeDraftItems": True})

    @patch("wix_safe_agent_cli.commands.data_items.HttpClient")
    def test_data_items_bulk_insert_references_dry_run_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"isReferenced": False})
        args = SimpleNamespace(
            data_collection_id="posts",
            data_item_references_json='[{"referringItemFieldName":"author","referringItemId":"post-1","referencedItemId":"author-1"}]',
            return_entity=True,
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_items.cmd_data_items_bulk_insert_references(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["method"], "data-items.bulk-insert-references")
        self.assertTrue(payload["dry_run"])
        request = payload["plan"]["request"]
        self.assertEqual(request["method"], "POST")
        self.assertEqual(request["path"], "/wix-data/v2/bulk/items/insert-references")
        self.assertEqual(request["body"]["dataCollectionId"], "posts")
        self.assertEqual(request["body"]["returnEntity"], True)
        self.assertEqual(len(request["body"]["dataItemReferences"]), 1)
        self.assertEqual(request["body"]["dataItemReferences"][0]["referringItemFieldName"], "author")

    @patch("wix_safe_agent_cli.commands.data_items.HttpClient")
    def test_data_items_bulk_remove_references_dry_run_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"isReferenced": True})
        args = SimpleNamespace(
            data_collection_id="posts",
            data_item_references_json='[{"referringItemFieldName":"author","referringItemId":"post-1","referencedItemId":"author-1"}]',
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_items.cmd_data_items_bulk_remove_references(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["method"], "data-items.bulk-remove-references")
        self.assertTrue(payload["dry_run"])
        request = payload["plan"]["request"]
        self.assertEqual(request["method"], "POST")
        self.assertEqual(request["path"], "/wix-data/v2/bulk/items/remove-references")
        self.assertEqual(request["body"]["dataCollectionId"], "posts")
        self.assertEqual(len(request["body"]["dataItemReferences"]), 1)

    @patch("wix_safe_agent_cli.commands.data_items.HttpClient")
    def test_data_items_bulk_insert_dry_run_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"results": [], "bulkActionMetadata": {"successCount": 0, "failureCount": 0}})
        args = SimpleNamespace(
            data_collection_id="posts",
            data_items_json='[{"id":"i1","name":"Alice"},{"id":"i2","name":"Bob"}]',
            app_options_json='{"includeHiddenProducts":true}',
            return_entity=True,
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_items.cmd_data_items_bulk_insert(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["method"], "data-items.bulk-insert")
        self.assertTrue(payload["dry_run"])
        self.assertIn("plan", payload)
        self.assertEqual(payload["plan"]["method"], "data-items.bulk-insert")
        request = payload["plan"]["request"]
        self.assertEqual(request["method"], "POST")
        self.assertEqual(request["path"], "/wix-data/v2/bulk/items/insert")
        self.assertEqual(request["body"]["dataCollectionId"], "posts")
        self.assertEqual(request["body"]["returnEntity"], True)
        self.assertEqual(request["body"]["appOptions"], {"includeHiddenProducts": True})
        self.assertEqual(len(request["body"]["dataItems"]), 2)
        self.assertEqual(request["body"]["dataItems"][0]["id"], "i1")

    @patch("wix_safe_agent_cli.commands.data_items.HttpClient")
    def test_data_items_save_apply_without_plan_in_is_refused_before_http(self, mock_client: unittest.mock.MagicMock) -> None:
        args = SimpleNamespace(
            data_collection_id="posts",
            data_item_json='{"id":"i9","name":"Alice"}',
            app_options_json=None,
            include_draft_items=False,
        )
        ctx = self._ctx(apply=True, yes=True, enforce_reviewed_plan=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_items.cmd_data_items_save(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertEqual(payload["method"], "data-items.save")
        self.assertEqual(mock_client.return_value.request.call_count, 0)

    @patch("wix_safe_agent_cli.commands.data_items.HttpClient")
    def test_data_items_truncate_apply_without_plan_in_is_refused_before_http(self, mock_client: unittest.mock.MagicMock) -> None:
        args = SimpleNamespace(
            data_collection_id="posts",
        )
        ctx = self._ctx(apply=True, yes=True, enforce_reviewed_plan=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_items.cmd_data_items_truncate(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertEqual(payload["method"], "data-items.truncate")
        self.assertEqual(mock_client.return_value.request.call_count, 0)

    @patch("wix_safe_agent_cli.commands.data_items.HttpClient")
    def test_data_items_bulk_remove_apply_without_plan_in_is_refused_before_http(self, mock_client: unittest.mock.MagicMock) -> None:
        args = SimpleNamespace(
            data_collection_id="posts",
            data_item_ids_json='["i1","i2"]',
            condition_json=None,
            app_options_json=None,
            include_draft_items=False,
        )
        ctx = self._ctx(apply=True, yes=True, ack_irreversible=True, enforce_reviewed_plan=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_items.cmd_data_items_bulk_remove(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertEqual(payload["method"], "data-items.bulk-remove")
        self.assertEqual(mock_client.return_value.request.call_count, 0)

    @patch("wix_safe_agent_cli.commands.data_items.HttpClient")
    def test_data_items_bulk_save_apply_without_plan_in_is_refused_before_http(self, mock_client: unittest.mock.MagicMock) -> None:
        args = SimpleNamespace(
            data_collection_id="posts",
            data_items_json='[{"id":"i1","name":"Alice"},{"id":"i2","name":"Bob"}]',
            app_options_json=None,
            include_draft_items=False,
            return_entity=False,
        )
        ctx = self._ctx(apply=True, yes=True, enforce_reviewed_plan=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_items.cmd_data_items_bulk_save(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertEqual(payload["method"], "data-items.bulk-save")
        self.assertEqual(mock_client.return_value.request.call_count, 0)

    @patch("wix_safe_agent_cli.commands.data_items.HttpClient")
    def test_data_items_bulk_update_apply_without_plan_in_is_refused_before_http(self, mock_client: unittest.mock.MagicMock) -> None:
        args = SimpleNamespace(
            data_collection_id="posts",
            data_items_json='[{"id":"i1","name":"Alice"},{"id":"i2","name":"Bob"}]',
            condition_json=None,
            app_options_json=None,
            include_draft_items=False,
            return_entity=False,
        )
        ctx = self._ctx(apply=True, yes=True, enforce_reviewed_plan=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_items.cmd_data_items_bulk_update(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertEqual(payload["method"], "data-items.bulk-update")
        self.assertEqual(mock_client.return_value.request.call_count, 0)

    @patch("wix_safe_agent_cli.commands.data_items.HttpClient")
    def test_data_items_bulk_insert_references_apply_without_plan_in_is_refused_before_http(self, mock_client: unittest.mock.MagicMock) -> None:
        args = SimpleNamespace(
            data_collection_id="posts",
            data_item_references_json=(
                '[{"referringItemFieldName":"authors","referringItemId":"p1","referencedItemId":"a1"}]'
            ),
            return_entity=False,
        )
        ctx = self._ctx(apply=True, yes=True, enforce_reviewed_plan=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_items.cmd_data_items_bulk_insert_references(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertEqual(payload["method"], "data-items.bulk-insert-references")
        self.assertEqual(mock_client.return_value.request.call_count, 0)

    @patch("wix_safe_agent_cli.commands.data_items.HttpClient")
    def test_data_items_bulk_remove_references_apply_without_plan_in_is_refused_before_http(self, mock_client: unittest.mock.MagicMock) -> None:
        args = SimpleNamespace(
            data_collection_id="posts",
            data_item_references_json=(
                '[{"referringItemFieldName":"authors","referringItemId":"p1","referencedItemId":"a1"}]'
            ),
        )
        ctx = self._ctx(apply=True, yes=True, enforce_reviewed_plan=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_items.cmd_data_items_bulk_remove_references(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertEqual(payload["method"], "data-items.bulk-remove-references")
        self.assertEqual(mock_client.return_value.request.call_count, 0)

    @patch("wix_safe_agent_cli.commands.data_items.HttpClient")
    def test_data_items_bulk_insert_dry_run_rejects_too_many_items(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"results": []})
        too_many_items = [
            {"id": f"item-{i}", "value": i}
            for i in range(1001)
        ]
        args = SimpleNamespace(
            data_collection_id="posts",
            data_items_json=json.dumps(too_many_items),
            app_options_json=None,
            return_entity=False,
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_items.cmd_data_items_bulk_insert(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")

    @patch("wix_safe_agent_cli.commands.data_items.HttpClient")
    def test_data_items_bulk_insert_dry_run_rejects_duplicate_explicit_item_ids(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"results": []})
        args = SimpleNamespace(
            data_collection_id="posts",
            data_items_json='[{"id":"dup"},{"id":"dup"}]',
            app_options_json=None,
            return_entity=False,
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_items.cmd_data_items_bulk_insert(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")

    @patch("wix_safe_agent_cli.commands.data_items.HttpClient")
    def test_data_items_bulk_insert_apply_refuses_missing_ids_without_return_entity(self, mock_client: unittest.mock.MagicMock) -> None:
        args = SimpleNamespace(
            data_collection_id="posts",
            data_items_json='[{"name":"NoID"},{"id":"i2"}]',
            app_options_json=None,
            return_entity=False,
        )
        ctx = self._ctx(apply=True, yes=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_items.cmd_data_items_bulk_insert(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertEqual(payload["method"], "data-items.bulk-insert")
        self.assertIn("return-entity", payload["reasons"][0])
        self.assertEqual(mock_client.return_value.request.call_count, 0)

    @patch("wix_safe_agent_cli.commands.data_items.HttpClient")
    def test_data_items_bulk_insert_apply_reads_back_when_ids_known(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.side_effect = [
            RuntimeError("HTTP 404 for https://www.wixapis.com/wix-data/v2/items/i1"),
            RuntimeError("HTTP 404 for https://www.wixapis.com/wix-data/v2/items/i2"),
            _DummyResponse({"results": [{"id": "i1"}, {"id": "i2"}], "bulkActionMetadata": {"successCount": 2, "failureCount": 0}}),
            _DummyResponse({"dataItem": {"id": "i1"}}),
            _DummyResponse({"dataItem": {"id": "i2"}}),
        ]
        args = SimpleNamespace(
            data_collection_id="posts",
            data_items_json='[{"id":"i1"},{"id":"i2"}]',
            app_options_json=None,
            return_entity=False,
        )
        ctx = self._ctx(apply=True, yes=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_items.cmd_data_items_bulk_insert(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertFalse(payload["receipt"]["verification"]["read_back"]["checks"][0]["response"] is None)
        self.assertEqual(len(mock_client.return_value.request.call_args_list), 5)

        calls = mock_client.return_value.request.call_args_list
        self.assertEqual(calls[0].kwargs["method"], "GET")
        self.assertEqual(calls[1].kwargs["method"], "GET")
        self.assertEqual(calls[2].kwargs["method"], "POST")
        self.assertEqual(calls[3].kwargs["method"], "GET")
        self.assertEqual(calls[4].kwargs["method"], "GET")

    @patch("wix_safe_agent_cli.commands.data_items.HttpClient")
    def test_data_items_bulk_insert_apply_refuses_when_explicit_id_already_exists(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"dataItem": {"id": "i1"}}),
        ]
        args = SimpleNamespace(
            data_collection_id="posts",
            data_items_json='[{"id":"i1"}]',
            app_options_json=None,
            return_entity=True,
        )
        ctx = self._ctx(apply=True, yes=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_items.cmd_data_items_bulk_insert(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("already exist", payload["reasons"][0])

    @patch("wix_safe_agent_cli.commands.data_items.HttpClient")
    def test_data_items_bulk_insert_apply_fails_when_total_failures_reported(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.side_effect = [
            RuntimeError("HTTP 404 for https://www.wixapis.com/wix-data/v2/items/i1"),
            _DummyResponse(
                {
                    "results": [{"itemMetadata": {"error": {"code": "WDE0000"}}}],
                    "bulkActionMetadata": {"totalSuccesses": 0, "totalFailures": 1},
                }
            ),
        ]
        args = SimpleNamespace(
            data_collection_id="posts",
            data_items_json='[{"id":"i1"}]',
            app_options_json=None,
            return_entity=True,
        )
        ctx = self._ctx(apply=True, yes=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_items.cmd_data_items_bulk_insert(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["method"], "data-items.bulk-insert")
        self.assertEqual(payload["receipt"]["verification"]["bulkActionMetadata"]["totalFailures"], 1)
        self.assertEqual(len(mock_client.return_value.request.call_args_list), 2)

    @patch("wix_safe_agent_cli.commands.data_items.HttpClient")
    def test_data_items_bulk_patch_dry_run_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"dataItem": {"id": "i1", "count": 1}}),
            _DummyResponse({"dataItem": {"id": "i2", "count": 2}}),
        ]
        args = SimpleNamespace(
            data_collection_id="posts",
            patches_json='[{"dataItemId":"i1","fieldModifications":[{"op":"set","field":"count","value":10}]},{"dataItemId":"i2","fieldModifications":[{"op":"set","field":"count","value":20}]}]',
            condition_json=None,
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_items.cmd_data_items_bulk_patch(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["method"], "data-items.bulk-patch")
        self.assertTrue(payload["dry_run"])
        request = payload["plan"]["request"]
        self.assertEqual(request["method"], "POST")
        self.assertEqual(request["path"], "/wix-data/v2/bulk/items/patch")
        self.assertEqual(request["body"]["dataCollectionId"], "posts")
        self.assertEqual(len(request["body"]["patches"]), 2)
        self.assertEqual(request["body"]["patches"][0]["dataItemId"], "i1")

    @patch("wix_safe_agent_cli.commands.data_items.HttpClient")
    def test_data_items_bulk_patch_dry_run_rejects_too_many_patches(self, mock_client: unittest.mock.MagicMock) -> None:
        too_many_patches = [
            {"dataItemId": f"item-{i}", "fieldModifications": [{"op": "set", "field": "count", "value": i}]}
            for i in range(101)
        ]
        args = SimpleNamespace(
            data_collection_id="posts",
            patches_json=json.dumps(too_many_patches),
            condition_json=None,
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_items.cmd_data_items_bulk_patch(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertEqual(mock_client.return_value.request.call_count, 0)

    @patch("wix_safe_agent_cli.commands.data_items.HttpClient")
    def test_data_items_bulk_patch_dry_run_rejects_duplicate_data_item_ids(self, mock_client: unittest.mock.MagicMock) -> None:
        args = SimpleNamespace(
            data_collection_id="posts",
            patches_json='[{"dataItemId":"dup","fieldModifications":[{"op":"set","field":"count","value":1}]},{"dataItemId":"dup","fieldModifications":[{"op":"set","field":"count","value":2}]}]',
            condition_json=None,
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_items.cmd_data_items_bulk_patch(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertEqual(mock_client.return_value.request.call_count, 0)

    @patch("wix_safe_agent_cli.commands.data_items.HttpClient")
    def test_data_items_bulk_patch_apply_reads_back_verification(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"dataItem": {"id": "i1", "count": 1}}),
            _DummyResponse({"dataItem": {"id": "i2", "count": 2}}),
            _DummyResponse({"dataItem": {"id": "i1", "count": 1}}),
            _DummyResponse({"dataItem": {"id": "i2", "count": 2}}),
            _DummyResponse(
                {
                    "results": [
                        {"dataItemId": "i1"},
                        {"dataItemId": "i2"},
                    ],
                    "bulkActionMetadata": {"totalSuccesses": 2, "totalFailures": 0},
                }
            ),
            _DummyResponse({"dataItem": {"id": "i1", "count": 10}}),
            _DummyResponse({"dataItem": {"id": "i2", "count": 20}}),
        ]
        args = SimpleNamespace(
            data_collection_id="posts",
            patches_json='[{"dataItemId":"i1","fieldModifications":[{"op":"set","field":"count","value":10}]},{"dataItemId":"i2","fieldModifications":[{"op":"set","field":"count","value":20}]}]',
            condition_json=None,
        )
        ctx = self._ctx(apply=True, yes=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_items.cmd_data_items_bulk_patch(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertFalse(payload["dry_run"])
        self.assertEqual(payload["method"], "data-items.bulk-patch")
        self.assertTrue(payload["receipt"]["verification"]["ok"])
        self.assertEqual(len(payload["receipt"]["verification"]["read_back"]["checks"]), 2)
        self.assertEqual(len(mock_client.return_value.request.call_args_list), 7)

    @patch("wix_safe_agent_cli.commands.data_items.HttpClient")
    def test_data_items_bulk_patch_apply_fails_when_total_failures_reported(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"dataItem": {"id": "i1", "count": 1}}),
            _DummyResponse({"dataItem": {"id": "i1", "count": 1}}),
            _DummyResponse(
                {
                    "results": [{"itemMetadata": {"error": {"code": "WDE0000"}}}],
                    "bulkActionMetadata": {"totalSuccesses": 0, "totalFailures": 1},
                }
            ),
            _DummyResponse({"dataItem": {"id": "i1", "count": 1}}),
        ]
        args = SimpleNamespace(
            data_collection_id="posts",
            patches_json='[{"dataItemId":"i1","fieldModifications":[{"op":"set","field":"count","value":10}]}]',
            condition_json=None,
        )
        ctx = self._ctx(apply=True, yes=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_items.cmd_data_items_bulk_patch(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["method"], "data-items.bulk-patch")
        self.assertEqual(payload["receipt"]["verification"]["bulkActionMetadata"]["totalFailures"], 1)

    @patch("wix_safe_agent_cli.commands.data_items.HttpClient")
    def test_data_items_bulk_patch_apply_refuses_when_item_changed_since_plan(self, mock_client: unittest.mock.MagicMock) -> None:
        before = {"dataItem": {"id": "i1", "count": 1}}
        changed = {"dataItem": {"id": "i1", "count": 2}}

        mock_client.return_value.request.return_value = _DummyResponse(before)
        args = SimpleNamespace(
            data_collection_id="posts",
            patches_json='[{"dataItemId":"i1","fieldModifications":[{"op":"set","field":"count","value":10}]}]',
            condition_json=None,
        )
        dry_buf = io.StringIO()
        with redirect_stdout(dry_buf):
            dry_rc = data_items.cmd_data_items_bulk_patch(args, self._ctx())
        self.assertEqual(dry_rc, 0)
        dry_payload = json.loads(dry_buf.getvalue())

        with tempfile.TemporaryDirectory() as d:
            plan_path = Path(d) / "plan.json"
            plan_path.write_text(json.dumps(dry_payload["plan"]), encoding="utf-8")

            mock_client.return_value.request.return_value = _DummyResponse(changed)
            apply_ctx = self._ctx(apply=True, yes=True)
            apply_ctx["plan_in"] = str(plan_path)
            apply_buf = io.StringIO()
            with redirect_stdout(apply_buf):
                apply_rc = data_items.cmd_data_items_bulk_patch(args, apply_ctx)

        apply_payload = json.loads(apply_buf.getvalue())
        self.assertEqual(apply_rc, 0)
        self.assertTrue(apply_payload["refused"])
        self.assertIn("changed since plan", apply_payload["reasons"][0])

    @patch("wix_safe_agent_cli.commands.data_items.HttpClient")
    def test_data_items_insert_reference_dry_run_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"dataItem": {"id": "post-1"}})
        args = SimpleNamespace(
            data_collection_id="posts",
            referring_item_field_name="author",
            referring_item_id="post-1",
            referenced_item_id="author-1",
            consistent_read=True,
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_items.cmd_data_items_insert_reference(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["method"], "data-items.insert-reference")
        self.assertTrue(payload["dry_run"])
        self.assertIn("plan", payload)
        self.assertEqual(payload["plan"]["request"]["method"], "POST")
        self.assertEqual(payload["plan"]["request"]["path"], "/wix-data/v2/items/insert-reference")
        body = payload["plan"]["request"]["body"]
        self.assertEqual(body["dataCollectionId"], "posts")
        self.assertEqual(body["dataItemReference"]["referringItemFieldName"], "author")
        self.assertEqual(body["dataItemReference"]["referringItemId"], "post-1")
        self.assertEqual(body["dataItemReference"]["referencedItemId"], "author-1")

    @patch("wix_safe_agent_cli.commands.data_items.HttpClient")
    def test_data_items_remove_reference_dry_run_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"dataItem": {"id": "post-1"}})
        args = SimpleNamespace(
            data_collection_id="posts",
            referring_item_field_name="author",
            referring_item_id="post-1",
            referenced_item_id="author-2",
            consistent_read=False,
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_items.cmd_data_items_remove_reference(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["method"], "data-items.remove-reference")
        self.assertTrue(payload["dry_run"])
        self.assertIn("plan", payload)
        self.assertEqual(payload["plan"]["request"]["method"], "POST")
        self.assertEqual(payload["plan"]["request"]["path"], "/wix-data/v2/items/remove-reference")
        body = payload["plan"]["request"]["body"]
        self.assertEqual(body["dataCollectionId"], "posts")
        self.assertEqual(body["dataItemReference"]["referencedItemId"], "author-2")

    @patch("wix_safe_agent_cli.commands.data_items.HttpClient")
    def test_data_items_remove_reference_apply_does_not_require_irreversible_ack(
        self,
        mock_client: unittest.mock.MagicMock,
    ) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"dataItem": {"id": "post-1"}}),
            _DummyResponse({"dataItem": {"id": "post-1"}}),
            _DummyResponse({"isReferenced": True}),
            _DummyResponse({"dataItemReference": {"referringItemId": "post-1"}}),
            _DummyResponse({"isReferenced": False}),
        ]
        args = SimpleNamespace(
            data_collection_id="posts",
            referring_item_field_name="author",
            referring_item_id="post-1",
            referenced_item_id="author-2",
            consistent_read=False,
        )
        ctx = self._ctx(apply=True, yes=True, ack_irreversible=False)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_items.cmd_data_items_remove_reference(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertFalse(payload["dry_run"])
        self.assertTrue(payload["receipt"]["verification"]["ok"])

    @patch("wix_safe_agent_cli.commands.data_items.HttpClient")
    def test_data_items_replace_references_dry_run_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"dataItem": {"id": "post-1"}})
        args = SimpleNamespace(
            data_collection_id="posts",
            referring_item_field_name="authors",
            referring_item_id="post-1",
            new_referenced_item_ids_json='["a1","a2"]',
            consistent_read=True,
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_items.cmd_data_items_replace_references(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["method"], "data-items.replace-references")
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["request"]["method"], "POST")
        self.assertEqual(payload["plan"]["request"]["path"], "/wix-data/v2/items/replace-references")
        body = payload["plan"]["request"]["body"]
        self.assertEqual(body["dataCollectionId"], "posts")
        self.assertEqual(body["referringItemFieldName"], "authors")
        self.assertEqual(body["referringItemId"], "post-1")
        self.assertEqual(body["newReferencedItemIds"], ["a1", "a2"])

    @patch("wix_safe_agent_cli.commands.data_items.HttpClient")
    def test_data_items_replace_references_apply_refuses_drift(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"dataItem": {"id": "post-1"}})
        args = SimpleNamespace(
            data_collection_id="posts",
            referring_item_field_name="authors",
            referring_item_id="post-1",
            new_referenced_item_ids_json='["a1","a2"]',
            consistent_read=False,
        )
        dry_buf = io.StringIO()
        with redirect_stdout(dry_buf):
            rc = data_items.cmd_data_items_replace_references(args, self._ctx())
        self.assertEqual(rc, 0)
        dry_payload = json.loads(dry_buf.getvalue())

        with tempfile.TemporaryDirectory() as d:
            plan_path = Path(d) / "plan.json"
            plan_path.write_text(json.dumps(dry_payload["plan"]), encoding="utf-8")

            mock_client.return_value.request.return_value = _DummyResponse({"dataItem": {"id": "post-1", "note": "changed"}})
            apply_ctx = self._ctx(apply=True, yes=True)
            apply_ctx["plan_in"] = str(plan_path)
            apply_buf = io.StringIO()
            with redirect_stdout(apply_buf):
                apply_rc = data_items.cmd_data_items_replace_references(args, apply_ctx)

        apply_payload = json.loads(apply_buf.getvalue())
        self.assertEqual(apply_rc, 0)
        self.assertTrue(apply_payload["refused"])
        self.assertIn("changed since plan", apply_payload["reasons"][0])

    @patch("wix_safe_agent_cli.commands.data_items.HttpClient")
    def test_data_items_save_apply_without_plan_in_refuses_before_write_request(self, mock_client: unittest.mock.MagicMock) -> None:
        args = SimpleNamespace(
            data_collection_id="posts",
            data_item_json='{"id":"i10","data":{"title":"Hello"}}',
            app_options_json=None,
            include_draft_items=False,
        )
        mock_client.return_value.request.side_effect = [
            RuntimeError("HTTP 404 for https://www.wixapis.com/wix-data/v2/items/i10"),
        ]

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_items.cmd_data_items_save(args, self._ctx(apply=True, yes=True, enforce_reviewed_plan=True))
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("reviewed saved plan", payload["reasons"][0])
        self.assertEqual(mock_client.return_value.request.call_count, 0)

    @patch("wix_safe_agent_cli.commands.data_items.HttpClient")
    def test_data_items_truncate_apply_without_plan_in_refuses_before_write_request(self, mock_client: unittest.mock.MagicMock) -> None:
        args = SimpleNamespace(data_collection_id="posts")
        mock_client.return_value.request.return_value = _DummyResponse({"totalCount": 3})

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_items.cmd_data_items_truncate(
                args,
                self._ctx(apply=True, yes=True, ack_irreversible=True, enforce_reviewed_plan=True),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("reviewed saved plan", payload["reasons"][0])
        self.assertEqual(mock_client.return_value.request.call_count, 0)

    @patch("wix_safe_agent_cli.commands.data_items.HttpClient")
    def test_data_items_bulk_remove_apply_without_plan_in_refuses_before_write_request(
        self,
        mock_client: unittest.mock.MagicMock,
    ) -> None:
        args = SimpleNamespace(
            data_collection_id="posts",
            data_item_ids_json='["i1","i2"]',
            condition_json=None,
            app_options_json=None,
            include_draft_items=False,
        )
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"dataItem": {"id": "i1"}}),
            _DummyResponse({"dataItem": {"id": "i2"}}),
        ]

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_items.cmd_data_items_bulk_remove(
                args,
                self._ctx(apply=True, yes=True, ack_irreversible=True, enforce_reviewed_plan=True),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("reviewed saved plan", payload["reasons"][0])
        self.assertEqual(mock_client.return_value.request.call_count, 0)

    @patch("wix_safe_agent_cli.commands.data_items.HttpClient")
    def test_data_items_update_dry_run_includes_before_snapshot_and_update_apply_refuses_drift(
        self,
        mock_client: unittest.mock.MagicMock,
    ) -> None:
        before = {"dataItem": {"id": "i7", "value": 1}}
        changed = {"dataItem": {"id": "i7", "value": 2}}

        mock_client.return_value.request.return_value = _DummyResponse(before)
        args = SimpleNamespace(
            data_collection_id="posts",
            data_item_id="i7",
            data_item_json='{"id":"i7","value":1}',
            condition_json=None,
            language=None,
        )

        buf = io.StringIO()
        with redirect_stdout(buf):
            dry_run_rc = data_items.cmd_data_items_update(args, self._ctx())
        self.assertEqual(dry_run_rc, 0)
        dry_run_payload = json.loads(buf.getvalue())
        self.assertTrue(dry_run_payload["dry_run"])
        self.assertEqual(dry_run_payload["plan"]["baseline"]["before_state"], before)

        with tempfile.TemporaryDirectory() as d:
            plan_path = Path(d) / "plan.json"
            plan_path.write_text(json.dumps(dry_run_payload["plan"]), encoding="utf-8")

            mock_client.return_value.request.side_effect = [_DummyResponse(changed)]
            apply_ctx = self._ctx(apply=True, yes=True)
            apply_ctx["plan_in"] = str(plan_path)
            apply_buf = io.StringIO()
            with redirect_stdout(apply_buf):
                apply_rc = data_items.cmd_data_items_update(args, apply_ctx)

            apply_payload = json.loads(apply_buf.getvalue())
            self.assertEqual(apply_rc, 0)
            self.assertTrue(apply_payload["refused"])
            self.assertIn("changed since plan", apply_payload["reasons"][0])

    @patch("wix_safe_agent_cli.commands.data_items.HttpClient")
    def test_data_items_patch_apply_reads_back_verification(self, mock_client: unittest.mock.MagicMock) -> None:
        before = {"dataItem": {"id": "i8", "count": 1}}
        patched = {"dataItem": {"id": "i8", "count": 2}}
        mock_client.return_value.request.side_effect = [
            _DummyResponse(before),
            _DummyResponse(before),
            _DummyResponse(patched),
            _DummyResponse(patched),
        ]

        args = SimpleNamespace(
            data_collection_id="posts",
            data_item_id="i8",
            patch_json='{"count":2}',
            condition_json=None,
            language=None,
        )
        apply_ctx = self._ctx(apply=True, yes=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_items.cmd_data_items_patch(args, apply_ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertFalse(payload["dry_run"])
        self.assertEqual(payload["method"], "data-items.patch")
        self.assertTrue(payload["receipt"]["verification"]["ok"])
        calls = mock_client.return_value.request.call_args_list
        self.assertEqual(len(calls), 4)
        self.assertEqual(calls[2].kwargs["json_body"]["patch"]["dataItemId"], "i8")
        self.assertEqual(calls[3].kwargs["method"], "GET")

    @patch("wix_safe_agent_cli.commands.data_items.HttpClient")
    def test_data_items_remove_apply_requires_ack_and_reports_404_verified_removed(self, mock_client: unittest.mock.MagicMock) -> None:
        args = SimpleNamespace(
            data_collection_id="posts",
            data_item_id="i9",
            condition_json=None,
            language=None,
        )

        mock_client.return_value.request.return_value = _DummyResponse({"dataItem": {"id": "i9"}})
        ack_ctx = self._ctx(apply=True, yes=True, ack_irreversible=False)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc_ack = data_items.cmd_data_items_remove(args, ack_ctx)
        payload_ack = json.loads(buf.getvalue())

        self.assertEqual(rc_ack, 0)
        self.assertTrue(payload_ack["dry_run"])

        mock_client.reset_mock()
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"dataItem": {"id": "i9"}}),
            _DummyResponse({"dataItem": {"id": "i9"}}),
            _DummyResponse({}),
            RuntimeError("HTTP 404 for https://www.wixapis.com/wix-data/v2/items/i9"),
        ]
        remove_ctx = self._ctx(apply=True, yes=True, ack_irreversible=True)
        remove_buf = io.StringIO()
        with redirect_stdout(remove_buf):
            rc_remove = data_items.cmd_data_items_remove(args, remove_ctx)
        payload_remove = json.loads(remove_buf.getvalue())

        self.assertEqual(rc_remove, 0)
        self.assertFalse(payload_remove["dry_run"])
        self.assertTrue(payload_remove["ok"])
        self.assertTrue(payload_remove["receipt"]["verification"]["removed"])
        self.assertTrue(payload_remove["receipt"]["verification"]["ok"])
        remove_call = mock_client.return_value.request.call_args_list[2]
        self.assertEqual(remove_call.kwargs["params"], {"dataCollectionId": "posts"})
        self.assertEqual(remove_call.kwargs["json_body"], None)

    @patch("wix_safe_agent_cli.commands.data_items.HttpClient")
    def test_data_items_update_apply_injects_matching_body_id(self, mock_client: unittest.mock.MagicMock) -> None:
        before = {"dataItem": {"id": "i4", "value": 1}}
        after = {"dataItem": {"id": "i4", "value": 3}}
        mock_client.return_value.request.side_effect = [
            _DummyResponse(before),
            _DummyResponse(before),
            _DummyResponse(after),
            _DummyResponse(after),
        ]

        args = SimpleNamespace(
            data_collection_id="posts",
            data_item_id="i4",
            data_item_json='{"value":3}',
            condition_json=None,
            language=None,
        )
        ctx = self._ctx(apply=True, yes=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_items.cmd_data_items_update(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        update_call = mock_client.return_value.request.call_args_list[2]
        self.assertEqual(update_call.kwargs["json_body"]["dataItem"]["id"], "i4")

    def test_cli_parser_recognizes_data_items_write_subcommands(self) -> None:
        parser = build_parser()

        insert = parser.parse_args(["data-items", "insert", "--data-collection-id", "posts", "--data-item-json", '{"id":"x1"}'])
        self.assertEqual(insert.data_items_cmd, "insert")
        self.assertTrue(insert.write_capable)

        save = parser.parse_args(["data-items", "save", "--data-collection-id", "posts", "--data-item-json", '{"id":"x1"}'])
        self.assertEqual(save.data_items_cmd, "save")
        self.assertTrue(save.write_capable)

        truncate = parser.parse_args(["data-items", "truncate", "--data-collection-id", "posts"])
        self.assertEqual(truncate.data_items_cmd, "truncate")
        self.assertTrue(truncate.write_capable)

        update = parser.parse_args(
            [
                "data-items",
                "update",
                "--data-collection-id",
                "posts",
                "--data-item-id",
                "x1",
                "--data-item-json",
                '{"id":"x1"}',
            ]
        )
        self.assertEqual(update.data_items_cmd, "update")
        self.assertTrue(update.write_capable)

        patch = parser.parse_args(
            [
                "data-items",
                "patch",
                "--data-collection-id",
                "posts",
                "--data-item-id",
                "x1",
                "--patch-json",
                '{"field":"value"}',
            ]
        )
        self.assertEqual(patch.data_items_cmd, "patch")
        self.assertTrue(patch.write_capable)

        remove = parser.parse_args(["data-items", "remove", "--data-collection-id", "posts", "--data-item-id", "x1"])
        self.assertEqual(remove.data_items_cmd, "remove")
        self.assertTrue(remove.write_capable)

        insert_reference = parser.parse_args(
            [
                "data-items",
                "insert-reference",
                "--data-collection-id",
                "posts",
                "--referring-item-field-name",
                "author",
                "--referring-item-id",
                "post-1",
                "--referenced-item-id",
                "author-1",
            ]
        )
        self.assertEqual(insert_reference.data_items_cmd, "insert-reference")
        self.assertTrue(insert_reference.write_capable)

        remove_reference = parser.parse_args(
            [
                "data-items",
                "remove-reference",
                "--data-collection-id",
                "posts",
                "--referring-item-field-name",
                "author",
                "--referring-item-id",
                "post-1",
                "--referenced-item-id",
                "author-1",
            ]
        )
        self.assertEqual(remove_reference.data_items_cmd, "remove-reference")
        self.assertTrue(remove_reference.write_capable)

        replace_references = parser.parse_args(
            [
                "data-items",
                "replace-references",
                "--data-collection-id",
                "posts",
                "--referring-item-field-name",
                "authors",
                "--referring-item-id",
                "post-1",
                "--new-referenced-item-ids-json",
                '["a1","a2"]',
            ]
        )
        self.assertEqual(replace_references.data_items_cmd, "replace-references")
        self.assertTrue(replace_references.write_capable)

        bulk_insert = parser.parse_args(
            [
                "data-items",
                "bulk-insert",
                "--data-collection-id",
                "posts",
                "--data-items-json",
                '[{"id":"i1"}]',
            ]
        )
        self.assertEqual(bulk_insert.data_items_cmd, "bulk-insert")
        self.assertTrue(bulk_insert.write_capable)

        bulk_save = parser.parse_args(
            [
                "data-items",
                "bulk-save",
                "--data-collection-id",
                "posts",
                "--data-items-json",
                '[{"id":"i1"}]',
            ]
        )
        self.assertEqual(bulk_save.data_items_cmd, "bulk-save")
        self.assertTrue(bulk_save.write_capable)

        bulk_update = parser.parse_args(
            [
                "data-items",
                "bulk-update",
                "--data-collection-id",
                "posts",
                "--data-items-json",
                '[{"id":"i1"}]',
            ]
        )
        self.assertEqual(bulk_update.data_items_cmd, "bulk-update")
        self.assertTrue(bulk_update.write_capable)

        bulk_remove = parser.parse_args(
            [
                "data-items",
                "bulk-remove",
                "--data-collection-id",
                "posts",
                "--data-item-ids-json",
                '["x1"]',
            ]
        )
        self.assertEqual(bulk_remove.data_items_cmd, "bulk-remove")
        self.assertTrue(bulk_remove.write_capable)

        bulk_insert_references = parser.parse_args(
            [
                "data-items",
                "bulk-insert-references",
                "--data-collection-id",
                "posts",
                "--data-item-references-json",
                '[{"referringItemFieldName":"author","referringItemId":"post-1","referencedItemId":"author-1"}]',
            ]
        )
        self.assertEqual(bulk_insert_references.data_items_cmd, "bulk-insert-references")
        self.assertTrue(bulk_insert_references.write_capable)

        bulk_remove_references = parser.parse_args(
            [
                "data-items",
                "bulk-remove-references",
                "--data-collection-id",
                "posts",
                "--data-item-references-json",
                '[{"referringItemFieldName":"author","referringItemId":"post-1","referencedItemId":"author-1"}]',
            ]
        )
        self.assertEqual(bulk_remove_references.data_items_cmd, "bulk-remove-references")
        self.assertTrue(bulk_remove_references.write_capable)

        bulk_patch = parser.parse_args(
            [
                "data-items",
                "bulk-patch",
                "--data-collection-id",
                "posts",
                "--patches-json",
                '[{"dataItemId":"x1","fieldModifications":[{"op":"set","field":"count","value":1}]}]',
            ]
        )
        self.assertEqual(bulk_patch.data_items_cmd, "bulk-patch")
        self.assertTrue(bulk_patch.write_capable)

    def test_cli_parser_recognizes_data_items_read_subcommands(self) -> None:
        parser = build_parser()

        aggregate = parser.parse_args(
            [
                "data-items",
                "aggregate",
                "--data-collection-id",
                "cities",
                "--aggregation-json",
                '{"operations":[{"sum":"population"}]}',
            ]
        )
        self.assertEqual(aggregate.data_items_cmd, "aggregate")
        self.assertFalse(aggregate.write_capable)

        aggregate_pipeline = parser.parse_args(
            [
                "data-items",
                "aggregate-pipeline",
                "--data-collection-id",
                "cities",
                "--pipeline-json",
                '{"stages":[{"match":{"state":"CA"}}]}',
            ]
        )
        self.assertEqual(aggregate_pipeline.data_items_cmd, "aggregate-pipeline")
        self.assertFalse(aggregate_pipeline.write_capable)

        distinct = parser.parse_args(
            [
                "data-items",
                "distinct",
                "--data-collection-id",
                "cities",
                "--field-name",
                "state",
            ]
        )
        self.assertEqual(distinct.data_items_cmd, "distinct")
        self.assertFalse(distinct.write_capable)

        search = parser.parse_args(
            [
                "data-items",
                "search",
                "--data-collection-id",
                "cities",
                "--search-json",
                '{"search":{"expression":"foo","mode":"AND"}}',
            ]
        )
        self.assertEqual(search.data_items_cmd, "search")
        self.assertFalse(search.write_capable)

        query_referenced = parser.parse_args(
            [
                "data-items",
                "query-referenced",
                "--data-collection-id",
                "posts",
                "--referring-item-field-name",
                "author",
                "--referring-item-id",
                "post-1",
            ]
        )
        self.assertEqual(query_referenced.data_items_cmd, "query-referenced")
        self.assertFalse(query_referenced.write_capable)

        is_referenced = parser.parse_args(
            [
                "data-items",
                "is-referenced",
                "--data-collection-id",
                "posts",
                "--referring-item-field-name",
                "author",
                "--referring-item-id",
                "post-1",
                "--referenced-item-id",
                "author-1",
            ]
        )
        self.assertEqual(is_referenced.data_items_cmd, "is-referenced")
        self.assertFalse(is_referenced.write_capable)
