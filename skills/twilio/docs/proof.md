# What is proved

The source has local and mocked proof for its command boundary and safety behavior. It does not have live Twilio account proof.

## Current verification — 2026-09-03

The focused inventory suite against the pinned checkout passed **20/20** checks. The complete local suite passed **125 tests with 2 expected skips** when `TWILIO_OAI_SPEC_ROOT` was unset, and passed **125 tests with zero skips** when `TWILIO_OAI_SPEC_ROOT` pointed to the pinned checkout. Ruff is clean, mypy is clean across the current source and scripts, and the package build, clean installed validator, and local-contract smoke commands passed. No live Twilio request, credential check, or provider callback was used.

## Pinned boundary

The generator reads 60 JSON specifications from official `twilio/twilio-oai` commit `ef1d81e7b6e49e602530601e913eedc21aedd6da` and accounts for 1,554 raw operations:

- 1,333 fixed commands
- 205 past-end-of-life rows
- 9 exact older routes mapped to their canonical command
- 1 developer-preview row without a stable complete request contract
- 6 rows whose complete current request contract is not publicly available

The catalog loader checks those totals before registering commands. Command names are unique, the generated catalog and `docs/api_coverage.md` come from the same rows, and no raw URL or arbitrary-method command exists.

The pinned OpenAPI left 81 writes empty or partly untyped. The audit checked each one against current official Twilio docs and Twilio-owned product schemas. Seventy-one now have operation-specific manual request supplements. The remaining audited rows retain explicit dispositions in the generated coverage ledger. Separately, the overall inventory has 205 legacy, 9 canonical-duplicate, 1 developer-preview, and 6 private-or-unavailable raw rows outside the callable command count; these categories are not a second manual-contract equation.

The boundary still contains two Frontline commands for existing customers. Frontline is end-of-sale and scheduled to retire on September 30, 2026, so those commands are access-gated, live-unverified, and require a boundary review before that date.

## Local and mocked behavior

The local suite covers:

- imports, package version, one-object CLI output, safe parse errors, and accurate operation help for protected output and snapshots
- deterministic inventory generation, per-operation coverage, duplicate analysis, end-of-life dispositions, request schemas, private-data annotations, and risk labels
- the 81-row manual-contract audit, operation-specific sources and restrictions, priority commands, and the absence of any unresolved unbounded write schema
- API-key Basic auth, the warned Auth Token fallback, OAuth selection, declared Authorization headers, and paired region-and-edge routing
- fixed input validation for path, query, headers, bodies, required fields, unknown fields, and content types
- exact-field flexible JSON, stringified form JSON parsing, object or array shape and size limits, refusal of undocumented branches, and recursive redaction inside nested JSON strings
- Studio widget-type and state-envelope refusal, accepted-flow nested Definition risk escalation, Video rule filter/exclusivity/duplicate checks, and required composition inputs for composition create plus composition-hook create and update
- ordinary read retries, private-data-safe output, protected sensitive-output files, command-specific reduced snapshots, and secret-safe errors
- request validation before dry-run planning, plan creation, account and input binding, changed-plan refusal, snapshot file permissions, category acknowledgements, paid Lookup planning, exact bulk target derivation, count matching, and the 25-target limit
- receipt pre-creation before HTTP, existing and unwritable receipt refusal, one-attempt writes, `succeeded`/`failed`/`uncertain` attempt records, mocked post-write reads, and the difference between queued and delivered
- safe example files, all four documented Twilio test-credential fixtures, wrapper-to-command alignment, documentation links, and packaged catalog access
- local-contract validation for strict ConversationRelay TwiML, bounded nested Language children, GET/POST Connect methods, documented WebSocket messages, raw-body webhook signatures with environment-only Auth Token lookup and repeated-value canonicalization, and Agent Connect metadata; plus installed-boundary regression and validator smoke coverage
- strict SCIM PatchOp paths/types, paired username/email rules, required optimistic locking, redacted version-only snapshots, snapshot command/account/target binding, Porting public-host HTTPS and event refusals, overwrite planning, mandatory snapshots, paired post-write GETs, and operation-specific normal-output, provider-error, and failed-receipt redaction

These checks use local fixtures and mocked HTTP responses. They prove what the tool constructs, refuses, records, and reports without contacting Twilio.

## Not proved against Twilio

No live credentials were available for this build. No provider request was made for an account read, message, call, Verify attempt, Lookup, number purchase, preview product, entitlement-gated product, or post-write check. No delivery callback was received.

The four included fixtures cover the operations Twilio documents for test credentials: SMS, calls, phone-number purchases, and Lookup. The first three use Twilio's documented `+15005550006` test value. The Lookup fixture uses `+12345678924` with `Fields=sim_swap`, as documented for a successful SIM-swap magic-number response. These fixtures were validated locally but were not sent with Twilio test credentials. They do not update live state or connect real numbers, and SMS or call test requests do not trigger status callbacks.

Therefore, local green tests do not prove credential permissions, regional availability, account entitlements, provider-side validation, billing, carrier delivery, webhook delivery, or current preview behavior.

## Reproduce the local checks

From the tool folder:

```bash
.venv/bin/python -m unittest -q
.venv/bin/ruff check src tests scripts
.venv/bin/mypy src scripts
.venv/bin/python -m build
.venv/bin/qwayk-twilio-safe-agent-cli inventory summary
.venv/bin/qwayk-twilio-safe-agent-cli inventory show \
  --command api-v2010.fetch-account
```

The normal suite does not contain a machine-specific checkout path. It validates the bundled catalog on a clean clone. To include direct pinned-source hash and writer-regeneration checks, set `TWILIO_OAI_SPEC_ROOT` to a checkout at the pinned commit before running the suite:

```bash
TWILIO_OAI_SPEC_ROOT=/path/to/pinned/twilio-oai \
  .venv/bin/python -m unittest -q
```

To reproduce the generated boundary from a clean checkout of the pinned official commit:

```bash
.venv/bin/python scripts/generate_twilio_inventory.py \
  --spec-root /path/to/pinned/twilio-oai
```

Live verification is a separate step requiring approved credentials, product access, and an operation chosen not to contact a person or create an unwanted charge.
