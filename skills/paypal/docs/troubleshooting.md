# Troubleshooting

When PayPal stops or returns an error, start with the boring checks first: setup, account access, target IDs, API limits, and the tool's safety gates. That usually tells you whether the problem is local configuration, provider permissions, a bad request, or a write that correctly refused to run.

Keep the JSON error output. It is the best clue for an agent reviewing orders, payments, captures, refunds, subscriptions, and account activity, and it is safer than retrying commands blindly. For any write-related error, stop before retrying and confirm the needed approval or plan.

A good first troubleshooting ask is: "Read the PayPal error, explain what failed in plain English, tell me the safest next check, and do not retry any write or destructive action."

## `auth check` failed

Check these first:

- `PAYPAL_ENVIRONMENT` matches the credentials you copied
- `PAYPAL_CLIENT_ID` and `PAYPAL_CLIENT_SECRET` came from the same PayPal REST app
- you are using the PayPal Developer Dashboard app credentials, not a website login

Normal retry:

```bash
qwayk-paypal-safe-agent-cli --output json auth check
```

## A write returned a plan or refusal instead of executing

That is the normal safety behavior.

- generate and review the dry-run plan first
- request `--apply` only after review
- add `--yes` for actions that require it, such as `payment-tokens delete`, `disputes accept-claim`, or `payments authorizations.void`
- do not add `--ack-irreversible` unless the shipped command surface grows a command that actually requires it

If the tool returns:

```json
{"ok": true, "refused": true, ...}
```

that means it safely refused before PayPal HTTP instead of guessing or writing anyway.

## A documented command still fails in your account

Some PayPal products need extra account approval, partner setup, or real merchant data.
This is most common with:

- partner referrals
- payouts
- referenced payouts
- disputes
- transaction reporting

Check the notes in `docs/api_coverage.md` and `docs/proof.md`.

## A `POST` command does not ask for `--apply`

That can be correct.
Some PayPal endpoints use `POST` for query or verification work, not writes.

Examples:

- `invoicing search-invoices`
- `pricing quote-exchange-rates`
- `webhooks verify-webhook-signature`

## Debug HTTP

Use `--verbose` to print request start/end lines to stderr.
The tool must never print Authorization headers or token values.

## Debug Python errors

By default the tool prints one JSON error object.
If you need a stack trace while developing, add `--debug`.
