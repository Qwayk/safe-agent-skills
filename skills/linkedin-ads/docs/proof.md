# What has been checked

## November 23, 2026 local checks

The source and local catalog copies each passed all 24 tests with `python -m unittest -q`. I built a Python source archive and wheel from each copy, installed each wheel in a fresh virtual environment with local dependencies available, and reran the 24 tests against each install. All 177 API commands in 42 families loaded in both installs.

The installed tools ran the [quickstart](quickstart.md) with simulated LinkedIn replies. Setup accepted an alternate token setting, the account check returned a role, and the campaign report used the account and both dates shown in the guide. The tool saved a campaign pause plan and refused to send it before explicit approval to proceed without a saved copy. With the required flags, it sent the partial-update header and saved LinkedIn's simulated reply. A separate read returned the new campaign status.

I validated both skill files. The type check passed. Ruff still reports 10 existing import and formatting findings. These checks used simulated replies, with zero attempts to contact LinkedIn.

## LinkedIn access still to check

The [coverage table](api_coverage.md) records which operations need app approval or account permissions (`access-gated`), a restricted LinkedIn product (`private-api-gated`), or a LinkedIn tier or role (`tier-gated`). `live-unverified` means the known command still needs a check against LinkedIn with approved access. A token and a successful account check alone do not establish access for reports, lead forms, conversions, or restricted products.

The restricted product checks include Company Intelligence, Ad Page Sets, ad segment sources and segments, Audience Insights, DMP engagement source types and segments, and Media Planning. Access depends on the specific app and account.

## Earlier checks and sample files

The earlier local check recorded 22 passing tests. It covered version output, onboarding and token commands, write plans and approval refusals, JSON errors, and local run history. The saved examples below show earlier output with sample values. Their timestamps and commands are kept as recorded. To run the current commands, use the [quickstart](quickstart.md).

- [Version response](examples/outputs/version.json)
- [Account check response](examples/outputs/auth_check.json)
- [Saved plan](examples/plan.example.json)
- [Write refusal](examples/receipt.example.json)
