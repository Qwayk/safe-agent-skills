# Porkbun

The Porkbun API tool for agents helps you manage domains and domain services in your Porkbun account.

You can ask your agent to check current prices and domain availability, review expirations and transfers, inspect DNS and nameservers, save an SSL bundle privately, search marketplace listings, or review webhook deliveries.

For example: “Show me the current .com registration, renewal, and transfer prices,” “Find domains in my account that expire soon,” “Review the DNS records for example.com,” or “Prepare a new A record for app.example.com.”

The agent starts by reading and explaining what it found. If you ask it to register, renew, transfer, or change anything, it saves a plan and waits for your approval. Spending, terms acceptance, secrets, deletes, sends, and other externally visible changes need extra confirmation.

Each saved plan is authenticated locally with HMAC-SHA256 and the owner-only `.state/plan-signing.key`. Apply must use the same local key and tool state that created the plan. A changed plan, missing key, or different key is refused before the write. If several processes create the first plan at the same time, one key is created and all processes use it.

## Start here first

- Want practical ideas for useful asks? [See what you can ask your agent](docs/use_cases.md)
- Need setup? [Connect the account](docs/onboarding.md)
- Want to understand approval timing? [Read what happens before changes are applied](docs/safety_model.md)

If you want command details next, use [Quickstart](docs/quickstart.md) and the [Command guide](docs/command_reference.md).

## What your agent can do

- Check current registration, renewal, and transfer prices.
- Review domain availability, your domain list, expiry dates, auto-renew settings, and transfer status.
- Inspect nameservers, glue records, URL forwarding, DNS records, and DNSSEC.
- Save SSL certificates and private keys to an owner-only file instead of printing them.
- Search marketplace listings and review account balances, API settings, webhook endpoints, and delivery history.
- Build clear plans for write actions, including what will change and why.
- Point out risks, missing settings, and what to confirm before approval.

## What happens before live changes

Read actions can run right away after auth validation. Any write is proposed first as a saved plan with exact targets. Creating a plan may make read-only provider calls to collect the current state or validate a native dry run, but it does not apply the write.

These actions always wait for approval:

- registration, renewal, and transfer
- DNS or nameserver edits
- auto-renew, glue record, URL forwarding, and DNSSEC changes
- account invitations
- webhook creation, updates, secret rotation, test deliveries, deletion, or resend
- email password changes and secret-bearing results

Registration, renewal, and transfer also require clear spend confirmation. Registration separately requires explicit agreement to Porkbun’s terms.

The tool writes plans, receipts, secret results, and onboarding `.env` files atomically with owner-only `0600` permissions. Tool-created `.state` directories use `0700`, and the plan-signing key uses `0600`. For a secret-bearing operation, the CLI checks and reserves the `--secret-out` destination before any provider call. If that destination is unsafe or cannot be written, Porkbun is not called.

Plan, receipt, and secret output files must be different from one another and must not point to the environment file, a JSON input file, or a plan input file. The CLI detects relative, absolute, `..`, symbolic-link, and existing-file aliases before any provider request or local replacement.

Provider redirects are disabled. Any `3xx` response fails instead of being followed or treated as success.

## What access this tool needs

You need a pair of Porkbun credentials:

- Porkbun API Key
- Porkbun Secret API Key

Use a dedicated key restricted by source IP and domain as much as possible. Never paste secrets in chat.

## Install and first run

Install slug: `porkbun`

Ask your agent to install the `porkbun` skill from the Qwayk skills catalog.

If your host does not install skills for you, run:

```bash
npx skills add Qwayk/safe-agent-skills@porkbun -g -y
```

Then try: “Show me the current .com registration, renewal, and transfer prices.”

## What it covers today

- All 53 documented Porkbun API paths through 66 fixed commands: 39 reads and 27 writes
- Domain pricing, availability, portfolio, transfer state, and expiration checks
- Domain registration, renewal, transfer, and account invitation planning
- DNS, nameserver, glue, URL forwarding, SSL, and DNSSEC work
- Marketplace listing reads
- Webhook endpoint, event type, delivery, test, resend, and secret-management work

Production requests are limited to Porkbun’s two official hosts:

- `https://api.porkbun.com/api/json/v3`
- `https://api-ipv4.porkbun.com/api/json/v3`

There is no arbitrary method, path, URL, or raw-request command.

## Limits

- No browser or account-dashboard automation is included.
- No webhook callback receiver hosting is included.
- No reseller, private, undocumented, or unsupported APIs are included.
- No live Porkbun account or provider call was used as proof for this release, so live-account behavior remains unverified.
- There is no rollback promise for live actions.
- Extra confirmation is always required for spend, terms acceptance, secrets, deletes, sends, and externally visible changes.

## Helpful docs

- [Browse all docs](docs/README.md)
- [Quickstart](docs/quickstart.md)
- [Command guide](docs/command_reference.md)
- [Proof and verification](docs/proof.md)
- [API coverage](docs/api_coverage.md)
