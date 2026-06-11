# Skill: Cloudinary REST API (Safe CLI)

This page is the agent-facing rule sheet for the public Cloudinary skill.
If you just want to use the skill, start with the README plus the use-cases and onboarding docs.

Use this skill to work with the official Cloudinary REST APIs through `cloudinary-safe-agent-cli`.

## Core rules

- Never ask the user to paste Cloudinary secrets into chat.
- Always use `cloudinary-safe-agent-cli --output json`.
- Use `operations list` or `operations show` before guessing a command.
- Reads can run directly.
- Writes must stay dry-run first.
- Write apply needs a reviewed plan and `--ack-no-snapshot` before Cloudinary HTTP when no before-state can be saved.
- Delete-like actions and access-key actions need `--ack-irreversible`.
- Sensitive or binary results need `--out`.

## Setup

Make sure `.env` has:

- `CLOUDINARY_CLOUD_NAME=...`
- `CLOUDINARY_API_KEY=...`
- `CLOUDINARY_API_SECRET=...`

For account commands also set:

- `CLOUDINARY_ACCOUNT_ID=...`
- `CLOUDINARY_ACCOUNT_API_KEY=...`
- `CLOUDINARY_ACCOUNT_API_SECRET=...`

## Safe workflow

1. Verify the tool exists:
- `cloudinary-safe-agent-cli --output json --version`

2. Verify auth:
- `cloudinary-safe-agent-cli --output json auth check`

3. Find the right shipped command:
- `cloudinary-safe-agent-cli --output json operations list --area upload --limit 20`
- `cloudinary-safe-agent-cli --output json operations show --area upload --op upload-signed`

4. Run a read:
- `cloudinary-safe-agent-cli --output json operations ...`

5. Preview a write:
- `cloudinary-safe-agent-cli --output json --plan-out plan.json operations ...`

6. Attempt apply only after review:
- `cloudinary-safe-agent-cli --output json --apply --yes --plan-in plan.json operations ...`

7. Add extra safety flags when needed:
- `--ack-irreversible` for delete-like and access-key actions
- `--out` for sensitive or binary results

## Refusal conditions

- Missing Cloudinary setup for the requested API area
- Write requested without a dry-run review step
- Apply requested without clear target params
- Current write apply needs reviewed approval and `--ack-no-snapshot` when no before-state can be saved
- Sensitive or binary result requested without `--out`
