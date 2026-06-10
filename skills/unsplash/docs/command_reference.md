# Command reference

Use this page when you need the exact Unsplash command, flag, or safety rule.
If you want the plain-English path first, start with [What you can do](use_cases.md), [Connect your account](onboarding.md), and [Quickstart](quickstart.md).

## Onboarding and local state writes

- `unsplash-api-tool onboarding [--no-write-env]`
- `unsplash-api-tool auth key set --file auth.json`

## Auth

- `unsplash-api-tool --output json --version`
- `unsplash-api-tool auth check`
- `unsplash-api-tool auth key status`

## Tracked write flows (plan/apply; irreversible in this CLI)

These commands are write-capable and do not apply changes unless:
- `--apply` is passed (and `--yes` for risky actions)
- you accept the plan flow output from a dry-run plan.

Tracked write flows do not offer automatic restore/rollback. Approved apply requires explicit no-snapshot approval and must emit a receipt that records the recovery limit.

## Photos

- `unsplash-api-tool photos list [--page N] [--per-page N] [--order-by latest|oldest|popular]`
- `unsplash-api-tool photos get --id <photo_id>`
- `unsplash-api-tool photos random [--count 1..30] [--query ...] [--username ...] [--orientation ...] [--content-filter low|high]`
- `unsplash-api-tool photos search --query <q> [--page N] [--per-page N] [--order-by relevant|latest]`
- `unsplash-api-tool photos stats --id <photo_id> [--resolution ...] [--quantity ...]`
- `unsplash-api-tool photos download --id <photo_id> [--dest path] [--plan-out plan.json]`
- `unsplash-api-tool --apply photos download --id <photo_id> [--dest path]`
- `unsplash-api-tool --apply --yes photos download --id <photo_id> --dest path --overwrite`

Current `photos download --apply` requires explicit no-snapshot approval before `GET /photos/:id/download` and before optional local file writes when no saved snapshot is available.

## Collections

- `unsplash-api-tool collections list [--page N] [--per-page N]`
- `unsplash-api-tool collections get --id <collection_id>`
- `unsplash-api-tool collections photos --id <collection_id> [--page N] [--per-page N] [--orientation ...]`
- `unsplash-api-tool collections related --id <collection_id>`

## Topics

- `unsplash-api-tool topics list [--page N] [--per-page N] [--order-by featured|latest|oldest|position]`
- `unsplash-api-tool topics get --id <topic_slug_or_id>`
- `unsplash-api-tool topics photos --id <topic_slug_or_id> [--page N] [--per-page N] [--orientation ...]`

## Users

- `unsplash-api-tool users get --username <username>`
- `unsplash-api-tool users photos --username <username> [--page N] [--per-page N] [--order-by ...] [--orientation ...]`
- `unsplash-api-tool users likes --username <username> [--page N] [--per-page N] [--order-by ...] [--orientation ...]`
- `unsplash-api-tool users collections --username <username> [--page N] [--per-page N]`
- `unsplash-api-tool users statistics --username <username> [--resolution ...] [--quantity ...]`

## Search

- `unsplash-api-tool search photos --query <q> [--page N] [--per-page N]`
- `unsplash-api-tool search collections --query <q> [--page N] [--per-page N]`
- `unsplash-api-tool search users --query <q> [--page N] [--per-page N]`

## Stats (global)

- `unsplash-api-tool stats total`
- `unsplash-api-tool stats month`

## Export (deterministic pagination → local JSON file)

Notes:
- `--per-page` is capped at 30 (per official Unsplash docs pagination maximum).
- Multi-page exports require `--yes` when `--max-pages > 1`.

Common flags:
- `--out <path>` (required)
- `--start-page N` (default 1)
- `--max-pages N` (default 1)
- `--per-page N` (default 10; max 30)
- `--sleep-ms N` (default 0)

- `unsplash-api-tool export photos-search --query <q> [--order-by relevant|latest] --out export.json [--start-page N] [--max-pages N] [--per-page N] [--sleep-ms N]`
- `unsplash-api-tool export photos-list [--order-by latest|oldest|popular] --out export.json [--start-page N] [--max-pages N] [--per-page N] [--sleep-ms N]`
- `unsplash-api-tool export collections-photos --id <collection_id> [--orientation ...] --out export.json [--start-page N] [--max-pages N] [--per-page N] [--sleep-ms N]`
- `unsplash-api-tool export topics-photos --id <topic_slug_or_id> [--orientation ...] --out export.json [--start-page N] [--max-pages N] [--per-page N] [--sleep-ms N]`
- `unsplash-api-tool export users-photos --username <username> [--order-by ...] [--orientation ...] --out export.json [--start-page N] [--max-pages N] [--per-page N] [--sleep-ms N]`

## Jobs

- `unsplash-api-tool jobs run --file jobs.csv [--limit N] [--plan-out plan.json]`
- `unsplash-api-tool --apply --yes --plan-in plan.json jobs run --file jobs.csv`

Current jobs with write rows require explicit no-snapshot approval before per-row write actions or stub receipts.

## Local immediate writes (manual cleanup only)

These commands write local files/state without a tracked plan/apply flow. No automatic rollback is possible.

- `unsplash-api-tool export photos-search --query <q> [--order-by relevant|latest] --out export.json [--start-page N] [--max-pages N] [--per-page N] [--sleep-ms N]`
- `unsplash-api-tool export photos-list [--order-by latest|oldest|popular] --out export.json [--start-page N] [--max-pages N] [--per-page N] [--sleep-ms N]`
- `unsplash-api-tool export collections-photos --id <collection_id> [--orientation ...] --out export.json [--start-page N] [--max-pages N] [--per-page N] [--sleep-ms N]`
- `unsplash-api-tool export topics-photos --id <topic_slug_or_id> [--orientation ...] --out export.json [--start-page N] [--max-pages N] [--per-page N] [--sleep-ms N]`
- `unsplash-api-tool export users-photos --username <username> [--order-by ...] [--orientation ...] --out export.json [--start-page N] [--max-pages N] [--per-page N] [--sleep-ms N]`

## Runs (history)

Write-capable commands automatically save proof artifacts under `.state/runs/` and append an index row to `.state/runs/index.jsonl`.

These live next to your `--env-file` (usually next to your `.env` file), so they’re easy to find.

Optional flags:
- `--run-id <id>`: set a specific run id (otherwise the tool generates one)
- `--artifacts-dir <path>`: override where artifacts are written for this run
- `--no-artifacts`: disable writing run artifacts (advanced)

- `unsplash-api-tool runs list [--limit 20]`
- `unsplash-api-tool runs show --run-id 2026-01-19T104512Z_a3f91c`

## Demo (plan/refusal workflow examples)

- `unsplash-api-tool demo read`
- `unsplash-api-tool demo write --selector demo-resource [--plan-out plan.json]`
- `unsplash-api-tool --apply --plan-in plan.json demo write --selector demo-resource`

Current demo write apply requires explicit no-snapshot approval before stub receipt output.
