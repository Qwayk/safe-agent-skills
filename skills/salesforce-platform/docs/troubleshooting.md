# Troubleshooting

## `Missing SALESFORCE_INSTANCE_URL`

Set `SALESFORCE_INSTANCE_URL` in `.env`.

## `Missing Salesforce access token`

Either:

- set `SALESFORCE_ACCESS_TOKEN` in `.env`, or
- run `qwayk-salesforce-platform-safe-agent-cli auth token set --file token.json`

## `SALESFORCE_API_VERSION must look like 67.0`

Use the bare version number. Do not include the `v` prefix in `.env`.

## Knowledge article reads fail

Support Knowledge endpoints often need:

- `--header Accept-Language=en-US`
- extra filters through `--query-param`

They also require Salesforce Knowledge to be enabled in the org.

## Bulk results are too large for stdout

Use `--download-to` for CSV or binary responses.

## Blob upload request is rejected

For documented blob-upload flows, use `--multipart-file` instead of `--body-file`.

## Debugging

- `--verbose` prints request start and finish lines to stderr.
- `--debug` re-raises exceptions with a full stack trace.
