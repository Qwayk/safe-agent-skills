# Qdrant Cloud

Ask your agent which Qdrant Cloud clusters are running, what they cost, who can access them, and which backups are ready. If you need to change a cluster or restore a backup, the agent can show the target and request before you approve it.

A good first request is “List my Qdrant Cloud accounts and clusters, then show which backups are available.” The tool can start with a local setup check. It contacts Qdrant when you approve live access and the command includes `--live`.

Every change needs a saved plan tied to the account, resource, API key and request you reviewed. Restoring over an existing cluster can discard newer data and change what you pay. [Review a change or restore](docs/safety_model.md)

## Get started

Install the `qdrant-cloud` skill from Qwayk’s public catalog:

```bash
npx skills add Qwayk/safe-agent-skills@qdrant-cloud -g -y
```

Then [install the CLI and set up your key](docs/onboarding.md). Use a Qdrant Cloud Management Key for this tool.

## What you can do

- List clusters, backups, regions, release versions and quotas.
- Check access, API keys, invoices, cluster usage and logs.
- Get an estimate before changing cluster size or backup storage.
- Prepare a reviewed change to a cluster, backup schedule, billing or access.

The tool manages the Qdrant Cloud account and its resources. Use Qdrant’s database API to search or change vectors inside a cluster. See [the pinned commands and current coverage gaps](docs/api_coverage.md).

## Helpful guides

- [List your accounts and clusters](docs/quickstart.md)
- [Find the exact command](docs/command_reference.md)
- [See what to ask your agent](docs/use_cases.md)
- [Read the test results](docs/proof.md)
