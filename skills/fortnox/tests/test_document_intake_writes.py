from __future__ import annotations

import hashlib
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any
from unittest.mock import patch

from fortnox_api_tool.cli import main


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _api_response(*, status: int, path: str, body: Any) -> dict[str, Any]:
    return {
        "status": status,
        "url": f"https://api.fortnox.se/3{path}",
        "token_source": "env",
        "token_expired": None,
        "body": body,
    }


class TestDocumentIntakeWrites(unittest.TestCase):
    def _run(self, *, env_path: Path, args: list[str]) -> tuple[int, dict[str, Any]]:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["--output", "json", "--env-file", str(env_path), *args])
        text = buf.getvalue().strip()
        self.assertTrue(text, "Command did not emit JSON output")
        return rc, json.loads(text)

    def _plan_from_output(self, payload: dict[str, Any]) -> dict[str, Any]:
        plan = payload.get("plan")
        if isinstance(plan, dict):
            return plan
        plan_out = payload.get("plan_out") or payload.get("plan_path")
        self.assertTrue(plan_out)
        self.assertIsInstance(plan_out, str)
        return json.loads(Path(plan_out).read_text(encoding="utf-8"))

    def _write_env(self, td: str) -> Path:
        env_path = Path(td) / ".env"
        env_path.write_text(
            "FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n",
            encoding="utf-8",
        )
        return env_path

    def _write_json(self, path: Path, payload: dict[str, Any]) -> None:
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def test_custom_document_types_create_dry_run_emits_plan(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            payload_path = Path(td) / "custom_document_type.json"
            self._write_json(
                payload_path,
                {"referenceType": "RETURNS", "category": "OUTBOUND"},
            )
            expected_hash = _sha256(payload_path)

            with patch("fortnox_api_tool.commands.document_intake_writes.request_data") as request_data:
                rc, payload = self._run(
                    env_path=env_path,
                    args=["custom-document-types", "create", "--json-file", str(payload_path)],
                )

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"].get("baseline", {}).get("payload_sha256"), expected_hash)
        self.assertEqual(request_data.call_count, 0)

    def test_custom_document_types_create_apply_accepts_numeric_json_response(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            payload_path = Path(td) / "custom_document_type.json"
            self._write_json(
                payload_path,
                {"referenceType": "RETURNS", "category": "OUTBOUND"},
            )

            with patch("fortnox_api_tool.commands.document_intake_writes.request_data") as request_data:
                with patch("fortnox_api_tool.commands.document_intake_writes.request_json") as request_json:
                    rc, plan_payload = self._run(
                        env_path=env_path,
                        args=["custom-document-types", "create", "--json-file", str(payload_path)],
                    )
                    self.assertEqual(rc, 0)
                    plan = self._plan_from_output(plan_payload)
                    plan_path = Path(td) / "plan.json"
                    plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                    request_data.return_value = _api_response(
                        status=201,
                        path="/api/warehouse/documentdeliveries/custom/documenttypes-v1",
                        body=1,
                    )
                    request_json.return_value = _api_response(
                        status=200,
                        path="/api/warehouse/documentdeliveries/custom/documenttypes-v1/RETURNS",
                        body={"referenceType": "RETURNS", "category": "OUTBOUND"},
                    )
                    rc_apply, payload_apply = self._run(
                        env_path=env_path,
                        args=[
                            "custom-document-types",
                            "create",
                            "--json-file",
                            str(payload_path),
                            "--apply",
                            "--plan-in",
                            str(plan_path),
                        ],
                    )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply.get("ok", False))
        self.assertEqual(request_data.call_args.kwargs["method"], "POST")
        self.assertFalse(request_data.call_args.kwargs["expect_json_object"])
        self.assertEqual(request_json.call_args.kwargs["method"], "GET")

    def test_custom_inbound_documents_save_rejects_type_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            payload_path = Path(td) / "custom_inbound.json"
            self._write_json(
                payload_path,
                {"referenceType": "WRONG", "id": "doc-42", "released": False},
            )

            rc, payload = self._run(
                env_path=env_path,
                args=[
                    "custom-inbound-documents",
                    "save",
                    "--type",
                    "RETURNS",
                    "--id",
                    "doc-42",
                    "--json-file",
                    str(payload_path),
                ],
            )

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("match --type", payload["error"])

    def test_custom_inbound_documents_release_refuses_without_yes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            payload_path = Path(td) / "custom_inbound.json"
            self._write_json(
                payload_path,
                {"referenceType": "RETURNS", "id": "doc-42", "released": True},
            )

            rc, plan_payload = self._run(
                env_path=env_path,
                args=[
                    "custom-inbound-documents",
                    "release",
                    "--type",
                    "RETURNS",
                    "--id",
                    "doc-42",
                    "--json-file",
                    str(payload_path),
                ],
            )
            self.assertEqual(rc, 0)
            plan = self._plan_from_output(plan_payload)
            plan_path = Path(td) / "plan.json"
            plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

            rc_apply, payload_apply = self._run(
                env_path=env_path,
                args=[
                    "custom-inbound-documents",
                    "release",
                    "--type",
                    "RETURNS",
                    "--id",
                    "doc-42",
                    "--json-file",
                    str(payload_path),
                    "--apply",
                    "--plan-in",
                    str(plan_path),
                ],
            )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply.get("refused", False))
        self.assertIn("--apply --yes", " ".join(payload_apply["reasons"]))

    def test_custom_outbound_documents_void_refuses_without_ack(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            payload_path = Path(td) / "custom_outbound.json"
            self._write_json(
                payload_path,
                {"referenceType": "RETURNS", "id": "doc-77", "voided": True},
            )

            rc, plan_payload = self._run(
                env_path=env_path,
                args=[
                    "custom-outbound-documents",
                    "void",
                    "--type",
                    "RETURNS",
                    "--id",
                    "doc-77",
                    "--json-file",
                    str(payload_path),
                ],
            )
            self.assertEqual(rc, 0)
            plan = self._plan_from_output(plan_payload)
            plan_path = Path(td) / "plan.json"
            plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

            rc_apply, payload_apply = self._run(
                env_path=env_path,
                args=[
                    "custom-outbound-documents",
                    "void",
                    "--type",
                    "RETURNS",
                    "--id",
                    "doc-77",
                    "--json-file",
                    str(payload_path),
                    "--apply",
                    "--yes",
                    "--plan-in",
                    str(plan_path),
                ],
            )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply.get("refused", False))
        self.assertIn("ack-irreversible", " ".join(payload_apply["reasons"]).lower())

    def test_manual_inbound_documents_create_apply_performs_post_and_get_verify(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            payload_path = Path(td) / "manual_inbound_create.json"
            self._write_json(
                payload_path,
                {"note": "dock intake", "released": False},
            )

            with patch("fortnox_api_tool.commands.document_intake_writes.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["manual-inbound-documents", "create", "--json-file", str(payload_path)],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_json.side_effect = [
                    _api_response(
                        status=201,
                        path="/api/warehouse/deliveries-v1/inbounddeliveries",
                        body={"id": "42", "note": "dock intake"},
                    ),
                    _api_response(
                        status=200,
                        path="/api/warehouse/deliveries-v1/inbounddeliveries/42",
                        body={"id": "42", "note": "dock intake"},
                    ),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "manual-inbound-documents",
                        "create",
                        "--json-file",
                        str(payload_path),
                        "--apply",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply.get("ok", False))
        self.assertEqual(request_json.call_args_list[0].kwargs["method"], "POST")
        self.assertEqual(request_json.call_args_list[1].kwargs["method"], "GET")

    def test_manual_inbound_documents_update_note_apply_performs_patch_and_verifies_note(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            payload_path = Path(td) / "manual_inbound_note.json"
            self._write_json(
                payload_path,
                {"id": "42", "note": "updated note"},
            )

            with patch("fortnox_api_tool.commands.document_intake_writes.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=[
                        "manual-inbound-documents",
                        "update-note",
                        "--id",
                        "42",
                        "--json-file",
                        str(payload_path),
                    ],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_json.side_effect = [
                    _api_response(
                        status=200,
                        path="/api/warehouse/deliveries-v1/inbounddeliveries/42",
                        body={"id": "42", "note": "updated note"},
                    ),
                    _api_response(
                        status=200,
                        path="/api/warehouse/deliveries-v1/inbounddeliveries/42",
                        body={"id": "42", "note": "updated note"},
                    ),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "manual-inbound-documents",
                        "update-note",
                        "--id",
                        "42",
                        "--json-file",
                        str(payload_path),
                        "--apply",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply.get("ok", False))
        self.assertEqual(request_json.call_args_list[0].kwargs["method"], "PATCH")
        self.assertTrue(payload_apply["receipt"]["verification"]["verification_note_matches"])

    def test_manual_outbound_documents_release_apply_requires_yes_and_verifies_released(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            payload_path = Path(td) / "manual_outbound_release.json"
            self._write_json(
                payload_path,
                {"id": "88", "released": True},
            )

            with patch("fortnox_api_tool.commands.document_intake_writes.request_json") as request_json:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=[
                        "manual-outbound-documents",
                        "release",
                        "--id",
                        "88",
                        "--json-file",
                        str(payload_path),
                    ],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                rc_refused, payload_refused = self._run(
                    env_path=env_path,
                    args=[
                        "manual-outbound-documents",
                        "release",
                        "--id",
                        "88",
                        "--json-file",
                        str(payload_path),
                        "--apply",
                        "--plan-in",
                        str(plan_path),
                    ],
                )
                self.assertEqual(rc_refused, 0)
                self.assertTrue(payload_refused.get("refused", False))

                request_json.side_effect = [
                    _api_response(
                        status=200,
                        path="/api/warehouse/deliveries-v1/outbounddeliveries/88/release",
                        body={"id": "88"},
                    ),
                    _api_response(
                        status=200,
                        path="/api/warehouse/deliveries-v1/outbounddeliveries/88",
                        body={"id": "88", "released": True},
                    ),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "manual-outbound-documents",
                        "release",
                        "--id",
                        "88",
                        "--json-file",
                        str(payload_path),
                        "--apply",
                        "--yes",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply.get("ok", False))
        self.assertEqual(request_json.call_args_list[0].kwargs["method"], "PUT")
        self.assertTrue(payload_apply["receipt"]["verification"]["verification_released_true"])

    def test_email_senders_add_trusted_apply_verifies_list_after_write(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            payload_path = Path(td) / "trusted_sender.json"
            self._write_json(
                payload_path,
                {"TrustedSender": {"Email": "ap@example.com"}},
            )

            with patch("fortnox_api_tool.commands.document_intake_writes.request_data") as request_data:
                with patch("fortnox_api_tool.commands.document_intake_writes.request_json") as request_json:
                    rc, plan_payload = self._run(
                        env_path=env_path,
                        args=[
                            "email-senders",
                            "add-a-new-email-address-as-trusted",
                            "--json-file",
                            str(payload_path),
                        ],
                    )
                    self.assertEqual(rc, 0)
                    plan = self._plan_from_output(plan_payload)
                    plan_path = Path(td) / "plan.json"
                    plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                    request_data.return_value = _api_response(
                        status=204,
                        path="/emailsenders/trusted",
                        body={"TrustedSender": {"Email": "ap@example.com", "Id": 7}},
                    )
                    request_json.return_value = _api_response(
                        status=200,
                        path="/emailsenders",
                        body={
                            "EmailSenders": {
                                "TrustedSenders": [{"Email": "ap@example.com", "Id": 7}],
                                "RejectedSenders": [],
                            }
                        },
                    )
                    rc_apply, payload_apply = self._run(
                        env_path=env_path,
                        args=[
                            "email-senders",
                            "add-a-new-email-address-as-trusted",
                            "--json-file",
                            str(payload_path),
                            "--apply",
                            "--plan-in",
                            str(plan_path),
                        ],
                    )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply.get("ok", False))
        self.assertEqual(request_data.call_args.kwargs["method"], "POST")
        self.assertFalse(request_data.call_args.kwargs["expect_json"])
        self.assertTrue(payload_apply["receipt"]["verification"]["trusted_sender_present"])

    def test_email_senders_delete_refuses_without_yes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)

            rc, plan_payload = self._run(
                env_path=env_path,
                args=["email-senders", "delete", "--id", "7"],
            )
            self.assertEqual(rc, 0)
            plan = self._plan_from_output(plan_payload)
            plan_path = Path(td) / "plan.json"
            plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

            rc_apply, payload_apply = self._run(
                env_path=env_path,
                args=[
                    "email-senders",
                    "delete",
                    "--id",
                    "7",
                    "--apply",
                    "--plan-in",
                    str(plan_path),
                ],
            )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply.get("refused", False))
        self.assertIn("--apply --yes", " ".join(payload_apply["reasons"]))

    def test_email_senders_delete_apply_verifies_absence(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)

            with patch("fortnox_api_tool.commands.document_intake_writes.request_data") as request_data:
                with patch("fortnox_api_tool.commands.document_intake_writes.request_json") as request_json:
                    rc, plan_payload = self._run(
                        env_path=env_path,
                        args=["email-senders", "delete", "--id", "7"],
                    )
                    self.assertEqual(rc, 0)
                    plan = self._plan_from_output(plan_payload)
                    plan_path = Path(td) / "plan.json"
                    plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                    request_data.return_value = _api_response(
                        status=204,
                        path="/emailsenders/trusted/7",
                        body=None,
                    )
                    request_json.return_value = _api_response(
                        status=200,
                        path="/emailsenders",
                        body={
                            "EmailSenders": {
                                "TrustedSenders": [{"Email": "other@example.com", "Id": 8}],
                                "RejectedSenders": [],
                            }
                        },
                    )
                    rc_apply, payload_apply = self._run(
                        env_path=env_path,
                        args=[
                            "email-senders",
                            "delete",
                            "--id",
                            "7",
                            "--apply",
                            "--yes",
                            "--plan-in",
                            str(plan_path),
                        ],
                    )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply.get("ok", False))
        self.assertEqual(request_data.call_args.kwargs["method"], "DELETE")
        self.assertTrue(payload_apply["receipt"]["verification"]["trusted_sender_absent"])

    def test_archive_delete_refuses_without_ack(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)

            rc, plan_payload = self._run(
                env_path=env_path,
                args=["archive", "delete", "--id", "55", "--path", "inbox_v"],
            )
            self.assertEqual(rc, 0)
            plan = self._plan_from_output(plan_payload)
            plan_path = Path(td) / "plan.json"
            plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

            rc_apply, payload_apply = self._run(
                env_path=env_path,
                args=[
                    "archive",
                    "delete",
                    "--id",
                    "55",
                    "--path",
                    "inbox_v",
                    "--apply",
                    "--yes",
                    "--plan-in",
                    str(plan_path),
                ],
            )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply.get("refused", False))
        self.assertIn("ack-irreversible", " ".join(payload_apply["reasons"]).lower())

    def test_archive_delete_apply_verifies_absence(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)

            with patch("fortnox_api_tool.commands.document_intake_writes.request_data") as request_data:
                with patch("fortnox_api_tool.commands.document_intake_writes.request_json") as request_json:
                    rc, plan_payload = self._run(
                        env_path=env_path,
                        args=["archive", "delete", "--id", "55", "--path", "inbox_v"],
                    )
                    self.assertEqual(rc, 0)
                    plan = self._plan_from_output(plan_payload)
                    plan_path = Path(td) / "plan.json"
                    plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                    request_data.return_value = _api_response(status=204, path="/archive/55", body=None)
                    request_json.side_effect = RuntimeError("HTTP 404 for GET https://api.fortnox.se/3/archive/55?path=inbox_v")
                    rc_apply, payload_apply = self._run(
                        env_path=env_path,
                        args=[
                            "archive",
                            "delete",
                            "--id",
                            "55",
                            "--path",
                            "inbox_v",
                            "--apply",
                            "--yes",
                            "--ack-irreversible",
                            "--plan-in",
                            str(plan_path),
                        ],
                    )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply.get("ok", False))
        self.assertEqual(request_data.call_args.kwargs["method"], "DELETE")
        self.assertEqual(request_data.call_args.kwargs["query_params"], {"path": "inbox_v"})
        self.assertTrue(payload_apply["receipt"]["verification"]["absent"])

    def test_archive_remove_requires_explicit_path(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            rc, payload = self._run(env_path=env_path, args=["archive", "remove", "--path", ""])
        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")

    def test_archive_upload_apply_uses_multipart_and_verifies_by_id(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            upload_path = Path(td) / "voucher.pdf"
            upload_path.write_bytes(b"%PDF-1.4\n")

            with patch("fortnox_api_tool.commands.document_intake_writes.request_multipart_file") as request_multipart_file:
                with patch("fortnox_api_tool.commands.document_intake_writes.request_json") as request_json:
                    rc, plan_payload = self._run(
                        env_path=env_path,
                        args=[
                            "archive",
                            "upload-a-file-to-a-specific-subdirectory",
                            "--file",
                            str(upload_path),
                            "--path",
                            "inbox_v",
                        ],
                    )
                    self.assertEqual(rc, 0)
                    plan = self._plan_from_output(plan_payload)
                    plan_path = Path(td) / "plan.json"
                    plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                    request_multipart_file.return_value = _api_response(
                        status=201,
                        path="/archive",
                        body={"File": {"Id": "99", "Name": "voucher.pdf", "Path": "inbox_v"}},
                    )
                    request_json.return_value = _api_response(
                        status=200,
                        path="/archive/99",
                        body={"Folder": {"Id": "99", "Name": "voucher.pdf"}},
                    )
                    rc_apply, payload_apply = self._run(
                        env_path=env_path,
                        args=[
                            "archive",
                            "upload-a-file-to-a-specific-subdirectory",
                            "--file",
                            str(upload_path),
                            "--path",
                            "inbox_v",
                            "--apply",
                            "--plan-in",
                            str(plan_path),
                        ],
                    )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply.get("ok", False))
        self.assertEqual(request_multipart_file.call_args.kwargs["query_params"], {"path": "inbox_v"})
        self.assertEqual(payload_apply["receipt"]["target_id"], "99")

    def test_inbox_remove_apply_verifies_absence(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)

            with patch("fortnox_api_tool.commands.document_intake_writes.request_data") as request_data:
                with patch("fortnox_api_tool.commands.document_intake_writes.request_json") as request_json:
                    rc, plan_payload = self._run(
                        env_path=env_path,
                        args=["inbox", "remove", "--id", "abc"],
                    )
                    self.assertEqual(rc, 0)
                    plan = self._plan_from_output(plan_payload)
                    plan_path = Path(td) / "plan.json"
                    plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                    request_data.return_value = _api_response(status=204, path="/inbox/abc", body=None)
                    request_json.side_effect = RuntimeError("HTTP 404 for GET https://api.fortnox.se/3/inbox/abc")
                    rc_apply, payload_apply = self._run(
                        env_path=env_path,
                        args=[
                            "inbox",
                            "remove",
                            "--id",
                            "abc",
                            "--apply",
                            "--yes",
                            "--ack-irreversible",
                            "--plan-in",
                            str(plan_path),
                        ],
                    )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply.get("ok", False))
        self.assertEqual(request_data.call_args.kwargs["method"], "DELETE")
        self.assertTrue(payload_apply["receipt"]["verification"]["absent"])

    def test_inbox_upload_apply_uses_multipart_and_verifies_by_id(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            upload_path = Path(td) / "supplier.pdf"
            upload_path.write_bytes(b"%PDF-1.4\n")

            with patch("fortnox_api_tool.commands.document_intake_writes.request_multipart_file") as request_multipart_file:
                with patch("fortnox_api_tool.commands.document_intake_writes.request_json") as request_json:
                    rc, plan_payload = self._run(
                        env_path=env_path,
                        args=[
                            "inbox",
                            "upload-a-file",
                            "--file",
                            str(upload_path),
                            "--folder-id",
                            "folder-7",
                            "--path",
                            "inbox_s",
                        ],
                    )
                    self.assertEqual(rc, 0)
                    plan = self._plan_from_output(plan_payload)
                    plan_path = Path(td) / "plan.json"
                    plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                    request_multipart_file.return_value = _api_response(
                        status=201,
                        path="/inbox",
                        body={"File": {"Id": "302", "Name": "supplier.pdf", "Path": "inbox_s"}},
                    )
                    request_json.return_value = _api_response(
                        status=200,
                        path="/inbox/302",
                        body={"Folder": {"Id": "302", "Name": "supplier.pdf"}},
                    )
                    rc_apply, payload_apply = self._run(
                        env_path=env_path,
                        args=[
                            "inbox",
                            "upload-a-file",
                            "--file",
                            str(upload_path),
                            "--folder-id",
                            "folder-7",
                            "--path",
                            "inbox_s",
                            "--apply",
                            "--plan-in",
                            str(plan_path),
                        ],
                    )

        self.assertEqual(rc_apply, 0)
        self.assertTrue(payload_apply.get("ok", False))
        self.assertEqual(
            request_multipart_file.call_args.kwargs["query_params"],
            {"folderId": "folder-7", "path": "inbox_s"},
        )
        self.assertEqual(payload_apply["receipt"]["target_id"], "302")
