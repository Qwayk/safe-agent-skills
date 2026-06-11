from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace

from pinterest_api_tool.commands.audit import cmd_audit_snapshot
from pinterest_api_tool.config import Config
from pinterest_api_tool.http import HttpResponse
from pinterest_api_tool.output import Output


class _FakeHttp:
    def __init__(self, responses: list[dict]) -> None:
        self._responses = list(responses)
        self.calls: list[dict[str, object]] = []

    def request(self, method: str, url: str, **kwargs):  # noqa: ANN001
        self.calls.append({"method": method, "url": url, "params": kwargs.get("params")})
        if not self._responses:
            raise AssertionError("No more fake responses available")
        data = self._responses.pop(0)
        if isinstance(data, dict) and data.get("_raise"):
            raise RuntimeError(str(data["_raise"]))
        return HttpResponse(status=200, headers={}, body=json.dumps(data).encode("utf-8"), url=url)


class _Audit:
    def write(self, event: str, payload):  # noqa: ANN001
        _ = event, payload


class TestAuditSnapshot(unittest.TestCase):
    def test_snapshot_writes_files(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            tool_dir = Path(d) / "tool"
            tool_dir.mkdir()
            env_file = tool_dir / ".env"
            env_file.write_text("PINTEREST_API_BASE_URL=https://api.pinterest.com/v5\n", encoding="utf-8")

            token_dir = tool_dir / ".state"
            token_dir.mkdir()
            (token_dir / "token.json").write_text(json.dumps({"access_token": "X"}), encoding="utf-8")

            out_dir = Path(d) / "out"

            http = _FakeHttp(
                [
                    {"items": [{"id": "b1"}], "bookmark": None},  # /boards
                    {"items": [], "bookmark": None},  # /boards/b1/sections
                    {"items": [{"id": "p1"}], "bookmark": None},  # /pins
                ]
            )

            args = SimpleNamespace(
                out_dir=str(out_dir),
                ad_account_id=None,
                include_ads=False,
                include_catalogs=False,
                include_user_account=False,
                include_business_access=False,
                business_id=None,
                include_resources=False,
                include_conversions=False,
                export_limit=50000,
                export_page_size=100,
                boards_limit=100000,
                pins_limit=1000000,
                page_size=100,
                skip_analytics=True,
            )
            ctx = {
                "cfg": Config(
                    base_url="https://api.pinterest.com/v5",
                    access_token=None,
                    app_id=None,
                    app_secret=None,
                    refresh_token=None,
                    timeout_s=30,
                ),
                "http": http,
                "env_file": str(env_file),
                "out": Output(mode="json"),
                "audit": _Audit(),
            }

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_audit_snapshot(args, ctx)
            self.assertEqual(rc, 0)

            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            files = payload["files"]
            for key in ["meta", "boards", "board_sections_by_board", "boards_summary", "pins"]:
                self.assertIn(key, files)
                self.assertTrue(Path(files[key]).exists())

            self.assertEqual(payload["fatal_errors"], [])
            self.assertEqual(len(http.calls), 3)
            self.assertIn("/boards", str(http.calls[0]["url"]))
            self.assertIn("/boards/b1/sections", str(http.calls[1]["url"]))
            self.assertIn("/pins", str(http.calls[2]["url"]))

    def test_snapshot_include_ads_requires_ad_account_id_and_warns(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            tool_dir = Path(d) / "tool"
            tool_dir.mkdir()
            env_file = tool_dir / ".env"
            env_file.write_text("PINTEREST_API_BASE_URL=https://api.pinterest.com/v5\n", encoding="utf-8")

            token_dir = tool_dir / ".state"
            token_dir.mkdir()
            (token_dir / "token.json").write_text(json.dumps({"access_token": "X"}), encoding="utf-8")

            out_dir = Path(d) / "out"

            http = _FakeHttp(
                [
                    {"items": [{"id": "b1"}], "bookmark": None},  # /boards
                    {"items": [], "bookmark": None},  # /boards/b1/sections
                    {"items": [{"id": "p1"}], "bookmark": None},  # /pins
                ]
            )

            args = SimpleNamespace(
                out_dir=str(out_dir),
                ad_account_id=None,
                include_ads=True,
                include_catalogs=False,
                include_user_account=False,
                include_business_access=False,
                business_id=None,
                include_resources=False,
                include_conversions=False,
                export_limit=50000,
                export_page_size=100,
                boards_limit=100000,
                pins_limit=1000000,
                page_size=100,
                skip_analytics=True,
            )
            ctx = {
                "cfg": Config(
                    base_url="https://api.pinterest.com/v5",
                    access_token=None,
                    app_id=None,
                    app_secret=None,
                    refresh_token=None,
                    timeout_s=30,
                ),
                "http": http,
                "env_file": str(env_file),
                "out": Output(mode="json"),
                "audit": _Audit(),
            }

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_audit_snapshot(args, ctx)
            self.assertEqual(rc, 0)

            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(len(http.calls), 3)
            warnings = payload.get("warnings") or []
            self.assertTrue(any(w.get("stage") == "ads" for w in warnings))
            self.assertNotIn("ads_ad_accounts", payload.get("files") or {})

    def test_snapshot_include_ads_and_catalogs_writes_extra_files(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            tool_dir = Path(d) / "tool"
            tool_dir.mkdir()
            env_file = tool_dir / ".env"
            env_file.write_text("PINTEREST_API_BASE_URL=https://api.pinterest.com/v5\n", encoding="utf-8")

            token_dir = tool_dir / ".state"
            token_dir.mkdir()
            (token_dir / "token.json").write_text(json.dumps({"access_token": "X"}), encoding="utf-8")

            out_dir = Path(d) / "out"

            http = _FakeHttp(
                [
                    {"items": [{"id": "b1"}], "bookmark": None},  # /boards
                    {"items": [], "bookmark": None},  # /boards/b1/sections
                    {"items": [{"id": "p1"}], "bookmark": None},  # /pins
                    {"items": [{"id": "a1"}], "bookmark": None},  # /ad_accounts
                    {"items": [{"id": "c1"}], "bookmark": None},  # /ad_accounts/{id}/campaigns
                    {"items": [{"id": "g1"}], "bookmark": None},  # /ad_accounts/{id}/ad_groups
                    {"items": [{"id": "ad1"}], "bookmark": None},  # /ad_accounts/{id}/ads
                    {"rows": []},  # /ad_accounts/{id}/analytics (shape varies by endpoint)
                    {"rows": []},  # /ad_accounts/{id}/campaigns/analytics
                    {"rows": []},  # /ad_accounts/{id}/ad_groups/analytics
                    {"rows": []},  # /ad_accounts/{id}/ads/analytics
                    {"rows": []},  # /ad_accounts/{id}/pins/analytics
                    {"rows": []},  # /ad_accounts/{id}/targeting_analytics
                    {"rows": []},  # /ad_accounts/{id}/campaigns/targeting_analytics
                    {"rows": []},  # /ad_accounts/{id}/ad_groups/targeting_analytics
                    {"rows": []},  # /ad_accounts/{id}/ads/targeting_analytics
                    {"insights": {}},  # /ad_accounts/{id}/audience_insights
                    {"audiences": []},  # /ad_accounts/{id}/insights/audiences
                    {"items": [{"id": "cat1"}], "bookmark": None},  # /catalogs
                    {"items": [{"id": "f1"}], "bookmark": None},  # /catalogs/feeds
                    {"items": [{"id": "pg1"}], "bookmark": None},  # /catalogs/product_groups
                    {"items": [{"id": "r1"}], "bookmark": None},  # /catalogs/reports
                    {"stats": {}},  # /catalogs/reports/stats
                    {"items": [{"id": "pr1"}], "bookmark": None},  # /catalogs/feeds/f1/processing_results
                    {"items": [{"id": "ii1"}], "bookmark": None},  # /catalogs/processing_results/pr1/item_issues
                    {"items": [{"id": "prod1"}], "bookmark": None},  # /catalogs/product_groups/pg1/products
                ]
            )

            args = SimpleNamespace(
                out_dir=str(out_dir),
                ad_account_id="123",
                include_ads=True,
                include_catalogs=True,
                include_user_account=False,
                include_business_access=False,
                business_id=None,
                include_resources=False,
                include_conversions=False,
                export_limit=50000,
                export_page_size=100,
                boards_limit=100000,
                pins_limit=1000000,
                page_size=100,
                skip_analytics=True,
            )
            ctx = {
                "cfg": Config(
                    base_url="https://api.pinterest.com/v5",
                    access_token=None,
                    app_id=None,
                    app_secret=None,
                    refresh_token=None,
                    timeout_s=30,
                ),
                "http": http,
                "env_file": str(env_file),
                "out": Output(mode="json"),
                "audit": _Audit(),
            }

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_audit_snapshot(args, ctx)
            self.assertEqual(rc, 0)

            payload = json.loads(buf.getvalue())
            files = payload["files"]
            for key in [
                "ads_ad_accounts",
                "ads_campaigns",
                "ads_ad_groups",
                "ads_ads",
                "ads_ad_account_analytics",
                "ads_campaigns_analytics",
                "ads_ad_groups_analytics",
                "ads_ads_analytics",
                "ads_pins_analytics",
                "ads_targeting_analytics_ad_account",
                "ads_targeting_analytics_campaigns",
                "ads_targeting_analytics_ad_groups",
                "ads_targeting_analytics_ads",
                "ads_audience_insights",
                "ads_insights_audiences",
                "catalogs_catalogs",
                "catalogs_feeds",
                "catalogs_product_groups",
                "catalogs_reports",
                "catalogs_reports_stats",
                "catalogs_feed_processing_results_dir",
                "catalogs_item_issues_dir",
                "catalogs_product_group_products_dir",
            ]:
                self.assertIn(key, files)
                self.assertTrue(Path(files[key]).exists())
            self.assertTrue((out_dir / "catalogs" / "feed_processing_results" / "f1.json").exists())
            self.assertTrue((out_dir / "catalogs" / "item_issues" / "pr1.json").exists())
            self.assertTrue((out_dir / "catalogs" / "product_group_products" / "pg1.json").exists())

    def test_snapshot_include_ads_failure_is_warning(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            tool_dir = Path(d) / "tool"
            tool_dir.mkdir()
            env_file = tool_dir / ".env"
            env_file.write_text("PINTEREST_API_BASE_URL=https://api.pinterest.com/v5\n", encoding="utf-8")

            token_dir = tool_dir / ".state"
            token_dir.mkdir()
            (token_dir / "token.json").write_text(json.dumps({"access_token": "X"}), encoding="utf-8")

            out_dir = Path(d) / "out"

            http = _FakeHttp(
                [
                    {"items": [{"id": "b1"}], "bookmark": None},  # /boards
                    {"items": [], "bookmark": None},  # /boards/b1/sections
                    {"items": [{"id": "p1"}], "bookmark": None},  # /pins
                    {"items": [{"id": "a1"}], "bookmark": None},  # /ad_accounts
                    {"_raise": "HTTP 403 for GET https://api.pinterest.com/v5/ad_accounts/123/campaigns"},  # campaigns
                    {"items": [{"id": "g1"}], "bookmark": None},  # /ad_accounts/{id}/ad_groups
                    {"items": [{"id": "ad1"}], "bookmark": None},  # /ad_accounts/{id}/ads
                    {"rows": []},  # /ad_accounts/{id}/analytics
                    {"rows": []},  # /ad_accounts/{id}/campaigns/analytics
                    {"rows": []},  # /ad_accounts/{id}/ad_groups/analytics
                    {"rows": []},  # /ad_accounts/{id}/ads/analytics
                    {"rows": []},  # /ad_accounts/{id}/pins/analytics
                    {"rows": []},  # /ad_accounts/{id}/targeting_analytics
                    {"rows": []},  # /ad_accounts/{id}/campaigns/targeting_analytics
                    {"rows": []},  # /ad_accounts/{id}/ad_groups/targeting_analytics
                    {"rows": []},  # /ad_accounts/{id}/ads/targeting_analytics
                    {"insights": {}},  # /ad_accounts/{id}/audience_insights
                    {"audiences": []},  # /ad_accounts/{id}/insights/audiences
                ]
            )

            args = SimpleNamespace(
                out_dir=str(out_dir),
                ad_account_id="123",
                include_ads=True,
                include_catalogs=False,
                include_user_account=False,
                include_business_access=False,
                business_id=None,
                include_resources=False,
                include_conversions=False,
                export_limit=50000,
                export_page_size=100,
                boards_limit=100000,
                pins_limit=1000000,
                page_size=100,
                skip_analytics=True,
            )
            ctx = {
                "cfg": Config(
                    base_url="https://api.pinterest.com/v5",
                    access_token=None,
                    app_id=None,
                    app_secret=None,
                    refresh_token=None,
                    timeout_s=30,
                ),
                "http": http,
                "env_file": str(env_file),
                "out": Output(mode="json"),
                "audit": _Audit(),
            }

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_audit_snapshot(args, ctx)
            self.assertEqual(rc, 0)

            payload = json.loads(buf.getvalue())
            warnings = payload.get("warnings") or []
            self.assertTrue(any(w.get("stage") == "ads_campaigns" for w in warnings))
            files = payload.get("files") or {}
            self.assertIn("ads_ad_accounts", files)
            self.assertIn("ads_ad_groups", files)
            self.assertIn("ads_ads", files)
            self.assertNotIn("ads_campaigns", files)

    def test_snapshot_include_business_access_requires_business_id_and_warns(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            tool_dir = Path(d) / "tool"
            tool_dir.mkdir()
            env_file = tool_dir / ".env"
            env_file.write_text("PINTEREST_API_BASE_URL=https://api.pinterest.com/v5\n", encoding="utf-8")

            token_dir = tool_dir / ".state"
            token_dir.mkdir()
            (token_dir / "token.json").write_text(json.dumps({"access_token": "X"}), encoding="utf-8")

            out_dir = Path(d) / "out"

            http = _FakeHttp(
                [
                    {"items": [{"id": "b1"}], "bookmark": None},  # /boards
                    {"items": [], "bookmark": None},  # /boards/b1/sections
                    {"items": [{"id": "p1"}], "bookmark": None},  # /pins
                ]
            )

            args = SimpleNamespace(
                out_dir=str(out_dir),
                ad_account_id=None,
                include_ads=False,
                include_catalogs=False,
                include_user_account=False,
                include_business_access=True,
                business_id=None,
                include_resources=False,
                include_conversions=False,
                export_limit=50000,
                export_page_size=100,
                boards_limit=100000,
                pins_limit=1000000,
                page_size=100,
                skip_analytics=True,
            )
            ctx = {
                "cfg": Config(
                    base_url="https://api.pinterest.com/v5",
                    access_token=None,
                    app_id=None,
                    app_secret=None,
                    refresh_token=None,
                    timeout_s=30,
                ),
                "http": http,
                "env_file": str(env_file),
                "out": Output(mode="json"),
                "audit": _Audit(),
            }

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_audit_snapshot(args, ctx)
            self.assertEqual(rc, 0)

            payload = json.loads(buf.getvalue())
            warnings = payload.get("warnings") or []
            self.assertTrue(any(w.get("stage") == "business_access" for w in warnings))

    def test_snapshot_include_user_account_resources_and_conversions_writes_files(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            tool_dir = Path(d) / "tool"
            tool_dir.mkdir()
            env_file = tool_dir / ".env"
            env_file.write_text("PINTEREST_API_BASE_URL=https://api.pinterest.com/v5\n", encoding="utf-8")

            token_dir = tool_dir / ".state"
            token_dir.mkdir()
            (token_dir / "token.json").write_text(json.dumps({"access_token": "X"}), encoding="utf-8")

            out_dir = Path(d) / "out"

            http = _FakeHttp(
                [
                    {"items": [{"id": "b1"}], "bookmark": None},  # /boards
                    {"items": [], "bookmark": None},  # /boards/b1/sections
                    {"items": [{"id": "p1"}], "bookmark": None},  # /pins
                    {"items": [{"id": "biz1"}], "bookmark": None},  # /user_account/businesses
                    {"items": [{"id": "f1"}], "bookmark": None},  # /user_account/followers
                    {"items": [{"id": "fo1"}], "bookmark": None},  # /user_account/following
                    {"items": [{"id": "fb1"}], "bookmark": None},  # /user_account/following/boards
                    {"items": [{"id": "w1"}], "bookmark": None},  # /user_account/websites
                    {"verification": []},  # /user_account/websites/verification
                    {"countries": []},  # /resources/ad_account_countries
                    {"delivery_metrics": []},  # /resources/delivery_metrics
                    {"ready_state": {}},  # /resources/metrics_ready_state
                    {"items": [{"id": "t1"}], "bookmark": None},  # /ad_accounts/{id}/conversion_tags
                    {"page_visit": {}},  # /ad_accounts/{id}/conversion_tags/page_visit
                    {"ocpm": {}},  # /ad_accounts/{id}/conversion_tags/ocpm_eligible
                    {"eqs": {}},  # /ad_accounts/{id}/conversion_eqs
                ]
            )

            args = SimpleNamespace(
                out_dir=str(out_dir),
                ad_account_id="123",
                include_ads=False,
                include_catalogs=False,
                include_user_account=True,
                include_business_access=False,
                business_id=None,
                include_resources=True,
                include_conversions=True,
                export_limit=50000,
                export_page_size=100,
                boards_limit=100000,
                pins_limit=1000000,
                page_size=100,
                skip_analytics=True,
            )
            ctx = {
                "cfg": Config(
                    base_url="https://api.pinterest.com/v5",
                    access_token=None,
                    app_id=None,
                    app_secret=None,
                    refresh_token=None,
                    timeout_s=30,
                ),
                "http": http,
                "env_file": str(env_file),
                "out": Output(mode="json"),
                "audit": _Audit(),
            }

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_audit_snapshot(args, ctx)
            self.assertEqual(rc, 0)

            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            files = payload.get("files") or {}
            for key in [
                "user_account_businesses",
                "user_account_followers",
                "user_account_following",
                "user_account_following_boards",
                "user_account_websites",
                "user_account_websites_verification",
                "resources_ad_account_countries",
                "resources_delivery_metrics",
                "resources_metrics_ready_state",
                "conversions_tags",
                "conversions_page_visit",
                "conversions_ocpm_eligible",
                "conversions_eqs",
            ]:
                self.assertIn(key, files)
                self.assertTrue(Path(files[key]).exists())

            self.assertTrue((out_dir / "user_account" / "businesses.json").exists())
            self.assertTrue((out_dir / "resources" / "ad_account_countries.json").exists())
            self.assertTrue((out_dir / "conversions" / "tags.json").exists())
