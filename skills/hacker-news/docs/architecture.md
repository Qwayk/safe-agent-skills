# Architecture

Layers:
- `cli.py`: argument parsing, shared flags, JSON-safe errors, and command routing
- `hacker_news_client.py`: small Hacker News API wrapper for URL building and JSON reads
- `config.py`: `.env` parsing and API root validation
- `http.py`: HTTP wrapper around `requests`
- `output.py`: deterministic stdout contract
- `audit_log.py`: optional JSONL audit events with redaction
- `errors.py`: consistent error types
