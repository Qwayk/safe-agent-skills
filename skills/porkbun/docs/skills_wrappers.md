# Skills wrappers

The runtime command is `porkbun`.

Load the tracked Porkbun skill when a user asks for:

- domain list/availability checks
- DNS, nameserver, glue, URL-forwarding checks
- SSL and marketplace reads
- API settings, balances, invites, and webhook management
- any safe planning and execution flow for writes

## Wrapper first check

Before any tool call:

1. `porkbun --output json onboarding` (writes `.env` template)
2. `porkbun --output json auth check` (safe auth read)
3. `porkbun --output json domain get-domains` (safe first account read)

`onboarding` writes `.env` atomically as an owner-only `0600` file. Never ask the user to paste API keys in chat or put them in command arguments.

## Non-negotiables

- Never use raw Porkbun endpoints.
- Never ask users to paste keys.
- Keep the official boundary at 53 paths and 66 fixed commands: 39 reads and 27 writes.
- Allow only `https://api.porkbun.com/api/json/v3` and `https://api-ipv4.porkbun.com/api/json/v3`.
- Never run write commands without:
  - a plan
  - approval
  - required acknowledgement flags
  - clear readback review
- Treat saved plans as local authenticated instructions. They carry an HMAC-SHA256 signature made with owner-only `.state/plan-signing.key`.
- Run plan and apply with the same local key and `.state`. Refuse if the plan moved without its state, the key is missing or different, or the plan changed.
- Keep tool-created `.state` directories at `0700`. Plans, receipts, secret files, the signing key, and onboarding `.env` files must be atomic owner-only `0600` files.
- Keep active plan, receipt, and secret output paths different from one another and from the environment, JSON input, and plan input files. Treat aliases through relative paths, `..`, symbolic links, or existing-file identity as the same path.
- Require `--ack-secret` and keep full secret-bearing outputs in `--secret-out` only.
- Let the CLI preflight and reserve `--secret-out` before any provider call. An unsafe or unwritable destination must stop with no request.
- Do not follow redirects. Treat every `3xx` response as failure.
- For `porkbun account get-account-invite-status`, put `{"token":"..."}` in a private JSON file and pass its path with `--input`. Never use `--token`.

## When to refuse

- ambiguous target
- missing `PORKBUN_API_KEY` / `PORKBUN_SECRET_API_KEY`
- required acknowledgement flags missing for a planned write
- missing plan confirmation for apply
- missing or mismatched local plan-signing key/state
- colliding output and input/control file roles
- unsafe secret-output destination
- redirect response

Repository tests use fakes and local fixtures. They made no live Porkbun calls and do not prove live-account behavior.

This wrapper is implemented in `skills/porkbun/SKILL.md` for agent hosts that load tracked skills from source.
