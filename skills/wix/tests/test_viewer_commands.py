from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import viewer
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = action, payload


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestViewerCommands(unittest.TestCase):
    def _ctx(self, **overrides) -> dict:
        cfg = SimpleNamespace(
            base_url="https://www.wixapis.com",
            timeout_s=30.0,
            access_token="token",
            api_key=None,
            account_id=None,
            app_id=None,
            app_secret=None,
            instance_id=None,
            has_official_app_auth=False,
        )
        ctx = {
            "cfg": cfg,
            "env_file": "/tmp/.env",
            "tool": "wix-safe-agent-cli",
            "tool_version": "0.0.0",
            "command_str": "wix-safe-agent-cli viewer-cache invalidate",
            "apply": False,
            "yes": False,
            "verbose": False,
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
            "plan_in": None,
            "plan_out": None,
            "receipt_out": None,
            "ack_irreversible": False,
            "enforce_reviewed_plan": False,
        }
        ctx.update(overrides)
        return ctx

    def test_parser_recognizes_viewer_commands(self) -> None:
        parser = build_parser()
        invalidate = parser.parse_args(["viewer-cache", "invalidate", "--invalidation-methods-json", '[{"tag":"products"}]'])
        seo = parser.parse_args(["viewer-seo-tags", "resolve-item", "--page-url", "https://example.com/p/shoe", "--slug", "shoe", "--item-type", "wix-stores-product"])
        self.assertEqual(invalidate.viewer_cache_cmd, "invalidate")
        self.assertTrue(invalidate.write_capable)
        self.assertEqual(seo.viewer_seo_tags_cmd, "resolve-item")
        self.assertFalse(seo.write_capable)

    def test_cache_invalidate_dry_run_plan(self) -> None:
        args = SimpleNamespace(invalidation_methods_json='[{"tag":"products"}]')
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = viewer.cmd_viewer_cache_invalidate(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["auth_mode"], "app_token")
        self.assertEqual(payload["plan"]["request"]["path"], "/ssr/v1/invalidate-cache")
        self.assertEqual(payload["plan"]["request"]["body"]["invalidationMethods"][0]["tag"], "products")

    def test_cache_invalidate_requires_tag(self) -> None:
        args = SimpleNamespace(invalidation_methods_json='[{}]')
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = viewer.cmd_viewer_cache_invalidate(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertIn("tag", payload["error"])

    @patch("wix_safe_agent_cli.commands.viewer.HttpClient")
    def test_resolve_item_uses_official_path_and_params(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"seoTags": {"id": "tags-1"}})
        args = SimpleNamespace(page_url="https://example.com/p/shoe", slug="shoe", item_type="wix-stores-product", seo_data_json=None)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = viewer.cmd_viewer_seo_tags_resolve_item(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["path"], "/promote/seo/v1/resolve-item-seo-tags")
        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["params"]["pageUrl"], "https://example.com/p/shoe")
        self.assertEqual(call.kwargs["params"]["slug"], "shoe")
        self.assertEqual(call.kwargs["params"]["itemType"], "wix-stores-product")


if __name__ == "__main__":
    unittest.main()
