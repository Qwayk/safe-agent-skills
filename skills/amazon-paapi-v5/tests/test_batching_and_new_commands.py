from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace

import amazon_pa_api_tool.commands.browse as browse_mod
import amazon_pa_api_tool.commands.product as product_mod
from amazon_pa_api_tool.commands._shared import (
    PAAPI_MAX_BROWSE_NODE_IDS_PER_REQUEST,
    PAAPI_MAX_ITEM_IDS_PER_REQUEST,
    batch_values,
    resolve_resources,
)
from amazon_pa_api_tool.output import Output
from amazon_pa_api_tool.paapi import PaApiResponse


class _NullAudit:
    def write(self, *_args: object, **_kwargs: object) -> None:
        return None


class _FakePaApiClient:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict]] = []

    def get_items(self, *, item_ids: list[str], resources: list[str] | None = None) -> PaApiResponse:
        self.calls.append(("GetItems", {"item_ids": list(item_ids), "resources": list(resources or [])}))
        items = [{"ASIN": a, "ItemInfo": {"Title": {"DisplayValue": f"Title {a}"}}} for a in item_ids]
        return PaApiResponse(status=200, request_id=f"req-{len(self.calls)}", data={"ItemsResult": {"Items": items}})

    def get_browse_nodes(self, *, browse_node_ids: list[str], resources: list[str] | None = None) -> PaApiResponse:
        self.calls.append(("GetBrowseNodes", {"browse_node_ids": list(browse_node_ids), "resources": list(resources or [])}))
        nodes = [{"Id": i, "DisplayName": f"Node {i}"} for i in browse_node_ids]
        return PaApiResponse(
            status=200,
            request_id=f"req-{len(self.calls)}",
            data={"BrowseNodesResult": {"BrowseNodes": nodes}},
        )

    def get_variations(
        self,
        *,
        asin: str,
        variation_page: int = 1,
        variation_count: int = 10,
        resources: list[str] | None = None,
    ) -> PaApiResponse:
        self.calls.append(
            (
                "GetVariations",
                {
                    "asin": asin,
                    "variation_page": variation_page,
                    "variation_count": variation_count,
                    "resources": list(resources or []),
                },
            )
        )
        items = [{"ASIN": f"{asin}-{i}"} for i in range(variation_count)]
        return PaApiResponse(
            status=200,
            request_id=f"req-{len(self.calls)}",
            data={"VariationsResult": {"Items": items}},
        )


class TestSharedHelpers(unittest.TestCase):
    def test_resolve_resources_default(self) -> None:
        self.assertEqual(resolve_resources(preset=None, resources=None, default_resources=["A", "B"]), ["A", "B"])

    def test_resolve_resources_preset_and_explicit_dedupes(self) -> None:
        out = resolve_resources(preset="basic", resources=["B", "X", "X"], default_resources=["A", "B"])
        self.assertEqual(out, ["A", "B", "X"])

    def test_resolve_resources_unknown_preset(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "Unknown --resources-preset"):
            resolve_resources(preset="nope", resources=None, default_resources=["A"])

    def test_batch_values_yes_guard(self) -> None:
        values = [str(i) for i in range(11)]
        with self.assertRaisesRegex(RuntimeError, "Re-run with --yes"):
            batch_values(
                values,
                batch_size=10,
                api_max_per_request=10,
                max_requests=10,
                yes=False,
                what="x",
            )

    def test_batch_values_splits_when_yes(self) -> None:
        values = [str(i) for i in range(11)]
        batches = batch_values(
            values,
            batch_size=10,
            api_max_per_request=10,
            max_requests=10,
            yes=True,
            what="x",
        )
        self.assertEqual(len(batches), 2)
        self.assertEqual(batches[0], values[:10])
        self.assertEqual(batches[1], values[10:])

    def test_batch_values_respects_api_max(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "--batch-size must be <= 10"):
            batch_values(
                ["a"],
                batch_size=11,
                api_max_per_request=10,
                max_requests=10,
                yes=True,
                what="x",
            )

    def test_batch_values_max_requests(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "exceeds --max-requests"):
            batch_values(
                [str(i) for i in range(21)],
                batch_size=10,
                api_max_per_request=10,
                max_requests=2,
                yes=True,
                what="x",
            )


