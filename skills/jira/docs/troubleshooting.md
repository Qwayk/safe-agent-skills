# Troubleshooting

## Missing Jira credentials

Run `jira-safe onboarding`, fill `.env`, then use `jira-safe --env-file .env auth check`. Basic auth needs the URL, email, and API token together. OAuth needs the URL and bearer access token.
Basic URLs must be root `https://your-domain.atlassian.net` sites. OAuth URLs must be exactly `https://api.atlassian.com/ex/jira/<cloudId>`. The CLI intentionally refuses other hosts and paths.

## A reviewed plan now says the signing key is missing

Plans are tied to the private `.state/plan-signing.key` beside the selected `.env` file. Do not copy the key or weaken its mode. Create a new plan on this install, review it, and apply that new plan.

## HTTP 401 or 403

401 normally means Jira rejected the credential. 403 normally means the connected user or OAuth scopes cannot perform that operation. The CLI does not print Jira's response body because it can contain private account information.

## A command says it is gated or excluded

Read its row in `docs/api_coverage.md`. Forge-only and Connect-only operations need an app runtime the CLI does not provide. Jira Service Management service registry and Jira Operations are outside this product. Experimental rows are named but do not run.

## Apply refuses a changed file

The body or upload hash no longer matches the reviewed plan. Create a new dry-run plan from the updated file and review it again.

## Before-state read failed

The write stopped before mutation. Fix access or the target and retry. Use `--ack-no-snapshot` only when you have reviewed why the snapshot is unavailable and accept continuing without it.

## Jira returned binary content

Rerun the same fixed read with `--response-out FILE`. Binary content is saved to disk and never printed into JSON output.
