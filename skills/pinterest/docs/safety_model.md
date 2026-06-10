# Safety model

This tool is read-mostly. It can read Pinterest data and write requested local exports, but current Pinterest write families are plan-and-approve-with-no-snapshot-warning when no saved snapshot is available.

Core rules:
- Default write-family behavior is a dry-run plan or read-only preview. No Pinterest provider write is sent.
- Dry-run plans include `before_state.required: true`, `before_state.supported: false`, and `before_state.status: "no_snapshot_available"`.
- Confirmed apply attempts still require `--apply --yes`.
- Destructive operations additionally require `--ack-irreversible`.
- Ads operations that can increase spend additionally require `--ack-spend`.
- Operations that can trigger significant remote work, like feed ingest or report jobs, additionally require `--ack-volume`.
- After all required flags are present, the tool requires explicit no-snapshot approval before Pinterest provider writes, local token writes, report receipts/downloads, job output, or successful write receipts.
- The tool has no built-in rollback, restore, or provider backup path for remote writes.

Allowed local outputs:
- `audit snapshot` writes JSON files locally after read-only Pinterest calls.
- `pins links plan` writes a local plan file from prior pin data.
- Optional `--log-file` writes redacted JSONL audit events.

Blocked local setup writes:
- `auth login`, `auth code exchange`, and `auth token set` require explicit no-snapshot approval before token exchange, `.state/token.json` writes, or `.env` updates.
- For reads today, use a manually configured `.env` token or refresh-token values.

Write-capable families now covered by the explicit no-snapshot approval:
- Boards: `boards create|update|delete|ensure`.
- Board sections: `board-sections create|update|delete|ensure`.
- Pins: `pins create|update|delete|save|ensure`.
- Pin link hygiene: `pins links apply`.
- Ads: `ads campaigns create|update|pause|resume`, `ads ad-groups create|update|pause|resume`, and `ads ads create|update|pause|resume`.
- Catalogs: `catalogs create` and `catalogs feeds create|update|ingest`.
- Ads reports: `ads reports create` and `ads reports run`.
- Batch jobs: `jobs run` for remote-write rows such as `ads.reports.run`.

What must be added before live apply can be allowed:
- Command-specific before-state capture or a provider-backed backup ID.
- A verification plan tied to the saved before-state.
- Clear rollback status. For Pinterest this may remain `automatic_rollback: false`, but the lack of rollback must be explicit before any live write is allowed.
