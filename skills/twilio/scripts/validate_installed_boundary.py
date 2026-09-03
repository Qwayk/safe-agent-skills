"""Validate the two manually completed commands from an installed wheel."""

from __future__ import annotations

import contextlib
import io
import json
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import Mock

from twilio_safe_agent_cli import __version__
from twilio_safe_agent_cli.cli import build_parser
from twilio_safe_agent_cli.config import Config
from twilio_safe_agent_cli.errors import SafetyError, ToolError, ValidationError
from twilio_safe_agent_cli.redaction import write_protected_json
from twilio_safe_agent_cli.registry import load_registry
from twilio_safe_agent_cli.runtime import execute_operation, execute_read, prepare_request


def _must_refuse(operation: dict[str, Any], input_obj: dict[str, Any], cfg: Config) -> None:
    try:
        prepare_request(operation, input_obj, cfg)
    except ValidationError:
        return
    raise AssertionError("installed command accepted input outside its fixed contract")


def _must_refuse_snapshot(
    operation: dict[str, Any],
    input_obj: dict[str, Any],
    cfg: Config,
    registry: Any,
    snapshot: Path,
) -> None:
    try:
        execute_operation(
            operation,
            input_obj,
            cfg,
            registry=registry,
            tool_version=__version__,
            apply=False,
            yes=False,
            plan_out=None,
            plan_in=None,
            receipt_out=None,
            snapshot_in=str(snapshot),
            acknowledgements={},
            target_count=None,
            sensitive_out=None,
        )
    except SafetyError:
        return
    raise AssertionError("installed command accepted an unbound snapshot")


