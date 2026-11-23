from __future__ import annotations

import csv
import hashlib
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import requests

from freepik_api_tool.cli import main

PNG = b"\x89PNG\r\n\x1a\nexample"
LICENSE = "https://provider.example/license.pdf"
PREVIEW = "https://provider.example/preview.jpg"


def response(url: str, *, payload=None, binary: bytes | None = None, status: int = 200):
    reply = requests.Response()
    reply.url = url
    reply.status_code = status
    reply._content = binary if binary is not None else json.dumps(payload).encode()
    reply._content_consumed = True
    return reply


class TestReviewedDownloads(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.env = self.root / "freepik.env"
        self.env.write_text("FREEPIK_API_KEY=test-key\n", encoding="utf-8")
        self.jobs = self.root / "jobs.csv"
        self.jobs.write_text("resource_id,format\n123,jpg\n456,jpg\n789,jpg\n", encoding="utf-8")
        self.plan = self.root / "preview.json"
        self.ledger = self.root / "licensed-downloads-ledger.csv"
        self.batch = ["jobs", "run", "--file", str(self.jobs)]
        self.single = ["download", "--id", "123", "--format", "jpg"]
        self.licensed = []
        self.binary_urls = []
        self.fail_second_binary = False
        self.multiple_files = False
        self.bad_reply = ""
        request = patch.object(requests.Session, "request", side_effect=self.provider)
        request.start()
        self.addCleanup(request.stop)

    def provider(self, method, url, **kwargs):
        if url.startswith("https://files.example/"):
            self.binary_urls.append(url)
            if self.fail_second_binary and url.endswith("/456"):
                raise requests.Timeout("file transfer stopped")
            return response(url, binary=PNG)
        if "/download" in url:
            self.licensed.append((url, kwargs["params"]))
            if self.bad_reply == "timeout":
                raise requests.Timeout("license reply lost")
            if self.bad_reply == "503":
                return response(url, status=503)
            rid = url.split("/resources/")[1].split("/")[0]
            data = {"url": f"https://files.example/{rid}", "filename": "photo.jpg", "downloadId": f"d-{rid}"}
            if self.bad_reply != "no license":
                data["licenseUrl"] = LICENSE
            if self.multiple_files:
                return response(url, payload={"data": [
                    data,
                    {"url": "https://files.example/456", "filename": "other.jpg", "downloadId": "d-456"},
                ], "licenseUrl": LICENSE})
            return response(url, payload={"data": data})
        if url.endswith("/resources"):
            return response(url, payload={"data": [{"id": 123, "title": "Photo"}]})
        rid = int(url.rsplit("/", 1)[1])
        return response(url, payload={"data": {
            "id": rid, "title": "Photo", "related": {"thumbnail_url": "https://provider.example/wrong.jpg"},
            "preview": {"url": PREVIEW}, "is_ai_generated": False, "has_prompt": False,
        }})

    def cli(self, *args: str):
        stdout = io.StringIO()
        with redirect_stdout(stdout), patch.dict("os.environ", {}, clear=True):
            rc = main(["--env-file", str(self.env), "--project-dir", str(self.root), *args])
        return rc, json.loads(stdout.getvalue())

    def save(self, command) -> dict:
        rc, result = self.cli("--plan-out", str(self.plan), *command)
        self.assertEqual(rc, 0, result)
        self.assertTrue(result["dry_run"])
        self.assertEqual(result["plan_out"], str(self.plan))
        self.assertFalse(self.licensed)
        self.assertFalse(self.ledger.exists())
        self.assertNotIn("test-key", self.plan.read_text())
        return result

    def apply(self, command, *, batch=False):
        flags = ["--apply", "--ack-no-snapshot", "--plan-in", str(self.plan)]
        if batch:
            flags.append("--yes")
        return self.cli(*flags, *command)

    def test_auth_preview_and_successful_single_download(self) -> None:
        self.assertTrue(self.cli("auth", "check")[1]["ok"])
        self.assertEqual(self.cli("preview", "--id", "123")[1]["preview_url"], PREVIEW)
        self.save(self.single)
        rc, result = self.apply(self.single)
        self.assertEqual(rc, 0, result)
        self.assertEqual(len(self.licensed), 1)
        [row] = result["rows"]
        self.assertEqual(row["format"], "png")
        self.assertEqual(row["notes"], "requested_format=jpg")
        self.assertEqual(row["download_id"], "d-123")
        self.assertEqual(row["license_url"], LICENSE)
        self.assertEqual(row["sha256"], hashlib.sha256(PNG).hexdigest())
        self.assertEqual(Path(row["file_path"]).read_bytes(), PNG)
        self.assertNotEqual(self.apply(self.single)[0], 0)
        self.assertEqual(len(self.licensed), 1)

    def test_changed_destination_account_and_old_preview_refused(self) -> None:
        self.save(self.single)
        self.assertNotEqual(self.apply([*self.single, "--out-dir", str(self.root / "new")])[0], 0)
        self.assertNotEqual(self.apply(["download", "--id", "456", "--format", "jpg"])[0], 0)
        self.assertNotEqual(self.apply([*self.single, "--image-size", "2000px"])[0], 0)
        self.env.write_text("FREEPIK_API_KEY=other-account\n", encoding="utf-8")
        self.assertNotEqual(self.apply(self.single)[0], 0)
        self.plan.write_text('{"resource_id":"123","format":"jpg"}', encoding="utf-8")
        self.assertNotEqual(self.apply(self.single)[0], 0)
        self.assertFalse(self.licensed)

    def test_neither_timeout_nor_503_repeats_the_licensing_request(self) -> None:
        sized = [*self.single, "--image-size", "2000px"]
        self.save(sized)
        for failure in ("timeout", "503"):
            with self.subTest(failure=failure):
                self.licensed.clear()
                self.bad_reply = failure
                rc, result = self.apply(sized)
                self.assertEqual(rc, 1)
                self.assertEqual(result["provider_status"], "outcome_unknown")
                self.assertEqual(self.licensed, [
                    ("https://api.freepik.com/v1/resources/123/download", {"image_size": "2000px"}),
                ])
                self.assertFalse(self.binary_urls)
                self.assertFalse(self.ledger.exists())

    def test_batch_flags_and_changed_rows_block_licensing(self) -> None:
        self.save(self.batch)
        self.assertNotEqual(self.cli("--apply", "--ack-no-snapshot", *self.batch)[0], 0)
        self.assertNotEqual(self.cli("--apply", "--yes", *self.batch)[0], 0)
        self.jobs.write_text("resource_id,format\n123,png\n", encoding="utf-8")
        self.assertNotEqual(self.apply(self.batch, batch=True)[0], 0)
        self.assertFalse(self.licensed)

    def test_batch_emits_one_result_and_keeps_success_before_failure(self) -> None:
        self.assertEqual(self.save(self.batch)["count"], 3)
        self.fail_second_binary = True
        rc, result = self.apply(self.batch, batch=True)
        self.assertEqual(rc, 1)
        self.assertFalse(result["ok"])
        self.assertEqual(result["count"], 2)
        self.assertEqual(result["remaining"], 1)
        self.assertEqual(result["downloaded_files"], 1)
        self.assertEqual(len(self.licensed), 2)
        self.assertEqual(result["results"][1]["result"]["provider_status"], "replied")
        self.assertEqual(result["results"][1]["result"]["download_id"], "d-456")
        self.assertEqual(result["recovery"]["strategy"], "no_inverse")
        self.assertFalse(result["recovery"]["automatic_rollback"])
        with self.ledger.open(newline="") as stream:
            [row] = list(csv.DictReader(stream))
        self.assertEqual(row["resource_id"], "123")
        self.assertTrue(Path(row["file_path"]).is_file())

    def test_provider_reply_without_license_keeps_the_download_id(self) -> None:
        self.save(self.single)
        self.bad_reply = "no license"
        rc, result = self.apply(self.single)
        self.assertEqual(rc, 1)
        self.assertEqual(result["provider_status"], "replied")
        self.assertEqual(result["download_id"], "d-123")
        self.assertFalse(self.binary_urls)
        self.assertFalse(self.ledger.exists())

    def test_single_with_multiple_files_keeps_first_file_when_second_fails(self) -> None:
        self.save(self.single)
        self.multiple_files = True
        self.fail_second_binary = True
        rc, result = self.apply(self.single)
        self.assertEqual(rc, 1)
        self.assertEqual(result["provider_status"], "replied")
        self.assertEqual(len(self.licensed), 1)
        [row] = result["rows"]
        self.assertEqual(result["file_paths"], [row["file_path"]])
        self.assertEqual(row["download_id"], "d-123")
        self.assertEqual(Path(row["file_path"]).read_bytes(), PNG)
        with self.ledger.open(newline="") as stream:
            self.assertEqual(list(csv.DictReader(stream))[0]["sha256"], row["sha256"])
