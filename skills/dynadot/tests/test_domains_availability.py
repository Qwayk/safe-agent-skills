from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from dynadot_api_tool.commands.domains import cmd_domains_availability
from dynadot_api_tool.dynadot_api import DynadotApiResult
from dynadot_api_tool.output import Output


class _Audit:
    def write(self, event: str, payload: object) -> None:  # noqa: ARG002
        return


class _SequenceApi:
    def __init__(self, responses: list[dict[str, Any] | Exception]) -> None:
        self.responses = list(responses)
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def call(self, *, command: str, params: dict[str, Any] | None = None) -> DynadotApiResult:
        self.calls.append((command, dict(params or {})))
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return DynadotApiResult(command=command, response=response)


class TestDomainsAvailability(unittest.TestCase):
    def _ctx(self, *, api: object) -> dict[str, Any]:
        return {
            "cfg": SimpleNamespace(base_url="https://api.example.invalid", api_key="TESTKEY"),
            "tool": "dynadot-api-tool",
            "tool_version": "0.0.0",
            "command_str": "dynadot-api-tool",
            "apply": False,
            "yes": False,
            "timeout_s": 30.0,
            "verbose": False,
            "out": Output(mode="json"),
            "audit": _Audit(),
            "api": api,
        }

    def _args(self, **overrides: Any) -> SimpleNamespace:
        values: dict[str, Any] = {
            "domain": None,
            "domains_file": None,
            "max_attempts": 3,
            "domains_per_request": 1,
            "min_request_interval_s": 0.0,
            "retry_delay_s": 0.0,
            "show_price": False,
            "currency": None,
            "out": None,
        }
        values.update(overrides)
        return SimpleNamespace(**values)

    def _run(self, args: SimpleNamespace, api: _SequenceApi) -> tuple[int, dict[str, Any]]:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_domains_availability(args, self._ctx(api=api))
        return rc, json.loads(buf.getvalue())

    def test_checks_file_domains_one_per_request_and_normalizes_results(self) -> None:
        api = _SequenceApi(
            [
                {
                    "ResponseCode": "0",
                    "SearchResults": [
                        {"DomainName": "a.shop", "Available": "yes", "Status": "success"}
                    ],
                },
                {
                    "ResponseCode": "0",
                    "SearchResults": [
                        {"DomainName": "b.shop", "Available": "no", "Status": "success"}
                    ],
                },
            ]
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "domains.txt"
            path.write_text("A.shop\nb.shop\na.shop\n", encoding="utf-8")
            rc, payload = self._run(self._args(domains_file=str(path)), api)

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["available"], 1)
        self.assertEqual(payload["unavailable"], 1)
        self.assertEqual(payload["unresolved"], 0)
        self.assertEqual([call[1] for call in api.calls], [{"domain0": "a.shop"}, {"domain0": "b.shop"}])
        self.assertEqual([row["status"] for row in payload["results"]], ["available", "unavailable"])

    def test_registry_error_is_retried_and_never_treated_as_unavailable(self) -> None:
        api = _SequenceApi(
            [
                {
                    "ResponseCode": "0",
                    "SearchResults": [
                        {
                            "DomainName": "retry.shop",
                            "Available": "no",
                            "Status": "error",
                            "Error": "problem with connection to registry",
                        }
                    ],
                },
                {
                    "ResponseCode": "0",
                    "SearchResults": [
                        {"DomainName": "retry.shop", "Available": "yes", "Status": "success"}
                    ],
                },
            ]
        )
        rc, payload = self._run(self._args(domain=["retry.shop"]), api)

        self.assertEqual(rc, 0)
        self.assertEqual(payload["available"], 1)
        self.assertEqual(payload["unavailable"], 0)
        self.assertEqual(payload["results"][0]["status"], "available")
        self.assertEqual(payload["results"][0]["attempts"], 2)

    def test_api_exception_is_retried_until_clear_unavailable_result(self) -> None:
        api = _SequenceApi(
            [
                RuntimeError("temporary connection failure"),
                {
                    "ResponseCode": "0",
                    "SearchResults": [
                        {"DomainName": "taken.shop", "Available": "no", "Status": "success"}
                    ],
                },
            ]
        )
        rc, payload = self._run(self._args(domain=["taken.shop"]), api)

        self.assertEqual(rc, 0)
        self.assertEqual(payload["unavailable"], 1)
        self.assertEqual(payload["results"][0]["status"], "unavailable")
        self.assertEqual(payload["results"][0]["attempts"], 2)

    def test_missing_result_stays_unresolved_and_returns_nonzero(self) -> None:
        api = _SequenceApi(
            [
                {"ResponseCode": "0", "SearchResults": []},
                {"ResponseCode": "0", "SearchResults": []},
            ]
        )
        rc, payload = self._run(
            self._args(domain=["unknown.shop"], max_attempts=2),
            api,
        )

        self.assertEqual(rc, 2)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["unresolved"], 1)
        self.assertEqual(payload["unavailable"], 0)
        self.assertEqual(payload["results"][0]["status"], "unresolved")
        self.assertIn("did not include", payload["results"][0]["last_error"])

    def test_supports_singular_search_result_shape_and_price(self) -> None:
        api = _SequenceApi(
            [
                {
                    "ResponseCode": "0",
                    "SearchResult": {
                        "DomainName": "priced.shop",
                        "Available": "yes",
                        "Price": "1.99 in USD",
                    },
                }
            ]
        )
        rc, payload = self._run(
            self._args(
                domain=["priced.shop"],
                show_price=True,
                currency="USD",
            ),
            api,
        )

        self.assertEqual(rc, 0)
        self.assertEqual(payload["results"][0]["price"], "1.99 in USD")
        self.assertEqual(
            api.calls[0][1],
            {"domain0": "priced.shop", "show_price": "1", "currency": "usd"},
        )

    def test_writes_full_normalized_export_when_out_is_provided(self) -> None:
        api = _SequenceApi(
            [
                {
                    "ResponseCode": "0",
                    "SearchResults": [{"DomainName": "saved.shop", "Available": "yes"}],
                }
            ]
        )
        with tempfile.TemporaryDirectory() as tmp:
            out_path = Path(tmp) / "availability.json"
            rc, payload = self._run(
                self._args(domain=["saved.shop"], out=str(out_path)),
                api,
            )
            export = json.loads(out_path.read_text(encoding="utf-8"))

        self.assertEqual(rc, 0)
        self.assertNotIn("results", payload)
        self.assertEqual(export["counts"]["unresolved"], 0)
        self.assertEqual(export["results"][0]["status"], "available")


if __name__ == "__main__":
    unittest.main()
