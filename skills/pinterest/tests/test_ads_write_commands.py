from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace

from pinterest_api_tool.commands import ads as ads_cmd
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


def _ctx(*, http: _FakeHttp, apply: bool, yes: bool, ack_spend: bool) -> dict:
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
        "ack_spend": ack_spend,
        "ack_volume": False,
    }


class TestAdsWriteCommands(unittest.TestCase):
    def test_dry_run_create_update_pause_makes_no_write_calls(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            create_json = td_path / "create.json"
            update_json = td_path / "update.json"
            create_json.write_text(json.dumps({"name": "c1", "objective_type": "AWARENESS"}, indent=2) + "\n", encoding="utf-8")
            update_json.write_text(json.dumps({"name": "c1-updated"}, indent=2) + "\n", encoding="utf-8")

            cases = [
                (
                    ads_cmd.cmd_ads_campaigns_create,
                    SimpleNamespace(ad_account_id="123", body_file=str(create_json)),
                ),
                (
                    ads_cmd.cmd_ads_campaigns_update,
                    SimpleNamespace(ad_account_id="123", id="c123", body_file=str(update_json)),
                ),
                (
                    ads_cmd.cmd_ads_campaigns_pause,
                    SimpleNamespace(ad_account_id="123", id="c123"),
                ),
            ]
            for fn, args in cases:
                http = _FakeHttp([])
                ctx = _ctx(http=http, apply=False, yes=False, ack_spend=False)
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

    def test_apply_without_yes_is_refused(self) -> None:
        http = _FakeHttp([])
        ctx = _ctx(http=http, apply=True, yes=False, ack_spend=True)
        args = SimpleNamespace(ad_account_id="123", id="c123")
        with self.assertRaisesRegex(RuntimeError, "--yes"):
            ads_cmd.cmd_ads_campaigns_pause(args, ctx)
        self.assertEqual(http.calls, [])

    def test_apply_spend_ops_require_ack_spend(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            body_path = Path(td) / "create.json"
            body_path.write_text(json.dumps({"name": "c1", "objective_type": "AWARENESS"}, indent=2) + "\n", encoding="utf-8")

            http = _FakeHttp([])
            ctx = _ctx(http=http, apply=True, yes=True, ack_spend=False)
            args = SimpleNamespace(ad_account_id="123", body_file=str(body_path))
            with self.assertRaisesRegex(RuntimeError, "--ack-spend"):
                ads_cmd.cmd_ads_campaigns_create(args, ctx)
            self.assertEqual(http.calls, [])

    def test_pause_does_not_require_ack_spend_but_requires_no_snapshot_ack(self) -> None:
        http = _FakeHttp([{"id": "c123", "status": "PAUSED"}])
        ctx = _ctx(http=http, apply=True, yes=True, ack_spend=False)
        args = SimpleNamespace(ad_account_id="123", id="c123")
        with self.assertRaisesRegex(RuntimeError, "--ack-no-snapshot"):
            ads_cmd.cmd_ads_campaigns_pause(args, ctx)
        self.assertEqual(http.calls, [])

    def test_confirmed_apply_requires_no_snapshot_ack_before_ad_write_calls(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            create_campaign_json = td_path / "create_campaign.json"
            update_ad_group_json = td_path / "update_ad_group.json"
            create_campaign_json.write_text(
                json.dumps({"name": "c1", "objective_type": "AWARENESS"}, indent=2) + "\n",
                encoding="utf-8",
            )
            update_ad_group_json.write_text(json.dumps({"name": "ag1-new"}, indent=2) + "\n", encoding="utf-8")

            http = _FakeHttp([{"items": [{"data": {"id": "c1"}}]}, {"id": "c1"}])
            ctx = _ctx(http=http, apply=True, yes=True, ack_spend=True)
            args = SimpleNamespace(ad_account_id="123", body_file=str(create_campaign_json))
            with self.assertRaisesRegex(RuntimeError, "--ack-no-snapshot"):
                ads_cmd.cmd_ads_campaigns_create(args, ctx)
            self.assertEqual(http.calls, [])

            http = _FakeHttp([{"items": [{"data": {"id": "ag1"}}]}, {"id": "ag1"}])
            ctx = _ctx(http=http, apply=True, yes=True, ack_spend=True)
            args = SimpleNamespace(ad_account_id="123", id="ag1", body_file=str(update_ad_group_json))
            with self.assertRaisesRegex(RuntimeError, "--ack-no-snapshot"):
                ads_cmd.cmd_ads_ad_groups_update(args, ctx)
            self.assertEqual(http.calls, [])

            http = _FakeHttp(
                [
                    {"id": "a1", "status": "ACTIVE"},
                    {"items": [{"data": {"id": "a1"}}]},
                    {"id": "a1", "status": "PAUSED"},
                ]
            )
            ctx = _ctx(http=http, apply=True, yes=True, ack_spend=False)
            args = SimpleNamespace(ad_account_id="123", id="a1")
            with self.assertRaisesRegex(RuntimeError, "--ack-no-snapshot"):
                ads_cmd.cmd_ads_ads_pause(args, ctx)
            self.assertEqual(http.calls, [])
