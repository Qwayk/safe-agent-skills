# How Xero changes stay review-first

Reads can run after the tool proves the credential, scope, region, input, and exact tenant. Writes cannot run from a fresh command alone.

Xero API data must not be used to train or contribute to AI or machine-learning models under Xero's current Developer Terms. This CLI supports user-directed operational tasks; it does not add provider data to a model-training dataset. See Xero's [official policy FAQ](https://developer.xero.com/faq).

## Reads and private data

Financial, bank, payroll, tax, contact, file, and billing responses are sensitive. Normal stdout keeps the response shape but masks every provider-supplied value. Use `--protected-output` to place the full provider response in an owner-only local file; stdout then contains only the location, size, and SHA-256 hash.

The CLI refuses JSON request bodies and file uploads larger than 10 MB before a provider request. This follows Xero's newer global API request limit and Files guidance; some older Accounting attachment pages still mention 25 MB, so the tool uses the safer current global limit.

## The write flow

1. The fixed command validates its documented input.
2. The tool records the exact auth profile, tenant, URL, method, input hash, uploaded-file byte hash when applicable, risk flags, and command-catalog hash.
3. When an exact paired GET exists, the tool captures a before-state hash. Otherwise it records an honest no-snapshot warning.
4. The plan is saved with an integrity hash and owner-only permissions. No write has happened yet.
5. Apply reloads the plan and refuses if the catalog, auth profile, tenant, command, supplied input, uploaded file, integrity, or available before-state changed.
6. Required approvals are checked before the provider request.
7. The result is checked for HTTP errors and Xero validation errors, followed by the documented paired read when one exists.
8. A protected receipt records the provider status, redacted response, rate-limit headers, verification, and the limit of what can be claimed.

## Approval levels

- `--approve` confirms the exact reviewed plan.
- `--approve-high-risk` is additional approval for financial, payroll, bank-feed, destructive, bulk, file, auth, billing, legal, tax, employment, and similar effects.
- `--ack-no-snapshot` confirms that Xero offers no reliable before-state for that exact action.

These are separate decisions. One flag never silently stands in for another.

## What a receipt does not prove

An accepted response does not automatically mean an invoice was posted, a payment was settled, payroll was completed, an email was delivered, a bank item was reconciled, or a legal or tax obligation was satisfied. The receipt uses `accepted_not_stronger_state` unless stronger evidence is available.

## Rollback

There is no generic rollback. Some Xero actions can be corrected with another reviewed fixed command, while others cannot be safely undone. The tool never auto-rolls back and never promises restore behavior that the exact API operation does not provide.
