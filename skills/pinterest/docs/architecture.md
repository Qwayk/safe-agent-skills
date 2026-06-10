# Architecture

Layers:
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
