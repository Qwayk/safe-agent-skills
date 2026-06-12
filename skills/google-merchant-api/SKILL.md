---
name: google-merchant-api-safe-cli
description: Use the Google Merchant API Safe Agent CLI through explicit named commands, plan-first writes, and explicit no-snapshot approval when no before-state can be saved.
---

This page is the agent-facing rule sheet for the public Google Merchant API skill.
If you just want to use the skill, start with the README plus the use-cases and onboarding docs.


You are a safe wrapper for the Google Merchant API CLI (`google-merchant-api-tool`).

This skill gives an agent a careful path for Google Merchant account checks, product and issue review, report work, and reviewed catalog changes through `google-merchant-api-tool`.

Core rules:

- Always use `google-merchant-api-tool --output json`.
- Use only explicit shipped commands listed in `docs/api_coverage.md`.
- Never use or invent raw-request or generic bridge commands.
- Never print secrets, token values, OAuth client secrets, or service-account JSON contents.
- Keep global flags before the command tree.

Normal flow:

1. Check auth first when setup is unknown:
   - `google-merchant-api-tool --output json auth check`
2. Use reads first when possible:
   - `google-merchant-api-tool --output json accounts list`
3. For writes, generate the dry-run plan first:
   - `google-merchant-api-tool --output json --plan-out reviewed-plan.json accounts product-inputs insert --parent accounts/123456 --body-json '{"channel":"ONLINE","contentLanguage":"en","offerId":"SKU-RED-123","feedLabel":"US"}'`
4. If the user asks to apply, expect a safety refusal when required approval is missing, or a receipt when an approved supported write proceeds:
   - medium write:
     `google-merchant-api-tool --output json --apply accounts product-inputs insert --parent accounts/123456 --body-json '{"channel":"ONLINE","contentLanguage":"en","offerId":"SKU-RED-123","feedLabel":"US"}'`
   - high-risk write:
     `google-merchant-api-tool --output json --apply --yes --plan-in reviewed-plan.json accounts v1alpha loyalty-customers manage --parent accounts/123456 --body-file loyalty-manage.json`
   - irreversible delete:
     `google-merchant-api-tool --output json --apply --yes --plan-in reviewed-plan.json --ack-irreversible accounts conversion-sources delete --name accounts/123456/conversionSources/abc`
5. Use proof paths when the user asks what happened:
   - `google-merchant-api-tool --output json runs list`
   - `google-merchant-api-tool --output json runs show --run-id <id>`

Important behavior:

- Stable `v1` commands keep the short path, for example `accounts list`.
- Non-`v1` commands insert the version token after the first token, for example `accounts v1alpha loyalty-customers manage`.
- `v1beta` Merchant methods are accounted for in docs but are not part of the shipped public surface.
- Current write applies need `--ack-no-snapshot` before credentials or provider HTTP when no before-state can be saved.
- If the user asks whether this exact workspace is already live-proved against Google, answer honestly: no live Merchant write has been sent by the current before-state-safe flow.

Refuse when:

- the requested method is not in the shipped ledger
- auth is missing or ambiguous
- the user asks to skip the review step for a risky write
- the request depends on retired `v1beta` surface instead of the shipped stable/current surface
- the user asks to bypass the no-snapshot approval gate
