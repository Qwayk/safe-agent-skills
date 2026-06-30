from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import pro_gallery
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = action, payload


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestProGalleryCommands(unittest.TestCase):
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
            "verbose": False,
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
            "apply": False,
            "yes": False,
            "ack_irreversible": False,
            "plan_in": None,
            "plan_out": None,
            "receipt_out": None,
        }
        ctx.update(overrides)
        return ctx

    @patch("wix_safe_agent_cli.commands.pro_gallery.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.pro_gallery.HttpClient")
    def test_pro_gallery_reads_use_official_paths(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "Bearer token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"gallery": {"id": "gallery-1"}})

        cases = [
            (
                pro_gallery.cmd_pro_gallery_list_galleries,
                SimpleNamespace(params_json='{"limit":10}'),
                "GET",
                "/progallery/v2/galleries",
            ),
            (
                pro_gallery.cmd_pro_gallery_get_gallery,
                SimpleNamespace(gallery_id="gallery-1"),
                "GET",
                "/progallery/v2/galleries/gallery-1",
            ),
            (
                pro_gallery.cmd_pro_gallery_list_gallery_items,
                SimpleNamespace(gallery_id="gallery-1", params_json=None),
                "GET",
                "/progallery/v2/galleries/gallery-1/items",
            ),
            (
                pro_gallery.cmd_pro_gallery_get_gallery_item,
                SimpleNamespace(gallery_id="gallery-1", item_id="item-1"),
                "GET",
                "/progallery/v2/galleries/gallery-1/items/item-1",
            ),
        ]

        for func, args, http_method, path in cases:
            with self.subTest(path=path):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())

                self.assertEqual(rc, 0)
                self.assertEqual(payload["request"]["method"], http_method)
                self.assertEqual(payload["request"]["path"], path)
                self.assertEqual(payload["auth_mode"], "access_token")

    @patch("wix_safe_agent_cli.commands.pro_gallery.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.pro_gallery.HttpClient")
    def test_pro_gallery_create_dry_run_builds_reviewed_plan(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "Bearer token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"gallery": {"id": "gallery-1"}})

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = pro_gallery.cmd_pro_gallery_create_gallery(
                SimpleNamespace(gallery_json='{"gallery":{"name":"My Gallery"}}'),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["request"]["method"], "POST")
        self.assertEqual(payload["plan"]["request"]["path"], "/progallery/v2/galleries")
        self.assertIn("apply requires --plan-in, --apply, and --yes", payload["plan"]["preconditions"])

    @patch("wix_safe_agent_cli.commands.pro_gallery.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.pro_gallery.HttpClient")
    def test_pro_gallery_delete_requires_irreversible_ack(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "Bearer token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"gallery": {"id": "gallery-1"}})

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = pro_gallery.cmd_pro_gallery_delete_gallery(SimpleNamespace(gallery_id="gallery-1"), self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
        self.assertEqual(payload["plan"]["request"]["method"], "DELETE")
        self.assertEqual(payload["plan"]["request"]["path"], "/progallery/v2/galleries/gallery-1")

    def test_invalid_json_is_rejected(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = pro_gallery.cmd_pro_gallery_create_gallery(SimpleNamespace(gallery_json="[]"), self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("JSON object", payload["error"])

    def test_parser_includes_pro_gallery_commands(self) -> None:
        parser = build_parser()
        parsed = parser.parse_args(["pro-gallery", "bulk-delete-gallery-items", "--gallery-id", "gallery-1", "--delete-json", '{"itemIds":["item-1"]}'])
        self.assertTrue(parsed.write_capable)
        self.assertIs(parsed.func, pro_gallery.cmd_pro_gallery_bulk_delete_gallery_items)
