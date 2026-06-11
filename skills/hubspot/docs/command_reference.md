# Command reference

Use this page when you need the exact HubSpot command, flag, or safety rule.
If you want the plain-English path first, start with [What you can do](use_cases.md), [Connect your account](onboarding.md), and [Quickstart](quickstart.md).

## Global flags

- `--version`
- `--config <path>`
- `--project-dir <path>`
- `--env-file <path>` (default: `.env`)
- `--timeout-s <seconds>`
- `--verbose`
- `--debug`
- `--output json|text` (default: `json`)
- `--log-file <path>`
- `--apply`
- `--yes`
- `--plan-out <path>`
- `--plan-in <path>`
- `--receipt-out <path>`
- `--ack-irreversible`
- `--run-id <id>`
- `--artifacts-dir <path>`
- `--no-artifacts`

## Onboarding, auth, and runs

```bash
qwayk-hubspot-safe-agent-cli onboarding [--no-write-env]
qwayk-hubspot-safe-agent-cli auth check
qwayk-hubspot-safe-agent-cli auth token set --file token.json
qwayk-hubspot-safe-agent-cli auth token status
qwayk-hubspot-safe-agent-cli runs list [--limit <N>]
qwayk-hubspot-safe-agent-cli runs show --run-id <run-id>
```

Write commands are dry-run by default.
Use `--plan-out` only on the dry-run step.
Current `--apply` attempts for HubSpot writes require explicit no-snapshot approval before HubSpot HTTP when no saved snapshot is available.
Add `--yes` for batch or high-risk writes.
Add `--ack-irreversible` for archive, delete, merge, cancel, or other hard-to-undo actions.
Use `--plan-in` only on commands that require replay from a reviewed saved plan.
This tool does not use snapshots, provider backups, or automatic rollback.

## HubSpot command surface

Every HubSpot API action uses:

```bash
qwayk-hubspot-safe-agent-cli hubspot <family> <action> ...
```

Examples with `--apply` show the required gate flags for that command. In the current Wave 2 state, those commands return a safety refusal and send no HubSpot write.

### object-library

```bash
qwayk-hubspot-safe-agent-cli hubspot object-library list-enablement
qwayk-hubspot-safe-agent-cli hubspot object-library get-enablement --object-type services
```

### objects

```bash
qwayk-hubspot-safe-agent-cli hubspot objects list --object-type contacts --limit 10
qwayk-hubspot-safe-agent-cli hubspot objects get --object-type contacts --object-id 123
qwayk-hubspot-safe-agent-cli hubspot objects batch-read --object-type contacts --body-file body.json
qwayk-hubspot-safe-agent-cli hubspot objects search --object-type contacts --body-file search_body.json
qwayk-hubspot-safe-agent-cli --plan-out plan.json hubspot objects create --object-type contacts --body-file body.json
qwayk-hubspot-safe-agent-cli --apply hubspot objects create --object-type contacts --body-file body.json
qwayk-hubspot-safe-agent-cli --apply --yes --ack-irreversible hubspot objects archive --object-type contacts --object-id 123
qwayk-hubspot-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json hubspot objects gdpr-delete --object-type contacts --body-file body.json
```

### associations

```bash
qwayk-hubspot-safe-agent-cli hubspot associations create-default --from-object-type contacts --from-object-id 1 --to-object-type companies --to-object-id 2
qwayk-hubspot-safe-agent-cli hubspot associations list-record --from-object-type contacts --object-id 1 --to-object-type companies
qwayk-hubspot-safe-agent-cli --apply hubspot associations create-labeled --object-type contacts --object-id 1 --to-object-type companies --to-object-id 2 --body-file body.json
qwayk-hubspot-safe-agent-cli --apply --yes --ack-irreversible hubspot associations remove-record --object-type contacts --object-id 1 --to-object-type companies --to-object-id 2
qwayk-hubspot-safe-agent-cli --apply --yes hubspot associations batch-create-labeled --from-object-type contacts --to-object-type companies --body-file body.json
```

### association-labels

```bash
qwayk-hubspot-safe-agent-cli hubspot association-labels list --from-object-type contacts --to-object-type companies
qwayk-hubspot-safe-agent-cli --apply hubspot association-labels create --from-object-type contacts --to-object-type companies --body-file body.json
qwayk-hubspot-safe-agent-cli --apply hubspot association-labels update --from-object-type contacts --to-object-type companies --association-type-id 15 --body-file body.json
qwayk-hubspot-safe-agent-cli --apply --yes --ack-irreversible hubspot association-labels delete --from-object-type contacts --to-object-type companies --association-type-id 15
```

### association-limits

