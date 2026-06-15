# Troubleshooting

When Salesforce Platform stops or returns an error, start with the boring checks first: setup, account access, target IDs, API limits, and the tool's safety gates. That usually tells you whether the problem is local configuration, provider permissions, a bad request, or a write that correctly refused to run.

Keep the JSON error output. It is the best clue for an agent reviewing records, objects, fields, queries, and org metadata, and it is safer than retrying commands blindly. For any write-related error, stop before retrying and confirm the needed approval or plan.

A good first troubleshooting ask is: "Read the Salesforce Platform error, explain what failed in plain English, tell me the safest next check, and do not retry any write or destructive action."

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
