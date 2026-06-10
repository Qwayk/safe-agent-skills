from __future__ import annotations

import io
import json
from pathlib import Path
import tempfile
import unittest
from contextlib import redirect_stdout
from typing import Any
from unittest.mock import patch

from qwayk_pipedrive_safe_agent_cli.cli import main


class _Response:
    def __init__(self, status: int, body: dict[str, object], url: str) -> None:
        self.status = status
        self.headers = {}
        self.body = json.dumps(body).encode("utf-8")
        self.url = url

    def json(self) -> object:
        return json.loads(self.body.decode("utf-8"))


class _HttpClient:
    def __init__(self, timeout_s: float, verbose: bool, user_agent: str) -> None:
        self.requests: list[tuple[str, str, dict[str, str], dict[str, Any] | None]] = []
        self._response = _Response(200, {"data": []}, "https://api.test.pipedrive.com/api/v1/placeholder")

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        **kwargs: object,
    ) -> _Response:
        self.requests.append((method, url, dict(headers or {}), params))
        return self._response


def _load_catalog(root: Path) -> list[dict[str, Any]]:
    return json.loads((root / "src" / ".openapi" / "pipedrive_endpoint_catalog.json").read_text(encoding="utf-8"))


def _sample_value(param: dict[str, Any]) -> str:
    enum = param.get("enum")
    if isinstance(enum, list) and enum:
        return str(enum[0])
    ptype = str(param.get("type") or "").strip().lower()
    if ptype in {"integer", "number"}:
        return "1"
    if ptype in {"boolean"}:
        return "1"
    return "sample"


def _required_specs(entry: dict[str, Any]) -> list[tuple[str, str, str, str]]:
    required: list[tuple[str, str, str, str]] = []
    for section in ("path_parameters", "query_parameters"):
        for p in entry.get(section, []):
            if not isinstance(p, dict):
                continue
            if not bool(p.get("required")):
                continue
            name = str(p.get("name") or "").strip()
            flag = str(p.get("flag") or name).strip()
            if not flag or not name:
                continue
            required.append((section, flag, name, _sample_value(p)))
    return required


def _pick_family_representatives(entries: list[dict[str, Any]]) -> list[tuple[str, dict[str, Any]]]:
    chosen: dict[str, dict[str, Any]] = {}
    for entry in entries:
        if not str(entry.get("operation") or "").startswith("GET "):
            continue
        tokens = entry.get("command_tokens")
        if not isinstance(tokens, list) or len(tokens) != 2:
            continue
        family = str(tokens[0]).strip()
        if not family:
            continue
        req = _required_specs(entry)
        score = len(req)
        current = chosen.get(family)
        if current is None or score < len(_required_specs(current["entry"])):
            chosen[family] = {"entry": entry, "required": req}
        elif current is not None and score == len(_required_specs(current["entry"])):
            if entry.get("command_tokens", [])[1] < current["entry"]["command_tokens"][1]:
                chosen[family] = {"entry": entry, "required": req}

    return sorted([(family, payload["entry"]) for family, payload in chosen.items()], key=lambda item: item[0])


class TestGeneratedFamilySmoke(unittest.TestCase):
    def _write_env(self, root: str, token: str = "token-xyz", domain: str = "test-company") -> str:
        env_path = Path(root) / ".env"
        env_path.write_text(f"PIPEDRIVE_API_TOKEN={token}\nPIPEDRIVE_API_DOMAIN={domain}\n", encoding="utf-8")
        return str(env_path)

    def test_each_family_has_one_runtime_smoke(self) -> None:
        root = Path(__file__).resolve().parents[1]
        entries = _load_catalog(root)
        families = _pick_family_representatives(entries)
        self.assertGreater(len(families), 0)

        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            client = _HttpClient(30.0, False, "qwayk")
            with patch("qwayk_pipedrive_safe_agent_cli.cli.HttpClient", return_value=client):
                for family, entry in families:
                    args = ["--output", "json", "--env-file", env_path]
                    command = list(entry["command_tokens"])
                    args.extend(command)
                    for section, flag, _name, value in _required_specs(entry):
                        args.extend([f"--{flag}", value])
                    buf = io.StringIO()
                    with redirect_stdout(buf):
                        rc = main(args)
                    payload = json.loads(buf.getvalue())
                    self.assertEqual(rc, 0, family)
                    self.assertEqual(payload["http"]["method"], "GET")
                    self.assertEqual(payload["operation"].split(" ", 1)[0], "GET")
                    self.assertNotIn("{", payload["request"]["path"])
                    for section, _flag, name, value in _required_specs(entry):
                        target = payload["request"]["path_parameters"] if section == "path_parameters" else payload["request"]["query"]
                        self.assertEqual(str(target[name]), value)

            self.assertEqual(len(client.requests), len(families))
