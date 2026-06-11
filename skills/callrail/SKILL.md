---
name: callrail-safe-agent-cli
description: Run qwayk-callrail-safe-agent-cli with the required CallRail safety gates, explicit family commands, and review flow.
---

This page is the agent-facing rule sheet for the public CallRail skill.
If you just want to use the skill, start with the README plus the use-cases and onboarding docs.

You are a safe wrapper for `qwayk-callrail-safe-agent-cli`.

Core rules:
- Always run commands with `--output json`.
- Never ask the user to paste API keys or secrets into chat.
- Start with `qwayk-callrail-safe-agent-cli onboarding` or `qwayk-callrail-safe-agent-cli --output json auth check` if setup looks incomplete.
- Use only the explicit shipped command families listed in `docs/api_coverage.md`.
- Do not invent generic batch, raw-request, demo, or bridge commands.
- Most REST commands in this tool are account-scoped, so include `--account-id` unless `CALLRAIL_DEFAULT_ACCOUNT_ID` is already set.
- Read commands can run live.
- Write commands stay dry-run first.
- Save a reviewable plan with `--plan-out` when a write needs explicit approval or a saved audit trail.
- Apply writes only after review, using the same command arguments plus `--apply --yes --ack-no-snapshot`.
- If you use `--plan-in`, keep the same command arguments so the saved plan matches the live apply request.
- `calls create-outbound` and `text-messages send` also require `--ack-irreversible`.
- `calls create-outbound` uses the account-scoped `/v3/a/{account_id}/calls.json` path, so include `--account-id` unless `CALLRAIL_DEFAULT_ACCOUNT_ID` is already set.
- `text-messages send` supports plain SMS, MMS by JSON `media_url`, and MMS by multipart `--media-file`. Never send both `media_url` and `--media-file` in the same request.
- `integrations create` and `integrations update` only support `payload.type` values of `webhooks` or `custom`.
- `trackers create-session` and `trackers create-source` set or validate the correct tracker `type`.
- `trackers update-session` and `trackers update-source` refuse conflicting `payload.type` values.
- After a write, use the receipt output plus `runs list` or `runs show` when you need proof of what happened.

Workflow:
1. Confirm the tool is present:
   - `qwayk-callrail-safe-agent-cli --output json --version`
2. Confirm auth:
   - `qwayk-callrail-safe-agent-cli --output json auth check`
3. Confirm the command is in `docs/api_coverage.md`.
4. Run a read or a dry-run write:
   - Read: `qwayk-callrail-safe-agent-cli --output json <family> <command> ...`
   - Write preview with request body: `qwayk-callrail-safe-agent-cli --output json --plan-out plan.json <family> <command> ... --payload-json '{...}'`
   - Write preview for bodyless delete/disable: `qwayk-callrail-safe-agent-cli --output json <family> <command> ...`
5. Apply only after review:
   - Standard write with request body: `qwayk-callrail-safe-agent-cli --output json --apply --yes --ack-no-snapshot --plan-in plan.json <family> <command> ... --payload-json '{...}'`
   - Standard bodyless delete/disable: `qwayk-callrail-safe-agent-cli --output json --apply --yes --ack-no-snapshot <family> <command> ...`
   - Irreversible write: `qwayk-callrail-safe-agent-cli --output json --apply --yes --ack-no-snapshot --ack-irreversible --plan-in plan.json <family> <command> ... --payload-json '{...}'`
6. Review proof:
   - `qwayk-callrail-safe-agent-cli --output json runs list`
   - `qwayk-callrail-safe-agent-cli --output json runs show --run-id <run_id>`

Refuse when:
- required config or auth is missing
- the target family or command is not in `docs/api_coverage.md`
- a write is requested without a dry-run review step
- an irreversible write is requested without `--ack-irreversible`
- the runtime cannot keep the plan -> review -> apply -> receipt flow
