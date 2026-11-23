from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch
from urllib.parse import quote

from requests import ConnectionError

from qwayk_themealdb_safe_agent_cli.cli import main


class _FakeResponse:
    def __init__(self, *, status_code: int, url: str, text: str):
        self.status_code = status_code
        self.url = url
        self.text = text
        self.headers: dict[str, str] = {}
        self.content = text.encode("utf-8")


class TestAuthCommand(unittest.TestCase):
    def test_auth_check_redacts_custom_api_key_on_error(self) -> None:
        secret_key = "super-secret-themealdb-key"
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = Path(temp_dir) / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "THEMEALDB_BASE_URL=https://www.themealdb.com/api/json/v1",
                        f"THEMEALDB_API_KEY={secret_key}",
                        "THEMEALDB_TIMEOUT_S=30",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            fake_response = _FakeResponse(
                status_code=401,
                url=f"https://www.themealdb.com/api/json/v1/{secret_key}/categories.php",
                text=f"bad key {secret_key}",
            )
            buffer = io.StringIO()
            with patch(
                "qwayk_themealdb_safe_agent_cli.http.requests.Session.request",
                return_value=fake_response,
            ):
                with redirect_stdout(buffer):
                    rc = main(["--output", "json", "--env-file", str(env_path), "auth", "check"])
        self.assertEqual(rc, 1)
        text = buffer.getvalue()
        self.assertNotIn(secret_key, text)
        payload = json.loads(text)
        self.assertIn("***REDACTED***", payload["error"])

    def test_custom_key_stays_private_in_verbose_errors_and_debug_traces(self) -> None:
        key = "fixture/key+with spaces"
        encoded = quote(key, safe="")
        url = f"https://www.themealdb.com/api/json/v1/{encoded}/categories.php"
        failure = _FakeResponse(status_code=403, url=url, text=f"Rejected {key} from {url}")
        for debug in (False, True):
            stdout, stderr = io.StringIO(), io.StringIO()
            with self.subTest(debug=debug), tempfile.TemporaryDirectory() as temp_dir:
                env_file = Path(temp_dir) / ".env"
                env_file.write_text(f"THEMEALDB_API_KEY={key}\n", encoding="utf-8")
                log = Path(temp_dir) / "audit.jsonl"
                args = ["--verbose", "--env-file", str(env_file), "--log-file", str(log)]
                if debug:
                    args.append("--debug")
                connection_error = ConnectionError(f"Failed to reach {url} with {key}") if debug else None
                with patch(
                    "requests.Session.request", return_value=failure, side_effect=connection_error,
                ), redirect_stdout(stdout), redirect_stderr(stderr):
                    rc = main([*args, "auth", "check"])
                self.assertEqual(rc, 1)
                self.assertFalse(json.loads(stdout.getvalue())["ok"])
                if debug:
                    self.assertIn("Traceback", stderr.getvalue())
                for output in (stdout.getvalue(), stderr.getvalue(), log.read_text(encoding="utf-8")):
                    self.assertNotIn(key, output)
                    self.assertNotIn(encoded, output)
                    self.assertIn("***REDACTED***", output)

    def test_connection_check_requires_categories(self) -> None:
        cases = [
            ({"error": "access denied"}, 1),
            ({"categories": None}, 1),
            ({"categories": []}, 1),
            ({"categories": [{"idCategory": "1", "strCategory": "Beef"}]}, 0),
        ]
        for response, expected in cases:
            out = io.StringIO()
            fake = _FakeResponse(
                status_code=200, url="https://www.themealdb.com/api/json/v1/1/categories.php",
                text=json.dumps(response),
            )
            with self.subTest(response=response), patch("requests.Session.request", return_value=fake), redirect_stdout(out):
                rc = main(["auth", "check"])
            self.assertEqual(rc, expected)
            self.assertEqual(json.loads(out.getvalue())["ok"], expected == 0)

    def test_custom_key_is_masked_in_results_and_log_context(self) -> None:
        key = "fixture/key+private"
        encoded = quote(key, safe="")
        out = io.StringIO()
        with tempfile.TemporaryDirectory() as temp_dir:
            env_file = Path(temp_dir) / ".env"
            env_file.write_text(f"THEMEALDB_API_KEY={key}\n", encoding="utf-8")
            log = Path(temp_dir) / "audit.jsonl"
            fake = _FakeResponse(
                status_code=200, url=f"https://www.themealdb.com/api/json/v1/{encoded}/search.php",
                text=json.dumps({"meals": [{"idMeal": "52771", "strMeal": "Test meal", "strSource": encoded}]}),
            )
            with patch("requests.Session.request", return_value=fake), redirect_stdout(out):
                rc = main([
                    "--env-file", str(env_file), "--log-file", str(log),
                    "search", "name", "--name", key,
                ])
            self.assertEqual(rc, 0)
            self.assertEqual(json.loads(out.getvalue())["meals"][0]["strSource"], "***REDACTED***")
            for output in (out.getvalue(), log.read_text(encoding="utf-8")):
                self.assertNotIn(key, output)
                self.assertNotIn(encoded, output)
