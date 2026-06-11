from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from gsc_api_tool.cli import main


class _FakeCredentials:
    token = "fake-token"
    valid = True
    expired = False


class _FakeHttpResponse:
    def __init__(self, status: int, payload: object) -> None:
        self.status = status
        self.json = payload


class _FakeHttpClient:
    def __init__(
        self,
        *,
        base_url: str,
        timeout_s: float,
        verbose: bool,
        creds: object,
    ) -> None:
        _ = base_url, timeout_s, verbose, creds

    def request_json(self, *, http_method: str, path: str, query: dict | None, body: object | None) -> _FakeHttpResponse:
        _ = query, body
        if http_method.upper() == "GET":
            if path.startswith("webmasters/v3/sites/") and "/sitemaps" in path:
                return _FakeHttpResponse(200, {"ok": True})
            if path == "webmasters/v3/sites":
                return _FakeHttpResponse(200, {"siteEntry": [{"siteUrl": "https://example.com/"}]})
            return _FakeHttpResponse(200, {})
        return _FakeHttpResponse(200, {"siteUrl": "https://example.com/"})


class TestRunArtifacts(unittest.TestCase):
    def test_write_dry_run_creates_run_folder_and_index(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GSC_TIMEOUT_S=30\n", encoding="utf-8")

            run_id = "2026-03-05T120000Z_deadbe"

            buf = io.StringIO()
            with patch("gsc_api_tool.commands.discovery_methods.GscHttpClient", _FakeHttpClient), patch(
                "gsc_api_tool.commands.discovery_methods.load_credentials_from_config",
                return_value=(_FakeCredentials(), None),
            ), redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--run-id",
                        run_id,
                        "sites",
                        "add",
                        "--site-url",
                        "https://example.com/",
                    ]
                )
            self.assertEqual(rc, 0)

            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["run_id"], run_id)

            artifacts_dir = Path(payload["artifacts_dir"])
            self.assertTrue(artifacts_dir.exists())
            self.assertTrue((artifacts_dir / "plan.json").exists())
            self.assertTrue((artifacts_dir / "summary.md").exists())
            self.assertTrue((artifacts_dir / "audit.jsonl").exists())
            self.assertTrue((artifacts_dir / "before_state.json").exists())

            runs_index = Path(payload["runs_index"])
            self.assertTrue(runs_index.exists())
            index_text = runs_index.read_text(encoding="utf-8")
            self.assertIn(run_id, index_text)
            plan_payload = json.loads((artifacts_dir / "plan.json").read_text(encoding="utf-8"))
            self.assertEqual(plan_payload["before_state_path"], str(artifacts_dir / "before_state.json"))
            self.assertEqual(plan_payload["before_state"], json.loads((artifacts_dir / "before_state.json").read_text(encoding="utf-8")))

    def test_runs_list_and_show_work(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GSC_TIMEOUT_S=30\n", encoding="utf-8")

            run_id = "2026-03-05T120500Z_c0ffee"
            buf = io.StringIO()
            with patch("gsc_api_tool.commands.discovery_methods.GscHttpClient", _FakeHttpClient), patch(
                "gsc_api_tool.commands.discovery_methods.load_credentials_from_config",
                return_value=(_FakeCredentials(), None),
            ), redirect_stdout(buf):
                _ = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--run-id",
                        run_id,
                        "sites",
                        "add",
                        "--site-url",
                        "https://example.com/",
                    ]
                )

            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = main(["--env-file", str(env_path), "runs", "list", "--limit", "5"])
            self.assertEqual(rc2, 0)
            payload2 = json.loads(buf2.getvalue())
            self.assertTrue(payload2["ok"])
            self.assertGreaterEqual(payload2["count"], 1)

            buf3 = io.StringIO()
            with redirect_stdout(buf3):
                rc3 = main(["--env-file", str(env_path), "runs", "show", "--run-id", run_id])
            self.assertEqual(rc3, 0)
            payload3 = json.loads(buf3.getvalue())
            self.assertTrue(payload3["ok"])
            self.assertEqual(payload3["run"]["run_id"], run_id)
            self.assertIsNotNone(payload3["summary_md"])

    def test_refusal_still_creates_run_history(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GSC_TIMEOUT_S=30\n", encoding="utf-8")

            run_id = "2026-03-05T121000Z_refuse1"
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--run-id",
                        run_id,
                        "--apply",
                        "sites",
                        "delete",
                        "--site-url",
                        "https://example.com/",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])

            artifacts_dir = Path(payload["artifacts_dir"])
            self.assertTrue((artifacts_dir / "summary.md").exists())
            runs_index = Path(payload["runs_index"])
            self.assertTrue(runs_index.exists())
            self.assertIn(run_id, runs_index.read_text(encoding="utf-8"))
