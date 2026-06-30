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
from wix_safe_agent_cli.commands import app_installation
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


class TestAppInstallationParser(unittest.TestCase):
    def test_parser_recognizes_all_app_installation_commands(self) -> None:
        parser = build_parser()

        get_installed = parser.parse_args(["app-installation", "get-installed"])
        self.assertEqual(get_installed.app_installation_cmd, "get-installed")
        self.assertFalse(get_installed.write_capable)
        self.assertEqual(get_installed.func.__name__, "cmd_app_installation_get_installed")

        is_permitted = parser.parse_args(
            ["app-installation", "is-permitted", "--request-json", '{"installType":"SITE"}']
        )
        self.assertEqual(is_permitted.app_installation_cmd, "is-permitted")
        self.assertFalse(is_permitted.write_capable)
        self.assertEqual(is_permitted.func.__name__, "cmd_app_installation_is_permitted")

        install = parser.parse_args(
            [
                "app-installation",
                "install",
                "--tenant-json",
                '{"id":"tenant-1","tenantType":"SITE"}',
                "--app-def-id",
                "app-def-1",
            ]
        )
        self.assertEqual(install.app_installation_cmd, "install")
        self.assertTrue(install.write_capable)
        self.assertEqual(install.func.__name__, "cmd_app_installation_install")

        install_from_share = parser.parse_args(
            [
                "app-installation",
                "install-from-share-url",
                "--tenant-json",
                '{"id":"tenant-1","tenantType":"SITE"}',
                "--share-url-id",
                "share-1",
            ]
        )
        self.assertEqual(install_from_share.app_installation_cmd, "install-from-share-url")
        self.assertTrue(install_from_share.write_capable)
        self.assertEqual(install_from_share.func.__name__, "cmd_app_installation_install_from_share_url")

        uninstall = parser.parse_args(
            [
                "app-installation",
                "uninstall",
                "--tenant-json",
                '{"id":"tenant-1","tenantType":"SITE"}',
                "--app-def-id",
                "app-def-1",
            ]
        )
        self.assertEqual(uninstall.app_installation_cmd, "uninstall")
        self.assertTrue(uninstall.write_capable)
        self.assertEqual(uninstall.func.__name__, "cmd_app_installation_uninstall")

        bulk_install = parser.parse_args(
            [
                "app-installation",
                "bulk-install",
                "--tenant-json",
                '{"id":"tenant-1","tenantType":"SITE"}',
                "--app-instances-json",
                '[{"appDefId":"app-def-1"}]',
            ]
        )
        self.assertEqual(bulk_install.app_installation_cmd, "bulk-install")
        self.assertTrue(bulk_install.write_capable)
        self.assertEqual(bulk_install.func.__name__, "cmd_app_installation_bulk_install")

        bulk_uninstall = parser.parse_args(
            [
                "app-installation",
                "bulk-uninstall",
                "--tenant-json",
                '{"id":"tenant-1","tenantType":"SITE"}',
                "--app-def-ids-json",
                '["app-def-1"]',
            ]
        )
        self.assertEqual(bulk_uninstall.app_installation_cmd, "bulk-uninstall")
        self.assertTrue(bulk_uninstall.write_capable)
        self.assertEqual(bulk_uninstall.func.__name__, "cmd_app_installation_bulk_uninstall")


