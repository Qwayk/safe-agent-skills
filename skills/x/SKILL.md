<INSTRUCTIONS>
# Skill: x-api-safe-cli

This page is the agent-facing rule sheet for the public X skill.
If you just want to use the skill, start with the README plus the use-cases and onboarding docs.

Use this skill when you need to interact with the **X API v2** safely via `x-api-tool`.

## Safety contract (non-negotiable)

- Default to **plan-only**. Do not hit the network unless explicitly allowed.
- GET/HEAD: require `--live` to execute.
- Non-GET: require `--apply --yes`; when no saved snapshot exists, also require `--ack-no-snapshot`.
- DELETE: also require `--ack-irreversible`.
- Never print secrets (bearer tokens, OAuth tokens, Authorization headers). Never show `.env` contents.

## Onboarding (first run)

1) Run `x-api-tool --output json --version` (no `.env` required).
2) Run `x-api-tool onboarding` (creates `.env` from `.env.example` if missing).
3) For auth:
   - App-only bearer: set `X_API_BEARER_TOKEN` in `.env`.
   - OAuth2 user token helpers plan first, then apply with `--apply --yes --ack-no-snapshot`.
4) Smoke check: `x-api-tool --output json --env-file .env auth check`.

## Generic API access (OpenAPI-backed)

Use the pinned OpenAPI inventory for coverage and determinism:
- List operations: `x-api-tool --output json --env-file .env api ops list`
- Plan: `x-api-tool --output json --env-file .env api <operationId> ...`

If the request is ambiguous, stop and ask for:
- the `operationId`, and
- any required path params and request body fields.

## DMs (strict policy)

- Never bulk-DM without clear intent evidence and an opt-out line.
- For bulk: require a CSV with `recipient,message,intent_evidence` and a non-empty `--opt-out-line`.
- Refuse recipients present in the local opt-out ledger (`x-api-tool dm opt-out list`).

## Proof artifacts and limitations

For write-capable actions, prefer:
- `--plan-out <path>` for review
- `--plan-in <path>` for the confirmed apply attempt
- `--receipt-out <path>` for the apply receipt

Apply without `--ack-no-snapshot` should stop safely (`refused=true`) before an X write. Apply with it should write a receipt for supported write paths.
</INSTRUCTIONS>
