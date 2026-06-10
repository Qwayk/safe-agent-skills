from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from zendesk_api_tool.cli import main
from zendesk_api_tool.commands_api import _operation_io  # type: ignore
from zendesk_api_tool.openapi_ops import load_operation_specs
from zendesk_api_tool.openapi_snapshot import load_pinned_openapi_snapshot


def _write_env(tmp: Path) -> Path:
    p = tmp / ".env"
    p.write_text("ZENDESK_BASE_URL=https://acme.zendesk.com\nZENDESK_TIMEOUT_S=1\n", encoding="utf-8")
    return p


def _run(argv: list[str]) -> tuple[int, dict]:
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = main(argv)
    payload = json.loads(buf.getvalue())
    return int(rc), payload


class _CaptureHttpClient:
    calls: list[dict[str, str]]
    calls = []

    def __init__(self, *, timeout_s: float, verbose: bool, user_agent: str) -> None:  # noqa: ARG002
        pass

    def request(
        self,
        *,
        method: str,
        url: str,
        headers: dict[str, str] | None = None,
        params: dict[str, str] | None = None,
        json_body: object | None = None,
        files: dict[str, tuple[str, bytes]] | None = None,
        retries: int = 0,  # noqa: ARG002
    ) -> SimpleNamespace:
        self.__class__.calls.append(
            {
                "method": method,
                "url": url,
                "headers": headers or {},
                "params": params or {},
                "has_body": json_body is not None,
                "has_files": bool(files),
            }
        )
        if method.upper() == "GET":
            return SimpleNamespace(
                status=200,
                url=url,
                headers={"content-type": "application/json"},
                json=lambda: {"ticket": {"id": 1234567890}},
                text=lambda: '{"ticket":{"id":1234567890}}',
            )
        return SimpleNamespace(
            status=201,
            url=url,
            headers={"content-type": "application/json"},
            json=lambda: {"ticket": {"id": 1234567890}},
            text=lambda: '{"ticket":{"id":1234567890}}',
        )


