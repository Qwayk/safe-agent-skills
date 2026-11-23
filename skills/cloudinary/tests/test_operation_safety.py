from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from ._helpers import FakeResponse, assert_blocked_before_state, run_cli, write_env


class TestOperationSafety(unittest.TestCase):
    def test_signed_upload_uses_the_reviewed_file_and_requires_replacement_approval(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env = write_env(root, product_auth=True)
            args = ["--env-file", str(env), "--no-artifacts"]
            apply = ["--apply", "--yes", "--ack-no-snapshot"]
            plan = root / "upload-plan.json"
            media = root / "image.jpg"
            media.write_bytes(b"reviewed image")
            source = root / "upload.json"
            source.write_text(json.dumps({"files": [{"name": "file", "path": str(media)}]}))
            upload = ["operations", "upload", "upload-signed", "--multipart-spec-file", str(source)]
            before = run_cli([*args, "--plan-out", str(plan), *upload])[1]["plan"]
            self.assertEqual(before["request_plan"]["form_fields"]["overwrite"], "false")
            self.assertFalse(before["requires_ack_irreversible"])
            reviewed = [*args, *apply, "--plan-in", str(plan)]
            for attempt in ([*args, *apply, *upload], [*reviewed, *upload, "--form-field", "public_id=changed"]):
                self.assertTrue(run_cli(attempt)[1]["refused"])
            media.write_bytes(b"different image")
            self.assertTrue(run_cli([*reviewed, *upload])[1]["refused"])
            media.write_bytes(b"reviewed image")
            original_env = env.read_text()
            env.write_text(original_env.replace("CLOUDINARY_CLOUD_NAME=demo", "CLOUDINARY_CLOUD_NAME=another"))
            self.assertTrue(run_cli([*reviewed, *upload])[1]["refused"])
            env.write_text(original_env)
            legacy = json.loads(plan.read_text())
            legacy["baseline"].pop("request_sha256")
            plan.write_text(json.dumps(legacy))
            self.assertTrue(run_cli([*reviewed, *upload])[1]["refused"])
            run_cli([*args, "--plan-out", str(plan), *upload])
            calls = []

            def request(**request_args):
                calls.append(request_args)
                return FakeResponse(payload={})

            self.assertEqual(run_cli([*reviewed, *upload], request_side_effect=request)[0], 0)
            self.assertEqual(calls[0]["files"]["file"][1], b"reviewed image")
            self.assertEqual(calls[0]["data"]["overwrite"], "false")
            replacement = [*upload, "--form-field", "overwrite=true"]
            run_cli([*args, "--plan-out", str(plan), *replacement])
            self.assertIn("--ack-irreversible", run_cli([*reviewed, *replacement])[1]["reasons"][0])
            self.assertEqual(
                run_cli([*reviewed, "--ack-irreversible", *replacement], request_side_effect=request)[0], 0
            )

    def test_metadata_update_sends_the_reviewed_json_and_checks_the_result(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            args = ["--env-file", str(write_env(root, product_auth=True)), "--no-artifacts"]
            plan = root / "edit-plan.json"
            body = root / "edit.json"
            body.write_text('{"display_name":"Approved name"}')
            update = ["operations", "admin", "resources-update-details-of-an-existing-resource-by-asset-id",
                      "--path-param", "asset_id=asset-a", "--body-json-file", str(body)]
            run_cli([*args, "--plan-out", str(plan), *update])
            apply = [*args, "--plan-in", str(plan), "--apply", "--yes", "--ack-no-snapshot", *update]
            edited = '{"display_name":"Different name"}'
            body.write_text(edited)
            self.assertTrue(run_cli(apply)[1]["refused"])
            body.write_text('{"display_name":"Approved name"}')

            for visible in ("Old name", "Approved name"):
                with self.subTest(visible=visible):
                    def request(*, response_name=visible, **request_args):
                        if request_args["method"] == "PUT":
                            self.assertEqual(request_args["json"], {"display_name": "Approved name"})
                        return FakeResponse(payload={"display_name": response_name})

                    rc, result = run_cli(apply, request_side_effect=request)
                    self.assertEqual(rc, 0)
                    expected = True if visible == "Approved name" else None
                    self.assertIs(result["receipt"]["verification"]["ok"], expected)

    def test_delete_receipt_uses_the_missing_result_instead_of_any_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            args = ["--env-file", str(write_env(root, product_auth=True)), "--no-artifacts"]
            plan = root / "delete.json"
            delete = ["operations", "upload", "destroy-by-public-id", "--form-field", "public_id=media"]
            run_cli([*args, "--plan-out", str(plan), *delete])
            apply = [*args, "--plan-in", str(plan), "--apply", "--yes", "--ack-no-snapshot"]
            self.assertIn("--ack-irreversible", run_cli([*apply, *delete])[1]["reasons"][0])
            for status, expected in [(404, True), (403, None), (429, None), (500, None), (200, False)]:
                with self.subTest(status=status):
                    def request(*, response_status=status, **request_args):
                        if request_args["method"] == "POST":
                            return FakeResponse(payload={"result": "ok"})
                        return FakeResponse(status_code=response_status, payload={})

                    rc, result = run_cli([*apply, "--ack-irreversible", *delete], request_side_effect=request)
                    self.assertEqual(rc, 0)
                    self.assertIs(result["receipt"]["verification"]["ok"], expected)

            rc, result = run_cli([*apply, "--ack-irreversible", *delete],
                                 request_side_effect=lambda **_: FakeResponse(payload={"result": "not found"}))
            self.assertEqual(rc, 0)
            self.assertIs(result["receipt"]["changed"], False)

    def test_key_creation_keeps_the_returned_secret_only_in_the_private_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            args = ["--env-file", str(write_env(root, account_auth=True)),
                    "--project-dir", str(root), "--no-artifacts"]
            plan, body, receipt = (root / name for name in ("plan.json", "body.json", "receipt.json"))
            body.write_text('{"name":"new key"}')
            create = ["operations", "provisioning", "generateaccesskey",
                      "--path-param", "sub_account_id=example", "--body-json-file", str(body)]
            run_cli([*args, "--plan-out", str(plan), *create])
            value = "test-only-generated-secret"
            calls = []

            def request(**request_args):
                calls.append(request_args["method"])
                return FakeResponse(payload={"api_secret": value})

            apply = [*args, "--plan-in", str(plan), "--apply", "--yes", "--ack-no-snapshot",
                     "--ack-irreversible", "--receipt-out", str(receipt), *create, "--out", "private.json"]
            rc, result = run_cli(apply, request_side_effect=request)
            self.assertEqual(rc, 0)
            self.assertEqual(calls, ["POST"])
            self.assertNotIn(value, json.dumps(result))
            self.assertNotIn(value, receipt.read_text())
            self.assertIn(value, (root / "private.json").read_text())
            self.assertEqual((root / "private.json").stat().st_mode & 0o777, 0o600)
            self.assertTrue(run_cli(apply, request_side_effect=request)[1]["refused"])
            self.assertEqual(calls, ["POST"])

    def test_path_params_are_percent_encoded_before_request(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env_path = write_env(root, product_context=True, product_auth=True)
            seen: dict[str, str] = {}

            def _request(*args, **kwargs):
                seen["url"] = str(kwargs.get("url") or "")
                return FakeResponse(payload={"asset_id": "asset-1"}, url=seen["url"])

            rc, payload = run_cli(
                [
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "operations",
                    "admin",
                    "resources-get-details-of-a-single-resource-by-public-id",
                    "--path-param",
                    "resource_type=image",
                    "--path-param",
                    "type=upload",
                    "--path-param",
                    "public_id=folder/a b",
                ],
                request_side_effect=_request,
            )

            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertIn("/folder%2Fa%20b", seen["url"])
            self.assertNotIn("/folder/a b", seen["url"])

    def test_delete_like_operations_require_ack_irreversible(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env_path = write_env(root, product_context=True)
            rc, payload = run_cli(
                [
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "--apply",
                    "--yes",
                    "operations",
                    "admin",
                    "folders-delete-folder",
                    "--path-param",
                    "folder=archive/old",
                ]
            )

            self.assertEqual(rc, 0)
            self.assertTrue(payload["refused"])
            self.assertIn("--ack-irreversible", payload["reasons"][0])

    def test_plan_in_rejects_path_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env_path = write_env(root, product_context=True)
            plan_path = root / "delete-folder-plan.json"

            rc, payload = run_cli(
                [
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "--plan-out",
                    str(plan_path),
                    "operations",
                    "admin",
                    "folders-delete-folder",
                    "--path-param",
                    "folder=archive/old",
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["dry_run"])
            self.assertTrue(plan_path.exists())
            assert_blocked_before_state(self, payload["plan"])

            rc, payload = run_cli(
                [
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "--apply",
                    "--yes",
                    "--ack-irreversible",
                    "--plan-in",
                    str(plan_path),
                    "operations",
                    "admin",
                    "folders-delete-folder",
                    "--path-param",
                    "folder=archive/new",
                ]
            )

            self.assertEqual(rc, 0)
            self.assertTrue(payload["refused"])
            self.assertIn("plan method or path does not match", payload["reasons"][0])

    def test_sensitive_reads_require_out(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env_path = write_env(root, product_context=True)
            rc, payload = run_cli(
                [
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "operations",
                    "live_streaming",
                    "getlivestreams",
                ]
            )

            self.assertEqual(rc, 0)
            self.assertTrue(payload["refused"])
            self.assertIn("Re-run with --out", payload["reasons"][0])
