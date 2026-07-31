# Skills wrappers (Agent Skills)

The tracked `sav` skill tells an agent when to use this tool, which read to try first, and when to stop for approval.

This wrapper is published in one of two exclusive layouts:
- Source checkout: `skills/sav/SKILL.md`
- Public mirror: top-level `SKILL.md`

Exactly one layout should exist at a time. This resolver behavior is intentional so the wrapper logic is not duplicated across two active files.

## Core wrapper rules

- Keep write defaults as dry-runs (`--plan-out` without apply).
- Every write apply must include:
  - `--apply`
  - `--yes`
  - `--plan-in`
  - `--ack-no-snapshot`
  - `--ack-high-risk`
- Keep plan/receipt/key paths private by default (`.state/plans`, `.state/receipts`, `.state/keys`).
- Expect mode-`0600` plan/receipt/key files and mode-`0700` state directories.
- Plans use `schema_version: 2` and are signed with HMAC-SHA256.
- Do not use this wrapper for registrations, auction bids, browser automation, undocumented endpoints, or arbitrary API requests.
- Do not claim hidden raw bridge support.
- Do not suggest any environment or literal command-line fallback for a transfer authorization code.
- Treat `provider_response_only` as true only when `provider_response_received` is true.
- Treat `receipt_written` as local receipt persistence only. It does not verify SAV account state.
- Treat `provider_accepted` as a 2xx provider response only, never independent verification.
- Never follow redirects; treat every provider response outside 2xx as a failure.
- If an apply outcome is unknown or its final receipt was not written, do not retry blindly.
- Require finite positive timeouts and strict domain/nameserver values before any request.
- Treat WHOIS and auth-like fields as sensitive and do not echo them in plain chat.
