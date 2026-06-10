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
- Refuse licensed download apply before the Freepik download/license endpoint until real saved snapshot support is available.
- When licensed apply is safely enabled later, verify inventory/audit logging before calling it done.
