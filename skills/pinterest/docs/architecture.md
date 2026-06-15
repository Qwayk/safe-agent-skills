# Architecture

Pinterest is built as a small command-line tool for boards, pins, ads, catalogs, reports, and auth state. The architecture is intentionally plain: commands parse the user request, configuration loads only the needed account settings, the client layer talks to the API, and the output layer returns one predictable JSON result.

This matters when an agent is using the skill for real work. You can see where credentials are loaded, where HTTP requests happen, where local plans or receipts are saved, and where safety checks stop a risky action before it reaches Pinterest.

A good architecture check is: "Show me which layer handles configuration, which layer sends the API request, and where a plan or receipt would be saved for Pinterest."

## Runtime layers

- `cli.py`: argument parsing + shared flags
- `commands/*`: user-facing verbs
- `config.py`: `.env` parsing and validation
- `http.py`: HTTP client wrapper around `requests`
- `api.py`: Pinterest API wrapper (auth headers + pagination helpers)
- `audit_log.py`: optional JSONL audit events (secrets redacted)

Token storage:
- `.env` can hold `PINTEREST_ACCESS_TOKEN` (short-lived) or refresh-token credentials.
- `.state/token.json` holds the current access token (and refresh token if available). It is gitignored.
- `resolve_access_token(...)` chooses the best available token and refreshes when needed.

Audit snapshot:
- Implemented in `commands/audit.py`.
- Fetches boards, sections-by-board, pins, and (optionally) analytics.
- Writes one JSON file per “stage” so it’s easy to diff and review.
