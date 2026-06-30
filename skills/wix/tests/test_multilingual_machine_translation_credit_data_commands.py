from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import multilingual_machine_translation_credit_data
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def __init__(self) -> None:
        self.writes: list[tuple[str, dict]] = []

    def write(self, action: str, payload: dict) -> None:
        self.writes.append((action, payload))


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestMultilingualMachineTranslationCreditDataCommands(unittest.TestCase):
    def _ctx(self) -> dict:
        cfg = SimpleNamespace(
            base_url="https://www.wixapis.com",
            timeout_s=30.0,
            access_token="site-token",
            api_key=None,
            account_id=None,
            app_id=None,
            app_secret=None,
            instance_id=None,
            has_official_app_auth=False,
        )
        return {
            "cfg": cfg,
            "env_file": "/tmp/.env",
            "tool": "wix-safe-agent-cli",
            "tool_version": "0.0.0",
            "command_str": "wix-safe-agent-cli multilingual-machine-translation-credit-data",
            "apply": False,
            "yes": False,
            "verbose": False,
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
        }

    def test_parser_recognizes_credit_data_commands(self) -> None:
        parser = build_parser()
        cases = [
            (["multilingual-machine-translation-credit-data", "get"], "get"),
            (["multilingual-machine-translation-credit-data", "check-sufficient", "--word-count", "100"], "check-sufficient"),
        ]
        for argv, command in cases:
            parsed = parser.parse_args(argv)
            self.assertEqual(parsed.multilingual_machine_translation_credit_data_cmd, command)
            self.assertFalse(parsed.write_capable)

    @patch("wix_safe_agent_cli.commands.multilingual_machine_translation_credit_data.HttpClient")
    def test_get_uses_official_get_path(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"creditData": {"creditsUsed": 10}})
        buf = io.StringIO()
        ctx = self._ctx()
        with redirect_stdout(buf):
            rc = multilingual_machine_translation_credit_data.cmd_multilingual_machine_translation_credit_data_get(SimpleNamespace(), ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["method"], "multilingual-machine-translation-credit-data.get")
        self.assertEqual(payload["request"], {"method": "GET", "path": "/translation-credits/v1/credit"})
        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["method"], "GET")
        self.assertTrue(str(call.kwargs["url"]).endswith("/translation-credits/v1/credit"))
        self.assertEqual(call.kwargs["headers"]["Authorization"], "site-token")
        self.assertIsNone(call.kwargs["json_body"])
        self.assertEqual(ctx["audit"].writes[0][0], "multilingual-machine-translation-credit-data.get")

    @patch("wix_safe_agent_cli.commands.multilingual_machine_translation_credit_data.HttpClient")
    def test_check_sufficient_uses_post_body(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"sufficientCredits": True})
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = multilingual_machine_translation_credit_data.cmd_multilingual_machine_translation_credit_data_check_sufficient(
                SimpleNamespace(word_count=100),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["method"], "POST")
        self.assertEqual(payload["request"]["path"], "/translation-credits/v1/credit/is-eligible")
        self.assertEqual(payload["request"]["body"], {"wordCount": 100})
        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["method"], "POST")
        self.assertTrue(str(call.kwargs["url"]).endswith("/translation-credits/v1/credit/is-eligible"))
        self.assertEqual(call.kwargs["json_body"], {"wordCount": 100})
        self.assertEqual(call.kwargs["headers"]["Content-Type"], "application/json")

    def test_check_sufficient_rejects_negative_word_count(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = multilingual_machine_translation_credit_data.cmd_multilingual_machine_translation_credit_data_check_sufficient(
                SimpleNamespace(word_count=-1),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertIn("at least 0", payload["error"])


if __name__ == "__main__":
    unittest.main()
