from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any
from unittest.mock import patch

from spaceship_safe_agent_cli.cli import main


class _FakeHttpResponse:
    def __init__(self, status: int, payload: dict[str, Any] | None = None) -> None:
        self.status = status
        self.headers: dict[str, str] = {}
        self.body = json.dumps(payload or {}).encode("utf-8")
        self.url = ""
        self.attempts = 1
        self.retry_after = None
        self.throttled = False

    def text(self) -> str:
        return self.body.decode("utf-8", errors="replace")


class _FakeTransport:
    def __init__(self, responses: list[_FakeHttpResponse]) -> None:
        self.responses = responses
        self.calls: list[dict[str, Any]] = []

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
    ) -> _FakeHttpResponse:
        self.calls.append(
            {
                "method": method,
                "url": url,
                "headers": headers or {},
                "params": params or {},
                "json_body": json_body,
                "data": data,
            }
        )
        return self.responses.pop(0)


class _ExplodingTransport:
    def __init__(self, message: str) -> None:
        self.message = message

    def request(self, *args: Any, **kwargs: Any) -> None:
        _ = args, kwargs
        raise RuntimeError(self.message)


class TestRunArtifacts(unittest.TestCase):
    def _valid_env(self) -> str:
        return "\n".join(
            [
                "SPACESHIP_API_KEY=" + "test-key-not-secret",
                "SPACESHIP_API_SECRET=" + "test-secret-not-secret",
                "SPACESHIP_TIMEOUT_S=30",
            ]
        )

    def _write_body_file(self, root: Path) -> Path:
        body_path = root / "body.json"
        body_path.write_text("{}", encoding="utf-8")
        return body_path

    def test_domains_delete_refusal_creates_run_folder_and_index(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._valid_env() + "\n", encoding="utf-8")
            run_id = "2026-01-19T120000Z_deadbe"

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--run-id",
                        run_id,
                        "domains",
                        "delete",
                        "example.com",
                    ]
                )
            self.assertEqual(rc, 0)

            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["run_id"], run_id)

            artifacts_dir = Path(payload["artifacts_dir"])
            self.assertTrue(artifacts_dir.exists())
            self.assertTrue((artifacts_dir / "summary.md").exists())
            self.assertTrue((artifacts_dir / "audit.jsonl").exists())

            runs_index = Path(payload["runs_index"])
            self.assertTrue(runs_index.exists())
            index_text = runs_index.read_text(encoding="utf-8")
            self.assertIn(run_id, index_text)

    def test_runs_list_and_show_work(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._valid_env() + "\n", encoding="utf-8")
            run_id = "2026-01-19T120500Z_c0ffee"
            setup_output = io.StringIO()
            with redirect_stdout(setup_output):
                main(
                    [
                        "--env-file",
                        str(env_path),
                        "--run-id",
                        run_id,
                        "domains",
                        "delete",
                        "example.com",
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
            env_path.write_text(self._valid_env() + "\n", encoding="utf-8")
            run_id = "2026-01-19T121000Z_refuse1"
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--run-id",
                        run_id,
                        "domains",
                        "delete",
                        "example.com",
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

    def test_run_id_traversal_is_refused_before_any_outside_path_is_created(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._valid_env() + "\n", encoding="utf-8")
            invalid_ids = (
                "",
                "   ",
                ".",
                "..",
                "../../escaped",
                r"..\escaped",
                str(root / "absolute-run"),
            )
            for invalid_run_id in invalid_ids:
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--env-file",
                            str(env_path),
                            "--run-id",
                            invalid_run_id,
                            "domains",
                            "delete",
                            "example.com",
                        ]
                    )
                self.assertEqual(rc, 1, invalid_run_id)
                payload = json.loads(buf.getvalue())
                self.assertEqual(payload["error_type"], "ValidationError")
            self.assertFalse((root / "escaped").exists())
            self.assertFalse((root / "absolute-run").exists())
            self.assertFalse((root / ".state" / "runs").exists())

            outside = root / "outside"
            outside.mkdir()
            runs_root = root / ".state" / "runs"
            runs_root.mkdir(parents=True)
            (runs_root / "linked-run").symlink_to(outside, target_is_directory=True)
            symlink_buf = io.StringIO()
            with redirect_stdout(symlink_buf):
                symlink_rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--run-id",
                        "linked-run",
                        "domains",
                        "delete",
                        "example.com",
                    ]
                )
            self.assertEqual(symlink_rc, 1)
            self.assertIn("resolves outside", json.loads(symlink_buf.getvalue())["error"])
            self.assertEqual(list(outside.iterdir()), [])

    def test_private_path_identifiers_do_not_escape_through_stdout_or_audit(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._valid_env() + "\n", encoding="utf-8")
            cases = (
                (["contacts", "get", "CONTACT-PATH-CANARY-f66"], "CONTACT-PATH-CANARY-f66"),
                (
                    ["contacts", "attributes", "get", "CONTACT-ATTRIBUTE-CANARY-g77"],
                    "CONTACT-ATTRIBUTE-CANARY-g77",
                ),
                (
                    ["sellerhub", "safepay", "get", "TRANSACTION-PATH-CANARY-h88"],
                    "TRANSACTION-PATH-CANARY-h88",
                ),
            )
            for index, (command, canary) in enumerate(cases):
                audit_path = root / f"audit-{index}.jsonl"
                stdout = io.StringIO()
                transport = _ExplodingTransport(f"provider error echoed {canary}")
                with patch("spaceship_safe_agent_cli.cli.HttpClient", return_value=transport):
                    with redirect_stdout(stdout):
                        rc = main(
                            [
                                "--env-file",
                                str(env_path),
                                "--log-file",
                                str(audit_path),
                                *command,
                            ]
                        )
                self.assertEqual(rc, 1)
                combined = stdout.getvalue() + audit_path.read_text(encoding="utf-8")
                self.assertNotIn(canary, combined)
                self.assertIn("sha256:", combined)

    def test_private_write_error_canaries_never_reach_run_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._valid_env() + "\n", encoding="utf-8")
            contact_canary = "CONTACT-CANARY-91f3"
            billing_canary = "BILLING-CANARY-82a4"
            transfer_canary = "TRANSFER-CODE-CANARY-73b5"
            opaque_canary = "OPAQUE-ERROR-CANARY-64c6"
            body_path = root / "contacts.json"
            body_path.write_text(
                json.dumps(
                    {
                        "registrant": contact_canary,
                        "admin": contact_canary,
                        "billing": billing_canary,
                        "tech": contact_canary,
                    }
                ),
                encoding="utf-8",
            )
            plan_run = "2026-08-01T130000Z_privateplan"
            plan_transport = _FakeTransport(
                [_FakeHttpResponse(200, {"contacts": {"billing": billing_canary}})]
            )
            plan_stdout = io.StringIO()
            with patch("spaceship_safe_agent_cli.cli.HttpClient", return_value=plan_transport):
                with redirect_stdout(plan_stdout):
                    plan_rc = main(
                        [
                            "--env-file",
                            str(env_path),
                            "--run-id",
                            plan_run,
                            "domains",
                            "set-contacts",
                            "example.com",
                            "--body-file",
                            str(body_path),
                        ]
                    )
            self.assertEqual(plan_rc, 0)
            plan_path = root / ".state" / "runs" / plan_run / "plan.json"
            self.assertTrue(plan_path.exists())

            apply_run = "2026-08-01T130100Z_privateapply"
            error_text = " ".join(
                [contact_canary, billing_canary, transfer_canary, opaque_canary]
            )
            apply_transport = _FakeTransport(
                [
                    _FakeHttpResponse(200, {"contacts": {"billing": billing_canary}}),
                    _FakeHttpResponse(400, {"detail": error_text}),
                ]
            )
            apply_stdout = io.StringIO()
            global_audit = root / "global-audit.jsonl"
            with patch("spaceship_safe_agent_cli.cli.HttpClient", return_value=apply_transport):
                with redirect_stdout(apply_stdout):
                    apply_rc = main(
                        [
                            "--env-file",
                            str(env_path),
                            "--run-id",
                            apply_run,
                            "--log-file",
                            str(global_audit),
                            "--apply",
                            "--yes",
                            "--plan-in",
                            str(plan_path),
                            "--ack-private-data",
                            "domains",
                            "set-contacts",
                            "example.com",
                            "--body-file",
                            str(body_path),
                        ]
                    )
            self.assertEqual(apply_rc, 1)
            self.assertEqual([call["method"] for call in apply_transport.calls], ["GET", "PUT"])
            receipt_path = root / ".state" / "runs" / apply_run / "receipt.json"
            self.assertTrue(receipt_path.exists())

            persisted_parts = [plan_stdout.getvalue(), apply_stdout.getvalue()]
            persisted_parts.extend(
                path.read_text(encoding="utf-8", errors="replace")
                for path in (root / ".state").rglob("*")
                if path.is_file()
            )
            persisted_parts.append(global_audit.read_text(encoding="utf-8"))
            persisted = "\n".join(persisted_parts)
            for private_value in (
                contact_canary,
                billing_canary,
                transfer_canary,
                opaque_canary,
            ):
                self.assertNotIn(private_value, persisted)

    def test_write_main_saves_default_and_explicit_plan_and_receipt_paths(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._valid_env() + "\n", encoding="utf-8")
            body_path = root / "contact.json"
            body_path.write_text(
                json.dumps({"firstName": "Private Name", "email": "private@example.com"}),
                encoding="utf-8",
            )

            plan_run = "2026-08-01T120000Z_plan01"
            plan_transport = _FakeTransport([])
            planned = io.StringIO()
            with patch("spaceship_safe_agent_cli.cli.HttpClient", return_value=plan_transport):
                with redirect_stdout(planned):
                    plan_rc = main(
                        [
                            "--env-file",
                            str(env_path),
                            "--run-id",
                            plan_run,
                            "contacts",
                            "save",
                            "--body-file",
                            str(body_path),
                        ]
                    )
            self.assertEqual(plan_rc, 0)
            self.assertEqual(plan_transport.calls, [])
            default_plan = root / ".state" / "runs" / plan_run / "plan.json"
            self.assertTrue(default_plan.exists())
            self.assertTrue((default_plan.parent / "summary.md").exists())
            index_path = root / ".state" / "runs" / "index.jsonl"
            self.assertIn(plan_run, index_path.read_text(encoding="utf-8"))

            explicit_plan = root / "reviewed-plan.json"
            explicit_run = "2026-08-01T120100Z_plan02"
            explicit_plan_transport = _FakeTransport([])
            with patch(
                "spaceship_safe_agent_cli.cli.HttpClient",
                return_value=explicit_plan_transport,
            ):
                with redirect_stdout(io.StringIO()):
                    explicit_plan_rc = main(
                        [
                            "--env-file",
                            str(env_path),
                            "--run-id",
                            explicit_run,
                            "--plan-out",
                            str(explicit_plan),
                            "contacts",
                            "save",
                            "--body-file",
                            str(body_path),
                        ]
                    )
            self.assertEqual(explicit_plan_rc, 0)
            self.assertTrue(explicit_plan.exists())
            self.assertFalse(
                (root / ".state" / "runs" / explicit_run / "plan.json").exists()
            )

            apply_run = "2026-08-01T120200Z_apply1"
            apply_transport = _FakeTransport(
                [
                    _FakeHttpResponse(200, {"contactId": "private-contact-id"}),
                    _FakeHttpResponse(
                        200,
                        {"firstName": "Private Name", "email": "private@example.com"},
                    ),
                ]
            )
            applied = io.StringIO()
            with patch("spaceship_safe_agent_cli.cli.HttpClient", return_value=apply_transport):
                with redirect_stdout(applied):
                    apply_rc = main(
                        [
                            "--env-file",
                            str(env_path),
                            "--run-id",
                            apply_run,
                            "--apply",
                            "--yes",
                            "--plan-in",
                            str(default_plan),
                            "--ack-private-data",
                            "--ack-no-snapshot",
                            "contacts",
                            "save",
                            "--body-file",
                            str(body_path),
                        ]
                    )
            self.assertEqual(apply_rc, 0)
            apply_payload = json.loads(applied.getvalue())
            self.assertFalse(apply_payload["refused"])
            default_receipt = root / ".state" / "runs" / apply_run / "receipt.json"
            self.assertTrue(default_receipt.exists())
            self.assertTrue((default_receipt.parent / "summary.md").exists())
            self.assertIn(apply_run, index_path.read_text(encoding="utf-8"))
            self.assertEqual([call["method"] for call in apply_transport.calls], ["PUT", "GET"])

            explicit_receipt = root / "saved-receipt.json"
            receipt_run = "2026-08-01T120300Z_apply2"
            receipt_transport = _FakeTransport(
                [
                    _FakeHttpResponse(200, {"contactId": "private-contact-id"}),
                    _FakeHttpResponse(200, {"email": "private@example.com"}),
                ]
            )
            with patch("spaceship_safe_agent_cli.cli.HttpClient", return_value=receipt_transport):
                with redirect_stdout(io.StringIO()):
                    receipt_rc = main(
                        [
                            "--env-file",
                            str(env_path),
                            "--run-id",
                            receipt_run,
                            "--apply",
                            "--yes",
                            "--plan-in",
                            str(default_plan),
                            "--receipt-out",
                            str(explicit_receipt),
                            "--ack-private-data",
                            "--ack-no-snapshot",
                            "contacts",
                            "save",
                            "--body-file",
                            str(body_path),
                        ]
                    )
            self.assertEqual(receipt_rc, 0)
            self.assertTrue(explicit_receipt.exists())
            self.assertFalse(
                (root / ".state" / "runs" / receipt_run / "receipt.json").exists()
            )

            persisted = "\n".join(
                path.read_text(encoding="utf-8", errors="replace")
                for path in (root / ".state").rglob("*")
                if path.is_file()
            )
            persisted += explicit_plan.read_text(encoding="utf-8")
            persisted += explicit_receipt.read_text(encoding="utf-8")
            for private_value in (
                "Private Name",
                "private@example.com",
                "private-contact-id",
                "test-key-not-secret",
                "test-secret-not-secret",
            ):
                self.assertNotIn(private_value, persisted)
