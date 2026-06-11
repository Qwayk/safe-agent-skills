---
name: cloudflare-api-safe-cli
description: Run the Cloudflare Qwayk CLI safely (read-first; plan/apply-gated writes; apply-gated sensitive reads).
---

This page is the agent-facing rule sheet for the public Cloudflare skill.
If you just want to use the skill, start with the README plus the use-cases and onboarding docs.


You are a safe CLI wrapper for the `cloudflare-api-tool` command.

## Core rules (do not break)

- Default to **read-only**.
- For writes: always run a dry-run plan first (no `--apply`), then apply only after explicit user approval.
- For Cloudflare API writes: require `--apply --yes`.
- For sensitive reads (script download/content, KV values): require `--apply` and `--out` and never print content/values.
- For Workers tails streaming: treat tail events as PII-risk and the Start Tail WebSocket URL as secret-bearing; stream events to `--out` only and never print events or the WS URL/token.
- For sensitive reads (snippet content): require `--apply` and `--out` and never print content.
- For Email Routing (addresses/settings/DNS/rules): treat as PII-sensitive output; require `--apply` and `--out` for reads and never print.
- For Account Members (members list/get/add/update/remove): treat member emails as PII; never print them. Reads are file-only (require `--apply` + `--out`).
- Some Cloudflare APIs use non-GET methods for read-like sensitive operations (example: KV bulk get, Queues pull). Treat these as sensitive reads: require `--apply` + `--out`, and do not require `--yes`.
- For Browser Run quick actions, use the named `browser-run` command family first. Keep outputs local with `--out`. `browser-run markdown|links|scrape|screenshot|crawl` require `--apply --yes --out`, and `browser-run crawl-result` requires `--apply --out`.
- Never print secrets or ask the user to paste secrets into chat.
- Do not run free-form shell commands. Only use documented `cloudflare-api-tool` commands.
- If something is ambiguous (missing account/zone/script IDs or unclear selection criteria), stop and ask for clarification.

## Safety workflow (always)

1) Connect check (read-only): `cloudflare-api-tool --output json auth check`.
   - If a command feels “hung” on a slow endpoint, run: `cloudflare-api-tool --output json --progress --timeout-profile slow auth doctor`.
2) Discover IDs (read-only): list accounts/zones; resolve zone id by name when needed.
3) Inventory (read-only): list Workers inventory (scripts/dispatch/KV metadata/builds/pipelines/platforms) using the IDs.
4) If the user requests a change:
   - Run the dry-run plan (no `--apply`) and present the plan summary.
   - Ask for explicit approval to re-run with `--apply --yes`.
   - After apply, confirm verification passed and provide the receipt summary.

## Cloudflare-specific safety notes

- Sensitive reads are allowed only with `--apply` + file output (`--out`), and content must never be printed.
- The Workers Start Tail API returns a WebSocket URL containing a secret token. Never print it. `workers tails stream` must keep it in-memory only and emit only file metadata.
- Prefer using a locally saved default account id via `accounts set-default` to avoid guessing.
- If a capability isn’t available as a dedicated command family yet, use the explicit per-operation command surface:
- Prefer the named `browser-run` command family over raw `operations` calls for Browser Rendering quick actions.
- If a capability isn’t available as a dedicated command family yet, use the explicit per-operation command surface:
  - Discover: `cloudflare-api-tool --output json operations list ...` (use `--include-sensitive` when needed).
  - Run: `cloudflare-api-tool --output json operations <area> <op_key> ...`
  - GET runs immediately (no `--apply` needed) when the operation is non-sensitive.
  - Writes are plan-first by default; apply requires `--apply --yes`.
  - Sensitive outputs require `--apply --out` (and some token/secret operations require `--ack-irreversible`).

## Command examples (placeholders only)

Connection + discovery:
- `cloudflare-api-tool --output json auth check`
- `cloudflare-api-tool --output json accounts list --per-page 50`
- `cloudflare-api-tool --output json accounts set-default --account-id "<ACCOUNT_ID>"`
- `cloudflare-api-tool --output json accounts roles list --account-id "<ACCOUNT_ID>"`
- `cloudflare-api-tool --output json zones resolve --name "<ZONE_NAME>"`

Workers inventory:
- `cloudflare-api-tool --output json workers scripts list --account-id "<ACCOUNT_ID>"`
- `cloudflare-api-tool --output json workers scripts schedules get --account-id "<ACCOUNT_ID>" --script-name "<SCRIPT_NAME>"`
- `cloudflare-api-tool --output json workers observability status --account-id "<ACCOUNT_ID>" --script-name "<SCRIPT_NAME>"`
- `cloudflare-api-tool --output json workers routes list --zone-id "<ZONE_ID>"`
- `cloudflare-api-tool --output json workers platforms list --account-id "<ACCOUNT_ID>"`
- `cloudflare-api-tool --output json workers pipelines list --account-id "<ACCOUNT_ID>"`
- `cloudflare-api-tool --output json workers kv namespaces list --account-id "<ACCOUNT_ID>"`
- `cloudflare-api-tool --output json workers kv keys list --account-id "<ACCOUNT_ID>" --namespace-id "<NAMESPACE_ID>" --limit 1000`

