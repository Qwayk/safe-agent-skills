# Architecture

The Contentsquare skill is built as a small command-line tool with explicit command groups for Data Export, Metrics, Enrichment, and Speed Analysis Lab, plus shared OAuth, safety, output, and run-record helpers. This matters when an agent is using the skill for real work. A reviewer can see where commands come from, where request values are checked, where plans and receipts are written, and why unsupported tracking SDKs or warehouse setup docs should not be hidden inside this server-side CLI.

A good architecture check is: confirm the command maps to a documented server-side Contentsquare endpoint, then check that the shared OAuth, dry-run plan, apply gates, redaction, and receipt output still handle that command family.

Read this after the user-facing docs, not before them. Do not add a catch-all request command to make missing coverage look complete.

## Runtime

- `cli.py`: argument parsing + shared flags
- `config.py`: `.env` parsing and validation
- `http.py`: HTTP client wrapper around `requests`
- `audit_log.py`: optional JSONL audit events (secrets redacted)
- `runs.py`: local run artifacts + history index (`.state/runs/`)
- `errors.py`: consistent error taxonomy (`ValidationError`, `SafetyError`, `NotSupportedError`)
- `json_files.py`: safe JSON read/write helpers for plan/receipt files
- `contentsquare_client.py`: family-aware OAuth and documented Contentsquare API calls
- `catalog.py`: command-family metadata and coverage helpers
- `oauth_tokens.py`: server-to-server token request shape and redacted token handling
- `project_config.py`: local project and run settings

## Request flow

1. The CLI parses a named Contentsquare command.
2. The command family selects the documented OAuth scope.
3. Read commands call the official endpoint and return one JSON object.
4. Write commands create a dry-run plan unless a reviewed plan is applied.
5. Apply checks the saved plan, required flags, and required acknowledgements.
6. Receipts and run records are written only after the command reaches its expected step.
