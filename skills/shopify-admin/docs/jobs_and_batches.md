# Jobs and batches

This tool does not ship a CSV “jobs runner” command.

If you need batching, prefer:
- generating plans one mutation at a time (reviewable), or
- using a small wrapper script in your own repo that shells out to explicit CLI commands.

## Safety rules

- Always default to dry-run (no `--apply`) when testing new mutations.
- Live mutation apply needs a reviewed plan. If no operation-specific saved snapshot is available, the CLI must require explicit no-snapshot approval and record that limit in the receipt.
- Never log/store tokens.

## Plan files (recommended)

For any mutation, you can create a plan file in dry-run mode:

```bash
shopify-admin-api-tool mutation <operation-kebab> --vars vars.json --plan-out plan.json
```

Attempted apply from the saved plan requires explicit no-snapshot approval before Shopify HTTP when no operation-specific saved snapshot is available:

```bash
shopify-admin-api-tool --apply --yes --plan-in plan.json mutation <operation-kebab> --vars vars.json
```
