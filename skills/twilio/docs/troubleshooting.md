# Troubleshooting

## The tool says credentials are missing

Run the local check first:

```bash
qwayk-twilio-safe-agent-cli auth check
```

For normal Basic-auth commands, set the Account SID plus both API key values. A key SID without its secret is refused. If you use the Account Auth Token fallback, expect a warning.

An OAuth-only command needs `TWILIO_OAUTH_ACCESS_TOKEN`; that token does not replace Basic credentials for other commands.

## Region or edge is refused

Set `TWILIO_REGION` and `TWILIO_EDGE` together, and use credentials valid in that region. The tool refuses only one value and refuses routed hosts outside `twilio.com`.

## The command rejects an input field

Check the exact command help and its row in [API coverage](api_coverage.md). Input names and capitalization must match the pinned Twilio specification. The tool deliberately rejects unknown sections, parameters, body fields, read-only fields, and content types.

Do not work around the error with a raw request. First check `inventory show` and the operation's row in API coverage. Some commands intentionally expose a documented safe subset, so an optional field shown in another SDK or example may still be refused. If the current official contract still cannot support the field safely, report it as a boundary gap.

## A read produced a plan

Some `GET` requests create cost. `lookups-v2 fetch-phone-number` is the common example. Review the plan, then apply it only with the required spend acknowledgement. This is expected behavior, not a failed read.

## Apply says the plan does not match

The command, account, region, edge, input, catalog, tool version, or snapshot changed after planning. Do not edit the plan. Generate a new plan from the exact intended input and review it again.

## Apply asks for more approval

Read `required_acknowledgements` in the plan. `--apply --yes` is not enough for contact, spend, bulk, destructive, access, identity, production, preview, or no-snapshot risk. Bulk work also needs the exact target list in the validated body and `--target-count` equal to the derived list length, from 1 to 25.

If a bulk plan is refused before approval, check that the command's declared target list exists and has no more than 25 entries. The tool refuses a missing list, an input it cannot count exactly, or a mismatched count.

## Twilio accepted the request but the result is not delivered

Accepted, queued, scheduled, sending, sent, completed, delivered, and read are different provider states. The tool reports the state Twilio returned. Check the receipt and the appropriate Twilio status resource or callback before claiming delivery.

## Apply cannot create the receipt

Choose a new writable path for `--receipt-out`. The tool creates the mode-`600` receipt before HTTP and refuses to overwrite any existing file. This protects old evidence and ensures a request cannot start without a place to record an uncertain outcome.

## The receipt says uncertain

No provider response arrived. Do not assume the request failed, and do not retry automatically. Check the relevant Twilio resource, logs, or status system first. A `failed` receipt means Twilio returned a non-2xx response; `succeeded` means Twilio returned 2xx, not that delivery or the final business result is complete.

## You need more request detail

Add global `--verbose` before the command group. It prints only the HTTP method, Twilio hostname, and status to stderr. It does not print headers, query values, or bodies.

Use `--debug` only while debugging the local Python code. A traceback may include local file paths; keep it out of public logs. Normal JSON output remains one object.

## A preview or entitlement-gated command fails

The command may be correctly generated but unavailable to the current account, region, or product entitlement. Live preview behavior was not proved in this build. Confirm access with Twilio; do not substitute another endpoint or claim support from local tests alone.

Frontline is a known time-bound case. Its two commands are for existing Frontline customers only. The product is end-of-sale and scheduled to retire on September 30, 2026; a new or non-entitled account should not expect access.
