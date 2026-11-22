---
name: plausible-api-safe-cli
description: Read Plausible traffic and goals, run reports, and prepare site or event changes for approval.
---

Use `plausible-api-tool --output json` for Plausible traffic, goals, sites and event work. Start with the site and period the user wants. Use the Stats API for reads and the Events API only for an approved event send. Keep keys out of chat and command examples.

## Read traffic

1. Run `plausible-api-tool --output json --env-file .env auth check` with the chosen settings file.
2. Use `plausible-api-tool --output json --env-file .env report weekly --days 7 --limit 50` for top pages, channels and goals. Use `report membership` for membership details.
3. Check the actual site, period and row counts before interpreting a result. If it is incomplete, use the next offset where needed. A missing goal is unavailable.
4. To check a query file without credentials, run `plausible-api-tool --output json stats validate --file QUERY.json`.

## Prepare and check changes

- Show a dry-run plan using `--plan-out PATH` and wait for approval. Use `--apply --yes` for writes and follow the command's additional approval flags.
- Event sends need `--ack-irreversible` and `--ack-no-snapshot` as well as apply approval. Shared-link creation needs `--ack-no-snapshot` when there is no saved previous state.
- Save the receipt with `--receipt-out PATH`. Check the reported result and the `recovery` field before claiming a change was confirmed or can be undone. A site update lists the requested fields and the values Plausible returned. Event verification is a best-effort check.
- Use the named CLI commands and exact flags in the tool's `docs/command_reference.md`. Read `docs/onboarding.md` for setup and `docs/safety_model.md` for the approval and recovery rules.
