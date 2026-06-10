# Historical note about jobs and batches

There is no public `jobs` or CSV batch command in the shipped Merchant CLI.

This page exists only to quarantine older template expectations and to explain the current product rule:

- use explicit named Merchant commands only
- orchestrate multi-row work outside the CLI, one explicit command per item
- keep the current safety loop for each write: plan, review, explicit no-snapshot approval, audit summary

If you need batch-style work, build it around the shipped explicit commands from `docs/command_reference.md` and keep `docs/api_coverage.md` as the source of truth for what is actually supported.
