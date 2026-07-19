# Extending the Twilio command surface

The pinned official OpenAPI checkout owns the operation boundary. Current official Twilio documentation and Twilio-owned product schemas may supply missing request typing for an operation already in that boundary. Do not hand-add a route or work around the catalog with a raw request path.

## Update the boundary

1. Choose and record a new official `twilio/twilio-oai` commit.
2. Review added, removed, versioned, preview, access-gated, deprecated, and end-of-life operations before generating anything.
3. Update the pinned commit, manual contract evidence, and disposition policy in `openapi_inventory.py`.
4. Regenerate the catalog and coverage together:

```bash
.venv/bin/python scripts/generate_twilio_inventory.py \
  --spec-root /path/to/pinned/twilio-oai
```

5. Inspect the count change and every non-command disposition in `docs/api_coverage.md`.
6. Update behavior tests, examples, public docs, and the tracked skill wrapper when the user-visible contract changes.

Never edit `docs/api_coverage.md` or the packaged catalog by hand. They are two views of the same generated inventory.

The next time-bound review is Frontline. Its two operations remain for existing customers, but Twilio is retiring Frontline on September 30, 2026. Regenerate the official boundary and decide their post-retirement disposition before that date.

## Preserve fixed inputs

The request builder must continue to reject unknown top-level sections, parameters, body fields, read-only fields, and content types. New auth handling must come from a declared operation security scheme or declared Authorization header.

Do not accept arbitrary URLs, methods, headers, SDK calls, or TwiML programs as a shortcut. If the pinned request is incomplete, inspect current official Twilio docs and Twilio-owned product schemas. Add a manual supplement only when they define a fixed operation-specific request contract, record the evidence and restrictions, and add behavior tests. Otherwise use the exact playbook-approved non-command disposition that the evidence supports.

Flexible JSON is allowed only inside the exact named field and operation where Twilio documents it. Stringified JSON in form fields must be parsed, checked for the documented object or array shape and size, and recursively redacted. Known nested fields remain typed. Do not use an example, a different API version, or a product schema to expose an undocumented optional branch.

## Preserve the write contract

Any new effectful operation must validate its fixed request before planning, remain plan-first, bind to the exact account and input, and require the right category acknowledgements. Apply must create a new protected receipt before HTTP, refuse an existing or unwritable path, make no automatic write retry, and preserve `succeeded`, `failed`, or `uncertain` attempt status. Add a paired read only when the server and literal path match exactly; otherwise keep the provider response as the available check.

Run the focused inventory and behavior tests before the complete local suite. Live Twilio requests require separate approval and suitable credentials; they are not a normal extension test.
