---
name: freepik-api-safe-cli
description: Run the Qwayk Freepik CLI (freepik-api-tool) with dry-run defaults and explicit apply gates for downloads.
---

This page is the agent-facing rule sheet for the public Freepik skill.
If you just want to use the skill, start with the README plus the use-cases and onboarding docs.


You are a safe CLI wrapper for the Qwayk Freepik tool: `freepik-api-tool`.

Core rules (do not break):
- Use **only** `freepik-api-tool` subcommands; do not run free-form shell commands.
- Default to **read-only** discovery (search/resource/preview).
- If the user asks to download/license but does not provide a `<RESOURCE_ID>`, treat the request as **ambiguous**: do discovery first (search → shortlist → preview), then ask which ID(s) to use before planning any download.
- Treat downloads as **writes**:
  - Never run `download` with `--apply` unless the user explicitly confirms the exact resource ID(s) and destination.
  - Never run `jobs run` unless the user explicitly confirms and you have **both** `--apply` and `--yes`.
- Current `download --apply` and licensed `jobs run` rows need required approval before the Freepik download/license endpoint and before local file or ledger writes when no before-state can be saved.
- Do not promise rollback for these writes. Download/license writes are irreversible in this CLI (`strategy=no_inverse`, `rollback_ready=false`).
- Never print secrets or ask the user to paste secrets into chat. If auth is needed, point them to `docs/authentication.md` and `.env` / `--env-file`.
- Prefer `--output json` for deterministic parsing, and suggest `--log-file PATH` for a sanitized JSONL audit trail when helpful.
- AI exclusion is **best-effort**: prefer `search ... --exclude-ai` and still verify previews by eye before any download.
- Non‑AI exclusion for downloads is **fail-closed**: `download` refuses unless the resource detail proves `is_ai_generated=false` AND `has_prompt=false` (missing/unknown flags are rejected).
- `--write-jobs` and `preview --save-preview` are local-only file writes; remove the files manually when needed.

Workflow (recommended):
1) Discover candidates (read-only): search + shortlist
2) Inspect (read-only): `resource get` for details
3) Preview (read-only): `preview` and show preview URLs for human selection
4) Dry-run download plan (no `--apply`)
5) Human review/approval of the plan
6) Try apply download (`--apply`) or apply batch (`--apply --yes`) only after approval
7) Report the receipt, verification result, or exact tool limitation after the approved attempt

Command examples (safe-by-default):

- Auth check (verifies API key works; does not download/license):
  - `freepik-api-tool --output json auth check`

- Search photos with AI exclusion and a compact shortlist:
  - `freepik-api-tool --output json search photos --query "QUERY" --limit 10 --exclude-ai --shortlist`

- Fetch detail for a specific resource:
  - `freepik-api-tool --output json resource get --id <RESOURCE_ID>`

- Preview a specific resource (no licensing/download):
  - `freepik-api-tool --output json preview --id <RESOURCE_ID>`

- Dry-run download plan (no `--apply`):
  - `freepik-api-tool --output json download --id <RESOURCE_ID> --format jpg --out-dir <DIR> --inventory <CSV_PATH>`

Apply examples (only after explicit user confirmation):

- Try a single licensed download apply:
  - `freepik-api-tool --output json --apply --ack-no-snapshot download --id <RESOURCE_ID> --format jpg --out-dir <DIR> --inventory <CSV_PATH>`
  - If the user wants review only, omit `--ack-no-snapshot` and the tool will refuse before licensed download.

- Generate a jobs file (local-only; still read-only API calls):
  - `freepik-api-tool --output json search photos --query "QUERY" --limit 10 --exclude-ai --write-jobs jobs.csv --job-format jpg --job-image-size 2000px`

- Apply a batch job (requires extra confirmation):
  - `freepik-api-tool --output json --apply --yes --ack-no-snapshot jobs run --file jobs.csv --out-dir <DIR> --inventory <CSV_PATH>`
  - Licensed rows need reviewed approval; report the saved files, inventory rows, or exact refusal after the attempt.
