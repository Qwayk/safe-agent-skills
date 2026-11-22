# Pinterest test results

## November 23, 2026 local checks

Both local copies passed 95 tests from source and again after building and installing a wheel in a fresh environment. Both command-line installs reported version 0.1.0. The skill files and local links passed their checks. The tests ran with network access disabled and used no Pinterest credentials.

- Each settings file used its own token file. The explicit token took priority. Importing an old file left the original in place. A renewal used the saved refresh token and kept the returned token out of the output.
- A board’s pin list resumed after the last pin returned. The section preview could read the existing section.
- Board and pin previews saved the account and the exact request. Missing approval, a changed title or link, or a different account stopped the tested writes. The tool read back the board or pin after applying.
- A simulated server error sent the create request once. The tool told the operator to check Pinterest before trying again.

The type check still reports three earlier findings in `config.py`, `cli.py`, and `commands/ads.py`. The live account, app permissions, and Pinterest’s response to real writes still need separate verification.

## Earlier checks

The local docs and commands were checked on June 11, 2026. The earlier local test baseline was February 3, 2026. These examples are from that work.

- [Version](examples/outputs/version.json)
- [Error](examples/outputs/error.json)
- [Sample plan](examples/plan.example.json)
- [Missing-approval example](examples/receipt.example.json)

Run `python3 -m unittest -q` from the tool folder after installing it. JSON mode emits one object to stdout, including errors and version output.
