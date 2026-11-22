# Threads test results

## November 23, 2026 local checks

Both local copies of `threads-api-tool` passed 65 tests from the source and again after installing a wheel built from a fresh source archive. `--version` worked outside the checkout. Both skill files passed validation, and the type check passed for 26 source files. Nine older code style warnings remain in files outside this edit.

With fake Threads replies, I checked these steps.

- Onboarding created a settings file in a new directory. A user token alone was enough to check the account and read recent posts, including the next-page cursor.
- Missing approval, a missing plan, changed text, a different API version and a different signed-in account each blocked draft creation. Publishing also stopped when the account or draft ID changed.
- A separate read confirmed the ID and text after publishing. A missing post ID, failed post read and lost publish reply each stayed unconfirmed. None caused a resend. The draft status command returned the processing error supplied by Threads.
- Fake sign-in codes and tokens stayed out of command output, saved plans, receipts, audit logs and run history. Approved token changes saved the token only in the local token file.

The checks made zero live Threads requests. [Quickstart](quickstart.md) · [Permission and API coverage](api_coverage.md)

## May 26 and June 4, 2026 records

On May 26, local checks confirmed the version output, the JSON error for a missing token, named read commands and draft previews with the documented media type. The draft command used for the preview was `PYTHONPATH=src python3 -m threads_api_tool --output json --plan-out /tmp/threads.plan.json posts create-text --threads-user-id demo-user --text Draft`.

On June 4, `.venv/bin/python -m unittest -q` passed 66 tests for tool version `0.1.0` and Threads API `v1.0`. That record covered approval before a write when the tool could not save the previous state.

These saved examples are from the earlier checks.

- [Version](examples/outputs/version.json)
- [Account check](examples/outputs/auth_check.json)
- [Draft plan](examples/plan.example.json)
- [Refusal when approval was missing](examples/receipt.example.json)
