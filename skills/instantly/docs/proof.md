# Instantly test results

## November 22, 2026

This local update passed 124 tests from the checkout and 124 after installing a wheel built from the source archive. The installed CLI opened help and reported version 0.6.0. The archive included the skill, guides and working examples. The CLI still listed all 168 commands, the skill passed validation, and all 35 local links worked.

The tests used simulated replies. They checked the selected settings file and its permissions, the key used for a saved plan, the status returned after starting or pausing a campaign, and the saved batch counts and request keys after a lost import reply. No live Instantly calls were made.

## June 4, 2026

The June 4 check ran `.venv/bin/python -m unittest -q` for CLI 0.6.0 against simulated Instantly API v2 replies. All 118 tests passed. It made no live calls.

## Saved examples

These examples show the output from that earlier version. Make a new preview with the current tool before applying a change.

- [Version](examples/outputs/version.json)
- [Connection check](examples/outputs/auth_check.json)
- [Plan](examples/plan.example.json)
- [Receipt](examples/receipt.example.json)

## Repeat the checks

Run `python -m unittest -q` from the tool folder after installing it. The suite uses simulated replies. To check what ships, build the source archive, build a wheel from that archive and install the wheel into a fresh environment. Run `instantly-api-tool --version` and `instantly-api-tool --help` outside the checkout.

A real connection check needs an Instantly key with the right permissions. See [setup](onboarding.md), [command coverage](api_coverage.md) and the [provider docs](references.md).
