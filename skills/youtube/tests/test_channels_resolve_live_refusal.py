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


def _env_file(root: Path) -> Path:
    env_path = root / ".env"
    env_path.write_text("YOUTUBE_API_BASE_URL=http://example.invalid\nYOUTUBE_TIMEOUT_S=30\n", encoding="utf-8")
    return env_path


class TestChannelsResolveLiveRefusal(unittest.TestCase):
    def test_resolve_live_selection_required_includes_candidates(self) -> None:
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
                        "resolve",
                        "--channel",
                        "Some channel name",
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

