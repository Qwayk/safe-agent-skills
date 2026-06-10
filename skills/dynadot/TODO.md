# TODO (Dynadot tool)

Purpose:
- Keep a simple “what’s next” list so work can continue across multiple chats without losing context.

## Next (recommended)

- (Done) Add a guided end-to-end “transfer run” workflow (push → accept → check/fix name servers → summary), with safe resume.
- (Done) Add 100% Dynadot API3 command coverage from official request examples (`api3/`).
- (Done) Add verify-after-write for API3 writes (strict read-back when feasible; otherwise read-back snapshots recorded in receipts).

## Next (only when Dynadot publishes docs)

- If Dynadot publishes full request examples/parameter tables for the menu-only commands currently out-of-scope,
  add them safely (no guessing). Track them in `docs/api_coverage.md`.

## Later (only if needed)

- Expand Dynadot API coverage command-by-command (use the coverage ledger as the checklist).
