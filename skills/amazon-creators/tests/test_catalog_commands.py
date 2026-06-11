from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from amazon_creators_api_tool.cli import main


class CatalogCommandTests(unittest.TestCase):
    def _write_env(self, base: str) -> str:
        env_path = os.path.join(base, ".env")
        with open(env_path, "w", encoding="utf-8") as f:
            f.write("AMAZON_CREATORS_API_BASE_URL=https://creatorsapi.amazon/catalog/v1\n")
            f.write("AMAZON_CREATORS_CREDENTIAL_ID=cred-id\n")
            f.write("AMAZON_CREATORS_CREDENTIAL_SECRET=secret\n")
            f.write("AMAZON_CREATORS_CREDENTIAL_VERSION=2\n")
            f.write("AMAZON_CREATORS_LOCALE=en_US\n")
            f.write("AMAZON_CREATORS_TIMEOUT_S=30\n")
            f.write("AMAZON_CREATORS_PARTNER_TAG=partner-tag\n")
        return env_path

    def _run_cmd(self, env_path: str, args: list[str]) -> dict[str, object]:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["--output", "json", "--env-file", env_path] + args)
        self.assertEqual(rc, 0)
        return json.loads(buf.getvalue())

    def test_browse_nodes_request(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)

            captured: dict[str, object] = {}
            node_payload = {
                "id": "100",
                "displayName": "Books",
                "parentNode": "0",
                "ancestors": ["0", "1"],
                "browseNodePath": "/Books",
            }

            def fake_call(cfg, ctx, operation, body, locale):
                captured["operation"] = operation
                captured["body"] = body
                return {"browseNodesResult": {"browseNodes": [node_payload]}}

            with patch("amazon_creators_api_tool.commands.catalog._call_operation", side_effect=fake_call):
                resp = self._run_cmd(
                    env_path,
                    ["--apply", "browse-nodes", "describe", "--browse-node-id", "100"],
                )

            self.assertEqual(captured["operation"], "GetBrowseNodes")
            self.assertEqual(captured["body"]["browseNodeIds"], ["100"])
            self.assertEqual(resp["operation"], "GetBrowseNodes")
            self.assertEqual(captured["body"]["marketplace"], "www.amazon.com")
            self.assertEqual(captured["body"]["partnerTag"], "partner-tag")
            self.assertEqual(
                captured["body"]["resources"],
                ["browseNodes.ancestor", "browseNodes.children"],
            )
            self.assertEqual(resp["resources"], ["browseNodes.ancestor", "browseNodes.children"])
            self.assertIn("browse_nodes", resp)
            self.assertEqual(resp["browse_nodes"][0]["node_id"], "100")
            self.assertEqual(resp["browse_nodes"][0]["name"], "Books")
            self.assertFalse(resp["dry_run"])
            self.assertEqual(resp["receipt"]["operation"], "GetBrowseNodes")
            self.assertEqual(resp["receipt"]["selector"]["operation"], "GetBrowseNodes")
            self.assertTrue(resp["receipt_out"])
            self.assertTrue(resp["receipt_out"].endswith("receipt.json"))

    def test_items_request(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)

            captured: dict[str, object] = {}

            def fake_call(cfg, ctx, operation, body, locale):
                captured["operation"] = operation
                captured["body"] = body
                return {"itemsResult": {"items": [{"asin": "B0ITEM"}]}}

            with patch("amazon_creators_api_tool.commands.catalog._call_operation", side_effect=fake_call):
                resp = self._run_cmd(
                    env_path,
                    ["--apply", "items", "get", "--item-id", "B0ITEM", "--resource", "ItemInfo"],
                )

            self.assertEqual(captured["operation"], "GetItems")
            self.assertEqual(captured["body"]["itemIds"], ["B0ITEM"])
            self.assertEqual(resp["operation"], "GetItems")
            self.assertEqual(resp["items"][0]["asin"], "B0ITEM")
            self.assertEqual(captured["body"]["marketplace"], "www.amazon.com")
            self.assertEqual(captured["body"]["partnerTag"], "partner-tag")
            self.assertEqual(
                captured["body"]["resources"],
                [
                    "itemInfo.byLineInfo",
                    "itemInfo.classifications",
                    "itemInfo.contentInfo",
                    "itemInfo.contentRating",
                    "itemInfo.externalIds",
                    "itemInfo.features",
                    "itemInfo.manufactureInfo",
                    "itemInfo.productInfo",
                    "itemInfo.technicalInfo",
                    "itemInfo.title",
                    "itemInfo.tradeInInfo",
                ],
            )
            self.assertFalse(resp["dry_run"])
            self.assertEqual(resp["receipt"]["operation"], "GetItems")
            self.assertTrue(resp["receipt_out"])
            self.assertTrue(resp["receipt_out"].endswith("receipt.json"))

    def test_variations_request(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)

            captured: dict[str, object] = {}

            def fake_call(cfg, ctx, operation, body, locale):
                captured["operation"] = operation
                captured["body"] = body
                return {"variationsResult": {"items": [{"asin": "B0VAR"}]}}

            with patch("amazon_creators_api_tool.commands.catalog._call_operation", side_effect=fake_call):
                resp = self._run_cmd(
                    env_path,
                    ["--apply", "variations", "get", "--asin", "B0VAR"],
                )

            self.assertEqual(captured["operation"], "GetVariations")
            self.assertEqual(captured["body"]["asin"], "B0VAR")
            self.assertEqual(resp["operation"], "GetVariations")
            self.assertEqual(resp["items"][0]["asin"], "B0VAR")
            self.assertEqual(captured["body"]["marketplace"], "www.amazon.com")
            self.assertEqual(captured["body"]["partnerTag"], "partner-tag")
            self.assertEqual(captured["body"]["variationCount"], 10)
            self.assertEqual(captured["body"]["variationPage"], 1)
            self.assertIn("variationSummary.price.highestPrice", captured["body"]["resources"])
            self.assertIn("variationSummary.price.lowestPrice", captured["body"]["resources"])
            self.assertIn("variationSummary.variationDimension", captured["body"]["resources"])
            self.assertFalse(resp["dry_run"])
            self.assertEqual(resp["receipt"]["operation"], "GetVariations")
            self.assertTrue(resp["receipt_out"])
            self.assertTrue(resp["receipt_out"].endswith("receipt.json"))

    def test_search_request(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)

            captured: dict[str, object] = {}

            def fake_call(cfg, ctx, operation, body, locale):
                captured["operation"] = operation
                captured["body"] = body
                return {"searchResult": {"items": [{"asin": "B0SEARCH"}]}}

            with patch("amazon_creators_api_tool.commands.catalog._call_operation", side_effect=fake_call):
                resp = self._run_cmd(
                    env_path,
                    ["--apply", "search", "--keywords", "book", "--resource", "ItemInfo"],
                )

            self.assertEqual(captured["operation"], "SearchItems")
            self.assertEqual(captured["body"]["keywords"], "book")
            self.assertEqual(captured["body"]["itemCount"], 10)
            self.assertEqual(captured["body"]["itemPage"], 1)
            self.assertEqual(resp["operation"], "SearchItems")
            self.assertEqual(resp["items"][0]["asin"], "B0SEARCH")
            self.assertEqual(captured["body"]["marketplace"], "www.amazon.com")
            self.assertEqual(captured["body"]["partnerTag"], "partner-tag")
            self.assertEqual(
                captured["body"]["resources"],
                [
                    "itemInfo.byLineInfo",
                    "itemInfo.classifications",
                    "itemInfo.contentInfo",
                    "itemInfo.contentRating",
                    "itemInfo.externalIds",
                    "itemInfo.features",
                    "itemInfo.manufactureInfo",
                    "itemInfo.productInfo",
                    "itemInfo.technicalInfo",
                    "itemInfo.title",
                    "itemInfo.tradeInInfo",
                ],
            )
            self.assertFalse(resp["dry_run"])
            self.assertEqual(resp["receipt"]["operation"], "SearchItems")
            self.assertTrue(resp["receipt_out"])
            self.assertTrue(resp["receipt_out"].endswith("receipt.json"))

    def test_catalog_dry_run_plan_skips_http(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)

            with patch("amazon_creators_api_tool.commands.catalog._call_operation") as mock_call:
                resp = self._run_cmd(
                    env_path,
                    ["items", "get", "--item-id", "B0ITEM", "--resource", "ItemInfo"],
                )

            mock_call.assert_not_called()
            self.assertTrue(resp["dry_run"])
            self.assertIn("plan", resp)
            self.assertEqual(resp["plan"]["selector"]["operation"], "GetItems")
            self.assertEqual(
                resp["plan"]["selector"]["resources"],
                [
                    "itemInfo.byLineInfo",
                    "itemInfo.classifications",
                    "itemInfo.contentInfo",
                    "itemInfo.contentRating",
                    "itemInfo.externalIds",
                    "itemInfo.features",
                    "itemInfo.manufactureInfo",
                    "itemInfo.productInfo",
                    "itemInfo.technicalInfo",
                    "itemInfo.title",
                    "itemInfo.tradeInInfo",
                ],
            )
