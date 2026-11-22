from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

import requests

from contentsquare_safe_agent_cli.cli import main


def run_cli(argv: list[str]) -> tuple[int, dict]:
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = main(argv)
    return rc, json.loads(buf.getvalue())


class ContentsquareCommandTests(unittest.TestCase):
    def test_write_dry_run_creates_plan_without_auth(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            body = Path(td) / "body.json"
            plan = Path(td) / "plan.json"
            env = Path(td) / ".env"
            body.write_text('{"projectId": 123, "name": "daily sessions"}', encoding="utf-8")
            env.write_text(
                "CONTENTSQUARE_CLIENT_ID=id\nCONTENTSQUARE_CLIENT_SECRET=secret\n",
                encoding="utf-8",
            )
            rc, payload = run_cli(
                [
                    "--env-file",
                    str(env),
                    "--plan-out",
                    str(plan),
                    "data-export",
                    "create-job",
                    "--body-json",
                    str(body),
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["dry_run"])
            self.assertTrue(plan.exists())
            self.assertEqual(payload["plan"]["operation"], "create-export-job")

    def test_live_write_requires_reviewed_plan(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env = Path(td) / ".env"
            env.write_text(
                "CONTENTSQUARE_CLIENT_ID=id\nCONTENTSQUARE_CLIENT_SECRET=secret\n",
                encoding="utf-8",
            )
            rc, payload = run_cli(
                [
                    "--env-file",
                    str(env),
                    "--apply",
                    "--yes",
                    "data-export",
                    "create-job",
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["refused"])

    def test_read_command_calls_fixed_endpoint(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env = Path(td) / ".env"
            env.write_text(
                "CONTENTSQUARE_CLIENT_ID=id\nCONTENTSQUARE_CLIENT_SECRET=secret\nCONTENTSQUARE_API_BASE_URL=https://api.cs.example\n",
                encoding="utf-8",
            )
            with mock.patch(
                "contentsquare_safe_agent_cli.commands.contentsquare.ContentsquareClient"
            ) as client_cls:
                client_cls.return_value.request.return_value = {"items": []}
                rc, payload = run_cli(
                    [
                        "--env-file",
                        str(env),
                        "metrics",
                        "site",
                        "bounce-rate",
                        "--project-id",
                        "42",
                        "--start-date",
                        "2026-06-01",
                        "--end-date",
                        "2026-06-07",
                        "--segment-id",
                        "100",
                        "--goal-id",
                        "200",
                        "--period",
                        "daily",
                    ]
                )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            client_cls.return_value.request.assert_called_once()
            _, path = client_cls.return_value.request.call_args.args
            self.assertEqual(path, "/v1/metrics/site/bounce-rate")
            params = client_cls.return_value.request.call_args.kwargs["params"]
            self.assertEqual(
                params,
                {
                    "projectId": "42",
                    "startDate": "2026-06-01",
                    "endDate": "2026-06-07",
                    "segmentIds": "100",
                    "goalId": "200",
                    "period": "daily",
                },
            )
            self.assertNotIn("project-id", params)
            self.assertNotIn("start-date", params)
            self.assertNotIn("segment-id", params)

    def test_data_export_list_jobs_uses_documented_filter_params(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env = Path(td) / ".env"
            env.write_text(
                "CONTENTSQUARE_CLIENT_ID=id\nCONTENTSQUARE_CLIENT_SECRET=secret\nCONTENTSQUARE_API_BASE_URL=https://api.cs.example\n",
                encoding="utf-8",
            )
            with mock.patch(
                "contentsquare_safe_agent_cli.commands.contentsquare.ContentsquareClient"
            ) as client_cls:
                client_cls.return_value.request.return_value = {"payload": []}
                rc, payload = run_cli(
                    [
                        "--env-file",
                        str(env),
                        "data-export",
                        "list-jobs",
                        "--state",
                        "completed",
                        "--order",
                        "ASC",
                        "--format",
                        "CSV",
                        "--frequency",
                        "daily",
                        "--scope-filter",
                        "views",
                        "--page",
                        "3",
                        "--limit",
                        "50",
                    ]
                )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            params = client_cls.return_value.request.call_args.kwargs["params"]
            self.assertEqual(
                params,
                {
                    "state": "completed",
                    "order": "ASC",
                    "format": "CSV",
                    "frequency": "daily",
                    "scope": "views",
                    "page": 3,
                    "limit": 50,
                },
            )

    def test_dynamic_var_keys_uses_documented_from_to_params(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env = Path(td) / ".env"
            env.write_text(
                "CONTENTSQUARE_CLIENT_ID=id\nCONTENTSQUARE_CLIENT_SECRET=secret\nCONTENTSQUARE_API_BASE_URL=https://api.cs.example\n",
                encoding="utf-8",
            )
            with mock.patch(
                "contentsquare_safe_agent_cli.commands.contentsquare.ContentsquareClient"
            ) as client_cls:
                client_cls.return_value.request.return_value = {"payload": []}
                rc, payload = run_cli(
                    [
                        "--env-file",
                        str(env),
                        "data-export",
                        "dynamic-var-keys",
                        "--from",
                        "2026-06-01T00:00:00Z",
                        "--to",
                        "2026-06-07T00:00:00Z",
                    ]
                )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            params = client_cls.return_value.request.call_args.kwargs["params"]
            self.assertEqual(params, {"from": "2026-06-01T00:00:00Z", "to": "2026-06-07T00:00:00Z"})

    def test_object_read_uses_documented_ids_param(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env = Path(td) / ".env"
            env.write_text(
                "CONTENTSQUARE_CLIENT_ID=id\nCONTENTSQUARE_CLIENT_SECRET=secret\nCONTENTSQUARE_API_BASE_URL=https://api.cs.example\n",
                encoding="utf-8",
            )
            with mock.patch(
                "contentsquare_safe_agent_cli.commands.contentsquare.ContentsquareClient"
            ) as client_cls:
                client_cls.return_value.request.return_value = {"payload": []}
                rc, payload = run_cli(
                    [
                        "--env-file",
                        str(env),
                        "metrics",
                        "segments",
                        "--project-id",
                        "42",
                        "--ids",
                        "10,11",
                    ]
                )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            params = client_cls.return_value.request.call_args.kwargs["params"]
            self.assertEqual(params, {"projectId": "42", "ids": "10,11"})

    def test_segment_ids_alias_and_device_use_documented_params(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env = Path(td) / ".env"
            env.write_text(
                "CONTENTSQUARE_CLIENT_ID=id\nCONTENTSQUARE_CLIENT_SECRET=secret\nCONTENTSQUARE_API_BASE_URL=https://api.cs.example\n",
                encoding="utf-8",
            )
            with mock.patch(
                "contentsquare_safe_agent_cli.commands.contentsquare.ContentsquareClient"
            ) as client_cls:
                client_cls.return_value.request.return_value = {"payload": {}}
                rc, payload = run_cli(
                    [
                        "--env-file",
                        str(env),
                        "metrics",
                        "site",
                        "visits",
                        "--project-id",
                        "42",
                        "--start-date",
                        "2026-06-01",
                        "--end-date",
                        "2026-06-07",
                        "--segment-ids",
                        "100,101",
                        "--device",
                        "desktop",
                    ]
                )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            params = client_cls.return_value.request.call_args.kwargs["params"]
            self.assertEqual(
                params,
                {
                    "projectId": "42",
                    "startDate": "2026-06-01",
                    "endDate": "2026-06-07",
                    "segmentIds": "100,101",
                    "device": "desktop",
                },
            )

    def test_download_run_file_uses_nested_file_url(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env = Path(td) / ".env"
            output = Path(td) / "part.jsonl"
            env.write_text(
                "CONTENTSQUARE_CLIENT_ID=id\nCONTENTSQUARE_CLIENT_SECRET=secret\nCONTENTSQUARE_API_BASE_URL=https://api.cs.example\n",
                encoding="utf-8",
            )
            with mock.patch(
                "contentsquare_safe_agent_cli.commands.contentsquare.ContentsquareClient"
            ) as client_cls, mock.patch("requests.get") as get:
                client_cls.return_value.request.return_value = {
                    "payload": {
                        "jobRunId": 77,
                        "files": [
                            {"partId": 9, "url": "https://download.example/part-9", "expirationDate": "2026-06-30T00:00:00Z"}
                        ],
                    }
                }
                get.return_value.__enter__.return_value = _response(200, b"ok\n")
                rc, payload = run_cli(
                    [
                        "--env-file",
                        str(env),
                        "data-export",
                        "download-run-file",
                        "--job-id",
                        "123",
                        "--run-id-value",
                        "77",
                        "--output-file",
                        str(output),
                    ]
                )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            get.assert_called_once_with("https://download.example/part-9", timeout=30.0, stream=True)
            self.assertEqual(output.read_bytes(), b"ok\n")
            self.assertEqual(payload["file"]["part_id"], 9)

    def test_download_run_file_requires_choice_for_multiple_files(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env = Path(td) / ".env"
            output = Path(td) / "part.jsonl"
            env.write_text(
                "CONTENTSQUARE_CLIENT_ID=id\nCONTENTSQUARE_CLIENT_SECRET=secret\nCONTENTSQUARE_API_BASE_URL=https://api.cs.example\n",
                encoding="utf-8",
            )
            with mock.patch(
                "contentsquare_safe_agent_cli.commands.contentsquare.ContentsquareClient"
            ) as client_cls, mock.patch("requests.get") as get:
                client_cls.return_value.request.return_value = {
                    "payload": {
                        "files": [
                            {"partId": 1, "url": "https://download.example/part-1"},
                            {"partId": 2, "url": "https://download.example/part-2"},
                        ]
                    }
                }
                rc, payload = run_cli(
                    [
                        "--env-file",
                        str(env),
                        "data-export",
                        "download-run-file",
                        "--job-id",
                        "123",
                        "--run-id-value",
                        "77",
                        "--output-file",
                        str(output),
                    ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["refused"])
            self.assertIn("multiple files", payload["reasons"][0])
            get.assert_not_called()

    def test_download_run_file_can_choose_file_index(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env = Path(td) / ".env"
            output = Path(td) / "part.jsonl"
            env.write_text(
                "CONTENTSQUARE_CLIENT_ID=id\nCONTENTSQUARE_CLIENT_SECRET=secret\nCONTENTSQUARE_API_BASE_URL=https://api.cs.example\n",
                encoding="utf-8",
            )
            with mock.patch(
                "contentsquare_safe_agent_cli.commands.contentsquare.ContentsquareClient"
            ) as client_cls, mock.patch("requests.get") as get:
                client_cls.return_value.request.return_value = {
                    "payload": {
                        "files": [
                            {"partId": 1, "url": "https://download.example/part-1"},
                            {"partId": 2, "url": "https://download.example/part-2"},
                        ]
                    }
                }
                get.return_value.__enter__.return_value = _response(200, b"second\n")
                rc, payload = run_cli(
                    [
                        "--env-file",
                        str(env),
                        "data-export",
                        "download-run-file",
                        "--job-id",
                        "123",
                        "--run-id-value",
                        "77",
                        "--file-index",
                        "1",
                        "--output-file",
                        str(output),
                    ]
                )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            get.assert_called_once_with("https://download.example/part-2", timeout=30.0, stream=True)
            self.assertEqual(payload["file"]["file_index"], 1)

    def test_download_run_file_can_choose_part_id(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env = Path(td) / ".env"
            output = Path(td) / "part.jsonl"
            env.write_text(
                "CONTENTSQUARE_CLIENT_ID=id\nCONTENTSQUARE_CLIENT_SECRET=secret\nCONTENTSQUARE_API_BASE_URL=https://api.cs.example\n",
                encoding="utf-8",
            )
            with mock.patch(
                "contentsquare_safe_agent_cli.commands.contentsquare.ContentsquareClient"
            ) as client_cls, mock.patch("requests.get") as get:
                client_cls.return_value.request.return_value = {
                    "payload": {
                        "files": [
                            {"partId": 1, "url": "https://download.example/part-1"},
                            {"partId": 2, "url": "https://download.example/part-2"},
                        ]
                    }
                }
                get.return_value.__enter__.return_value = _response(200, b"second\n")
                rc, payload = run_cli(
                    [
                        "--env-file",
                        str(env),
                        "data-export",
                        "download-run-file",
                        "--job-id",
                        "123",
                        "--run-id-value",
                        "77",
                        "--part-id",
                        "2",
                        "--output-file",
                        str(output),
                    ]
                )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            get.assert_called_once_with("https://download.example/part-2", timeout=30.0, stream=True)
            self.assertEqual(payload["file"]["part_id"], 2)

    def test_download_run_file_rejects_selected_file_without_url(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env = Path(td) / ".env"
            output = Path(td) / "part.jsonl"
            env.write_text(
                "CONTENTSQUARE_CLIENT_ID=id\nCONTENTSQUARE_CLIENT_SECRET=secret\nCONTENTSQUARE_API_BASE_URL=https://api.cs.example\n",
                encoding="utf-8",
            )
            with mock.patch(
                "contentsquare_safe_agent_cli.commands.contentsquare.ContentsquareClient"
            ) as client_cls, mock.patch("requests.get") as get:
                client_cls.return_value.request.return_value = {
                    "payload": {
                        "files": [
                            {"partId": 1, "expirationDate": "2026-06-30T00:00:00Z"}
                        ]
                    }
                }
                rc, payload = run_cli(
                    [
                        "--env-file",
                        str(env),
                        "data-export",
                        "download-run-file",
                        "--job-id",
                        "123",
                        "--run-id-value",
                        "77",
                        "--output-file",
                        str(output),
                    ]
                )
            self.assertEqual(rc, 1)
            self.assertIn("files[].url", payload["error"])
            get.assert_not_called()


def _response(status: int, body: bytes, headers: dict[str, str] | None = None) -> requests.Response:
    response = requests.Response()
    response.status_code = status
    response.url = "https://example.invalid/fixture"
    response.headers.update(headers or {})
    response._content = body
    response._content_consumed = True
    return response


class ReviewedChangeTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        env = self.root / "settings file.env"
        env.write_text(
            "CONTENTSQUARE_CLIENT_ID=test-client\n"
            "CONTENTSQUARE_CLIENT_SECRET=test-secret\n"
            "CONTENTSQUARE_PROJECT_ID=100\n",
            encoding="utf-8",
        )
        self.env = env
        self.args = ["--no-artifacts", "--env-file", str(env)]
        self.plan = self.root / "plan.json"
        self.receipt = self.root / "receipt.json"
        self.body = self.root / "job.json"
        self.body.write_text('{"name": "sessions", "format": "CSV"}', encoding="utf-8")
        self.apply = [
            "--plan-in", str(self.plan), "--apply", "--yes",
            "--receipt-out", str(self.receipt),
        ]
        self.create = ["data-export", "create-job"]

    def preview(self, *flags: str) -> dict:
        code, result = run_cli(self.args + ["--plan-out", str(self.plan)] + self.create + ["--body-json", str(self.body), *flags])
        self.assertEqual(code, 0)
        return result["plan"]

    def test_apply_checks_project_credentials_command_query_and_body_before_auth(self) -> None:
        with mock.patch("requests.Session.request") as request:
            preview = self.preview()
            self.assertEqual(preview["selector"]["oauth_project_id"], "100")
            self.assertNotIn("test-secret", self.plan.read_text())
            for flags, command in [
                (["--oauth-project-id", "200"], self.create),
                ([], self.create + ["--scope", "metrics"]),
                ([], self.create + ["--project-id", "300"]),
                (["--ack-no-snapshot"], ["speed-analysis", "event-create"]),
            ]:
                with self.subTest(flags=flags, command=command):
                    _, result = run_cli(self.args + self.apply + flags + command)
                    self.assertTrue(result["refused"])
            self.body.write_text('{"name": "some other export"}', encoding="utf-8")
            _, result = run_cli(self.args + self.apply + self.create + ["--body-json", str(self.body)])
            self.assertTrue(result["refused"])
            self.env.write_text(self.env.read_text().replace("test-secret", "different-secret"), encoding="utf-8")
            _, result = run_cli(self.args + self.apply + self.create)
            self.assertTrue(result["refused"])
            request.assert_not_called()

    def test_changed_or_old_plan_needs_a_new_preview(self) -> None:
        preview = self.preview()
        with mock.patch("requests.Session.request") as request:
            for plan in ({"proposed_changes": {}}, {**preview, "proposed_changes": {"name": "edited"}}):
                self.plan.write_text(json.dumps(plan), encoding="utf-8")
                _, result = run_cli(self.args + self.apply + self.create)
                self.assertTrue(result["refused"])
            request.assert_not_called()

    def test_matching_plan_uses_saved_body_and_gives_export_follow_up(self) -> None:
        preview = self.preview()
        replies = [
            _response(200, b'{"access_token": "test-token"}'),
            _response(200, b'{"success": true, "payload": {"jobId": 13}}'),
        ]
        with mock.patch("requests.Session.request", side_effect=replies) as request:
            code, result = run_cli(self.args + self.apply + self.create)
        self.assertEqual(code, 0)
        self.assertEqual(request.call_args.kwargs["json"], preview["proposed_changes"])
        self.assertFalse(request.call_args.kwargs["allow_redirects"])
        receipt = json.loads(self.receipt.read_text())
        self.assertEqual(receipt["outcome"], "accepted")
        self.assertIsNone(result["verified"])
        self.assertEqual(
            receipt["follow_up"],
            f"contentsquare-safe-cli --env-file '{self.env}' data-export list-runs --job-id 13",
        )

    def test_write_sends_once_and_saves_an_uncertain_receipt_when_reply_is_lost(self) -> None:
        self.preview()
        for reply in (
            _response(503, b"unavailable"),
            _response(200, b"<html>unreadable response</html>"),
            requests.exceptions.Timeout(),
        ):
            with self.subTest(reply=reply), mock.patch(
                "requests.Session.request",
                side_effect=[_response(200, b'{"access_token": "test-token"}'), reply],
            ) as request, mock.patch("contentsquare_safe_agent_cli.http.time.sleep") as sleep:
                code, result = run_cli(self.args + self.apply + self.create)
                self.assertEqual(request.call_count, 2)
                sleep.assert_not_called()
            self.assertEqual(code, 1)
            self.assertIsNone(result["changed"])
            receipt = json.loads(self.receipt.read_text())
            self.assertEqual(receipt["outcome"], "uncertain")
            self.assertIn("data-export list-jobs", receipt["follow_up"])

    def test_speed_report_read_can_retry_and_reports_provider_rejection(self) -> None:
        replies = [
            _response(200, b'{"access_token": "test-token"}'),
            _response(503, b"unavailable"),
            _response(200, b'{"success": false, "payload": null}'),
        ]
        with mock.patch("requests.Session.request", side_effect=replies) as request, mock.patch(
            "contentsquare_safe_agent_cli.http.time.sleep"
        ) as sleep:
            code, result = run_cli(self.args + ["speed-analysis", "analysis-report"])
        self.assertEqual(request.call_count, 3)
        sleep.assert_called_once()
        self.assertEqual(code, 1)
        self.assertFalse(result["verified"])

    def test_enrichment_can_accept_a_status_only_reply(self) -> None:
        command = ["enrichment", "send-batch", "--integration-id", "12"]
        code, _ = run_cli(self.args + ["--plan-out", str(self.plan)] + command)
        self.assertEqual(code, 0)
        with mock.patch(
            "requests.Session.request",
            side_effect=[_response(200, b'{"access_token": "test-token"}'), _response(200, b"")],
        ):
            code, result = run_cli(self.args + self.apply + ["--ack-no-snapshot"] + command)
        self.assertEqual(code, 0)
        self.assertEqual(result["receipt"]["outcome"], "accepted")
        self.assertIsNone(result["verified"])

    def test_export_run_reports_readiness_and_bad_download_preserves_previous_file(self) -> None:
        run = {
            "state": "RUNNING",
            "files": [],
        }
        run_args = ["--job-id", "13", "--run-id-value", "29"]
        output = self.root / "export.csv"
        output.write_bytes(b"older export")
        with mock.patch(
            "contentsquare_safe_agent_cli.commands.contentsquare.ContentsquareClient"
        ) as client, mock.patch("requests.get") as get:
            client.return_value.request.return_value = {"success": True, "payload": run}
            _, pending = run_cli(self.args + ["data-export", "get-run"] + run_args)
            self.assertEqual(pending["export_run"], {"state": "RUNNING", "ready_to_download": False})
            run["state"] = "SUCCESS"
            run["files"] = [{"url": "https://example.invalid/export.csv", "partId": 0}]
            _, complete = run_cli(self.args + ["data-export", "get-run"] + run_args)
            self.assertTrue(complete["export_run"]["ready_to_download"])
            for reply in (
                _response(200, b""),
                _response(200, b"short", {"Content-Length": "10"}),
                _response(200, b"<html>expired</html>"),
            ):
                get.return_value = reply
                code, result = run_cli(
                    self.args + ["data-export", "download-run-file", "--output-file", str(output), "--overwrite"] + run_args
                )
                self.assertEqual(code, 1)
                self.assertFalse(result["ok"])
                self.assertEqual(output.read_bytes(), b"older export")
            get.return_value = _response(200, b"session_id\n123\n", {"Content-Length": "15"})
            code, result = run_cli(
                self.args + ["data-export", "download-run-file", "--output-file", str(output), "--overwrite"] + run_args
            )
            self.assertEqual(code, 0)
            self.assertTrue(result["verified"])
            self.assertEqual(output.read_bytes(), b"session_id\n123\n")


if __name__ == "__main__":
    unittest.main()
