from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch
from gtm_api_tool.gtm_api import ApiResponse

from gtm_api_tool.cli import main


class TestRunArtifacts(unittest.TestCase):
    def test_write_dry_run_creates_run_folder_and_index(self) -> None:
        class FakeApi:
            def __init__(self, **kwargs: object) -> None:
                _ = kwargs

            def request(self, **kwargs: object) -> ApiResponse:
                method = str(kwargs.get("http_method") or "").upper()
                path = str(kwargs.get("path") or "")
                if method == "GET":
                    return ApiResponse(
                        status=200,
                        url="https://example.invalid/" + path,
                        body_json={"path": path, "name": "before-state"},
                        body_text=None,
                    )
                raise AssertionError(f"dry-run should not write: {method} {path}")

        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "GTM_BASE_URL=http://example.invalid",
                        "GTM_TIMEOUT_S=30",
                        "GTM_AUTH_MODE=adc",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            run_id = "2026-01-19T120000Z_deadbe"

            buf = io.StringIO()
            with patch("gtm_api_tool.commands.discovery_methods.GtmApi", FakeApi), redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--run-id",
                        run_id,
                        "accounts",
                        "update",
                        "--path",
                        "accounts/123",
                        "--body-json",
                        "{}",
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
            self.assertTrue((artifacts_dir / "before_state.json").exists())
            self.assertTrue((artifacts_dir / "summary.md").exists())
            self.assertTrue((artifacts_dir / "audit.jsonl").exists())
            self.assertIn("Before-state", (artifacts_dir / "summary.md").read_text(encoding="utf-8"))

            runs_index = Path(payload["runs_index"])
            self.assertTrue(runs_index.exists())
            index_text = runs_index.read_text(encoding="utf-8")
            self.assertIn(run_id, index_text)
            self.assertIn("before_state_path", index_text)

    def test_runs_list_and_show_work(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GTM_BASE_URL=http://example.invalid\nGTM_TIMEOUT_S=30\nGTM_AUTH_MODE=adc\n", encoding="utf-8")

            run_id = "2026-01-19T120500Z_c0ffee"
            buf = io.StringIO()
            with redirect_stdout(buf):
                _ = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--run-id",
                        run_id,
                        "accounts",
                        "update",
                        "--path",
                        "accounts/123",
                        "--body-json",
                        "{}",
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
            env_path.write_text("GTM_BASE_URL=http://example.invalid\nGTM_TIMEOUT_S=30\nGTM_AUTH_MODE=adc\n", encoding="utf-8")

            run_id = "2026-01-19T121000Z_refuse1"
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--run-id",
                        run_id,
                        "--apply",
                        "accounts",
                        "containers",
                        "versions",
                        "publish",
                        "--path",
                        "accounts/1/containers/2/versions/3",
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

    def test_apply_run_artifacts_include_before_state_snapshot(self) -> None:
        calls: list[tuple[str, str]] = []

        class FakeApi:
            def __init__(self, **kwargs: object) -> None:
                _ = kwargs

            def request(self, **kwargs: object) -> ApiResponse:
                method = str(kwargs.get("http_method") or "").upper()
                path = str(kwargs.get("path") or "")
                calls.append((method, path))
                if method == "GET":
                    return ApiResponse(
                        status=200,
                        url="https://example.invalid/" + path,
                        body_json={"name": "before"},
                        body_text=None,
                    )
                return ApiResponse(
                    status=200,
                    url="https://example.invalid/" + path,
                    body_json={"result": "ok"},
                    body_text=None,
                )

        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GTM_BASE_URL=http://example.invalid\nGTM_TIMEOUT_S=30\nGTM_AUTH_MODE=adc\n", encoding="utf-8")

            run_id = "2026-01-19T121500Z_before1"
            buf = io.StringIO()
            with patch("gtm_api_tool.commands.discovery_methods.GtmApi", FakeApi), redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--run-id",
                        run_id,
                        "--apply",
                        "accounts",
                        "update",
                        "--path",
                        "accounts/123",
                        "--body-json",
                        "{}",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertIn("receipt", payload)
            artifacts_dir = Path(payload["artifacts_dir"])
            before_state_file = artifacts_dir / "before_state.json"
            self.assertTrue(before_state_file.exists())
            self.assertEqual(payload["receipt"]["before_state"]["artifact_path"], str(before_state_file))

            summary = artifacts_dir / "summary.md"
            self.assertTrue(summary.exists())
            summary_text = summary.read_text(encoding="utf-8")
            self.assertIn("Before-state", summary_text)
            self.assertGreaterEqual(len(calls), 2)
            self.assertEqual(calls[0], ("GET", "tagmanager/v2/accounts/123"))
            self.assertEqual(calls[1][0], "PUT")

            runs_index = Path(payload["runs_index"])
            rows = [line for line in runs_index.read_text(encoding="utf-8").splitlines() if line]
            self.assertTrue(any(run_id in row for row in rows))
            self.assertTrue(any("before_state_path" in row for row in rows))
