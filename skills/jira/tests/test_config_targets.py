from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from jira_safe_agent_cli.config import load_config
from jira_safe_agent_cli.errors import ValidationError

from .helpers import run_cli


class ConfigTargetTests(unittest.TestCase):
    def write_env(self, root: Path, *, base_url: str, oauth: bool = False) -> Path:
        path = root / ".env"
        auth = (
            "JIRA_OAUTH_ACCESS_TOKEN=test-oauth\n"
            if oauth
            else "JIRA_EMAIL=tester@example.com\nJIRA_API_TOKEN=test-basic\n"
        )
        path.write_text(f"JIRA_BASE_URL={base_url}\n{auth}", encoding="utf-8")
        return path

    def test_valid_basic_and_oauth_targets(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            basic = self.write_env(root, base_url="https://example-site.atlassian.net")
            self.assertEqual(load_config(str(basic)).auth_mode, "basic")
            oauth = root / "oauth.env"
            oauth.write_text(
                "JIRA_BASE_URL=https://api.atlassian.com/ex/jira/cloud_123\n"
                "JIRA_OAUTH_ACCESS_TOKEN=test-oauth\n",
                encoding="utf-8",
            )
            self.assertEqual(load_config(str(oauth)).auth_mode, "bearer")

    def test_invalid_targets_refuse_before_http(self) -> None:
        cases = (
            ("https://example.com", False),
            ("https://nested.example.atlassian.net", False),
            ("https://example.atlassian.net/rest/api/3", False),
            ("https://example.atlassian.net:8443", False),
            ("https://example.atlassian.net", True),
            ("https://api.atlassian.com/ex/jira", True),
            ("https://api.atlassian.com/ex/jira/cloud-123/rest", True),
            ("https://evil.example/ex/jira/cloud-123", True),
            ("http://localhost:9876/forward", False),
        )
        for index, (base_url, oauth) in enumerate(cases):
            with self.subTest(base_url=base_url), tempfile.TemporaryDirectory() as directory:
                env = self.write_env(Path(directory), base_url=base_url, oauth=oauth)
                with patch("requests.Session.request") as request:
                    rc, payload, _ = run_cli(
                        ["--env-file", str(env), "auth", "check"]
                    )
                self.assertEqual(rc, 1, index)
                self.assertEqual(payload["error_type"], "ValidationError")
                request.assert_not_called()

    def test_local_test_root_is_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env = self.write_env(Path(directory), base_url="http://127.0.0.1:9876")
            self.assertEqual(load_config(str(env)).base_url, "http://127.0.0.1:9876")

    def test_malformed_port_is_validation_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env = self.write_env(Path(directory), base_url="https://site.atlassian.net:bad")
            with self.assertRaises(ValidationError):
                load_config(str(env))


if __name__ == "__main__":
    unittest.main()
