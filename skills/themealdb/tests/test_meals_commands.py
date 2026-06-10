from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace

from qwayk_themealdb_safe_agent_cli.audit_log import AuditLogger
from qwayk_themealdb_safe_agent_cli.commands import meals as meals_cmd
from qwayk_themealdb_safe_agent_cli.config import Config
from qwayk_themealdb_safe_agent_cli.errors import ValidationError
from qwayk_themealdb_safe_agent_cli.output import Output


class _FakeResponse:
    def __init__(self, payload: dict):
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class _FakeHttp:
    def __init__(self, payload: dict):
        self.payload = payload
        self.calls: list[dict] = []

    def request(self, method: str, url: str, *, params=None, headers=None, retries=0, retry_on=()) -> _FakeResponse:
        self.calls.append(
            {
                "method": method,
                "url": url,
                "params": params,
                "headers": headers,
                "retries": retries,
                "retry_on": retry_on,
            }
        )
        return _FakeResponse(self.payload)


class TestMealsCommands(unittest.TestCase):
    def _run_command(self, func, args: SimpleNamespace, payload: dict) -> tuple[int, dict, list[dict]]:
        buffer = io.StringIO()
        output = Output(mode="json")
        cfg = Config(
            base_url="https://www.themealdb.com/api/json/v1",
            api_key="1",
            api_key_source="default_public_key",
            timeout_s=30.0,
        )
        http = _FakeHttp(payload)
        ctx = {
            "cfg": cfg,
            "http": http,
            "audit": AuditLogger(path=None, enabled=False),
            "out": output,
            "env_file": ".env",
            "tool": "qwayk-themealdb-safe-agent-cli",
            "command": "test command",
        }
        output.set_provenance({"tool": "qwayk-themealdb-safe-agent-cli", "version": "0.1.0"})
        with redirect_stdout(buffer):
            rc = func(args, ctx)
        return rc, json.loads(buffer.getvalue()), http.calls

    def test_categories_reads_categories_key(self) -> None:
        rc, payload, calls = self._run_command(
            meals_cmd.cmd_categories,
            SimpleNamespace(),
            {"categories": [{"idCategory": "1", "strCategory": "Beef"}]},
        )
        self.assertEqual(rc, 0)
        self.assertEqual(payload["command"], "categories")
        self.assertEqual(payload["count"], 1)
        self.assertEqual(calls[0]["url"], "https://www.themealdb.com/api/json/v1/1/categories.php")

    def test_search_name_passes_s_param_and_normalizes_empty_results(self) -> None:
        rc, payload, calls = self._run_command(
            meals_cmd.cmd_search_name,
            SimpleNamespace(name="Arrabiata"),
            {"meals": None},
        )
        self.assertEqual(rc, 0)
        self.assertEqual(payload["command"], "search.name")
        self.assertEqual(payload["count"], 0)
        self.assertFalse(payload["found"])
        self.assertEqual(calls[0]["params"], {"s": "Arrabiata"})

    def test_search_first_letter_requires_one_letter(self) -> None:
        with self.assertRaises(ValidationError):
            meals_cmd.cmd_search_first_letter(SimpleNamespace(letter="ab"), {})

    def test_lookup_id_uses_i_param(self) -> None:
        rc, payload, calls = self._run_command(
            meals_cmd.cmd_lookup_id,
            SimpleNamespace(meal_id="52772"),
            {"meals": [{"idMeal": "52772", "strMeal": "Teriyaki Chicken Casserole"}]},
        )
        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["meal_id"], "52772")
        self.assertEqual(calls[0]["params"], {"i": "52772"})

    def test_list_areas_returns_items(self) -> None:
        rc, payload, calls = self._run_command(
            meals_cmd.cmd_list_areas,
            SimpleNamespace(),
            {"meals": [{"strArea": "Canadian", "strCountry": "Canada"}]},
        )
        self.assertEqual(rc, 0)
        self.assertEqual(payload["item_kind"], "area")
        self.assertEqual(payload["count"], 1)
        self.assertEqual(calls[0]["params"], {"a": "list"})

    def test_filter_category_passes_c_param(self) -> None:
        rc, payload, calls = self._run_command(
            meals_cmd.cmd_filter_category,
            SimpleNamespace(category="Seafood"),
            {"meals": [{"idMeal": "52959", "strMeal": "Baked salmon with fennel & tomatoes"}]},
        )
        self.assertEqual(rc, 0)
        self.assertEqual(payload["command"], "filter.category")
        self.assertEqual(calls[0]["params"], {"c": "Seafood"})
