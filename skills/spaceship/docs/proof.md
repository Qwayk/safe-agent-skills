# What we tested

## November 23, 2026 local checks

Fresh installs of both local copies loaded 41 commands and passed 66 offline tests. The simulated replies checked the price and term, a changed account, separate plan and receipt paths, a lost reply, an async ID saved for follow-up, a second attempt, and new transfers and SafePay deals with no earlier record. The SafePay checks caught a different domain or amount and showed which party still needed to confirm.

Both copies passed Ruff and mypy. All local guide links and four sample JSON files worked. Both archives have the right skill file and the wheels include the CLI. The public archive now includes its top-level skill instructions.

## August 1, 2026

Version `0.1.0` passed 65 source tests with Python 3.12.13. Ruff, mypy across 32 source and test files, and Python compilation passed. The wheel and source archive built and passed the privacy checks. The installed wheel loaded 40 named API commands, including two that returned HTTP 501 locally.

The simulated replies checked the fixed host, disabled redirects, path encoding, query limits, sold-domain cursors and date filters, and private output. The tests covered a renewal plan without credentials, the required approvals, stale state, HTTP 204, and HTTP 202 with an operation ID. They also checked that private values stayed out of plans, receipts, logs, and run history, and that run IDs could not create files outside their folder.

The [August coverage](api_coverage.md) and [source hashes](references.md) preserve the original API boundary. Those tests used simulated Spaceship replies.

## Repeat the checks

```bash
python -m unittest discover -s tests -q
ruff check src tests
mypy src
```

The [example plan](examples/plan.example.json) and [example receipt](examples/receipt.example.json) use sample values. Account access, exact costs, rate limits, and completed changes in Spaceship require separate live checks.
