# Jobber test record

## November 22, 2026 offline checks

The local catalog copy passed 42 tests and 6 subtests. A fresh Python 3.12 environment installed the built wheel and ran help, version, and `schema summary`. The installed command list matched the checkout file and loaded 384 reads, 596 writes, and 46 webhook topics.

The installed CLI reported when no connection was available, read a sample account using a simulated reply, and saved a CSV preview without applying it. The checks made zero external requests. The `jobber` skill wrapper and local links passed. Five overlapping files were combined, bringing the folder from 68 files to 63.

Commands included `python -m pytest -q` and `python -m pip wheel --no-deps --no-index --no-build-isolation`. These checks cover the local package.

## June 12, 2026

The checkout recorded 59 passing tests for CLI output, auth helpers, named operations, write previews, approval flags, CSV jobs and webhook helpers. Its workflow checks and `git diff --check` also passed. The tests used sample data and API version `2025-04-16`.

## Installation checks

These commands only read local package data:

```bash
qwayk-jobber-safe-agent-cli --help
qwayk-jobber-safe-agent-cli --output json --version
qwayk-jobber-safe-agent-cli --output json schema summary
```

For an authorized read from a connected account, follow [Check a Jobber account](quickstart.md). Keep live changes out of install checks. See [Review a Jobber change](safety_model.md) for the approval process.

## Example results

These files show what the CLI returns. They use sample data.

- [Version](examples/outputs/version.json)
- [Connection check](examples/outputs/auth_check.json)
- [Plan](examples/plan.example.json)
- [Receipt](examples/receipt.example.json)

The [coverage guide](api_coverage.md) lists the included commands. [Official Jobber docs](references.md)
