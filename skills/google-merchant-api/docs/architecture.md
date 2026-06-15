# Architecture

Google Merchant Center is built as a small command-line tool for accounts, products, feeds, promotions, shipping, and merchant settings. The architecture is intentionally plain: commands parse the user request, configuration loads only the needed account settings, the client layer talks to the API, and the output layer returns one predictable JSON result.

This matters when an agent is using the skill for real work. You can see where credentials are loaded, where HTTP requests happen, where local plans or receipts are saved, and where safety checks stop a risky action before it reaches Google Merchant Center.

A good architecture check is: "Show me which layer handles configuration, which layer sends the API request, and where a plan or receipt would be saved for Google Merchant Center."

## Runtime layers

- `cli.py`: argument parsing + shared flags
- `commands/*`: user-facing verbs
- `config.py`: `.env` parsing and validation
- `http.py`: HTTP client wrapper around `requests`
- `audit_log.py`: optional JSONL audit events (secrets redacted)
- `runs.py`: local run artifacts + history index (`.state/runs/`)
- `errors.py`: consistent error taxonomy (`ValidationError`, `SafetyError`, `NotSupportedError`)
- `json_files.py`: safe JSON read/write helpers for plan/receipt files
