from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from hubspot_safe_agent_cli.cli import build_parser
from hubspot_safe_agent_cli.commands import hubspot


class TestHubspotCommandFamilies(unittest.TestCase):
    def setUp(self) -> None:
        self.parser = build_parser()
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.body = Path(self._tmp.name) / "body.json"
        self.body.write_text("{}", encoding="utf-8")
        self.upload = Path(self._tmp.name) / "upload.csv"
        self.upload.write_text("email\nperson@example.com\n", encoding="utf-8")

    def _assert(self, argv: list[str], family: str, action: str) -> None:
        args = self.parser.parse_args(argv)
        self.assertEqual(args.hubspot_family, family)
        self.assertEqual(args.hubspot_action, action)
        self.assertIs(args.func, hubspot.cmd_hubspot_api)

    def _argv_for_spec(self, family: str, action: str, spec: hubspot.ActionSpec) -> list[str]:
        sample_path_args = {
            "object_type": "contacts",
            "object_id": "123",
            "from_object_type": "contacts",
            "from_object_id": "1",
            "to_object_type": "companies",
            "to_object_id": "2",
            "association_type_id": "15",
            "property_name": "email",
            "group_name": "contactinformation",
            "owner_id": "1234",
            "pipeline_id": "default",
            "stage_id": "appointmentscheduled",
            "task_id": "task-1",
            "import_id": "import-1",
        }
        argv = ["hubspot", family, action]
        for name in hubspot._path_names(spec.path):
            argv.extend([f"--{name.replace('_', '-')}", sample_path_args[name]])
        if spec.requires_body_file:
            argv.extend(["--body-file", str(self.body)])
        if spec.requires_request_file:
            argv.extend(["--request-file", str(self.body)])
        if spec.requires_files:
            argv.extend(["--file", str(self.upload)])
        return argv

    def test_parser_has_main_families(self) -> None:
        cases = [
            ("object-library", "list-enablement", []),
            ("objects", "list", ["--object-type", "contacts"]),
            ("objects", "get", ["--object-type", "contacts", "--object-id", "123"]),
            ("objects", "search", ["--object-type", "contacts", "--body-file", str(self.body)]),
            (
                "associations",
                "create-default",
                [
                    "--from-object-type",
                    "contacts",
                    "--from-object-id",
                    "1",
                    "--to-object-type",
                    "companies",
                    "--to-object-id",
                    "2",
                ],
            ),
            (
                "association-labels",
                "list",
                ["--from-object-type", "contacts", "--to-object-type", "companies"],
            ),
            ("association-limits", "list-all", []),
            ("properties", "list", ["--object-type", "contacts"]),
            ("property-groups", "list", ["--object-type", "contacts"]),
            ("owners", "list", []),
            ("pipelines", "list", ["--object-type", "contacts"]),
            (
                "pipeline-stages",
                "list",
                ["--object-type", "contacts", "--pipeline-id", "pipeline-1"],
            ),
            ("schemas", "list", []),
            ("imports", "errors", ["--import-id", "import-1"]),
            ("exports", "status", ["--task-id", "task-1"]),
        ]
        for family, action, extra in cases:
            argv = ["hubspot", family, action] + extra
            self._assert(argv, family, action)

    def test_every_shipped_action_parses_with_required_args(self) -> None:
        for family, actions in hubspot.actions().items():
            for action, spec in actions.items():
                with self.subTest(family=family, action=action):
                    argv = self._argv_for_spec(family, action, spec)
                    args = self.parser.parse_args(argv)
                    self.assertEqual(args.hubspot_family, family)
                    self.assertEqual(args.hubspot_action, action)
                    self.assertIs(args.func, hubspot.cmd_hubspot_api)
                    self.assertEqual(args.write_capable, spec.write)
