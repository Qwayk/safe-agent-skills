from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import dataclass
from typing import Any
from unittest.mock import patch

import requests

from instantly_api_tool.cli import main


@dataclass
class _FakeResponse:
    status_code: int
    url: str
    headers: dict[str, str]
    content: bytes
    _text: str

    @property
    def text(self) -> str:  # requests.Response compatible
        return self._text


def _json_response(*, url: str, status: int, obj: Any) -> _FakeResponse:
    text = json.dumps(obj, ensure_ascii=False)
    return _FakeResponse(
        status_code=status,
        url=url,
        headers={"content-type": "application/json"},
        content=text.encode("utf-8"),
        _text=text,
    )


def _write_env(td: str) -> str:
    env_path = os.path.join(td, ".env")
    with open(env_path, "w", encoding="utf-8") as f:
        f.write("INSTANTLY_API_BASE_URL=https://api.instantly.ai/api/v2\n")
        f.write("INSTANTLY_API_KEY=test_api_key\n")
    return env_path


def _run_json(argv: list[str]) -> tuple[int, dict[str, Any]]:
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = main(argv)
    payload = json.loads(buf.getvalue())
    return rc, payload


def _run_json_with_stderr(argv: list[str]) -> tuple[int, dict[str, Any], str]:
    out_buf = io.StringIO()
    err_buf = io.StringIO()
    with redirect_stdout(out_buf), redirect_stderr(err_buf):
        rc = main(argv)
    payload = json.loads(out_buf.getvalue())
    return rc, payload, err_buf.getvalue()


def _run_stdout(argv: list[str]) -> tuple[int, str]:
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = main(argv)
    return rc, buf.getvalue()