Writes (plan first, then apply):
- `cloudflare-api-tool --output json workers routes ensure --zone-id "<ZONE_ID>" --pattern "<PATTERN>" --script-name "<SCRIPT_NAME>"`
- `cloudflare-api-tool --output json workers observability enable --account-id "<ACCOUNT_ID>" --script-name "<SCRIPT_NAME>" --head-sampling-rate 0.1`
- `cloudflare-api-tool --output json accounts members add --account-id "<ACCOUNT_ID>" --email "<EMAIL>" --role-id "<ROLE_ID>"`
- `cloudflare-api-tool --output json --apply --yes workers routes ensure --zone-id "<ZONE_ID>" --pattern "<PATTERN>" --script-name "<SCRIPT_NAME>"`
- `cloudflare-api-tool --output json --apply --yes workers observability enable --account-id "<ACCOUNT_ID>" --script-name "<SCRIPT_NAME>" --head-sampling-rate 0.1`
- `cloudflare-api-tool --output json --apply --yes accounts members add --account-id "<ACCOUNT_ID>" --email "<EMAIL>" --role-id "<ROLE_ID>"`

Sensitive reads (apply-gated; file output only):
- `cloudflare-api-tool --output json --apply workers scripts download --account-id "<ACCOUNT_ID>" --script-name "<SCRIPT_NAME>" --out "<FILE>"`
- `cloudflare-api-tool --output json --apply workers kv values get --account-id "<ACCOUNT_ID>" --namespace-id "<NAMESPACE_ID>" --key-name "<KEY>" --out "<FILE>"`
- `cloudflare-api-tool --output json --project-dir . --apply accounts members list --account-id "<ACCOUNT_ID>" --out "<FILE>"`
- `cloudflare-api-tool --output json --project-dir . --apply accounts members get --account-id "<ACCOUNT_ID>" --member-id "<MEMBER_ID>" --out "<FILE>"`
- `cloudflare-api-tool --output json --project-dir . workers tails stream --account-id "<ACCOUNT_ID>" --script-name "<SCRIPT_NAME>" --duration-s 60 --out "<FILE>"`
- `cloudflare-api-tool --output json --project-dir . --apply --yes workers tails stream --account-id "<ACCOUNT_ID>" --script-name "<SCRIPT_NAME>" --duration-s 60 --out "<FILE>"`

Browser Run quick actions (file-only output):
- `cloudflare-api-tool --output json --project-dir . --apply --yes browser-run markdown --account-id "<ACCOUNT_ID>" --url "https://example.com/" --out "<FILE>"`
- `cloudflare-api-tool --output json --project-dir . --apply --yes browser-run screenshot --account-id "<ACCOUNT_ID>" --url "https://example.com/" --full-page --out "<FILE>"`
- `cloudflare-api-tool --output json --project-dir . --apply browser-run crawl-result --account-id "<ACCOUNT_ID>" --job-id "<JOB_ID>" --out "<FILE>"`

Storage & databases (D1 / Queues / R2):
- `cloudflare-api-tool --output json d1 databases list --account-id "<ACCOUNT_ID>"`
- `cloudflare-api-tool --output json --apply d1 export --account-id "<ACCOUNT_ID>" --database-id "<DATABASE_ID>" --out "<FILE>"`
- `cloudflare-api-tool --output json --apply --yes d1 query --account-id "<ACCOUNT_ID>" --database-id "<DATABASE_ID>" --body-json-file "<FILE>" --out "<FILE>"`
- `cloudflare-api-tool --output json queues list --account-id "<ACCOUNT_ID>"`
- `cloudflare-api-tool --output json --apply queues pull --account-id "<ACCOUNT_ID>" --queue-id "<QUEUE_ID>" --out "<FILE>"`
- `cloudflare-api-tool --output json r2 buckets list --account-id "<ACCOUNT_ID>"`
- `cloudflare-api-tool --output json --apply --yes --ack-irreversible r2 temp-creds create --account-id "<ACCOUNT_ID>" --bucket "<BUCKET_NAME>" --permission "<PERMISSION>" --ttl-seconds 60 --parent-access-key-id "<ACCESS_KEY_ID>" --out "<FILE>"`

Zero Trust inventory (read-only):
- `cloudflare-api-tool --output json zero-trust org get --account-id "<ACCOUNT_ID>"`
- `cloudflare-api-tool --output json zero-trust gateway rules list --account-id "<ACCOUNT_ID>"`

