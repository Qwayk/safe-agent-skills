# Skill: Microsoft Ads SafeCLI (`msads-api-tool`)

This page is the agent-facing rule sheet for the public Microsoft Ads skill.
If you just want to use the skill, start with the README plus the use-cases and onboarding docs.

Use this skill to interact with the Microsoft Advertising API v13 via the safe-by-default CLI in this repo.

## Safety rules (non-negotiable)

- No network requests without `--live`.
- Writes require `--apply` (and may require `--yes`, `--ack-irreversible`, and/or `--plan-in` depending on risk).
- Prefer `--plan-out` → review → `--plan-in` for high-risk/irreversible operations.
- Never print or paste secrets (DeveloperToken, OAuth tokens, client secrets). Use redacted outputs only.
- Current write applies need `--ack-no-snapshot` before SOAP HTTP when no before-state can be saved. Review the result and confirm whether the tool produced a receipt or an exact limitation.

## Setup and quick checks (offline)

- Version:
  - `msads-api-tool --output json --version`
- Auth/config status (offline; does not hit the network):
  - `msads-api-tool --output json auth check`

## Live read (requires explicit opt-in)

- Use `--live` for any real API call (read or write).
- Example (read-like operation):
  - `msads-api-tool --output json --live customer-management get-accounts-info --request-json request.json`

## Writes (plan → review → approved attempt)

1) Plan (dry-run):
   - `msads-api-tool --output json <service> <operation> --request-json request.json --plan-out plan.json`
2) Review `plan.json` (human/agent).
3) Confirm the receipt or exact tool limitation:
   - `msads-api-tool --output json --live --apply --plan-in plan.json <service> <operation> --request-json request.json`

Notes:
- If the operation is high-risk/irreversible, the CLI stops unless the required flags are present.
- After required gates pass, current writes still need required approval before SOAP HTTP when before-state capture support does not exist yet.
