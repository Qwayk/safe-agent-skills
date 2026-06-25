from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


class TestGcpDiscoveryInventory(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(__file__).resolve().parents[1]

    def test_build_inventory_filters_in_scope_services_and_writes_coverage(self) -> None:
        from gcp_safe_agent_cli import gcp_discovery_inventory as inventory_mod

        directory = {
            "items": [
                {
                    "id": "compute:v1",
                    "name": "compute",
                    "version": "v1",
                    "title": "Compute Engine API",
                    "preferred": True,
                    "documentationLink": "https://developers.google.com/compute/docs/reference/latest/",
                    "discoveryRestUrl": "https://compute.googleapis.com/discovery/v1/apis/compute/v1/rest",
                },
                {
                    "id": "youtube:v3",
                    "name": "youtube",
                    "version": "v3",
                    "title": "YouTube Data API v3",
                    "preferred": True,
                    "documentationLink": "https://developers.google.com/youtube/",
                    "discoveryRestUrl": "https://youtube.googleapis.com/discovery/v1/apis/youtube/v3/rest",
                },
            ]
        }
        compute_doc = {
            "name": "compute",
            "version": "v1",
            "title": "Compute Engine API",
            "resources": {
                "instances": {
                    "methods": {
                        "list": {
                            "id": "compute.instances.list",
                            "path": "projects/{project}/zones/{zone}/instances",
                            "httpMethod": "GET",
                            "description": "Lists instances.",
                        },
                        "delete": {
                            "id": "compute.instances.delete",
                            "path": "projects/{project}/zones/{zone}/instances/{instance}",
                            "httpMethod": "DELETE",
                            "description": "Deletes an instance.",
                        },
                    }
                }
            },
        }

        def fake_fetch_json(url: str) -> dict:
            if url.endswith("/discovery/v1/apis"):
                return directory
            if url.endswith("/compute/v1/rest"):
                return compute_doc
            raise AssertionError(f"Unexpected URL: {url}")

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            with patch.object(inventory_mod, "fetch_json", side_effect=fake_fetch_json):
                result = inventory_mod.generate_inventory(
                    directory_url="https://discovery.googleapis.com/discovery/v1/apis",
                    output_dir=tmp_path / "docs" / "_generated",
                    coverage_path=tmp_path / "docs" / "api_coverage.md",
                )

            self.assertEqual(result["summary"]["included_service_count"], 1)
            self.assertEqual(result["summary"]["excluded_service_count"], 1)
            self.assertEqual(result["summary"]["included_operation_count"], 2)
            self.assertEqual(result["services"][0]["service_id"], "compute:v1")
            op_names = {op["operation_name"] for op in result["services"][0]["operations"]}
            self.assertEqual(op_names, {"instances-list", "instances-delete"})
            classifications = {op["operation_name"]: op["classification"] for op in result["services"][0]["operations"]}
            self.assertEqual(classifications["instances-delete"], "irreversible")

            coverage = (tmp_path / "docs" / "api_coverage.md").read_text(encoding="utf-8")
            self.assertIn("## Boundary", coverage)
            self.assertIn("## Inventory summary", coverage)
            self.assertIn("## Per-operation evidence", coverage)
            self.assertIn("## Safety and risk coverage", coverage)
            self.assertIn("## Exceptions ledger", coverage)

            generated = json.loads((tmp_path / "docs" / "_generated" / "gcp_discovery_inventory.json").read_text(encoding="utf-8"))
        self.assertEqual(generated["summary"]["included_service_count"], 1)
        generated_names = {op["operation_name"] for op in generated["services"][0]["operations"]}
        self.assertEqual(generated_names, {"instances-list", "instances-delete"})

    def test_generated_registry_uses_kebab_operation_lookup(self) -> None:
        from gcp_safe_agent_cli import generated_registry

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            generated_dir = root / "docs" / "_generated"
            generated_dir.mkdir(parents=True)
            payload = {
                "summary": {"included_service_count": 1, "included_operation_count": 1},
                "services": [
                    {
                        "service_id": "compute:v1",
                        "api_id": "compute",
                        "version": "v1",
                        "title": "Compute Engine API",
                        "operations": [
                            {
                                "operation_id": "compute.instances.list",
                                "operation_name": "instances-list",
                                "classification": "read",
                                "risk_categories": ["no_snapshot"],
                            }
                        ],
                    }
                ],
            }
            (generated_dir / "gcp_discovery_inventory.json").write_text(json.dumps(payload), encoding="utf-8")

            registry = generated_registry.load_registry(root)

        service = registry.get_service("compute")
        self.assertIsNotNone(service)
        self.assertEqual(service["service_id"], "compute:v1")
        operation = registry.get_operation("compute", "instances-list")
        self.assertIsNotNone(operation)
        self.assertEqual(operation["operation_id"], "compute.instances.list")
        self.assertTrue(registry.has_operation("compute", "instances-list"))

    def test_checked_in_inventory_includes_known_gcp_boundary_repairs(self) -> None:
        payload = json.loads((self.root / "docs" / "_generated" / "gcp_discovery_inventory.json").read_text(encoding="utf-8"))
        services = {service["api_id"]: service for service in payload["services"]}
        self.assertIn("cloudtasks", services)
        self.assertEqual(services["cloudtasks"]["version"], "v2")
        self.assertIn("analyticshub", services)
        self.assertEqual(services["analyticshub"]["version"], "v1")
        self.assertIn("datalabeling", services)
        self.assertEqual(services["datalabeling"]["version"], "v1beta1")
        self.assertIn("official_interface_definition_url", services["datalabeling"])
        self.assertIn("integrations", services)
        self.assertEqual(services["integrations"]["version"], "v1+v2-rest")
        self.assertIn("official_rest_documentation_url", services["integrations"])
        integration_operations = {op["operation_name"] for op in services["integrations"]["operations"]}
        self.assertIn("v1-projects-locations-integrations-delete", integration_operations)
        self.assertIn("v2-projects-locations-integrations-executions-task-executions-get", integration_operations)

        gaps = [row for row in payload["exceptions_ledger"] if row["kind"] == "discovery-gap"]
        self.assertEqual(gaps, [])

    def test_cloud_tasks_and_analytics_hub_are_not_excluded_by_broad_names(self) -> None:
        from gcp_safe_agent_cli import gcp_discovery_inventory as inventory_mod

        directory = {
            "items": [
                {
                    "id": "cloudtasks:v2",
                    "name": "cloudtasks",
                    "version": "v2",
                    "title": "Cloud Tasks API",
                    "preferred": True,
                    "documentationLink": "https://cloud.google.com/tasks/",
                    "discoveryRestUrl": "https://cloudtasks.googleapis.com/$discovery/rest?version=v2",
                },
                {
                    "id": "tasks:v1",
                    "name": "tasks",
                    "version": "v1",
                    "title": "Google Tasks API",
                    "preferred": True,
                    "documentationLink": "https://developers.google.com/workspace/tasks/",
                    "discoveryRestUrl": "https://tasks.googleapis.com/$discovery/rest?version=v1",
                },
                {
                    "id": "analyticshub:v1",
                    "name": "analyticshub",
                    "version": "v1",
                    "title": "Analytics Hub API",
                    "preferred": True,
                    "documentationLink": "https://cloud.google.com/bigquery/docs/analytics-hub-introduction",
                    "discoveryRestUrl": "https://analyticshub.googleapis.com/$discovery/rest?version=v1",
                },
                {
                    "id": "analyticsdata:v1beta",
                    "name": "analyticsdata",
                    "version": "v1beta",
                    "title": "Google Analytics Data API",
                    "preferred": True,
                    "documentationLink": "https://developers.google.com/analytics/devguides/reporting/data/v1/",
                    "discoveryRestUrl": "https://analyticsdata.googleapis.com/$discovery/rest?version=v1beta",
                },
            ]
        }
        simple_doc = {
            "resources": {
                "projects": {
                    "methods": {
                        "get": {
                            "id": "service.projects.get",
                            "path": "v1/{+name}",
                            "httpMethod": "GET",
                            "description": "Gets a resource.",
                        }
                    }
                }
            }
        }

        def fake_fetch_json(url: str) -> dict:
            if url.endswith("/discovery/v1/apis"):
                return directory
            if "cloudtasks.googleapis.com" in url or "analyticshub.googleapis.com" in url:
                return simple_doc
            raise AssertionError(f"Excluded service should not be fetched: {url}")

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            with patch.object(inventory_mod, "fetch_json", side_effect=fake_fetch_json):
                result = inventory_mod.generate_inventory(
                    directory_url="https://discovery.googleapis.com/discovery/v1/apis",
                    output_dir=tmp_path / "docs" / "_generated",
                    coverage_path=tmp_path / "docs" / "api_coverage.md",
                )

        included = {service["api_id"] for service in result["services"]}
        self.assertIn("cloudtasks", included)
        self.assertIn("analyticshub", included)
        self.assertNotIn("tasks", included)
        self.assertNotIn("analyticsdata", included)

    def test_datalabeling_uses_official_googleapis_proto_fallback_when_discovery_fails(self) -> None:
        from gcp_safe_agent_cli import gcp_discovery_inventory as inventory_mod

        directory = {
            "items": [
                {
                    "id": "datalabeling:v1beta1",
                    "name": "datalabeling",
                    "version": "v1beta1",
                    "title": "Data Labeling API",
                    "preferred": True,
                    "documentationLink": "https://cloud.google.com/data-labeling/docs/",
                    "discoveryRestUrl": "https://datalabeling.googleapis.com/$discovery/rest?version=v1beta1",
                }
            ]
        }
        proto = """
        service DataLabelingService {
          rpc CreateDataset(CreateDatasetRequest) returns (Dataset) {
            option (google.api.http) = {
              post: "/v1beta1/{parent=projects/*}/datasets"
              body: "*"
            };
          }
          rpc GetDataset(GetDatasetRequest) returns (Dataset) {
            option (google.api.http) = {
              get: "/v1beta1/{name=projects/*/datasets/*}"
            };
          }
        }
        """

        def fake_fetch_json(url: str) -> dict:
            if url.endswith("/discovery/v1/apis"):
                return directory
            raise RuntimeError("Discovery unavailable")

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            with patch.object(inventory_mod, "fetch_json", side_effect=fake_fetch_json), patch.object(
                inventory_mod, "fetch_text", return_value=proto
            ):
                result = inventory_mod.generate_inventory(
                    directory_url="https://discovery.googleapis.com/discovery/v1/apis",
                    output_dir=tmp_path / "docs" / "_generated",
                    coverage_path=tmp_path / "docs" / "api_coverage.md",
                )

        self.assertEqual(result["summary"]["discovery_gap_count"], 0)
        service = result["services"][0]
        self.assertEqual(service["api_id"], "datalabeling")
        self.assertEqual(service["base_url"], "https://datalabeling.googleapis.com/")
        self.assertEqual(service["official_interface_definition_url"], inventory_mod.GOOGLEAPIS_PROTO_FALLBACKS[("datalabeling", "v1beta1")]["source_url"])
        operations = {op["operation_name"]: op for op in service["operations"]}
        self.assertEqual(operations["create-dataset"]["path"], "v1beta1/{+parent}/datasets")
        self.assertEqual(operations["create-dataset"]["classification"], "high_no_snapshot")
        self.assertEqual(operations["get-dataset"]["classification"], "read")

    def test_application_integration_uses_official_rest_docs_when_discovery_fails(self) -> None:
        from gcp_safe_agent_cli import gcp_discovery_inventory as inventory_mod

        directory = {
            "items": [
                {
                    "id": "integrations:v1",
                    "name": "integrations",
                    "version": "v1",
                    "title": "Application Integration API",
                    "preferred": True,
                    "documentationLink": "https://cloud.google.com/application-integration",
                    "discoveryRestUrl": "https://integrations.googleapis.com/$discovery/rest?version=v1",
                }
            ]
        }
        index_html = """
        <a href="/application-integration/docs/reference/rest/v1/projects.locations.integrations/delete">delete</a>
        <a href="/application-integration/docs/reference/rest/v2/projects.locations.integrations.executions.taskExecutions/get">get</a>
        """
        pages = {
            "https://docs.cloud.google.com/application-integration/docs/reference/rest": index_html,
            "https://docs.cloud.google.com/application-integration/docs/reference/rest/v1/projects.locations.integrations/delete": """
                <h1>Method: projects.locations.integrations.delete</h1>
                Delete the selected integration and all versions inside
                <h2>HTTP request</h2>
                <code>DELETE https://integrations.googleapis.com/v1/{name=projects/*/locations/*/integrations/*}</code>
            """,
            "https://docs.cloud.google.com/application-integration/docs/reference/rest/v2/projects.locations.integrations.executions.taskExecutions/get": """
                <h1>Method: projects.locations.integrations.executions.taskExecutions.get</h1>
                Get a TaskExecution in the specified project.
                <h2>HTTP request</h2>
                <code>GET https://integrations.googleapis.com/v2/{name=projects/*/locations/*/integrations/*/executions/*/taskExecutions/*}</code>
            """,
        }

        def fake_fetch_json(url: str) -> dict:
            if url.endswith("/discovery/v1/apis"):
                return directory
            raise RuntimeError("Discovery unavailable")

        def fake_fetch_text(url: str) -> str:
            try:
                return pages[url]
            except KeyError as exc:
                raise AssertionError(f"Unexpected URL: {url}") from exc

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            with patch.object(inventory_mod, "fetch_json", side_effect=fake_fetch_json), patch.object(
                inventory_mod, "fetch_text", side_effect=fake_fetch_text
            ):
                result = inventory_mod.generate_inventory(
                    directory_url="https://discovery.googleapis.com/discovery/v1/apis",
                    output_dir=tmp_path / "docs" / "_generated",
                    coverage_path=tmp_path / "docs" / "api_coverage.md",
                )

        self.assertEqual(result["summary"]["discovery_gap_count"], 0)
        service = result["services"][0]
        self.assertEqual(service["api_id"], "integrations")
        self.assertEqual(service["version"], "v1+v2-rest")
        self.assertEqual(service["base_url"], "https://integrations.googleapis.com/")
        self.assertEqual(service["official_rest_documentation_url"], inventory_mod.OFFICIAL_REST_DOC_FALLBACKS[("integrations", "v1")]["source_url"])
        operations = {op["operation_name"]: op for op in service["operations"]}
        self.assertEqual(
            operations["v1-projects-locations-integrations-delete"]["path"],
            "v1/{+name}",
        )
        self.assertEqual(operations["v1-projects-locations-integrations-delete"]["classification"], "irreversible")
        self.assertEqual(
            operations["v2-projects-locations-integrations-executions-task-executions-get"]["path"],
            "v2/{+name}",
        )
        self.assertEqual(
            operations["v2-projects-locations-integrations-executions-task-executions-get"]["classification"],
            "read",
        )
        self.assertIn("source=https://docs.cloud.google.com/application-integration/docs/reference/rest/v1/projects.locations.integrations/delete", operations["v1-projects-locations-integrations-delete"]["evidence"])
