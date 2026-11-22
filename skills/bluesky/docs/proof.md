# Bluesky test results

## November 23, 2026 local checks

The source and local catalog copies each passed 29 tests from the checkout and 29 again after installing a wheel built from a fresh source archive. The installed command ran `--version`, `api ops list` and `onboarding` outside the checkout. Each install loaded all 304 commands and created a settings file with both sign-in fields. The type check passed for 22 source files in each copy. Ruff still reports eight formatting issues in files outside this edit.

Fake Bluesky replies and a network block showed the following.

- The public feed used a GET request with no token, even after an app password was set locally. `auth check` left sign-in to `auth login`. Sign-in, the account check, refresh and the signed-in feed read used the expected servers.
- Missing approval, a missing plan, edited text and a changed server each stopped the post before HTTP. An account mismatch stopped the write after a read-only account check.
- With the reviewed plan and approval present, the tool sent the same request to the same server. The receipt recorded the plan hash, `--ack-no-snapshot`, the URI and the content ID. A separate `getRecord` read returned that same URI, content ID and text. The receipt marked automatic verification as skipped.

These were local checks with no live Bluesky requests. See the [commands used for reading and checking a post](quickstart.md).

## June 4, 2026 record

The earlier record listed CLI version `0.1.0`, an auth check, a profile preview and live read command, and a command list check. The May 25 inventory counted 222 HTTP reference pages and 82 commands documented only in the lexicons. [API coverage](api_coverage.md)

The saved examples from that record are still here.

- [Version](examples/outputs/version.json)
- [Account check](examples/outputs/auth_check.json)
- [Plan](examples/plan.example.json)
- [Refusal when approval was missing](examples/receipt.example.json)