class TestAppInstallationCommands(unittest.TestCase):
    def _ctx(self, **overrides) -> dict:
        cfg = SimpleNamespace(
            base_url="https://www.wixapis.com",
            timeout_s=30.0,
            access_token="token-abc",
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
            "command_str": "wix-safe-agent-cli app-installation",
            "apply": False,
            "yes": False,
            "verbose": False,
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
            "plan_in": None,
            "plan_out": None,
            "receipt_out": None,
            "ack_irreversible": False,
        }
        ctx.update(overrides)
        return ctx

    def _run(self, func, args, ctx: dict) -> tuple[int, dict]:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = func(args, ctx)
        return rc, json.loads(buf.getvalue())

    def _build_plan_file(self, func, args) -> str:
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as handle:
            plan_path = handle.name

        try:
            rc, payload = self._run(func, args, self._ctx(plan_out=plan_path))
            self.assertEqual(rc, 0)
            self.assertTrue(payload["dry_run"])
            self.assertTrue(Path(plan_path).exists())
            return plan_path
        except Exception:
            Path(plan_path).unlink(missing_ok=True)
            raise

    def test_get_installed_request_shape_and_response_redaction(self) -> None:
        args = SimpleNamespace()
        ctx = self._ctx()

        with patch("wix_safe_agent_cli.commands.app_installation.HttpClient") as mock_client:
            mock_client.return_value.request.return_value = _DummyResponse(
                {"appInstances": [{"id": "inst-1", "appToken": "secret-token"}]}
            )
            rc, payload = self._run(app_installation.cmd_app_installation_get_installed, args, ctx)

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(payload["request"]["path"], "/apps-installer-service/v1/app-instances")
        self.assertEqual(payload["response"]["appInstances"][0]["appToken"], "***REDACTED***")

        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["method"], "GET")
        self.assertTrue(str(call.kwargs["url"]).endswith("/apps-installer-service/v1/app-instances"))
        self.assertEqual(call.kwargs["headers"]["Authorization"], "token-abc")
        self.assertNotIn("Content-Type", call.kwargs["headers"])

    def test_is_permitted_request_shape(self) -> None:
        args = SimpleNamespace(request_json='{"installType":"SITE","tenant":{"id":"tenant-1"}}')
        ctx = self._ctx()

        with patch("wix_safe_agent_cli.commands.app_installation.HttpClient") as mock_client:
            mock_client.return_value.request.return_value = _DummyResponse({"permitted": True})
            rc, payload = self._run(app_installation.cmd_app_installation_is_permitted, args, ctx)

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["method"], "POST")
        self.assertEqual(
            payload["request"]["path"],
            "/apps-installer-service/v1/app-instance/is-permitted-to-install",
        )
        self.assertEqual(payload["request"]["body"]["installType"], "SITE")
        self.assertEqual(mock_client.return_value.request.call_args.kwargs["json_body"]["installType"], "SITE")

    def test_is_permitted_rejects_missing_install_type(self) -> None:
        args = SimpleNamespace(request_json='{"tenant":{"id":"tenant-1"}}')
        ctx = self._ctx()

        rc, payload = self._run(app_installation.cmd_app_installation_is_permitted, args, ctx)

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertIn("installType", payload["error"])

    @patch("wix_safe_agent_cli.commands.app_installation.HttpClient")
    def test_write_commands_dry_run_emit_plan_and_do_not_call_http(self, mock_client: unittest.mock.MagicMock) -> None:
        cases = [
            (
                app_installation.cmd_app_installation_install,
                SimpleNamespace(
                    tenant_json='{"id":"tenant-1","tenantType":"SITE"}',
                    app_def_id="app-def-1",
                    enabled="false",
                    version="1.2.3",
                ),
                "/apps-installer-service/v1/app-instance/install",
            ),
            (
                app_installation.cmd_app_installation_install_from_share_url,
                SimpleNamespace(
                    tenant_json='{"id":"tenant-1","tenantType":"SITE"}',
                    share_url_id="share-1",
                    dev_override_id="override-1",
                ),
                "/apps-installer-service/v1/app-share-url/install",
            ),
            (
                app_installation.cmd_app_installation_uninstall,
                SimpleNamespace(
                    tenant_json='{"id":"tenant-1","tenantType":"SITE"}',
                    app_def_id="app-def-1",
                ),
                "/apps-installer-service/v1/app-instance/uninstall",
            ),
            (
                app_installation.cmd_app_installation_bulk_install,
                SimpleNamespace(
                    tenant_json='{"id":"tenant-1","tenantType":"SITE"}',
                    app_instances_json='[{"appDefId":"app-def-1","enabled":true},{"appDefId":"app-def-2","version":"2.0.0"}]',
                ),
                "/apps-installer-service/v1/bulk/app-instance/install",
            ),
            (
                app_installation.cmd_app_installation_bulk_uninstall,
                SimpleNamespace(
                    tenant_json='{"id":"tenant-1","tenantType":"SITE"}',
                    app_def_ids_json='["app-def-1","app-def-2"]',
                ),
                "/apps-installer-service/v1/bulk/app-instance/uninstall",
            ),
        ]

        for func, args, path in cases:
            with self.subTest(path=path):
                mock_client.return_value.request.reset_mock()
                rc, payload = self._run(func, args, self._ctx())
                self.assertEqual(rc, 0)
                self.assertTrue(payload["dry_run"])
                self.assertEqual(payload["plan"]["request"]["path"], path)
                self.assertEqual(mock_client.return_value.request.call_count, 0)

    @patch("wix_safe_agent_cli.commands.app_installation.HttpClient")
    def test_write_commands_refuse_apply_without_plan_in_before_http(self, mock_client: unittest.mock.MagicMock) -> None:
        cases = [
            (
                app_installation.cmd_app_installation_install,
                SimpleNamespace(
                    tenant_json='{"id":"tenant-1","tenantType":"SITE"}',
                    app_def_id="app-def-1",
                    enabled="true",
                    version=None,
                ),
            ),
            (
                app_installation.cmd_app_installation_install_from_share_url,
                SimpleNamespace(
                    tenant_json='{"id":"tenant-1","tenantType":"SITE"}',
                    share_url_id="share-1",
                    dev_override_id=None,
                ),
            ),
            (
                app_installation.cmd_app_installation_uninstall,
                SimpleNamespace(
                    tenant_json='{"id":"tenant-1","tenantType":"SITE"}',
                    app_def_id="app-def-1",
                ),
            ),
            (
                app_installation.cmd_app_installation_bulk_install,
                SimpleNamespace(
                    tenant_json='{"id":"tenant-1","tenantType":"SITE"}',
                    app_instances_json='[{"appDefId":"app-def-1"}]',
                ),
            ),
            (
                app_installation.cmd_app_installation_bulk_uninstall,
                SimpleNamespace(
                    tenant_json='{"id":"tenant-1","tenantType":"SITE"}',
                    app_def_ids_json='["app-def-1"]',
                ),
            ),
        ]

        for func, args in cases:
            with self.subTest(func=func.__name__):
                mock_client.return_value.request.reset_mock()
                rc, payload = self._run(
                    func,
                    args,
                    self._ctx(apply=True, yes=True, ack_irreversible=True),
                )
                self.assertEqual(rc, 0)
                self.assertTrue(payload["dry_run"])
                self.assertTrue(payload["refused"])
                self.assertEqual(mock_client.return_value.request.call_count, 0)

    def test_install_apply_posts_expected_body_and_redacts_app_token(self) -> None:
        args = SimpleNamespace(
            tenant_json='{"id":"tenant-1","tenantType":"SITE"}',
            app_def_id="app-def-1",
            enabled="false",
            version="1.2.3",
        )
        plan_path = self._build_plan_file(app_installation.cmd_app_installation_install, args)

        try:
            with patch("wix_safe_agent_cli.commands.app_installation.HttpClient") as mock_client:
                mock_client.return_value.request.return_value = _DummyResponse(
                    {
                        "appInstance": {
                            "id": "inst-1",
                            "appDefId": "app-def-1",
                            "enabled": False,
                            "version": "1.2.3",
                            "appToken": "secret-token",
                        }
                    }
                )
                rc, payload = self._run(
                    app_installation.cmd_app_installation_install,
                    args,
                    self._ctx(apply=True, yes=True, ack_irreversible=True, plan_in=plan_path),
                )

            self.assertEqual(rc, 0)
            self.assertFalse(payload["dry_run"])
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["receipt"]["response"]["appInstance"]["appToken"], "***REDACTED***")
            self.assertEqual(payload["receipt"]["verification"]["type"], "provider-response")
            self.assertIn("appInstance.id", payload["receipt"]["verification"]["notes"])

            call = mock_client.return_value.request.call_args
            self.assertEqual(call.kwargs["method"], "POST")
            self.assertTrue(str(call.kwargs["url"]).endswith("/apps-installer-service/v1/app-instance/install"))
            self.assertEqual(
                call.kwargs["json_body"],
                {
                    "tenant": {"id": "tenant-1", "tenantType": "SITE"},
                    "appInstance": {"appDefId": "app-def-1", "enabled": False, "version": "1.2.3"},
                },
            )
        finally:
            Path(plan_path).unlink(missing_ok=True)

    def test_uninstall_apply_posts_expected_body_and_allows_empty_response(self) -> None:
        args = SimpleNamespace(
            tenant_json='{"id":"tenant-1","tenantType":"SITE"}',
            app_def_id="app-def-1",
        )
        plan_path = self._build_plan_file(app_installation.cmd_app_installation_uninstall, args)

        try:
            with patch("wix_safe_agent_cli.commands.app_installation.HttpClient") as mock_client:
                mock_client.return_value.request.return_value = _DummyResponse({})
                rc, payload = self._run(
                    app_installation.cmd_app_installation_uninstall,
                    args,
                    self._ctx(apply=True, yes=True, ack_irreversible=True, plan_in=plan_path),
                )

            self.assertEqual(rc, 0)
            self.assertFalse(payload["dry_run"])
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["receipt"]["response"], {})
            self.assertIn("empty", payload["receipt"]["verification"]["notes"])

            call = mock_client.return_value.request.call_args
            self.assertEqual(call.kwargs["method"], "POST")
            self.assertTrue(str(call.kwargs["url"]).endswith("/apps-installer-service/v1/app-instance/uninstall"))
            self.assertEqual(
                call.kwargs["json_body"],
                {"tenant": {"id": "tenant-1", "tenantType": "SITE"}, "appDefId": "app-def-1"},
            )
        finally:
            Path(plan_path).unlink(missing_ok=True)

    def test_invalid_bulk_limits_and_required_fields(self) -> None:
        cases = [
            (
                app_installation.cmd_app_installation_install,
                SimpleNamespace(
                    tenant_json='{"id":"tenant-1"}',
                    app_def_id="app-def-1",
                    enabled="true",
                    version=None,
                ),
                "tenantType",
            ),
            (
                app_installation.cmd_app_installation_bulk_install,
                SimpleNamespace(
                    tenant_json='{"id":"tenant-1","tenantType":"SITE"}',
                    app_instances_json=json.dumps([{"version": "1.0"}]),
                ),
                "appDefId",
            ),
            (
                app_installation.cmd_app_installation_bulk_install,
                SimpleNamespace(
                    tenant_json='{"id":"tenant-1","tenantType":"SITE"}',
                    app_instances_json=json.dumps([{"appDefId": f"app-{i}"} for i in range(21)]),
                ),
                "more than 20",
            ),
            (
                app_installation.cmd_app_installation_bulk_uninstall,
                SimpleNamespace(
                    tenant_json='{"id":"tenant-1","tenantType":"SITE"}',
                    app_def_ids_json=json.dumps([f"app-{i}" for i in range(21)]),
                ),
                "more than 20",
            ),
        ]

        for func, args, expected in cases:
            with self.subTest(func=func.__name__):
                rc, payload = self._run(func, args, self._ctx())
                self.assertEqual(rc, 1)
                self.assertFalse(payload["ok"])
                self.assertIn(expected, payload["error"])
