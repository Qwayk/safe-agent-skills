from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from fortnox_api_tool.cli import main


def _write_env(tmpdir: str) -> Path:
    env_path = Path(tmpdir) / ".env"
    env_path.write_text("FORTNOX_API_BASE_URL=https://api.fortnox.se/3\n", encoding="utf-8")
    return env_path


class TestDocumentIntakeReads(unittest.TestCase):
    def test_archive_get_root_supports_optional_query_params(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = _write_env(d)
            buf = io.StringIO()
            with patch(
                "fortnox_api_tool.commands.accounting_reads.request_json",
                return_value={
                    "status": 200,
                    "url": "https://api.fortnox.se/3/archive?path=inbox_a&fileid=fa-123",
                    "token_source": "env",
                    "token_expired": None,
                    "body": {"Folder": {"Name": "inbox_a"}},
                },
            ) as mock_request_json:
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            str(env_path),
                            "archive",
                            "get-root",
                            "--path",
                            "inbox_a",
                            "--file-id",
                            "fa-123",
                        ]
                    )
            self.assertEqual(rc, 0)
            mock_request_json.assert_called_once()
            self.assertEqual(mock_request_json.call_args.kwargs["path"], "/archive")
            self.assertEqual(
                mock_request_json.call_args.kwargs["query_params"],
                {"path": "inbox_a", "fileid": "fa-123"},
            )
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["path"], "/archive")

    def test_archive_get_root_supports_one_optional_query_param(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = _write_env(d)
            buf = io.StringIO()
            with patch(
                "fortnox_api_tool.commands.accounting_reads.request_json",
                return_value={
                    "status": 200,
                    "url": "https://api.fortnox.se/3/archive?path=inbox_v",
                    "token_source": "env",
                    "token_expired": None,
                    "body": {"Folder": {"Name": "inbox_v"}},
                },
            ) as mock_request_json:
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            str(env_path),
                            "archive",
                            "get-root",
                            "--path",
                            "inbox_v",
                        ]
                    )
            self.assertEqual(rc, 0)
            self.assertEqual(
                mock_request_json.call_args.kwargs["query_params"],
                {"path": "inbox_v"},
            )
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["path"], "/archive")

    def test_archive_get_file_is_wired(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = _write_env(d)
            buf = io.StringIO()
            with patch(
                "fortnox_api_tool.commands.accounting_reads.request_json",
                return_value={
                    "status": 200,
                    "url": "https://api.fortnox.se/3/archive/42",
                    "token_source": "env",
                    "token_expired": None,
                    "body": {"File": {"Id": "42"}},
                },
            ):
                with redirect_stdout(buf):
                    rc = main(["--output", "json", "--env-file", str(env_path), "archive", "get-file", "--id", "42"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["path"], "/archive/42")

    def test_inbox_get_root_is_wired(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = _write_env(d)
            buf = io.StringIO()
            with patch(
                "fortnox_api_tool.commands.accounting_reads.request_json",
                return_value={
                    "status": 200,
                    "url": "https://api.fortnox.se/3/inbox",
                    "token_source": "env",
                    "token_expired": None,
                    "body": {"Folder": {"Name": "root"}},
                },
            ):
                with redirect_stdout(buf):
                    rc = main(["--output", "json", "--env-file", str(env_path), "inbox", "get-root"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["path"], "/inbox")

    def test_inbox_get_file_is_wired(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = _write_env(d)
            buf = io.StringIO()
            with patch(
                "fortnox_api_tool.commands.accounting_reads.request_json",
                return_value={
                    "status": 200,
                    "url": "https://api.fortnox.se/3/inbox/abc",
                    "token_source": "env",
                    "token_expired": None,
                    "body": {"File": {"Id": "abc"}},
                },
            ):
                with redirect_stdout(buf):
                    rc = main(["--output", "json", "--env-file", str(env_path), "inbox", "get-file", "--id", "abc"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["path"], "/inbox/abc")

    def test_custom_document_types_list_is_wired(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = _write_env(d)
            buf = io.StringIO()
            with patch(
                "fortnox_api_tool.commands.accounting_reads.request_json",
                return_value={
                    "status": 200,
                    "url": "https://api.fortnox.se/api/warehouse/documentdeliveries/custom/documenttypes-v1",
                    "token_source": "env",
                    "token_expired": None,
                    "body": {"items": []},
                },
            ):
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            str(env_path),
                            "custom-document-types",
                            "list",
                        ]
                    )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["path"], "/api/warehouse/documentdeliveries/custom/documenttypes-v1")

    def test_custom_document_types_get_is_wired(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = _write_env(d)
            buf = io.StringIO()
            with patch(
                "fortnox_api_tool.commands.accounting_reads.request_json",
                return_value={
                    "status": 200,
                    "url": "https://api.fortnox.se/api/warehouse/documentdeliveries/custom/documenttypes-v1/RETURNS",
                    "token_source": "env",
                    "token_expired": None,
                    "body": {"referenceType": "RETURNS"},
                },
            ):
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            str(env_path),
                            "custom-document-types",
                            "get",
                            "--type",
                            "RETURNS",
                        ]
                    )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["path"], "/api/warehouse/documentdeliveries/custom/documenttypes-v1/RETURNS")

    def test_custom_inbound_documents_get_is_wired(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = _write_env(d)
            buf = io.StringIO()
            with patch(
                "fortnox_api_tool.commands.accounting_reads.request_json",
                return_value={
                    "status": 200,
                    "url": "https://api.fortnox.se/api/warehouse/documentdeliveries/custom/inbound-v1/RETURNS/123",
                    "token_source": "env",
                    "token_expired": None,
                    "body": {"id": "123", "type": "RETURNS"},
                },
            ):
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            str(env_path),
                            "custom-inbound-documents",
                            "get",
                            "--type",
                            "RETURNS",
                            "--id",
                            "123",
                        ]
                    )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["path"], "/api/warehouse/documentdeliveries/custom/inbound-v1/RETURNS/123")

    def test_custom_outbound_documents_get_is_wired(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = _write_env(d)
            buf = io.StringIO()
            with patch(
                "fortnox_api_tool.commands.accounting_reads.request_json",
                return_value={
                    "status": 200,
                    "url": "https://api.fortnox.se/api/warehouse/documentdeliveries/custom/outbound-v1/SHIP/987",
                    "token_source": "env",
                    "token_expired": None,
                    "body": {"id": "987", "referenceType": "SHIP"},
                },
            ):
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            str(env_path),
                            "custom-outbound-documents",
                            "get",
                            "--type",
                            "SHIP",
                            "--id",
                            "987",
                        ]
                    )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["path"], "/api/warehouse/documentdeliveries/custom/outbound-v1/SHIP/987")

    def test_manual_documents_list_is_wired(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = _write_env(d)
            buf = io.StringIO()
            with patch(
                "fortnox_api_tool.commands.accounting_reads.request_json",
                return_value={
                    "status": 200,
                    "url": "https://api.fortnox.se/api/warehouse/deliveries-v1",
                    "token_source": "env",
                    "token_expired": None,
                    "body": {"deliveries": []},
                },
            ):
                with redirect_stdout(buf):
                    rc = main(["--output", "json", "--env-file", str(env_path), "manual-documents", "list"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["path"], "/api/warehouse/deliveries-v1")

    def test_manual_inbound_documents_get_is_wired(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = _write_env(d)
            buf = io.StringIO()
            with patch(
                "fortnox_api_tool.commands.accounting_reads.request_json",
                return_value={
                    "status": 200,
                    "url": "https://api.fortnox.se/api/warehouse/deliveries-v1/inbounddeliveries/123",
                    "token_source": "env",
                    "token_expired": None,
                    "body": {"id": "123"},
                },
            ):
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            str(env_path),
                            "manual-inbound-documents",
                            "get",
                            "--id",
                            "123",
                        ]
                    )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["path"], "/api/warehouse/deliveries-v1/inbounddeliveries/123")

    def test_manual_outbound_documents_get_is_wired(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = _write_env(d)
            buf = io.StringIO()
            with patch(
                "fortnox_api_tool.commands.accounting_reads.request_json",
                return_value={
                    "status": 200,
                    "url": "https://api.fortnox.se/api/warehouse/deliveries-v1/outbounddeliveries/456",
                    "token_source": "env",
                    "token_expired": None,
                    "body": {"id": "456"},
                },
            ):
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            str(env_path),
                            "manual-outbound-documents",
                            "get",
                            "--id",
                            "456",
                        ]
                    )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["path"], "/api/warehouse/deliveries-v1/outbounddeliveries/456")

    def test_email_senders_list_is_wired(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = _write_env(d)
            buf = io.StringIO()
            with patch(
                "fortnox_api_tool.commands.accounting_reads.request_json",
                return_value={
                    "status": 200,
                    "url": "https://api.fortnox.se/3/emailsenders",
                    "token_source": "env",
                    "token_expired": None,
                    "body": {"TrustedSenders": [], "RejectedSenders": []},
                },
            ):
                with redirect_stdout(buf):
                    rc = main(["--output", "json", "--env-file", str(env_path), "email-senders", "list"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["path"], "/emailsenders")
