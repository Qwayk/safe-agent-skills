# HubSpot commands

Use this page for exact commands and options. Start with [account setup](onboarding.md) and [a first read](quickstart.md).

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
- `--ack-no-snapshot`
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

Use `--plan-out` to save a preview. After you approve the change, `--apply --ack-no-snapshot` sends it without a saved copy of the old data. Add the other flags shown for that command. For imports, bulk changes, and certain permanent deletions, pass the reviewed preview with `--plan-in`. [Full review steps](safety_model.md)

## HubSpot command surface

Every HubSpot API action uses:

```bash
qwayk-hubspot-safe-agent-cli hubspot <family> <action> ...
```

The examples with `--apply` can send real changes. First run the command without the approval flags and save the preview when the command needs one.

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
qwayk-hubspot-safe-agent-cli --apply --ack-no-snapshot hubspot objects create --object-type contacts --body-file body.json
qwayk-hubspot-safe-agent-cli --apply --ack-no-snapshot --yes --ack-irreversible hubspot objects archive --object-type contacts --object-id 123
qwayk-hubspot-safe-agent-cli --apply --ack-no-snapshot --yes --ack-irreversible --plan-in plan.json hubspot objects gdpr-delete --object-type contacts --body-file body.json
```

### associations

```bash
qwayk-hubspot-safe-agent-cli hubspot associations create-default --from-object-type contacts --from-object-id 1 --to-object-type companies --to-object-id 2
qwayk-hubspot-safe-agent-cli hubspot associations list-record --from-object-type contacts --object-id 1 --to-object-type companies
qwayk-hubspot-safe-agent-cli --apply --ack-no-snapshot hubspot associations create-labeled --object-type contacts --object-id 1 --to-object-type companies --to-object-id 2 --body-file body.json
qwayk-hubspot-safe-agent-cli --apply --ack-no-snapshot --yes --ack-irreversible hubspot associations remove-record --object-type contacts --object-id 1 --to-object-type companies --to-object-id 2
qwayk-hubspot-safe-agent-cli --apply --ack-no-snapshot --yes --plan-in plan.json hubspot associations batch-create-labeled --from-object-type contacts --to-object-type companies --body-file body.json
```

### association-labels

```bash
qwayk-hubspot-safe-agent-cli hubspot association-labels list --from-object-type contacts --to-object-type companies
qwayk-hubspot-safe-agent-cli --apply --ack-no-snapshot hubspot association-labels create --from-object-type contacts --to-object-type companies --body-file body.json
qwayk-hubspot-safe-agent-cli --apply --ack-no-snapshot hubspot association-labels update --from-object-type contacts --to-object-type companies --association-type-id 15 --body-file body.json
qwayk-hubspot-safe-agent-cli --apply --ack-no-snapshot --yes --ack-irreversible hubspot association-labels delete --from-object-type contacts --to-object-type companies --association-type-id 15
```

### association-limits

```bash
qwayk-hubspot-safe-agent-cli hubspot association-limits list-all
qwayk-hubspot-safe-agent-cli hubspot association-limits get --from-object-type contacts --to-object-type companies
qwayk-hubspot-safe-agent-cli --apply --ack-no-snapshot --yes --plan-in plan.json hubspot association-limits batch-create --from-object-type contacts --to-object-type companies --body-file body.json
qwayk-hubspot-safe-agent-cli --apply --ack-no-snapshot --yes --ack-irreversible --plan-in plan.json hubspot association-limits batch-purge --from-object-type contacts --to-object-type companies --body-file body.json
```

### properties

```bash
qwayk-hubspot-safe-agent-cli hubspot properties list --object-type contacts
qwayk-hubspot-safe-agent-cli hubspot properties get --object-type contacts --property-name email
qwayk-hubspot-safe-agent-cli --apply --ack-no-snapshot hubspot properties create --object-type contacts --body-file body.json
qwayk-hubspot-safe-agent-cli --apply --ack-no-snapshot hubspot properties update --object-type contacts --property-name my_prop --body-file body.json
qwayk-hubspot-safe-agent-cli --apply --ack-no-snapshot --yes --ack-irreversible hubspot properties archive --object-type contacts --property-name my_prop
```

### property-groups

```bash
qwayk-hubspot-safe-agent-cli hubspot property-groups list --object-type contacts
qwayk-hubspot-safe-agent-cli hubspot property-groups get --object-type contacts --group-name contactinformation
qwayk-hubspot-safe-agent-cli --apply --ack-no-snapshot hubspot property-groups create --object-type contacts --body-file body.json
qwayk-hubspot-safe-agent-cli --apply --ack-no-snapshot --yes --ack-irreversible hubspot property-groups archive --object-type contacts --group-name my_group
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
qwayk-hubspot-safe-agent-cli --apply --ack-no-snapshot --yes hubspot pipelines create --object-type deals --body-file body.json
qwayk-hubspot-safe-agent-cli --apply --ack-no-snapshot --yes --ack-irreversible hubspot pipelines archive --object-type deals --pipeline-id default --validate-references-before-delete --validate-deal-stage-usages-before-delete
```

### pipeline-stages

```bash
qwayk-hubspot-safe-agent-cli hubspot pipeline-stages list --object-type deals --pipeline-id default
qwayk-hubspot-safe-agent-cli hubspot pipeline-stages get --object-type deals --pipeline-id default --stage-id appointmentscheduled
qwayk-hubspot-safe-agent-cli --apply --ack-no-snapshot hubspot pipeline-stages create --object-type deals --pipeline-id default --body-file body.json
qwayk-hubspot-safe-agent-cli --apply --ack-no-snapshot --yes --ack-irreversible hubspot pipeline-stages archive --object-type deals --pipeline-id default --stage-id appointmentscheduled
```

### schemas

```bash
qwayk-hubspot-safe-agent-cli hubspot schemas list --include-properties --include-associations --include-audit
qwayk-hubspot-safe-agent-cli hubspot schemas get --object-type p_custom_object --include-properties --include-audit
qwayk-hubspot-safe-agent-cli --apply --ack-no-snapshot --yes hubspot schemas create --body-file body.json
qwayk-hubspot-safe-agent-cli --apply --ack-no-snapshot --yes --ack-irreversible hubspot schemas archive --object-type p_custom_object
qwayk-hubspot-safe-agent-cli --apply --ack-no-snapshot --yes --ack-irreversible --plan-in plan.json hubspot schemas hard-delete --object-type p_custom_object
```

### imports

```bash
qwayk-hubspot-safe-agent-cli hubspot imports list
qwayk-hubspot-safe-agent-cli hubspot imports get --import-id import-1
qwayk-hubspot-safe-agent-cli --plan-out plan.json hubspot imports create --request-file import_request.json --file contacts.csv
qwayk-hubspot-safe-agent-cli --apply --ack-no-snapshot --yes --plan-in plan.json hubspot imports create --request-file import_request.json --file contacts.csv
qwayk-hubspot-safe-agent-cli hubspot imports errors --import-id import-1 --limit 25
qwayk-hubspot-safe-agent-cli --apply --ack-no-snapshot --yes --ack-irreversible hubspot imports cancel --import-id import-1
```

### exports

```bash
qwayk-hubspot-safe-agent-cli --apply --ack-no-snapshot --yes hubspot exports create --body-file body.json
qwayk-hubspot-safe-agent-cli hubspot exports status --task-id task-123
```

Check the import ID in the receipt before you look for progress or errors. For a bulk change, the receipt shows whether HubSpot reported a partial failure.

## Where the code lives

The CLI entry point is in `src/hubspot_safe_agent_cli/cli.py`. HubSpot actions and the checks before sending a change are in `commands/hubspot.py` under the same package. See `config.py` and `oauth_tokens.py` for local settings and tokens, `http.py` for HTTP, and `runs.py` for saved runs.
