# Changelog

All notable changes to this project are documented in this file.

This format is based on Keep a Changelog, and this project follows Semantic Versioning.
Because this tool is pre-1.0 (`0.x`), minor version bumps may include breaking changes.

## [Unreleased]

### Added
- `auth zone-create-check` for a safe bulk-onboarding preflight. It tests zone-create permission with an intentionally invalid payload, so it catches token-scope problems before a real zone-create batch.
- First-class `browser-run` command family for common Cloudflare Browser Rendering quick actions: `markdown`, `links`, `scrape`, `screenshot`, `crawl`, and `crawl-result`. The wrapper keeps the existing file-only account-write safety gates but removes raw `operations` names and manual body JSON files for common probes.
- Live official Cloudflare API inventory generator: `scripts/generate_live_official_api_inventory.py`, plus committed outputs `docs/_generated/live_official_api_inventory.json`, `docs/api_coverage_live_official.md`, and `docs/live_api_drift_2026-04-27.md`.
- First-class Cloudflare Observatory read helpers: `observability speed availabilities`, `observability speed pages list`, `observability speed page latest`, `observability speed page trend`, and `observability speed page history`, with normal-URL input and built-in summaries.
- `observability web-analytics status` to bundle zone RUM state, matching Web Analytics site state, and ruleset lookup status in one read-only command.
- `observability audit` to combine Web Analytics status, Observatory coverage, homepage/page performance summaries, and Cloudflare log-surface access checks for one zone.
- `auth explain --for ...` for the new observability surfaces so the CLI can state the likely minimum permissions before the user goes back to the Cloudflare dashboard.
- `pages deploy` now keeps dry-runs local, creates a missing Pages project on apply using `name` + `production_branch`, and records that ensure/create step in the receipt. (Issue #408)
- Phase 9 (Pages): offline subset + generated coverage ledger for Pages Projects/Deployments/Domains + build cache; allowlisting for `operations <area> <op_key>`; sensitive file-only output hidden from `operations list` unless `--include-sensitive`; rollback requires `--ack-irreversible` and uses safe read-back verification. (Issue #258)
- Phase 10 (Images): offline subset + generated coverage ledger for Images/Variants/Signing Keys; allowlisting for `operations <area> <op_key>`; blob/direct_upload/keys are sensitive file-only output hidden from `operations list` unless `--include-sensitive`; direct_upload is treated as read-like POST (no `--yes`); signing key creation requires `--ack-irreversible`. (Issue #261)
- Phase 11 (AI Gateway): offline subset + generated coverage ledger for Gateways/Dynamic Routes/Logs/Datasets/Evaluations/Provider Configs; allowlisting for `operations <area> <op_key>`; logs/datasets/evals/provider configs are classified as sensitive file-only output and hidden from `operations list` unless `--include-sensitive`; provider config writes require `--ack-irreversible` and responses are never printed. (Issue #265)
- Phase 12 (Vectorize): offline subset + generated coverage ledger for Vectorize v2 indexes + vector ops (query/get-by-ids/insert/upsert/delete-by-ids) + metadata index ops; allowlisting for `operations <area> <op_key>`; all Vectorize operations are classified as sensitive file-only output hidden from `operations list` unless `--include-sensitive`; query/get-by-ids are treated as read-like POST (no `--yes`). (Issue #267)
- Phase 13 (AutoRAG): offline subset + generated coverage ledger for RAG search (`ai-search`, `search`) + files/jobs inventory + job logs + sync trigger; allowlisting for `operations <area> <op_key>`; all AutoRAG operations are classified as sensitive file-only output hidden from `operations list` unless `--include-sensitive`; `ai-search`/`search` are treated as read-like POST (no `--yes`); `sync` is a state-changing PATCH (requires `--yes`). (Issue #273)
- Phase 14 (Workers AI): offline subset + generated coverage ledger for Workers AI model runs (`/ai/run/...`) + model discovery + finetunes; allowlisting for `operations <area> <op_key>`; all Workers AI operations are classified as sensitive file-only output hidden from `operations list` unless `--include-sensitive`; model runs are treated as read-like POSTs (no `--yes`). (Issue #279)
- Phase 15 (AI Search): offline subset + generated coverage ledger for AI Search instances/items/jobs/logs + search/chat + tokens; allowlisting for `operations <area> <op_key>`; all AI Search operations are classified as sensitive file-only output and hidden from `operations list` unless `--include-sensitive`; search/chat are treated as read-like POSTs (no `--yes`); token create/update requires `--ack-irreversible`. (Issue #289)
- Phase 16 (Email Security): offline subset extracts + generated coverage ledgers for Email Security (Investigate/Submissions/PhishGuard), Email Security Settings, DLP Email, and Radar Email Security/Routing; allowlisting for `operations <area> <op_key>`; all Phase 16 operations are classified as sensitive file-only output hidden from `operations list` unless `--include-sensitive`; refuses apply without `--out`. (Issue #291)
- Phase 17 (Radar HTTP/DNS): offline subset extracts + generated coverage ledgers for Radar HTTP and Radar DNS analytics; allowlisting for `operations <area> <op_key>`; classified as sensitive file-only output due to "User Details" token groups and hidden from `operations list` unless `--include-sensitive`; refuses apply without `--out`. (Issue #293)
- Phase 18 (Radar Attacks Layer 7/Layer 3): offline subset extracts + generated coverage ledgers for Radar attacks analytics; allowlisting for `operations <area> <op_key>`; classified as sensitive file-only output due to "User Details" token groups and hidden from `operations list` unless `--include-sensitive`; refuses apply without `--out`. (Issue #295)
- Phase 19 (Radar BGP): offline subset extracts + generated coverage ledger for Radar BGP analytics; allowlisting for `operations <area> <op_key>`; classified as sensitive file-only output due to "User Details" token groups and hidden from `operations list` unless `--include-sensitive`; refuses apply without `--out`. (Issue #297)
- Phase 20 (Radar NetFlows): offline subset extracts + generated coverage ledger for Radar NetFlows analytics; allowlisting for `operations <area> <op_key>`; classified as sensitive file-only output due to "User Details" token groups and hidden from `operations list` unless `--include-sensitive`; refuses apply without `--out`. (Issue #299)
- Phase 21 (Radar complete): offline subset extract + generated coverage ledger for all `/radar/*` operations; allowlisting for `operations <area> <op_key>`; all Radar operations are classified as sensitive file-only output hidden from `operations list` unless `--include-sensitive`; dataset download (`POST /radar/datasets/download`) is gated as a download-like write requiring `--apply --yes --out`. (Issue #301)
- Phase 22 (Accounts GET): offline subset extract + generated coverage ledger for all `GET /accounts/*` operations; allowlisting for `operations <area> <op_key>`; newly allowlisted operations are classified as sensitive file-only output and hidden from `operations list` unless `--include-sensitive`; unit tests lock the exact allowlist to the extract. (Issue #303)
- Phase 23 (Accounts writes): offline subset extract + generated delta coverage ledger for remaining `/accounts*` write operations (POST/PUT/PATCH/DELETE); allowlisting for `operations <area> <op_key>`; applied `/accounts*` writes require `--apply --yes --out` (file-only output; never printed); `DELETE /accounts*` additionally requires `--ack-irreversible`; receipts use redacted verification (no embedded response bodies); unit tests lock the exact allowlist to the extract and enforce the safety gates. (Issue #309)
- Phase 24 (Zones GET): offline subset extract + generated coverage ledger for all `GET /zones/*` operations; allowlisting for `operations <area> <op_key>`; newly allowlisted operations are classified as sensitive file-only output and hidden from `operations list` unless `--include-sensitive`; unit tests lock the exact allowlist to the extract. (Issue #305)
- Phase 25 (Zones writes): offline subset extract + generated delta coverage ledger for remaining `/zones*` write operations (POST/PUT/PATCH/DELETE); allowlisting for `operations <area> <op_key>`; writes remain gated behind `--apply --yes`; unit tests lock completeness to the in-repo snapshot extract (no live Cloudflare credentials used). (Issue #307)
- Phase 27 (Top-level User/Org/System): offline subset extracts + generated coverage ledgers for remaining top-level endpoints (for example `/user/*`, `/organizations/*`, `/memberships/*`, `/tenants/*`, `/system/*`, `/certificates`, `/telemetry/*`, and `/accounts`/`/zones` list endpoints); allowlisting for `operations <area> <op_key>`; conservative sensitivity (file-only output; hidden from `operations list` unless `--include-sensitive`); destructive operations require `--ack-irreversible`. (No live Cloudflare credentials used.)

### Changed
- `runs list` and `runs show` now filter to Cloudflare tool rows only, even when the local run index contains mixed tools.
- Cloudflare Pages proof/docs/front doors now reflect the first-class direct-upload deploy flow and `0.7.6`.
- Breaking: removed the generic `openapi` CLI command family and introduced explicit per-operation `operations <area> <op_key>` commands for full allowlisted coverage; docs/examples/tests updated and drift guards added. (Issue #375)
- Phase 26 (Docs alignment): refreshed the vendored Cloudflare OpenAPI snapshot (and regenerated extracts + coverage ledgers) to stay aligned with the official upstream schema. (Last verified UTC: 2026-02-18)
- Pages deploy: switched the first-class `pages deploy` wrapper from a mocked zip upload shape to Cloudflare's real direct-upload asset flow (upload token, missing-hash check, asset upload, hash upsert, manifest deployment), added `--branch` for preview deployments, and added read-back verification of the created deployment. (Issue #408)

### Fixed
- Cloudflare auth-scheme failures such as `Method not allowed for this authentication scheme` now include a clearer plain-English hint instead of only the raw vendor message.
- `observability web-analytics status` now also matches Cloudflare site entries that identify the zone only inside nested `ruleset.zone_name` / `ruleset.zone_tag`, which showed up in the live PB Services account.
- Workers: `workers tails stream` now requests the expected WebSocket subprotocol and disables compression to avoid handshake errors (for example HTTP 406); errors include a safe exception summary.
- Workers: `workers logs search|keys|values` now call the account-scoped Workers Observability Telemetry endpoints (Cloudflare no longer serves `/telemetry/*` as top-level routes).
- Phase 26 (Docs alignment): handle Cloudflare D1 operationId renames (`d1-export-database`, `d1-import-database`) while keeping backward compatibility for older snapshot ids; tests updated accordingly.

## [0.7.6] - 2026-02-12

### Added
- UX/perf hardening for slow endpoints: split timeouts (`CLOUDFLARE_CONNECT_TIMEOUT_S`, `CLOUDFLARE_READ_TIMEOUT_S`), `--timeout-profile slow`, and `--progress` heartbeats to stderr. (No change to stdout JSON contract.)
- Short-TTL cache for explicitly allowlisted safe GET inventory reads (opt-in per endpoint; stored under `.state/cache/`).
- `auth doctor`: read-only latency/permissions doctor for common endpoints (optional parallelism via `--parallel`).
- Local-only config helpers: `config init` (seed `.env` from `.env.example`) and `config check` (validate env basics; no API calls).
- Convenience read helpers:
  - `tunnels list|resolve|config get`
  - `zero-trust access apps resolve`

### Changed
- The active `operations <area> <op_key>` allowlist now comes from the committed live official Cloudflare API inventory instead of the historical vendored snapshot ledgers, which removed 441 stale local-only operations, fixed 6 path drifts, and added 112 live official operations.
- Local default account id storage can key by a non-secret env fingerprint (base URL + token fingerprint) to reduce friction when env paths move.

## [0.7.5] - 2026-02-11

### Added
- Phase 8A (Workflows): offline Workflows subset + coverage ledger, allowlisting for `operations <area> <op_key>`, and sensitivity gating for workflow instance detail/logs (file-only output; refuses apply without `--out`). (Issue #252)
- Waiting Room (Phase 8B): offline subset/ledger for zone + account Waiting Room endpoints. (Issue #253)

### Changed
- operations command surface: classify Waiting Room preview POST as read-like non-GET (apply does not require `--yes`; receipts report `changed=false`). (Issue #253)

## [0.7.4] - 2026-02-11

### Added
- Workers: `workers logs search|keys|values` to query stored Workers logs/events via the Workers Observability Telemetry API with strict file-only output. `search` supports first-class lookup by Error ID / request id (x-request-id) and safe key auto-discovery (refuses when ambiguous). (Issue #246)

## [0.7.3] - 2026-02-10

### Added
- Account access (Phase 7F): `accounts roles` (list/get) and `accounts members` (list/get/add/update/remove) with strict PII-safe defaults (member emails never printed; member reads are file-only).

### Changed
- Privacy: redact `--email` values from command strings written to stdout plans/receipts, audit logs, and run history.

## [0.7.2] - 2026-02-10

### Added
- Workers: `workers observability status|enable|disable` wrapper commands for toggling per-script observability via Workers script-settings PATCH, with plan/apply gates and read-back verification.
- Workers: `workers tails stream` to safely stream tail logs to a local file (never prints event contents or the secret-bearing WebSocket URL).

### Fixed
- OpenAPI allowlist: classify Workers Start Tail as `sensitive_write_result` so `operations <area> <op_key>` requires `--out` + `--ack-irreversible` and cannot print the WS URL/token.

## [0.7.1] - 2026-02-10

### Added
- Email Routing (Phase 7E-6): offline subset/ledger, sensitivity override (file-only output), and named `email-routing` command family (addresses/settings/dns/rules) with strict plan/apply gating and PII-safe defaults.

## [0.7.0] - 2026-02-10

### Added
- Turnstile widgets (Phase 7E-5): offline subset/ledger, sensitivity override, and named `turnstile widgets` command family (list/get/create/update/delete/rotate-secret) with strict file-only output for sensitive responses.
- Safety gating for Turnstile secret-bearing operations (create + rotate-secret): `--apply --yes --ack-irreversible` plus mandatory `--out` file output.

## [0.6.0] - 2026-02-09

### Added
- Registrar Domains (Phase 7E-4): PII-safe file-only `registrar domains` command family (list/get/update), offline subset/ledger, and sensitivity override to prevent printing response bodies.
- `auth probe`: a read-only capability probe that quickly identifies missing token permissions (no writes; no sensitive reads).

## [0.5.0] - 2026-02-09

### Added
- Zone settings (Phase 7E-3): zone settings list/patch plus allowlisted single-setting get/patch with plan/apply/verify and read-back verification.
- Rulesets entrypoints (Phase 7E-3): `waf rulesets entrypoint-update` (zone/account) wrapper with plan/apply/verify and read-back verification.
- Offline zone settings subset + generated coverage ledger + generated setting-path allowlist derived from the in-repo Cloudflare OpenAPI snapshot.

## [0.4.0] - 2026-02-09

### Added
- Cloudflare API client with envelope parsing, safe retries, and secret redaction.
- Read-only commands: onboarding, auth check, accounts list/set-default, zones list/resolve.
- Workers platform read-only inventory commands (scripts/routes/subdomain/domains/dispatch/KV metadata/versions/deployments/tails).
- Expanded Workers platform read-only coverage: account settings, placement regions, Workers for Platforms inventory, service environment settings, script extras (schedules/script-settings/usage-model/subdomain/secrets), dispatch extras (bindings/tags/secrets), builds, and pipelines (v1 + legacy/deprecated GETs).
- Workers write workflows (plan/apply/verify/receipt): routes ensure/ensure-absent, subdomain ensure/ensure-absent, domains attach/detach.
- Sensitive reads (apply-gated; file output only): Workers script download/content and KV values get (never prints content/values).
- Zero Trust read-only inventory commands (org/gateway rules+lists+config/logging/devices/access apps+policies) + generated coverage ledger.
- Advanced operations command surface: call any Workers platform + Zero Trust endpoint from the in-repo snapshot extracts (plan/apply/verify/receipt; sensitive outputs to file only).
- Jobs runner (CSV): batch allowlisted operation calls with the same safety gates; stops on first error.
- Workers for Platforms walkthrough doc + proof examples for dispatch namespace planning and assets upload session safety refusals.
- DNS (Phase 7A): named DNS commands for records, export/import, DNS scan, settings/views, DNSSEC, and Secondary DNS (ACL/Peer/TSIG + zone transfers), with safe-by-default plan/apply gates and TSIG/export file-only handling.
- Cloudflare offline OpenAPI subsets + ledgers for storage & databases: D1, Hyperdrive, Queues, R2, R2 Catalog, Secrets Store, Pipelines.
- Observability (Phase 7D): new `observability` command family (Logpush, zone logs, audit logs, request tracer, and RUM/Web Analytics) + offline subset/ledger; audit logs and request tracer outputs are file-only and never printed.
- New command families:
  - `d1`: databases list/get + export/query (export/pull/file-only; query requires `--yes`)
  - `queues`: list/get + pull (file-only)
  - `r2`: buckets list/get + temp credentials create (secret-bearing; file-only)
  - `waf`: Rulesets/WAF inventory commands (rulesets/firewall access rules/rate limits/snippets/page rules/managed transforms), plus snippet content (sensitive file-only) and managed transforms update (plan-first; apply requires `--apply --yes`)
- Phase 7B allowlist expansion: new generated coverage ledgers for Rulesets/WAF subsets (Rulesets, Firewall, Filters, Managed transforms, Rate limits, Snippets, Page rules).
- Phase 7E-1 (TLS/SSL + Custom Hostnames + cache purge): new offline subset extracts + generated ledgers, sensitivity classification (`sensitive_read`), and named command families:
  - `custom-hostnames` (SSL for SaaS)
  - `ssl-tls` (certificate packs, universal SSL, verification, recommendation, automatic mode, analyze)
  - `cache purge` (zone cache purge; plan-first; apply requires `--apply --yes`)
- Phase 7E-2 (Load Balancing): new offline subset extracts + generated ledger + safety classification and named command family:
  - `load-balancers` (monitors, pools, monitor groups; preview/health/references)

### Changed
- Coverage ledgers: Workers platform and Zero Trust are now fully runnable via `operations <area> <op_key>` (generated docs updated accordingly).
- operations command surface allowlist: auto-discovers `docs/api_coverage_*.md` ledgers and now includes DNS + storage/database ledgers.
- Safety: sensitive non-GET operations are file-only; certain read-like POST operations require `--apply` + `--out` but not `--yes` (receipts report `changed=false`).

### Fixed
- Ensure argument/usage errors in `--output json` mode emit exactly one JSON error object (no argparse usage text).

### Removed
