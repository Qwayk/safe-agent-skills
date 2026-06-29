# Safety model

Zapier can reach connected apps, send messages, create records, and modify workflows. This tool treats discovery and review as normal reads, and treats every state-changing or side-effect operation as plan-first.

## Rules

1. Reads return direct responses when credentials are valid.
2. POST, PUT, PATCH, and DELETE operations output a plan first.
3. High-risk operations require:
   - `--apply`
   - `--plan-in`
   - and one of `--yes`, `--ack-irreversible`, or `--ack-no-snapshot`.
4. Secrets are redacted from JSON output and local artifacts.
5. Plans and receipts include environment fingerprint, operation identity, and verification state.

## High-risk operations

The strictest gate covers action execution, Zap creation, authentications, inbox deletion, inbox message lease/ack/release, promotions deletion, and AI Action execution or deletion. Those actions can affect connected products or remove queue state, so an agent must show the plan first and wait for approval.

## Why this is safer than raw API access

All operations are explicit. The CLI only allows the 62 pinned API operations from official Zapier specs. There is no generic request passthrough, no arbitrary method/path input, and no natural-language "run anything" shortcut.
