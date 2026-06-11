from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from gtm_api_tool.cli import main
from gtm_api_tool.gtm_api import ApiResponse


class TestWriteGates(unittest.TestCase):
    def _write_env(self, root: Path) -> Path:
        p = root / ".env"
        p.write_text("GTM_AUTH_MODE=adc\nGTM_TIMEOUT_S=30\n", encoding="utf-8")
        return p

    def test_write_method_dry_run_emits_plan(self) -> None:
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
            env_path = self._write_env(root)
            plan_path = root / "plan.json"
            buf = io.StringIO()
            with patch("gtm_api_tool.commands.discovery_methods.GtmApi", FakeApi), redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--plan-out",
                        str(plan_path),
                        "accounts",
                        "containers",
                        "workspaces",
                        "tags",
                        "update",
                        "--path",
                        "accounts/1/containers/2/workspaces/3/tags/4",
                        "--body-json",
                        "{}",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertIn("plan", payload)
            recovery = payload["plan"]["recovery"]
            self.assertEqual(recovery["end_state"], "rollback_by_inverse_action")
            self.assertEqual(recovery["strategy"], "revert")
            self.assertIn("before_state", payload["plan"])
            self.assertTrue(payload["plan"]["before_state"]["attempted"])
            self.assertTrue(Path(payload["plan"]["before_state_path"]).exists())
            self.assertTrue(plan_path.exists())

    def test_apply_without_plan_in_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = self._write_env(root)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
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

    def test_high_risk_apply_requires_yes(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = self._write_env(root)
            plan_path = root / "plan.json"

            # Dry-run plan.
            buf0 = io.StringIO()
            with redirect_stdout(buf0):
                _ = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--plan-out",
                        str(plan_path),
                        "accounts",
                        "containers",
                        "combine",
                        "--path",
                        "accounts/1/containers/2",
                        "--body-json",
                        "{}",
                    ]
                )
            self.assertTrue(plan_path.exists())

            # Apply missing --yes should be refused before any network.
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--plan-in",
                        str(plan_path),
                        "accounts",
                        "containers",
                        "combine",
                        "--path",
                        "accounts/1/containers/2",
                        "--body-json",
                        "{}",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])

    def test_medium_apply_without_plan_in_is_allowed(self) -> None:
        class FakeApi:
            def __init__(self, **kwargs: object) -> None:
                _ = kwargs

            def request(self, **kwargs: object) -> ApiResponse:
                _ = kwargs
                return ApiResponse(status=200, url="https://example.invalid", body_json={}, body_text=None)

        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = self._write_env(root)
            buf = io.StringIO()
            with patch("gtm_api_tool.commands.discovery_methods.GtmApi", FakeApi), redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
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
            self.assertTrue(payload["ok"])
            self.assertFalse(payload.get("dry_run", True))
            self.assertIn("receipt", payload)

    def test_apply_captures_before_state_for_update(self) -> None:
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
                        body_json={"name": "before-state"},
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
            env_path = self._write_env(root)
            buf = io.StringIO()
            with patch("gtm_api_tool.commands.discovery_methods.GtmApi", FakeApi), redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
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
            self.assertTrue(payload["ok"])
            self.assertFalse(payload.get("dry_run", True))
            self.assertIn("receipt", payload)
            receipt = payload["receipt"]
            self.assertIn("before_state", receipt)
            self.assertTrue(receipt["before_state"]["attempted"])
            self.assertEqual(receipt["before_state"]["path"], "tagmanager/v2/accounts/123")

            artifacts_dir = Path(payload["artifacts_dir"])
            self.assertTrue((artifacts_dir / "before_state.json").exists())

            self.assertGreaterEqual(len(calls), 2)
            self.assertEqual(calls[0], ("GET", "tagmanager/v2/accounts/123"))
            self.assertEqual(calls[1][0], "PUT")

    def test_apply_captures_before_state_for_publish_action(self) -> None:
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
                        body_json={"name": "before-state"},
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
            env_path = self._write_env(root)
            plan_path = root / "plan.json"
            with redirect_stdout(io.StringIO()):
                _ = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--plan-out",
                        str(plan_path),
                        "accounts",
                        "containers",
                        "versions",
                        "publish",
                        "--path",
                        "accounts/1/containers/2/versions/3",
                    ]
                )
            self.assertTrue(plan_path.exists())

            buf = io.StringIO()
            with patch("gtm_api_tool.commands.discovery_methods.GtmApi", FakeApi), redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--yes",
                        "--ack-irreversible",
                        "--plan-in",
                        str(plan_path),
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
            self.assertFalse(payload.get("dry_run", True))
            self.assertIn("receipt", payload)
            receipt = payload["receipt"]
            self.assertIn("before_state", receipt)
            self.assertTrue(receipt["before_state"]["attempted"])
            self.assertEqual(receipt["before_state"]["path"], "tagmanager/v2/accounts/1/containers/2/versions/3")

            artifacts_dir = Path(payload["artifacts_dir"])
            self.assertTrue((artifacts_dir / "before_state.json").exists())

            self.assertGreaterEqual(len(calls), 2)
            self.assertEqual(calls[0], ("GET", "tagmanager/v2/accounts/1/containers/2/versions/3"))
            self.assertEqual(calls[1][0], "POST")

    def test_irreversible_requires_yes_and_ack(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = self._write_env(root)
            plan_path = root / "plan.json"

            # Dry-run plan.
            buf0 = io.StringIO()
            with redirect_stdout(buf0):
                _ = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--plan-out",
                        str(plan_path),
                        "accounts",
                        "containers",
                        "workspaces",
                        "tags",
                        "delete",
                        "--path",
                        "accounts/1/containers/2/workspaces/3/tags/4",
                    ]
                )
            self.assertTrue(plan_path.exists())

            # Apply missing ack.
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--yes",
                        "--plan-in",
                        str(plan_path),
                        "accounts",
                        "containers",
                        "workspaces",
                        "tags",
                        "delete",
                        "--path",
                        "accounts/1/containers/2/workspaces/3/tags/4",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])

            # Apply missing yes.
            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-irreversible",
                        "--plan-in",
                        str(plan_path),
                        "accounts",
                        "containers",
                        "workspaces",
                        "tags",
                        "delete",
                        "--path",
                        "accounts/1/containers/2/workspaces/3/tags/4",
                    ]
                )
            self.assertEqual(rc2, 0)
            payload2 = json.loads(buf2.getvalue())
            self.assertTrue(payload2["ok"])
            self.assertTrue(payload2["refused"])

    def test_apply_receipt_includes_concrete_create_rollback_plan(self) -> None:
        class FakeApi:
            def __init__(self, **kwargs: object) -> None:
                _ = kwargs
                self.seen_verification = False

            def request(self, **kwargs: object) -> ApiResponse:
                method = str(kwargs.get("http_method") or "").upper()
                if method == "POST":
                    return ApiResponse(
                        status=200,
                        url="https://example.invalid/tagmanager/v2/accounts/1/containers",
                        body_json={"path": "accounts/1/containers/2"},
                        body_text=None,
                    )

                self.seen_verification = True
                return ApiResponse(
                    status=200,
                    url="https://example.invalid/tagmanager/v2/accounts/1/containers/2",
                    body_json={},
                    body_text=None,
                )

        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = self._write_env(root)
            buf = io.StringIO()
            with patch("gtm_api_tool.commands.discovery_methods.GtmApi", FakeApi), redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "accounts",
                        "containers",
                        "create",
                        "--parent",
                        "accounts/1",
                        "--body-json",
                        "{}",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertFalse(payload.get("dry_run", True))
            self.assertIn("receipt", payload)
            recovery = payload["receipt"]["recovery"]
            self.assertEqual(recovery["end_state"], "rollback_by_inverse_action")
            self.assertEqual(recovery["strategy"], "delete_after_create")
            self.assertTrue(recovery["rollback_ready"])
            self.assertEqual(
                recovery["rollback_plan"]["path"],
                "tagmanager/v2/accounts/1/containers/2",
            )
