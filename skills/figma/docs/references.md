# References (official sources used)

Provider: Figma  
Last verified (UTC): `2026-05-27`

## Official source-of-truth documents

- `Figma REST API` home: https://developers.figma.com/docs/rest-api/
- OpenAPI spec: https://raw.githubusercontent.com/figma/rest-api-spec/main/openapi/openapi.yaml
- file endpoints: https://developers.figma.com/docs/rest-api/file-endpoints/
- version history endpoints: https://developers.figma.com/docs/rest-api/version-history-endpoints/
- comments endpoints: https://developers.figma.com/docs/rest-api/comments-endpoints/
- users endpoints: https://developers.figma.com/docs/rest-api/users-endpoints/
- projects endpoints: https://developers.figma.com/docs/rest-api/projects-endpoints/
- component endpoints: https://developers.figma.com/docs/rest-api/component-endpoints/
- webhooks endpoints: https://developers.figma.com/docs/rest-api/webhooks-endpoints/
- activity logs endpoints: https://developers.figma.com/docs/rest-api/activity-logs-endpoints/
- developer logs endpoints: https://developers.figma.com/docs/rest-api/developer-logs-endpoints/
- discovery endpoints: https://developers.figma.com/docs/rest-api/discovery-endpoints/
- payments endpoints: https://developers.figma.com/docs/rest-api/payments-endpoints/
- variables endpoints: https://developers.figma.com/docs/rest-api/variables-endpoints/
- dev resources endpoints: https://developers.figma.com/docs/rest-api/dev-resources-endpoints/
- library analytics endpoints: https://developers.figma.com/docs/rest-api/library-analytics-endpoints/
- oembed endpoints: https://developers.figma.com/docs/rest-api/oembed-endpoints/

## Project-owned source-of-truth module

- `this skill folder/src/figma_safe_agent_cli/operation_specs.py`

## Validation note

- `GET /v1/discovery` is included from official docs but is not present in the published OpenAPI YAML; it is captured in the inventory as a docs-backed endpoint until validated against live behavior.
