# Architecture

Fortnox is built as a small command-line tool for invoices, supplier bills, bookkeeping, payroll, stock, attachments, websocket topics, and plan-first changes. The architecture is intentionally plain: commands parse the requested Fortnox job, configuration loads only local account settings, the API layer sends official Fortnox REST or websocket requests, and the output layer returns one predictable JSON result.

This matters when an agent is using the skill for real work. You can see where credentials are loaded, where Fortnox requests happen, where local plans or receipts are saved, and where safety checks stop risky work before it reaches live accounting or customer records.

A good architecture check is: "Show me which layer handles Fortnox configuration, which layer sends the API or websocket request, and where a plan or receipt would be saved before a risky change."

## Architecture notes

Read this page before changing or reviewing how the public skill is wired.

## Runtime layers

- `cli.py`: argument parsing + shared flags
- `commands/*`: user-facing verbs
- `config.py`: `.env` parsing and validation
- `http.py`: HTTP client wrapper around `requests`
- `audit_log.py`: optional JSONL audit events (secrets redacted)
- `runs.py`: local run artifacts + history index (`.state/runs/`)
- `errors.py`: consistent error taxonomy (`ValidationError`, `SafetyError`, `NotSupportedError`)
- `json_files.py`: safe JSON read/write helpers for plan/receipt files