class TestCliApiSafetyGates(unittest.TestCase):
    def test_read_requires_live_to_execute(self) -> None:
        snapshot = load_pinned_openapi_snapshot()
        specs = load_operation_specs(snapshot)

        # Pick a GET operation with no path params and no required query params.
        read_spec = None
        for s in specs:
            if s.method.lower() != "get":
                continue
            if s.path_params:
                continue
            op_io = _operation_io(snapshot, s)
            if any(required for _name, required in op_io.query_params):
                continue
            read_spec = s
            break
        self.assertIsNotNone(read_spec)

        with tempfile.TemporaryDirectory() as td:
            env = _write_env(Path(td))
            rc, payload = _run(["--output", "json", "--env-file", str(env), "api", read_spec.command_name])
            self.assertEqual(rc, 0, payload)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertTrue(payload["live_required"])

    def test_write_defaults_to_plan_and_requires_apply_yes_plan_in(self) -> None:
        snapshot = load_pinned_openapi_snapshot()
        specs = load_operation_specs(snapshot)

        write_spec = None
        for s in specs:
            if s.method.lower() != "post":
                continue
            if s.path_params:
                continue
            op_io = _operation_io(snapshot, s)
            if not (op_io.has_request_body and op_io.body_supports_json):
                continue
            if any(required for _name, required in op_io.query_params):
                continue
            write_spec = s
            break
        self.assertIsNotNone(write_spec)

        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            env = _write_env(td_path)
            plan_path = td_path / "plan.json"

            # Dry-run plan works without --apply.
            rc, payload = _run(
                [
                    "--output",
                    "json",
                    "--env-file",
                    str(env),
                    "--plan-out",
                    str(plan_path),
                    "api",
                    write_spec.command_name,
                    "--body-json",
                    "{}",
                ]
            )
            self.assertEqual(rc, 0, payload)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertTrue(plan_path.exists())
            before_state = payload["plan"]["before_state"]
            self.assertTrue(before_state["required"])
            self.assertFalse(before_state["supported"])
            recovery = payload["plan"]["recovery"]
            self.assertFalse(recovery["automatic_rollback"])
            self.assertEqual(recovery["backups"], [])
            self.assertEqual(recovery["snapshots"], [])
            self.assertIsNone(recovery["rollback_plan"])
            self.assertEqual(payload["plan"]["request"]["method"], "POST")

            # Apply without required gates refuses (safe no-op, rc=0).
            rc2, payload2 = _run(
                [
                    "--output",
                    "json",
                    "--env-file",
                    str(env),
                    "--apply",
                    "api",
                    write_spec.command_name,
                    "--body-json",
                    "{}",
                ]
            )
            self.assertEqual(rc2, 0, payload2)
            self.assertTrue(payload2["ok"])
            self.assertTrue(payload2.get("refused"))

            # Apply with gates but without --live still refuses (safe no-op).
            rc3, payload3 = _run(
                [
                    "--output",
                    "json",
                    "--env-file",
                    str(env),
                    "--apply",
                    "--yes",
                    "--plan-in",
                    str(plan_path),
                    "api",
                    write_spec.command_name,
                    "--body-json",
                    "{}",
                ]
            )
            self.assertEqual(rc3, 0, payload3)
            self.assertTrue(payload3["ok"])
            self.assertTrue(payload3.get("refused"))

    def test_delete_requires_ack_irreversible(self) -> None:
        snapshot = load_pinned_openapi_snapshot()
        specs = load_operation_specs(snapshot)

        delete_spec = None
        for s in specs:
            if s.method.lower() != "delete":
                continue
            delete_spec = s
            break
        self.assertIsNotNone(delete_spec)

        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            env = _write_env(td_path)
            plan_path = td_path / "plan.json"

            argv = ["--output", "json", "--env-file", str(env), "--plan-out", str(plan_path), "api", delete_spec.command_name]
            for param in delete_spec.path_params:
                argv.extend([f"--{param}", "123"])
            rc, payload = _run(argv)
            self.assertEqual(rc, 0, payload)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])

            # Missing --ack-irreversible should require explicit no-snapshot approval before any network call.
            argv2 = [
                "--output",
                "json",
                "--env-file",
                str(env),
                "--apply",
                "--yes",
                "--plan-in",
                str(plan_path),
                "api",
                delete_spec.command_name,
            ]
            for param in delete_spec.path_params:
                argv2.extend([f"--{param}", "123"])
            rc2, payload2 = _run(argv2)
            self.assertEqual(rc2, 0, payload2)
            self.assertTrue(payload2["ok"])
            self.assertTrue(payload2.get("refused"))

    def test_write_apply_with_live_refuses_before_http(self) -> None:
        snapshot = load_pinned_openapi_snapshot()
        specs = load_operation_specs(snapshot)

        write_spec = None
        for s in specs:
            if s.method.lower() != "post":
                continue
            if s.path_params:
                continue
            op_io = _operation_io(snapshot, s)
            if not (op_io.has_request_body and op_io.body_supports_json):
                continue
            if any(required for _name, required in op_io.query_params):
                continue
            write_spec = s
            break
        self.assertIsNotNone(write_spec)

        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            env = td_path / ".env"
            env.write_text(
                "\n".join(
                    [
                        "ZENDESK_BASE_URL=https://acme.zendesk.com",
                        "ZENDESK_TIMEOUT_S=1",
                        "ZENDESK_EMAIL=agent@example.com",
                        "ZENDESK_API_TOKEN=super-secret-token",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            plan_path = td_path / "plan.json"

            rc_plan, plan_payload = _run(
                [
                    "--output",
                    "json",
                    "--env-file",
                    str(env),
                    "--plan-out",
                    str(plan_path),
                    "api",
                    write_spec.command_name,
                    "--body-json",
                    "{}",
                ]
            )
            self.assertEqual(rc_plan, 0, plan_payload)
            self.assertTrue(plan_path.exists())

            _CaptureHttpClient.calls = []
            with patch("zendesk_api_tool.commands_api.HttpClient", _CaptureHttpClient):
                rc_apply, apply_payload = _run(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env),
                        "--apply",
                        "--yes",
                        "--plan-in",
                        str(plan_path),
                        "api",
                        "--live",
                        write_spec.command_name,
                        "--body-json",
                        "{}",
                    ]
                )

            self.assertEqual(rc_apply, 0, apply_payload)
            self.assertTrue(apply_payload["ok"])
            self.assertTrue(apply_payload["refused"])
            self.assertFalse(_CaptureHttpClient.calls)
            self.assertNotIn("receipt", apply_payload)
            joined = " ".join(apply_payload["reasons"])
            self.assertIn("before-state snapshot", joined)
            self.assertIn("ack-no-snapshot", joined)
