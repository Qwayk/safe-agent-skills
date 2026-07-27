# Configuration

The CLI reads `.env` by default. OS environment values override the file.

| Variable | Required | Meaning |
| --- | --- | --- |
| `JIRA_BASE_URL` | yes | Jira site URL for Basic auth, or the official `api.atlassian.com/ex/jira/<cloudId>` base for OAuth. |
| `JIRA_EMAIL` | with Basic auth | Atlassian account email. |
| `JIRA_API_TOKEN` | with Basic auth | Atlassian API token. |
| `JIRA_OAUTH_ACCESS_TOKEN` | with OAuth | Existing OAuth 2.0 bearer token. Takes priority when both methods exist. |
| `JIRA_TIMEOUT_S` | no | Positive request timeout in seconds; default `30`. |

Basic auth accepts only a root Jira Cloud site URL shaped like `https://your-domain.atlassian.net`. OAuth accepts only `https://api.atlassian.com/ex/jira/<cloudId>`, with no extra path. Custom production ports, embedded credentials, query strings, fragments, and other hosts are refused before HTTP. Root `localhost` and `127.0.0.1` URLs are reserved for local tests.

`JIRA_EMAIL` and `JIRA_API_TOKEN` must be set together. When a write plan is created, the CLI also creates `.state/plan-signing.key` with mode `0600`. Keep that local file private. A plan must be applied with the same `.env` location and local signing key that created it; if the key is missing, create and review a new plan.

`.env`, `.state/`, `.venv/`, build output, caches, and package metadata are gitignored.
