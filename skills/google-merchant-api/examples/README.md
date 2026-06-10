# Examples folder notes

This folder contains local helper files and a small legacy quarantine area.

## What is active

- The real customer-facing proof examples live under `docs/examples/`.
- The shipped CLI surface is the explicit Merchant command tree documented in `docs/api_coverage.md`.

## What is quarantined

- `jobs.csv`
- `jobs_with_write.csv`

Those two CSV files are archival template leftovers only. They are not runnable public commands, they are not part of the customer skill wrapper, and they should not be used to describe the current product.
