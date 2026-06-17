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
        "url": f"https://api.fortnox.se{path}",
        "token_source": "env",
        "token_expired": None,
        "body": body,
    }


def _attachment_item(
    *,
    entity_id: int = 101,
    entity_type: str = "OF",
    file_id: str = "FILE-1",
    attachment_id: str = "497f6eca-6276-4993-bfeb-53cbbbba6f08",
    include_on_send: bool = True,
) -> dict[str, Any]:
    return {
        "entityId": entity_id,
        "entityType": entity_type,
        "fileId": file_id,
        "id": attachment_id,
        "includeOnSend": include_on_send,
    }


class TestAttachment(unittest.TestCase):
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

    def test_attachment_get_wires_documented_query_params(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n", encoding="utf-8")

            with patch("fortnox_api_tool.commands.attachment.request_data") as request_data:
                request_data.return_value = _api_response(
                    status=200,
                    path="/api/fileattachments/attachments-v1",
                    body=[_attachment_item()],
                )
                rc, payload = self._run(
                    env_path=env_path,
                    args=["attachment", "get", "--entity-id", "101", "--entity-id", "102", "--entity-type", "OF"],
                )

            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(request_data.call_args.kwargs["path"], "/api/fileattachments/attachments-v1")
            self.assertEqual(
                request_data.call_args.kwargs["query_params"],
                {"entityid": [101, 102], "entitytype": "OF"},
            )

    def test_attachment_list_wires_documented_query_params(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n", encoding="utf-8")

            with patch("fortnox_api_tool.commands.attachment.request_data") as request_data:
                request_data.return_value = _api_response(
                    status=200,
                    path="/api/fileattachments/attachments-v1/numberofattachments",
                    body=[{"entityId": 101, "numberOfAttachments": 1}],
                )
                rc, payload = self._run(
                    env_path=env_path,
                    args=["attachment", "list", "--entity-id", "101", "--entity-id", "102", "--entity-type", "OF"],
                )

            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(request_data.call_args.kwargs["path"], "/api/fileattachments/attachments-v1/numberofattachments")
            self.assertEqual(
                request_data.call_args.kwargs["query_params"],
                {"entityids": [101, 102], "entitytype": "OF"},
            )

    def test_attachment_attach_dry_run_emits_plan(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n", encoding="utf-8")
            payload_path = Path(td) / "attach.json"
            payload_path.write_text(json.dumps([_attachment_item()], indent=2), encoding="utf-8")

            with patch("fortnox_api_tool.commands.attachment.request_data") as request_data:
                rc, payload = self._run(
                    env_path=env_path,
                    args=["attachment", "attach-files-to-one-or-more-entities", "--json-file", str(payload_path)],
                )

            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["plan"]["baseline"]["payload_sha256"], _sha256(payload_path))
            self.assertEqual(request_data.call_count, 0)

    def test_attachment_attach_apply_posts_array_and_verifies_response(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n", encoding="utf-8")
            payload_path = Path(td) / "attach.json"
            payload_path.write_text(json.dumps([_attachment_item(), _attachment_item(entity_id=102, file_id="FILE-2")], indent=2), encoding="utf-8")

            with patch("fortnox_api_tool.commands.attachment.request_data") as request_data:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["attachment", "attach-files-to-one-or-more-entities", "--json-file", str(payload_path)],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_data.side_effect = [
                    _api_response(
                        status=204,
                        path="/api/fileattachments/attachments-v1",
                        body=None,
                    ),
                    _api_response(
                        status=200,
                        path="/api/fileattachments/attachments-v1",
                        body=[_attachment_item()],
                    ),
                    _api_response(
                        status=200,
                        path="/api/fileattachments/attachments-v1",
                        body=[_attachment_item(entity_id=102, file_id="FILE-2")],
                    ),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "attachment",
                        "attach-files-to-one-or-more-entities",
                        "--json-file",
                        str(payload_path),
                        "--apply",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

            self.assertEqual(rc_apply, 0)
            self.assertTrue(payload_apply["ok"])
            self.assertEqual(request_data.call_args_list[0].kwargs["method"], "POST")
            self.assertEqual(request_data.call_args_list[0].kwargs["path"], "/api/fileattachments/attachments-v1")
            self.assertEqual(len(request_data.call_args_list[0].kwargs["json_body"]), 2)
            self.assertEqual(request_data.call_args_list[1].kwargs["method"], "GET")
            self.assertEqual(request_data.call_args_list[2].kwargs["method"], "GET")

    def test_attachment_update_apply_puts_documented_path_and_checks_id(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n", encoding="utf-8")
            attachment = _attachment_item(include_on_send=False)
            payload_path = Path(td) / "update.json"
            payload_path.write_text(json.dumps(attachment, indent=2), encoding="utf-8")

            with patch("fortnox_api_tool.commands.attachment.request_data") as request_data:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["attachment", "update", "--attachment-id", attachment["id"], "--json-file", str(payload_path)],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_data.side_effect = [
                    _api_response(
                        status=204,
                        path=f"/api/fileattachments/attachments-v1/{attachment['id']}",
                        body=None,
                    ),
                    _api_response(
                        status=200,
                        path="/api/fileattachments/attachments-v1",
                        body=[attachment],
                    ),
                ]
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "attachment",
                        "update",
                        "--attachment-id",
                        attachment["id"],
                        "--json-file",
                        str(payload_path),
                        "--apply",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

            self.assertEqual(rc_apply, 0)
            self.assertTrue(payload_apply["ok"])
            self.assertEqual(request_data.call_args_list[0].kwargs["method"], "PUT")
            self.assertEqual(
                request_data.call_args_list[0].kwargs["path"],
                f"/api/fileattachments/attachments-v1/{attachment['id']}",
            )
            self.assertEqual(request_data.call_args_list[1].kwargs["method"], "GET")

    def test_attachment_detach_requires_ack_for_apply(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n", encoding="utf-8")
            attachment_id = "497f6eca-6276-4993-bfeb-53cbbbba6f08"

            with patch("fortnox_api_tool.commands.attachment.request_data") as request_data:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["attachment", "detach-file", "--attachment-id", attachment_id],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "attachment",
                        "detach-file",
                        "--attachment-id",
                        attachment_id,
                        "--apply",
                        "--yes",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

            self.assertEqual(rc_apply, 0)
            self.assertTrue(payload_apply.get("refused", False))
            self.assertIn("ack-irreversible", " ".join(payload_apply.get("reasons", [])))
            self.assertEqual(request_data.call_count, 0)

    def test_attachment_detach_apply_uses_delete_and_204(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n", encoding="utf-8")
            attachment_id = "497f6eca-6276-4993-bfeb-53cbbbba6f08"

            with patch("fortnox_api_tool.commands.attachment.request_data") as request_data:
                rc, plan_payload = self._run(
                    env_path=env_path,
                    args=["attachment", "detach-file", "--attachment-id", attachment_id],
                )
                self.assertEqual(rc, 0)
                plan = self._plan_from_output(plan_payload)
                plan_path = Path(td) / "plan.json"
                plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

                request_data.return_value = _api_response(
                    status=204,
                    path=f"/api/fileattachments/attachments-v1/{attachment_id}",
                    body=None,
                )
                rc_apply, payload_apply = self._run(
                    env_path=env_path,
                    args=[
                        "attachment",
                        "detach-file",
                        "--attachment-id",
                        attachment_id,
                        "--apply",
                        "--yes",
                        "--ack-irreversible",
                        "--plan-in",
                        str(plan_path),
                    ],
                )

            self.assertEqual(rc_apply, 0)
            self.assertTrue(payload_apply["ok"])
            self.assertEqual(request_data.call_args.kwargs["method"], "DELETE")
            self.assertEqual(
                request_data.call_args.kwargs["path"],
                f"/api/fileattachments/attachments-v1/{attachment_id}",
            )

    def test_attachment_validate_posts_json_array_without_write_flags(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\nFORTNOX_API_TOKEN=token\n", encoding="utf-8")
            payload_path = Path(td) / "validate.json"
            payload_path.write_text(json.dumps([_attachment_item()], indent=2), encoding="utf-8")

            with patch("fortnox_api_tool.commands.attachment.request_data") as request_data:
                request_data.return_value = _api_response(
                    status=204,
                    path="/api/fileattachments/attachments-v1/validateincludedonsend",
                    body=None,
                )
                rc, payload = self._run(
                    env_path=env_path,
                    args=[
                        "attachment",
                        "validates-a-list-of-attachments-that-will-be-included-on-send",
                        "--json-file",
                        str(payload_path),
                    ],
                )

            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(request_data.call_args.kwargs["method"], "POST")
            self.assertEqual(
                request_data.call_args.kwargs["path"],
                "/api/fileattachments/attachments-v1/validateincludedonsend",
            )
            self.assertEqual(len(request_data.call_args.kwargs["json_body"]), 1)
