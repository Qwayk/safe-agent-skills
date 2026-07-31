# Safety model

The tool can run the four read commands after authentication because they do not change the account. The other eight SAV operations use HTTP GET too, but they change domain or sale settings, so the tool treats them as writes.

All read commands run directly against SAV and never write data.

All write commands are dry-runs unless apply flags are fully supplied.

## Write safety gates

An apply attempt is allowed only with all of the following in one command:

- `--apply`
- `--yes`
- `--plan-in <path>`
- `--ack-no-snapshot`
- `--ack-high-risk`

A dry-run always saves one mode-`0600` plan. Use `--plan-out` to choose its path. Without that flag, the tool saves it under `.state/plans/` beside the selected env file.

## What the plan/receipt actually guarantees

- The plan keeps the minimum exact values needed for apply and is signed with HMAC-SHA256 (`schema_version: 2`).
- The displayed plan hides transfer codes and WHOIS contact data.
- Domain names and nameserver values are validated as strict FQDNs before any write plan.
- Missing, malformed, or changed plan/key state fails before any provider request.
- Receipt handling is explicit:
  - if the runtime cannot write a pre-write receipt, the command returns safely with `ok: false`, `outcome: "not_attempted"`, and `retry: "fix-receipt-path-before-retry"`.
  - if the provider returns a non-2xx status, `outcome` is `failure` and the redacted provider response is still written.
  - if the request fails before a provider response, `outcome` is `unknown` and `retry: "do-not-retry"` to avoid blind replays.
  - if SAV returns a response but the final receipt cannot be saved, output says that the provider responded, whether it was 2xx, that provider/account state remains unverified, and that the user must not retry blindly.
- Reliable before-state snapshots are not available from the documented collection.
- `snapshot_status` is `"unavailable"` on every write plan.
- `independent_readback_available` is `false`.
- `rollback_available` is `false`.
- All non-2xx provider responses are treated as failure outcomes.

Displayed output and receipts are redacted for:

- auth-like values in keys like `auth`, `auth-code`, `auth_code`, `authCode`, and `auth-code-file`
- WHOIS or contact metadata and redaction targets (`whois`, `whoisContact`, `whois_contact`, `whoiscontact`, `postalCode`, `emailAddress`, `phone`, `phoneNumber`).
- identity and address metadata (`name`, `organization`, `street`, `city`, `state`, `country`, `postalCode`, `postal_code`, `phone`, `email_address`).
- status fields are not redacted (`status`, `statusCode`, `status_code`, etc.).

When a provider response exists, `provider_response_only` is `true`; without a provider response it is `false`. A 2xx response uses `outcome: "provider_accepted"`, which does not prove the lasting SAV account state. On provider HTTP failure, output is `ok: false` with return code `1`, and the response receipt is redacted.

## What is currently not available

- No restore path, snapshot restore, or backup workflow.
- No generic read-after-write guarantee.
- No guarantee that provider responses are durable proof of irreversible state.
- No raw-request or arbitrary-URL command beyond the fixed 12 operations.
