# Cloudflare

Use the Cloudflare CLI to check which DNS records point to a website, which Worker receives its traffic, or who can reach an app protected by Zero Trust. It can also help you find the logs you need when a request fails.

Try asking your agent, “Find the Cloudflare zone for my website and show me where its DNS records point.” Or ask it to check a Worker route and show you what would change before it updates the route.

Your agent starts by checking the connection and finding the right account and zone. For a live change, it shows you what it plans to change and waits for your approval. Private results such as logs and Worker code go to a local file.

## Start here first

[Connect your Cloudflare account](docs/onboarding.md), then follow the [quickstart](docs/quickstart.md) to list accounts and find the right zone.

## What your agent can do

- Check domains, DNS records, DNSSEC and zone settings.
- Find Workers routes, scripts and deployments, or look up an error in stored Worker logs.
- Review Pages projects and prepare a deployment plan.
- Check Zero Trust policies, access rules and account permissions.
- Check storage and databases, or use Browser Run to save a screenshot or page text to a local file.

See [example requests](docs/use_cases.md) for more ways to start.

## What happens before live changes

Review the exact account, resource and change before giving approval. The agent should tell you what it can save before the change and how it will check the result afterward. Some changes require separate approval to continue without a saved copy of the old settings. Some destructive changes and operations that return a secret need an extra confirmation. [Approval and file-output rules](docs/safety_model.md)

Before onboarding domains in bulk, ask the agent to run `auth zone-create-check` for the chosen account.

## What access this tool needs

Start with a Cloudflare API token that has read access for your task. Some commands need an account ID or zone ID. Features such as Browser Run and D1 need their own Cloudflare permissions. [Token setup and checks](docs/onboarding.md)

## Install and first run

Ask your agent to install the `cloudflare-api-safe-cli` skill from `Qwayk/safe-agent-skills`. If the skill does not appear, reopen the app or attach it to the workspace.

You can also install the skill from a terminal:

```bash
npx skills add Qwayk/safe-agent-skills@cloudflare-api-safe-cli -g -y
```

For a local checkout, see the [CLI install steps](docs/quickstart.md#install-the-cli). First ask the agent to check the connection, list your accounts and find the zone that matches your website.

## What it covers today

Use named commands for regular jobs. When a job has no named helper, use `operations list` to find a supported Cloudflare operation. The [coverage list](docs/api_coverage.md) shows what this copy of the tool includes and when that list was checked.

## Limits

Some operations need more access than a read-only token provides. A successful connection check only proves the token can make that check. When Cloudflare cannot confirm the result of a change, the receipt should say what it could verify. Review how you would recover before approving a change that has no saved copy of the old settings.

## Helpful docs

- [All Cloudflare docs](docs/README.md)
- [Command guide](docs/command_reference.md)
- [What has been verified](docs/proof.md)
