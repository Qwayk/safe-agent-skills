from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from callrail_safe_agent_cli.cli import main


class _DummyResponse:
    def __init__(self, *, status: int, url: str, payload: object) -> None:
        self.status_code = int(status)
        self.url = str(url)
        self.content = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.headers: dict[str, str] = {}


def _write_env_file(
    path: Path,
    *,
    base_url: str,
    token: str = "tok_test",
    timeout_s: int = 30,
) -> None:
    path.write_text(
        "\n".join(
            [
                f"CALLRAIL_API_BASE_URL={base_url}",
                f"CALLRAIL_API_TOKEN={token}",
                f"CALLRAIL_TIMEOUT_S={timeout_s}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


class TestGenericExecutionContract(unittest.TestCase):
    def test_real_read_commands_use_expected_get_endpoints(self) -> None:
        read_cases = [
            ("accounts", "get", ["--account-id", "acc_123"], "https://api.callrail.test/v3/a/acc_123.json"),
            ("calls", "list", [], "https://api.callrail.test/v3/a/acc_default/calls.json"),
            ("calls", "summary", [], "https://api.callrail.test/v3/a/acc_default/calls/summary.json"),
            ("calls", "timeseries", [], "https://api.callrail.test/v3/a/acc_default/calls/timeseries.json"),
            ("calls", "recording", ["--call-id", "call_123"], "https://api.callrail.test/v3/a/acc_default/calls/call_123/recording.json"),
            ("companies", "list", [], "https://api.callrail.test/v3/a/acc_default/companies.json"),
            ("companies", "get", ["--company-id", "cmp_123"], "https://api.callrail.test/v3/a/acc_default/companies/cmp_123.json"),
            ("form-submissions", "list", [], "https://api.callrail.test/v3/a/acc_default/form_submissions.json"),
            ("form-submissions", "summary", [], "https://api.callrail.test/v3/a/acc_default/forms/summary.json"),
            ("integrations", "list", ["--company-id", "cmp_123"], "https://api.callrail.test/v3/a/acc_default/integrations.json"),
            ("integrations", "get", ["--integration-id", "123"], "https://api.callrail.test/v3/a/acc_default/integrations/123.json"),
            ("integration-filters", "list", ["--company-id", "cmp_123"], "https://api.callrail.test/v3/a/acc_default/integration_triggers.json"),
            ("integration-filters", "get", ["--integration-filter-id", "123"], "https://api.callrail.test/v3/a/acc_default/integration_triggers/123.json"),
            ("notifications", "list", [], "https://api.callrail.test/v3/a/acc_default/notifications.json"),
            ("outbound-caller-ids", "list", ["--company-id", "cmp_123"], "https://api.callrail.test/v3/a/acc_default/caller_ids.json"),
            (
                "outbound-caller-ids",
                "get",
                ["--caller-id", "cid_123"],
                "https://api.callrail.test/v3/a/acc_default/caller_ids/cid_123.json",
            ),
            ("page-views", "list", ["--call-id", "call_123"], "https://api.callrail.test/v3/a/acc_default/calls/call_123/page_views.json"),
            ("sms-threads", "list", [], "https://api.callrail.test/v3/a/acc_default/sms-threads.json"),
            ("sms-threads", "get", ["--thread-id", "thread_123"], "https://api.callrail.test/v3/a/acc_default/sms-threads/thread_123.json"),
            ("summary-emails", "list", [], "https://api.callrail.test/v3/a/acc_default/summary_emails"),
            (
                "summary-emails",
                "get",
                ["--summary-email-id", "sum_123"],
                "https://api.callrail.test/v3/a/acc_default/summary_emails/sum_123.json",
            ),
            ("text-messages", "list", [], "https://api.callrail.test/v3/a/acc_default/text-messages.json"),
            ("text-messages", "get", ["--conversation-id", "conv_123"], "https://api.callrail.test/v3/a/acc_default/text-messages/conv_123.json"),
            ("message-flows", "list", [], "https://api.callrail.test/v3/a/acc_default/message-flows.json"),
            (
                "message-flows",
                "get",
                ["--message-flow-id", "flow_123"],
                "https://api.callrail.test/v3/a/acc_default/message-flows/flow_123.json",
            ),
            ("trackers", "list", [], "https://api.callrail.test/v3/a/acc_default/trackers.json"),
            ("trackers", "get", ["--tracker-id", "trk_123"], "https://api.callrail.test/v3/a/acc_default/trackers/trk_123.json"),
            ("users", "list", [], "https://api.callrail.test/v3/a/acc_default/users.json"),
            ("users", "get", ["--user-id", "usr_123"], "https://api.callrail.test/v3/a/acc_default/users/usr_123.json"),
            ("leads", "list", [], "https://api.callrail.test/v3/a/acc_default/leads.json"),
            ("lead-timelines", "get", ["--lead-id", "lead_123"], "https://api.callrail.test/v3/a/acc_default/leads/lead_123/timeline.json"),
        ]

        for family, api_cmd, argv, expected_url in read_cases:
            with self.subTest(command=f"{family} {api_cmd}"):
                with tempfile.TemporaryDirectory() as td:
                    env_path = Path(td) / ".env"
                    _write_env_file(env_path, base_url="https://api.callrail.test")

                    captured: dict[str, object] = {}

                    def fake_request(self, method, url, **kwargs):  # noqa: ANN001
                        captured["method"] = method
                        captured["url"] = str(url)
                        captured["headers"] = dict(kwargs.get("headers") or {})
                        return _DummyResponse(status=200, url=str(url), payload={"ok": True})

                    buf = io.StringIO()
                    with patch.dict(os.environ, {"CALLRAIL_DEFAULT_ACCOUNT_ID": "acc_default"}):
                        with patch("requests.Session.request", new=fake_request):
                            with redirect_stdout(buf):
                                rc = main(
                                    [
                                        "--output",
                                        "json",
                                        "--env-file",
                                        str(env_path),
                                        family,
                                        api_cmd,
                                        *argv,
                                    ]
                                )

                    payload = json.loads(buf.getvalue())
                    self.assertEqual(rc, 0)
                    self.assertEqual(payload.get("ok"), True)
                    self.assertEqual(payload["request"]["method"], captured.get("method"))
                    self.assertEqual(payload["request"]["url"], captured.get("url"))
                    self.assertEqual(payload["request"]["method"], "GET")
                    self.assertEqual(payload["request"]["url"], expected_url)
                    self.assertEqual(payload["response"]["status"], 200)

    def test_write_commands_without_apply_plan_without_http(self) -> None:
        write_cases = [
            ("calls", "update", ["--call-id", "call_123"], "{}"),
            ("tags", "create", [], "{}"),
            ("tags", "update", ["--tag-id", "tag_123"], "{}"),
            ("tags", "delete", ["--tag-id", "tag_123"], None),
            ("companies", "create", [], "{}"),
            ("companies", "update", ["--company-id", "cmp_123"], "{}"),
            ("companies", "bulk-update", [], "{}"),
            ("companies", "disable", ["--company-id", "cmp_123"], None),
            ("form-submissions", "create", [], "{}"),
            ("form-submissions", "update", ["--submission-id", "sub_123"], "{}"),
            ("form-submissions", "ignore-fields", [], "{}"),
            ("integrations", "create", [], '{"type":"webhooks"}'),
            ("integrations", "update", ["--integration-id", "123"], '{"type":"custom"}'),
            ("integrations", "disable", ["--integration-id", "123"], None),
            ("integration-filters", "create", [], "{}"),
            ("integration-filters", "update", ["--integration-filter-id", "123"], "{}"),
            ("integration-filters", "delete", ["--integration-filter-id", "123"], None),
            ("notifications", "create", [], "{}"),
            ("notifications", "update", ["--notification-id", "123"], "{}"),
            ("notifications", "delete", ["--notification-id", "123"], None),
            ("outbound-caller-ids", "create", [], "{}"),
            ("outbound-caller-ids", "delete", ["--caller-id", "cid_123"], None),
            ("sms-threads", "update", ["--thread-id", "thread_123"], "{}"),
            ("summary-emails", "create", [], "{}"),
            ("summary-emails", "update", ["--summary-email-id", "sum_123"], "{}"),
            ("summary-emails", "delete", ["--summary-email-id", "sum_123"], None),
            ("text-messages", "send", [], "{}"),
            ("message-flows", "create", [], "{}"),
            ("message-flows", "update", ["--message-flow-id", "flow_123"], "{}"),
            ("message-flows", "delete", ["--message-flow-id", "flow_123"], None),
            ("trackers", "create-session", [], "{}"),
            ("trackers", "create-source", [], "{}"),
            ("trackers", "update-session", ["--tracker-id", "trk_123"], "{}"),
            ("trackers", "update-source", ["--tracker-id", "trk_123"], "{}"),
            ("trackers", "disable", ["--tracker-id", "trk_123"], None),
            ("users", "create", [], "{}"),
            ("users", "update", ["--user-id", "usr_123"], "{}"),
            ("users", "delete", ["--user-id", "usr_123"], None),
        ]

        for family, api_cmd, argv, payload_json in write_cases:
            with self.subTest(command=f"{family} {api_cmd}"):
                with tempfile.TemporaryDirectory() as td:
                    env_path = Path(td) / ".env"
                    _write_env_file(env_path, base_url="https://api.callrail.test")

                    calls: list[tuple[str, str, dict[str, object] | None]] = []

                    def fake_request(self, method, url, **kwargs):  # noqa: ANN001
                        calls.append((method, str(url), dict(kwargs.get("json") or {})))
                        return _DummyResponse(status=200, url=str(url), payload={"ok": True})

                    buf = io.StringIO()
                    args = [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        family,
                        api_cmd,
                        *argv,
                    ]
                    if payload_json is not None:
                        args.extend(["--payload-json", payload_json])

                    with patch.dict(os.environ, {"CALLRAIL_DEFAULT_ACCOUNT_ID": "acc_default"}):
                        with patch("requests.Session.request", new=fake_request):
                            with redirect_stdout(buf):
                                rc = main(args)

                    payload = json.loads(buf.getvalue())
                    self.assertEqual(rc, 0)
                    self.assertEqual(calls, [])
                    self.assertEqual(payload.get("ok"), True)
                    self.assertEqual(payload.get("dry_run"), True)
                    self.assertIn("plan", payload)

    def test_write_contracts_match_official_methods_and_paths(self) -> None:
        write_contracts = [
            ("calls", "update", ["--call-id", "call_123"], "PUT", "https://api.callrail.test/v3/a/acc_default/calls/call_123.json", "{}"),
            ("tags", "update", ["--tag-id", "tag_123"], "PUT", "https://api.callrail.test/v3/a/acc_default/tags/tag_123.json", "{}"),
            ("companies", "update", ["--company-id", "cmp_123"], "PUT", "https://api.callrail.test/v3/a/acc_default/companies/cmp_123.json", "{}"),
            ("companies", "bulk-update", [], "POST", "https://api.callrail.test/v3/a/acc_default/companies/bulk_update.json", "{}"),
            ("companies", "disable", ["--company-id", "cmp_123"], "DELETE", "https://api.callrail.test/v3/a/acc_default/companies/cmp_123.json", None),
            ("form-submissions", "update", ["--submission-id", "sub_123"], "PUT", "https://api.callrail.test/v3/a/acc_default/form_submissions/sub_123.json", "{}"),
            ("form-submissions", "ignore-fields", [], "POST", "https://api.callrail.test/v3/a/acc_default/form_submissions/ignored_fields.json", "{}"),
            ("integrations", "update", ["--integration-id", "int_123"], "PUT", "https://api.callrail.test/v3/a/acc_default/integrations/int_123.json", '{"type":"custom","name":"safe"}'),
            ("integrations", "disable", ["--integration-id", "int_123"], "DELETE", "https://api.callrail.test/v3/a/acc_default/integrations/int_123.json", None),
            ("integration-filters", "update", ["--integration-filter-id", "ftr_123"], "PUT", "https://api.callrail.test/v3/a/acc_default/integration_triggers/ftr_123.json", "{}"),
            ("integration-filters", "delete", ["--integration-filter-id", "ftr_123"], "DELETE", "https://api.callrail.test/v3/a/acc_default/integration_triggers/ftr_123.json", None),
            ("notifications", "update", ["--notification-id", "n_123"], "PUT", "https://api.callrail.test/v3/a/acc_default/notifications/n_123.json", "{}"),
            ("notifications", "delete", ["--notification-id", "n_123"], "DELETE", "https://api.callrail.test/v3/a/acc_default/notifications/n_123.json", None),
            ("outbound-caller-ids", "delete", ["--caller-id", "cid_123"], "DELETE", "https://api.callrail.test/v3/a/acc_default/caller_ids/cid_123.json", None),
            ("sms-threads", "update", ["--thread-id", "thread_123"], "PUT", "https://api.callrail.test/v3/a/acc_default/sms-threads/thread_123.json", "{}"),
            ("summary-emails", "update", ["--summary-email-id", "sum_123"], "PUT", "https://api.callrail.test/v3/a/acc_default/summary_emails/sum_123.json", "{}"),
            ("summary-emails", "delete", ["--summary-email-id", "sum_123"], "DELETE", "https://api.callrail.test/v3/a/acc_default/summary_emails/sum_123.json", None),
            ("message-flows", "update", ["--message-flow-id", "flow_123"], "PUT", "https://api.callrail.test/v3/a/acc_default/message-flows/flow_123.json", "{}"),
            ("message-flows", "delete", ["--message-flow-id", "flow_123"], "DELETE", "https://api.callrail.test/v3/a/acc_default/message-flows/flow_123.json", None),
            ("trackers", "create-session", [], "POST", "https://api.callrail.test/v3/a/acc_default/trackers.json", "{}"),
            ("trackers", "create-source", [], "POST", "https://api.callrail.test/v3/a/acc_default/trackers.json", "{}"),
            ("trackers", "update-session", ["--tracker-id", "trk_123"], "PUT", "https://api.callrail.test/v3/a/acc_default/trackers/trk_123.json", "{}"),
            ("trackers", "update-source", ["--tracker-id", "trk_123"], "PUT", "https://api.callrail.test/v3/a/acc_default/trackers/trk_123.json", "{}"),
            ("trackers", "disable", ["--tracker-id", "trk_123"], "DELETE", "https://api.callrail.test/v3/a/acc_default/trackers/trk_123.json", None),
            ("users", "update", ["--user-id", "usr_123"], "PUT", "https://api.callrail.test/v3/a/acc_default/users/usr_123.json", "{}"),
            ("users", "delete", ["--user-id", "usr_123"], "DELETE", "https://api.callrail.test/v3/a/acc_default/users/usr_123.json", None),
        ]

        for family, api_cmd, argv, expected_method, expected_url, payload_json in write_contracts:
            with self.subTest(command=f"{family} {api_cmd}"):
                with tempfile.TemporaryDirectory() as td:
                    env_path = Path(td) / ".env"
                    _write_env_file(env_path, base_url="https://api.callrail.test")

                    calls: list[tuple[str, str, dict[str, object] | None]] = []

                    def fake_request(self, method: str, url: str, **kwargs: object) -> _DummyResponse:  # noqa: ANN001, ARG001
                        calls.append((method, str(url), dict(kwargs.get("json") or {})))
                        return _DummyResponse(status=201, url=str(url), payload={"ok": True})

                    buf = io.StringIO()
                    with patch.dict(os.environ, {"CALLRAIL_DEFAULT_ACCOUNT_ID": "acc_default"}):
                        with patch("requests.Session.request", new=fake_request):
                            with redirect_stdout(buf):
                                args = [
                                    "--apply",
                                    "--yes",
                                    "--ack-no-snapshot",
                                    "--output",
                                    "json",
                                    "--env-file",
                                    str(env_path),
                                    family,
                                    api_cmd,
                                    *argv,
                                ]
                                if payload_json is not None:
                                    args.extend(["--payload-json", payload_json])
                                rc = main(args)

                    payload = json.loads(buf.getvalue())
                    self.assertEqual(rc, 0)
                    self.assertEqual(payload.get("ok"), True)
                    self.assertEqual(payload.get("request", {}).get("method"), expected_method)
                    self.assertEqual(payload.get("request", {}).get("url"), expected_url)
                    self.assertEqual(len(calls), 1)
                    self.assertEqual(calls[0][0], expected_method)
                    self.assertEqual(calls[0][1], expected_url)
                    self.assertEqual(payload.get("response", {}).get("status"), 201)

    def test_read_query_params_are_forwarded_and_recorded(self) -> None:
        query_cases = [
            (
                "accounts",
                "list",
                ["--page", "3", "--search", "acme", "--hipaa-account", "true"],
                {
                    "page": "3",
                    "search": "acme",
                    "hipaa_account": "true",
                },
                "https://api.callrail.test/v3/a.json",
            ),
            (
                "calls",
                "list",
                ["--company-id", "cmp_123", "--tracker-id", "trk_1", "--tracker-id", "trk_2", "--page", "1"],
                {"company_id": "cmp_123", "tracker_id": ["trk_1", "trk_2"], "page": "1"},
                "https://api.callrail.test/v3/a/acc_default/calls.json",
            ),
            (
                "calls",
                "summary",
                ["--company-id", "cmp_123", "--group-by", "day", "--date-range", "last_7_days"],
                {"company_id": "cmp_123", "group_by": "day", "date_range": "last_7_days"},
                "https://api.callrail.test/v3/a/acc_default/calls/summary.json",
            ),
            (
                "calls",
                "timeseries",
                ["--company-id", "cmp_123", "--interval", "day", "--date-range", "last_7_days"],
                {"company_id": "cmp_123", "interval": "day", "date_range": "last_7_days"},
                "https://api.callrail.test/v3/a/acc_default/calls/timeseries.json",
            ),
            (
                "accounts",
                "get",
                ["--account-id", "acc_123", "--fields", "numeric_id"],
                {"fields": "numeric_id"},
                "https://api.callrail.test/v3/a/acc_123.json",
            ),
            (
                "calls",
                "get",
                ["--call-id", "call_123", "--fields", "milestones,keywords_spotted"],
                {"fields": ["milestones", "keywords_spotted"]},
                "https://api.callrail.test/v3/a/acc_default/calls/call_123.json",
            ),
            (
                "companies",
                "get",
                ["--company-id", "cmp_123", "--fields", "verified_caller_ids"],
                {"fields": "verified_caller_ids"},
                "https://api.callrail.test/v3/a/acc_default/companies/cmp_123.json",
            ),
            (
                "users",
                "list",
                ["--company-id", "cmp_123", "--page", "2", "--per-page", "50", "--sort", "email", "--order", "asc"],
                {"company_id": "cmp_123", "page": "2", "per_page": "50", "sort": "email", "order": "asc"},
                "https://api.callrail.test/v3/a/acc_default/users.json",
            ),
            (
                "leads",
                "list",
                ["--company-id", "cmp_123", "--page", "4", "--fields", "id,name", "--sort", "created_at"],
                {"company_id": "cmp_123", "page": "4", "fields": ["id", "name"], "sort": "created_at"},
                "https://api.callrail.test/v3/a/acc_default/leads.json",
            ),
            (
                "text-messages",
                "list",
                ["--company-id", "cmp_123", "--page", "5", "--search", "foo bar", "--fields", "id,conversation_id"],
                {"company_id": "cmp_123", "page": "5", "search": "foo bar", "fields": ["id", "conversation_id"]},
                "https://api.callrail.test/v3/a/acc_default/text-messages.json",
            ),
            (
                "form-submissions",
                "summary",
                [
                    "--company-id",
                    "cmp_123",
                    "--custom-form-ids",
                    "cf_1",
                    "--custom-form-ids",
                    "cf_2",
                    "--fields",
                    "id,name",
                    "--date-range",
                    "last_7_days",
                ],
                {
                    "company_id": "cmp_123",
                    "custom_form_ids": ["cf_1", "cf_2"],
                    "fields": ["id", "name"],
                    "date_range": "last_7_days",
                },
                "https://api.callrail.test/v3/a/acc_default/forms/summary.json",
            ),
            (
                "integrations",
                "list",
                ["--company-id", "cmp_123", "--page", "7", "--per-page", "25", "--fields", "signing_key"],
                {"company_id": "cmp_123", "page": "7", "per_page": "25", "fields": "signing_key"},
                "https://api.callrail.test/v3/a/acc_default/integrations.json",
            ),
            (
                "integrations",
                "get",
                ["--integration-id", "123", "--fields", "signing_key"],
                {"fields": "signing_key"},
                "https://api.callrail.test/v3/a/acc_default/integrations/123.json",
            ),
            (
                "notifications",
                "list",
                ["--page", "2", "--per-page", "10", "--notification-type", "first_time_call"],
                {"page": "2", "per_page": "10", "notification_type": "first_time_call"},
                "https://api.callrail.test/v3/a/acc_default/notifications.json",
            ),
            (
                "page-views",
                "list",
                ["--call-id", "call_123", "--page", "2", "--per-page", "25", "--time-zone", "America/Los_Angeles"],
                {"page": "2", "per_page": "25", "time_zone": "America/Los_Angeles"},
                "https://api.callrail.test/v3/a/acc_default/calls/call_123/page_views.json",
            ),
            (
                "sms-threads",
                "get",
                ["--thread-id", "thread_123", "--page", "2", "--per-page", "25", "--with-msg-errors", "true", "--fields", "messages"],
                {"page": "2", "per_page": "25", "with_msg_errors": "true", "fields": "messages"},
                "https://api.callrail.test/v3/a/acc_default/sms-threads/thread_123.json",
            ),
            (
                "summary-emails",
                "list",
                ["--page", "3", "--frequency", "weekly", "--company-id", "cmp_123"],
                {"page": "3", "frequency": "weekly", "company_id": "cmp_123"},
                "https://api.callrail.test/v3/a/acc_default/summary_emails",
            ),
            (
                "text-messages",
                "get",
                ["--conversation-id", "conv_123", "--fields", "lead_status,source"],
                {"fields": ["lead_status", "source"]},
                "https://api.callrail.test/v3/a/acc_default/text-messages/conv_123.json",
            ),
            (
                "message-flows",
                "list",
                ["--page", "2", "--per-page", "10", "--company-id", "cmp_123"],
                {"page": "2", "per_page": "10", "company_id": "cmp_123"},
                "https://api.callrail.test/v3/a/acc_default/message-flows.json",
            ),
            (
                "trackers",
                "get",
                ["--tracker-id", "trk_123", "--fields", "campaign_name,swap_targets"],
                {"fields": ["campaign_name", "swap_targets"]},
                "https://api.callrail.test/v3/a/acc_default/trackers/trk_123.json",
            ),
        ]

        for family, api_cmd, argv, expected_params, expected_url in query_cases:
            with self.subTest(command=f"{family} {api_cmd}"):
                with tempfile.TemporaryDirectory() as td:
                    env_path = Path(td) / ".env"
                    _write_env_file(env_path, base_url="https://api.callrail.test")

                    captured: dict[str, object] = {}

                    def fake_request(self, method: str, url: str, **kwargs: object) -> _DummyResponse:  # noqa: ANN001, ARG001
                        captured["method"] = method
                        captured["url"] = str(url)
                        captured["params"] = dict(kwargs.get("params") or {})
                        return _DummyResponse(status=200, url=str(url), payload={"ok": True})

                    buf = io.StringIO()
                    with patch.dict(os.environ, {"CALLRAIL_DEFAULT_ACCOUNT_ID": "acc_default"}):
                        with patch("requests.Session.request", new=fake_request):
                            with redirect_stdout(buf):
                                rc = main(
                                    [
                                        "--output",
                                        "json",
                                        "--env-file",
                                        str(env_path),
                                        family,
                                        api_cmd,
                                        *argv,
                                    ]
                                )

                    payload = json.loads(buf.getvalue())
                    self.assertEqual(rc, 0)
                    self.assertEqual(payload.get("ok"), True)
                    self.assertEqual(payload.get("request", {}).get("url"), expected_url)
                    self.assertEqual(payload.get("request", {}).get("params"), expected_params)
                    self.assertEqual(payload.get("response", {}).get("status"), 200)
                    self.assertEqual(captured.get("url"), expected_url)
                    self.assertEqual(captured.get("params"), expected_params)

    def test_required_company_id_query_flags_are_enforced(self) -> None:
        required_query_cases = [
            ("integrations", "list", "Integrations list"),
            ("integration-filters", "list", "Integration-filters list"),
            ("outbound-caller-ids", "list", "Outbound-caller-ids list"),
        ]
        for family, api_cmd, label in required_query_cases:
            with self.subTest(command=label):
                with tempfile.TemporaryDirectory() as td:
                    env_path = Path(td) / ".env"
                    _write_env_file(env_path, base_url="https://api.callrail.test")

                    captured: dict[str, object] = {}

                    def fake_request(self, method: str, url: str, **kwargs: object) -> _DummyResponse:  # noqa: ANN001, ARG001
                        captured["method"] = method
                        captured["url"] = str(url)
                        return _DummyResponse(status=200, url=str(url), payload={"ok": True})

                    buf = io.StringIO()
                    with patch.dict(os.environ, {"CALLRAIL_DEFAULT_ACCOUNT_ID": "acc_default"}):
                        with patch("requests.Session.request", new=fake_request):
                            with redirect_stdout(buf):
                                rc = main(
                                    [
                                        "--output",
                                        "json",
                                        "--env-file",
                                        str(env_path),
                                        family,
                                        api_cmd,
                                    ]
                                )

                    payload = json.loads(buf.getvalue())
                    self.assertEqual(rc, 1)
                    self.assertEqual(payload.get("ok"), False)
                    self.assertIn("requires --company-id", str(payload.get("error")))
                    self.assertNotIn("response", payload)
                    self.assertEqual(captured, {})

    def test_removed_reference_commands_are_not_shipped_subcommands(self) -> None:
        removed_cases = [
            ("tags", "available-colors"),
            ("integrations", "configure"),
            ("message-flows", "configure"),
            ("trackers", "request-number"),
            ("trackers", "configure-call-flows"),
            ("trackers", "session-call-sources"),
            ("trackers", "source-call-sources"),
            ("users", "roles"),
        ]

        for family, api_cmd in removed_cases:
            with self.subTest(command=f"{family} {api_cmd}"):
                with tempfile.TemporaryDirectory() as td:
                    env_path = Path(td) / ".env"
                    _write_env_file(env_path, base_url="https://api.callrail.test")

                    calls: list[tuple[str, str]] = []

                    def fake_request(self, method, url, **kwargs):  # noqa: ANN001
                        calls.append((method, str(url)))
                        return _DummyResponse(status=200, url=str(url), payload={"ok": True})

                    buf = io.StringIO()
                    with patch("requests.Session.request", new=fake_request):
                        with redirect_stdout(buf):
                            rc = main(["--output", "json", "--env-file", str(env_path), family, api_cmd])

                    payload = json.loads(buf.getvalue())
                    self.assertEqual(rc, 1)
                    self.assertEqual(calls, [])
                    self.assertEqual(payload.get("ok"), False)
                    self.assertIn("invalid choice", str(payload.get("error")))

    def test_auth_check_calls_accounts_endpoint_and_has_no_oauth_status_block(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            _write_env_file(env_path, base_url="https://api.callrail.test")

            captured: dict[str, object] = {}

            def fake_request(self, method, url, **kwargs):  # noqa: ANN001
                captured["method"] = method
                captured["url"] = str(url)
                captured["headers"] = dict(kwargs.get("headers") or {})
                return _DummyResponse(
                    status=200,
                    url=str(url),
                    payload={"accounts": [{"id": "acc_test", "name": "Primary"}]},
                )

            buf = io.StringIO()
            with patch("requests.Session.request", new=fake_request):
                with redirect_stdout(buf):
                    rc = main(["--output", "json", "--env-file", str(env_path), "auth", "check"])

            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            request = payload["request"]
            response = payload["response"]
            self.assertEqual(payload.get("ok"), True)
            self.assertTrue(payload.get("env_token_present"))
            self.assertNotIn("oauth_token", payload)
            self.assertEqual(request["method"], captured.get("method"))
            self.assertEqual(request["url"], captured.get("url"))
            self.assertEqual(request["url"], "https://api.callrail.test/v3/a.json")
            self.assertEqual(response["status"], 200)
            sent_headers = {str(k).lower(): str(v) for k, v in dict(captured.get("headers") or {}).items()}
            self.assertEqual(sent_headers.get("authorization"), "Token token=tok_test")
            shown_headers = {str(k).lower(): str(v) for k, v in dict(request.get("headers") or {}).items()}
            self.assertEqual(shown_headers.get("authorization"), "***REDACTED***")

    def test_accounts_list_calls_real_v3_a_json_with_authorization_and_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            _write_env_file(env_path, base_url="https://api.callrail.test")

            captured: dict[str, object] = {}

            def fake_request(self, method, url, **kwargs):  # noqa: ANN001
                captured["method"] = method
                captured["url"] = str(url)
                captured["headers"] = dict(kwargs.get("headers") or {})
                return _DummyResponse(
                    status=200,
                    url=str(url),
                    payload={"accounts": [{"id": "acc_test", "name": "Primary"}]},
                )

            buf = io.StringIO()
            with patch("requests.Session.request", new=fake_request):
                with redirect_stdout(buf):
                    rc = main(["--output", "json", "--env-file", str(env_path), "accounts", "list"])

            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            request = payload["request"]
            response = payload["response"]
            self.assertEqual(request["method"], captured.get("method"))
            self.assertEqual(request["url"], captured.get("url"))
            self.assertEqual(request["url"], "https://api.callrail.test/v3/a.json")
            self.assertEqual(response["status"], 200)
            sent_headers = {str(k).lower(): str(v) for k, v in dict(captured.get("headers") or {}).items()}
            self.assertEqual(sent_headers.get("authorization"), "Token token=tok_test")
            shown_headers = {str(k).lower(): str(v) for k, v in dict(request.get("headers") or {}).items()}
            self.assertEqual(shown_headers.get("authorization"), "***REDACTED***")

    def test_calls_get_uses_default_account_id_env_when_not_explicit(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            _write_env_file(env_path, base_url="https://api.callrail.test/")

            captured: dict[str, object] = {}

            def fake_request(self, method, url, **kwargs):  # noqa: ANN001
                captured["method"] = method
                captured["url"] = str(url)
                captured["headers"] = dict(kwargs.get("headers") or {})
                return _DummyResponse(status=200, url=str(url), payload={"id": "call_abc", "duration": 42})

            buf = io.StringIO()
            with patch.dict(os.environ, {"CALLRAIL_DEFAULT_ACCOUNT_ID": "acc_default"}):
                with patch("requests.Session.request", new=fake_request):
                    with redirect_stdout(buf):
                        rc = main(
                            [
                                "--output",
                                "json",
                                "--env-file",
                                str(env_path),
                                "calls",
                                "get",
                                "--call-id",
                                "call_abc",
                            ]
                        )

            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            request = payload["request"]
            response = payload["response"]
            self.assertEqual(request["method"], captured.get("method"))
            self.assertEqual(request["url"], captured.get("url"))
            self.assertEqual(request["url"], "https://api.callrail.test/v3/a/acc_default/calls/call_abc.json")
            self.assertEqual(response["status"], 200)
            sent_headers = {str(k).lower(): str(v) for k, v in dict(captured.get("headers") or {}).items()}
            self.assertEqual(sent_headers.get("authorization"), "Token token=tok_test")
            shown_headers = {str(k).lower(): str(v) for k, v in dict(request.get("headers") or {}).items()}
            self.assertEqual(shown_headers.get("authorization"), "***REDACTED***")

    def test_calls_create_outbound_without_apply_is_dry_run_plan_and_no_http(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            _write_env_file(env_path, base_url="https://api.callrail.test")

            calls = []

            def fake_request(self, method, url, **kwargs):  # noqa: ANN001
                calls.append((method, str(url), dict(kwargs.get("headers") or {}), kwargs.get("json")))
                return _DummyResponse(status=200, url=str(url), payload={"ok": True})

            payload_json = json.dumps({"to": {"number": "+15551234567"}, "from": {"number": "+15559876543"}})

            buf = io.StringIO()
            with patch("requests.Session.request", new=fake_request):
                with redirect_stdout(buf):
                    with patch.dict(os.environ, {"CALLRAIL_DEFAULT_ACCOUNT_ID": "acc_default"}):
                        rc = main(
                            [
                                "--output",
                                "json",
                                "--env-file",
                                str(env_path),
                                "calls",
                                "create-outbound",
                                "--payload-json",
                                payload_json,
                            ]
                        )

            self.assertEqual(calls, [])
            self.assertEqual(rc, 0, buf.getvalue())
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload.get("ok"), True)
            self.assertEqual(payload.get("dry_run"), True)
            self.assertIn("plan", payload)