def _write_plan(td: str, name: str, plan: dict[str, Any]) -> str:
    path = os.path.join(td, name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(plan, f)
    return path


class TestInstantlyCommands(unittest.TestCase):
    def test_analytics_accounts_daily_wires_query_params(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            return _json_response(url=url, status=200, obj={"items": []})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            rc, payload = _run_json(
                [
                    "--output",
                    "json",
                    "--env-file",
                    env,
                    "analytics",
                    "accounts-daily",
                    "--emails",
                    "a@example.com,b@example.com",
                    "--start-date",
                    "2024-01-01",
                    "--end-date",
                    "2024-01-31",
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0]["method"], "GET")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/accounts/analytics/daily"))
            self.assertEqual(calls[0]["kwargs"]["params"]["emails"], "a@example.com,b@example.com")
            self.assertEqual(calls[0]["kwargs"]["params"]["start_date"], "2024-01-01")
            self.assertEqual(calls[0]["kwargs"]["params"]["end_date"], "2024-01-31")

    def test_analytics_campaigns_optional_bool_query_params_only_sent_when_true(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            return _json_response(url=url, status=200, obj={"items": []})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)

            rc, payload = _run_json(
                [
                    "--output",
                    "json",
                    "--env-file",
                    env,
                    "analytics",
                    "campaigns",
                    "--start-date",
                    "2024-01-01",
                    "--end-date",
                    "2024-01-31",
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0]["method"], "GET")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/campaigns/analytics"))
            self.assertNotIn("exclude_total_leads_count", calls[0]["kwargs"]["params"])

            rc, payload = _run_json(
                [
                    "--output",
                    "json",
                    "--env-file",
                    env,
                    "analytics",
                    "campaigns",
                    "--start-date",
                    "2024-01-01",
                    "--end-date",
                    "2024-01-31",
                    "--exclude-total-leads-count",
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(len(calls), 2)
            self.assertTrue(calls[1]["kwargs"]["params"]["exclude_total_leads_count"])

    def test_campaigns_list_wires_pagination_and_next_cursor(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            return _json_response(url=url, status=200, obj={"items": [], "next_starting_after": "NEXT"})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            rc, payload = _run_json(
                [
                    "--output",
                    "json",
                    "--env-file",
                    env,
                    "campaigns",
                    "list",
                    "--limit",
                    "10",
                    "--starting-after",
                    "CUR",
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["next_starting_after"], "NEXT")
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0]["method"], "GET")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/campaigns"))
            self.assertEqual(calls[0]["kwargs"]["params"]["limit"], 10)
            self.assertEqual(calls[0]["kwargs"]["params"]["starting_after"], "CUR")

    def test_campaigns_search_by_contact_wires_query_params(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            return _json_response(url=url, status=200, obj={"items": []})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            rc, payload = _run_json(["--output", "json", "--env-file", env, "campaigns", "search-by-contact", "--email", "a@example.com"])
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0]["method"], "GET")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/campaigns/search-by-contact"))
            self.assertEqual(calls[0]["kwargs"]["params"]["search"], "a@example.com")

    def test_campaigns_delete_refuses_without_plan_in_on_apply(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env = _write_env(td)
            rc, payload = _run_json(
                [
                    "--output",
                    "json",
                    "--env-file",
                    env,
                    "--apply",
                    "--yes",
                    "campaigns",
                    "delete",
                    "--campaign-id",
                    "C1",
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertIn("plan-in", " ".join(payload.get("reasons") or []))

    def test_accounts_list_wires_pagination_and_next_cursor(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            return _json_response(url=url, status=200, obj={"items": [], "next_starting_after": "NEXT"})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            rc, payload = _run_json(
                [
                    "--output",
                    "json",
                    "--env-file",
                    env,
                    "--apply",
                    "--yes",
                    "accounts",
                    "list",
                    "--limit",
                    "10",
                    "--starting-after",
                    "CUR",
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertFalse(payload["dry_run"])
            self.assertIn("receipt_out", payload)
            self.assertNotIn("accounts", payload)
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0]["method"], "GET")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/accounts"))
            self.assertEqual(calls[0]["kwargs"]["params"]["limit"], 10)
            self.assertEqual(calls[0]["kwargs"]["params"]["starting_after"], "CUR")
            receipt_path = payload["receipt_out"]
            self.assertTrue(receipt_path and os.path.exists(receipt_path))
            with open(receipt_path, "r", encoding="utf-8") as f:
                receipt = json.load(f)
            self.assertEqual(receipt["result"]["next_starting_after"], "NEXT")

    def test_accounts_list_dry_run_does_not_call_http(self) -> None:
        called = False

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            nonlocal called
            called = True
            return _json_response(url=url, status=200, obj={"items": [], "next_starting_after": None})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            rc, payload = _run_json(
                ["--output", "json", "--env-file", env, "accounts", "list", "--limit", "10", "--starting-after", "CUR"]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertFalse(called)
            plan_out = payload.get("plan_out")
            self.assertTrue(plan_out and os.path.exists(plan_out))

    def test_lead_lists_list_wires_pagination_and_next_cursor(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            return _json_response(url=url, status=200, obj={"items": [], "next_starting_after": "NEXT"})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            rc, payload = _run_json(
                [
                    "--output",
                    "json",
                    "--env-file",
                    env,
                    "lead-lists",
                    "list",
                    "--limit",
                    "10",
                    "--starting-after",
                    "CUR",
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["next_starting_after"], "NEXT")
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0]["method"], "GET")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/lead-lists"))
            self.assertEqual(calls[0]["kwargs"]["params"]["limit"], 10)
            self.assertEqual(calls[0]["kwargs"]["params"]["starting_after"], "CUR")

    def test_lead_lists_verification_stats_endpoint(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            return _json_response(url=url, status=200, obj={"ok": True})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            rc, payload = _run_json(
                [
                    "--output",
                    "json",
                    "--env-file",
                    env,
                    "lead-lists",
                    "verification-stats",
                    "--lead-list-id",
                    "LL1",
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0]["method"], "GET")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/lead-lists/LL1/verification-stats"))

    def test_lead_labels_list_wires_pagination_and_next_cursor(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            return _json_response(url=url, status=200, obj={"items": [], "next_starting_after": "NEXT"})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            rc, payload = _run_json(
                [
                    "--output",
                    "json",
                    "--env-file",
                    env,
                    "lead-labels",
                    "list",
                    "--limit",
                    "10",
                    "--starting-after",
                    "CUR",
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["next_starting_after"], "NEXT")
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0]["method"], "GET")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/lead-labels"))
            self.assertEqual(calls[0]["kwargs"]["params"]["limit"], 10)
            self.assertEqual(calls[0]["kwargs"]["params"]["starting_after"], "CUR")

    def test_custom_tags_list_wires_pagination_and_next_cursor(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            return _json_response(url=url, status=200, obj={"items": [], "next_starting_after": "NEXT"})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            rc, payload = _run_json(
                [
                    "--output",
                    "json",
                    "--env-file",
                    env,
                    "custom-tags",
                    "list",
                    "--limit",
                    "10",
                    "--starting-after",
                    "CUR",
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["next_starting_after"], "NEXT")
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0]["method"], "GET")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/custom-tags"))
            self.assertEqual(calls[0]["kwargs"]["params"]["limit"], 10)
            self.assertEqual(calls[0]["kwargs"]["params"]["starting_after"], "CUR")

    def test_custom_tag_mappings_list_wires_pagination_and_next_cursor(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            return _json_response(url=url, status=200, obj={"items": [], "next_starting_after": "NEXT"})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            rc, payload = _run_json(
                [
                    "--output",
                    "json",
                    "--env-file",
                    env,
                    "custom-tag-mappings",
                    "list",
                    "--limit",
                    "10",
                    "--starting-after",
                    "CUR",
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["next_starting_after"], "NEXT")
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0]["method"], "GET")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/custom-tag-mappings"))
            self.assertEqual(calls[0]["kwargs"]["params"]["limit"], 10)
            self.assertEqual(calls[0]["kwargs"]["params"]["starting_after"], "CUR")

    def test_account_campaign_mappings_get_wires_path(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            return _json_response(url=url, status=200, obj={"ok": True})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            rc, payload = _run_json(
                [
                    "--output",
                    "json",
                    "--env-file",
                    env,
                    "account-campaign-mappings",
                    "get",
                    "--email",
                    "a@example.com",
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0]["method"], "GET")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/account-campaign-mappings/a@example.com"))

    def test_subsequences_list_wires_pagination_and_next_cursor(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            return _json_response(url=url, status=200, obj={"items": [], "next_starting_after": "NEXT"})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            rc, payload = _run_json(
                [
                    "--output",
                    "json",
                    "--env-file",
                    env,
                    "subsequences",
                    "list",
                    "--limit",
                    "10",
                    "--starting-after",
                    "CUR",
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["next_starting_after"], "NEXT")
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0]["method"], "GET")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/subsequences"))
            self.assertEqual(calls[0]["kwargs"]["params"]["limit"], 10)
            self.assertEqual(calls[0]["kwargs"]["params"]["starting_after"], "CUR")

    def test_subsequences_sending_status_wires_with_ai_summary(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            return _json_response(url=url, status=200, obj={"ok": True})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            rc, payload = _run_json(
                [
                    "--output",
                    "json",
                    "--env-file",
                    env,
                    "subsequences",
                    "sending-status",
                    "--subsequence-id",
                    "S1",
                    "--with-ai-summary",
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0]["method"], "GET")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/subsequences/S1/sending-status"))
            self.assertTrue(calls[0]["kwargs"]["params"]["with_ai_summary"])

    def test_campaigns_create_dry_run_does_not_call_http(self) -> None:
        called = False

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            nonlocal called
            called = True
            return _json_response(url=url, status=200, obj={"ok": True})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            campaign_json = os.path.join(td, "campaign.json")
            with open(campaign_json, "w", encoding="utf-8") as f:
                json.dump({"name": "Test"}, f)
            rc, payload = _run_json(
                ["--output", "json", "--env-file", env, "campaigns", "create", "--file", campaign_json]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertFalse(called)
            plan_out = payload.get("plan_out")
            self.assertTrue(plan_out and os.path.exists(plan_out))

    def test_subsequences_create_dry_run_does_not_call_http(self) -> None:
        called = False

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            nonlocal called
            called = True
            return _json_response(url=url, status=200, obj={"ok": True})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            subseq_json = os.path.join(td, "subsequence.json")
            with open(subseq_json, "w", encoding="utf-8") as f:
                json.dump({"name": "S1"}, f)
            rc, payload = _run_json(
                ["--output", "json", "--env-file", env, "subsequences", "create", "--file", subseq_json]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertFalse(called)
            plan_out = payload.get("plan_out")
            self.assertTrue(plan_out and os.path.exists(plan_out))

    def test_accounts_create_dry_run_does_not_call_http(self) -> None:
        called = False

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            nonlocal called
            called = True
            return _json_response(url=url, status=200, obj={"ok": True})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            account_json = os.path.join(td, "account.json")
            with open(account_json, "w", encoding="utf-8") as f:
                json.dump({"email": "user@example.com", "password": "super_secret"}, f)
            rc, payload = _run_json(["--output", "json", "--env-file", env, "accounts", "create", "--file", account_json])
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertFalse(called)
            plan_out = payload.get("plan_out")
            self.assertTrue(plan_out and os.path.exists(plan_out))

    def test_accounts_mark_fixed_endpoint(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            if method == "POST":
                return _json_response(url=url, status=200, obj={"ok": True})
            return _json_response(url=url, status=200, obj={"email": "a@example.com"})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            rc, payload = _run_json(["--output", "json", "--env-file", env, "--apply", "accounts", "mark-fixed", "--email", "a@example.com"])
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(len(calls), 3)
            self.assertEqual(calls[0]["method"], "GET")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/accounts/a@example.com"))
            self.assertEqual(calls[1]["method"], "POST")
            self.assertTrue(calls[1]["url"].endswith("/api/v2/accounts/a@example.com/mark-fixed"))
            self.assertIn("before_state", payload)

    def test_accounts_move_requires_yes_on_apply(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env = _write_env(td)
            move_json = os.path.join(td, "move.json")
            with open(move_json, "w", encoding="utf-8") as f:
                json.dump({"emails": ["a@example.com"], "to_group_id": "G1"}, f)
            rc, payload = _run_json(["--output", "json", "--env-file", env, "--apply", "accounts", "move", "--file", move_json])
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])

    def test_accounts_delete_refuses_without_yes_and_requires_plan_in_on_apply(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env = _write_env(td)
            rc, payload = _run_json(
                ["--output", "json", "--env-file", env, "--apply", "accounts", "delete", "--email", "a@example.com"]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])

            rc2, payload2 = _run_json(
                [
                    "--output",
                    "json",
                    "--env-file",
                    env,
                    "--apply",
                    "--yes",
                    "accounts",
                    "delete",
                    "--email",
                    "a@example.com",
                ]
            )
            self.assertEqual(rc2, 0)
            self.assertTrue(payload2["ok"])
            self.assertTrue(payload2["refused"])

    def test_subsequences_delete_refuses_without_yes_and_requires_plan_in_on_apply(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env = _write_env(td)
            rc, payload = _run_json(
                [
                    "--output",
                    "json",
                    "--env-file",
                    env,
                    "--apply",
                    "subsequences",
                    "delete",
                    "--subsequence-id",
                    "S1",
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])

            rc2, payload2 = _run_json(
                [
                    "--output",
                    "json",
                    "--env-file",
                    env,
                    "--apply",
                    "--yes",
                    "subsequences",
                    "delete",
                    "--subsequence-id",
                    "S1",
                ]
            )
            self.assertEqual(rc2, 0)
            self.assertTrue(payload2["ok"])
            self.assertTrue(payload2["refused"])

    def test_custom_tags_toggle_resource_refuses_without_yes_on_apply(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env = _write_env(td)
            toggle_json = os.path.join(td, "toggle.json")
            with open(toggle_json, "w", encoding="utf-8") as f:
                json.dump({"resource_type": "lead", "resource_id": "L1", "tag_id": "T1"}, f)
            rc, payload = _run_json(
                [
                    "--output",
                    "json",
                    "--env-file",
                    env,
                    "--apply",
                    "custom-tags",
                    "toggle-resource",
                    "--file",
                    toggle_json,
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])

    def test_leads_add_bulk_refuses_without_yes_on_apply(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env = _write_env(td)
            leads_json = os.path.join(td, "leads.json")
            with open(leads_json, "w", encoding="utf-8") as f:
                json.dump([{"email": "a@example.com"}], f)
            rc, payload = _run_json(
                [
                    "--output",
                    "json",
                    "--env-file",
                    env,
                    "--apply",
                    "leads",
                    "add-bulk",
                    "--campaign-id",
                    "C1",
                    "--json",
                    leads_json,
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])

    def test_leads_bulk_delete_refuses_without_plan_in_on_apply(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env = _write_env(td)
            bulk_json = os.path.join(td, "bulk_delete.json")
            with open(bulk_json, "w", encoding="utf-8") as f:
                json.dump({"lead_ids": ["L1"]}, f)
            rc, payload = _run_json(
                [
                    "--output",
                    "json",
                    "--env-file",
                    env,
                    "--apply",
                    "--yes",
                    "leads",
                    "bulk-delete",
                    "--file",
                    bulk_json,
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertIn("plan-in", " ".join(payload.get("reasons") or []))

    def test_supersearch_enrichment_create_requires_yes_on_apply(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env = _write_env(td)
            create_json = os.path.join(td, "create_enrichment.json")
            with open(create_json, "w", encoding="utf-8") as f:
                json.dump({"resource_id": "R1"}, f)
            rc, payload = _run_json(
                ["--output", "json", "--env-file", env, "--apply", "supersearch-enrichment", "create", "--file", create_json]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])

    def test_supersearch_enrichment_count_leads_endpoint(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            return _json_response(url=url, status=200, obj={"count": 3})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            count_json = os.path.join(td, "count.json")
            with open(count_json, "w", encoding="utf-8") as f:
                json.dump({"search": "example"}, f)
            rc, payload = _run_json(
                ["--output", "json", "--env-file", env, "supersearch-enrichment", "count-leads", "--file", count_json]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0]["method"], "POST")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/supersearch-enrichment/count-leads-from-supersearch"))

    def test_phase5_campaigns_patch_wires_method_and_path(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            return _json_response(url=url, status=200, obj={"ok": True})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            patch_json = os.path.join(td, "campaign_patch.json")
            with open(patch_json, "w", encoding="utf-8") as f:
                json.dump({"name": "Updated"}, f)

            rc, payload = _run_json(
                ["--output", "json", "--env-file", env, "campaigns", "patch", "--campaign-id", "C1", "--file", patch_json]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertEqual(len(calls), 0)

            rc2, payload2 = _run_json(
                ["--output", "json", "--env-file", env, "--apply", "campaigns", "patch", "--campaign-id", "C1", "--file", patch_json]
            )
            self.assertEqual(rc2, 0)
            self.assertTrue(payload2["ok"])
            self.assertFalse(payload2["dry_run"])
            self.assertGreaterEqual(len(calls), 1)
            self.assertEqual(calls[0]["method"], "GET")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/campaigns/C1"))
            self.assertEqual(calls[1]["method"], "PATCH")
            self.assertTrue(calls[1]["url"].endswith("/api/v2/campaigns/C1"))
            self.assertIn("before_state", payload2)

    def test_phase5_campaigns_sending_status_wires_method_and_path(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            return _json_response(url=url, status=200, obj={"status": "ok"})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            rc, payload = _run_json(
                ["--output", "json", "--env-file", env, "campaigns", "sending-status", "--campaign-id", "C1"]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0]["method"], "GET")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/campaigns/C1/sending-status"))

    def test_phase5_campaigns_share_requires_yes_and_wires_path_on_apply(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            return _json_response(url=url, status=200, obj={"ok": True})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            rc, payload = _run_json(["--output", "json", "--env-file", env, "--apply", "campaigns", "share", "--campaign-id", "C1"])
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])

            calls.clear()
            rc2, payload2 = _run_json(
                ["--output", "json", "--env-file", env, "--apply", "--yes", "campaigns", "share", "--campaign-id", "C1"]
            )
            self.assertEqual(rc2, 0)
            self.assertTrue(payload2["ok"])
            self.assertFalse(payload2["dry_run"])
            self.assertGreaterEqual(len(calls), 1)
            self.assertEqual(calls[0]["method"], "GET")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/campaigns/C1"))
            self.assertEqual(calls[1]["method"], "POST")
            self.assertTrue(calls[1]["url"].endswith("/api/v2/campaigns/C1/share"))
            self.assertIn("before_state", payload2)

    def test_phase5_campaigns_create_from_export_requires_yes_and_wires_path_on_apply(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            if method == "POST":
                return _json_response(url=url, status=200, obj={"id": "NEW"})
            return _json_response(url=url, status=200, obj={"id": "NEW"})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            rc, payload = _run_json(
                ["--output", "json", "--env-file", env, "--apply", "campaigns", "create-from-export", "--campaign-id", "C1"]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])

            calls.clear()
            rc2, payload2 = _run_json(
                ["--output", "json", "--env-file", env, "--apply", "--yes", "campaigns", "create-from-export", "--campaign-id", "C1"]
            )
            self.assertEqual(rc2, 0)
            self.assertTrue(payload2["ok"])
            self.assertTrue(payload2["refused"])
            self.assertEqual(calls, [])

    def test_phase5_campaigns_export_wires_method_and_path(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            return _json_response(url=url, status=200, obj={"ok": True})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            rc, payload = _run_json(["--output", "json", "--env-file", env, "campaigns", "export", "--campaign-id", "C1"])
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertEqual(len(calls), 0)

            rc2, payload2 = _run_json(["--output", "json", "--env-file", env, "--apply", "campaigns", "export", "--campaign-id", "C1"])
            self.assertEqual(rc2, 0)
            self.assertTrue(payload2["ok"])
            self.assertFalse(payload2["dry_run"])
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0]["method"], "POST")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/campaigns/C1/export"))

    def test_phase5_campaigns_duplicate_requires_yes_and_wires_method_and_path_on_apply(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            if method == "POST":
                return _json_response(url=url, status=200, obj={"id": "NEW"})
            return _json_response(url=url, status=200, obj={"id": "NEW"})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            dup_json = os.path.join(td, "dup.json")
            with open(dup_json, "w", encoding="utf-8") as f:
                json.dump({"name": "Copy"}, f)

            rc, payload = _run_json(
                ["--output", "json", "--env-file", env, "--apply", "campaigns", "duplicate", "--campaign-id", "C1", "--file", dup_json]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])

            calls.clear()
            rc2, payload2 = _run_json(
                ["--output", "json", "--env-file", env, "--apply", "--yes", "campaigns", "duplicate", "--campaign-id", "C1", "--file", dup_json]
            )
            self.assertEqual(rc2, 0)
            self.assertTrue(payload2["ok"])
            self.assertTrue(payload2["refused"])
            self.assertEqual(calls, [])

    def test_phase5_campaigns_count_launched_wires_method_and_path(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            return _json_response(url=url, status=200, obj=7)

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            rc, payload = _run_json(["--output", "json", "--env-file", env, "campaigns", "count-launched"])
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["count"], 7)
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0]["method"], "GET")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/campaigns/count-launched"))

    def test_phase5_campaigns_add_variables_wires_method_and_path_on_apply(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            return _json_response(url=url, status=200, obj={"ok": True})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            vars_json = os.path.join(td, "vars.json")
            with open(vars_json, "w", encoding="utf-8") as f:
                json.dump({"variables": []}, f)
            rc, payload = _run_json(
                ["--output", "json", "--env-file", env, "campaigns", "add-variables", "--campaign-id", "C1", "--file", vars_json]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertEqual(len(calls), 0)

            rc2, payload2 = _run_json(
                ["--output", "json", "--env-file", env, "--apply", "campaigns", "add-variables", "--campaign-id", "C1", "--file", vars_json]
            )
            self.assertEqual(rc2, 0)
            self.assertTrue(payload2["ok"])
            self.assertFalse(payload2["dry_run"])
            self.assertGreaterEqual(len(calls), 1)
            self.assertEqual(calls[0]["method"], "GET")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/campaigns/C1"))
            self.assertEqual(calls[1]["method"], "POST")
            self.assertTrue(calls[1]["url"].endswith("/api/v2/campaigns/C1/variables"))
            self.assertIn("before_state", payload2)

    def test_phase5_accounts_move_requires_yes_and_wires_method_and_path_on_apply(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            return _json_response(url=url, status=200, obj={"ok": True})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            move_json = os.path.join(td, "move2.json")
            with open(move_json, "w", encoding="utf-8") as f:
                json.dump({"emails": ["a@example.com"], "to_group_id": "G1"}, f)

            rc, payload = _run_json(["--output", "json", "--env-file", env, "--apply", "accounts", "move", "--file", move_json])
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])

            calls.clear()
            rc2, payload2 = _run_json(
                ["--output", "json", "--env-file", env, "--apply", "--yes", "accounts", "move", "--file", move_json]
            )
            self.assertEqual(rc2, 0)
            self.assertTrue(payload2["ok"])
            self.assertFalse(payload2["dry_run"])
            self.assertEqual(len(calls), 2)
            self.assertEqual(calls[0]["method"], "GET")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/accounts/a@example.com"))
            self.assertEqual(calls[1]["method"], "POST")
            self.assertTrue(calls[1]["url"].endswith("/api/v2/accounts/move"))
            self.assertIn("before_state", payload2)

    def test_phase5_leads_create_wires_method_and_path(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            return _json_response(url=url, status=200, obj={"id": "L1"})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            lead_json = os.path.join(td, "lead.json")
            with open(lead_json, "w", encoding="utf-8") as f:
                json.dump({"email": "a@example.com"}, f)

            rc, payload = _run_json(["--output", "json", "--env-file", env, "leads", "create", "--file", lead_json])
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertEqual(len(calls), 0)

            rc2, payload2 = _run_json(["--output", "json", "--env-file", env, "--apply", "leads", "create", "--file", lead_json])
            self.assertEqual(rc2, 0)
            self.assertTrue(payload2["ok"])
            self.assertTrue(payload2["refused"])
            self.assertEqual(calls, [])

    def test_phase5_leads_patch_wires_method_and_path(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            return _json_response(url=url, status=200, obj={"ok": True})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            patch_json = os.path.join(td, "lead_patch.json")
            with open(patch_json, "w", encoding="utf-8") as f:
                json.dump({"first_name": "A"}, f)
            rc, payload = _run_json(["--output", "json", "--env-file", env, "leads", "patch", "--lead-id", "L1", "--file", patch_json])
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertEqual(len(calls), 0)

            rc2, payload2 = _run_json(
                ["--output", "json", "--env-file", env, "--apply", "leads", "patch", "--lead-id", "L1", "--file", patch_json]
            )
            self.assertEqual(rc2, 0)
            self.assertTrue(payload2["ok"])
            self.assertFalse(payload2["dry_run"])
            self.assertGreaterEqual(len(calls), 1)
            self.assertEqual(calls[0]["method"], "GET")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/leads/L1"))
            self.assertEqual(calls[1]["method"], "PATCH")
            self.assertTrue(calls[1]["url"].endswith("/api/v2/leads/L1"))
            self.assertIn("before_state", payload2)

    def test_phase5_leads_delete_requires_plan_in_and_wires_method_and_path_on_apply(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            return _json_response(url=url, status=200, obj={"ok": True})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            rc, payload = _run_json(
                ["--output", "json", "--env-file", env, "--apply", "--yes", "leads", "delete", "--lead-id", "L1"]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])

            rc2, payload2 = _run_json(["--output", "json", "--env-file", env, "leads", "delete", "--lead-id", "L1"])
            self.assertEqual(rc2, 0)
            self.assertTrue(payload2["ok"])
            self.assertTrue(payload2["dry_run"])
            plan = payload2["plan"]
            plan_path = _write_plan(td, "plan_leads_delete.json", plan)

            calls.clear()
            rc3, payload3 = _run_json(
                [
                    "--output",
                    "json",
                    "--env-file",
                    env,
                    "--apply",
                    "--yes",
                    "--plan-in",
                    plan_path,
                    "leads",
                    "delete",
                    "--lead-id",
                    "L1",
                ]
            )
            self.assertEqual(rc3, 0)
            self.assertTrue(payload3["ok"])
            self.assertFalse(payload3["dry_run"])
            self.assertGreaterEqual(len(calls), 1)
            self.assertEqual(calls[0]["method"], "GET")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/leads/L1"))
            self.assertEqual(calls[1]["method"], "DELETE")
            self.assertTrue(calls[1]["url"].endswith("/api/v2/leads/L1"))
            self.assertIn("before_state", payload3)

    def test_phase5_leads_bulk_delete_wires_method_and_path_on_apply(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            return _json_response(url=url, status=200, obj={"ok": True})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            bulk_json = os.path.join(td, "bulk_delete2.json")
            with open(bulk_json, "w", encoding="utf-8") as f:
                json.dump({"lead_ids": ["L1"]}, f)
            rc, payload = _run_json(["--output", "json", "--env-file", env, "leads", "bulk-delete", "--file", bulk_json])
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            plan = payload["plan"]
            plan_path = _write_plan(td, "plan_leads_bulk_delete.json", plan)

            calls.clear()
            rc2, payload2 = _run_json(
                ["--output", "json", "--env-file", env, "--apply", "--yes", "--plan-in", plan_path, "leads", "bulk-delete", "--file", bulk_json]
            )
            self.assertEqual(rc2, 0)
            self.assertTrue(payload2["ok"])
            self.assertFalse(payload2["dry_run"])
            self.assertEqual(len(calls), 2)
            self.assertEqual(calls[0]["method"], "GET")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/leads/L1"))
            self.assertEqual(calls[1]["method"], "DELETE")
            self.assertTrue(calls[1]["url"].endswith("/api/v2/leads"))
            self.assertIn("before_state", payload2)

    def test_phase5_leads_merge_wires_method_and_path_on_apply(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            return _json_response(url=url, status=200, obj={"ok": True})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            merge_json = os.path.join(td, "merge.json")
            with open(merge_json, "w", encoding="utf-8") as f:
                json.dump({"source_lead_id": "L1", "target_lead_id": "L2"}, f)
            rc, payload = _run_json(["--output", "json", "--env-file", env, "leads", "merge", "--file", merge_json])
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            plan = payload["plan"]
            plan_path = _write_plan(td, "plan_leads_merge.json", plan)

            calls.clear()
            rc2, payload2 = _run_json(
                ["--output", "json", "--env-file", env, "--apply", "--yes", "--plan-in", plan_path, "leads", "merge", "--file", merge_json]
            )
            self.assertEqual(rc2, 0)
            self.assertTrue(payload2["ok"])
            self.assertFalse(payload2["dry_run"])
            self.assertEqual(len(calls), 3)
            self.assertEqual(calls[0]["method"], "GET")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/leads/L1"))
            self.assertEqual(calls[1]["method"], "GET")
            self.assertTrue(calls[1]["url"].endswith("/api/v2/leads/L2"))
            self.assertEqual(calls[2]["method"], "POST")
            self.assertTrue(calls[2]["url"].endswith("/api/v2/leads/merge"))
            self.assertIn("before_state", payload2)

    def test_phase5_leads_update_interest_status_requires_yes_and_wires_path_on_apply(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            return _json_response(url=url, status=200, obj={"ok": True})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            body_json = os.path.join(td, "interest.json")
            with open(body_json, "w", encoding="utf-8") as f:
                json.dump({"lead_ids": ["L1"], "interest_status": "interested"}, f)
            rc, payload = _run_json(
                ["--output", "json", "--env-file", env, "--apply", "leads", "update-interest-status", "--file", body_json]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])

            calls.clear()
            rc2, payload2 = _run_json(
                ["--output", "json", "--env-file", env, "--apply", "--yes", "leads", "update-interest-status", "--file", body_json]
            )
            self.assertEqual(rc2, 0)
            self.assertTrue(payload2["ok"])
            self.assertFalse(payload2["dry_run"])
            self.assertEqual(len(calls), 2)
            self.assertEqual(calls[0]["method"], "GET")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/leads/L1"))
            self.assertEqual(calls[1]["method"], "POST")
            self.assertTrue(calls[1]["url"].endswith("/api/v2/leads/update-interest-status"))
            self.assertIn("before_state", payload2)

    def test_phase5_leads_remove_from_subsequence_requires_yes_and_wires_path_on_apply(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            return _json_response(url=url, status=200, obj={"ok": True})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            body_json = os.path.join(td, "remove.json")
            with open(body_json, "w", encoding="utf-8") as f:
                json.dump({"lead_ids": ["L1"], "subsequence_id": "S1"}, f)
            rc, payload = _run_json(
                ["--output", "json", "--env-file", env, "--apply", "leads", "remove-from-subsequence", "--file", body_json]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])

            calls.clear()
            rc2, payload2 = _run_json(
                ["--output", "json", "--env-file", env, "--apply", "--yes", "leads", "remove-from-subsequence", "--file", body_json]
            )
            self.assertEqual(rc2, 0)
            self.assertTrue(payload2["ok"])
            self.assertFalse(payload2["dry_run"])
            self.assertEqual(len(calls), 2)
            self.assertEqual(calls[0]["method"], "GET")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/leads/L1"))
            self.assertEqual(calls[1]["method"], "POST")
            self.assertTrue(calls[1]["url"].endswith("/api/v2/leads/subsequence/remove"))
            self.assertIn("before_state", payload2)

    def test_phase5_leads_bulk_assign_requires_yes_and_wires_path_on_apply(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            return _json_response(url=url, status=200, obj={"ok": True})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            body_json = os.path.join(td, "assign.json")
            with open(body_json, "w", encoding="utf-8") as f:
                json.dump({"lead_ids": ["L1"], "email_account": "a@example.com"}, f)
            rc, payload = _run_json(["--output", "json", "--env-file", env, "--apply", "leads", "bulk-assign", "--file", body_json])
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])

            calls.clear()
            rc2, payload2 = _run_json(
                ["--output", "json", "--env-file", env, "--apply", "--yes", "leads", "bulk-assign", "--file", body_json]
            )
            self.assertEqual(rc2, 0)
            self.assertTrue(payload2["ok"])
            self.assertFalse(payload2["dry_run"])
            self.assertEqual(len(calls), 2)
            self.assertEqual(calls[0]["method"], "GET")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/leads/L1"))
            self.assertEqual(calls[1]["method"], "POST")
            self.assertTrue(calls[1]["url"].endswith("/api/v2/leads/bulk-assign"))
            self.assertIn("before_state", payload2)

    def test_phase5_leads_move_requires_yes_and_wires_path_on_apply(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            return _json_response(url=url, status=200, obj={"ok": True})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            body_json = os.path.join(td, "move_leads.json")
            with open(body_json, "w", encoding="utf-8") as f:
                json.dump({"lead_ids": ["L1"], "to_campaign_id": "C2"}, f)
            rc, payload = _run_json(["--output", "json", "--env-file", env, "--apply", "leads", "move", "--file", body_json])
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])

            calls.clear()
            rc2, payload2 = _run_json(["--output", "json", "--env-file", env, "--apply", "--yes", "leads", "move", "--file", body_json])
            self.assertEqual(rc2, 0)
            self.assertTrue(payload2["ok"])
            self.assertFalse(payload2["dry_run"])
            self.assertEqual(len(calls), 2)
            self.assertEqual(calls[0]["method"], "GET")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/leads/L1"))
            self.assertEqual(calls[1]["method"], "POST")
            self.assertTrue(calls[1]["url"].endswith("/api/v2/leads/move"))
            self.assertIn("before_state", payload2)

    def test_phase5_leads_move_to_subsequence_requires_yes_and_wires_path_on_apply(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            return _json_response(url=url, status=200, obj={"ok": True})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            body_json = os.path.join(td, "move_subseq.json")
            with open(body_json, "w", encoding="utf-8") as f:
                json.dump({"lead_ids": ["L1"], "subsequence_id": "S2"}, f)
            rc, payload = _run_json(
                ["--output", "json", "--env-file", env, "--apply", "leads", "move-to-subsequence", "--file", body_json]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])

            calls.clear()
            rc2, payload2 = _run_json(
                ["--output", "json", "--env-file", env, "--apply", "--yes", "leads", "move-to-subsequence", "--file", body_json]
            )
            self.assertEqual(rc2, 0)
            self.assertTrue(payload2["ok"])
            self.assertFalse(payload2["dry_run"])
            self.assertEqual(len(calls), 2)
            self.assertEqual(calls[0]["method"], "GET")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/leads/L1"))
            self.assertEqual(calls[1]["method"], "POST")
            self.assertTrue(calls[1]["url"].endswith("/api/v2/leads/subsequence/move"))
            self.assertIn("before_state", payload2)

    def test_phase5_leads_add_bulk_requires_yes_and_wires_path_on_apply(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            if url.endswith("/api/v2/leads/list"):
                return _json_response(url=url, status=200, obj={"items": []})
            return _json_response(url=url, status=200, obj={"ok": True})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            leads_json = os.path.join(td, "leads_one.json")
            with open(leads_json, "w", encoding="utf-8") as f:
                json.dump([{"email": "a@example.com"}], f)

            rc, payload = _run_json(
                ["--output", "json", "--env-file", env, "--apply", "--yes", "leads", "add-bulk", "--campaign-id", "C1", "--json", leads_json]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertEqual(calls, [])

    def test_phase5_subsequences_duplicate_requires_yes_and_wires_method_and_path_on_apply(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            if method == "POST":
                return _json_response(url=url, status=200, obj={"id": "NEW"})
            return _json_response(url=url, status=200, obj={"id": "NEW"})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            rc, payload = _run_json(
                ["--output", "json", "--env-file", env, "--apply", "subsequences", "duplicate", "--subsequence-id", "S1"]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])

            calls.clear()
            rc2, payload2 = _run_json(
                ["--output", "json", "--env-file", env, "--apply", "--yes", "subsequences", "duplicate", "--subsequence-id", "S1"]
            )
            self.assertEqual(rc2, 0)
            self.assertTrue(payload2["ok"])
            self.assertTrue(payload2["refused"])
            self.assertEqual(calls, [])

    def test_phase5_subsequences_pause_and_resume_wire_method_and_path_on_apply(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            return _json_response(url=url, status=200, obj={"ok": True})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            rc, payload = _run_json(["--output", "json", "--env-file", env, "subsequences", "pause", "--subsequence-id", "S1"])
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertEqual(len(calls), 0)

            rc2, payload2 = _run_json(["--output", "json", "--env-file", env, "--apply", "subsequences", "pause", "--subsequence-id", "S1"])
            self.assertEqual(rc2, 0)
            self.assertTrue(payload2["ok"])
            self.assertFalse(payload2["dry_run"])
            self.assertGreaterEqual(len(calls), 1)
            self.assertEqual(calls[0]["method"], "GET")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/subsequences/S1"))
            self.assertEqual(calls[1]["method"], "POST")
            self.assertTrue(calls[1]["url"].endswith("/api/v2/subsequences/S1/pause"))
            self.assertIn("before_state", payload2)

            calls.clear()
            rc3, payload3 = _run_json(
                ["--output", "json", "--env-file", env, "--apply", "subsequences", "resume", "--subsequence-id", "S1"]
            )
            self.assertEqual(rc3, 0)
            self.assertTrue(payload3["ok"])
            self.assertFalse(payload3["dry_run"])
            self.assertGreaterEqual(len(calls), 1)
            self.assertEqual(calls[0]["method"], "GET")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/subsequences/S1"))
            self.assertEqual(calls[1]["method"], "POST")
            self.assertTrue(calls[1]["url"].endswith("/api/v2/subsequences/S1/resume"))
            self.assertIn("before_state", payload3)

    def test_phase5_webhooks_get_and_event_types_wire_method_and_path(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            return _json_response(url=url, status=200, obj={"ok": True})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            rc, payload = _run_json(["--output", "json", "--env-file", env, "webhooks", "get", "--webhook-id", "W1"])
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0]["method"], "GET")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/webhooks/W1"))

            calls.clear()
            rc2, payload2 = _run_json(["--output", "json", "--env-file", env, "webhooks", "event-types"])
            self.assertEqual(rc2, 0)
            self.assertTrue(payload2["ok"])
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0]["method"], "GET")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/webhooks/event-types"))

    def test_phase5_webhooks_resume_wires_method_and_path_on_apply(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            return _json_response(url=url, status=200, obj={"ok": True})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            rc, payload = _run_json(["--output", "json", "--env-file", env, "webhooks", "resume", "--webhook-id", "W1"])
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertEqual(len(calls), 0)

            rc2, payload2 = _run_json(["--output", "json", "--env-file", env, "--apply", "webhooks", "resume", "--webhook-id", "W1"])
            self.assertEqual(rc2, 0)
            self.assertTrue(payload2["ok"])
            self.assertFalse(payload2["dry_run"])
            self.assertGreaterEqual(len(calls), 1)
            self.assertEqual(calls[0]["method"], "GET")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/webhooks/W1"))
            self.assertEqual(calls[1]["method"], "POST")
            self.assertTrue(calls[1]["url"].endswith("/api/v2/webhooks/W1/resume"))
            self.assertIn("before_state", payload2)

    def test_phase5_do_not_contact_get_and_patch_wire_method_and_path(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            return _json_response(url=url, status=200, obj={"ok": True})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            rc, payload = _run_json(["--output", "json", "--env-file", env, "do-not-contact", "get", "--entry-id", "E1"])
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0]["method"], "GET")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/block-lists-entries/E1"))

            calls.clear()
            patch_json = os.path.join(td, "dnc_patch.json")
            with open(patch_json, "w", encoding="utf-8") as f:
                json.dump({"email": "b@example.com"}, f)
            rc2, payload2 = _run_json(
                ["--output", "json", "--env-file", env, "--apply", "do-not-contact", "patch", "--entry-id", "E1", "--file", patch_json]
            )
            self.assertEqual(rc2, 0)
            self.assertTrue(payload2["ok"])
            self.assertTrue(payload2["refused"])

            rc3, payload3 = _run_json(
                ["--output", "json", "--env-file", env, "--apply", "--yes", "do-not-contact", "patch", "--entry-id", "E1", "--file", patch_json]
            )
            self.assertEqual(rc3, 0)
            self.assertTrue(payload3["ok"])
            self.assertFalse(payload3["dry_run"])
            self.assertGreaterEqual(len(calls), 1)
            self.assertEqual(calls[0]["method"], "GET")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/block-lists-entries/E1"))
            self.assertEqual(calls[1]["method"], "PATCH")
            self.assertTrue(calls[1]["url"].endswith("/api/v2/block-lists-entries/E1"))
            self.assertIn("before_state", payload3)

    def test_phase5_supersearch_enrichment_endpoints_wire_method_and_path(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            return _json_response(url=url, status=200, obj={"ok": True})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)

            rc, payload = _run_json(["--output", "json", "--env-file", env, "supersearch-enrichment", "get", "--resource-id", "R1"])
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0]["method"], "GET")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/supersearch-enrichment/R1"))

            calls.clear()
            rc2, payload2 = _run_json(["--output", "json", "--env-file", env, "supersearch-enrichment", "history", "--resource-id", "R1"])
            self.assertEqual(rc2, 0)
            self.assertTrue(payload2["ok"])
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0]["method"], "GET")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/supersearch-enrichment/history/R1"))

            calls.clear()
            preview_json = os.path.join(td, "preview.json")
            with open(preview_json, "w", encoding="utf-8") as f:
                json.dump({"search": "example"}, f)
            rc3, payload3 = _run_json(
                ["--output", "json", "--env-file", env, "supersearch-enrichment", "preview-leads", "--file", preview_json]
            )
            self.assertEqual(rc3, 0)
            self.assertTrue(payload3["ok"])
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0]["method"], "POST")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/supersearch-enrichment/preview-leads-from-supersearch"))

            calls.clear()
            settings_json = os.path.join(td, "settings.json")
            with open(settings_json, "w", encoding="utf-8") as f:
                json.dump({"enabled": True}, f)
            rc4_refuse, payload4_refuse = _run_json(
                [
                    "--output",
                    "json",
                    "--env-file",
                    env,
                    "--apply",
                    "supersearch-enrichment",
                    "patch-settings",
                    "--resource-id",
                    "R1",
                    "--file",
                    settings_json,
                ]
            )
            self.assertEqual(rc4_refuse, 0)
            self.assertTrue(payload4_refuse["ok"])
            self.assertTrue(payload4_refuse["refused"])
            self.assertEqual(len(calls), 0)

            rc4, payload4 = _run_json(
                [
                    "--output",
                    "json",
                    "--env-file",
                    env,
                    "--apply",
                    "--yes",
                    "supersearch-enrichment",
                    "patch-settings",
                    "--resource-id",
                    "R1",
                    "--file",
                    settings_json,
                ]
            )
            self.assertEqual(rc4, 0)
            self.assertTrue(payload4["ok"])
            self.assertFalse(payload4["dry_run"])
            self.assertEqual(len(calls), 3)
            self.assertEqual(calls[0]["method"], "GET")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/supersearch-enrichment/R1"))
            self.assertEqual(calls[1]["method"], "PATCH")
            self.assertTrue(calls[1]["url"].endswith("/api/v2/supersearch-enrichment/R1/settings"))
            self.assertEqual(calls[2]["method"], "GET")
            self.assertTrue(calls[2]["url"].endswith("/api/v2/supersearch-enrichment/R1"))
            self.assertIn("before_state", payload4)

            calls.clear()
            create_json = os.path.join(td, "create.json")
            with open(create_json, "w", encoding="utf-8") as f:
                json.dump({"resource_id": "R1"}, f)
            rc_create_refuse, payload_create_refuse = _run_json(
                ["--output", "json", "--env-file", env, "--apply", "supersearch-enrichment", "create", "--file", create_json]
            )
            self.assertEqual(rc_create_refuse, 0)
            self.assertTrue(payload_create_refuse["ok"])
            self.assertTrue(payload_create_refuse["refused"])
            self.assertEqual(len(calls), 0)

            rc_create, payload_create = _run_json(
                ["--output", "json", "--env-file", env, "--apply", "--yes", "supersearch-enrichment", "create", "--file", create_json]
            )
            self.assertEqual(rc_create, 0)
            self.assertTrue(payload_create["ok"])
            self.assertTrue(payload_create["refused"])
            self.assertEqual(calls, [])

            calls.clear()
            run_json = os.path.join(td, "run.json")
            with open(run_json, "w", encoding="utf-8") as f:
                json.dump({"resource_id": "R1"}, f)
            rc5_refuse, payload5_refuse = _run_json(
                ["--output", "json", "--env-file", env, "--apply", "supersearch-enrichment", "run", "--file", run_json]
            )
            self.assertEqual(rc5_refuse, 0)
            self.assertTrue(payload5_refuse["ok"])
            self.assertTrue(payload5_refuse["refused"])
            self.assertEqual(len(calls), 0)

            rc5, payload5 = _run_json(
                ["--output", "json", "--env-file", env, "--apply", "--yes", "supersearch-enrichment", "run", "--file", run_json]
            )
            self.assertEqual(rc5, 0)
            self.assertTrue(payload5["ok"])
            self.assertTrue(payload5["refused"])
            self.assertEqual(calls, [])

            calls.clear()
            enrich_json = os.path.join(td, "enrich.json")
            with open(enrich_json, "w", encoding="utf-8") as f:
                json.dump({"resource_id": "R1"}, f)
            rc6_refuse, payload6_refuse = _run_json(
                ["--output", "json", "--env-file", env, "--apply", "supersearch-enrichment", "enrich-leads", "--file", enrich_json]
            )
            self.assertEqual(rc6_refuse, 0)
            self.assertTrue(payload6_refuse["ok"])
            self.assertTrue(payload6_refuse["refused"])
            self.assertEqual(len(calls), 0)

            rc6, payload6 = _run_json(
                ["--output", "json", "--env-file", env, "--apply", "--yes", "supersearch-enrichment", "enrich-leads", "--file", enrich_json]
            )
            self.assertEqual(rc6, 0)
            self.assertTrue(payload6["ok"])
            self.assertTrue(payload6["refused"])
            self.assertEqual(calls, [])

            calls.clear()
            ai_json = os.path.join(td, "ai.json")
            with open(ai_json, "w", encoding="utf-8") as f:
                json.dump({"resource_id": "R1"}, f)
            rc7_refuse, payload7_refuse = _run_json(
                ["--output", "json", "--env-file", env, "--apply", "supersearch-enrichment", "ai", "--file", ai_json]
            )
            self.assertEqual(rc7_refuse, 0)
            self.assertTrue(payload7_refuse["ok"])
            self.assertTrue(payload7_refuse["refused"])
            self.assertEqual(len(calls), 0)

            rc7, payload7 = _run_json(
                ["--output", "json", "--env-file", env, "--apply", "--yes", "supersearch-enrichment", "ai", "--file", ai_json]
            )
            self.assertEqual(rc7, 0)
            self.assertTrue(payload7["ok"])
            self.assertTrue(payload7["refused"])
            self.assertEqual(calls, [])

    def test_sensitive_accounts_get_writes_redacted_receipt_only(self) -> None:
        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            return _json_response(
                url=url,
                status=200,
                obj={
                    "email": "a@example.com",
                    "password": "p@ssw0rd",
                    "token": "tok_123",
                    "accessToken": "acc_123",
                    "refreshToken": "ref_123",
                    "apiKey": "k_123",
                    "note": "Authorization: Bearer REAL_TOKEN==",
                },
            )

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            rc, payload = _run_json(
                ["--output", "json", "--env-file", env, "--apply", "--yes", "accounts", "get", "--email", "a@example.com"]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertFalse(payload["dry_run"])
            self.assertIn("receipt_out", payload)
            self.assertNotIn("account", payload)
            receipt_path = payload["receipt_out"]
            self.assertTrue(receipt_path and os.path.exists(receipt_path))
            receipt_text = ""
            with open(receipt_path, "r", encoding="utf-8") as f:
                receipt_text = f.read()
            receipt = json.loads(receipt_text)
            account = receipt["result"]["account"]
            self.assertEqual(account["password"], "***REDACTED***")
            self.assertEqual(account["token"], "***REDACTED***")
            self.assertEqual(account["accessToken"], "***REDACTED***")
            self.assertEqual(account["refreshToken"], "***REDACTED***")
            self.assertEqual(account["apiKey"], "***REDACTED***")
            self.assertNotIn("REAL_TOKEN==", account["note"])
            self.assertNotIn("p@ssw0rd", receipt_text)
            self.assertNotIn("tok_123", receipt_text)
            self.assertNotIn("acc_123", receipt_text)
            self.assertNotIn("ref_123", receipt_text)
            self.assertNotIn("k_123", receipt_text)
            self.assertNotIn("REAL_TOKEN==", receipt_text)

    def test_sensitive_accounts_get_stdout_text_does_not_leak_secrets(self) -> None:
        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            return _json_response(
                url=url,
                status=200,
                obj={
                    "email": "a@example.com",
                    "password": "p@ssw0rd",
                    "token": "tok_123",
                    "accessToken": "acc_123",
                    "refreshToken": "ref_123",
                    "apiKey": "k_123",
                    "note": "Authorization: Bearer REAL_TOKEN==",
                },
            )

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            rc, out = _run_stdout(
                ["--output", "text", "--env-file", env, "--apply", "--yes", "accounts", "get", "--email", "a@example.com"]
            )
            self.assertEqual(rc, 0)
            self.assertNotIn("p@ssw0rd", out)
            self.assertNotIn("tok_123", out)
            self.assertNotIn("acc_123", out)
            self.assertNotIn("ref_123", out)
            self.assertNotIn("k_123", out)
            self.assertNotIn("REAL_TOKEN==", out)
            self.assertIn("receipt_out", out)

    def test_sensitive_accounts_ctd_status_writes_redacted_receipt_only(self) -> None:
        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            return _json_response(
                url=url,
                status=200,
                obj={
                    "ok": True,
                    "token": "tok_123",
                    "note": "Authorization: Bearer REAL_TOKEN==",
                },
            )

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            rc, payload = _run_json(["--output", "json", "--env-file", env, "--apply", "--yes", "accounts", "ctd-status"])
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertFalse(payload["dry_run"])
            self.assertIn("receipt_out", payload)
            self.assertNotIn("ctd_status", payload)
            receipt_path = payload["receipt_out"]
            with open(receipt_path, "r", encoding="utf-8") as f:
                receipt_text = f.read()
            self.assertNotIn("REAL_TOKEN==", receipt_text)
            self.assertNotIn("tok_123", receipt_text)
            receipt = json.loads(receipt_text)
            self.assertEqual(receipt["result"]["ctd_status"]["token"], "***REDACTED***")
            self.assertNotIn("REAL_TOKEN==", receipt["result"]["ctd_status"]["note"])

    def test_verbose_stderr_redacts_bearer_tokens_with_padding(self) -> None:
        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            raise requests.RequestException("upstream error: Authorization: Bearer REAL_TOKEN+/==")

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            rc, payload, err = _run_json_with_stderr(
                ["--output", "json", "--env-file", env, "--verbose", "--apply", "--yes", "accounts", "get", "--email", "a@example.com"]
            )
            self.assertEqual(rc, 1)
            self.assertFalse(payload["ok"])
            self.assertNotIn("REAL_TOKEN+/==", err)
            self.assertIn("***REDACTED***", err)

    def test_threads_reply_requires_ack_irreversible(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env = _write_env(td)
            plan_path = _write_plan(
                td,
                "plan.json",
                {
                    "selector": {"kind": "threads.reply", "value": "T1"},
                    "baseline": {"env_fingerprint": "https://api.instantly.ai/api/v2"},
                    "request": {
                        "method": "POST",
                        "path": "/emails/reply",
                        "body": {"thread_id": "T1", "reply_to_uuid": "R1", "message": "Hello"},
                    },
                },
            )
            rc, payload = _run_json(
                [
                    "--output",
                    "json",
                    "--env-file",
                    env,
                    "--apply",
                    "--yes",
                    "--plan-in",
                    plan_path,
                    "threads",
                    "reply",
                    "--thread-id",
                    "T1",
                    "--reply-to-uuid",
                    "R1",
                    "--message",
                    "Hello",
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertIn("ack-irreversible", " ".join(payload.get("reasons") or []))

    def test_threads_reply_refuses_without_plan_in_on_apply(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env = _write_env(td)
            rc, payload = _run_json(
                [
                    "--output",
                    "json",
                    "--env-file",
                    env,
                    "--apply",
                    "--yes",
                    "--ack-irreversible",
                    "threads",
                    "reply",
                    "--thread-id",
                    "T1",
                    "--reply-to-uuid",
                    "R1",
                    "--message",
                    "Hello",
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertIn("plan-in", " ".join(payload.get("reasons") or []))

    def test_emails_forward_requires_ack_irreversible(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env = _write_env(td)
            plan_path = _write_plan(
                td,
                "plan.json",
                {
                    "selector": {"kind": "emails.forward", "value": "h1"},
                    "baseline": {"env_fingerprint": "https://api.instantly.ai/api/v2"},
                    "request": {"method": "POST", "path": "/emails/forward", "body": {"email_id": "E1"}},
                },
            )
            rc, payload = _run_json(
                [
                    "--output",
                    "json",
                    "--env-file",
                    env,
                    "--apply",
                    "--yes",
                    "--plan-in",
                    plan_path,
                    "emails",
                    "forward",
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertIn("ack-irreversible", " ".join(payload.get("reasons") or []))

    def test_emails_forward_refuses_without_plan_in_on_apply(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env = _write_env(td)
            rc, payload = _run_json(
                [
                    "--output",
                    "json",
                    "--env-file",
                    env,
                    "--apply",
                    "--yes",
                    "--ack-irreversible",
                    "emails",
                    "forward",
                    "--file",
                    "forward.json",
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertIn("plan-in", " ".join(payload.get("reasons") or []))

    def test_emails_forward_apply_calls_post_and_verify_get(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            if method == "POST" and url.endswith("/api/v2/emails/forward"):
                return _json_response(url=url, status=200, obj={"ok": True})
            if method == "GET" and url.endswith("/api/v2/emails/E1"):
                return _json_response(url=url, status=200, obj={"id": "E1"})
            return _json_response(url=url, status=200, obj={"ok": True})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            plan_path = _write_plan(
                td,
                "plan.json",
                {
                    "selector": {"kind": "emails.forward", "value": "h1"},
                    "baseline": {"env_fingerprint": "https://api.instantly.ai/api/v2"},
                    "request": {"method": "POST", "path": "/emails/forward", "body": {"email_id": "E1"}},
                },
            )
            rc, payload = _run_json(
                [
                    "--output",
                    "json",
                    "--env-file",
                    env,
                    "--apply",
                    "--yes",
                    "--ack-irreversible",
                    "--plan-in",
                    plan_path,
                    "emails",
                    "forward",
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertEqual(calls, [])

    def test_emails_patch_dry_run_does_not_call_http(self) -> None:
        called = False

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            nonlocal called
            called = True
            return _json_response(url=url, status=200, obj={"ok": True})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            patch_path = os.path.join(td, "patch.json")
            with open(patch_path, "w", encoding="utf-8") as f:
                json.dump({"foo": "bar"}, f)
            rc, payload = _run_json(["--output", "json", "--env-file", env, "emails", "patch", "--email-id", "E1", "--file", patch_path])
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertFalse(called)

    def test_emails_patch_apply_calls_patch_and_verify_get(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            if method == "PATCH":
                return _json_response(url=url, status=200, obj={"ok": True})
            if method == "GET":
                return _json_response(url=url, status=200, obj={"id": "E1"})
            return _json_response(url=url, status=200, obj={"ok": True})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            patch_path = os.path.join(td, "patch.json")
            with open(patch_path, "w", encoding="utf-8") as f:
                json.dump({"foo": "bar"}, f)
            rc, payload = _run_json(
                ["--output", "json", "--env-file", env, "--apply", "emails", "patch", "--email-id", "E1", "--file", patch_path]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertFalse(payload["dry_run"])
            self.assertEqual(len(calls), 3)
            self.assertEqual(calls[0]["method"], "GET")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/emails/E1"))
            self.assertEqual(calls[1]["method"], "PATCH")
            self.assertTrue(calls[1]["url"].endswith("/api/v2/emails/E1"))
            self.assertEqual(calls[2]["method"], "GET")
            self.assertTrue(calls[2]["url"].endswith("/api/v2/emails/E1"))
            self.assertIn("before_state", payload)

    def test_emails_delete_refuses_without_plan_in_on_apply(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env = _write_env(td)
            rc, payload = _run_json(["--output", "json", "--env-file", env, "--apply", "--yes", "emails", "delete", "--email-id", "E1"])
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertIn("plan-in", " ".join(payload.get("reasons") or []))

    def test_emails_delete_apply_verifies_404(self) -> None:
        calls: list[dict[str, Any]] = []
        get_count = 0

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            nonlocal get_count
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            if method == "DELETE":
                return _json_response(url=url, status=200, obj={"ok": True})
            if method == "GET":
                get_count += 1
                if get_count == 1:
                    return _json_response(url=url, status=200, obj={"id": "E1"})
                return _json_response(url=url, status=404, obj={"error": "not found"})
            return _json_response(url=url, status=200, obj={"ok": True})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            plan_path = _write_plan(
                td,
                "plan.json",
                {
                    "selector": {"kind": "emails.delete", "value": "E1"},
                    "baseline": {"env_fingerprint": "https://api.instantly.ai/api/v2"},
                    "request": {"method": "DELETE", "path": "/emails/E1", "body": {}},
                },
            )
            rc, payload = _run_json(
                ["--output", "json", "--env-file", env, "--apply", "--yes", "--plan-in", plan_path, "emails", "delete", "--email-id", "E1"]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertFalse(payload["dry_run"])
            self.assertTrue(payload["receipt"]["verification"]["ok"])
            self.assertEqual(len(calls), 3)
            self.assertEqual(calls[0]["method"], "GET")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/emails/E1"))
            self.assertEqual(calls[1]["method"], "DELETE")
            self.assertTrue(calls[1]["url"].endswith("/api/v2/emails/E1"))
            self.assertEqual(calls[2]["method"], "GET")
            self.assertTrue(calls[2]["url"].endswith("/api/v2/emails/E1"))
            self.assertIn("before_state", payload)

    def test_webhooks_event_types_endpoint(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            return _json_response(url=url, status=200, obj={"items": []})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            rc, payload = _run_json(["--output", "json", "--env-file", env, "webhooks", "event-types"])
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0]["method"], "GET")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/webhooks/event-types"))

    def test_webhooks_resume_dry_run_does_not_call_http(self) -> None:
        called = False

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            nonlocal called
            called = True
            return _json_response(url=url, status=200, obj={"ok": True})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            rc, payload = _run_json(["--output", "json", "--env-file", env, "webhooks", "resume", "--webhook-id", "W1"])
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertFalse(called)

    def test_webhooks_delete_refuses_without_yes_on_apply(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env = _write_env(td)
            rc, payload = _run_json(
                ["--output", "json", "--env-file", env, "--apply", "webhooks", "delete", "--webhook-id", "W1"]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])

            rc2, payload2 = _run_json(
                ["--output", "json", "--env-file", env, "--apply", "--yes", "webhooks", "delete", "--webhook-id", "W1"]
            )
            self.assertEqual(rc2, 0)
            self.assertTrue(payload2["ok"])
            self.assertTrue(payload2["refused"])

    def test_webhooks_delete_refuses_without_plan_in_on_apply(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env = _write_env(td)
            rc, payload = _run_json(
                [
                    "--output",
                    "json",
                    "--env-file",
                    env,
                    "--apply",
                    "--yes",
                    "webhooks",
                    "delete",
                    "--webhook-id",
                    "W1",
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertIn("plan-in", " ".join(payload.get("reasons") or []))

    def test_emails_list_defaults_to_safe_limit_20(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            return _json_response(url=url, status=200, obj={"items": [], "next_starting_after": None})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            rc, payload = _run_json(["--output", "json", "--env-file", env, "emails", "list"])
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0]["method"], "GET")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/emails"))
            self.assertEqual(calls[0]["kwargs"]["params"]["limit"], 20)

    def test_emails_unread_count_endpoint(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            return _json_response(url=url, status=200, obj={"count": 7})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            rc, payload = _run_json(["--output", "json", "--env-file", env, "emails", "unread-count"])
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0]["method"], "GET")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/emails/unread/count"))

    def test_dnc_list_endpoint_and_pagination(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            return _json_response(url=url, status=200, obj={"items": [], "next_starting_after": "N"})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            rc, payload = _run_json(
                [
                    "--output",
                    "json",
                    "--env-file",
                    env,
                    "do-not-contact",
                    "list",
                    "--limit",
                    "5",
                    "--starting-after",
                    "S",
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["next_starting_after"], "N")
            self.assertEqual(calls[0]["kwargs"]["params"]["limit"], 5)
            self.assertEqual(calls[0]["kwargs"]["params"]["starting_after"], "S")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/block-lists-entries"))

    def test_dnc_get_endpoint(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            return _json_response(url=url, status=200, obj={"id": "E1"})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            rc, payload = _run_json(["--output", "json", "--env-file", env, "do-not-contact", "get", "--entry-id", "E1"])
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0]["method"], "GET")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/block-lists-entries/E1"))

    def test_dnc_patch_requires_yes_on_apply(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env = _write_env(td)
            patch_json = os.path.join(td, "patch.json")
            with open(patch_json, "w", encoding="utf-8") as f:
                json.dump({"email": "x@example.com"}, f)
            rc, payload = _run_json(
                ["--output", "json", "--env-file", env, "--apply", "do-not-contact", "patch", "--entry-id", "E1", "--file", patch_json]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])

    def test_dnc_delete_refuses_without_plan_in_on_apply(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env = _write_env(td)
            rc, payload = _run_json(
                [
                    "--output",
                    "json",
                    "--env-file",
                    env,
                    "--apply",
                    "--yes",
                    "do-not-contact",
                    "delete",
                    "--entry-id",
                    "E1",
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertIn("plan-in", " ".join(payload.get("reasons") or []))

    def test_background_jobs_list_wires_pagination_and_next_cursor(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            return _json_response(url=url, status=200, obj={"items": [], "next_starting_after": "NEXT"})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            rc, payload = _run_json(
                [
                    "--output",
                    "json",
                    "--env-file",
                    env,
                    "background-jobs",
                    "list",
                    "--limit",
                    "10",
                    "--starting-after",
                    "CUR",
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["next_starting_after"], "NEXT")
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0]["method"], "GET")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/background-jobs"))
            self.assertEqual(calls[0]["kwargs"]["params"]["limit"], 10)
            self.assertEqual(calls[0]["kwargs"]["params"]["starting_after"], "CUR")

    def test_background_jobs_get_endpoint(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            return _json_response(url=url, status=200, obj={"id": "J1"})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            rc, payload = _run_json(["--output", "json", "--env-file", env, "background-jobs", "get", "--job-id", "J1"])
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0]["method"], "GET")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/background-jobs/J1"))

    def test_campaigns_activate_plan_has_correct_endpoint(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env = _write_env(td)
            rc, payload = _run_json(["--output", "json", "--env-file", env, "campaigns", "activate", "--campaign-id", "C1"])
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            plan = payload["plan"]
            self.assertEqual(plan["request"]["method"], "POST")
            self.assertEqual(plan["request"]["path"], "/campaigns/C1/activate")
            self.assertEqual(plan["request"]["body"], {})

    def test_leads_list_uses_post_json_body(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            return _json_response(url=url, status=200, obj={"items": [], "next_starting_after": None})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            rc, payload = _run_json(
                [
                    "--output",
                    "json",
                    "--env-file",
                    env,
                    "leads",
                    "list",
                    "--campaign-id",
                    "C1",
                    "--limit",
                    "2",
                    "--starting-after",
                    "CUR",
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0]["method"], "POST")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/leads/list"))
            self.assertEqual(calls[0]["kwargs"]["json"]["campaign_id"], "C1")
            self.assertEqual(calls[0]["kwargs"]["json"]["limit"], 2)
            self.assertEqual(calls[0]["kwargs"]["json"]["starting_after"], "CUR")

    def test_webhooks_patch_plan_has_correct_method_and_path(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env = _write_env(td)
            patch_json = os.path.join(td, "patch.json")
            with open(patch_json, "w", encoding="utf-8") as f:
                json.dump({"url": "https://example.com/webhook"}, f)
            rc, payload = _run_json(
                [
                    "--output",
                    "json",
                    "--env-file",
                    env,
                    "webhooks",
                    "patch",
                    "--webhook-id",
                    "W1",
                    "--file",
                    patch_json,
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            plan = payload["plan"]
            self.assertEqual(plan["request"]["method"], "PATCH")
            self.assertEqual(plan["request"]["path"], "/webhooks/W1")

    def test_webhook_events_list_filters_by_webhook_id(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            return _json_response(url=url, status=200, obj={"items": []})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            rc, payload = _run_json(
                ["--output", "json", "--env-file", env, "webhook-events", "list", "--webhook-id", "W1"]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(calls[0]["kwargs"]["params"]["limit"], 20)
            self.assertEqual(calls[0]["kwargs"]["params"]["webhook_id"], "W1")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/webhook-events"))

    def test_webhook_events_list_refuses_over_limit_without_http_call(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            return _json_response(url=url, status=200, obj={"items": []})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            rc, payload = _run_json(
                ["--output", "json", "--env-file", env, "webhook-events", "list", "--limit", "51"]
            )
            self.assertEqual(rc, 1)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "ValidationError")
            self.assertEqual(calls, [])

    def test_webhook_events_get_endpoint(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            return _json_response(url=url, status=200, obj={"id": "E1"})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            rc, payload = _run_json(["--output", "json", "--env-file", env, "webhook-events", "get", "--event-id", "E1"])
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0]["method"], "GET")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/webhook-events/E1"))

    def test_webhook_events_summary_wires_dates(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            return _json_response(url=url, status=200, obj={"total": 0})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            rc, payload = _run_json(
                [
                    "--output",
                    "json",
                    "--env-file",
                    env,
                    "webhook-events",
                    "summary",
                    "--from",
                    "2024-01-01",
                    "--to",
                    "2024-01-31",
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0]["method"], "GET")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/webhook-events/summary"))
            self.assertEqual(calls[0]["kwargs"]["params"]["from"], "2024-01-01")
            self.assertEqual(calls[0]["kwargs"]["params"]["to"], "2024-01-31")

    def test_workspace_whitelabel_get_endpoint(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            return _json_response(url=url, status=200, obj={"domain": None})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            rc, payload = _run_json(["--output", "json", "--env-file", env, "workspace", "whitelabel-domain", "get"])
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0]["method"], "GET")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/workspaces/current/whitelabel-domain"))

    def test_workspace_billing_plan_details_endpoint(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            return _json_response(url=url, status=200, obj={"ok": True})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            rc, payload = _run_json(["--output", "json", "--env-file", env, "workspace-billing", "plan-details"])
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0]["method"], "GET")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/workspace-billing/plan-details"))

    def test_workspace_members_list_wires_pagination(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            return _json_response(url=url, status=200, obj={"items": [], "next_starting_after": None})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            rc, payload = _run_json(
                [
                    "--output",
                    "json",
                    "--env-file",
                    env,
                    "workspace-members",
                    "list",
                    "--limit",
                    "3",
                    "--starting-after",
                    "CUR",
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0]["method"], "GET")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/workspace-members"))
            self.assertEqual(calls[0]["kwargs"]["params"]["limit"], 3)
            self.assertEqual(calls[0]["kwargs"]["params"]["starting_after"], "CUR")

    def test_workspace_group_members_admin_endpoint(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            return _json_response(url=url, status=200, obj={"items": []})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            rc, payload = _run_json(["--output", "json", "--env-file", env, "workspace-group-members", "admin"])
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0]["method"], "GET")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/workspace-group-members/admin"))

    def test_oauth_session_status_endpoint(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            return _json_response(url=url, status=200, obj={"status": "ok"})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            rc, payload = _run_json(
                ["--output", "json", "--env-file", env, "oauth", "session-status", "--session-id", "S1"]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0]["method"], "GET")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/oauth/session/status/S1"))

    def test_api_keys_create_refuses_without_ack_store_secret_locally(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env = _write_env(td)
            plan_path = _write_plan(
                td,
                "plan.json",
                {
                    "selector": {"kind": "api-keys.create", "value": "file.json"},
                    "baseline": {"env_fingerprint": "https://api.instantly.ai/api/v2"},
                    "request": {"method": "POST", "path": "/api-keys", "body": {"name": "Key 1"}},
                },
            )
            rc, payload = _run_json(
                [
                    "--output",
                    "json",
                    "--env-file",
                    env,
                    "--apply",
                    "--yes",
                    "--plan-in",
                    plan_path,
                    "api-keys",
                    "create",
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertIn("ack-store-secret-locally", " ".join(payload.get("reasons") or []))

    def test_api_keys_create_apply_requires_plan_in(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env = _write_env(td)
            create_json = os.path.join(td, "create.json")
            with open(create_json, "w", encoding="utf-8") as f:
                json.dump({"name": "Key 1"}, f)
            rc, payload = _run_json(
                [
                    "--output",
                    "json",
                    "--env-file",
                    env,
                    "--apply",
                    "--yes",
                    "api-keys",
                    "create",
                    "--file",
                    create_json,
                    "--ack-store-secret-locally",
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertIn("plan-in", " ".join(payload.get("reasons") or []))

    def test_api_keys_create_stores_secret_but_never_prints_it(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            if method == "POST" and url.endswith("/api/v2/api-keys"):
                return _json_response(url=url, status=200, obj={"id": "K1", "name": "Key 1", "key": "SECRET_VALUE"})
            if method == "GET" and url.endswith("/api/v2/api-keys"):
                return _json_response(url=url, status=200, obj={"items": [{"id": "K1", "name": "Key 1"}]})
            return _json_response(url=url, status=200, obj={"ok": True})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            plan_path = _write_plan(
                td,
                "plan.json",
                {
                    "selector": {"kind": "api-keys.create", "value": "file.json"},
                    "baseline": {"env_fingerprint": "https://api.instantly.ai/api/v2"},
                    "request": {"method": "POST", "path": "/api-keys", "body": {"name": "Key 1"}},
                },
            )
            rc, payload = _run_json(
                [
                    "--output",
                    "json",
                    "--env-file",
                    env,
                    "--apply",
                    "--yes",
                    "--plan-in",
                    plan_path,
                    "api-keys",
                    "create",
                    "--ack-store-secret-locally",
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertFalse(payload.get("dry_run", True))
            self.assertNotIn("SECRET_VALUE", json.dumps(payload))
            secret_path = payload["receipt"]["result"]["sensitive_output"]["path"]
            with open(secret_path, "r", encoding="utf-8") as f:
                self.assertIn("SECRET_VALUE", f.read())
            self.assertGreaterEqual(len(calls), 2)

    def test_api_keys_list_redacts_sensitive_fields(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            return _json_response(
                url=url,
                status=200,
                obj={"items": [{"id": "K1", "name": "Key 1", "key": "SECRET_VALUE"}], "next_starting_after": None},
            )

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            rc, payload = _run_json(["--output", "json", "--env-file", env, "api-keys", "list"])
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertNotIn("SECRET_VALUE", json.dumps(payload))
            self.assertEqual(payload["api_keys"]["items"][0]["id"], "K1")
            self.assertEqual(payload["api_keys"]["items"][0]["name"], "Key 1")
            self.assertTrue(calls)
            self.assertEqual(calls[0]["method"], "GET")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/api-keys"))

    def test_dfy_list_accounts_with_passwords_stores_secret_but_never_prints_it(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            return _json_response(
                url=url,
                status=200,
                obj={"items": [{"email": "a@example.com", "password": "P@ssw0rd"}], "next_starting_after": None},
            )

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            rc, payload = _run_json(
                [
                    "--output",
                    "json",
                    "--env-file",
                    env,
                    "dfy-email-account-orders",
                    "list-accounts",
                    "--with-passwords",
                    "--ack-store-secret-locally",
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertNotIn("P@ssw0rd", json.dumps(payload))
            self.assertTrue(calls)
            self.assertEqual(calls[0]["method"], "GET")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/dfy-email-account-orders/accounts"))
            self.assertTrue(calls[0]["kwargs"]["params"]["with_passwords"])
            secret_path = payload["sensitive_output"]["path"]
            with open(secret_path, "r", encoding="utf-8") as f:
                self.assertIn("P@ssw0rd", f.read())

    def test_inbox_placement_tests_create_refuses_without_ack_irreversible(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env = _write_env(td)
            test_json = os.path.join(td, "test.json")
            with open(test_json, "w", encoding="utf-8") as f:
                json.dump({"sending_method": 1, "emails": ["user@example.com"]}, f)
            rc, payload = _run_json(
                [
                    "--output",
                    "json",
                    "--env-file",
                    env,
                    "--apply",
                    "--yes",
                    "inbox-placement",
                    "tests",
                    "create",
                    "--file",
                    test_json,
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertIn("ack-irreversible", " ".join(payload.get("reasons") or []))

    def test_inbox_placement_tests_list_wires_default_limit(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            return _json_response(url=url, status=200, obj={"items": []})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            rc, payload = _run_json(["--output", "json", "--env-file", env, "inbox-placement", "tests", "list"])
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0]["method"], "GET")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/inbox-placement-tests"))
            self.assertEqual(calls[0]["kwargs"]["params"]["limit"], 20)

    def test_inbox_placement_reports_list_omits_optional_skip_flags_when_missing(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            return _json_response(url=url, status=200, obj={"items": []})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            rc, payload = _run_json(
                ["--output", "json", "--env-file", env, "inbox-placement", "reports", "list", "--test-id", "T1"]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(len(calls), 1)
            self.assertTrue(calls[0]["url"].endswith("/api/v2/inbox-placement-reports"))
            params = calls[0]["kwargs"]["params"]
            self.assertNotIn("skip_blacklist_report", params)
            self.assertNotIn("skip_spam_assassin_report", params)

    def test_email_verification_create_refuses_without_yes_on_apply(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env = _write_env(td)
            rc, payload = _run_json(
                ["--output", "json", "--env-file", env, "--apply", "email-verification", "create", "--email", "a@example.com"]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])

    def test_email_verification_status_wires_urlencoding(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            return _json_response(url=url, status=200, obj={"status": "ok"})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            rc, payload = _run_json(
                ["--output", "json", "--env-file", env, "email-verification", "status", "--email", "a@example.com"]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0]["method"], "GET")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/email-verification/a%40example.com"))

    def test_audit_log_list_hides_items_by_default(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            return _json_response(url=url, status=200, obj=[{"id": "A1", "activity_type": 1, "message": "secret"}])

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            rc, payload = _run_json(
                [
                    "--output",
                    "json",
                    "--env-file",
                    env,
                    "audit-log",
                    "list",
                    "--start-date",
                    "2024-01-01",
                    "--end-date",
                    "2024-01-31",
                    "--search",
                    "login",
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertIn("audit_log_summaries", payload)
            self.assertNotIn("audit_logs", payload)
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0]["method"], "GET")
            self.assertTrue(calls[0]["url"].endswith("/api/v2/audit-logs"))
            self.assertEqual(calls[0]["kwargs"]["params"]["start_date"], "2024-01-01")
            self.assertEqual(calls[0]["kwargs"]["params"]["end_date"], "2024-01-31")
            self.assertEqual(calls[0]["kwargs"]["params"]["search"], "login")

    def test_audit_log_list_include_items_refuses_without_out_and_does_not_call_http(self) -> None:
        called = False

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            nonlocal called
            called = True
            return _json_response(url=url, status=200, obj=[])

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            rc, payload = _run_json(
                [
                    "--output",
                    "json",
                    "--env-file",
                    env,
                    "audit-log",
                    "list",
                    "--start-date",
                    "2024-01-01",
                    "--end-date",
                    "2024-01-31",
                    "--include-items",
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertFalse(called)

    def test_audit_log_list_include_items_writes_file_and_keeps_stdout_minimal(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            return _json_response(url=url, status=200, obj=[{"id": "A1", "activity_type": 1, "message": "secret"}])

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            out_path = os.path.join(td, "audit-logs.json")
            rc, payload = _run_json(
                [
                    "--output",
                    "json",
                    "--env-file",
                    env,
                    "audit-log",
                    "list",
                    "--start-date",
                    "2024-01-01",
                    "--end-date",
                    "2024-01-31",
                    "--include-items",
                    "--out",
                    out_path,
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertNotIn("audit_logs", payload)
            self.assertEqual(payload["out_path"], out_path)
            self.assertEqual(len(calls), 1)
            self.assertTrue(calls[0]["url"].endswith("/api/v2/audit-logs"))
            with open(out_path, "r", encoding="utf-8") as f:
                saved = json.loads(f.read())
            self.assertEqual(saved[0]["id"], "A1")

    def test_http_error_redacts_bearer_tokens(self) -> None:
        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            return _FakeResponse(
                status_code=401,
                url=url,
                headers={"content-type": "text/plain"},
                content=b"unauthorized",
                _text='Bad header: Authorization: \"Bearer SECRET_TOKEN\"',
            )

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            rc, payload = _run_json(["--output", "json", "--env-file", env, "whoami"])
            self.assertEqual(rc, 1)
            self.assertFalse(payload["ok"])
            self.assertNotIn("SECRET_TOKEN", payload["error"])
            self.assertIn("***REDACTED***", payload["error"])

    def test_request_exception_redacts_bearer_tokens(self) -> None:
        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            raise requests.RequestException('Network fail with Authorization: "Bearer SECRET_TOKEN"')

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            rc, payload = _run_json(["--output", "json", "--env-file", env, "whoami"])
            self.assertEqual(rc, 1)
            self.assertFalse(payload["ok"])
            self.assertNotIn("SECRET_TOKEN", payload["error"])
            self.assertIn("***REDACTED***", payload["error"])

    def test_write_plan_declares_no_machine_rollback_path(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env = _write_env(td)
            rc, payload = _run_json(
                [
                    "--output",
                    "json",
                    "--env-file",
                    env,
                    "campaigns",
                    "activate",
                    "--campaign-id",
                    "C1",
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])

            plan = payload["plan"]
            rollback = plan.get("rollback") or {}
            self.assertIsInstance(rollback, dict)
            self.assertFalse(rollback.get("supported"))
            self.assertIn("no machine rollback path", str(rollback.get("notes", "")).lower())

    def test_apply_receipt_has_no_backups_and_no_rollback_plan(self) -> None:
        calls: list[dict[str, Any]] = []

        def _req(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:  # noqa: ANN001
            calls.append({"method": method, "url": url, "kwargs": kwargs})
            if method == "POST":
                return _json_response(url=url, status=200, obj={"ok": True})
            if method == "GET":
                return _json_response(url=url, status=200, obj={"id": "C1", "status": "active"})
            return _json_response(url=url, status=200, obj={})

        with tempfile.TemporaryDirectory() as td, patch("requests.Session.request", new=_req):
            env = _write_env(td)
            rc, payload = _run_json(
                [
                    "--output",
                    "json",
                    "--env-file",
                    env,
                    "--apply",
                    "campaigns",
                    "activate",
                    "--campaign-id",
                    "C1",
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertFalse(payload.get("dry_run", True))

            receipt = payload.get("receipt")
            if receipt is None:
                receipt_path = payload.get("receipt_out")
                self.assertTrue(receipt_path and os.path.exists(receipt_path))
                with open(receipt_path, "r", encoding="utf-8") as f:
                    receipt = json.load(f)

            self.assertIsNotNone(receipt)
            self.assertEqual(receipt.get("backups"), [])
            self.assertIsNone(receipt.get("rollback_plan"))
            self.assertGreaterEqual(len(calls), 1)
