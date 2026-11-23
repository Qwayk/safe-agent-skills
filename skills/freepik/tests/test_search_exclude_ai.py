from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from freepik_api_tool.commands.search import cmd_search_images
from freepik_api_tool.config import Config
from freepik_api_tool.freepik_api import FreepikApi


class TestSearchExcludeAi(unittest.TestCase):
    def test_exclude_ai_filters_by_detail_flags(self) -> None:
        cfg = Config(
            base_url="https://api.freepik.com/v1",
            api_key="k",
            timeout_s=1.0,
            auth_header="x-freepik-api-key",
            auth_prefix="",
            accept_language=None,
            image_size=None,
            download_url_jsonpath=None,
            license_url_jsonpath=None,
        )

        args = SimpleNamespace(
            query="ai",
            page=1,
            limit=5,
            param=[],
            exclude_ai=True,
        )

        out = Mock()
        ctx = {"cfg": cfg, "timeout_s": 1.0, "verbose": False, "out": out}

        search_payload = {"data": [{"id": rid} for rid in range(1, 6)], "meta": {"total": 5}}

        def _detail_for(rid: str) -> dict[str, object]:
            if rid == "2":
                return {"data": {"id": 2, "is_ai_generated": True}}
            if rid == "3":
                return {"data": {"id": 3, "has_prompt": True}}
            if rid == "4":
                return {"data": {"id": 4, "is_ai_generated": False}}
            return {"data": {"id": 1, "is_ai_generated": False, "has_prompt": False}}

        with patch.object(FreepikApi, "get_resources", autospec=True, return_value=search_payload), patch.object(
            FreepikApi,
            "get_resource",
            autospec=True,
            side_effect=lambda self, rid: _detail_for(rid),
        ):
            rc = cmd_search_images(args, ctx)
            emitted = out.emit.call_args.args[0]
            args.shortlist = True
            cmd_search_images(args, ctx)

        self.assertEqual(rc, 0)
        self.assertEqual([x["id"] for x in emitted["data"]], [1])
        self.assertEqual(emitted["tool"]["removed_ids"], ["2", "3", "4", "5"])
        self.assertEqual(emitted["tool"]["unknown"], 2)
        shortlist = out.emit.call_args.args[0]
        self.assertEqual([x["id"] for x in shortlist["items"]], ["1"])
        self.assertEqual(shortlist["tool"], emitted["tool"])
