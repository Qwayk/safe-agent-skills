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


def _write_env_file(path: Path, *, base_url: str, token: str = "tok_test", timeout_s: int = 30) -> None:
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


class TestRunArtifacts(unittest.TestCase):
    def _run(self, *, env_path: Path, argv: list[str], fake_request=None) -> tuple[int, dict[str, object]]:
        buf = io.StringIO()
        with patch.dict(os.environ, {"CALLRAIL_DEFAULT_ACCOUNT_ID": "acc_default"}):
            ctx = redirect_stdout(buf)
            if fake_request is None:
                with ctx:
                    rc = main(["--output", "json", "--env-file", str(env_path), *argv])
            else:
                with patch("requests.Session.request", new=fake_request):
                    with ctx:
                        rc = main(["--output", "json", "--env-file", str(env_path), *argv])
        return rc, json.loads(buf.getvalue())

    def test_dry_run_write_creates_run_artifacts_and_is_visible_in_runs_commands(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            _write_env_file(env_path, base_url="https://api.callrail.test")

            rc, payload = self._run(
                env_path=env_path,
                argv=[
                    "tags",
                    "create",
                    "--payload-json",
                    '{"name":"VIP Lead","color":"blue"}',
                ],
            )

            self.assertEqual(rc, 0)
            self.assertTrue(payload.get("dry_run"))
            run_id = str(payload.get("run_id") or "")
            artifacts_dir = Path(str(payload.get("artifacts_dir") or ""))
            self.assertTrue(run_id)
            self.assertTrue(artifacts_dir.exists())
            self.assertTrue((artifacts_dir / "plan.json").exists())
            self.assertTrue((artifacts_dir / "summary.md").exists())
            self.assertTrue((artifacts_dir / "audit.jsonl").exists())

            list_rc, list_payload = self._run(env_path=env_path, argv=["runs", "list", "--limit", "5"])
            self.assertEqual(list_rc, 0)
            self.assertEqual(list_payload.get("count"), 1)
            self.assertEqual(list_payload.get("runs", [])[0].get("run_id"), run_id)

            show_rc, show_payload = self._run(env_path=env_path, argv=["runs", "show", "--run-id", run_id])
            self.assertEqual(show_rc, 0)
            self.assertEqual(show_payload.get("run", {}).get("run_id"), run_id)
            self.assertIn("Outcome: dry_run", str(show_payload.get("summary_md") or ""))

    def test_apply_write_creates_receipt_and_run_summary(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            _write_env_file(env_path, base_url="https://api.callrail.test")

            def fake_request(self, method, url, **kwargs):  # noqa: ANN001
                _ = (method, url, kwargs)
                return _DummyResponse(status=201, url=str(url), payload={"id": "tag_123", "name": "VIP Lead"})

            rc, payload = self._run(
                env_path=env_path,
                argv=[
                    "--apply",
                    "--yes",
                    "--ack-no-snapshot",
                    "tags",
                    "create",
                    "--payload-json",
                    '{"name":"VIP Lead"}',
                ],
                fake_request=fake_request,
            )

            self.assertEqual(rc, 0)
            self.assertFalse(payload.get("dry_run"))
            artifacts_dir = Path(str(payload.get("artifacts_dir") or ""))
            self.assertTrue((artifacts_dir / "receipt.json").exists())
            self.assertTrue((artifacts_dir / "summary.md").exists())
            receipt_obj = json.loads((artifacts_dir / "receipt.json").read_text(encoding="utf-8"))
            self.assertEqual(receipt_obj.get("command"), "tags create")
            self.assertEqual(receipt_obj.get("response", {}).get("status"), 201)
            summary_text = (artifacts_dir / "summary.md").read_text(encoding="utf-8")
            self.assertIn("Outcome: ok", summary_text)
