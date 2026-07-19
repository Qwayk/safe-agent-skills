# Changelog

## Unreleased

### Added

- A packaged catalog generated from 61 official Twilio OpenAPI specifications pinned at commit `1a9189c79a73781ddf45afcd0afd1f210742d68c`.
- 1,325 fixed CLI commands with request validation from the pinned operation definitions and operation-specific official request contracts.
- A local `inventory show --command NAME` inspector for one command's fixed input contract.
- API-key Basic authentication by default, a warned Account Auth Token fallback, operation-scoped OAuth, and paired region-and-edge routing.
- Direct safe reads, protected sensitive-output files, plan-first paid reads and writes, approval acknowledgements, optional protected snapshot binding, receipts, and post-write checks.
- Public guides, safe examples, the Twilio skill wrapper, generated API coverage, and local behavior tests.
- A public skill package with the install slug `twilio` in `Qwayk/safe-agent-skills`.

### Safety

- Removed the starter tool's generic request and jobs patterns. The Twilio tool has no raw URL, arbitrary method, SDK pass-through, or generic batch runner.
- Audited all 81 writes that the pinned OpenAPI did not type completely against current Twilio documentation and Twilio-owned product schemas. Added 67 fixed commands, mapped two deprecated Preview Marketplace writes to stable v1 commands, and kept 12 rows non-callable with exact official evidence.
- Added a strict SCIM user PATCH with path-specific scalar types, paired equal username/email changes, required `If-Match`, redacted snapshots, and snapshot-version binding.
- Added the Public Beta Porting webhook overwrite with HTTPS-only targets, the exact 12 POST-side notification values, required before-state snapshot, and paired-GET verification.
- Allowed flexible JSON only in the exact field documented for that operation. Stringified form JSON is parsed, shape- and size-checked, and recursively redacted; undocumented optional branches remain refused.
- Added fixed request contracts for Verify starts, Studio flows and executions, Video rooms and rules, all seven Sync writes, a restricted Proxy session create, Event Streams sinks and subscriptions, and Numbers and TrustHub regulatory writes.
- Added Lookup as the fourth documented Twilio test-credential fixture alongside SMS, calls, and phone-number purchases. No fixture was sent to Twilio.
- Bulk plans derive an exact target list and count, refuse a missing list or count mismatch, and hard-stop above 25 targets.
- Validated every effectful input before producing its dry-run plan.
- Required apply to create a new protected receipt before HTTP, refusing an unwritable or existing receipt destination.
- Recorded each provider attempt as `succeeded` after a 2xx response, `failed` after a provider non-2xx response, or `uncertain` when no provider response arrived.
- Writes make one provider attempt and are never retried automatically.
- Provider responses keep `accepted`, `queued`, `sent`, and `delivered` distinct.

### Limits

- No live Twilio account, send, call, Verify, Lookup, phone-number purchase, or delivery callback has been used as release proof.
- The two Frontline commands remain access-gated for existing customers and require boundary review before Twilio retires Frontline on September 30, 2026.
