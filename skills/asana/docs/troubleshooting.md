# Troubleshooting

## The CLI says the token is missing

Put an already-issued bearer token in `ASANA_ACCESS_TOKEN` in the selected `.env` file or OS environment. Check that global `--env-file` comes before `auth` or `api`. The tool cannot create, exchange, or refresh a token.

## Asana returns 401

The token is invalid, expired, revoked, or not being read from the intended env file. Replace it outside the CLI, then run `auth check`. The error never prints the token.

## Asana returns 403

The token was understood but the user, OAuth scopes, service account, account plan, or feature access does not allow that target. Run `commands show COMMAND` to inspect the official OAuth scopes and access notes. Do not switch to a raw request.

## A parameter or body is refused locally

Use `commands show COMMAND`. Parameter names are exact. Asana JSON bodies need a top-level `data` object. Attachment form fields are different and accept only documented multipart fields; `connect_to_app` is outside this tool.

## Apply says the plan changed

The plan, its authenticated signature, or the local signing key no longer matches. Create a new plan and review it. Do not edit a saved plan or recompute its public ID to bypass the check.

## Apply says the target changed

The current same-target read does not match the saved before-state. Another person or process changed Asana after planning. Read the target again and create a new plan.

## Apply asks for another acknowledgement

`--acknowledge-no-snapshot` accepts that no reliable before-state exists. `--acknowledge-risk` accepts the plan's named destructive, wider, administrative, collaboration, file, export, webhook, rule, agent, budget, rate, approval, or automation risk. Add only the flag the reviewed plan requires.

## An async request did not finish

Accepted, queued, running, or timed out is not completion. Use `--wait` when the response contains a job GID, or use the fixed job/export/status command shown in the command inventory. A missing job GID remains unverified.

## Rate limiting

The HTTP client retries reads for a small bounded set of 429 and transient 5xx responses and respects `Retry-After` up to 30 seconds. Writes are not retried automatically because an uncertain retry could duplicate a change. If limits continue, narrow requested fields, reduce pages or concurrency outside the CLI, and create a new plan later.

## Debug output

`--verbose` writes method, official path, status, and timing to stderr without query values or headers. `--debug` adds a local traceback for code debugging. JSON stdout remains one object.
