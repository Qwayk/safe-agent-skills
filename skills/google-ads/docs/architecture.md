# Architecture

Layers:
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
