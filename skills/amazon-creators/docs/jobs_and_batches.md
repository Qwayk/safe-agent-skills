# Jobs and batches

This tool uses a safe loop for the remote catalog API and keeps loops simple:
- Catalog commands are read-only and use dry-run plan + apply flow.
- Local write helpers (`onboarding`, `auth token set`, `auth token fetch`) now plan and require approval before local file writes when no saved snapshot is available.

- Catalog commands emit a dry-run `plan` object by default and do not hit Amazon until you pass `--apply`.
- When `--apply` is used, the CLI calls the catalog API, returns simplified output, and writes a `receipt`.
- For local write helpers, dry-run plans and blocked apply refusals are the current safe behavior.

Example flow:
1. Dry run to verify plan:
   ```bash
   amazon-creators-api-tool --output json items get \
     --item-id "Z123" \
     --resource-preset book-media
   ```
2. Apply to fetch live data:
   ```bash
   amazon-creators-api-tool --output json items get \
     --item-id "Z123" \
     --resource-preset book-media \
     --apply
   ```
3. Review the local token-helper plan if needed:
   ```bash
   amazon-creators-api-tool --output json auth token fetch
   ```

Use run history for validation:
- `runs list` and `runs show` cover catalog and local-helper commands.
- Inspect stored plans, catalog receipts, and blocked-helper refusal output under `.state/runs/<run_id>/` when artifacts are enabled.
