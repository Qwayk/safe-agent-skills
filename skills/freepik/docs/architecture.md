# Architecture

Freepik is built as a small command-line tool for image search, licensed downloads, binary fetches, and local inventory files. The architecture is intentionally plain: commands parse the user request, configuration loads only the needed account settings, the client layer talks to the API, and the output layer returns one predictable JSON result.

This matters when an agent is using the skill for real work. You can see where credentials are loaded, where HTTP requests happen, where local plans or receipts are saved, and where safety checks stop a risky action before it reaches Freepik.

A good architecture check is: "Show me which layer handles configuration, which layer sends the API request, and where a plan or receipt would be saved for Freepik."

## Runtime layers

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
