import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout

from ghost_api_tool.cli import main as cli_main


class V2VersionTests(unittest.TestCase):
    def test_version_is_single_json_object_in_json_mode(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cli_main(["--output", "json", "--version"])
        self.assertEqual(rc, 0)
        obj = json.loads(buf.getvalue())
        self.assertTrue(obj["ok"])
        self.assertEqual(obj["tool"], "ghost-api-tool")
        self.assertIn("version", obj)


class V2RunsArtifactsTests(unittest.TestCase):
    def _write_env(self, root: str) -> str:
        env_path = os.path.join(root, ".env")
        with open(env_path, "w", encoding="utf-8") as f:
            f.write("GHOST_ADMIN_API_URL=https://example.com/ghost/api/admin/\n")
            f.write("GHOST_ADMIN_API_KEY=abc:" + "00" * 32 + "\n")
            f.write("GHOST_ACCEPT_VERSION=v5.0\n")
            f.write("GHOST_TIMEOUT_S=5\n")
        return env_path

    def _write_empty_jobs_csv(self, root: str) -> str:
        csv_path = os.path.join(root, "jobs.csv")
        with open(csv_path, "w", encoding="utf-8") as f:
            f.write("action,slug\n")
        return csv_path

    def test_dry_run_jobs_creates_run_artifacts_and_index(self):
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            jobs_csv = self._write_empty_jobs_csv(td)

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cli_main(["--env-file", env_path, "--output", "json", "jobs", "run", "--file", jobs_csv])
            self.assertEqual(rc, 0)
            out = json.loads(buf.getvalue())
            self.assertTrue(out["ok"])
            self.assertIsNotNone(out.get("run_id"))
            self.assertIsNotNone(out.get("artifacts_dir"))

            artifacts_dir = out["artifacts_dir"]
            self.assertTrue(os.path.isdir(artifacts_dir))
            self.assertTrue(os.path.exists(os.path.join(artifacts_dir, "plan.json")))
            self.assertTrue(os.path.exists(os.path.join(artifacts_dir, "summary.md")))

            runs_index = os.path.join(td, ".state", "runs", "index.jsonl")
            self.assertTrue(os.path.exists(runs_index))

            audit_log = os.path.join(artifacts_dir, "audit.jsonl")
            self.assertTrue(os.path.exists(audit_log))

            # runs list should show at least one run.
            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = cli_main(["--env-file", env_path, "--output", "json", "runs", "list", "--limit", "5"])
            self.assertEqual(rc2, 0)
            out2 = json.loads(buf2.getvalue())
            self.assertGreaterEqual(out2["count"], 1)

    def test_apply_with_plan_in_enforces_drift_detection(self):
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            jobs_csv = self._write_empty_jobs_csv(td)

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cli_main(["--env-file", env_path, "--output", "json", "jobs", "run", "--file", jobs_csv])
            self.assertEqual(rc, 0)
            out = json.loads(buf.getvalue())
            plan_path = os.path.join(out["artifacts_dir"], "plan.json")
            self.assertTrue(os.path.exists(plan_path))

            # Mixed row writes need a plan-first gate and either before-state support,
            # explicit no-snapshot approval, or a real blocker reason per row.
            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = cli_main(
                    [
                        "--env-file",
                        env_path,
                        "--output",
                        "json",
                        "--apply",
                        "--yes",
                        "--plan-in",
                        plan_path,
                        "jobs",
                        "run",
                        "--file",
                        jobs_csv,
                    ]
                )
            self.assertEqual(rc2, 0)
            out2 = json.loads(buf2.getvalue())
            self.assertTrue(out2["ok"])
            self.assertTrue(bool(out2.get("refused")))
            self.assertIn("jobs.run", out2["reasons"][0])

            # Drift path: tamper baseline sha to force refusal.
            with open(plan_path, encoding="utf-8") as f:
                tampered = json.loads(f.read())
            tampered.setdefault("baseline", {})
            tampered["baseline"]["raw_plan_sha256"] = "0" * 64
            tampered_path = os.path.join(td, "tampered.plan.json")
            with open(tampered_path, "w", encoding="utf-8") as f:
                json.dump(tampered, f)

            buf3 = io.StringIO()
            with redirect_stdout(buf3):
                rc3 = cli_main(
                    [
                        "--env-file",
                        env_path,
                        "--output",
                        "json",
                        "--apply",
                        "--yes",
                        "--plan-in",
                        tampered_path,
                        "jobs",
                        "run",
                        "--file",
                        jobs_csv,
                    ]
                )
            self.assertEqual(rc3, 0)
            out3 = json.loads(buf3.getvalue())
            self.assertTrue(out3["ok"])
            self.assertTrue(out3.get("refused"))

    def test_high_risk_apply_requires_plan_in(self):
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            jobs_csv = self._write_empty_jobs_csv(td)

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cli_main(
                    [
                        "--env-file",
                        env_path,
                        "--output",
                        "json",
                        "--apply",
                        "--yes",
                        "jobs",
                        "run",
                        "--file",
                        jobs_csv,
                    ]
                )
            self.assertEqual(rc, 0)
            out = json.loads(buf.getvalue())
            self.assertTrue(out["ok"])
            self.assertTrue(out.get("refused"))

    def test_audit_has_run_start_and_end(self):
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            jobs_csv = self._write_empty_jobs_csv(td)

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cli_main(["--env-file", env_path, "--output", "json", "jobs", "run", "--file", jobs_csv])
            self.assertEqual(rc, 0)
            out = json.loads(buf.getvalue())
            audit_log = os.path.join(out["artifacts_dir"], "audit.jsonl")
            self.assertTrue(os.path.exists(audit_log))
            events = []
            with open(audit_log, encoding="utf-8") as f:
                for line in f:
                    obj = json.loads(line)
                    events.append(obj.get("event"))
            self.assertIn("run.start", events)
            self.assertIn("run.end", events)
