# References

This page records the official sources behind the tool so the behavior is easy to audit later.

Prefer official Google docs. If something depends on another source, say why it was used.

Guidelines:
- Never include secrets in this file.
- When a capability depends on a specific documented behavior, link the exact page.
- Update this file whenever you add or change behavior based on new research.

## Provider docs (official)

- Google Application Default Credentials: https://docs.cloud.google.com/docs/authentication/application-default-credentials
- Troubleshoot ADC: https://docs.cloud.google.com/docs/authentication/troubleshoot-adc
- Quota project overview: https://docs.cloud.google.com/docs/quotas/quota-project
- Set the quota project: https://docs.cloud.google.com/docs/quotas/set-quota-project
- Discovery API overview: https://docs.cloud.google.com/docs/discovery
- Discovery API use guide: https://docs.cloud.google.com/docs/discovery/use-api
- Discovery API list method: https://docs.cloud.google.com/docs/discovery/list
- Google Discovery directory used for the generated inventory: https://discovery.googleapis.com/discovery/v1/apis
- Google Discovery format reference: https://developers.google.com/discovery
- Google public API interface definitions used as the fallback source family: https://github.com/googleapis/googleapis
- Data Labeling fallback proto used when Discovery was unavailable: https://raw.githubusercontent.com/googleapis/googleapis/master/google/cloud/datalabeling/v1beta1/data_labeling_service.proto
- Cloud Tasks REST reference used to confirm `cloudtasks:v2`: https://docs.cloud.google.com/tasks/docs/reference/rest
- BigQuery Analytics Hub REST reference used to confirm `analyticshub:v1`: https://docs.cloud.google.com/bigquery/docs/reference/analytics-hub/rest
- Application Integration REST reference used to generate the v1 and v2 fallback command surface: https://docs.cloud.google.com/application-integration/docs/reference/rest
- `gcloud auth application-default login`: https://docs.cloud.google.com/sdk/gcloud/reference/auth/application-default/login
- `gcloud auth application-default set-quota-project`: https://docs.cloud.google.com/sdk/gcloud/reference/auth/application-default/set-quota-project
- Last verified (UTC): `2026-06-25`

## Local source inputs

- Generated inventory: `docs/_generated/gcp_discovery_inventory.json`
- Generated from the official Google Discovery directory on `2026-06-25`
- Coverage summary: `docs/api_coverage.md`

## Other sources (only if needed)

- None
