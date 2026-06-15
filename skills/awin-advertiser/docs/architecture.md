# Architecture

Awin Advertiser is built as a small command-line tool for advertiser transactions, publisher checks, offers, product feeds, and conversion work. The architecture is intentionally plain: commands parse the user request, configuration loads only the needed account settings, the client layer talks to the API, and the output layer returns one predictable JSON result.

This matters when an agent is using the skill for real work. You can see where credentials are loaded, where HTTP requests happen, where local plans or receipts are saved, and where safety checks stop a risky action before it reaches Awin Advertiser.

A good architecture check is: "Show me which layer handles configuration, which layer sends the API request, and where a plan or receipt would be saved for Awin Advertiser."

## Runtime layers

- `__main__.py`: starts the installed command and hands control to the CLI.
- `audit_log.py`: writes optional audit events without printing secret values.
- `cli.py`: parses commands, shared flags, dry-run/apply choices, and routes each request.
- `config.py`: loads `.env`, validates required Awin values, and keeps secrets out of normal output.
- `errors.py`: turns validation, safety, and provider problems into predictable errors.
- `http.py`: sends Awin API requests with redaction-safe error handling.
- `json_files.py`: reads and writes plan, receipt, and input JSON files safely.
- `output.py`: keeps the one-object JSON output contract stable.
- `project_config.py`: keeps project-level defaults separate from command logic.
- `runs.py`: records local plans, receipts, and run history under `.state/runs/`.

## Safety and state

- Read commands go straight through the request path and do not change the advertiser account.
- Write-capable commands start as plans and require the apply flags plus a reviewed plan file before live changes.
- Local run history keeps the review trail separate from the Awin account, so an agent can show what it planned or applied without exposing secrets.

## Why this shape matters

Awin Advertiser mixes bearer-token reads, access-token query patterns, and `x-api-key` conversion work. Keeping command parsing, configuration, HTTP calls, run history, and output formatting separate makes those differences easier to inspect and harder to blur during live work.
