# Safety model

## Core rules

- Read commands run directly.
- A small number of non-mutating `POST` endpoints also run directly because they generate derived results rather than change org data. Current examples are parameterized search, scheduler lookup calls, and `openapi-sobjects create`.
- Write-capable commands default to dry-run plans.
- Apply requests need `--apply`.
- Higher-risk apply requests also require `--yes`.
- Irreversible deletes and resets also require `--ack-irreversible`.
- User password set/reset commands require `--plan-in` on apply.
- After those gates and any plan drift check pass, Salesforce write apply saves before-state when practical. When no useful before-state can be saved, apply requires explicit no-snapshot approval before provider HTTP and records that limit in the receipt.
- The tool never prints raw access tokens.

## Plans, refusals, and drift checks

- Dry-run writes emit a plan.
- Write plans include `before_state.required: true`, `before_state.supported: false`, and a `no-snapshot-approval` verification plan.
- Approved supported apply requests emit write receipts. Missing approval, plan drift, missing credentials, unclear targets, or failed safety checks emit safe refusals instead.
- When you apply from `--plan-in`, the tool checks that the current request still matches the saved plan fingerprint.
- If the request drifts, the tool refuses the apply.

## Recovery contract for planned writes

- Plans include `recovery` with explicit no-recovery fields:
  - `automatic_rollback: false`
  - `backups: []`
  - `snapshots: []`
  - `rollback_plan: null`
  - `restore_note: "No automatic rollback, snapshots, or backups are created. If a restore action is available, run a separate explicit restore command as its own command."`
- Plan `rollback` and plan `recovery` include explicit no-recovery notes.

## Multipart blob uploads

Blob uploads are supported through `--multipart-file` on the documented sObject create, update, external-ID upsert, and collections write flows.

The manifest is reviewed in dry-run like any other write input. The plan records part names, content types, file sizes, and content hashes without printing binary data.

## Local proof artifacts

Write-capable commands create local proof artifacts next to the selected `--env-file`:

- `.state/runs/<run_id>/plan.json`
- `.state/runs/<run_id>/receipt.json` when an approved supported write proceeds
- `.state/runs/<run_id>/summary.md`
- `.state/runs/<run_id>/audit.jsonl`

Use `runs list` and `runs show` to inspect this history.
