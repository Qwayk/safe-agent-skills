from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

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
                get.return_value.status_code = 200
                get.return_value.content = b"ok\n"
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
            get.assert_called_once_with("https://download.example/part-9", timeout=30.0)
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
                get.return_value.status_code = 200
                get.return_value.content = b"second\n"
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
            get.assert_called_once_with("https://download.example/part-2", timeout=30.0)
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
                get.return_value.status_code = 200
                get.return_value.content = b"second\n"
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
            get.assert_called_once_with("https://download.example/part-2", timeout=30.0)
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


if __name__ == "__main__":
    unittest.main()
