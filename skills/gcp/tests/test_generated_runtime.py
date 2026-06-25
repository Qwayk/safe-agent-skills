from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from gcp_safe_agent_cli.cli import main
from gcp_safe_agent_cli.config import load_config
from gcp_safe_agent_cli.google_auth import AdcState, load_adc_credentials


class _StubCredentials:
    def __init__(self, token: str | None, valid: bool) -> None:
        self.token = token
        self.valid = valid
        self.expired = not valid
        self.refresh_calls = 0

    def refresh(self, request: object) -> None:
        _ = request
        self.refresh_calls += 1
        self.token = "refreshed-token"
        self.valid = True
        self.expired = False


class _FakeResponse:
    def __init__(self, *, status_code: int, payload: object, url: str) -> None:
        self.status_code = status_code
        self._payload = payload
        self.url = url
        self.headers = {}
        self.content = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.text = json.dumps(payload, ensure_ascii=False)


class TestGeneratedRuntime(unittest.TestCase):
    def test_load_config_supports_gcp_adc_env_vars(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "GCP_QUOTA_PROJECT=quota-proj",
                        "GCP_ALLOWED_PROJECTS=proj-a, proj-b",
                        "GCP_ALLOWED_FOLDERS=folder-a",
                        "GCP_ALLOWED_ORGANIZATIONS=org-a, org-b",
                        "GCP_ALLOWED_BILLING_ACCOUNTS=BA-1, BA-2",
                        "GCP_ALLOWED_REGIONS=us-central1, europe-west1",
                        "GCP_TIMEOUT_S=12",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            cfg = load_config(str(env_path))

        self.assertEqual(cfg.quota_project, "quota-proj")
        self.assertEqual(cfg.allowed_projects, ("proj-a", "proj-b"))
        self.assertEqual(cfg.allowed_folders, ("folder-a",))
        self.assertEqual(cfg.allowed_organizations, ("org-a", "org-b"))
        self.assertEqual(cfg.allowed_billing_accounts, ("BA-1", "BA-2"))
        self.assertEqual(cfg.allowed_regions, ("us-central1", "europe-west1"))
        self.assertEqual(cfg.timeout_s, 12.0)

    def test_adc_refreshes_only_when_needed(self) -> None:
        ready = _StubCredentials(token="ready-token", valid=True)
        with patch("gcp_safe_agent_cli.google_auth.google.auth.default", return_value=(ready, "proj-a")) as default, patch(
            "gcp_safe_agent_cli.google_auth.Request"
        ) as request_cls:
            state = load_adc_credentials(quota_project_id="quota-a")
        default.assert_called_once_with(
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
            quota_project_id="quota-a",
        )
        request_cls.assert_not_called()
        self.assertEqual(state.project_id, "proj-a")
        self.assertFalse(state.refreshed)
        self.assertEqual(ready.refresh_calls, 0)

        stale = _StubCredentials(token=None, valid=False)
        with patch("gcp_safe_agent_cli.google_auth.google.auth.default", return_value=(stale, "proj-b")) as default2, patch(
            "gcp_safe_agent_cli.google_auth.Request"
        ) as request_cls2:
            state2 = load_adc_credentials(quota_project_id=None)
        default2.assert_called_once_with(
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
            quota_project_id=None,
        )
        request_cls2.assert_called_once()
        self.assertEqual(state2.project_id, "proj-b")
        self.assertTrue(state2.refreshed)
        self.assertEqual(stale.refresh_calls, 1)
        self.assertEqual(stale.token, "refreshed-token")

    def test_compute_instances_list_accepts_generated_command(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GCP_TIMEOUT_S=30\n", encoding="utf-8")

            input_path = root / "input.json"
            input_path.write_text(
                json.dumps(
                    {
                        "path": {"project": "proj-a", "zone": "us-central1-a"},
                        "query": {"maxResults": 1},
                    }
                ),
                encoding="utf-8",
            )

            fake_doc = {"baseUrl": "https://compute.googleapis.com/compute/v1/"}
            creds = _StubCredentials(token="adc-token", valid=True)
            api_response = _FakeResponse(
                status_code=200,
                payload={"items": [{"name": "i-1"}]},
                url="https://compute.googleapis.com/compute/v1/projects/proj-a/zones/us-central1-a/instances?maxResults=1",
            )

            with patch("gcp_safe_agent_cli.generated_runtime.load_discovery_document", return_value=fake_doc), patch(
                "gcp_safe_agent_cli.generated_runtime.load_adc_credentials",
                return_value=AdcState(credentials=creds, project_id="proj-a", quota_project_id=None, refreshed=False),
            ), patch("gcp_safe_agent_cli.http.requests.Session.request", return_value=api_response) as request:
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--env-file",
                            str(env_path),
                            "--output",
                            "json",
                            "compute",
                            "instances-list",
                            "--input-json",
                            str(input_path),
                        ]
                    )

        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["service_id"], "compute")
        self.assertEqual(payload["operation_name"], "instances-list")
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertIn("/projects/***REDACTED***/zones/***REDACTED***/instances", payload["request"]["url"])
        self.assertEqual(payload["request"]["params"], {"maxResults": 1})
        self.assertEqual(payload["response"]["items"][0]["name"], "i-1")
        request.assert_called_once()

    def test_read_response_redacts_config_values_even_inside_json_values(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GCP_QUOTA_PROJECT=secret-quota-project\nGCP_TIMEOUT_S=30\n", encoding="utf-8")

            input_path = root / "input.json"
            input_path.write_text(
                json.dumps(
                    {
                        "path": {"project": "proj-a", "zone": "us-central1-a"},
                        "query": {"filter": "secret-query-value"},
                    }
                ),
                encoding="utf-8",
            )

            fake_doc = {"baseUrl": "https://compute.googleapis.com/compute/v1/"}
            creds = _StubCredentials(token="adc-token", valid=True)
            api_response = _FakeResponse(
                status_code=200,
                payload={"items": [{"name": "i-1", "displayName": "secret-quota-project"}]},
                url="https://compute.googleapis.com/compute/v1/projects/proj-a/zones/us-central1-a/instances?filter=secret-query-value",
            )

            with patch("gcp_safe_agent_cli.generated_runtime.load_discovery_document", return_value=fake_doc), patch(
                "gcp_safe_agent_cli.generated_runtime.load_adc_credentials",
                return_value=AdcState(
                    credentials=creds,
                    project_id="proj-a",
                    quota_project_id="secret-quota-project",
                    refreshed=False,
                ),
            ), patch("gcp_safe_agent_cli.http.requests.Session.request", return_value=api_response):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--env-file",
                            str(env_path),
                            "--output",
                            "json",
                            "compute",
                            "instances-list",
                            "--input-json",
                            str(input_path),
                        ]
                    )

        self.assertEqual(rc, 0)
        stdout = buf.getvalue()
        payload = json.loads(stdout)
        self.assertEqual(payload["response"]["items"][0]["displayName"], "***REDACTED***")
        self.assertNotIn("secret-query-value", payload["response_url"])
        self.assertNotIn("secret-quota-project", stdout)

    def test_read_response_redacts_quota_project_override(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GCP_TIMEOUT_S=30\n", encoding="utf-8")

            input_path = root / "input.json"
            input_path.write_text(
                json.dumps(
                    {
                        "path": {"project": "proj-a", "zone": "us-central1-a"},
                        "query": {"maxResults": 1},
                    }
                ),
                encoding="utf-8",
            )

            fake_doc = {"baseUrl": "https://compute.googleapis.com/compute/v1/"}
            creds = _StubCredentials(token="adc-token", valid=True)
            api_response = _FakeResponse(
                status_code=200,
                payload={"items": [{"name": "i-1", "displayName": "secret-quota-project"}]},
                url="https://compute.googleapis.com/compute/v1/projects/proj-a/zones/us-central1-a/instances?maxResults=1",
            )

            with patch("gcp_safe_agent_cli.generated_runtime.load_discovery_document", return_value=fake_doc), patch(
                "gcp_safe_agent_cli.generated_runtime.load_adc_credentials",
                return_value=AdcState(
                    credentials=creds,
                    project_id="proj-a",
                    quota_project_id="secret-quota-project",
                    refreshed=False,
                ),
            ), patch("gcp_safe_agent_cli.http.requests.Session.request", return_value=api_response):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--env-file",
                            str(env_path),
                            "--output",
                            "json",
                            "compute",
                            "instances-list",
                            "--input-json",
                            str(input_path),
                            "--quota-project",
                            "secret-quota-project",
                        ]
                    )

        self.assertEqual(rc, 0)
        stdout = buf.getvalue()
        payload = json.loads(stdout)
        self.assertEqual(payload["response"]["items"][0]["displayName"], "***REDACTED***")
        self.assertNotIn("secret-quota-project", stdout)

    def test_missing_path_param_is_validation_error_and_does_not_call_http(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GCP_TIMEOUT_S=30\n", encoding="utf-8")
            input_path = root / "input.json"
            input_path.write_text(json.dumps({"path": {"project": "proj-a"}}), encoding="utf-8")

            with patch("gcp_safe_agent_cli.generated_runtime.load_discovery_document") as load_doc, patch(
                "gcp_safe_agent_cli.http.requests.Session.request"
            ) as request:
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--env-file",
                            str(env_path),
                            "--output",
                            "json",
                            "compute",
                            "instances-list",
                            "--input-json",
                            str(input_path),
                        ]
                    )

        self.assertEqual(rc, 1)
        payload = json.loads(buf.getvalue())
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("zone", payload["error"])
        load_doc.assert_not_called()
        request.assert_not_called()

    def test_region_allowlist_refuses_forbidden_read_zone_before_http(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GCP_ALLOWED_REGIONS=us-central1\nGCP_TIMEOUT_S=30\n", encoding="utf-8")
            input_path = root / "input.json"
            input_path.write_text(
                json.dumps({"path": {"project": "proj-a", "zone": "europe-west1-b"}}),
                encoding="utf-8",
            )

            with patch("gcp_safe_agent_cli.generated_runtime.load_discovery_document") as load_doc, patch(
                "gcp_safe_agent_cli.http.requests.Session.request"
            ) as request:
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--env-file",
                            str(env_path),
                            "--output",
                            "json",
                            "compute",
                            "instances-list",
                            "--input-json",
                            str(input_path),
                        ]
                    )

        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["refused"])
        self.assertIn("europe-west1", payload["reasons"][0])
        self.assertIn("GCP_ALLOWED_REGIONS", payload["reasons"][0])
        load_doc.assert_not_called()
        request.assert_not_called()

    def test_region_allowlist_refuses_forbidden_dry_run_write_zone(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GCP_ALLOWED_REGIONS=us-central1\nGCP_TIMEOUT_S=30\n", encoding="utf-8")
            input_path = root / "input.json"
            input_path.write_text(
                json.dumps(
                    {
                        "path": {
                            "project": "proj-a",
                            "zone": "europe-west1-b",
                            "instance": "instance-a",
                        }
                    }
                ),
                encoding="utf-8",
            )
            plan_out = root / "plan.json"

            with patch("gcp_safe_agent_cli.generated_runtime.load_discovery_document") as load_doc, patch(
                "gcp_safe_agent_cli.http.requests.Session.request"
            ) as request:
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--env-file",
                            str(env_path),
                            "--output",
                            "json",
                            "compute",
                            "instances-delete",
                            "--input-json",
                            str(input_path),
                            "--plan-out",
                            str(plan_out),
                        ]
                    )

        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["refused"])
        self.assertFalse(plan_out.exists())
        load_doc.assert_not_called()
        request.assert_not_called()

    def test_region_allowlist_refuses_forbidden_apply_location_name_before_http(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            plan_env_path = root / "plan.env"
            plan_env_path.write_text("GCP_ALLOWED_REGIONS=europe-west1\nGCP_TIMEOUT_S=30\n", encoding="utf-8")
            apply_env_path = root / "apply.env"
            apply_env_path.write_text("GCP_ALLOWED_REGIONS=us-central1\nGCP_TIMEOUT_S=30\n", encoding="utf-8")
            input_path = root / "input.json"
            input_payload = json.dumps(
                {
                    "path": {
                        "project": "proj-a",
                        "zone": "europe-west1-b",
                        "instance": "instance-a",
                    }
                }
            )
            input_path.write_text(input_payload, encoding="utf-8")
            plan_out = root / "plan.json"

            buf_plan = io.StringIO()
            with redirect_stdout(buf_plan):
                rc_plan = main(
                    [
                        "--env-file",
                        str(plan_env_path),
                        "--output",
                        "json",
                        "compute",
                        "instances-delete",
                        "--input-json",
                        str(input_path),
                        "--plan-out",
                        str(plan_out),
                    ]
                )
            self.assertEqual(rc_plan, 0)
            self.assertTrue(plan_out.exists())

            with patch("gcp_safe_agent_cli.generated_runtime.load_discovery_document") as load_doc, patch(
                "gcp_safe_agent_cli.http.requests.Session.request"
            ) as request:
                buf_apply = io.StringIO()
                with redirect_stdout(buf_apply):
                    rc_apply = main(
                        [
                            "--env-file",
                            str(apply_env_path),
                            "--output",
                            "json",
                            "compute",
                            "instances-delete",
                            "--input-json",
                            str(input_path),
                            "--plan-in",
                            str(plan_out),
                            "--apply",
                            "--yes",
                            "--ack-no-snapshot",
                            "--ack-irreversible",
                        ]
                    )

        self.assertEqual(rc_apply, 0)
        payload = json.loads(buf_apply.getvalue())
        self.assertTrue(payload["refused"])
        self.assertIn("europe-west1", payload["reasons"][0])
        load_doc.assert_not_called()
        request.assert_not_called()

    def test_region_allowlist_parses_common_location_resource_names(self) -> None:
        from gcp_safe_agent_cli.generated_runtime import _region_candidates

        candidates = dict(
            _region_candidates(
                {
                    "name": "projects/proj-a/locations/europe-west1/services/svc-a",
                    "locationsId": "us-central1",
                    "zone": "asia-south1-c",
                }
            )
        )
        self.assertEqual(candidates["name:location"], "europe-west1")
        self.assertEqual(candidates["locationsId"], "us-central1")
        self.assertEqual(candidates["zone"], "asia-south1")

    def test_write_dry_run_creates_plan_and_does_not_call_http(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GCP_TIMEOUT_S=30\n", encoding="utf-8")
            input_path = root / "input.json"
            input_path.write_text(
                json.dumps(
                    {
                        "path": {
                            "project": "proj-a",
                            "zone": "us-central1-a",
                            "instance": "instance-a",
                        }
                    }
                ),
                encoding="utf-8",
            )
            plan_out = root / "plan.json"

            with patch("gcp_safe_agent_cli.generated_runtime.load_discovery_document") as load_doc, patch(
                "gcp_safe_agent_cli.http.requests.Session.request"
            ) as request:
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--env-file",
                            str(env_path),
                            "--output",
                            "json",
                            "compute",
                            "instances-delete",
                            "--input-json",
                            str(input_path),
                            "--plan-out",
                            str(plan_out),
                        ]
                    )
                self.assertEqual(rc, 0)
                payload = json.loads(buf.getvalue())
                self.assertTrue(payload["ok"])
                self.assertTrue(payload["dry_run"])
                self.assertTrue(plan_out.exists())
                self.assertIn("plan", payload)
                self.assertEqual(payload["plan_out"], "plan.json")
                self.assertEqual(payload["plan"]["operation_name"], "instances-delete")
                plan_file = json.loads(plan_out.read_text(encoding="utf-8"))
                self.assertEqual(plan_file["request_preview"]["path_values"]["project"], "***REDACTED***")
                self.assertEqual(plan_file["request_preview"]["path_values"]["zone"], "***REDACTED***")
                self.assertEqual(plan_file["request_preview"]["path_values"]["instance"], "***REDACTED***")
                self.assertEqual(plan_file["input"]["path"]["instance"], "***REDACTED***")
                self.assertEqual(plan_file["input_fingerprint"], payload["plan"]["input_fingerprint"])
                self.assertEqual(plan_file["plan_fingerprint"], payload["plan"]["plan_fingerprint"])
                load_doc.assert_not_called()
                request.assert_not_called()

    def test_inventory_summary_command_works(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["--output", "json", "inventory", "summary"])
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertIn("summary", payload)
        self.assertIn("services", payload)

    def test_apply_gates_refuse_without_required_flags(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GCP_TIMEOUT_S=30\n", encoding="utf-8")
            input_payload = json.dumps(
                {
                    "path": {
                        "project": "proj-a",
                        "zone": "us-central1-a",
                        "instance": "instance-a",
                    }
                }
            )
            input_path = root / "input.json"
            input_path.write_text(input_payload, encoding="utf-8")
            plan_out = root / "plan.json"

            with patch("gcp_safe_agent_cli.generated_runtime.load_discovery_document", return_value={"baseUrl": "https://compute.googleapis.com/compute/v1/"}), patch(
                "gcp_safe_agent_cli.generated_runtime.load_adc_credentials",
                return_value=AdcState(credentials=_StubCredentials(token="adc-token", valid=True), project_id="proj-a", quota_project_id=None, refreshed=False),
            ), patch("gcp_safe_agent_cli.http.requests.Session.request", return_value=_FakeResponse(status_code=200, payload={"ok": True}, url="https://example.invalid")):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--env-file",
                            str(env_path),
                            "--output",
                            "json",
                            "compute",
                            "instances-delete",
                            "--input-json",
                            str(input_path),
                            "--plan-out",
                            str(plan_out),
                        ]
                    )
                self.assertEqual(rc, 0)
                self.assertTrue(plan_out.exists())

                input_path2 = root / "input-apply.json"
                input_path2.write_text(input_payload, encoding="utf-8")

                def _run_apply(*, include_plan_in: bool = True, extra_args: list[str]) -> dict[str, object]:
                    stdout = io.StringIO()
                    argv = ["--env-file", str(env_path), "--output", "json", "compute", "instances-delete"]
                    if include_plan_in:
                        argv.extend(["--plan-in", str(plan_out)])
                    argv.extend(["--input-json", str(input_path2), "--apply", *extra_args])
                    with redirect_stdout(stdout):
                        rc2 = main(argv)
                    self.assertEqual(rc2, 0)
                    return json.loads(stdout.getvalue())

                missing_plan = _run_apply(include_plan_in=False, extra_args=["--yes", "--ack-no-snapshot", "--ack-irreversible"])
                self.assertTrue(missing_plan["refused"])
                self.assertIn("--plan-in", missing_plan["reasons"][0])

                missing_yes = _run_apply(extra_args=["--ack-no-snapshot", "--ack-irreversible"])
                self.assertTrue(missing_yes["refused"])
                self.assertIn("--yes", missing_yes["reasons"][0])

                missing_no_snapshot = _run_apply(extra_args=["--yes", "--ack-irreversible"])
                self.assertTrue(missing_no_snapshot["refused"])
                self.assertIn("--ack-no-snapshot", missing_no_snapshot["reasons"][0])

                missing_irreversible = _run_apply(extra_args=["--yes", "--ack-no-snapshot"])
                self.assertTrue(missing_irreversible["refused"])
                self.assertIn("--ack-irreversible", missing_irreversible["reasons"][0])

    def test_receipt_redacts_response_and_includes_fingerprint(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GCP_TIMEOUT_S=30\n", encoding="utf-8")
            input_path = root / "input.json"
            input_path.write_text(
                json.dumps(
                    {
                        "path": {
                            "project": "proj-a",
                            "zone": "us-central1-a",
                            "instance": "instance-a",
                        }
                    }
                ),
                encoding="utf-8",
            )
            plan_out = root / "plan.json"
            receipt_out = root / "receipt.json"

            with patch("gcp_safe_agent_cli.generated_runtime.load_discovery_document", return_value={"baseUrl": "https://compute.googleapis.com/compute/v1/"}), patch(
                "gcp_safe_agent_cli.generated_runtime.load_adc_credentials",
                return_value=AdcState(credentials=_StubCredentials(token="adc-token", valid=True), project_id="proj-a", quota_project_id=None, refreshed=False),
            ), patch("gcp_safe_agent_cli.http.requests.Session.request", return_value=_FakeResponse(status_code=200, payload={"ok": True}, url="https://example.invalid")):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--env-file",
                            str(env_path),
                            "--output",
                            "json",
                            "compute",
                            "instances-delete",
                            "--input-json",
                            str(input_path),
                            "--plan-out",
                            str(plan_out),
                        ]
                    )
            self.assertEqual(rc, 0)
            self.assertTrue(plan_out.exists())

            with patch("gcp_safe_agent_cli.generated_runtime.load_discovery_document", return_value={"baseUrl": "https://compute.googleapis.com/compute/v1/"}), patch(
                "gcp_safe_agent_cli.generated_runtime.load_adc_credentials",
                return_value=AdcState(credentials=_StubCredentials(token="adc-token", valid=True), project_id="proj-a", quota_project_id=None, refreshed=False),
            ), patch("gcp_safe_agent_cli.http.requests.Session.request", return_value=_FakeResponse(status_code=200, payload={"access_token": "SHOULD-NOT-PRINT", "nested": {"refresh_token": "HUSH", "safe": "ok"}}, url="https://example.invalid")):
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    rc2 = main(
                        [
                            "--env-file",
                            str(env_path),
                            "--output",
                            "json",
                            "compute",
                            "instances-delete",
                            "--input-json",
                            str(input_path),
                            "--plan-in",
                            str(plan_out),
                            "--apply",
                            "--yes",
                            "--ack-no-snapshot",
                            "--ack-irreversible",
                            "--receipt-out",
                            str(receipt_out),
                        ]
                    )
                self.assertEqual(rc2, 0)
                payload = json.loads(stdout.getvalue())
                self.assertTrue(payload["ok"])
                self.assertIn("receipt", payload)
                self.assertEqual(payload["receipt_out"], "receipt.json")
                self.assertIn("plan_fingerprint", payload["receipt"])
                self.assertIn("plan_check", payload["receipt"])
                self.assertFalse(payload["receipt"]["read_back_verified"])
                self.assertEqual(payload["receipt"]["verification_status"], "limited_verification")
                self.assertIn("limited verification: successful provider response only", payload["receipt"]["verification_note"])
                self.assertEqual(payload["receipt"]["response"]["access_token"], "***REDACTED***")
                self.assertEqual(payload["receipt"]["response"]["nested"]["refresh_token"], "***REDACTED***")
                self.assertEqual(payload["receipt"]["response"]["nested"]["safe"], "ok")
                self.assertNotIn("SHOULD-NOT-PRINT", stdout.getvalue())
                self.assertTrue(receipt_out.exists())
                receipt_file = json.loads(receipt_out.read_text(encoding="utf-8"))
                self.assertEqual(receipt_file["response"]["access_token"], "***REDACTED***")

    def test_auth_check_redacts_secret_env_values_from_errors(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "GCP_QUOTA_PROJECT=secret-quota-project",
                        "GCP_ALLOWED_PROJECTS=secret-project",
                        "GCP_TIMEOUT_S=30",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            with patch(
                "gcp_safe_agent_cli.commands.auth.load_adc_credentials",
                side_effect=RuntimeError("boom secret-quota-project secret-project"),
            ):
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    rc = main(["--env-file", str(env_path), "--output", "json", "auth", "check"])

        self.assertEqual(rc, 1)
        payload = json.loads(stdout.getvalue())
        self.assertFalse(payload["ok"])
        self.assertNotIn("secret-quota-project", payload["error"])
        self.assertNotIn("secret-project", payload["error"])
