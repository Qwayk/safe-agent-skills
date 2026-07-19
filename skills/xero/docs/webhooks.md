# Xero webhook receiver safety

This CLI does not host a webhook receiver. Xero's pinned `xero-webhooks.yaml` is callback-only, so there is no polling or generic webhook command. Use these rules if a separate application receives Xero callbacks.

## Verify the raw request before parsing it

1. Read the exact raw HTTP request body bytes. Do not parse and re-serialize JSON before verification.
2. Calculate HMAC-SHA256 over those raw bytes with the webhook signing key from the Xero app settings.
3. Base64-encode the digest and compare it with the `x-xero-signature` header using a constant-time comparison.
4. Return `401 Unauthorized` when the signature is missing or wrong. Do not process the payload.
5. Return a `2xx` response only for a correctly signed payload.

Keep the signing key in secret storage. Never log it, place it in a plan, print it to stdout, or paste it into chat.

## Pass Xero's intent-to-receive check

Xero sends signed empty-event payloads when a webhook is created, re-enabled, or its URL changes. The receiver must apply the same signature verification: respond with `2xx` for every correctly signed validation payload and `401` for every incorrectly signed payload. The HTTPS endpoint must use port 443, respond within five seconds, and send no response cookies.

## Expect retries and duplicates

Treat delivery as at least once. Xero immediately retries a failed delivery, then retries at decreasing frequency for up to 24 hours. Events can later be replayed in order after recovery. Store an event identity or a stable digest before applying side effects, make processing idempotent, and make a duplicate a safe no-op.

Acknowledge a valid callback quickly, then do slower work through a durable queue. If the receiver cannot durably accept the event, return a failure so Xero can retry.

## Protect tenant and event data

One app webhook can carry events for every connected organisation. Bind each event to its tenant ID before any lookup or write. Reject an unknown or disconnected tenant instead of falling back to another organisation.

Webhook bodies can contain contact, invoice, subscription, payroll, or other private identifiers. Keep raw bodies and processing logs owner-restricted, redact normal logs, set a retention limit, and never include full payloads in chat or ordinary stdout.

See Xero's official [webhook guide](https://developer.xero.com/documentation/guides/webhooks/overview/) and the callback schemas in the pinned OpenAPI source. This page documents receiver requirements; it is not proof that a receiver has been deployed or tested against live Xero callbacks.
