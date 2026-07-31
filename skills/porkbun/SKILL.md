---
name: porkbun
description: Read Porkbun domain and account data or prepare confirmed changes through the fixed safe CLI.
---

# Skill: Porkbun

Use this skill when someone needs help reading Porkbun account data or preparing and applying provider changes with confirmation.

Start with setup and an account read, then ask for approval before any write is applied.

## Core rules

- Never ask for, paste, or repeat `PORKBUN_API_KEY` or `PORKBUN_SECRET_API_KEY` in chat.
- Do not use free-form Porkbun API URLs.
- Keep the official boundary at 53 paths and 66 fixed commands: 39 reads and 27 writes.
- Allow only `https://api.porkbun.com/api/json/v3` and `https://api-ipv4.porkbun.com/api/json/v3`.
- Run `onboarding` or check `.env` values before first use.
- Run `auth check` before service reads when account context is not already known.
- Prefer `--output json` for parseable results.
- Never show full secrets or full credential-like payloads in normal output.
- For read-only operations, call directly after auth validation.
- For writes, use plan-first workflow: `--plan-out` first, review, then `--apply --yes --plan-in`.
- Saved plans are authenticated with HMAC-SHA256 using the owner-only local `.state/plan-signing.key`. Run plan and apply from the same working directory with the same `.state`; refuse if the key is missing, different, or the plan changed.
- Billable and high-risk writes also need required acknowledgements (`--ack-spend`, `--ack-terms`, `--ack-no-snapshot`, etc.) as the command surface requires.
- Secret-bearing reads and writes require both `--ack-secret` and `--secret-out`.
- Let the CLI preflight and reserve the secret destination before any provider call. If it is unsafe or unwritable, stop without contacting Porkbun.
- Keep tool-created `.state` directories at `0700`. Plans, receipts, secret results, the signing key, and onboarding `.env` files are atomic owner-only `0600` files.
- Keep active plan, receipt, and secret output paths distinct from one another and from environment, JSON input, and plan input files. The CLI must refuse aliases before any provider request or replacement.
- Never follow redirects. A `3xx` response is a failure, not a result or successful receipt.
- For `account get-account-invite-status`, put the token only in a private JSON `--input` file. Never use `--token`.
- Email password changes require `--ack-secret` for the sensitive input, and operations without a reliable snapshot also require `--ack-no-snapshot`.

## Safe workflow

1. Check command availability and onboarding:

```bash
porkbun --output json --version
porkbun --output json onboarding
```

2. Validate current auth state:

```bash
porkbun --output json auth check
```

3. Do a safe first read for the target object:

```bash
porkbun --output json domain get-domains
```

4. Build and review a plan:

```bash
porkbun --output json dns dns-create --domain example.com --input dns-create.json --plan-out dns-create.plan.json
```

5. Apply only after review:

```bash
porkbun --output json dns dns-create --domain example.com --input dns-create.json --apply --yes --plan-in dns-create.plan.json --receipt-out dns-create.receipt.json
```

Use the same `dns-create.json`, working directory, and local `.state` for both commands. Review the plan before apply.

6. Check an account invite from a private input file:

```json
{"token":"INVITE_TOKEN"}
```

```bash
chmod 600 invite-status.json
porkbun --output json account get-account-invite-status --input invite-status.json
```

7. Keep sensitive response payloads out of normal output:

```bash
porkbun --output json ssl get-ssl-retrieve --domain example.com --ack-secret --secret-out ssl_bundle.json
```

## Good asks

- “Check current DNS and nameserver state for `example.com`.”
- “Show transfer and renewal costs before I decide to pay.”
- “Review webhook deliveries for failed attempts.”
- “Prepare a plan to update this domain record, then show what else is required to apply.”
- “Set the mailbox password for `user@example.com` using a prepared JSON file and required safety acknowledgements.”

## Refuse if

- Credentials are missing or invalid for the requested action.
- A write is requested without a reviewed plan.
- Required acknowledgement flags are missing for an unsafe operation.
- Plan and apply do not share the same valid local signing key and `.state`.
- An active output path aliases another output, the environment file, JSON input, or plan input.
- A secret-output destination is unsafe or cannot be reserved.
- Porkbun returns a redirect.
- The request is for a dashboard, webhook receiver, or undocumented API path.

Do not claim live-account proof from the repository checks. They made no live Porkbun calls.
