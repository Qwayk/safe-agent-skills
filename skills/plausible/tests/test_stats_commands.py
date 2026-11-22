from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import requests

from plausible_api_tool.cli import main
from plausible_api_tool.commands.stats import (
    cmd_stats_compare,
    cmd_stats_goals_breakdown,
    cmd_stats_goals_list,
    cmd_stats_query,
    cmd_stats_validate,
)
from plausible_api_tool.http import HttpResponse
from plausible_api_tool.output import Output


class _Audit:
    def write(self, *_args, **_kwargs) -> None:
        return


class TestStatsCommands(unittest.TestCase):
    def test_query_requires_exactly_one_source(self) -> None:
        args = SimpleNamespace(file=None, query=None, stdin=False)
        ctx = {"cfg": SimpleNamespace(site_id="example.com"), "http": None, "out": Output(mode="json"), "audit": _Audit()}
        with self.assertRaisesRegex(RuntimeError, "exactly one"):
            cmd_stats_query(args, ctx)

    def test_query_adds_default_site_id(self) -> None:
        args = SimpleNamespace(file=None, query='{"metrics":["visitors"],"date_range":"7d"}', stdin=False)
        ctx = {"cfg": SimpleNamespace(site_id="example.com"), "http": None, "out": Output(mode="json"), "audit": _Audit()}

        captured: dict[str, object] = {}

        def fake_stats_query(_self, query):
            captured["query"] = query
            return {"ok": True}

        with patch("plausible_api_tool.commands.stats.PlausibleClient.stats_query", new=fake_stats_query):
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_stats_query(args, ctx)
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertEqual(captured["query"]["site_id"], "example.com")

    def test_query_file_loads(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "q.json"
            p.write_text('{"metrics":["visitors"],"date_range":"7d"}\n', encoding="utf-8")
            args = SimpleNamespace(file=str(p), query=None, stdin=False)
            ctx = {"cfg": SimpleNamespace(site_id="example.com"), "http": None, "out": Output(mode="json"), "audit": _Audit()}

            with patch("plausible_api_tool.commands.stats.PlausibleClient.stats_query", return_value={"ok": True}):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cmd_stats_query(args, ctx)
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])

    def test_goals_list_uses_pagination(self) -> None:
        args = SimpleNamespace(date_range="7d", limit=5, offset=0, all=False)
        ctx = {"cfg": SimpleNamespace(site_id="example.com"), "http": None, "out": Output(mode="json"), "audit": _Audit()}

        captured = {}

        def fake_stats_query(_self, query):
            captured["query"] = query
            return {"results": []}

        with patch("plausible_api_tool.commands.stats.PlausibleClient.stats_query", new=fake_stats_query):
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_stats_goals_list(args, ctx)
        self.assertEqual(rc, 0)
        self.assertIn("pagination", captured["query"])
        self.assertNotIn("limit", captured["query"])
        self.assertEqual(captured["query"]["pagination"]["limit"], 5)

    def test_goals_breakdown_uses_pagination(self) -> None:
        args = SimpleNamespace(goal="x", prop="placement", date_range="7d", limit=5, offset=0, all=False)
        ctx = {"cfg": SimpleNamespace(site_id="example.com"), "http": None, "out": Output(mode="json"), "audit": _Audit()}

        captured = {}

        def fake_stats_query(_self, query):
            captured["query"] = query
            return {"results": []}

        with patch("plausible_api_tool.commands.stats.PlausibleClient.stats_query", new=fake_stats_query):
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_stats_goals_breakdown(args, ctx)
        self.assertEqual(rc, 0)
        self.assertIn("pagination", captured["query"])
        self.assertNotIn("limit", captured["query"])
        self.assertEqual(captured["query"]["pagination"]["limit"], 5)

    def test_validate_rejects_top_level_limit(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "q.json"
            p.write_text('{"site_id":"x","date_range":"7d","metrics":["visitors"],"limit":10}\n', encoding="utf-8")
            args = SimpleNamespace(file=str(p))
            ctx = {"out": Output(mode="json")}
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_stats_validate(args, ctx)
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])

    def test_compare_builds_two_queries(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "base.json"
            p.write_text('{"site_id":"example.com","date_range":"7d","metrics":["visitors"]}\n', encoding="utf-8")
            args = SimpleNamespace(file=str(p), range="7d", compare="previous")
            ctx = {"cfg": SimpleNamespace(site_id="example.com"), "http": None, "out": Output(mode="json"), "audit": _Audit()}

            def fake_stats_query(_self, query):
                # Return shape compatible with indexing.
                assert "date_range" in query
                return {"results": [{"dimensions": [], "metrics": [1]}], "meta": {}}

            with patch("plausible_api_tool.commands.stats.PlausibleClient.stats_query", new=fake_stats_query):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cmd_stats_compare(args, ctx)
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])

