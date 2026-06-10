# Proof pack (publish-ready evidence)

Purpose:
- Make this tool “proof-first” for future posts/pages (E‑E‑A‑T).
- Capture the minimal evidence a customer can trust: what ran, what came back, what can go wrong, and how we verify.

Note: this is a living evidence file. Keep each item exact and honest about what was actually run.
You don't need to run these commands yourself. They exist for auditing and proof.

Rules:
- Never include secrets (tokens, client secrets, Authorization headers).
- Use obvious redactions/placeholder values in examples.
- Keep this file short and factual.

## Last verified

- Date (UTC): `2026-06-07`
- Verified by: `final practical snapshot repair pass + PYTHONPATH=src python3 -m unittest discover -s tests -t .`
- Tool version: `0.1.0`
- Provider API version (if applicable): `CallRail API v3`
- Environment: `local smoke checks with redacted mocked HTTP examples and fresh unittest rerun` / provider base URL: `https://api.callrail.com`

## Smoke checks (copy/paste)

Run inside the tool folder:

Most REST commands below need `--account-id` unless your local `.env` already sets `CALLRAIL_DEFAULT_ACCOUNT_ID`.

1) Create venv + install:
- `python3 -m venv .venv`
- `.venv/bin/python -m pip install -e .`

2) Version (no `.env` required):
- `qwayk-callrail-safe-agent-cli --output json --version`

3) Auth/config check (read-only):
- `qwayk-callrail-safe-agent-cli --output json auth check`

4) One representative read query:
- `qwayk-callrail-safe-agent-cli --output json accounts list`

5) One representative single-record field-selection read:
- `qwayk-callrail-safe-agent-cli --output json accounts get --account-id acc_example --fields numeric_id`

6) One representative outbound-call dry-run:
- `qwayk-callrail-safe-agent-cli --output json calls create-outbound --account-id acc_example --payload-json '{"caller_id":"+15550001111","customer_phone_number":"+15550002222","business_phone_number":"+15550003333"}'`

7) One representative write dry-run:
- `qwayk-callrail-safe-agent-cli --output json tags create --account-id acc_example --payload-json '{\"name\":\"VIP Lead\",\"color\":\"blue\"}'`

8) One representative MMS dry-run:
- `qwayk-callrail-safe-agent-cli --output json text-messages send --account-id acc_example --payload-json '{"company_id":"COM_example","customer_phone_number":"+15550002222","tracking_number":"+15550003333","content":"Photo attached","media_url":"https://cdn.example.com/sample.jpg"}'`

## Example outputs (redacted)

These committed example files show redacted, non-secret output:
- `docs/examples/outputs/version.json`
- `docs/examples/outputs/auth_check.json`
- `docs/examples/plan.example.json`
- `docs/examples/receipt.example.json`

## What can go wrong (and how we verify)

- **Invalid API key / wrong scopes** → use `auth check`; if `ok=false`, stop and update the token.
- **Write commands fail after auth passes** → very common when key has read-only access; confirm key was created with the needed write permissions.
- **Outbound call or SMS preview looks right but live apply still fails** → confirm the correct account context is being used (`--account-id` or `CALLRAIL_DEFAULT_ACCOUNT_ID`) and that the key has write access.
- **MMS send payload is rejected** → send either JSON `media_url` or multipart `--media-file`, never both in the same request.
- **Rate limiting** → confirm rate-limit responses are surfaced clearly and no retry storm happens.
- **Plan/receipt mismatch** → ensure write actions only run with `--apply --yes --ack-no-snapshot` and review the receipt vs planned command.
- **Transcript data** → some transcript fields can be null when the account lacks Premium Conversation Intelligence.

## Local vs live scope

- Local checks and plan generation are fully runnable in dry-run mode.
- The committed auth, plan, and receipt examples are redacted local examples generated from the current runtime shape.
- The committed proof pack includes local coverage for outbound-call account scoping and the two supported SMS/MMS request shapes (`media_url` JSON and `--media-file` multipart).
- The committed proof pack also includes local coverage for single-resource field selection and for the paginated SMS-thread read query shape.
- The 2026-06-07 repair added local coverage that writes without `--ack-no-snapshot` stop before HTTP, while approved no-snapshot writes run and record the approval in the receipt.
- The 2026-06-06 audit rechecked the official CallRail auth, field-selection, pagination, and REST-only command-surface docs behind the current coverage ledger.
- Live CallRail writes remain live-unverified in this repo unless you have valid write-enabled credentials and permission to run real apply calls.

## Live-unverified items
- Outbound call and SMS send actions are dangerous; confirm live behavior only in a controlled environment.
- MMS uploads via `--media-file` are locally covered but still need live provider proof with an approved test account.
- Receipt examples are redacted samples and must not be treated as evidence of real production writes.

## Links

- Sources used: `docs/references.md`
- Coverage main reference: `docs/api_coverage.md`
- Debug history: `docs/engineering_notes.md`
