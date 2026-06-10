# Architecture

Layers:
- `cli.py`: argument parsing + shared flags + output contract
- `commands/*`: user-facing command handlers
- `config.py`: `.env` parsing + validation + defaults
- `http.py`: HTTP client wrapper around `requests` (GET-only; token-safe verbose logging)
- `graph.py`: Graph API helper (versioned URL building, paging, error normalization)
- `audit_log.py`: optional JSONL audit events (secrets redacted)
- `errors.py`: consistent error taxonomy (`ValidationError`, `NotSupportedError`, `RemoteApiError`)