def main() -> None:
    registry = load_registry()
    assert registry.summary()["commands"] == 1_333
    assert registry.summary()["private_or_unavailable"] == 6

    help_stdout = io.StringIO()
    try:
        with contextlib.redirect_stdout(help_stdout):
            build_parser(registry).parse_args(["api-v2010", "fetch-account", "--help"])
    except SystemExit as exc:
        assert exc.code == 0
    else:
        raise AssertionError("installed operation help did not exit after --help")
    help_text = help_stdout.getvalue().lower()
    assert "protected current-state snapshot" in help_text
    assert "sensitive provider output" in help_text
    assert "reversible update" not in help_text
    assert "full provider result" not in help_text

    basic_cfg = Config(
        account_sid="AC" + "0" * 32,
        api_key_sid="SK" + "1" * 32,
        api_key_secret="test-placeholder",
        auth_token=None,
        oauth_access_token=None,
        region=None,
        edge=None,
        timeout_s=30,
    )
    oauth_cfg = Config(
        account_sid="AC" + "0" * 32,
        api_key_sid=None,
        api_key_secret=None,
        auth_token=None,
        oauth_access_token="test-oauth-placeholder",
        region=None,
        edge=None,
        timeout_s=30,
    )

    scim = registry.get("iam-organizations.patch-organization-user")
    assert scim is not None and scim["snapshot_required"] is True
    scim_input: dict[str, Any] = {
        "path": {"OrganizationSid": "OR" + "0" * 32, "UserSid": "US" + "0" * 32},
        "headers": {"If-Match": "W/13"},
        "content_type": "application/scim+json",
        "body": {
            "schemas": ["urn:ietf:params:scim:api:messages:2.0:PatchOp"],
            "Operations": [{"op": "replace", "path": "active", "value": False}],
        },
    }
    assert prepare_request(scim, scim_input, oauth_cfg).method == "PATCH"
    bad_scim: dict[str, Any] = {
        **scim_input,
        "body": {
            "schemas": ["urn:ietf:params:scim:api:messages:2.0:PatchOp"],
            "Operations": [],
        },
    }
    _must_refuse(scim, bad_scim, oauth_cfg)

    porting = registry.get("numbers-v1.create-porting-webhook-configuration")
    assert porting is not None and porting["snapshot_required"] is True
    assert porting["expected_effect"].startswith("POST overwrites")
    assert prepare_request(
        porting,
        {"body": {"port_in_target_url": "https://hooks.example.com/port-in"}},
        basic_cfg,
    ).method == "POST"
    _must_refuse(porting, {"body": {}}, basic_cfg)
    _must_refuse(
        porting,
        {"body": {"port_in_target_url": "https://intranet/port-in"}},
        basic_cfg,
    )
    _must_refuse(
        porting,
        {
            "body": {
                "port_in_target_url": "https://hooks.example.com/port-in",
                "notifications_of": ["PortInExpired"],
            }
        },
        basic_cfg,
    )

    with tempfile.TemporaryDirectory() as tmp:
        arbitrary_snapshot = Path(tmp) / "arbitrary.json"
        write_protected_json(
            arbitrary_snapshot,
            {"provider_state": {"meta": {"version": "W/13"}}},
        )
        _must_refuse_snapshot(
            scim,
            scim_input,
            oauth_cfg,
            registry,
            arbitrary_snapshot,
        )

    porting_read = registry.get("numbers-v1.fetch-porting-webhook-configuration-fetch")
    assert porting_read is not None
    response = Mock(status_code=200, headers={"Content-Type": "application/json"}, text="{}")
    response.json.return_value = {"port_in_target_url": "https://private.example.com/hook"}
    session = Mock()
    session.request.return_value = response
    safe_read = execute_read(porting_read, {}, basic_cfg, session=session)
    assert "private.example.com" not in json.dumps(safe_read)

    with tempfile.TemporaryDirectory() as tmp:
        snapshot = Path(tmp) / "porting-before.json"
        plan = Path(tmp) / "porting.plan.json"
        receipt = Path(tmp) / "porting.receipt.json"
        execute_read(
            porting_read,
            {},
            basic_cfg,
            session=session,
            sensitive_out=snapshot,
        )
        porting_input = {
            "body": {"port_in_target_url": "https://hooks.example.com/customer-secret"}
        }
        execute_operation(
            porting,
            porting_input,
            basic_cfg,
            registry=registry,
            tool_version=__version__,
            apply=False,
            yes=False,
            plan_out=str(plan),
            plan_in=None,
            receipt_out=None,
            snapshot_in=str(snapshot),
            acknowledgements={},
            target_count=None,
            sensitive_out=None,
        )
        failure_response = Mock(
            status_code=400,
            headers={"Content-Type": "application/json"},
            text="{}",
        )
        failure_response.json.return_value = {
            "detail": "Webhook https://hooks.example.com/customer-secret was rejected"
        }
        failure_session = Mock()
        failure_session.request.return_value = failure_response
        try:
            execute_operation(
                porting,
                porting_input,
                basic_cfg,
                registry=registry,
                tool_version=__version__,
                apply=True,
                yes=True,
                plan_out=None,
                plan_in=str(plan),
                receipt_out=str(receipt),
                snapshot_in=str(snapshot),
                acknowledgements={
                    "ack_identity": True,
                    "ack_preview": True,
                    "ack_production": True,
                },
                target_count=None,
                sensitive_out=None,
                session=failure_session,
            )
        except ToolError as exc:
            assert "customer-secret" not in str(exc)
        else:
            raise AssertionError("installed Porting failure guard did not observe a provider failure")
        assert "customer-secret" not in receipt.read_text(encoding="utf-8")

    scim_read = registry.get("iam-organizations.fetch-organization-user")
    assert scim_read is not None
    error_response = Mock(
        status_code=400,
        headers={"Content-Type": "application/scim+json"},
        text="{}",
    )
    error_response.json.return_value = {"detail": "Private Person private@example.com"}
    error_session = Mock()
    error_session.request.return_value = error_response
    try:
        execute_read(
            scim_read,
            {"path": scim_input["path"]},
            oauth_cfg,
            session=error_session,
        )
    except ToolError as exc:
        assert "Private Person" not in str(exc)
        assert "private@example.com" not in str(exc)
    else:
        raise AssertionError("installed SCIM error guard did not observe a provider failure")

    print(
        "installed boundary validated: SCIM PATCH and Porting overwrite, "
        "snapshot binding, public HTTPS hosts, operation-specific redaction, and accurate help"
    )


if __name__ == "__main__":
    main()
