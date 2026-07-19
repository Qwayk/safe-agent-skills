"""Validate the fixed Xero boundary from an installed wheel without provider requests."""

from __future__ import annotations

import contextlib
import io
import json
import pkgutil
import tempfile
from pathlib import Path
from typing import Any

import xero_safe_agent_cli
from xero_safe_agent_cli.auth import TokenStore
from xero_safe_agent_cli.cli import build_parser, main
from xero_safe_agent_cli.http import HttpResponse
from xero_safe_agent_cli.registry import load_registry
from xero_safe_agent_cli.runtime import ExecutionOptions, XeroRuntime
from xero_safe_agent_cli.tenants import TenantStore


class FakeTransport:
    def __init__(self, responses: list[HttpResponse]):
        self.responses = list(responses)
        self.calls: list[dict[str, Any]] = []

    def request(self, method: str, url: str, **kwargs: Any) -> HttpResponse:
        self.calls.append({"method": method, "url": url, **kwargs})
        if not self.responses:
            raise AssertionError("installed-boundary test attempted an unexpected provider request")
        return self.responses.pop(0)


def _json_cli(argv: list[str]) -> tuple[int, dict[str, Any]]:
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        code = main(argv)
    rendered = stdout.getvalue()
    decoder = json.JSONDecoder()
    value, end = decoder.raw_decode(rendered)
    assert not rendered[end:].strip(), "JSON mode emitted more than one stdout value"
    assert isinstance(value, dict)
    return code, value


def main_check() -> None:
    registry = load_registry()
    assert registry.summary()["commands"] == 474
    assert registry.summary()["openapi_operations"] == 477
    parser = build_parser(registry)
    parser_text = parser.format_help()
    assert "raw-request" not in parser_text
    assert "generic-request" not in parser_text

    packaged_modules = {
        module.name for module in pkgutil.walk_packages(xero_safe_agent_cli.__path__)
    }
    assert "commands" not in packaged_modules
    assert registry.get("accounting.get-invoices") is not None
    assert registry.get("accounting.create-invoices") is not None
    assert registry.get("payroll-au.get-timesheets") is None

    code, summary = _json_cli(["inventory", "summary"])
    assert code == 0 and summary["commands"] == 474
    error_code, error = _json_cli([])
    assert error_code == 2 and error["error_type"] == "ValidationError"

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        token_store = TokenStore(root / "oauth" / "token.json")
        token_store.write(
            {
                "access_token": "installed-test-secret",
                "refresh_token": "installed-test-refresh",
                "scope": "accounting.invoices accounting.invoices.read",
            }
        )
        tenant_store = TenantStore(root / "tenant.json")
        tenant_store.write(
            {
                "connection_id": "connection-1",
                "tenant_id": "tenant-1",
                "tenant_name": "Installed Test Organisation",
                "tenant_type": "ORGANISATION",
                "region": "AU",
            }
        )
        sensitive = json.dumps(
            {
                "Invoices": [
                    {
                        "InvoiceNumber": "PRIVATE-1",
                        "Contact": {"EmailAddress": "private@example.com"},
                        "BankAccountNumber": "123456789",
                    }
                ]
            }
        ).encode()
        transport = FakeTransport(
            [
                HttpResponse(
                    status=200,
                    headers={"content-type": "application/json"},
                    body=sensitive,
                    url="https://api.xero.com/api.xro/2.0/Invoices",
                )
            ]
        )
        runtime = XeroRuntime(registry, transport, token_store, tenant_store)
        read_result = runtime.execute(
            "accounting.get-invoices",
            {"query": {"Statuses": ["AUTHORISED"]}},
            ExecutionOptions(),
        )
        rendered = json.dumps(read_result)
        assert "private@example.com" not in rendered
        assert "123456789" not in rendered
        assert "installed-test-secret" not in rendered

        plan_path = root / "plans" / "invoice.json"
        planned = runtime.execute(
            "accounting.create-invoices",
            {"body": {"Invoices": [{"Type": "ACCREC", "Status": "DRAFT"}]}},
            ExecutionOptions(plan_out=plan_path),
        )
        assert planned["dry_run"] is True and planned["no_snapshot"] is True
        assert plan_path.exists() and plan_path.stat().st_mode & 0o777 == 0o600
        assert len(transport.calls) == 1, "planning a collection create made a provider write"

        token_store.write({"access_token": "installed-test-secret", "scope": "files"})
        upload = root / "reviewed.pdf"
        upload.write_bytes(b"reviewed installed file")
        file_plan_path = root / "plans" / "file.json"
        runtime.execute(
            "files.upload-file",
            {"file_path": str(upload)},
            ExecutionOptions(plan_out=file_plan_path),
        )
        upload.write_bytes(b"changed installed file")
        try:
            runtime.execute(
                "files.upload-file",
                {},
                ExecutionOptions(
                    apply=True,
                    plan_in=file_plan_path,
                    approve=True,
                    approve_high_risk=True,
                    ack_no_snapshot=True,
                ),
            )
        except Exception as exc:  # noqa: BLE001
            assert "file changed after planning" in str(exc)
        else:
            raise AssertionError("installed wheel accepted file bytes changed after planning")
        assert len(transport.calls) == 1, "changed planned file reached the provider transport"

    print(
        "installed boundary validated: 474 fixed commands, pinned catalog, one-object JSON, "
        "protected read output, plan-first writes, and changed-file refusal"
    )


if __name__ == "__main__":
    main_check()
