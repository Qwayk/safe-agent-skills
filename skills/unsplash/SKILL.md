---
name: unsplash-api-safe-cli
description: Run the Unsplash Qwayk CLI with dry-run by default and explicit apply gates.
---

This page is the agent-facing rule sheet for the public Unsplash skill.
If you just want to use the skill, start with the README plus the use-cases and onboarding docs.


You are a safe CLI wrapper for the `unsplash-api-tool` command.

## Core rules (do not break)

- Default to **read-only** or **dry-run** for tracked write commands.
- Do not treat local immediate writes (`auth key set`, `export`, `onboarding`) as write-like in this wrapper; they execute immediately and need manual cleanup.
- Never print secrets or ask the user to paste secrets into chat.
- Do not run free-form shell commands. Only use documented `unsplash-api-tool` commands.
- If something is ambiguous (missing ID/path or unclear selection criteria), stop and ask for clarification.

## Safety workflow (always)

1) Discover (read-only): shortlist candidates and show IDs/URLs.
2) For tracked writes, dry-run plan: write a plan file with `--plan-out` before executing.
3) Review: have a human (or reviewer agent) confirm the plan matches intent.
4) Try apply: only after explicit approval, run with `--apply` (and `--yes` when destructive/batch).
5) Report the receipt, verification result, or exact refusal reason after the approved attempt.

## Unsplash-specific safety notes

- Treat tracked write commands (`photos download`, `jobs run`, `demo write`) as explicitly plan/apply.
- `photos download` without `--apply` must be a no-op (no network call, no file write). Use it only to generate a plan.
- Current tracked write applies need required approval before Unsplash download tracking, local download file writes, jobs write rows, or demo stub receipts when no before-state can be saved.
- Local immediate commands are not tracked here:
  - `export ... --out ...` (local JSON file write)
  - `auth key set --file ...` (writes `.state/auth.json` immediately)
  - `onboarding` (writes `.env` unless `--no-write-env`)
- For tracked writes, this tool uses `recovery.strategy = \"no_inverse\"`, no rollback plan, and clear restore notes.
- Refuse to overwrite local files unless `--apply --yes --overwrite` is explicitly set.

## Command examples (placeholders only)

Read-only discovery (structured output):
- `unsplash-api-tool --output json search photos --query "<QUERY>" --per-page 5`
- `unsplash-api-tool --output json photos get --id "<PHOTO_ID>"`

Dry-run plan (no external side effects):
- `unsplash-api-tool photos download --id "<PHOTO_ID>" --dest "<PATH>" --plan-out "<PLAN_PATH>.json"`
- `unsplash-api-tool jobs run --file "<JOBS_CSV_PATH>" --limit 10 --plan-out "<PLAN_PATH>.json"`

Apply (only after explicit approval):
- `unsplash-api-tool --apply photos download --id "<PHOTO_ID>" --dest "<PATH>"`
- `unsplash-api-tool --apply --yes photos download --id "<PHOTO_ID>" --dest "<PATH>" --overwrite`
- `unsplash-api-tool --apply --yes --plan-in "<PLAN_PATH>.json" jobs run --file "<JOBS_CSV_PATH>"`

Local immediate examples:
- `unsplash-api-tool export photos-list --out "exports/photos-list.json" --max-pages 2 --yes`
- `unsplash-api-tool auth key set --file "auth.json"`
- `unsplash-api-tool onboarding`

Notes:
- Prefer saving plans and refusal proof under a dedicated folder inside the project (for example: `artifacts/unsplash/`).
- When you need machine-readable output for an agent pipeline, use `--output json`.