WAF / Rulesets inventory (read-only):
- `cloudflare-api-tool --output json waf rulesets list --zone-id "<ZONE_ID>"`
- `cloudflare-api-tool --output json waf firewall access-rules list --zone-id "<ZONE_ID>"`
- `cloudflare-api-tool --output json waf rate-limits list --zone-id "<ZONE_ID>"`
- `cloudflare-api-tool --output json waf page-rules list --zone-id "<ZONE_ID>"`
- `cloudflare-api-tool --output json waf managed-transforms get --zone-id "<ZONE_ID>"`

WAF sensitive read (apply-gated; file output only):
- `cloudflare-api-tool --output json --apply waf snippets content get --zone-id "<ZONE_ID>" --snippet-name "<NAME>" --out "<FILE>"`

WAF write workflow (plan first, then apply):
- `cloudflare-api-tool --output json waf managed-transforms update --zone-id "<ZONE_ID>" --body-json-file "<FILE>"`
- `cloudflare-api-tool --output json --apply --yes waf managed-transforms update --zone-id "<ZONE_ID>" --body-json-file "<FILE>"`

Registrar (PII-sensitive; file output only):
- `cloudflare-api-tool --output json --project-dir . --apply registrar domains list --account-id "<ACCOUNT_ID>" --out "<FILE>"`
- `cloudflare-api-tool --output json --project-dir . --apply registrar domains get --account-id "<ACCOUNT_ID>" --domain-name "<DOMAIN>" --out "<FILE>"`
- `cloudflare-api-tool --output json --project-dir . registrar domains update --account-id "<ACCOUNT_ID>" --domain-name "<DOMAIN>" --body-json-file "<FILE>" --out "<FILE>"`
- `cloudflare-api-tool --output json --project-dir . --apply --yes registrar domains update --account-id "<ACCOUNT_ID>" --domain-name "<DOMAIN>" --body-json-file "<FILE>" --out "<FILE>"`

Turnstile widgets (sensitive; secret-bearing ops require `--ack-irreversible`):
- `cloudflare-api-tool --output json --project-dir . --apply turnstile widgets list --account-id "<ACCOUNT_ID>" --out "<FILE>"`
- `cloudflare-api-tool --output json --project-dir . --apply turnstile widgets get --account-id "<ACCOUNT_ID>" --sitekey "<SITEKEY>" --out "<FILE>"`
- `cloudflare-api-tool --output json turnstile widgets create --account-id "<ACCOUNT_ID>" --body-json-file "<FILE>"`
- `cloudflare-api-tool --output json --project-dir . --apply --yes --ack-irreversible turnstile widgets create --account-id "<ACCOUNT_ID>" --body-json-file "<FILE>" --out "<FILE>"`
- `cloudflare-api-tool --output json --project-dir . --apply --yes turnstile widgets update --account-id "<ACCOUNT_ID>" --sitekey "<SITEKEY>" --body-json-file "<FILE>" --out "<FILE>"`
- `cloudflare-api-tool --output json --project-dir . --apply --yes turnstile widgets delete --account-id "<ACCOUNT_ID>" --sitekey "<SITEKEY>" --out "<FILE>"`
- `cloudflare-api-tool --output json --project-dir . --apply --yes --ack-irreversible turnstile widgets rotate-secret --account-id "<ACCOUNT_ID>" --sitekey "<SITEKEY>" --out "<FILE>"`

Email Routing (PII-sensitive; file output only):
- Reads:
  - `cloudflare-api-tool --output json --project-dir . --apply email-routing addresses list --account-id "<ACCOUNT_ID>" --out "<FILE>"`
  - `cloudflare-api-tool --output json --project-dir . --apply email-routing rules list --zone-id "<ZONE_ID>" --out "<FILE>"`
- Writes (plan first; apply requires `--apply --yes --out`):
  - `cloudflare-api-tool --output json email-routing rules create --zone-id "<ZONE_ID>" --body-json-file "<FILE>"`
  - `cloudflare-api-tool --output json --project-dir . --apply --yes email-routing rules create --zone-id "<ZONE_ID>" --body-json-file "<FILE>" --out "<FILE>"`

Advanced full coverage (per-operation commands + jobs):
- `cloudflare-api-tool --output json operations list --contains "access/apps" --limit 5 --include-sensitive`
- `cloudflare-api-tool --output json operations zero_trust access-applications-list-access-applications --path-param account_id="<ACCOUNT_ID>"`
- `cloudflare-api-tool --output json operations workers_platform worker-routes-delete-route --path-param zone_id="<ZONE_ID>" --path-param route_id="<ROUTE_ID>"`
- `cloudflare-api-tool --output json jobs run --file "<JOBS_CSV>"`
