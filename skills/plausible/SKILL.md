---
name: plausible-api-safe-cli
description: Run plausible-api-tool with dry-run by default and explicit apply/verify gates (Events API writes are irreversible).
---

This page is the agent-facing rule sheet for the public Plausible skill.
If you just want to use the skill, start with the README plus the use-cases and onboarding docs.


You are a safe wrapper for the Plausible Qwayk CLI (`plausible-api-tool`).

Core rules (do not break):
- Default to read-only. The Stats API is read-only; treat anything under `event` (Events API) as write-like and irreversible.
- No writes without explicit user approval. For this release, `event send` stays at plan level unless the current command has explicit no-snapshot approval support.
- Never print secrets or ask users to paste secrets into chat.
- Prefer `--output json` for machine-readable output.
- When proposing a write, produce a dry-run plan first (`--plan-out PATH`) and wait for explicit approval before applying.
- Read `plan.recovery` and `receipt.recovery` as the real write contract.
- `site goals ensure`, `site custom-props ensure`, `site custom-props delete`, and `site guests ensure` use `rollback_by_inverse_action`.
- `event send`, `site create`, `site update`, `site delete`, `site shared-links ensure`, `site goals delete`, and `site guests delete` stay `irreversible_and_clearly_labeled`.

Workflow:
1) Discover (read-only) to identify the correct site, pages, and time window.
2) Run read-only reports or generate a dry-run plan for write-like actions (`--plan-out PATH`).
3) Review the output/plan (human or reviewer agent).
4) Apply only when explicitly approved (writes require `--apply --yes --ack-irreversible`).
5) Verify (best-effort read-back where possible) and save a receipt (`--receipt-out PATH`) for applied writes.

References (tool docs):
- `docs/quickstart.md`, `docs/command_reference.md`, `docs/safety_model.md`
- Auth/setup: `docs/authentication.md`

## Copy/paste prompts (safe)

- “Using `plausible-api-tool`, check auth and then generate a 30‑day top pages report (limit 50). Return JSON.”
- “Validate this Stats query JSON for obvious mistakes (metrics/dimensions/date range), then run it in `--output json` mode.”
- “Create a dry-run plan for sending a Plausible event named `test_event` for `https://<YOUR_SITE>/` and write the plan to `.state/plans/event_send.json`. Do not apply.”

## Example CLI invocations (no shell)

Auth check:

- `plausible-api-tool --env-file .env --output json auth check`

Stats: top pages (30 days):

- `plausible-api-tool --env-file .env --output json stats pages top --metric pageviews --days 30 --limit 50`

Events: dry-run plan only (no apply):

- `plausible-api-tool --env-file .env --output json event send --name "test_event" --url "https://<YOUR_SITE>/" --plan-out .state/plans/event_send.json`
