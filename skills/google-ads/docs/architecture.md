# Architecture

Google Ads is built as a small command-line tool for customer access, GAQL reads, campaign settings, budgets, criteria, and bulk mutate work. The architecture is intentionally plain: commands parse the user request, configuration loads only the needed account settings, the client layer talks to the API, and the output layer returns one predictable JSON result.

This matters when an agent is using the skill for real work. You can see where credentials are loaded, where HTTP requests happen, where local plans or receipts are saved, and where safety checks stop a risky action before it reaches Google Ads.

A good architecture check is: "Show me which layer handles configuration, which layer sends the API request, and where a plan or receipt would be saved for Google Ads."

## Runtime layers

- `cli.py`: argument parsing + shared flags
- `commands/*`: user-facing verbs
  - `commands/helpers.py`: strict wrappers for repeated account edits
  - `commands/builders.py`: strict whole-campaign builders that compile one deterministic `GoogleAdsService.Mutate` request
- `config.py`: `.env` parsing and validation
- `google_ads_client.py`: Google Ads client construction + protobuf conversion helpers
- `audit_log.py`: optional JSONL audit events (secrets redacted)
- `runs.py`: local run history + artifacts (`.state/runs/` next to `--env-file` for write-capable commands)
- `errors.py`: consistent error taxonomy (`ValidationError`, `SafetyError`, `NotSupportedError`)
- `json_files.py`: safe JSON read/write helpers
