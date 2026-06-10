from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace

from pinterest_api_tool.commands import report_jobs as report_jobs_cmd
from pinterest_api_tool.config import Config
from pinterest_api_tool.http import DownloadExceededError, HttpResponse
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
                "json": kwargs.get("json_body"),
            }
        )
        if not self._responses:
            raise AssertionError("No more fake responses available")
        data = self._responses.pop(0)
        return HttpResponse(status=200, headers={}, body=json.dumps(data).encode("utf-8"), url=url)


class _Audit:
    def write(self, event: str, payload):  # noqa: ANN001
        _ = event, payload


class TestAdsReportsCommands(unittest.TestCase):
    def _ctx(self, http: _FakeHttp, *, apply: bool, yes: bool, ack_volume: bool, ack_no_snapshot: bool = False) -> dict:
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
            "apply": bool(apply),
            "yes": bool(yes),
            "ack_volume": bool(ack_volume),
            "ack_no_snapshot": bool(ack_no_snapshot),
        }

    def test_ads_reports_create_refuses_without_apply_yes_ack_volume(self) -> None:
        http = _FakeHttp([{"token": "t"}])
        ctx = self._ctx(http, apply=False, yes=False, ack_volume=False)
        with tempfile.TemporaryDirectory() as td:
            body_file = os.path.join(td, "req.json")
            with open(body_file, "w", encoding="utf-8") as f:
                json.dump({"foo": "bar"}, f)
            args = SimpleNamespace(ad_account_id="123", body_file=body_file)
            with self.assertRaises(RuntimeError) as e:
                report_jobs_cmd.cmd_ads_reports_create(args, ctx)
        self.assertIn("--apply", str(e.exception))
        self.assertIn("--yes", str(e.exception))
        self.assertIn("--ack-volume", str(e.exception))
        self.assertEqual(http.calls, [])

    def test_ads_reports_create_requires_no_snapshot_ack_before_post(self) -> None:
        http = _FakeHttp([{"token": "tok_1"}])
        ctx = self._ctx(http, apply=True, yes=True, ack_volume=True)
        with tempfile.TemporaryDirectory() as td:
            body_file = os.path.join(td, "req.json")
            with open(body_file, "w", encoding="utf-8") as f:
                json.dump({"level": "ad_account", "foo": "bar"}, f)
            args = SimpleNamespace(ad_account_id="123", body_file=body_file)

            with self.assertRaisesRegex(RuntimeError, "--ack-no-snapshot"):
                report_jobs_cmd.cmd_ads_reports_create(args, ctx)
            self.assertEqual(http.calls, [])

    def test_ads_reports_get_builds_correct_path_and_token_param(self) -> None:
        http = _FakeHttp([{"status": "FINISHED", "url": "https://example.com/r.csv"}])
        ctx = self._ctx(http, apply=False, yes=False, ack_volume=False)
        args = SimpleNamespace(ad_account_id="123", token="tok_1")

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = report_jobs_cmd.cmd_ads_reports_get(args, ctx)
        self.assertEqual(rc, 0)

        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["token"], "tok_1")

        self.assertEqual(len(http.calls), 1)
        self.assertEqual(http.calls[0]["method"], "GET")
        self.assertIn("/ad_accounts/123/reports", str(http.calls[0]["url"]))
        self.assertEqual(http.calls[0]["params"], {"token": "tok_1"})

    def test_ads_reports_run_requires_no_snapshot_ack_before_report_receipt_or_download(self) -> None:
        class _FakeHttpWithDownload(_FakeHttp):
            def download_to_file(self, url: str, *, max_bytes: int, dest_path: str, **kwargs):  # noqa: ANN001
                _ = url, max_bytes, dest_path, kwargs
                raise DownloadExceededError("exceeded")

        http = _FakeHttpWithDownload(
            [
                {"token": "tok_1"},
                {"status": "IN_PROGRESS"},
                {"status": "FINISHED", "url": "https://example.com/r.csv"},
            ]
        )
        ctx = self._ctx(http, apply=True, yes=True, ack_volume=True)
        with tempfile.TemporaryDirectory() as td:
            body_file = os.path.join(td, "req.json")
            with open(body_file, "w", encoding="utf-8") as f:
                json.dump({"foo": "bar"}, f)
            out_dir = os.path.join(td, "out")
            args = SimpleNamespace(
                ad_account_id="123",
                body_file=body_file,
                out_dir=out_dir,
                max_poll_attempts=10,
                max_poll_seconds=60.0,
                poll_interval_s=0.0,
                max_download_bytes=5,
            )

            with self.assertRaisesRegex(RuntimeError, "--ack-no-snapshot"):
                report_jobs_cmd.cmd_ads_reports_run(args, ctx)
            self.assertEqual(http.calls, [])
            self.assertFalse(os.path.exists(out_dir))
