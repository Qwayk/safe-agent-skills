from __future__ import annotations

import io
import json
import os
import tempfile
import time
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

import requests

from pinterest_api_tool.cli import main
from pinterest_api_tool.oauth_tokens import token_path_for_env_file, write_token_dict


class TestReviewedPinterestChanges(unittest.TestCase):
    def setUp(self) -> None:
        environment = patch.dict(os.environ, {k: v for k, v in os.environ.items() if not k.startswith("PINTEREST_")}, clear=True)
        environment.start()
        self.addCleanup(environment.stop)
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.settings = self.root / "first.env"
        self.settings.write_text("PINTEREST_ACCESS_TOKEN=fixture-access\n")
        self.account = "sample-username"
        self.calls: list[tuple[str, str]] = []
        self.fail_create = False
        self.pin = {"id": "sample-pin", "board_id": "board-1", "title": "Sample"}
        self.board = {"id": "sample-board", "name": "Sample"}
        fixtures = patch.object(requests.Session, "send", side_effect=self.reply)
        fixtures.start()
        self.addCleanup(fixtures.stop)

    def run_cli(self, *args: str) -> tuple[int, dict]:
        output = io.StringIO()
        with redirect_stdout(output):
            status = main(["--env-file", str(self.settings), *args])
        return status, json.loads(output.getvalue())

    def reply(self, request: requests.PreparedRequest, **kwargs) -> requests.Response:
        url = urlsplit(str(request.url))
        path = url.path.removeprefix("/v5")
        method = str(request.method)
        self.calls.append((method, path))
        status = 200
        if path == "/oauth/token":
            form = parse_qs(str(request.body))
            self.assertEqual(form["refresh_token"], ["fixture-saved-refresh"])
            body = {"access_token": "fixture-access", "refresh_token": "fixture-renewed", "expires_in": 3600}
        else:
            self.assertEqual(request.headers.get("Authorization"), "Bearer fixture-access")
            if path == "/user_account":
                body = {"username": self.account}
            elif path == "/boards" and method == "GET":
                body = {"items": []}
            elif path == "/boards":
                body = self.board
            elif path == "/boards/sample-board":
                body = self.board
            elif path == "/pins":
                status = 503 if self.fail_create else 200
                body = {"message": "Fixture could not confirm the write"} if self.fail_create else self.pin
            elif path == "/pins/sample-pin":
                if method == "PATCH":
                    self.pin.update(json.loads(request.body or "{}"))
                body = self.pin
            elif path == "/boards/board-1/sections":
                body = {"items": [{"id": "section-1", "name": "Sample section"}]}
            elif path == "/boards/board-1/pins":
                query = parse_qs(url.query)
                start = int(query.get("bookmark", ["0"])[0])
                count = int(query["page_size"][0])
                stop = min(start + count, 3)
                body = {"items": [{"id": str(i)} for i in range(start, stop)], "bookmark": str(stop) if stop < 3 else None}
            else:
                self.fail(f"Unexpected test request {method} {path}")
        response = requests.Response()
        response.status_code = status
        response.url = str(request.url)
        response._content = json.dumps(body).encode()
        return response

    def test_profiles_import_and_refresh_the_right_local_token(self) -> None:
        old = self.root / ".state" / "token.json"
        write_token_dict(data={"access_token": "older-fixture-access"}, dest_file=old)
        scoped = token_path_for_env_file(str(self.settings))
        other = token_path_for_env_file(str(self.root / "second.env"))
        self.assertNotEqual(scoped, other)
        result, _ = self.run_cli("--yes", "--ack-no-snapshot", "auth", "token", "set", "--file", str(old))
        self.assertEqual(result, 0)
        self.assertTrue(old.is_file())
        self.assertFalse(other.exists())
        self.assertEqual(self.run_cli("auth", "check")[1]["user_account"]["username"], self.account)

        self.settings.write_text(
            "PINTEREST_APP_ID=fixture-app\nPINTEREST_APP_SECRET=fixture-secret\n"
            "PINTEREST_REFRESH_TOKEN=fixture-old-settings-refresh\n"
        )
        write_token_dict(
            data={"access_token": "fixture-expired", "refresh_token": "fixture-saved-refresh", "expires_at": int(time.time()) - 100},
            dest_file=scoped,
        )
        status, payload = self.run_cli("auth", "check")
        self.assertEqual(status, 0)
        self.assertNotIn("fixture-renewed", json.dumps(payload))
        self.assertEqual(json.loads(scoped.read_text())["refresh_token"], "fixture-renewed")
        self.assertFalse(other.exists())

    def test_board_pin_bookmark_resumes_after_the_last_returned_pin(self) -> None:
        cmd = ("board-pins", "list", "--board-id", "board-1", "--page-size", "100")
        status, first = self.run_cli(*cmd, "--limit", "1")
        self.assertEqual(status, 0)
        status, rest = self.run_cli(*cmd, "--limit", "2", "--bookmark", first["bookmark"])
        self.assertEqual(status, 0)
        self.assertEqual([row["id"] for row in first["items"] + rest["items"]], ["0", "1", "2"])

    def test_pin_changes_require_the_same_plan_and_account(self) -> None:
        saved = str(self.root / "pinterest-plan.json")
        base = (
            "pins", "create", "--board-id", "board-1", "--media-source-type", "image_url",
            "--media-url", "https://example.invalid/pin.png",
        )
        flags = ("--apply", "--yes", "--ack-no-snapshot")
        self.assertTrue(self.run_cli(*base, "--title", "Sample")[1]["dry_run"])
        self.assertNotEqual(self.run_cli(*flags, *base, "--title", "Sample")[0], 0)
        self.assertEqual(self.calls, [])
        self.assertEqual(self.run_cli("--plan-out", saved, *base, "--title", "Sample")[0], 0)
        self.assertNotEqual(self.run_cli("--apply", "--yes", "--plan-in", saved, *base, "--title", "Sample")[0], 0)
        self.assertNotEqual(self.run_cli(*flags, "--plan-in", saved, *base, "--title", "Changed")[0], 0)
        self.account = "different-account"
        self.assertNotEqual(self.run_cli(*flags, "--plan-in", saved, *base, "--title", "Sample")[0], 0)
        self.assertEqual({method for method, _ in self.calls}, {"GET"})

        self.account = "sample-username"
        self.fail_create = True
        code, result = self.run_cli(*flags, "--plan-in", saved, *base, "--title", "Sample")
        self.assertNotEqual(code, 0)
        self.assertIn("Check Pinterest before retrying", result["error"])
        self.assertEqual(self.calls.count(("POST", "/pins")), 1)
        self.fail_create = False
        code, result = self.run_cli(*flags, "--plan-in", saved, *base, "--title", "Sample")
        self.assertEqual(code, 0)
        self.assertEqual(result["after"]["id"], "sample-pin")
        self.assertEqual(self.calls[-1], ("GET", "/pins/sample-pin"))

    def test_board_create_reads_the_saved_board(self) -> None:
        saved = str(self.root / "board-plan.json")
        cmd = ("boards", "create", "--name", "Sample")
        self.assertEqual(self.run_cli("--plan-out", saved, *cmd)[0], 0)
        status, result = self.run_cli("--apply", "--yes", "--ack-no-snapshot", "--plan-in", saved, *cmd)
        self.assertEqual(status, 0)
        self.assertEqual(result["after"]["id"], "sample-board")
        self.assertEqual(self.calls[-1], ("GET", "/boards/sample-board"))

    def test_section_ensure_preview_can_check_an_existing_section(self) -> None:
        cmd = ("board-sections", "ensure", "--board-id", "board-1", "--name", "Sample section")
        code, plan = self.run_cli(*cmd)
        self.assertEqual(code, 0)
        self.assertEqual(plan["request"]["section_id"], "section-1")
        self.assertEqual(self.calls, [("GET", "/boards/board-1/sections")])

    def test_pin_links_refuse_a_changed_plan_before_any_patch(self) -> None:
        self.pin["link"] = "https://example.invalid/old/"
        path = self.root / "links.json"
        item = {"pin_id": "sample-pin", "old_link": self.pin["link"], "new_link": "https://example.invalid/new/"}
        path.write_text(json.dumps({"items": [item]}))
        review = str(self.root / "link-review.json")
        cmd = ("pins", "links", "apply", "--plan", str(path))
        self.assertEqual(self.run_cli("--plan-out", review, *cmd)[0], 0)
        path.write_text(json.dumps({"items": [{**item, "new_link": "https://example.invalid/changed/"}]}))
        flags = ("--apply", "--yes", "--ack-no-snapshot", "--plan-in", review)
        self.assertNotEqual(self.run_cli(*flags, *cmd)[0], 0)
        self.assertNotIn(("PATCH", "/pins/sample-pin"), self.calls)
        path.write_text(json.dumps({"items": [item]}))
        self.assertEqual(self.run_cli(*flags, *cmd)[0], 0)
        self.assertEqual(self.pin["link"], item["new_link"])