class TestNewCommandHandlers(unittest.TestCase):
    def test_product_get_batches_and_calls_client(self) -> None:
        fake = _FakePaApiClient()
        original = product_mod.build_paapi_client
        try:
            product_mod.build_paapi_client = lambda _ctx: fake  # type: ignore[assignment]
            args = SimpleNamespace(
                asin=[f"B0000000{i:02d}" for i in range(11)],
                resources_preset="none",
                resource=["ItemInfo.Title"],
                batch_size=PAAPI_MAX_ITEM_IDS_PER_REQUEST,
                max_requests=10,
            )
            ctx = {"yes": True, "include_raw": False, "audit": _NullAudit(), "out": Output(mode="json")}
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = int(product_mod.cmd_product_get(args, ctx))
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["ok"], True)
            self.assertEqual(payload["requests"], 2)
            self.assertEqual([c[0] for c in fake.calls], ["GetItems", "GetItems"])
            for _, call in fake.calls:
                self.assertEqual(call["resources"], ["ItemInfo.Title"])
        finally:
            product_mod.build_paapi_client = original  # type: ignore[assignment]

    def test_product_get_requires_yes_for_multi_request(self) -> None:
        args = SimpleNamespace(
            asin=[f"B0000000{i:02d}" for i in range(11)],
            resources_preset=None,
            resource=None,
            batch_size=PAAPI_MAX_ITEM_IDS_PER_REQUEST,
            max_requests=10,
        )
        ctx = {"yes": False, "include_raw": False, "audit": _NullAudit(), "out": Output(mode="json")}
        with self.assertRaisesRegex(RuntimeError, "Re-run with --yes"):
            product_mod.cmd_product_get(args, ctx)

    def test_browse_get_batches_and_calls_client(self) -> None:
        fake = _FakePaApiClient()
        original = browse_mod.build_paapi_client
        try:
            browse_mod.build_paapi_client = lambda _ctx: fake  # type: ignore[assignment]
            args = SimpleNamespace(
                browse_node_id=[str(i) for i in range(11)],
                resources_preset="basic",
                resource=None,
                batch_size=PAAPI_MAX_BROWSE_NODE_IDS_PER_REQUEST,
                max_requests=10,
            )
            ctx = {"yes": True, "include_raw": False, "audit": _NullAudit(), "out": Output(mode="json")}
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = int(browse_mod.cmd_browse_get(args, ctx))
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["ok"], True)
            self.assertEqual(payload["requests"], 2)
            self.assertEqual([c[0] for c in fake.calls], ["GetBrowseNodes", "GetBrowseNodes"])
            for _, call in fake.calls:
                self.assertEqual(call["resources"], [])
        finally:
            browse_mod.build_paapi_client = original  # type: ignore[assignment]

    def test_product_variations_calls_client(self) -> None:
        fake = _FakePaApiClient()
        original = product_mod.build_paapi_client
        try:
            product_mod.build_paapi_client = lambda _ctx: fake  # type: ignore[assignment]
            args = SimpleNamespace(
                asin="B000000000",
                variation_page=2,
                variation_count=10,
                resources_preset="basic",
                resource=[],
            )
            ctx = {"yes": False, "include_raw": False, "audit": _NullAudit(), "out": Output(mode="json")}
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = int(product_mod.cmd_product_variations(args, ctx))
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["ok"], True)
            self.assertEqual(payload["asin"], "B000000000")
            self.assertEqual(payload["variation_page"], 2)
            self.assertEqual(payload["variation_count"], 10)
            self.assertEqual(fake.calls[0][0], "GetVariations")
        finally:
            product_mod.build_paapi_client = original  # type: ignore[assignment]
