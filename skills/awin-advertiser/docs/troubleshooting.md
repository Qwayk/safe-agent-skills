# Troubleshooting

When Awin Advertiser stops or returns an error, start with the boring checks first: setup, account access, target IDs, API limits, and the tool's safety gates. That usually tells you whether the problem is local configuration, provider permissions, a bad request, or a write that correctly refused to run.

Keep the JSON error output. It is the best clue for an agent reviewing advertiser programs, publishers, transactions, and performance data, and it is safer than retrying commands blindly. For any write-related error, stop before retrying and confirm the needed approval or plan.

A good first troubleshooting ask is: "Read the Awin Advertiser error, explain what failed in plain English, tell me the safest next check, and do not retry any write or destructive action."

## Debug HTTP

- Use `--verbose` to print request and response status lines to stderr.
- Confirm `AWIN_API_TOKEN` is set and not expired.
- Confirm the command is using the right `AWIN_ADVERTISER_ID`.

## Debug JSON errors

- `--output json` gives structured errors without stack traces.
- Add `--debug` only when you need Python stack traces for unexpected runtime errors.

## Auth and endpoint mapping

Awin advertiser endpoints do not all use the token in the same place.

- `auth check`, `publishers list`, `transactions list`, `transactions by-ids`, `reports publisher`, and `reports campaign` use `Authorization: Bearer <token>` plus `accessToken=<token>`.
- `transactions jobs`, `offers create`, and `product-feeds upload` use `Authorization: Bearer <token>` only.
- `conversion orders create` uses `x-api-key: <token>` only.

If one command works and another fails, check the endpoint-specific auth rule before assuming the token is bad.

## Batch validation stops

`transactions batch validate` uses `Authorization: Bearer <token>` plus `accessToken=<token>` as the tool's deterministic choice for an auth-ambiguous Awin endpoint.

If batch validation fails:

- confirm the batch file matches the examples in `docs/examples/inputs/`
- confirm every operation has the required advertiser transaction fields
- run without `--apply` first and inspect the plan
- use `--apply --yes --ack-irreversible --plan-in <path>` only after the plan is reviewed

## Write refusals

Write commands are expected to refuse when approval is missing.

Common causes:

- missing `--apply`
- missing `--yes`
- missing `--ack-irreversible`
- missing or stale `--plan-in`

Do not treat a refusal as a broken tool. Treat it as a stop sign until the plan and approval flags are correct.

## Secrets

- Do not paste tokens or secret output.
- If you suspect a leaked secret, rotate it immediately and update `.env`.
