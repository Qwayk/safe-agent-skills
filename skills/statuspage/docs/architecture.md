# Architecture

Layers:
- `cli.py`: argument parsing + shared flags
- `statuspage_client.py`: small Status API wrapper (URL construction + GET + JSON parsing)
- `config.py`: `.env` parsing and validation
- `http.py`: HTTP client wrapper around `requests`
- `audit_log.py`: optional JSONL audit events (secrets redacted)
- `errors.py`: consistent error taxonomy (`ValidationError`, `SafetyError`, `NotSupportedError`)
