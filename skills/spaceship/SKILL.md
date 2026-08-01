---
name: spaceship
description: Use the Qwayk Spaceship tool for documented domain, DNS, contact, transfer, personal-nameserver, SellerHub, checkout-link, SafePay, and async-operation work.
---

# Spaceship

Use `qwayk-spaceship-safe-agent-cli --output json` for the actual work.

Read the public `README.md`, `docs/use_cases.md`, `docs/safety_model.md`, and `docs/command_reference.md` before the first account task.

## Start with a read

Use one of the fixed documented read commands to confirm the target and current state. A good first action is `domains list --take 10` or `domains check-availability <domain>`.

Explain the result in normal words. Mask contact details, contact attributes, transfer authorization codes, SafePay parties and identifiers, and checkout links. Never repeat `SPACESHIP_API_KEY` or `SPACESHIP_API_SECRET`.

## Prepare every write first

Create a saved plan and review the exact target, request-body digest, critical request fields, snapshot or warning, risk categories, and `required_acknowledgements`. Use `--plan-out` when you need a specific plan path.

If no explicit output path is needed, use the automatic `.state/runs/<run_id>/plan.json` and `receipt.json` files. Use one non-empty local name for the run ID; refuse absolute paths, slashes, backslashes, `.` and `..`. Persisted command displays hash contact and SafePay transaction identifiers. Never repeat billing contact IDs or opaque private error text. For sold-domain reads, keep `take` within 1–100, use the official `cursor`, and preserve `--sale-date-time-from` and `--sale-date-time-to` when supplied.

Apply only after the user approves that exact plan. Use `--apply --yes --plan-in <path>` with every acknowledgement listed by the plan. High-risk plans can require `--ack-spend`, `--ack-ownership`, `--ack-dns-risk`, `--ack-financial`, `--ack-destructive`, `--ack-private-data`, or `--ack-no-snapshot`.

After apply, report whether Spaceship completed the request, accepted it for processing, or left final state unverified. Preserve `spaceship-async-operationid`; HTTP 202 means accepted, not completed. Use `async-operations status <operationId>` for a later status read.

## Refuse unsafe or unavailable work

Refuse any generic or undocumented request, a host other than `https://spaceship.dev/api`, a redirect response, a vague target, a changed plan, missing confirmation, missing acknowledgement, or a request to reveal secrets or raw private values. Never follow a redirect or resend the custom credential headers to another host.

Always refuse these two commands locally without a provider call:

- `domains delete <domain>`
- `domains personal-nameservers get-host <domain> <currentHost>`

Spaceship documents both as under development with HTTP 501.

Live Spaceship behavior remains unverified in this source build because no credential or provider request was used.
