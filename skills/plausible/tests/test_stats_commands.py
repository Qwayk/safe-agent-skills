from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from plausible_api_tool.commands.stats import cmd_stats_compare, cmd_stats_query, cmd_stats_validate
from plausible_api_tool.commands.stats import cmd_stats_goals_breakdown, cmd_stats_goals_list
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
