# Architecture

Meta Ads is built as a small command-line tool for ad accounts, campaigns, ad sets, ads, insights, and Graph API inventory. The architecture is intentionally plain: commands parse the user request, configuration loads only the needed account settings, the client layer talks to the API, and the output layer returns one predictable JSON result.

This matters when an agent is using the skill for real work. You can see where credentials are loaded, where HTTP requests happen, where local plans or receipts are saved, and where safety checks stop a risky action before it reaches Meta Ads.

A good architecture check is: "Show me which layer handles configuration, which layer sends the API request, and where a plan or receipt would be saved for Meta Ads."

## Runtime layers

- `cli.py`: argument parsing + shared flags + output contract
- `commands/*`: user-facing command handlers
- `config.py`: `.env` parsing + validation + defaults
- `http.py`: HTTP client wrapper around `requests` (GET-only; token-safe verbose logging)
- `graph.py`: Graph API helper (versioned URL building, paging, error normalization)
- `audit_log.py`: optional JSONL audit events (secrets redacted)
- `errors.py`: consistent error taxonomy (`ValidationError`, `NotSupportedError`, `RemoteApiError`)
