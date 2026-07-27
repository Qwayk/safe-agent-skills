from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from .helpers import fake_response, run_cli, write_basic_env, write_oauth_env


class CliTests(unittest.TestCase):
    def test_version_and_inventory_commands(self) -> None:
        rc, payload, _ = run_cli(["--version"])
        self.assertEqual(rc, 0)
        self.assertEqual(payload["tool"], "jira-safe")
        rc, payload, _ = run_cli(
            ["operations", "show", "--surface", "platform", "--command", "get-issue"]
        )
        self.assertEqual(rc, 0)
        self.assertEqual(payload["operation"]["path"], "/rest/api/3/issue/{issueIdOrKey}")

    def test_parse_error_is_one_json_object(self) -> None:
        rc, payload, raw = run_cli(["platform", "not-a-command"])
        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        _, end = json.JSONDecoder().raw_decode(raw)
        self.assertFalse(raw[end:].strip())

    def test_gated_command_fails_before_http(self) -> None:
        cases = [
            ("platform", "get-forge-app-property-keys", "access-gated-forge"),
            (
                "platform",
                "dynamic-modules-resource-get-modules-get",
                "access-gated-connect",
            ),
            ("platform", "analyse-expression", "developer-preview"),
            ("software", "get-incident-by-id", "intentionally-excluded"),
        ]
        for surface, command, status in cases:
            with self.subTest(command=command), patch("requests.Session.request") as request:
                rc, payload, _ = run_cli([surface, command])
                self.assertEqual(rc, 1)
                self.assertEqual(payload["error_type"], "NotSupportedError")
                self.assertIn(status, payload["error"])
                request.assert_not_called()

    def test_oauth_only_command_refuses_basic_auth_before_http(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env = write_basic_env(Path(directory))
            with patch("requests.Session.request") as request:
                rc, payload, _ = run_cli(
                    ["--env-file", str(env), "software", "get-linked-workspaces"]
                )
        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "NotSupportedError")
        self.assertIn("JIRA_OAUTH_ACCESS_TOKEN", payload["error"])
        request.assert_not_called()

    def test_onboarding_creates_private_placeholder_env(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env = Path(directory) / ".env"
            rc, payload, raw = run_cli(["--env-file", str(env), "onboarding"])
            self.assertEqual(rc, 0)
            self.assertTrue(payload["env_created"])
            self.assertEqual(os.stat(env).st_mode & 0o777, 0o600)
            self.assertIn("JIRA_BASE_URL=", env.read_text(encoding="utf-8"))
            self.assertNotIn("REPLACE_LOCALLY", raw)

    def test_basic_auth_check_does_not_print_token(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env = write_basic_env(Path(directory))
            with patch(
                "requests.Session.request",
                return_value=fake_response(body={"accountId": "abc", "displayName": "Test User"}),
            ) as request:
                rc, payload, raw = run_cli(["--env-file", str(env), "auth", "check"])
        self.assertEqual(rc, 0)
        self.assertEqual(payload["auth_mode"], "basic")
        self.assertNotIn("test-secret-token", raw)
        self.assertEqual(
            request.call_args.kwargs["auth"], ("tester@example.com", "test-secret-token")
        )

    def test_oauth_auth_check_uses_bearer_without_printing_it(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env = write_oauth_env(Path(directory))
            with patch(
                "requests.Session.request", return_value=fake_response(body={"accountId": "abc"})
            ) as request:
                rc, payload, raw = run_cli(["--env-file", str(env), "auth", "check"])
        self.assertEqual(rc, 0)
        self.assertEqual(payload["auth_mode"], "bearer")
        self.assertNotIn("oauth-secret-token", raw)
        self.assertEqual(
            request.call_args.kwargs["headers"]["Authorization"], "Bearer oauth-secret-token"
        )


if __name__ == "__main__":
    unittest.main()
