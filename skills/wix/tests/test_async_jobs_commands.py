from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import async_jobs
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def __init__(self) -> None:
        self.writes: list[tuple[str, dict]] = []

    def write(self, action: str, payload: dict) -> None:
        self.writes.append((action, payload))


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestAsyncJobsParser(unittest.TestCase):
    def test_parser_recognizes_async_jobs_commands(self) -> None:
        parser = build_parser()

        get_args = parser.parse_args(["async-jobs", "get", "--job-id", "job-1"])
        self.assertEqual(get_args.async_jobs_cmd, "get")
        self.assertFalse(get_args.write_capable)
        self.assertIs(get_args.func, async_jobs.cmd_async_jobs_get)

        list_items_args = parser.parse_args(["async-jobs", "list-items", "--job-id", "job-1"])
        self.assertEqual(list_items_args.async_jobs_cmd, "list-items")
        self.assertFalse(list_items_args.write_capable)
        self.assertIs(list_items_args.func, async_jobs.cmd_async_jobs_list_items)


class TestAsyncJobsCommands(unittest.TestCase):
    def _ctx(self) -> dict:
        cfg = SimpleNamespace(
            base_url="https://www.wixapis.com",
            timeout_s=30.0,
            app_id=None,
            app_secret=None,
            instance_id=None,
            access_token="token-abc",
            has_official_app_auth=False,
        )
        return {
            "cfg": cfg,
            "env_file": "/tmp/.env",
            "verbose": False,
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
        }

    @patch("wix_safe_agent_cli.commands.async_jobs.HttpClient")
    def test_get_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"job": {"id": "job-1"}})
        args = SimpleNamespace(job_id="job-1")
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = async_jobs.cmd_async_jobs_get(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["method"], "async-jobs.get")
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(payload["request"]["path"], "/async-jobs/v1/async-jobs/job-1")
        self.assertEqual(payload["response"]["job"]["id"], "job-1")

        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["headers"]["Authorization"], "token-abc")

    @patch("wix_safe_agent_cli.commands.async_jobs.HttpClient")
    def test_list_items_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"items": [{"id": "item-1"}]})
        args = SimpleNamespace(job_id="job-1")
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = async_jobs.cmd_async_jobs_list_items(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["method"], "async-jobs.list-items")
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(payload["request"]["path"], "/async-jobs/v1/async-jobs/job-1/items")
        self.assertEqual(payload["response"]["items"][0]["id"], "item-1")

        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["headers"]["Authorization"], "token-abc")

    @patch("wix_safe_agent_cli.commands.async_jobs.HttpClient")
    def test_commands_reject_empty_job_id(self, mock_client: unittest.mock.MagicMock) -> None:
        ctx = self._ctx()

        for func in (async_jobs.cmd_async_jobs_get, async_jobs.cmd_async_jobs_list_items):
            with self.subTest(func=func.__name__):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(SimpleNamespace(job_id="  "), ctx)
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 1)
                self.assertFalse(payload["ok"])
                self.assertIn("job-id", payload["error"])

        self.assertEqual(mock_client.return_value.request.call_count, 0)
