# Skills wrappers (Agent Skills)

The shipped commands can be used as a skill in agent runtimes that support deterministic CLI calls.

## Core rules

- Skills are instructions; the CLI enforces safety.
- No free-form shell execution.
- Never include secrets in prompts or examples.
- This tool supports reads + writes, but write RPCs are plan-first by default and require explicit approval (`--apply` + safety gates). The skill must never “auto-apply” writes.

## Where the skill lives

- Canonical location: `skills/google-ads-api-safe-cli/SKILL.md`.
- Users can copy or symlink the skill into their runtime skills folder (example: `.codex/skills/`).

## What the skill must include

- Smallest-query-first defaults for reads.
- Direct GAQL investigation with explicit completeness; optional exports and comparisons. Legacy heuristic diagnosis is not a required step.
- For writes: plan-first workflow (emit plan, ask for approval, then apply from a reviewed plan when required).
- For live writes: save before-state for supported updates and readable ad-schedule removes; other shapes require explicit no-snapshot approval.
- Create/upload, builder-create, unreadable removes, and other unsupported write shapes need explicit `--ack-no-snapshot` approval before live apply.
- For repeated account changes, prefer the helper commands before hand-writing raw RPC JSON:
  - keyword pauses
  - keyword adds
  - campaign negatives
  - budget changes
  - Maximize Clicks CPC ceiling changes
  - entity lookups by name
  - enable/pause entity batches
  - whole campaign-tree enable/pause
  - click conversion uploads
  - read-only overlap and policy-risk prechecks before live builds
- For whole campaign creation, prefer the strict builder commands before hand-writing many separate RPC envelopes:
  - search-campaign
  - competitor-search
  - dsa-feed-search
- If the helper takes `--items`, the skill can use JSON or CSV input.
- Refusal policy when config/auth is missing.
- Examples that avoid real ids/tokens.

## When to refuse

- If the target is ambiguous.
- If required config/auth is missing.
- If the request is likely to exceed quotas or return massive outputs and the user refuses to narrow it.
- If the user asks the skill to auto-apply recommendations, budgets, bids, or keyword removals directly from `snapshot analyze diagnose`.
- If a requested live write would not save before-state when possible and the tool has no explicit no-snapshot approval path for that action.

## Write outcomes and current access

Writes are submitted once, with SDK retries disabled. Reads retain bounded retries. A transport timeout or server error returns `outcome_unknown` and exit status 1, with read-back where possible. Do not replay the request automatically; inspect destination state first.

Partial failures return `partial_failure` and exit status 1. Receipts expose error codes and failed input locations, omitting provider messages/triggers that may echo private data. Reconcile successful items before retrying only failed items. Unknown or malformed detail formats preserve the receipt and increment `partial_failure.undecoded_details`; `errors_decoded` is false if any detail was not understood. Known errors in the same response remain available.

A read-back mismatch returns `verification_failed` and exit status 1. `accepted_unverified` means Google returned a response but completion was not fully proved; `validated` means validation only. Empty read-back targets never count as fully verified. Check the receipt outcome before claiming success.

OAuth credentials and Google Cloud project API access are required; developer tokens are no longer sent. Campaign settings in optimization and maximal-analysis exports include ACA and broad-match AI Max migration dates when Google returns them.
