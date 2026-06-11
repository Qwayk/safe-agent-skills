# Architecture

Layers:
- `cli.py`: argument parsing + shared flags
- `commands/*`: user-facing verbs
- `config.py`: `.env` parsing and validation
- `http.py`: HTTP client wrapper around `requests`
- `plausible.py`: Plausible API wrapper
- `audit_log.py`: optional JSONL audit events (secrets redacted)