class TestStatsCLI(unittest.TestCase):
    def setUp(self) -> None:
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.root = Path(folder.name)
        self.env_file = self.root / "site settings.env"
        self.env_file.write_text(
            "PLAUSIBLE_BASE_URL=https://plausible.example.invalid\n"
            "PLAUSIBLE_SITE_ID=example.invalid\n"
            "PLAUSIBLE_API_KEY=fake-analytics-key\n"
            "CF_ACCESS_CLIENT_ID=fake-cloudflare-id\n"
            "CF_ACCESS_CLIENT_SECRET=fake-cloudflare-secret\n",
            encoding="utf-8",
        )

    def run_cli(self, *args):
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = main(["--output", "json", "--env-file", str(self.env_file), *args])
        return code, json.loads(stdout.getvalue()), stderr.getvalue()

    def test_validate_works_before_creating_settings(self) -> None:
        self.env_file.unlink()
        query = self.root / "query.json"
        query.write_text('{"site_id":"example.invalid","date_range":"7d","metrics":["visitors"]}')
        with patch("requests.Session.request") as request:
            code, payload, _ = self.run_cli("stats", "validate", "--file", str(query))
        self.assertEqual(code, 0)
        self.assertTrue(payload["valid"])
        request.assert_not_called()

    def test_auth_and_stats_reject_an_unexpected_success_reply(self) -> None:
        fake = HttpResponse(200, {}, b'{"error":"unexpected reply"}', "https://plausible.example.invalid")
        with patch("plausible_api_tool.http.HttpClient.request", return_value=fake):
            code, payload, _ = self.run_cli("auth", "check")
            self.assertEqual(code, 1)
            self.assertFalse(payload["ok"])
            code, payload, _ = self.run_cli(
                "stats", "query", "--query", '{"metrics":["visitors"],"date_range":"7d"}'
            )
            self.assertEqual(code, 1)
            self.assertFalse(payload["ok"])

    def test_page_offsets_follow_rows_received_and_report_early_end(self) -> None:
        offsets = []

        def reply(method, url, *, json_body, **kwargs):
            self.assertEqual(method, "POST")
            self.assertEqual(json_body["date_range"], "7d")
            self.assertTrue(json_body["include"]["total_rows"])
            offset = json_body["pagination"]["offset"]
            offsets.append(offset)
            rows = [{"dimensions": ["/first"], "metrics": [2, 1]}] if offset == 0 else []
            body = {"results": rows, "meta": {"total_rows": 5}}
            return HttpResponse(200, {}, json.dumps(body).encode(), url)

        with patch("plausible_api_tool.http.HttpClient.request", side_effect=reply):
            args = ("stats", "pages", "top", "--date-range", "7d", "--limit", "2")
            code, page, _ = self.run_cli(*args)
            self.assertEqual(code, 0)
            self.assertFalse(page["pagination"]["complete"])
            self.assertEqual(page["pagination"]["next_offset"], 1)
            self.assertEqual(offsets, [0])
            offsets.clear()

            code, partial, _ = self.run_cli(*args, "--all")
        self.assertEqual(code, 1)
        self.assertEqual(offsets, [0, 1])
        self.assertEqual(partial["pagination"]["rows"], 1)
        self.assertFalse(partial["pagination"]["complete"])
        self.assertEqual(partial["pagination"]["next_offset"], 1)

    def test_all_pages_completes_with_or_without_the_reported_total(self) -> None:
        for total in (3, None):
            with self.subTest(total=total):
                offsets = []

                def reply(method, url, *, json_body, total=total, offsets=offsets, **kwargs):
                    offset = json_body["pagination"]["offset"]
                    offsets.append(offset)
                    rows = [
                        {"dimensions": [str(i)], "metrics": [1, 1]}
                        for i in range(offset, min(offset + 2, 3))
                    ]
                    body = {"results": rows, "meta": {} if total is None else {"total_rows": total}}
                    return HttpResponse(200, {}, json.dumps(body).encode(), url)

                with patch("plausible_api_tool.http.HttpClient.request", side_effect=reply):
                    code, payload, _ = self.run_cli("stats", "pages", "top", "--limit", "2", "--all")
                self.assertEqual(code, 0)
                self.assertEqual(offsets, [0, 2])
                self.assertEqual(len(payload["response"]["results"]), 3)
                self.assertTrue(payload["pagination"]["complete"])
                self.assertIsNone(payload["pagination"]["next_offset"])

    def test_weekly_report_skips_membership_and_marks_limited_sections(self) -> None:
        queries = []

        def reply(method, url, *, json_body, **kwargs):
            queries.append(json_body)
            body = {"results": [{"dimensions": ["one"], "metrics": [2, 1]}], "meta": {"total_rows": 3}}
            return HttpResponse(200, {}, json.dumps(body).encode(), url)

        with patch("plausible_api_tool.http.HttpClient.request", side_effect=reply):
            code, payload, _ = self.run_cli("report", "weekly", "--limit", "1")
        self.assertEqual(code, 0)
        self.assertEqual(len(queries), 3)
        self.assertNotIn("membership_funnels", payload["reports"])
        self.assertFalse(payload["reports"]["top_pages"]["pagination"]["complete"])

    def test_membership_report_keeps_missing_goals_separate_from_zero(self) -> None:
        def reply(method, url, *, json_body, **kwargs):
            filters = json_body.get("filters", [])
            if filters and filters[0][2][0] == "members_modal_shown_manual":
                raise RuntimeError("The goal `members_modal_shown_manual` is not configured for this site")
            return HttpResponse(200, {}, b'{"results":[]}', url)

        with patch("plausible_api_tool.http.HttpClient.request", side_effect=reply):
            code, payload, _ = self.run_cli("report", "membership", "--out-dir", str(self.root))
        self.assertEqual(code, 0)
        reports = payload["reports"]
        funnels = reports["membership_funnels"]
        self.assertIsNone(funnels["popup_manual"]["steps"][0]["events"])
        self.assertEqual(funnels["popup_auto"]["steps"][0]["events"], 0)
        self.assertIsNone(funnels["popup_manual"]["drop_off"][0]["drop_events"])
        self.assertIsNone(reports["members_modal_shown_manual_by_placement"]["response"])
        self.assertEqual(len(payload["csv_files"]), 1)

    def test_http_errors_hide_keys_in_output_and_audit(self) -> None:
        log_path = self.root / "audit.jsonl"
        secrets = ("fake-analytics-key", "fake-cloudflare-id", "fake-cloudflare-secret")

        def denied(**kwargs):
            response = requests.Response()
            response.status_code = 403
            response.url = kwargs["url"] + "?token=" + secrets[0]
            response._content = ("access denied " + " ".join(secrets)).encode()
            return response

        with patch("requests.Session.request", side_effect=denied):
            code, payload, stderr = self.run_cli(
                "--verbose", "--log-file", str(log_path), "stats", "query",
                "--query", '{"metrics":["visitors"],"date_range":"7d"}',
            )
        self.assertEqual(code, 1)
        combined = json.dumps(payload) + stderr + log_path.read_text()
        self.assertIn("403", combined)
        self.assertIn("***REDACTED***", combined)
        for secret in secrets:
            self.assertNotIn(secret, combined)

    def test_site_update_checks_the_requested_values(self) -> None:
        def reply(method, url, *, json_body=None, **kwargs):
            body = {
                "domain": "example.invalid",
                "tracker_script_configuration": {"outbound_links": method == "PUT", "file_downloads": False},
            }
            return HttpResponse(200, {}, json.dumps(body).encode(), url)

        receipt_path = self.root / "receipt.json"
        with patch("plausible_api_tool.http.HttpClient.request", side_effect=reply):
            code, payload, _ = self.run_cli(
                "--apply", "--yes", "--receipt-out", str(receipt_path), "site", "update",
                "--tracker-config", '{"outbound_links":true,"file_downloads":false}',
            )
        self.assertEqual(code, 0)
        self.assertFalse(payload["verified"])
        receipt = json.loads(receipt_path.read_text())
        self.assertFalse(receipt["verification"]["fields"]["tracker_script_configuration.outbound_links"]["confirmed"])
        self.assertTrue(receipt["verification"]["fields"]["tracker_script_configuration.file_downloads"]["confirmed"])
