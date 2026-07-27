# Proof and verification

Last verified: **2026-07-27**

This source was verified without an Asana credential and without sending any request to Asana. The checks prove the pinned inventory, local behavior, safety gates, documentation alignment, package contents, and clean installed CLI. They do not prove live account access or provider behavior.

## Pinned boundary proof

- Official input: `Asana/openapi` commit `56796a67a3c093eedf55fd9682357957a2ebfd85`
- Vendored input SHA-256: `cb3b90f4e0af56035eab0c648974f625b942a28a7144aa6c2326e38ca0bb3d56`
- Generated result: 175 paths, 249 operations, 49 tagged families, 248 fixed commands
- Intentional in-spec exclusion: `POST /batch`
- Generation check: `.venv/bin/python scripts/generate_inventory.py --check` passed

`docs/api_coverage.md`, the packaged manifest, and the operation inventory are generated together from that input. Every official operation ID appears once in the ledger.

## Source behavior checks

Python **3.12.13** ran:

```bash
.venv/bin/ruff check .
.venv/bin/mypy src
.venv/bin/python -m unittest -q
```

Results:

- Ruff: passed
- mypy: passed across 19 source files
- unittest: 44 tests passed

The tests cover importability, package identity, JSON stdout, missing-auth secrecy, private onboarding files, boundary counts, unique fixed commands, batch exclusion, OAuth scopes, preview and deprecation status, no generic command bridge, official-host routing, bounded identity output, documented parameters, offset pagination, strict Asana JSON envelopes, App Components field refusal, attachment fields, authenticated saved plans, snapshots, drift refusal, no-snapshot acknowledgement, fixed and request-content stronger approval, provider-failure receipts, readback verification, async job polling, audit redaction, example parsing, wrapper alignment, and coverage alignment.

Direct pre-HTTP refusal cases cover the exact recomputed-plan-ID `/batch` exploit, `/scim/Users`, changed method, operation, command, query, body, file metadata, risk, snapshot, and verification fields, missing or changed integrity, missing or changed signing state, and upload content drift. Real filesystem tests prove default and custom plan and receipt paths, the signing key, and default-style and custom audit paths are owner-only. They also prove new state directories use `0700`, new private files use `0600`, and atomic replacement preserves a stricter existing `0400` mode.

The same complete wrapper contract check passed the source layout at `skills/asana/SKILL.md` and a copied public-style layout with top-level `SKILL.md`. A layout with neither file failed as intended. The complete 44-test suite also passed from a real public-style copy containing only top-level `SKILL.md` and no source `skills/` tree.

HTTP calls in tests use an injected client. No base-URL environment override or live test transport is available in the production CLI.

## Package checks

```bash
.venv/bin/python -m build
```

Built successfully:

- `qwayk_asana_safe_agent_cli-0.1.0.tar.gz`
- `qwayk_asana_safe_agent_cli-0.1.0-py3-none-any.whl`

Fresh archives contained 95 source-distribution entries and 26 wheel entries. The wheel contains the packaged manifest and full fixed operation inventory. The source distribution contains the pinned official YAML, generator, docs, examples, tests, and `skills/asana/SKILL.md`; repo instruction files are excluded. Archive inspection also found no `.state`, cache, or bytecode files.

A clean Python 3.12 environment installed the wheel outside the source tree. The installed CLI then proved:

- version command: passed
- packaged manifest: 249 operations
- packaged fixed command list: 248 commands
- `commands show get-workspaces`: passed
- local schema-2 `create-task` plan generation from a fake non-provider token: passed without a network call
- generated plan, signing key, state directory, and receipt used the expected private modes and the plan contained no token value
- normal apply used an injected no-network transport and sent only `POST /tasks`
- an edited plan redirected to `/batch` with a recomputed public plan ID was refused before the injected transport saw HTTP

## Write-safety proof

Mocked behavior proves that:

- a write without `--apply` saves a plan and sends no provider write
- apply requires the saved plan, exact content-derived approval ID, and valid local HMAC-SHA256 integrity
- apply refuses repeated parameters, bodies, or files
- authenticated integrity is checked before snapshot or provider calls
- apply reconstructs the fixed path and typed query from preserved validated inputs and revalidates operation, command, method, body, secret rules, file metadata/hash, risk, snapshot identity, verification, and rollback
- a changed plan, changed signing key, changed upload, or changed same-target snapshot is refused before write
- no-snapshot and stronger-risk plans require separate acknowledgements
- writes are not retried automatically
- PUT readback compares requested fields and DELETE readback checks absence when a same-target GET exists
- failed provider attempts still save a failed receipt
- async job creation is not called complete until the fixed job read returns `succeeded`
- attachment apply verifies the planned file hash

The committed plan and receipt examples use fake GIDs and are illustrative. The example plan uses the schema-2 field shape but has a deliberately invalid example signature and is not applyable.

## What remains live-unverified

No live evidence exists yet for:

- personal access token, OAuth access token, or service-account permissions
- OAuth scope enforcement, feature plans, admin roles, or gated operations
- live reads, writes, uploads, downloads, webhooks, events, exports, audit logs, rules, agents, AI Studio usage, budgets, rates, or approvals
- provider rate limits, job timing, webhook handshake timing, response shapes, request IDs, or read-after-write consistency
- Asana-side side effects, notifications, fan-out, or restore possibilities

Those limits are allowed for this source build and remain visible in the coverage ledger and public docs. A future live test needs an explicit credential and provider-call authorization; it must begin with reads and use the same plan and approval gates for writes.