```bash
qwayk-hubspot-safe-agent-cli hubspot association-limits list-all
qwayk-hubspot-safe-agent-cli hubspot association-limits get --from-object-type contacts --to-object-type companies
qwayk-hubspot-safe-agent-cli --apply --yes hubspot association-limits batch-create --from-object-type contacts --to-object-type companies --body-file body.json
qwayk-hubspot-safe-agent-cli --apply --yes --ack-irreversible hubspot association-limits batch-purge --from-object-type contacts --to-object-type companies --body-file body.json
```

### properties

```bash
qwayk-hubspot-safe-agent-cli hubspot properties list --object-type contacts
qwayk-hubspot-safe-agent-cli hubspot properties get --object-type contacts --property-name email
qwayk-hubspot-safe-agent-cli --apply hubspot properties create --object-type contacts --body-file body.json
qwayk-hubspot-safe-agent-cli --apply hubspot properties update --object-type contacts --property-name my_prop --body-file body.json
qwayk-hubspot-safe-agent-cli --apply --yes --ack-irreversible hubspot properties archive --object-type contacts --property-name my_prop
```

### property-groups

```bash
qwayk-hubspot-safe-agent-cli hubspot property-groups list --object-type contacts
qwayk-hubspot-safe-agent-cli hubspot property-groups get --object-type contacts --group-name contactinformation
qwayk-hubspot-safe-agent-cli --apply hubspot property-groups create --object-type contacts --body-file body.json
qwayk-hubspot-safe-agent-cli --apply --yes --ack-irreversible hubspot property-groups archive --object-type contacts --group-name my_group
```

### owners

```bash
qwayk-hubspot-safe-agent-cli hubspot owners list
qwayk-hubspot-safe-agent-cli hubspot owners get --owner-id 1234
```

### pipelines

```bash
qwayk-hubspot-safe-agent-cli hubspot pipelines list --object-type deals
qwayk-hubspot-safe-agent-cli hubspot pipelines get --object-type deals --pipeline-id default
qwayk-hubspot-safe-agent-cli --apply --yes hubspot pipelines create --object-type deals --body-file body.json
qwayk-hubspot-safe-agent-cli --apply --yes --ack-irreversible hubspot pipelines archive --object-type deals --pipeline-id default --validate-references-before-delete --validate-deal-stage-usages-before-delete
```

### pipeline-stages

```bash
qwayk-hubspot-safe-agent-cli hubspot pipeline-stages list --object-type deals --pipeline-id default
qwayk-hubspot-safe-agent-cli hubspot pipeline-stages get --object-type deals --pipeline-id default --stage-id appointmentscheduled
qwayk-hubspot-safe-agent-cli --apply hubspot pipeline-stages create --object-type deals --pipeline-id default --body-file body.json
qwayk-hubspot-safe-agent-cli --apply --yes --ack-irreversible hubspot pipeline-stages archive --object-type deals --pipeline-id default --stage-id appointmentscheduled
```

### schemas

```bash
qwayk-hubspot-safe-agent-cli hubspot schemas list --include-properties --include-associations --include-audit
qwayk-hubspot-safe-agent-cli hubspot schemas get --object-type p_custom_object --include-properties --include-audit
qwayk-hubspot-safe-agent-cli --apply --yes hubspot schemas create --body-file body.json
qwayk-hubspot-safe-agent-cli --apply --yes --ack-irreversible hubspot schemas archive --object-type p_custom_object
qwayk-hubspot-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json hubspot schemas hard-delete --object-type p_custom_object
```

### imports

```bash
qwayk-hubspot-safe-agent-cli hubspot imports list
qwayk-hubspot-safe-agent-cli hubspot imports get --import-id import-1
qwayk-hubspot-safe-agent-cli --apply --yes hubspot imports create --request-file import_request.json --file contacts.csv
qwayk-hubspot-safe-agent-cli hubspot imports errors --import-id import-1 --limit 25
qwayk-hubspot-safe-agent-cli --apply --yes --ack-irreversible hubspot imports cancel --import-id import-1
```

### exports

```bash
qwayk-hubspot-safe-agent-cli --apply --yes hubspot exports create --body-file body.json
qwayk-hubspot-safe-agent-cli hubspot exports status --task-id task-123
```

## Safe order for writes

1. Run a read-only check first, such as `qwayk-hubspot-safe-agent-cli auth check`.
2. Run the write command without `--apply`.
3. Review the returned `plan` or saved `plan.json`.
4. Do not expect a live write yet. `--apply` requires explicit no-snapshot approval before HubSpot HTTP until before-state capture is added.
5. Save the run summary and audit log for proof of the plan or refusal.
