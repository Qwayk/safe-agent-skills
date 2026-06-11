import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
from unittest.mock import patch

from wordpress_api_tool.cli import main as cli_main


class JobsRunCommandTests(unittest.TestCase):
    def _run(self, argv):
        out = io.StringIO()
        err = io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            rc = int(cli_main(list(argv)))
        stdout = out.getvalue()
        stderr = err.getvalue()
        payload = json.loads(stdout)
        return rc, stdout, stderr, payload

    def _env_file(self, td_path: Path) -> Path:
        env_path = td_path / ".env"
        env_path.write_text(
            "\n".join(
                [
                    "WP_BASE_URL=https://example.com",
                    "WP_USERNAME=fake_user",
                    "WP_APP_PASSWORD=fake_password",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        return env_path

    def test_jobs_run_dry_run_still_works_and_saves_before_state(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            env_path = self._env_file(td_path)
            plan_out = td_path / "plan.json"
            jobs_path = td_path / "jobs.json"
            jobs_path.write_text(
                json.dumps(
                    {
                        "jobs": [
                            {"action": "media.set", "id": 123, "caption": "Photo"},
                            {
                                "action": "post.set_image_captions",
                                "slug": "hello-world",
                                "caption": "Cap",
                            },
                        ]
                    }
                ),
                encoding="utf-8",
            )

            def _media_set(*_args, **_kwargs):
                return {"changed": True, "verified": True, "changes": {"caption": {"before": "Old", "after": "Photo"}}}

            def _post_set(*_args, **_kwargs):
                return {"changed": True, "verified": True, "report": {"updated_blocks": 1}}

            with (
                patch("wordpress_api_tool.commands.jobs.media_set_core", side_effect=_media_set),
                patch("wordpress_api_tool.commands.jobs.post_set_image_captions_core", side_effect=_post_set),
            ):
                rc, _stdout, stderr, payload = self._run(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "--plan-out",
                        str(plan_out),
                        "jobs",
                        "run",
                        "--file",
                        str(jobs_path),
                    ]
                )

            self.assertEqual(rc, 0)
            self.assertEqual(stderr, "")
            self.assertIn("plan", payload)

            plan = payload.get("plan") or {}
            before_state = plan.get("before_state") or {}
            self.assertEqual(plan.get("rollback", {}).get("supported"), False)
            self.assertEqual(before_state.get("status"), "no_snapshot_available")
            job_file_snapshot = before_state.get("job_file_snapshot") or {}
            path = job_file_snapshot.get("path")
            self.assertIsInstance(path, str)
            self.assertTrue(path.endswith("/jobs.run.input__file-jobs.json"))
            self.assertTrue(Path(path).exists())
            self.assertEqual(len((plan.get("proposed_changes") or [])), 2)

            self.assertTrue(plan_out.exists())
            self.assertIn("jobs.run.input__file-jobs.json", plan_out.read_text(encoding="utf-8"))

    def test_jobs_run_apply_requires_no_snapshot_ack(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            env_path = self._env_file(td_path)
            jobs_path = td_path / "jobs.csv"
            jobs_path.write_text("action,id,caption\nmedia.set,123,Photo\n", encoding="utf-8")

            rc, _stdout, stderr, payload = self._run(
                [
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "--apply",
                    "--yes",
                    "jobs",
                    "run",
                    "--file",
                    str(jobs_path),
                ]
            )

            self.assertEqual(rc, 1)
            self.assertEqual(stderr, "")
            self.assertIn("ack-no-snapshot", (payload.get("error") or ""))
