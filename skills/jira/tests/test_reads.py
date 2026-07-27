from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from .helpers import fake_response, run_cli, write_basic_env


class ReadTests(unittest.TestCase):
    def test_jira_pagination_cursor_remains_in_json_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env = write_basic_env(Path(directory))
            with patch(
                "requests.Session.request",
                return_value=fake_response(
                    body={"values": [{"id": "10000"}], "nextPageToken": "next-123"}
                ),
            ):
                rc, payload, _ = run_cli(["--env-file", str(env), "platform", "search-projects"])
        self.assertEqual(rc, 0)
        self.assertEqual(payload["result"]["body"]["nextPageToken"], "next-123")

    def test_fixed_read_resolves_documented_path_and_query(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env = write_basic_env(Path(directory))
            with patch(
                "requests.Session.request",
                return_value=fake_response(
                    body={"key": "PAY-123"},
                    url="https://example.atlassian.net/rest/api/3/issue/PAY-123?expand=names",
                ),
            ) as request:
                rc, payload, _ = run_cli(
                    [
                        "--env-file",
                        str(env),
                        "platform",
                        "get-issue",
                        "--issue-id-or-key",
                        "PAY-123",
                        "--expand",
                        "names",
                    ]
                )
        self.assertEqual(rc, 0)
        self.assertEqual(payload["result"]["body"]["key"], "PAY-123")
        self.assertTrue(request.call_args.kwargs["url"].endswith("/rest/api/3/issue/PAY-123"))
        self.assertEqual(request.call_args.kwargs["params"], {"expand": "names"})

    def test_binary_response_requires_file_and_then_saves_it(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            env = write_basic_env(root)
            output = root / "avatar.png"
            with patch(
                "requests.Session.request",
                return_value=fake_response(body=b"PNGDATA", content_type="image/png"),
            ):
                rc, payload, _ = run_cli(
                    [
                        "--env-file",
                        str(env),
                        "platform",
                        "get-avatar-image-by-id",
                        "--type",
                        "project",
                        "--id",
                        "10000",
                        "--response-out",
                        str(output),
                    ]
                )
            self.assertEqual(rc, 0)
            self.assertEqual(output.read_bytes(), b"PNGDATA")
            self.assertEqual(output.stat().st_mode & 0o777, 0o600)
            self.assertEqual(payload["result"]["body"]["size"], 7)


if __name__ == "__main__":
    unittest.main()
