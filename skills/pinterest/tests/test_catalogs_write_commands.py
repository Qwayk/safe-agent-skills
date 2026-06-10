from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace

from pinterest_api_tool.commands import catalogs as catalogs_cmd
from pinterest_api_tool.config import Config
from pinterest_api_tool.http import HttpResponse
from pinterest_api_tool.output import Output


class _FakeHttp:
    def __init__(self, responses: list[dict]) -> None:
        self._responses = list(responses)
        self.calls: list[dict[str, object]] = []

    def request(self, method: str, url: str, **kwargs):  # noqa: ANN001
        self.calls.append(
            {
                "method": method,
                "url": url,
                "params": kwargs.get("params"),
                "json_body": kwargs.get("json_body"),
            }
        )
        if not self._responses:
            raise AssertionError("No more fake responses available")
        data = self._responses.pop(0)
        return HttpResponse(status=200, headers={}, body=json.dumps(data).encode("utf-8"), url=url)


class _Audit:
    def write(self, event: str, payload):  # noqa: ANN001
        _ = event, payload


def _ctx(*, http: _FakeHttp, apply: bool, yes: bool, ack_volume: bool) -> dict:
    return {
        "cfg": Config(
            base_url="https://api.pinterest.com/v5",
            access_token="X",
            app_id=None,
            app_secret=None,
            refresh_token=None,
            timeout_s=30,
        ),
        "http": http,
        "env_file": "/tmp/.env",
        "out": Output(mode="json"),
        "audit": _Audit(),
        "apply": apply,
        "yes": yes,
        "ack_spend": False,
        "ack_volume": ack_volume,
    }


class TestCatalogsWriteCommands(unittest.TestCase):
    def test_dry_run_create_update_ingest_makes_no_http_calls(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            catalog_json = td_path / "catalog.json"
            feed_json = td_path / "feed.json"
            feed_update_json = td_path / "feed_update.json"
            catalog_json.write_text(json.dumps({"name": "cat1", "catalog_type": "RETAIL"}, indent=2) + "\n", encoding="utf-8")
            feed_json.write_text(json.dumps({"name": "feed1"}, indent=2) + "\n", encoding="utf-8")
            feed_update_json.write_text(json.dumps({"name": "feed1-updated"}, indent=2) + "\n", encoding="utf-8")

            cases = [
                (
                    catalogs_cmd.cmd_catalogs_create,
                    SimpleNamespace(ad_account_id="123", body_file=str(catalog_json)),
                ),
                (
                    catalogs_cmd.cmd_catalogs_feeds_create,
                    SimpleNamespace(ad_account_id="123", body_file=str(feed_json)),
                ),
                (
                    catalogs_cmd.cmd_catalogs_feeds_update,
                    SimpleNamespace(ad_account_id="123", id="f1", body_file=str(feed_update_json)),
                ),
                (
                    catalogs_cmd.cmd_catalogs_feeds_ingest,
                    SimpleNamespace(ad_account_id="123", id="f1"),
                ),
            ]
            for fn, args in cases:
                http = _FakeHttp([])
                ctx = _ctx(http=http, apply=False, yes=False, ack_volume=False)
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = fn(args, ctx)
                self.assertEqual(rc, 0)
                payload = json.loads(buf.getvalue())
                self.assertTrue(payload["ok"])
                self.assertTrue(payload["dry_run"])
                self.assertIn("action", payload)
                self.assertIn("resource", payload)
                self.assertIn("request", payload)
                self.assertEqual(http.calls, [])

    def test_apply_ingest_requires_ack_volume(self) -> None:
        http = _FakeHttp([])
        ctx = _ctx(http=http, apply=True, yes=True, ack_volume=False)
        args = SimpleNamespace(ad_account_id="123", id="f1")
        with self.assertRaisesRegex(RuntimeError, "--ack-volume"):
            catalogs_cmd.cmd_catalogs_feeds_ingest(args, ctx)
        self.assertEqual(http.calls, [])

    def test_confirmed_apply_requires_no_snapshot_ack_before_catalog_write_calls(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            update_json = Path(td) / "feed_update.json"
            update_json.write_text(json.dumps({"name": "feed1-updated"}, indent=2) + "\n", encoding="utf-8")

            http = _FakeHttp([{"id": "f1"}, {"id": "f1"}, {"id": "f1"}])
            ctx = _ctx(http=http, apply=True, yes=True, ack_volume=False)
            args = SimpleNamespace(ad_account_id="123", id="f1", body_file=str(update_json))
            with self.assertRaisesRegex(RuntimeError, "--ack-no-snapshot"):
                catalogs_cmd.cmd_catalogs_feeds_update(args, ctx)
            self.assertEqual(http.calls, [])

            http = _FakeHttp([{"ok": True}, {"id": "f1"}])
            ctx = _ctx(http=http, apply=True, yes=True, ack_volume=True)
            args = SimpleNamespace(ad_account_id="123", id="f1")
            with self.assertRaisesRegex(RuntimeError, "--ack-no-snapshot"):
                catalogs_cmd.cmd_catalogs_feeds_ingest(args, ctx)
            self.assertEqual(http.calls, [])
