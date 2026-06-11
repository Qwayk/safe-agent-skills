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
from youtube_api_tool.json_files import read_json_file


def _env_file(root: Path) -> Path:
    env_path = root / ".env"
    env_path.write_text("YOUTUBE_API_BASE_URL=http://example.invalid\nYOUTUBE_TIMEOUT_S=30\n", encoding="utf-8")
    return env_path


class TestChannelsExportDataset(unittest.TestCase):
    def test_export_live_writes_dataset_files(self) -> None:
        calls: list[dict] = []

        responses = [
            # channels.list
            HttpResponse(
                status=200,
                headers={},
                body=json.dumps(
                    {
                        "items": [
                            {
                                "id": "UC_x5XG1OV2P6uZZ5FSM9Ttw",
                                "snippet": {"title": "Google for Developers"},
                                "contentDetails": {"relatedPlaylists": {"uploads": "UU_x5XG1OV2P6uZZ5FSM9Ttw"}},
                            }
                        ]
                    }
                ).encode("utf-8"),
                url="http://example.invalid/youtube/v3/channels",
            ),
            # playlistItems.list page 1 (A,B) with next token
            HttpResponse(
                status=200,
                headers={},
                body=json.dumps(
                    {
                        "items": [
                            {"contentDetails": {"videoId": "a1"}},
                            {"contentDetails": {"videoId": "b2"}},
                        ],
                        "nextPageToken": "T1",
                    }
                ).encode("utf-8"),
                url="http://example.invalid/youtube/v3/playlistItems",
            ),
            # playlistItems.list page 2 (B,C) no next token
            HttpResponse(
                status=200,
                headers={},
                body=json.dumps(
                    {
                        "items": [
                            {"contentDetails": {"videoId": "b2"}},
                            {"contentDetails": {"videoId": "c3"}},
                        ]
                    }
                ).encode("utf-8"),
                url="http://example.invalid/youtube/v3/playlistItems",
            ),
            # videos.list
            HttpResponse(
                status=200,
                headers={},
                body=json.dumps(
                    {
                        "items": [
                            {"id": "a1", "snippet": {"title": "A"}},
                            {"id": "b2", "snippet": {"title": "B"}},
                            {"id": "c3", "snippet": {"title": "C"}},
                        ]
                    }
                ).encode("utf-8"),
                url="http://example.invalid/youtube/v3/videos",
            ),
        ]

        def _fake_request(  # noqa: ANN001
            self,
            method,
            url,
            *,
            headers=None,
            params=None,
            json_body=None,
            data=None,
            files=None,
            retries=0,
            retry_on=(429, 500, 502, 503, 504),
        ):
            calls.append({"method": method, "url": url, "params": params, "headers": headers, "json_body": json_body, "retries": retries})
            return responses.pop(0)

        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = _env_file(root)
            out_dir = root / "export"

            buf = io.StringIO()
            with patch.dict(os.environ, {"YOUTUBE_API_KEY": "test_key"}, clear=False), patch(
                "youtube_api_tool.commands.channels._oauth_access_token",
                side_effect=RuntimeError("oauth should not be required for reads when api key exists"),
            ), patch(
                "youtube_api_tool.http.HttpClient.request",
                new=_fake_request,
            ), redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--output",
                        "json",
                        "channels",
                        "export",
                        "--channel",
                        "UC_x5XG1OV2P6uZZ5FSM9Ttw",
                        "--out-dir",
                        str(out_dir),
                        "--live",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["completed"])

            # Ensure API key fallback is used for reads.
            self.assertGreaterEqual(len(calls), 3)
            for call in calls:
                self.assertIn("key", call["params"])
                self.assertGreaterEqual(int(call.get("retries") or 0), 1)

            manifest = read_json_file(out_dir / "manifest.json")
            self.assertTrue(manifest["completed"])
            self.assertEqual(manifest["counts"]["video_ids"], 3)
            self.assertEqual(manifest["counts"]["playlist_pages_fetched"], 2)

            ids = (out_dir / "video_ids.txt").read_text(encoding="utf-8").splitlines()
            self.assertEqual(ids, ["a1", "b2", "c3"])
            urls = (out_dir / "video_urls.txt").read_text(encoding="utf-8").splitlines()
            self.assertEqual(
                urls,
                [
                    "https://www.youtube.com/watch?v=a1",
                    "https://www.youtube.com/watch?v=b2",
                    "https://www.youtube.com/watch?v=c3",
                ],
            )
            jsonl_lines = (out_dir / "videos.jsonl").read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(jsonl_lines), 3)
            first = json.loads(jsonl_lines[0])
            self.assertEqual(first["video_id"], "a1")
            self.assertEqual(first["watch_url"], "https://www.youtube.com/watch?v=a1")

    def test_export_live_selection_required_includes_candidates(self) -> None:
        responses = [
            # search.list (multiple candidates)
            HttpResponse(
                status=200,
                headers={},
                body=json.dumps(
                    {
                        "items": [
                            {"id": {"channelId": "UC1111111111111111111111"}, "snippet": {"title": "Candidate 1"}},
                            {"id": {"channelId": "UC2222222222222222222222"}, "snippet": {"title": "Candidate 2"}},
                        ]
                    }
                ).encode("utf-8"),
                url="http://example.invalid/youtube/v3/search",
            ),
        ]

        def _fake_request(  # noqa: ANN001
            self,
            method,
            url,
            *,
            headers=None,
            params=None,
            json_body=None,
            data=None,
            files=None,
            retries=0,
            retry_on=(429, 500, 502, 503, 504),
        ):
            return responses.pop(0)

        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = _env_file(root)
            out_dir = root / "export"

            buf = io.StringIO()
            with patch.dict(os.environ, {"YOUTUBE_API_KEY": "test_key"}, clear=False), patch(
                "youtube_api_tool.commands.channels._oauth_access_token",
                side_effect=RuntimeError("oauth should not be required for reads when api key exists"),
            ), patch(
                "youtube_api_tool.http.HttpClient.request",
                new=_fake_request,
            ), redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--output",
                        "json",
                        "channels",
                        "export",
                        "--channel",
                        "Some channel name",
                        "--out-dir",
                        str(out_dir),
                        "--live",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertEqual(payload.get("refusal_type"), "SelectionRequired")
            self.assertIsInstance(payload.get("candidates"), list)
            self.assertGreaterEqual(len(payload["candidates"]), 2)
            self.assertTrue(payload.get("selection", {}).get("required"))

    def test_export_resume_continues_from_checkpoint(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = _env_file(root)
            out_dir = root / "export"

            # First run: stop after one page and leave a checkpoint with nextPageToken.
            responses_1 = [
                HttpResponse(
                    status=200,
                    headers={},
                    body=json.dumps(
                        {
                            "items": [
                                {
                                    "id": "UC_x5XG1OV2P6uZZ5FSM9Ttw",
                                    "snippet": {"title": "Google for Developers"},
                                    "contentDetails": {"relatedPlaylists": {"uploads": "UU_x5XG1OV2P6uZZ5FSM9Ttw"}},
                                }
                            ]
                        }
                    ).encode("utf-8"),
                    url="http://example.invalid/youtube/v3/channels",
                ),
                HttpResponse(
                    status=200,
                    headers={},
                    body=json.dumps(
                        {
                            "items": [
                                {"contentDetails": {"videoId": "a1"}},
                                {"contentDetails": {"videoId": "b2"}},
                            ],
                            "nextPageToken": "T1",
                        }
                    ).encode("utf-8"),
                    url="http://example.invalid/youtube/v3/playlistItems",
                ),
            ]

            def _fake_request_1(  # noqa: ANN001
                self,
                method,
                url,
                *,
                headers=None,
                params=None,
                json_body=None,
                data=None,
                files=None,
                retries=0,
                retry_on=(429, 500, 502, 503, 504),
            ):
                return responses_1.pop(0)

            buf1 = io.StringIO()
            with patch.dict(os.environ, {"YOUTUBE_API_KEY": "test_key"}, clear=False), patch(
                "youtube_api_tool.commands.channels._oauth_access_token",
                side_effect=RuntimeError("oauth should not be required for reads when api key exists"),
            ), patch(
                "youtube_api_tool.http.HttpClient.request",
                new=_fake_request_1,
            ), redirect_stdout(buf1):
                rc1 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--output",
                        "json",
                        "channels",
                        "export",
                        "--channel",
                        "UC_x5XG1OV2P6uZZ5FSM9Ttw",
                        "--out-dir",
                        str(out_dir),
                        "--live",
                        "--max-pages",
                        "1",
                    ]
                )
            self.assertEqual(rc1, 0)
            payload1 = json.loads(buf1.getvalue())
            self.assertTrue(payload1["ok"])
            self.assertFalse(payload1["completed"])
            self.assertTrue((out_dir / "checkpoint.json").exists())

            cp = read_json_file(out_dir / "checkpoint.json")
            self.assertEqual(cp["stage"], "playlist_items")
            self.assertEqual(cp["playlist_items"]["next_page_token"], "T1")

            # Second run: resume, finish playlist and fetch videos.
            responses_2 = [
                HttpResponse(
                    status=200,
                    headers={},
                    body=json.dumps(
                        {
                            "items": [
                                {
                                    "id": "UC_x5XG1OV2P6uZZ5FSM9Ttw",
                                    "snippet": {"title": "Google for Developers"},
                                    "contentDetails": {"relatedPlaylists": {"uploads": "UU_x5XG1OV2P6uZZ5FSM9Ttw"}},
                                }
                            ]
                        }
                    ).encode("utf-8"),
                    url="http://example.invalid/youtube/v3/channels",
                ),
                HttpResponse(
                    status=200,
                    headers={},
                    body=json.dumps(
                        {
                            "items": [
                                {"contentDetails": {"videoId": "b2"}},
                                {"contentDetails": {"videoId": "c3"}},
                            ]
                        }
                    ).encode("utf-8"),
                    url="http://example.invalid/youtube/v3/playlistItems",
                ),
                HttpResponse(
                    status=200,
                    headers={},
                    body=json.dumps(
                        {
                            "items": [
                                {"id": "a1", "snippet": {"title": "A"}},
                                {"id": "b2", "snippet": {"title": "B"}},
                                {"id": "c3", "snippet": {"title": "C"}},
                            ]
                        }
                    ).encode("utf-8"),
                    url="http://example.invalid/youtube/v3/videos",
                ),
            ]

            def _fake_request_2(  # noqa: ANN001
                self,
                method,
                url,
                *,
                headers=None,
                params=None,
                json_body=None,
                data=None,
                files=None,
                retries=0,
                retry_on=(429, 500, 502, 503, 504),
            ):
                return responses_2.pop(0)

            buf2 = io.StringIO()
            with patch.dict(os.environ, {"YOUTUBE_API_KEY": "test_key"}, clear=False), patch(
                "youtube_api_tool.commands.channels._oauth_access_token",
                side_effect=RuntimeError("oauth should not be required for reads when api key exists"),
            ), patch(
                "youtube_api_tool.http.HttpClient.request",
                new=_fake_request_2,
            ), redirect_stdout(buf2):
                rc2 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--output",
                        "json",
                        "channels",
                        "export",
                        "--channel",
                        "UC_x5XG1OV2P6uZZ5FSM9Ttw",
                        "--out-dir",
                        str(out_dir),
                        "--live",
                        "--resume",
                    ]
                )
            self.assertEqual(rc2, 0)
            payload2 = json.loads(buf2.getvalue())
            self.assertTrue(payload2["ok"])
            self.assertTrue(payload2["completed"])

            ids = (out_dir / "video_ids.txt").read_text(encoding="utf-8").splitlines()
            self.assertEqual(ids, ["a1", "b2", "c3"])
