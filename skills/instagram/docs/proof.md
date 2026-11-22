# Instagram test results

## November 23, 2026 local checks

Both local copies passed 34 tests before and after installing a wheel built from a fresh source archive. The installed `instagram-api-tool --version` worked outside the checkout. Both skill files passed validation. The type check passed for 27 source files, and four existing import formatting warnings remain.

Fake Instagram replies covered the following steps.

- Onboarding created a settings file in a new directory. A user token alone was enough to check the professional account and read recent posts, including the next-page cursor.
- The sign-in reply in Meta’s documented `data` format saved a usable token. Earlier files in that format could also be read. Sign-in, exchange and refresh kept codes and tokens out of output and run records. A bad reply left the existing token in place.
- Draft creation stopped for missing approval, a missing plan, a changed caption, a different API version or a different account. Both carousel items sent the item flag. The final carousel used the approved pair of item IDs.
- Publishing stopped if the account or draft ID changed. A separate read confirmed the published post and its caption. A missing post ID, a failed read or a lost reply stayed unconfirmed without a resend.

The checks made zero live Instagram requests. [Quickstart](quickstart.md) · [API coverage](api_coverage.md)

## June 4, 2026 record

Local checks covered `instagram-api-tool` 0.1.0 on Graph API `v25.0` at `https://graph.instagram.com`. The record included the version, token status without values, missing-token errors, sign-in error handling, and refusal before an unapproved write. The suite ran with `.venv/bin/python -m unittest -q`.

These saved examples show earlier output. Use the quickstart for today’s commands.

- [Version](examples/outputs/version.json)
- [Account check](examples/outputs/auth_check.json)
- [Draft plan](examples/plan.example.json)
- [Refusal when approval was missing](examples/receipt.example.json)
