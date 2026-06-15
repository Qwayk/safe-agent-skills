# Architecture

YouTube is built as a small command-line tool for channels, videos, captions, playlists, uploads, metadata, and OAuth state. The architecture is intentionally plain: commands parse the user request, configuration loads only the needed account settings, the client layer talks to the API, and the output layer returns one predictable JSON result.

This matters when an agent is using the skill for real work. You can see where credentials are loaded, where HTTP requests happen, where local plans or receipts are saved, and where safety checks stop a risky action before it reaches YouTube.

A good architecture check is: "Show me which layer handles configuration, which layer sends the API request, and where a plan or receipt would be saved for YouTube."

## Architecture notes

This section is mainly for maintenance: it shows where each part of the YouTube tool lives and how requests move through the code.

Layers:
- `cli.py`: argument parsing + shared flags
- `commands/*`: user-facing verbs
- `config.py`: `.env` parsing and validation
- `http.py`: HTTP client wrapper around `requests`
- `audit_log.py`: optional JSONL audit events (secrets redacted)
- `runs.py`: local run artifacts + history index (`.state/runs/`)
- `errors.py`: consistent error taxonomy (`ValidationError`, `SafetyError`, `NotSupportedError`)
- `json_files.py`: safe JSON read/write helpers for plan/receipt files
- `commands/write_safety.py`: shared saved-state safety contracts for write-capable flows
