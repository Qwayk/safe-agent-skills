# Progress (Dynadot tool)

Goal: make it safe and easy to move **hundreds to thousands of domains** using Dynadot’s API — with a strict safety loop:
preview -> approve -> apply attempt -> explicit no-snapshot approval.

Last updated (UTC): **2026-06-04**

Current reset note:
- Write planning is still available.
- Write apply requires explicit no-snapshot approval when command-specific saved snapshot support is unavailable; missing approval refuses before Dynadot HTTP.
- Old receipt and read-back notes below describe earlier behavior and future design targets, not the write apply path.

## Phase 0 — foundation (make the project easy to continue)

Status: **done**

What’s included:
- A working CLI skeleton with safety flags.
- Clear docs (no template leftovers).
- A single progress page (this file).
- A complete “API commands coverage list” so “all capabilities” is measurable.
- A skill wrapper file for agent runtimes.

## Phase 1 — solve the real problem (domain push at scale)

Status: **done**

What Phase 1 ships:
- Push domains to another Dynadot account (bulk, chunked, safe-by-default).
- Auto-unlock domains for push during the push request (default behavior).
- List incoming push requests (receiver side).
- Accept or decline push requests (receiver side).
- Future verification target: re-check push requests and confirm the domains are gone after accept/decline.
- Optional planning resume from a previous receipt (skip domains already completed).

Safety rules for Phase 1:
- Dry-run by default (no changes unless you pass `--apply`).
- Batch/domain-transfer actions require `--apply --yes`.
- Apply requires explicit no-snapshot approval when no saved before-state is available.
- If the tool is unsure, it refuses safely and explains why.

## Phase 2 — “everything the API can do”

Status: **done**

What Phase 2 ships:
- 100% Dynadot API3 command coverage **from official request examples** via `dynadot-api-tool api3 <command>`.
- A complete, tested coverage ledger: `docs/api_coverage.md` stays in sync with `docs/official_commands.txt`.
 
Notes:
- Higher-level workflows and UX-first commands (like `transfer run` and `domains name-servers set`) remain available and are still the recommended entrypoints for common tasks.
- The Dynadot docs page also contains a few menu items that are not backed by full request examples/parameter tables; those are treated as out-of-scope until Dynadot publishes complete docs for them (see `docs/api_coverage.md`).

## Phase 3 — name server audit + bulk set (safe)

Status: **done**

What Phase 3 ships:
- Read-only audit/export of current name servers per domain (`domains name-servers export`).
- Diff current vs desired name servers with a clear preview and an optional diff file (`domains name-servers diff`).
- Bulk set name servers from the diff file (`domains name-servers set`) with:
  - preview-first plan output,
  - apply gating (`--apply --yes` and reviewed `--plan-in`),
  - explicit no-snapshot approval before Dynadot HTTP,
  - pacing/limits for intentional partial runs,
  - optional pacing between verification reads (`--sleep-between-verifications-s`),
  - optional pre-check that desired name servers exist in the account (warn by default; can require/refuse),
  - future read-back verification via `get_ns` after saved snapshot support is available.

## Phase 4 — guided end-to-end transfer run (safe)

Status: **done**

What Phase 4 ships:
- A guided workflow command that runs the full sequence:
  - push domains (sender),
  - accept matching push requests (receiver),
  - confirm domains appear in the receiver account (or report what’s still missing),
  - check/fix name servers (receiver),
  - and output a clear progress summary (done / remaining / failed).
- Planning resume from a previous transfer receipt (skips already done domains).
