# How live changes stay under your control

The tool can read stable Spaceship API data after credentials are configured. It does not turn a write request into a live change immediately.

## A write starts as a saved plan

The plan records the exact command, target, query, request-body digest, important spend or financial fields, risk categories, required acknowledgements, and a plan-integrity digest. Private contact, transfer, checkout, and SafePay values are masked or replaced by canonical SHA-256 digests.

When Spaceship offers a reliable read for the target, the tool saves a redacted snapshot digest. When the API cannot provide a reliable snapshot or full financial recheck, the plan says so and requires `--ack-no-snapshot`.

If you do not choose file paths, the plan and receipt are saved automatically under `.state/runs/<run_id>/`. A run ID must be one non-empty local path segment: absolute paths, slashes, backslashes, `.` and `..` are refused before a run folder is created. Explicit `--plan-out` and `--receipt-out` paths override the automatic plan and receipt locations.

Saved command displays keep normal domain targets useful, but replace contact IDs and SafePay transaction IDs with deterministic SHA-256 displays. Billing contact IDs are masked. If a private-data operation returns an unstructured error or a generic `detail`, `message`, response, or raw body, the tool saves only a redacted digest instead of the provider text.

## Apply uses the same reviewed request

A live write requires all of these:

1. The same command, target, query, and body used to create the plan.
2. `--apply --yes --plan-in <path>`.
3. Every stronger acknowledgement listed in the plan.
4. A matching plan-integrity digest.
5. A fresh preflight read when the official API exposes one.

If the target, body, snapshot, exposed price or expiration fields, or plan integrity changed, the tool refuses before the write. A successful apply sends exactly one provider write.

## Stronger acknowledgements

The plan selects only the flags that apply:

- `--ack-spend` for registration, renewal, restoration, auto-renew, or another cost risk.
- `--ack-ownership` for registration, transfers, listings, checkout, SafePay, or other ownership-sensitive work.
- `--ack-dns-risk` for DNS, nameserver, and personal-nameserver changes that can interrupt websites or email.
- `--ack-financial` for SellerHub pricing, checkout links, SafePay, and other financial obligations.
- `--ack-destructive` for supported deletion paths.
- `--ack-private-data` for contacts, transfer codes, and private transaction details.
- `--ack-no-snapshot` when Spaceship does not expose a reliable snapshot or full financial recheck.

## After the write

The receipt records the redacted request, HTTP status, rate-limit details, async operation ID, and verification result. The tool reads back state only when it has a reliable target for that operation. Otherwise it says `unverified` instead of treating the write response as proof of the final state.

Reliable readback includes a newly created domain by its reviewed domain, saved contact details or attributes when the write response returns `contactId`, a new SellerHub domain by the reviewed request `name`, and a new SafePay transaction when the response returns `transactionId`. Missing response IDs leave the receipt honestly `unverified`. Checkout-link creation has no reliable read target and remains `unverified`.

HTTP 204 is a successful response with no JSON body. HTTP 202 is `accepted_not_completed`; use the saved async operation ID with `async-operations status` to check later.

## Local refusals

Spaceship documents two operations as under development with HTTP 501. `domains delete` and `domains personal-nameservers get-host` refuse locally, without credentials or a network request.

The tool also refuses missing credentials for provider reads or applies, unsafe API hosts, changed plans, missing acknowledgements, unresolved path values, and requests outside the fixed command inventory.

HTTP redirects are never followed. A 3xx response fails at the original fixed host, and the custom API key and secret headers are not resent to the redirect destination.
