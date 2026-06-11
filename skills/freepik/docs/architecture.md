# Architecture

Layers:
- `cli.py`: argument parsing + shared flags
- `config.py`: `.env` parsing and validation
- `http.py`: HTTP client with verbose request lines + METHOD/URL on exceptions
- `freepik_api.py`: API wrapper (endpoints)
- `inventory.py`: inventory CSV ledger and SHA-256
- `commands/*`: user-facing commands

Extending safely:
- Add a new verb in `commands/`
- Keep downloads dry-run by default.
- Licensed apply must keep explicit `--ack-no-snapshot` approval until real saved snapshot support exists.
- Keep inventory and audit logging aligned with the real live-download behavior.
