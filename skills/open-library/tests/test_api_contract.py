from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any
from unittest.mock import patch
from urllib.parse import parse_qs, urlencode, urlparse

from qwayk_open_library_safe_agent_cli.cli import main
from qwayk_open_library_safe_agent_cli.http import HttpClient, HttpResponse


class TestApiContracts(unittest.TestCase):
    def _capture_call(self, command_args: list[str], expected_path: str, expected_params: dict[str, str] | None) -> None:
        calls: list[tuple[str, str]] = []

        def fake_request(self, method, url, **kwargs: Any) -> HttpResponse:  # type: ignore[override]
            final_url = str(url)
            params = kwargs.get("params")
            if params:
                final_url = final_url + "?" + urlencode(params)
            calls.append((method, final_url))
            return HttpResponse(
                status=200,
                headers={},
                url=final_url,
                body=json.dumps({"ok": True}).encode("utf-8"),
            )

        with tempfile.TemporaryDirectory() as td:
            env = Path(td) / ".env"
            env.write_text("OPEN_LIBRARY_BASE_URL=https://openlibrary.test\nOPEN_LIBRARY_TIMEOUT_S=5\n", encoding="utf-8")

            with patch.object(HttpClient, "request", fake_request):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(["--env-file", str(env), "--output", "json", *command_args])

        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload.get("ok"))

        self.assertEqual(len(calls), 1)
        method, url = calls[0]
        self.assertEqual(method, "GET")
        parsed = urlparse(url)
        self.assertEqual(parsed.path, expected_path)

        actual_params = {k: vals[0] for k, vals in parse_qs(parsed.query).items()}
        self.assertEqual(actual_params, expected_params or {})

    def test_exact_http_contract(self) -> None:
        cases = [
            (["search", "books", "--q", "dune"], "/search.json", {"q": "dune"}),
            (["search", "books", "--q", "dune", "--fields", "title,author_name", "--sort", "new", "--lang", "eng", "--limit", "20", "--page", "3", "--offset", "5"], "/search.json", {"q": "dune", "fields": "title,author_name", "sort": "new", "lang": "eng", "limit": "20", "page": "3", "offset": "5"}),
            (["search", "authors", "--q", "asimov"], "/search/authors.json", {"q": "asimov"}),
            (["search", "authors", "--q", "asimov", "--limit", "10", "--offset", "2"], "/search/authors.json", {"q": "asimov", "limit": "10", "offset": "2"}),
            (["works", "get", "OL123W"], "/works/OL123W.json", {}),
            (["works", "editions", "list", "OL123W"], "/works/OL123W/editions.json", {}),
            (["works", "editions", "list", "OL123W", "--limit", "3", "--offset", "10"], "/works/OL123W/editions.json", {"limit": "3", "offset": "10"}),
            (["editions", "get", "OL987M"], "/books/OL987M.json", {}),
            (["isbn", "lookup", "9780140328721"], "/isbn/9780140328721.json", {}),
            (["authors", "get", "OL555A"], "/authors/OL555A.json", {}),
            (["authors", "works", "list", "OL555A", "--limit", "8"], "/authors/OL555A/works.json", {"limit": "8"}),
            (["subjects", "get", "Fantasy"], "/subjects/Fantasy.json", {}),
            (["subjects", "get", "Science Fiction", "--details", "--ebooks", "--published-in", "2022", "--limit", "15", "--offset", "7"], "/subjects/Science%20Fiction.json", {"details": "true", "ebooks": "true", "published_in": "2022", "limit": "15", "offset": "7"}),
            (["works", "get", "works/OL123W"], "/works/OL123W.json", {}),
            (["isbn", "lookup", "0-306-40615-2"], "/isbn/0306406152.json", {}),
            (["subjects", "get", "Science Fiction"], "/subjects/Science%20Fiction.json", {}),
        ]

        for argv, expected_path, expected_params in cases:
            with self.subTest(argv=argv):
                self._capture_call(argv, expected_path, expected_params)

    def test_required_args(self) -> None:
        required_cases = [
            ["search", "books"],
            ["search", "authors"],
            ["works", "get"],
            ["works", "editions", "list"],
            ["editions", "get"],
            ["isbn", "lookup"],
            ["authors", "get"],
            ["authors", "works", "list"],
            ["subjects"],
            ["subjects", "get"],
        ]

        for argv in required_cases:
            with tempfile.TemporaryDirectory() as td:
                env = Path(td) / ".env"
                env.write_text("OPEN_LIBRARY_BASE_URL=https://openlibrary.test\n", encoding="utf-8")

                buf = io.StringIO()
                with patch.object(HttpClient, "request", lambda *a, **k: HttpResponse(200, {}, "", b"{}")):
                    with redirect_stdout(buf):
                        rc = main(["--env-file", str(env), "--output", "json", *argv])
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 1)
                self.assertFalse(payload["ok"])
                self.assertEqual(payload["error_type"], "ValidationError")

    def test_config_overrides_env_defaults(self) -> None:
        calls: list[str] = []

        def fake_request(self, method, url, **kwargs: Any) -> HttpResponse:  # type: ignore[override]
            final_url = str(url)
            params = kwargs.get("params")
            if params:
                final_url = final_url + "?" + urlencode(params)
            calls.append(final_url)
            return HttpResponse(
                status=200,
                headers={},
                url=final_url,
                body=json.dumps({"ok": True}).encode("utf-8"),
            )

        with tempfile.TemporaryDirectory() as td:
            env = Path(td) / ".env"
            cfg = Path(td) / "open-library.json"
            env.write_text("OPEN_LIBRARY_BASE_URL=https://env.example\nOPEN_LIBRARY_TIMEOUT_S=5\n", encoding="utf-8")
            cfg.write_text(
                json.dumps(
                    {
                        "base_url": "https://config.example",
                        "timeout_s": 9,
                        "user_agent_app": "qwayk-open-library-safe-agent-cli",
                    }
                ),
                encoding="utf-8",
            )

            with patch.object(HttpClient, "request", fake_request):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--env-file",
                            str(env),
                            "--config",
                            str(cfg),
                            "--output",
                            "json",
                            "search",
                            "books",
                            "--q",
                            "dune",
                            "--limit",
                            "1",
                        ]
                    )

        self.assertEqual(rc, 0)
        self.assertEqual(len(calls), 1)
        self.assertTrue(calls[0].startswith("https://config.example/search.json?"))
