from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from youtube_api_tool.cli import main
from youtube_api_tool.http import HttpResponse
from youtube_api_tool.youtube_discovery import extract_official_method_names, get_method_info, load_official_discovery_doc


class TestApiCommand(unittest.TestCase):
    def test_apply_get_refused_requires_live_flag(self) -> None:
        buf = io.StringIO()

        with patch(
            "youtube_api_tool.http.HttpClient.request",
            side_effect=AssertionError("should not reach network when GET is refused under --apply"),
        ), patch(
            "youtube_api_tool.commands.api._oauth_access_token",
            side_effect=AssertionError("should not require oauth when GET is refused under --apply"),
        ), redirect_stdout(buf):
            rc = main(
                [
                    "--output",
                    "json",
                    "--apply",
                    "api",
                    "search.list",
                    "--params-json",
                    "{\"part\":\"snippet\",\"q\":\"cats\"}",
                ]
            )
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertTrue(payload.get("refused"))
        self.assertEqual(payload.get("refusal_type"), "SafetyError")

    def test_apply_mediaupload_refused_without_upload_file(self) -> None:
        discovery = load_official_discovery_doc()
        info = get_method_info(discovery_obj=discovery, method_name="thumbnails.set")
        required = {p.name for p in info.params if p.required}
        params = {k: "X" for k in required}

        buf = io.StringIO()
        with patch(
            "youtube_api_tool.http.HttpClient.request",
            side_effect=AssertionError("should not reach network when mediaUpload is refused without --upload-file"),
        ), patch(
            "youtube_api_tool.commands.api._oauth_access_token",
            side_effect=AssertionError("should not require oauth when mediaUpload is refused without --upload-file"),
        ), redirect_stdout(buf):
            rc = main(
                [
                    "--output",
                    "json",
                    "--apply",
                    "--yes",
                    "api",
                    "thumbnails.set",
                    "--params-json",
                    json.dumps(params, sort_keys=True),
                ]
            )
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertTrue(payload.get("refused"))
        self.assertEqual(payload.get("refusal_type"), "SafetyError")

    def test_apply_non_get_requires_yes_refusal(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(
                [
                    "--output",
                    "json",
                    "--apply",
                    "api",
                    "videos.insert",
                    "--params-json",
                    "{}",
                ]
            )
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertTrue(payload.get("refused"))
        self.assertEqual(payload.get("refusal_type"), "SafetyError")

    def test_apply_delete_requires_ack_irreversible_refusal(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(
                [
                    "--output",
                    "json",
                    "--apply",
                    "--yes",
                    "api",
                    "videos.delete",
                    "--params-json",
                    "{\"id\":\"X\"}",
                ]
            )
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertTrue(payload.get("refused"))
        self.assertEqual(payload.get("refusal_type"), "SafetyError")

    def test_upload_flag_rejected_for_non_mediaupload_method(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "x.bin"
            f.write_bytes(b"abc")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "api",
                        "search.list",
                        "--upload-file",
                        str(f),
                    ]
                )
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertEqual(payload.get("error_type"), "ValidationError")

    def test_live_get_executes_without_apply_and_uses_api_key_fallback(self) -> None:
        discovery = load_official_discovery_doc()
        chosen = None
        # Pick a GET method with OAuth scopes and only `part` required so we can satisfy validation.
        for method in extract_official_method_names(discovery_obj=discovery):
            info = get_method_info(discovery_obj=discovery, method_name=method)
            required = {p.name for p in info.params if p.required}
            if info.http_method.upper() == "GET" and info.scopes and required.issubset({"part"}):
                chosen = method
                break
        if not chosen:
            self.skipTest("No suitable GET method with scopes found in discovery snapshot")

        calls: list[dict] = []

        def _fake_request(self, method, url, *, headers=None, params=None, json_body=None, data=None, files=None, retries=0, retry_on=(429, 500, 502, 503, 504)):  # noqa: ANN001
            calls.append({"method": method, "url": url, "headers": headers, "params": params, "json_body": json_body})
            return HttpResponse(status=200, headers={}, body=b"{}", url=url)

        buf = io.StringIO()
        with patch.dict(os.environ, {"YOUTUBE_API_KEY": "test_key"}, clear=False), patch(
            "youtube_api_tool.commands.api._oauth_access_token",
            side_effect=RuntimeError("oauth should not be required for live GET when api key exists"),
        ), patch(
            "youtube_api_tool.http.HttpClient.request",
            new=_fake_request,
        ), redirect_stdout(buf):
            rc = main(
                [
                    "--output",
                    "json",
                    "api",
                    chosen,
                    "--params-json",
                    "{\"part\":\"snippet\"}",
                    "--live",
                ]
            )
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertTrue(payload.get("live"))
        self.assertEqual(len(calls), 1)
        self.assertIn("key", calls[0]["params"])

    def test_paginate_loops_until_next_page_token_or_max_pages(self) -> None:
        calls: list[dict] = []

        responses = [
            HttpResponse(status=200, headers={}, body=b'{\"nextPageToken\":\"T1\"}', url="https://example.test/1"),
            HttpResponse(status=200, headers={}, body=b'{\"items\":[]}', url="https://example.test/2"),
        ]

        def _fake_request(self, method, url, *, headers=None, params=None, json_body=None, data=None, files=None, retries=0, retry_on=(429, 500, 502, 503, 504)):  # noqa: ANN001
            calls.append({"method": method, "url": url, "params": params})
            return responses.pop(0)

        buf = io.StringIO()
        with patch.dict(os.environ, {"YOUTUBE_API_KEY": "test_key"}, clear=False), patch(
            "youtube_api_tool.http.HttpClient.request",
            new=_fake_request,
        ), redirect_stdout(buf):
            rc = main(
                [
                    "--output",
                    "json",
                    "api",
                    "search.list",
                    "--params-json",
                    "{\"part\":\"snippet\",\"q\":\"cats\",\"maxResults\":1}",
                    "--live",
                    "--paginate",
                    "--max-pages",
                    "2",
                ]
            )
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertEqual(payload.get("page_count"), 2)
        self.assertEqual(len(calls), 2)
        self.assertNotIn("pageToken", calls[0]["params"])
        self.assertEqual(calls[1]["params"].get("pageToken"), "T1")

    def test_plan_in_apply_uses_plan_body_and_rejects_conflicting_body_flag(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            plan_path = Path(d) / "plan.json"

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--plan-out",
                        str(plan_path),
                        "api",
                        "playlists.insert",
                        "--params-json",
                        "{\"part\":\"snippet,status\"}",
                        "--body-json",
                        "{\"snippet\":{\"title\":\"X\"},\"status\":{\"privacyStatus\":\"private\"}}",
                    ]
                )
            self.assertEqual(rc, 0)

            captured: list[dict] = []

            def _fake_request(self, method, url, *, headers=None, params=None, json_body=None, data=None, files=None, retries=0, retry_on=(429, 500, 502, 503, 504)):  # noqa: ANN001
                captured.append({"method": method, "url": url, "json_body": json_body})
                return HttpResponse(status=200, headers={}, body=b"{}", url=url)

            buf2 = io.StringIO()
            with patch(
                "youtube_api_tool.commands.api._oauth_access_token",
                return_value="token",
            ), patch(
                "youtube_api_tool.http.HttpClient.request",
                new=_fake_request,
            ), redirect_stdout(buf2):
                rc2 = main(
                    [
                        "--output",
                        "json",
                        "--apply",
                        "--yes",
                        "--plan-in",
                        str(plan_path),
                        "api",
                        "playlists.insert",
                    ]
                )
            self.assertEqual(rc2, 0)
            payload2 = json.loads(buf2.getvalue())
            self.assertTrue(payload2["ok"])
            self.assertTrue(payload2["refused"])
            self.assertEqual(payload2["plan"]["before_state"]["status"], "no_snapshot_available")
            self.assertEqual(payload2["verification_plan"]["status"], "best_effort_after_apply")
            self.assertEqual(payload2["plan"]["request"]["body"]["snippet"]["title"], "X")
            self.assertEqual(captured, [])

            # Conflicting body flag should be rejected when using --plan-in.
            buf3 = io.StringIO()
            with redirect_stdout(buf3):
                rc3 = main(
                    [
                        "--output",
                        "json",
                        "--apply",
                        "--yes",
                        "--plan-in",
                        str(plan_path),
                        "api",
                        "videos.insert",
                        "--body-json",
                        "{\"snippet\":{\"title\":\"Y\"}}",
                    ]
                )
            self.assertEqual(rc3, 1)
            payload3 = json.loads(buf3.getvalue())
            self.assertFalse(payload3["ok"])
            self.assertEqual(payload3.get("error_type"), "ValidationError")

    def test_upload_drift_refuses_apply_from_plan_in(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            plan_path = Path(d) / "plan.json"
            upload_path = Path(d) / "x.bin"
            upload_path.write_bytes(b"abc")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--plan-out",
                        str(plan_path),
                        "api",
                        "videos.insert",
                        "--params-json",
                        "{\"part\":\"snippet,status\"}",
                        "--body-json",
                        "{\"snippet\":{\"title\":\"X\"},\"status\":{\"privacyStatus\":\"private\"}}",
                        "--upload-file",
                        str(upload_path),
                    ]
                )
            self.assertEqual(rc, 0)

            # Drift: change file size and mtime.
            upload_path.write_bytes(b"abcd")

            buf2 = io.StringIO()
            with patch(
                "youtube_api_tool.commands.api._oauth_access_token",
                return_value="token",
            ), patch(
                "youtube_api_tool.http.HttpClient.request",
                side_effect=AssertionError("should not reach network on drift refusal"),
            ), redirect_stdout(buf2):
                rc2 = main(
                    [
                        "--output",
                        "json",
                        "--apply",
                        "--yes",
                        "--plan-in",
                        str(plan_path),
                        "api",
                        "videos.insert",
                    ]
                )
            self.assertEqual(rc2, 0)
            payload2 = json.loads(buf2.getvalue())
            self.assertTrue(payload2["ok"])
            self.assertTrue(payload2.get("refused"))
            self.assertEqual(payload2.get("refusal_type"), "SafetyError")

    def test_resumable_upload_two_step_flow(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            plan_path = Path(d) / "plan.json"
            upload_path = Path(d) / "x.bin"
            upload_path.write_bytes(b"abc")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--plan-out",
                        str(plan_path),
                        "api",
                        "videos.insert",
                        "--params-json",
                        "{\"part\":\"snippet,status\"}",
                        "--body-json",
                        "{\"snippet\":{\"title\":\"X\"},\"status\":{\"privacyStatus\":\"private\"}}",
                        "--upload-file",
                        str(upload_path),
                        "--upload-protocol",
                        "resumable",
                    ]
                )
            self.assertEqual(rc, 0)

            reqs: list[dict] = []

            def _fake_request(self, method, url, *, headers=None, params=None, json_body=None, data=None, files=None, retries=0, retry_on=(429, 500, 502, 503, 504)):  # noqa: ANN001
                reqs.append({"method": method, "url": url, "params": params, "json_body": json_body})
                if len(reqs) == 1:
                    return HttpResponse(status=200, headers={"location": "https://upload.example.test/upload?upload_id=ABC"}, body=b"", url=url)
                if len(reqs) == 2:
                    return HttpResponse(status=200, headers={}, body=b'{\"id\":\"VID\"}', url=url)
                return HttpResponse(status=200, headers={}, body=b'{\"items\":[{\"id\":\"VID\"}]}', url=url)

            buf2 = io.StringIO()
            with patch(
                "youtube_api_tool.commands.api._oauth_access_token",
                return_value="token",
            ), patch(
                "youtube_api_tool.http.HttpClient.request",
                new=_fake_request,
            ), redirect_stdout(buf2):
                rc2 = main(
                    [
                        "--output",
                        "json",
                        "--apply",
                        "--yes",
                        "--plan-in",
                        str(plan_path),
                        "api",
                        "videos.insert",
                    ]
                )
            self.assertEqual(rc2, 0)
            payload2 = json.loads(buf2.getvalue())
            self.assertTrue(payload2["ok"])
            self.assertTrue(payload2["refused"])
            self.assertEqual(payload2["plan"]["before_state"]["status"], "no_snapshot_available")
            self.assertEqual(payload2["verification_plan"]["status"], "best_effort_after_apply")
            self.assertEqual(reqs, [])

    def test_media_download_requires_download_to_and_writes_file(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            out_path = Path(d) / "captions.vtt"
            calls: list[dict] = []

            def _fake_request(self, method, url, *, headers=None, params=None, json_body=None, data=None, files=None, retries=0, retry_on=(429, 500, 502, 503, 504)):  # noqa: ANN001
                calls.append({"method": method, "url": url, "headers": headers, "params": params, "json_body": json_body})
                return HttpResponse(status=200, headers={"content-type": "text/vtt"}, body=b"WEBVTT\\n\\n00:00:00.000 --> 00:00:01.000\\nHello\\n", url=url)

            buf = io.StringIO()
            with patch.dict(os.environ, {"YOUTUBE_API_KEY": "test_key"}, clear=False), patch(
                "youtube_api_tool.commands.api._oauth_access_token",
                side_effect=RuntimeError("oauth should not be required for live GET when api key exists"),
            ), patch(
                "youtube_api_tool.http.HttpClient.request",
                new=_fake_request,
            ), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "api",
                        "captions.download",
                        "--params-json",
                        "{\"id\":\"CAP\"}",
                        "--live",
                        "--download-to",
                        str(out_path),
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload.get("live"))
            self.assertTrue(out_path.exists())
            self.assertIn("download", payload)
            self.assertEqual(payload["download"]["path"], str(out_path))
            self.assertGreater(payload["download"]["size_bytes"], 0)
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0]["method"], "GET")
            self.assertIn("CAP", calls[0]["url"])
            self.assertEqual(calls[0]["params"]["alt"], "media")

    def test_apply_write_attempts_read_back_verification_when_possible(self) -> None:
        reqs: list[dict] = []

        def _fake_request(self, method, url, *, headers=None, params=None, json_body=None, data=None, files=None, retries=0, retry_on=(429, 500, 502, 503, 504)):  # noqa: ANN001
            reqs.append({"method": method, "url": url, "params": params, "json_body": json_body})
            if len(reqs) == 1:
                return HttpResponse(status=200, headers={}, body=b'{\"id\":\"PL\"}', url=url)
            return HttpResponse(status=200, headers={}, body=b'{\"items\":[{\"id\":\"PL\"}]}', url=url)

        buf = io.StringIO()
        with patch(
            "youtube_api_tool.commands.api._oauth_access_token",
            return_value="token",
        ), patch(
            "youtube_api_tool.http.HttpClient.request",
            new=_fake_request,
        ), redirect_stdout(buf):
            rc = main(
                [
                    "--output",
                    "json",
                    "--apply",
                    "--yes",
                    "api",
                    "playlists.insert",
                    "--params-json",
                    "{\"part\":\"snippet,status\"}",
                    "--body-json",
                    "{\"snippet\":{\"title\":\"X\"},\"status\":{\"privacyStatus\":\"private\"}}",
                ]
            )
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["refused"])
        self.assertEqual(payload["plan"]["before_state"]["status"], "no_snapshot_available")
        self.assertEqual(payload["verification_plan"]["status"], "best_effort_after_apply")
        recovery = payload.get("recovery")
        self.assertIsInstance(recovery, dict)
        self.assertEqual(recovery.get("end_state"), "irreversible_and_clearly_labeled")
        self.assertFalse(recovery.get("automatic_rollback"))
        self.assertEqual(recovery.get("backups"), [])
        self.assertEqual(recovery.get("snapshots"), [])
        self.assertIsNone(recovery.get("rollback_plan"))
        self.assertEqual(reqs, [])

    def test_demo_write_apply_records_no_recovery_contract(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            plan_path = Path(d) / "plan.json"
            receipt_path = Path(d) / "receipt.json"

            buf_plan = io.StringIO()
            with redirect_stdout(buf_plan):
                rc_plan = main(
                    [
                        "--output",
                        "json",
                        "--plan-out",
                        str(plan_path),
                        "demo",
                        "write",
                        "--selector",
                        "demo-resource",
                    ]
                )
            self.assertEqual(rc_plan, 0)
            payload_plan = json.loads(buf_plan.getvalue())
            self.assertTrue(payload_plan["ok"])
            self.assertTrue(payload_plan["dry_run"])
            self.assertIn("plan", payload_plan)
            plan_recovery = payload_plan["plan"].get("recovery")
            self.assertIsInstance(plan_recovery, dict)
            self.assertEqual(plan_recovery.get("end_state"), "irreversible_and_clearly_labeled")
            self.assertFalse(plan_recovery.get("automatic_rollback"))

            buf_apply = io.StringIO()
            with redirect_stdout(buf_apply):
                rc_apply = main(
                    [
                        "--output",
                        "json",
                        "--apply",
                        "--plan-in",
                        str(plan_path),
                        "--receipt-out",
                        str(receipt_path),
                        "demo",
                        "write",
                        "--selector",
                        "demo-resource",
                    ]
                )
            self.assertEqual(rc_apply, 0)
            payload_apply = json.loads(buf_apply.getvalue())
            self.assertTrue(payload_apply["ok"])
            self.assertFalse(payload_apply["dry_run"])
            self.assertTrue(payload_apply["refused"])
            self.assertEqual(payload_apply["plan"]["before_state"]["status"], "no_snapshot_available")
            self.assertEqual(payload_apply["verification_plan"]["status"], "best_effort_after_apply")
            apply_recovery = payload_apply.get("recovery")
            self.assertIsInstance(apply_recovery, dict)
            self.assertEqual(apply_recovery.get("end_state"), "irreversible_and_clearly_labeled")
            self.assertFalse(apply_recovery.get("automatic_rollback"))
            self.assertEqual(apply_recovery.get("snapshots"), [])
            self.assertEqual(apply_recovery.get("backups"), [])
            self.assertIsNone(apply_recovery.get("rollback_plan"))
            self.assertFalse(receipt_path.exists())
