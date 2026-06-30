from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import multilingual_machine_translation
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = action, payload


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestMultilingualMachineTranslationCommands(unittest.TestCase):
    def _ctx(self, **overrides) -> dict:
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
        ctx = {
            "cfg": cfg,
            "env_file": "/tmp/.env",
            "tool": "wix-safe-agent-cli",
            "tool_version": "0.0.0",
            "command_str": "wix-safe-agent-cli multilingual-machine-translation",
            "apply": False,
            "yes": False,
            "verbose": False,
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
            "plan_in": None,
            "plan_out": None,
            "receipt_out": None,
            "ack_irreversible": False,
            "enforce_reviewed_plan": False,
        }
        ctx.update(overrides)
        return ctx

    def test_parser_recognizes_commands(self) -> None:
        parser = build_parser()
        content = '{"id":"content-1","format":"PLAIN_TEXT","plainTextContent":"Hello"}'
        cases = [
            (["multilingual-machine-translation", "translate", "--source-language", "EN", "--target-language", "IT", "--content-json", content], "translate"),
            (["multilingual-machine-translation", "bulk-translate", "--source-language", "EN", "--target-language", "IT", "--contents-json", f"[{content}]"], "bulk-translate"),
        ]
        for argv, command in cases:
            parsed = parser.parse_args(argv)
            self.assertEqual(parsed.multilingual_machine_translation_cmd, command)
            self.assertTrue(parsed.write_capable)

    def test_translate_dry_run_builds_credit_spend_plan(self) -> None:
        args = SimpleNamespace(source_language="EN", target_language="IT", content_json='{"id":"content-1","format":"PLAIN_TEXT","plainTextContent":"Hello"}')
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = multilingual_machine_translation.cmd_multilingual_machine_translation_translate(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["request"]["path"], "/machine-translation/v3/machine-translate")
        self.assertIn("translation-credit-spend", payload["plan"]["risk_reasons"])
        self.assertIn("apply requires --ack-irreversible because successful translation consumes word credits", payload["plan"]["preconditions"])

    def test_same_language_is_refused_before_plan(self) -> None:
        args = SimpleNamespace(source_language="EN", target_language="en", content_json='{"id":"content-1","format":"PLAIN_TEXT","plainTextContent":"Hello"}')
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = multilingual_machine_translation.cmd_multilingual_machine_translation_translate(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertIn("different", payload["error"])

    def test_bulk_translate_validates_max_1000(self) -> None:
        contents = [{"id": f"c-{i}", "format": "PLAIN_TEXT", "plainTextContent": "Hello"} for i in range(1001)]
        args = SimpleNamespace(source_language="EN", target_language="IT", contents_json=json.dumps(contents))
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = multilingual_machine_translation.cmd_multilingual_machine_translation_bulk_translate(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertIn("1000", payload["error"])

    @patch("wix_safe_agent_cli.commands.multilingual_machine_translation.HttpClient")
    def test_bulk_translate_apply_with_ack_uses_official_path(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"results": [{"id": "content-1"}]})
        args = SimpleNamespace(source_language="EN", target_language="IT", contents_json='[{"id":"content-1","format":"PLAIN_TEXT","plainTextContent":"Hello"}]')
        ctx = self._ctx(apply=True, yes=True, ack_irreversible=True)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = multilingual_machine_translation.cmd_multilingual_machine_translation_bulk_translate(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertFalse(payload["dry_run"])
        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["method"], "POST")
        self.assertTrue(str(call.kwargs["url"]).endswith("/machine-translation/v3/bulk-machine-translate"))
        self.assertEqual(call.kwargs["headers"]["Authorization"], "site-token")
        self.assertEqual(call.kwargs["json_body"]["sourceLanguage"], "EN")

    def test_plan_in_mismatch_is_refused(self) -> None:
        args = SimpleNamespace(source_language="EN", target_language="IT", content_json='{"id":"content-1","format":"PLAIN_TEXT","plainTextContent":"Hello"}')
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as handle:
            json.dump(
                {
                    "method": "multilingual-machine-translation.translate",
                    "baseline": {
                        "env_fingerprint": "https://other.example",
                        "selector": {
                            "kind": "wix-multilingual-machine-translation",
                            "operation": "translate",
                            "source_language": "EN",
                            "target_language": "IT",
                            "content_id": "content-1",
                        },
                    },
                },
                handle,
            )
            plan_path = handle.name
        try:
            ctx = self._ctx(apply=True, yes=True, ack_irreversible=True, plan_in=plan_path)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = multilingual_machine_translation.cmd_multilingual_machine_translation_translate(args, ctx)
            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["refused"])
        finally:
            Path(plan_path).unlink()


if __name__ == "__main__":
    unittest.main()
