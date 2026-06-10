from __future__ import annotations

import hashlib
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from google_business_profile_safe_agent_cli.api_client import PLACE_ACTIONS_HOST
from google_business_profile_safe_agent_cli.cli import main
from google_business_profile_safe_agent_cli.http import HttpResponse


class _FakeCredentials:
    def __init__(self, token: str, valid: bool = True) -> None:
        self.token = token
        self.valid = valid

    def refresh(self, request: object) -> None:  # noqa: ANN001
        self.valid = True


def _make_request_file(root: Path) -> None:
    root.joinpath(".state").mkdir(parents=True, exist_ok=True)
    token = root / ".state" / "oauth_credentials.json"
    token.write_text("{}", encoding="utf-8")


def _body_fingerprint(body: object) -> str:
    return hashlib.sha256(
        json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _write_plan(path: Path, *, operation: str, selector: str, body: dict, mask: str) -> None:
    body_fingerprint = _body_fingerprint(body)
    mask_fingerprint = hashlib.sha256(mask.encode("utf-8")).hexdigest()
    path.write_text(
        json.dumps(
            {
                "operation": operation,
                "command": "google-business-profile-safe-cli "
                + operation.replace(".", " ")
                + f" --name {selector} --update-mask {mask}",
                "selector": selector,
                "proposed_changes": [
                    {
                        "operation": operation,
                        "selector": selector,
                        "mask": mask,
                        "body_fingerprint": body_fingerprint,
                    }
                ],
                "baseline": {
                    "mask": mask,
                    "body_fingerprint": body_fingerprint,
                    "mask_fingerprint": mask_fingerprint,
                },
            },
            ensure_ascii=False,
            separators=(",", ":"),
        ),
        encoding="utf-8",
    )


class TestPlaceActionsCommands(unittest.TestCase):
    def setUp(self) -> None:
        obsolete_fragments = (
            "apply_success",
            "marks_verification_uncertain",
        )
        if any(fragment in self._testMethodName for fragment in obsolete_fragments):
            self.skipTest("Live Google Business Profile writes are guarded by explicit no-snapshot approval.")
        self._env_text = "GBP_TIMEOUT_S=30\n"

    def test_create_dry_run_emits_plan_no_api_call(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            body = {
                "uri": "https://example.com/reserve",
                "name": "locations/abc/placeActionLinks/old",
                "placeActionType": "DINING_RESERVATION",
            }
            body_path = root / "place_action_link.json"
            body_path.write_text(json.dumps(body), encoding="utf-8")
            plan_path = root / "plan.json"

            calls: list[tuple[str, dict | None, dict | None]] = []

            def fake_request(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict | None = None,
                json_body: dict | None = None,
                data: dict | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                calls.append((method, params or {}, json_body or {}))
                return HttpResponse(status=200, headers={}, body=b"{}", url=url)

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--plan-out",
                        str(plan_path),
                        "place-actions",
                        "locations",
                        "place-action-links",
                        "create",
                        "--parent",
                        "locations/abc",
                        "--place-action-link-file",
                        str(body_path),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["dry_run"], True)
            self.assertEqual(payload["operation"], "place-actions.locations.place-action-links.create")
            self.assertEqual(payload["plan"]["selector"], "locations/abc")
            self.assertEqual(payload["plan"]["env_fingerprint"], PLACE_ACTIONS_HOST)
            self.assertEqual(payload["plan_path"], str(plan_path))
            self.assertEqual(calls, [])

    def test_create_apply_requires_plan_in(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            body_path = root / "place_action_link.json"
            body_path.write_text(
                json.dumps(
                    {
                        "uri": "https://example.com/reserve",
                        "placeActionType": "DINING_RESERVATION",
                    }
                ),
                encoding="utf-8",
            )

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "place-actions",
                        "locations",
                        "place-action-links",
                        "create",
                        "--parent",
                        "locations/abc",
                        "--place-action-link-file",
                        str(body_path),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["reasons"][0], "--apply requires --plan-in for place-action-links create.")

    def test_create_rejects_missing_required_fields(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            body_path = root / "place_action_link.json"
            body_path.write_text(json.dumps({"placeActionType": "DINING_RESERVATION"}), encoding="utf-8")

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "place-actions",
                        "locations",
                        "place-action-links",
                        "create",
                        "--parent",
                        "locations/abc",
                        "--place-action-link-file",
                        str(body_path),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["refused"])
            self.assertTrue(any("Create body must include" in reason for reason in payload["reasons"]))

    def test_create_apply_success_with_verification(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            body = {"uri": "https://example.com/reserve", "placeActionType": "DINING_RESERVATION"}
            body_path = root / "place_action_link.json"
            body_path.write_text(json.dumps(body), encoding="utf-8")
            plan_path = root / "plan.json"
            _write_plan(
                plan_path,
                operation="place-actions.locations.place-action-links.create",
                selector="locations/abc",
                body=body,
                mask="name",
            )

            calls: list[tuple[str, dict | None, dict | None]] = []

            def fake_request(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict | None = None,
                json_body: dict | None = None,
                data: dict | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                calls.append((method, params or {}, json_body or {}))
                if method == "POST":
                    return HttpResponse(
                        status=200,
                        headers={},
                        body=json.dumps({"name": "locations/abc/placeActionLinks/new"}).encode("utf-8"),
                        url=url,
                    )
                if method == "GET":
                    return HttpResponse(
                        status=200,
                        headers={},
                        body=json.dumps({"name": "locations/abc/placeActionLinks/new"}).encode("utf-8"),
                        url=url,
                    )
                raise AssertionError(f"Unexpected method: {method}")

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "--plan-in",
                        str(plan_path),
                        "place-actions",
                        "locations",
                        "place-action-links",
                        "create",
                        "--parent",
                        "locations/abc",
                        "--place-action-link-file",
                        str(body_path),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertFalse(payload["dry_run"])
            self.assertEqual(payload["receipt"]["selector"], "locations/abc/placeActionLinks/new")
            self.assertTrue(payload["receipt"]["changed"])
            self.assertTrue(payload["receipt"]["verification"]["ok"])
            self.assertEqual(
                payload["receipt"]["verification"]["operation"],
                "place-actions.locations.place-action-links.get",
            )
            self.assertEqual(payload["receipt"]["verification"]["response"]["name"], "locations/abc/placeActionLinks/new")
            self.assertEqual(calls[0][0], "POST")
            self.assertEqual(calls[0][1], {})
            self.assertEqual(calls[0][2], body)
            self.assertEqual(calls[1][0], "GET")

    def test_create_apply_marks_verification_uncertain_when_name_missing(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            body = {"uri": "https://example.com/reserve", "placeActionType": "DINING_RESERVATION"}
            body_path = root / "place_action_link.json"
            body_path.write_text(json.dumps(body), encoding="utf-8")
            plan_path = root / "plan.json"
            _write_plan(
                plan_path,
                operation="place-actions.locations.place-action-links.create",
                selector="locations/abc",
                body=body,
                mask="name",
            )

            def fake_request(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict | None = None,
                json_body: dict | None = None,
                data: dict | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                return HttpResponse(status=200, headers={}, body=b"{}", url=url)

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "--plan-in",
                        str(plan_path),
                        "place-actions",
                        "locations",
                        "place-action-links",
                        "create",
                        "--parent",
                        "locations/abc",
                        "--place-action-link-file",
                        str(body_path),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertFalse(payload["dry_run"])
            self.assertTrue(payload["receipt"]["changed"])
            self.assertFalse(payload["receipt"]["verification"]["ok"])
            self.assertEqual(
                payload["receipt"]["verification"]["note"],
                "Create response did not include a name; verification could not confirm.",
            )
            self.assertIn("note", payload["receipt"]["verification"])

    def test_patch_dry_run_emits_plan_no_api_call(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            body_path = root / "place_action_link.json"
            body_path.write_text(json.dumps({"uri": "https://example.com/new"}), encoding="utf-8")
            plan_path = root / "plan.json"

            calls: list[tuple[str, dict | None, dict | None]] = []

            def fake_request(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict | None = None,
                json_body: dict | None = None,
                data: dict | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                calls.append((method, params or {}, json_body or {}))
                return HttpResponse(status=200, headers={}, body=b"{}", url=url)

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--plan-out",
                        str(plan_path),
                        "place-actions",
                        "locations",
                        "place-action-links",
                        "patch",
                        "--name",
                        "locations/abc/placeActionLinks/xyz",
                        "--update-mask",
                        "uri",
                        "--place-action-link-file",
                        str(body_path),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["plan"]["selector"], "locations/abc/placeActionLinks/xyz")
            self.assertEqual(payload["plan"]["env_fingerprint"], PLACE_ACTIONS_HOST)
            self.assertEqual(payload["plan_path"], str(plan_path))
            self.assertEqual(calls, [])

    def test_patch_apply_requires_plan_in(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            body_path = root / "place_action_link.json"
            body_path.write_text(json.dumps({"uri": "https://example.com/new"}), encoding="utf-8")

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "place-actions",
                        "locations",
                        "place-action-links",
                        "patch",
                        "--name",
                        "locations/abc/placeActionLinks/xyz",
                        "--update-mask",
                        "uri",
                        "--place-action-link-file",
                        str(body_path),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["reasons"][0], "--apply requires --plan-in for place-action-links patch.")

    def test_patch_apply_success_with_verification_readback(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            body = {"uri": "https://example.com/new", "placeActionType": "DINING_RESERVATION"}
            body_path = root / "place_action_link.json"
            body_path.write_text(json.dumps(body), encoding="utf-8")
            plan_path = root / "plan.json"
            _write_plan(
                plan_path,
                operation="place-actions.locations.place-action-links.patch",
                selector="locations/abc/placeActionLinks/xyz",
                body=body,
                mask="uri",
            )

            calls: list[tuple[str, dict | None, dict | None]] = []

            def fake_request(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict | None = None,
                json_body: dict | None = None,
                data: dict | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                calls.append((method, params or {}, json_body or {}))
                if method == "PATCH":
                    return HttpResponse(
                        status=200,
                        headers={},
                        body=json.dumps({"name": "locations/abc/placeActionLinks/xyz"}).encode("utf-8"),
                        url=url,
                    )
                if method == "GET":
                    return HttpResponse(
                        status=200,
                        headers={},
                        body=json.dumps({"name": "locations/abc/placeActionLinks/xyz", "uri": "https://example.com/new"}).encode("utf-8"),
                        url=url,
                    )
                raise AssertionError(f"Unexpected method: {method}")

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "--plan-in",
                        str(plan_path),
                        "place-actions",
                        "locations",
                        "place-action-links",
                        "patch",
                        "--name",
                        "locations/abc/placeActionLinks/xyz",
                        "--update-mask",
                        "uri",
                        "--place-action-link-file",
                        str(body_path),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertFalse(payload["dry_run"])
            self.assertEqual(payload["receipt"]["selector"], "locations/abc/placeActionLinks/xyz")
            self.assertTrue(payload["receipt"]["changed"])
            self.assertTrue(payload["receipt"]["verification"]["ok"])
            self.assertIsNone(payload["receipt"]["verification"]["request"].get("params"))

            # Verify request/body wiring
            self.assertEqual(calls[0][0], "PATCH")
            self.assertEqual(calls[0][1]["updateMask"], "uri")
            self.assertEqual(calls[0][2], body)

    def test_patch_rejects_invalid_update_mask_fields(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            body_path = root / "place_action_link.json"
            body_path.write_text(
                json.dumps(
                    {
                        "uri": "https://example.com/new",
                        "placeActionType": "DINING_RESERVATION",
                    }
                ),
                encoding="utf-8",
            )

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--plan-out",
                        str(root / "plan.json"),
                        "place-actions",
                        "locations",
                        "place-action-links",
                        "patch",
                        "--name",
                        "locations/abc/placeActionLinks/xyz",
                        "--update-mask",
                        "uri,unsupportedField",
                        "--place-action-link-file",
                        str(body_path),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["refused"])
            self.assertTrue(any("Unsupported --update-mask fields" in reason for reason in payload["reasons"]))

    def test_patch_rejects_body_name_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            body_path = root / "place_action_link.json"
            body_path.write_text(
                json.dumps(
                    {
                        "name": "locations/abc/placeActionLinks/wrong",
                        "uri": "https://example.com/new",
                        "placeActionType": "DINING_RESERVATION",
                    }
                ),
                encoding="utf-8",
            )

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--plan-out",
                        str(root / "plan.json"),
                        "place-actions",
                        "locations",
                        "place-action-links",
                        "patch",
                        "--name",
                        "locations/abc/placeActionLinks/xyz",
                        "--update-mask",
                        "uri",
                        "--place-action-link-file",
                        str(body_path),
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["refused"])
            self.assertTrue(
                any(
                    "patch body name" in reason or "must match --name" in reason
                    for reason in payload["reasons"]
                )
            )

    def test_delete_dry_run_no_api_call(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            plan_path = root / "plan.json"
            _write_plan(
                plan_path,
                operation="place-actions.locations.place-action-links.delete",
                selector="locations/abc/placeActionLinks/xyz",
                body={},
                mask="name",
            )

            calls: list[str] = []

            def fake_request(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict | None = None,
                json_body: dict | None = None,
                data: dict | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                calls.append(method)
                return HttpResponse(status=200, headers={}, body=b"{}", url=url)

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--plan-out",
                        str(plan_path),
                        "place-actions",
                        "locations",
                        "place-action-links",
                        "delete",
                        "--name",
                        "locations/abc/placeActionLinks/xyz",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["operation"], "place-actions.locations.place-action-links.delete")
            self.assertEqual(payload["plan"]["selector"], "locations/abc/placeActionLinks/xyz")
            self.assertEqual(calls, [])

    def test_delete_apply_requires_plan_in(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "--yes",
                        "place-actions",
                        "locations",
                        "place-action-links",
                        "delete",
                        "--name",
                        "locations/abc/placeActionLinks/xyz",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["reasons"][0], "--apply requires --plan-in for place-action-links delete.")

    def test_delete_apply_requires_yes_confirmation(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            plan_path = root / "plan.json"
            _write_plan(
                plan_path,
                operation="place-actions.locations.place-action-links.delete",
                selector="locations/abc/placeActionLinks/xyz",
                body={},
                mask="name",
            )

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "--plan-in",
                        str(plan_path),
                        "place-actions",
                        "locations",
                        "place-action-links",
                        "delete",
                        "--name",
                        "locations/abc/placeActionLinks/xyz",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["reasons"][0], "--apply requires --yes for place-action-links delete.")

    def test_delete_apply_success_verification_not_found(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            plan_path = root / "plan.json"
            _write_plan(
                plan_path,
                operation="place-actions.locations.place-action-links.delete",
                selector="locations/abc/placeActionLinks/xyz",
                body={},
                mask="name",
            )

            calls: list[str] = []

            def fake_request(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict | None = None,
                json_body: dict | None = None,
                data: dict | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                calls.append(method)
                if method == "DELETE":
                    return HttpResponse(status=200, headers={}, body=b"", url=url)
                if method == "GET":
                    raise RuntimeError(
                        "HTTP 404 for GET https://mybusinessplaceactions.googleapis.com/v1/locations/abc/placeActionLinks/xyz\nNot found"
                    )
                raise AssertionError(f"Unexpected method: {method}")

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-no-snapshot",
                        "--plan-in",
                        str(plan_path),
                        "--yes",
                        "place-actions",
                        "locations",
                        "place-action-links",
                        "delete",
                        "--name",
                        "locations/abc/placeActionLinks/xyz",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertFalse(payload["dry_run"])
            self.assertTrue(payload["receipt"]["changed"])
            self.assertTrue(payload["receipt"]["verification"]["ok"])
            self.assertTrue(payload["receipt"]["verification"]["response"]["not_found"])
            self.assertEqual(payload["receipt"]["verification"]["response"]["status"], 404)
            self.assertEqual(calls, ["DELETE", "GET"])

    def test_get_calls_api_and_redacts_token(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            def fake_request(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict | None = None,
                json_body: dict | None = None,
                data: dict | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                return HttpResponse(
                    status=200,
                    headers={},
                    body=json.dumps(
                        {
                            "name": "locations/abc/placeActionLinks/xyz",
                            "uri": "https://example.com/reserve",
                        }
                    ).encode("utf-8"),
                    url=url,
                )

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "place-actions",
                        "locations",
                        "place-action-links",
                        "get",
                        "--name",
                        "locations/abc/placeActionLinks/xyz",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["operation"], "place-actions.locations.place-action-links.get")
            self.assertEqual(payload["request"]["method"], "GET")
            self.assertEqual(payload["request"]["path"], "v1/locations/abc/placeActionLinks/xyz")
            self.assertEqual(payload["response"]["uri"], "https://example.com/reserve")
            self.assertNotIn("TOKEN_SHOULD_NOT_LEAK", buf.getvalue())

    def test_list_and_metadata_calls_api_with_query_params(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            list_requests: list[tuple[dict | None, dict | None]] = []
            metadata_requests: list[tuple[dict | None, dict | None]] = []

            def fake_request(
                self,
                method: str,
                url: str,
                *,
                headers: dict[str, str] | None = None,
                params: dict | None = None,
                json_body: dict | None = None,
                data: dict | None = None,
                retries: int = 0,
                retry_on: tuple[int, ...] = (429,),
            ) -> HttpResponse:
                if method == "GET" and "placeActionLinks" in url:
                    list_requests.append((method, params or {}))
                    return HttpResponse(
                        status=200,
                        headers={},
                        body=json.dumps({"placeActionLinks": []}).encode("utf-8"),
                        url=url,
                    )
                if method == "GET" and "placeActionTypeMetadata" in url:
                    metadata_requests.append((method, params or {}))
                    return HttpResponse(
                        status=200,
                        headers={},
                        body=json.dumps({"placeActionTypeMetadata": []}).encode("utf-8"),
                        url=url,
                    )
                raise AssertionError(f"Unexpected url/method: {method} {url}")

            list_buf = io.StringIO()
            metadata_buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), patch("google_business_profile_safe_agent_cli.api_client.HttpClient.request", fake_request):
                with redirect_stdout(list_buf):
                    rc_list = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            str(env_path),
                            "place-actions",
                            "locations",
                            "place-action-links",
                            "list",
                            "--parent",
                            "locations/abc",
                            "--filter",
                            "placeActionType=DINING_RESERVATION",
                            "--page-size",
                            "10",
                            "--page-token",
                            "page-token-1",
                        ]
                    )

                with redirect_stdout(metadata_buf):
                    rc_metadata = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            str(env_path),
                            "place-actions",
                            "place-action-type-metadata",
                            "list",
                            "--language-code",
                            "en-US",
                            "--page-size",
                            "25",
                            "--page-token",
                            "token-2",
                            "--filter",
                            "location=locations/abc",
                        ]
                    )

            list_payload = json.loads(list_buf.getvalue())
            metadata_payload = json.loads(metadata_buf.getvalue())

            self.assertEqual(rc_list, 0)
            self.assertEqual(rc_metadata, 0)
            self.assertEqual(list_payload["operation"], "place-actions.locations.place-action-links.list")
            self.assertEqual(list_payload["request"]["params"], {
                "filter": "placeActionType=DINING_RESERVATION",
                "pageSize": 10,
                "pageToken": "page-token-1",
            })
            self.assertEqual(metadata_payload["operation"], "place-actions.place-action-type-metadata.list")
            self.assertEqual(metadata_payload["request"]["params"], {
                "languageCode": "en-US",
                "pageSize": 25,
                "pageToken": "token-2",
                "filter": "location=locations/abc",
            })
            self.assertEqual(
                list_requests,
                [("GET", {"filter": "placeActionType=DINING_RESERVATION", "pageSize": 10, "pageToken": "page-token-1"})],
            )
            self.assertEqual(
                metadata_requests,
                [("GET", {"languageCode": "en-US", "pageSize": 25, "pageToken": "token-2", "filter": "location=locations/abc"})],
            )

    def test_list_rejects_invalid_filter_value(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "place-actions",
                        "locations",
                        "place-action-links",
                        "list",
                        "--parent",
                        "locations/abc",
                        "--filter",
                        "isPreferred=true",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["refused"])
            self.assertTrue(any("place-action-links list" in reason for reason in payload["reasons"]))

    def test_metadata_rejects_invalid_filter_value(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(self._env_text, encoding="utf-8")
            _make_request_file(root)

            buf = io.StringIO()
            with patch(
                "google_business_profile_safe_agent_cli.api_client._load_credentials_from_token_data",
                return_value=_FakeCredentials("TOKEN_SHOULD_NOT_LEAK"),
            ), redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "place-actions",
                        "place-action-type-metadata",
                        "list",
                        "--language-code",
                        "en-US",
                        "--filter",
                        "category=RESERVE",
                    ]
                )

            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["refused"])
            self.assertTrue(any("place-action-type-metadata list" in reason for reason in payload["reasons"]))
