# Batches (bulk operations)

This tool intentionally avoids a generic “jobs runner” today. Instead, it provides focused batch commands with strict safety gates.

## Bulk lead injection

The main batch workflow is `leads add-bulk`:

1) Dry-run plan (no API calls):

```bash
instantly-api-tool --output json leads add-bulk --campaign-id CAMPAIGN_ID --csv examples/leads.csv
```

2) Apply status:

```bash
instantly-api-tool --output json --apply --yes leads add-bulk --campaign-id CAMPAIGN_ID --csv examples/leads.csv
```

Safety notes:
- Live apply currently requires explicit no-snapshot approval before HTTP because the tool cannot capture before-state for newly injected leads yet.
- Chunk size is enforced (`--chunk-size` must be `<= 1000`).
- If your input contains more than `--chunk-size` leads, the tool splits it into multiple API calls.
- The tool writes a plan on dry-run and a receipt on apply when the command is write-capable (see `docs/command_reference.md`).
